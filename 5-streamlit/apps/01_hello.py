"""01 · Hello, Streamlit

Open a terminal in the repository folder. The first time only, install the packages listed in pyproject.toml:

    uv sync

Then run the app:

    uv run streamlit run 5-streamlit/apps/01_hello.py

A browser tab opens at http://localhost:8501. Keep the terminal open: closing it stops the app.
Edit this file and save: the page offers "Rerun" (or click "Always rerun").
"""
from datetime import datetime

import streamlit as st

st.title("Hello, Streamlit 👋")
st.write("A normal Python script, run top to bottom.")

# The clock shows WHEN the script ran
now = datetime.now().strftime("%H:%M:%S")
st.write("The script ran at", now)

# Click and watch the clock: every click runs the whole file again
if st.button("Click me"):
    st.write("You clicked! The clock changed too.")

# Same story with any widget you touch
n = st.slider("Pick a number", 1, 10, 3)
st.write(f"{n} squared is {n * n}")
