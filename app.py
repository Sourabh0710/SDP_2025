import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
from gesture_engine import GestureEngine
import os

st.set_page_config(page_title="Gesture Lock App", layout="centered")

# Initialize engine
if "engine" not in st.session_state:
    st.session_state.engine = GestureEngine()
if "first_pattern" not in st.session_state:
    st.session_state.first_pattern = None
if "pattern_set" not in st.session_state:
    st.session_state.pattern_set = False

st.title("🔒 Gesture-Based Locking System")

st.markdown("Draw a gesture pattern in the box below:")

canvas_result = st_canvas(
    stroke_width=5,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=300,
    width=300,
    drawing_mode="freedraw",
    key="canvas"
)

if st.button("Submit Pattern"):
    if canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        if objects:
            raw_points = []
            for obj in objects:
                if obj["type"] == "path":
                    path = obj["path"]
                    for seg in path:
                        if len(seg) >= 3:
                            raw_points.append(seg[1:3])

            if raw_points:
                gesture = np.array(raw_points, dtype=np.float32)

                if not st.session_state.first_pattern:
                    st.session_state.first_pattern = gesture
                    st.success("Pattern recorded. Please draw it again to confirm.")
                else:
                    if st.session_state.engine.is_match(st.session_state.first_pattern, gesture):
                        st.session_state.engine.save_pattern(st.session_state.first_pattern)
                        st.session_state.pattern_set = True
                        st.success("✅ Pattern confirmed and saved securely.")
                        st.session_state.first_pattern = None
                    else:
                        st.error("❌ Patterns do not match. Please try again.")
                        st.session_state.first_pattern = None

                # Clear canvas on each submission
                st.experimental_rerun()

# If pattern is set, show project files like GitHub
if st.session_state.pattern_set:
    st.subheader("📁 Project Repository Structure")
    st.code("""
gesture_lock/
├── app.py                   ← Streamlit frontend
├── gesture_engine.py        ← Core logic (resampling, matching)
├── key.key                  ← Fernet encryption key
├── patterns.dat             ← Stored gesture patterns (encrypted)
├── unlock_attempts.log      ← Unlock log file
├── requirements.txt         ← Dependencies for deployment
    """, language="bash")

    st.markdown("You can now lock/unlock using your custom gesture.")

