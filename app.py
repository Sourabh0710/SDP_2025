import streamlit as st
import numpy as np
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Gesture Lock", layout="centered")
st.title("🔐 Gesture Lock")

# Initialize session state
if "pattern_count" not in st.session_state:
    st.session_state.pattern_count = 0
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# Show instruction
st.markdown("Draw your gesture pattern below. Each pattern will be submitted one at a time.")

# Only show canvas if not already submitted
if not st.session_state.submitted:

    # Drawable canvas
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=5,
        stroke_color="#000000",
        background_color="#ffffff",
        height=300,
        width=300,
        drawing_mode="freedraw",
        key=f"canvas_{st.session_state.pattern_count}",
    )

    # Button to submit pattern
    if st.button("Submit Pattern"):
        if canvas_result.image_data is not None:
            st.session_state.submitted = True
            st.image(canvas_result.image_data, caption=f"Pattern #{st.session_state.pattern_count + 1}")
            st.success("Pattern submitted. Canvas cleared.")
        else:
            st.warning("Please draw something before submitting.")

# Reset canvas after submission
if st.session_state.submitted:
    if st.button("Draw Again"):
        st.session_state.submitted = False
        st.session_state.pattern_count += 1
