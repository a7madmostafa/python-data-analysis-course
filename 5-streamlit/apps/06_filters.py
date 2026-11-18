"""06 · Widgets that filter the data

    uv run streamlit run 5-streamlit/apps/06_filters.py

The pattern of every dashboard:
    widgets  ->  a filtered DataFrame  ->  numbers and charts from the filtered DataFrame
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA = Path(__file__).resolve().parents[2] / "data" / "titanic.csv"
df = pd.read_csv(DATA)

st.title("Who survived the Titanic?")

# 1) the widgets
classes = st.multiselect("Class", [1, 2, 3], default=[1, 2, 3])
sex = st.radio("Sex", ["All", "male", "female"], horizontal=True)
ages = st.slider("Age", 0, 80, (0, 80))
keep_unknown = st.checkbox("Keep passengers with unknown age", value=True)   # 177 have no age!

# 2) one boolean mask per widget, the same filtering as in pandas
mask = df["Pclass"].isin(classes)
if sex != "All":
    mask &= df["Sex"] == sex
age_ok = df["Age"].between(*ages)
if keep_unknown:
    age_ok |= df["Age"].isna()
data = df[mask & age_ok]

# 3) everything below uses `data`, never `df`
if data.empty:
    st.warning("No passenger matches these filters. Pick at least one class.")
    st.stop()   # nothing after this line runs

col1, col2 = st.columns(2)
col1.metric("Passengers", len(data), border=True)
col2.metric("Survival rate", f"{data['Survived'].mean():.0%}", border=True)

rates = data.groupby("Pclass", as_index=False)["Survived"].mean()
fig = px.bar(rates, x="Pclass", y="Survived", text_auto=".0%",
             labels={"Pclass": "Class", "Survived": "Survival rate"})
fig.update_xaxes(type="category")
fig.update_yaxes(tickformat=".0%")
st.plotly_chart(fig)
