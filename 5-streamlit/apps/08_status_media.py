"""08 · Messages, progress and media

    uv run streamlit run 5-streamlit/apps/08_status_media.py

Tell the user what is happening: a message box, a spinner while something slow runs,
a progress bar, and pictures (sound and video work the same way).
"""
import time
from pathlib import Path

import streamlit as st

HERE = Path(__file__).resolve().parent

st.title("Messages, progress and media")

st.header("Message boxes")
st.success("Data loaded: 891 passengers.")
st.info("Tip: pick a class in the sidebar.")
st.warning("177 passengers have no age.")
st.error("No passenger matches these filters.")
st.exception(ValueError("Age can't be negative"))   # shows an error with its type

st.header("Balloons")
if st.button("Celebrate"):
    st.balloons()                           # or st.snow()

st.header("Something slow")
if st.button("Run a slow step"):
    with st.spinner("Counting the lifeboats..."):
        time.sleep(2)
    st.success("Done: 20 lifeboats.")

    bar = st.progress(0, text="Loading the passenger list")
    for pct in range(0, 101, 20):
        time.sleep(0.3)
        bar.progress(pct, text=f"Loading the passenger list: {pct}%")

    with st.status("Checking the file...", expanded=True) as status:
        st.write("Reading titanic.csv")
        time.sleep(0.5)
        st.write("Counting missing values")
        time.sleep(0.5)
        status.update(label="File checked", state="complete")

st.header("Media")
st.image(HERE / "images" / "titanic_ports.png", caption="Southampton → Cherbourg → Queenstown", width=500)
st.caption("st.audio('file.mp3') and st.video('file.mp4' or a YouTube link) work the same way.")
