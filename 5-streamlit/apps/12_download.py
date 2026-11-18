"""12 · Download: give the user a file

    uv run streamlit run 5-streamlit/apps/12_download.py

st.download_button turns any text or bytes into a file the user saves: here, the filtered rows as CSV.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path(__file__).resolve().parents[2] / "data" / "titanic.csv"
df = pd.read_csv(DATA)

st.title("Download what you see")

classes = st.multiselect("Class", [1, 2, 3], default=[1])
data = df[df["Pclass"].isin(classes)]
st.write(f"{len(data)} passengers")

# the filtered rows as a CSV file
st.download_button(
    "⬇️ Download these passengers (CSV)",
    data=data.to_csv(index=False),
    file_name="titanic_filtered.csv",
    mime="text/csv",
    on_click="ignore",          # downloading should not rerun the app
)
