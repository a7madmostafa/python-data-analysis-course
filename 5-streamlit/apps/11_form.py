"""11 · Forms: change many widgets, rerun once

    uv run streamlit run 5-streamlit/apps/11_form.py

Normally, every widget change reruns the script. Inside st.form, nothing happens
until the user clicks the submit button: good when the work after the filters is slow.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path(__file__).resolve().parents[2] / "data" / "titanic.csv"
df = pd.read_csv(DATA)

st.title("Find a passenger")

with st.form("search"):
    name = st.text_input("Name contains", placeholder="e.g. Allen")
    classes = st.multiselect("Class", [1, 2, 3], default=[1, 2, 3])
    ages = st.slider("Age", 0, 80, (0, 80))
    submitted = st.form_submit_button("Search")   # every form needs one

# The widgets above keep their values, but the script only "sees" them after Search
if submitted:
    found = df[df["Name"].str.contains(name, case=False)
               & df["Pclass"].isin(classes)
               & df["Age"].between(*ages)]
    st.write(f"{len(found)} passengers found")
    st.dataframe(found, hide_index=True)
else:
    st.info("Set the filters, then click Search.")
