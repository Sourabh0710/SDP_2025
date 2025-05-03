import numpy as np
import hashlib
from cryptography.fernet import Fernet
from sklearn.neighbors import KNeighborsClassifier
import logging


class GestureEngine:
    def __init__(self):
        self.points = []
        self.patterns = []
        self.pattern_hashes = []
        self.pattern_labels = []
        self.knn_model = KNeighborsClassifier(n_neighbors=1)
        self._load_or_generate_key()

    # Load or generate the encryption key
    def _load_or_generate_key(self):
        try:
            with open("key.key", "rb") as f:
                self.cipher = Fernet(f.read())
        except FileNotFoundError:
            self._generate_key()

    # Generate encryption key if not found
    def _generate_key(self):
        self.cipher = Fernet(Fernet.generate_key())
        with open("key.key", "wb") as f:
            f.write(self.cipher._key)

    # Normalize pattern
    def normalize(self, points):
        points = np.array(points)
        centroid = np.mean(points, axis=0)
        centered = points - centroid
        max_dist = np.max(np.sqrt(np.sum(centered ** 2, axis=1)))
        return centered / max_dist

    # Resample pattern to fixed number of points
    def resample(self, points, num_points=40):
        if len(points) < 2:
            raise ValueError("Insufficient points to resample.")
        distances = np.cumsum(np.sqrt(np.sum(np.diff(points, axis=0) ** 2, axis=1)))
        distances = np.insert(distances, 0, 0)
        uniform_distances = np.linspace(0, distances[-1], num_points)
        resampled_points = np.array([np.interp(uniform_distances, distances, coord) for coord in points.T]).T
        return resampled_points

    # Encrypt and hash pattern
    def encrypt_and_hash(self, pattern):
        encrypted = self.cipher.encrypt(pattern.tobytes())
        hash_val = hashlib.sha256(pattern.tobytes()).hexdigest()
        return encrypted, hash_val

    # Process pattern
    def process_pattern(self, pattern_points):
        if not pattern_points:
            raise ValueError("Pattern points cannot be empty.")

        # Convert to numpy array of coordinates
        raw_points = np.array(pattern_points)

        if raw_points.ndim != 2 or raw_points.shape[1] != 2:
            raise ValueError("Pattern points should be a list of 2D points.")

        # Resample the points to a fixed number
        try:
            resampled = self.resample(raw_points)
        except Exception as e:
            print(f"Error in resampling: {e}")
            return None

        # Normalize the resampled points
        normalized = self.normalize(resampled)

        # Encrypt and hash the pattern
        encrypted, hash_val = self.encrypt_and_hash(normalized)

        return encrypted, hash_val, normalized

    # Save pattern
    def save_pattern(self, encrypted, hash_val, pattern_label):
        self.patterns.append(encrypted)
        self.pattern_hashes.append(hash_val)
        self.pattern_labels.append(pattern_label)

    # Train KNN model
    def train_knn(self):
        X = [self.decrypt_pattern(p) for p in self.patterns]
        y = self.pattern_labels
        self.knn_model.fit(X, y)

    # Decrypt pattern
    def decrypt_pattern(self, encrypted):
        return np.frombuffer(self.cipher.decrypt(encrypted)).reshape(-1, 2)

    # Match pattern using KNN
    def match_pattern(self, normalized_pattern):
        pred = self.knn_model.predict([normalized_pattern.flatten()])[0]
        stored_pattern = self.decrypt_pattern(self.patterns[pred - 1])
        distance = np.mean(np.sqrt(np.sum((stored_pattern - normalized_pattern) ** 2, axis=1)))
        return distance
