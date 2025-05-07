import streamlit as st
from gesture_engine import GestureEngine
from streamlit_drawable_canvas import st_canvas
import time

# Initialize session state
if 'first_pattern' not in st.session_state:
    st.session_state.first_pattern = None
if 'pattern_verified' not in st.session_state:
    st.session_state.pattern_verified = False
if 'engine' not in st.session_state:
    st.session_state.engine = GestureEngine()
if 'canvas_key' not in st.session_state:
    st.session_state.canvas_key = str(time.time())  # for resetting canvas

st.title("🔐 Gesture-Based Pattern Lock")
st.markdown("Draw your gesture pattern below 👇")

# Show canvas
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=3,
    stroke_color="#000",
    background_color="#fff",
    update_streamlit=True,
    height=300,
    width=300,
    drawing_mode="freedraw",
    key=st.session_state.canvas_key,
    disabled=st.session_state.pattern_verified
)

# Extract pattern points
def extract_points(json_data):
    if not json_data or "objects" not in json_data:
        return []
    return [(obj["left"], obj["top"]) for obj in json_data["objects"] if obj["type"] == "path"]

# Handle submission
if st.button("✅ Submit Pattern"):
    pattern_points = extract_points(canvas_result.json_data)
    if not pattern_points:
        st.warning("⚠️ Please draw a valid pattern before submitting.")
    elif st.session_state.first_pattern is None:
        st.session_state.first_pattern = pattern_points
        st.success("✅ Pattern captured! Please draw it again to confirm.")
        st.session_state.canvas_key = str(time.time())  # reset canvas
        st.rerun()
    else:
        if st.session_state.engine.compare_patterns(st.session_state.first_pattern, pattern_points):
            st.session_state.pattern_verified = True
            st.success("🎉 Pattern verified successfully and saved!")
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
            st.session_state.canvas_key = str(time.time())  # reset again
            st.rerun()
