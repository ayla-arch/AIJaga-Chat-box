"""
Run the AiJaga app (quiz + chat + videos):

    pip install --upgrade streamlit
    streamlit run streamlit_app.py

Keep these 3 files in the SAME folder:
    aijaga_quiz.py   (questions + quiz page)
    aijaga_video.py  (adds the VIDEO feature)
    streamlit_app.py (this file - the one you run)
"""

import streamlit as st

from aijaga_video import PAGE  # quiz page + video feature

PAGE_HEIGHT = 1150

st.set_page_config(
    page_title="AiJaga - Health Quiz",
    page_icon="\U0001FA7A",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if hasattr(st, "iframe"):
    # Newer Streamlit: components.html was deprecated and later removed.
    st.iframe(PAGE, height=PAGE_HEIGHT)
else:
    # Older Streamlit
    import streamlit.components.v1 as components
    components.html(PAGE, height=PAGE_HEIGHT, scrolling=True)
