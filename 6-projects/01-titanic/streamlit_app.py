"""Titanic survival dashboard.

    uv run streamlit run 6-projects/01-titanic/streamlit_app.py

Reads data/titanic_clean.csv (written by analysis.ipynb). The charts are in charts.py.
Every number and chart is computed from the passengers that pass the sidebar filters.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

import charts as ch

st.set_page_config(page_title="Titanic survival", page_icon="🚢", layout="wide")
DATA = Path(__file__).resolve().parents[2] / "data" / "titanic_clean.csv"


@st.cache_data
def load_data(path):
    return pd.read_csv(path)


df = load_data(DATA)
st.title("🚢 Who survived the Titanic?")
st.caption("891 passengers of the training file (Kaggle) · cleaned in analysis.ipynb")

# ------------------------------------------------------------ filters
with st.sidebar:
    st.header("Filters")
    classes = st.pills("Class", ch.ORDERS["class"], selection_mode="multi", default=ch.ORDERS["class"])
    sexes = st.pills("Sex", ch.ORDERS["sex"], selection_mode="multi", default=ch.ORDERS["sex"])
    ports = st.multiselect("Port", ch.ORDERS["port"], default=ch.ORDERS["port"])
    ages = st.slider("Age", 0, 80, (0, 80))
    known_only = st.toggle("Only passengers with a known age", value=False)

data = df[df["class"].isin(classes) & df["sex"].isin(sexes) & df["port"].isin(ports)
          & df["age"].between(*ages)]
if known_only:
    data = data[data["age_known"]]
if data.empty:
    st.warning("No passenger matches these filters.")
    st.stop()

# ------------------------------------------------------------ KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Passengers", f"{len(data):,}", border=True)
col2.metric("Survived", f"{data['survived'].sum():,}", border=True)
col3.metric("Survival rate", f"{data['survived'].mean():.0%}",
            delta=f"{data['survived'].mean() - df['survived'].mean():+.0%} vs all", border=True)
col4.metric("Median fare", f"£{data['fare'].median():.0f}", border=True)

who, combos, ages_fares, table = st.tabs(["🛟 Who survived?", "🔀 Two groups", "📊 Ages and fares", "📋 Passengers"])

with who:
    by = st.radio("Split by", ch.GROUPS, horizontal=True, format_func=ch.LABELS.get)
    left, right = st.columns(2)
    with left:
        ch.show(ch.rate_bar(data, by), f"Survival rate by {ch.LABELS[by].lower()}", "Hover for the number of passengers")
    with right:
        ch.show(ch.count_bar(data, by), f"Passengers by {ch.LABELS[by].lower()}")

with combos:
    left, right = st.columns(2)
    row = left.selectbox("Rows", ch.GROUPS, index=1, format_func=ch.LABELS.get)
    col = right.selectbox("Columns", [g for g in ch.GROUPS if g != row], index=0, format_func=ch.LABELS.get)
    ch.show(ch.rate_heatmap(data, row, col), "Survival rate for every combination")
    ch.show(ch.port_mix(data), "Who boarded where?", "The share of each class at each port")

with ages_fares:
    left, right = st.columns(2)
    with left:
        ch.show(ch.age_hist(data), "Ages of survivors and victims", "Known ages only")
    with right:
        ch.show(ch.fare_box(data), "Fare by class and outcome", "Log scale; free tickets left out")

with table:
    cols = ["name", "class", "sex", "age", "title", "family_size", "fare", "port", "outcome"]
    st.dataframe(data[cols], hide_index=True, column_config={"fare": st.column_config.NumberColumn(format="£%.2f")})
    st.download_button("Download CSV", data[cols].to_csv(index=False), "titanic_passengers.csv", "text/csv")
