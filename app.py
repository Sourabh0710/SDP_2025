import streamlit as st
from gesture_engine import GestureEngine
from streamlit_drawable_canvas import st_canvas
import os

# 🔧 Initialize session state
if 'first_pattern' not in st.session_state:
    st.session_state.first_pattern = None
if 'pattern_verified' not in st.session_state:
    st.session_state.pattern_verified = False
if 'engine' not in st.session_state:
    st.session_state.engine = GestureEngine()
if 'reset_canvas' not in st.session_state:
    st.session_state.reset_canvas = False

st.title("🔐 Gesture-Based Pattern Lock")

st.markdown("Draw your gesture pattern below 👇")

# Canvas config
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=3,
    stroke_color="#000",
    background_color="#fff",
    update_streamlit=True,
    height=300,
    width=300,
    drawing_mode="freedraw",
    key="canvas",
    disabled=st.session_state.pattern_verified
)

# Reset canvas after submission
if st.session_state.reset_canvas:
    st.session_state.canvas = None
    st.session_state.reset_canvas = False
    st.rerun()

# Extract pattern points
if canvas_result.json_data is not None:
    raw_objects = canvas_result.json_data["objects"]
    if raw_objects:
        pattern_points = [(obj["left"], obj["top"]) for obj in raw_objects if obj["type"] == "path"]
    else:
        pattern_points = []

    if st.button("✅ Submit Pattern"):
        if pattern_points:
            if st.session_state.first_pattern is None:
                st.session_state.first_pattern = pattern_points
                st.success("Pattern captured! Please draw it again to confirm.")
                st.session_state.reset_canvas = True
                st.rerun()
            else:
                if st.session_state.engine.compare_patterns(st.session_state.first_pattern, pattern_points):
                    st.session_state.pattern_verified = True
                    st.success("✅ Pattern verified successfully!")

                    # Show file structure
                    st.subheader("📁 GitHub-Style Project Structure")
                    st.code("""
gesture_lock/
├── app.py
├── gesture_engine.py
├── key.key
├── patterns.dat
├── unlock_attempts.log
├── requirements.txt
""", language="text")
                else:
                    st.error("❌ Pattern does not match. Please try again.")
                    st.session_state.first_pattern = None
                    st.session_state.reset_canvas = True
                    st.rerun()
        else:
            st.warning("Please draw a pattern before submitting.")
