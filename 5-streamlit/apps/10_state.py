"""10 · Session state: memory between reruns

    uv run streamlit run 5-streamlit/apps/10_state.py

Each rerun starts the script from zero, so normal variables forget everything.
st.session_state is a dictionary that survives reruns (one per browser tab).
"""
import streamlit as st

st.title("Session state")

# ------------------------------------------------------------ 1. the bug everybody writes once
st.header("1. A counter that never counts")
count = 0
if st.button("Add one (normal variable)"):
    count += 1
st.write("count =", count, "← stuck at 0 or 1: `count = 0` runs again on every click")

# ------------------------------------------------------------ 2. the fix
st.header("2. The same counter in session_state")
if "count" not in st.session_state:      # only on the very first run
    st.session_state.count = 0
if st.button("Add one (session_state)"):
    st.session_state.count += 1
st.write("st.session_state.count =", st.session_state.count)

# ------------------------------------------------------------ 3. widgets with a key live in session_state
st.header("3. Widgets have keys")
st.selectbox("Class", [1, 2, 3], key="pclass")
st.write("The selectbox value is also in st.session_state['pclass'] →", st.session_state["pclass"])
