import streamlit as st
import numpy as np
from streamlit_drawable_canvas import st_canvas
from scipy.spatial.distance import euclidean

st.set_page_config(page_title="Gesture Lock", layout="centered")
st.title("🔐 Gesture Lock Setup")

# Config
TOLERANCE = 50  # Adjust as needed

# Helper to convert canvas image to list of points
def extract_points(image):
    if image is None:
        return []
    image = (255 - image[:, :, 0]) > 50  # Basic threshold
    points = np.column_stack(np.where(image))
    return points

def resample(points, num=100):
    if len(points) < 2:
        return np.array([])
    diffs = np.diff(points, axis=0)
    dists = np.sqrt((diffs ** 2).sum(axis=1))
    cumulative = np.cumsum(dists)
    cumulative = np.insert(cumulative, 0, 0)
    uniform_dists = np.linspace(0, cumulative[-1], num)
    resampled = np.zeros((num, 2))
    resampled[:, 0] = np.interp(uniform_dists, cumulative, points[:, 0])
    resampled[:, 1] = np.interp(uniform_dists, cumulative, points[:, 1])
    return resampled

# State
if "attempts" not in st.session_state:
    st.session_state.attempts = []
if "confirmed" not in st.session_state:
    st.session_state.confirmed = False
if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = 0

# Draw canvas
st.markdown("Draw the same pattern twice to confirm it:")
canvas_result = st_canvas(
    fill_color="rgba(255,165,0,0.3)",
    stroke_width=5,
    stroke_color="#000000",
    background_color="#ffffff",
    height=300,
    width=300,
    drawing_mode="freedraw",
    key=f"canvas_{st.session_state.canvas_key}"
)

# Submit button
if st.button("Submit Pattern"):
    if canvas_result.image_data is not None and np.any(canvas_result.image_data != 255):
        raw_pts = extract_points(canvas_result.image_data)
        if len(raw_pts) < 10:
            st.warning("Please draw a more detailed pattern.")
        else:
            resampled = resample(raw_pts)
            if resampled.size == 0:
                st.warning("Pattern is too simple.")
            else:
                st.session_state.attempts.append(resampled)
                st.session_state.canvas_key += 1  # Force reset canvas
                if len(st.session_state.attempts) == 1:
                    st.info("Now draw the **same** pattern again to confirm.")
                elif len(st.session_state.attempts) == 2:
                    dist = np.mean([euclidean(a, b) for a, b in zip(*st.session_state.attempts)])
                    if dist <= TOLERANCE:
                        st.success("✅ Pattern confirmed and saved successfully.")
                        st.session_state.confirmed = True
                    else:
                        st.error("❌ Patterns did not match. Please try again.")
                        st.session_state.attempts.clear()
    else:
        st.warning("Please draw a pattern before submitting.")

# Debug/Reset option
if st.session_state.confirmed:
    if st.button("Reset and Try Again"):
        st.session_state.attempts.clear()
        st.session_state.confirmed = False
        st.session_state.canvas_key += 1
