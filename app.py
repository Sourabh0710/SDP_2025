import streamlit as st
import numpy as np
import cv2
from gesture_engine import GestureEngine

# Streamlit App Configuration
st.set_page_config(page_title="Gesture Lock", layout="centered")

# Initialize Gesture Engine
if "engine" not in st.session_state:
    st.session_state.engine = GestureEngine()

# Global Variables
pattern_points = []
drawing = False
stage = "capture"
confirmations = []
MAX_ATTEMPTS = 3
attempts = 0
system_locked = False

# Draw function to update canvas
def draw_canvas():
    canvas = np.ones((400, 400, 3), dtype="uint8") * 255
    return canvas

# Capture mouse input for drawing pattern
def capture_pattern(event, x, y, flags, param):
    global pattern_points, drawing
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        pattern_points = [(x, y)]
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        pattern_points.append((x, y))
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        pattern_points.append((x, y))

# Main Streamlit app
def main():
    global pattern_points, stage, confirmations, attempts, system_locked

    if system_locked:
        st.write("System Locked due to failed attempts.")
        return

    # Instructions
    st.title("Gesture-Based Locking System")
    if stage == "capture":
        st.write("Step 1: Draw and confirm 3 patterns.")

    elif stage == "unlock":
        st.write("Step 2: Draw your pattern to unlock.")

    # Capture and draw pattern
    canvas = draw_canvas()
    st.image(canvas, channels="BGR")

    # Update pattern points and reset canvas after submission
    if len(pattern_points) > 1 and not drawing:
        try:
            encrypted, hash_val, normalized = st.session_state.engine.process_pattern(pattern_points)
            if encrypted is not None:
                if stage == "capture":
                    if len(confirmations) % 2 == 0:
                        confirmations.append(pattern_points)
                    else:
                        if np.allclose(confirmations[-1], pattern_points, atol=0.05):
                            st.session_state.engine.save_pattern(encrypted, hash_val, len(confirmations) + 1)
                            confirmations.clear()
                            stage = "unlock"
                            st.write("Pattern saved, now draw to unlock!")
                        else:
                            confirmations.clear()
                            st.write("Mismatch, please draw again.")
                elif stage == "unlock":
                    distance = st.session_state.engine.match_pattern(normalized)
                    if distance <= 0.1:
                        st.write("Unlocked successfully!")
                    else:
                        attempts += 1
                        if attempts >= MAX_ATTEMPTS:
                            system_locked = True
                            st.write("Too many failed attempts, system locked.")
                        else:
                            st.write("Pattern mismatch, try again.")
            else:
                st.write("Pattern error.")
        except Exception as e:
            st.write(f"Error: {e}")

    # Restart or exit option
    if st.button("Restart"):
        system_locked = False
        stage = "capture"
        confirmations.clear()
        attempts = 0
        pattern_points.clear()

if __name__ == "__main__":
    main()
