
import numpy as np
import hashlib
import os
import logging
from cryptography.fernet import Fernet
from sklearn.neighbors import KNeighborsClassifier

# Constants
POINTS_COUNT = 40
TOLERANCE = 0.6
TOTAL_PATTERNS = 3
MAX_ATTEMPTS = 5

# File paths
KEY_PATH = "key.key"
PATTERN_PATH = "patterns.dat"
LOG_PATH = "unlock_attempts.log"

logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                    format="%(asctime)s - %(message)s")


class GestureEngine:
    def __init__(self):
        self.stage = "capture"
        self.pattern_index = 1
        self.attempts = 0
        self.initial_patterns = []
        self.pattern_hashes = []
        self.pattern_labels = []
        self.knn_model = KNeighborsClassifier(n_neighbors=1)
        self._load_or_generate_key()
        self.load_saved_patterns()

    def _load_or_generate_key(self):
        if os.path.exists(KEY_PATH):
            with open(KEY_PATH, "rb") as f:
                self.cipher = Fernet(f.read())
        else:
            key = Fernet.generate_key()
            with open(KEY_PATH, "wb") as f:
                f.write(key)
            self.cipher = Fernet(key)

    def normalize(self, points):
        points = np.array(points)
        centroid = np.mean(points, axis=0)
        centered = points - centroid
        max_dist = np.max(np.sqrt(np.sum(centered ** 2, axis=1)))
        return centered / max_dist if max_dist > 0 else centered

    def resample(self, points, num_points=POINTS_COUNT):
        points = np.array(points)
        distances = np.cumsum(np.sqrt(np.sum(np.diff(points, axis=0) ** 2, axis=1)))
        distances = np.insert(distances, 0, 0)
        uniform_distances = np.linspace(0, distances[-1], num_points)
        return np.array([np.interp(uniform_distances, distances, coord) for coord in points.T]).T

    def encrypt_and_hash(self, pattern):
        encrypted = self.cipher.encrypt(pattern.tobytes())
        hash_val = hashlib.sha256(pattern.tobytes()).hexdigest()
        return encrypted, hash_val

    def decrypt_pattern(self, encrypted):
        return np.frombuffer(self.cipher.decrypt(encrypted)).reshape(-1, 2)

    def process_pattern(self, raw_points):
        resampled = self.resample(raw_points)
        normalized = self.normalize(resampled)
        flat = normalized.flatten()

        if self.stage == "capture":
            encrypted, hash_val = self.encrypt_and_hash(normalized)
            self.initial_patterns.append(encrypted)
            self.pattern_hashes.append(hash_val)
            self.pattern_labels.append(self.pattern_index)
            self.pattern_index += 1
            if self.pattern_index > TOTAL_PATTERNS:
                self.stage = "unlock"
                X = [self.decrypt_pattern(p).flatten() for p in self.initial_patterns]
                y = self.pattern_labels
                self.knn_model.fit(X, y)
                self.save_patterns_to_disk()
                return "All patterns saved. Draw to unlock"
            return f"Pattern {self.pattern_index - 1} saved. Draw next"

        elif self.stage == "unlock":
            pred = self.knn_model.predict([flat])[0]
            stored_pattern = self.decrypt_pattern(self.initial_patterns[pred - 1])
            distance = np.mean(np.sqrt(np.sum((stored_pattern - normalized) ** 2, axis=1)))
            if distance <= TOLERANCE:
                logging.info("Unlocked successfully.")
                return "Unlocked!"
            else:
                self.attempts += 1
                logging.warning(f"Failed attempt {self.attempts}")
                if self.attempts >= MAX_ATTEMPTS:
                    return "System Locked. Restart app."
                return "Incorrect Pattern"

    def save_patterns_to_disk(self):
        with open(PATTERN_PATH, "wb") as f:
            for enc, label in zip(self.initial_patterns, self.pattern_labels):
                f.write(len(enc).to_bytes(4, byteorder='big'))
                f.write(enc)
                f.write(label.to_bytes(1, byteorder='big'))

    def load_saved_patterns(self):
        if os.path.exists(PATTERN_PATH):
            with open(PATTERN_PATH, "rb") as f:
                encrypted_patterns = []
                labels = []
                while True:
                    try:
                        length = int.from_bytes(f.read(4), byteorder='big')
                        enc = f.read(length)
                        label = int.from_bytes(f.read(1), byteorder='big')
                        encrypted_patterns.append(enc)
                        labels.append(label)
                    except:
                        break
                if encrypted_patterns:
                    self.initial_patterns = encrypted_patterns
                    self.pattern_labels = labels
                    self.stage = "unlock"
                    X = [self.decrypt_pattern(p).flatten() for p in self.initial_patterns]
                    y = self.pattern_labels
                    self.knn_model.fit(X, y)
