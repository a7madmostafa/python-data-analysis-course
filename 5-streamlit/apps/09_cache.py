"""09 · Cache: don't do the slow work on every click

    uv run streamlit run 5-streamlit/apps/09_cache.py

Every click reruns the WHOLE script, including pd.read_csv. With a big file (or a database, or an API),
that's slow. @st.cache_data remembers what the function returned for the same inputs.
"""
import time
from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path(__file__).resolve().parents[2] / "data" / "titanic.csv"


def load_slow(path):
    time.sleep(2)            # pretend the file is huge
    return pd.read_csv(path)


@st.cache_data               # the only change: one line above the function
def load_cached(path):
    time.sleep(2)
    return pd.read_csv(path)


st.title("Cache")
use_cache = st.toggle("Use @st.cache_data", value=False)

start = time.perf_counter()
df = load_cached(DATA) if use_cache else load_slow(DATA)
seconds = time.perf_counter() - start

st.metric("This rerun took", f"{seconds:.2f} s", border=True)
st.slider("Move me to rerun the script", 0, 10, 5)
st.write("Without the cache, every move waits 2 seconds. With it, only the first run waits.")

if st.button("Clear the cache"):
    st.cache_data.clear()    # e.g. after the file changed on disk

st.dataframe(df.head(), hide_index=True)
