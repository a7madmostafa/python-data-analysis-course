"""07 · Layout

    uv run streamlit run 5-streamlit/apps/07_layout.py

By default, everything stacks from top to bottom. Layout puts things beside each other or out of the way:
sidebar, columns, tabs, expander, container.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Titanic layout", page_icon="🚢", layout="wide")   # wide: use the whole screen

DATA = Path(__file__).resolve().parents[2] / "data" / "titanic.csv"
df = pd.read_csv(DATA)

# ------------------------------------------------------------ sidebar: the filters live here
st.sidebar.header("Filters")
classes = st.sidebar.multiselect("Class", [1, 2, 3], default=[1, 2, 3])
with st.sidebar:                       # the `with` form: same thing, handy for many lines
    sex = st.radio("Sex", ["All", "male", "female"])
    st.caption("891 passengers, Kaggle training file")

data = df[df["Pclass"].isin(classes)]
if sex != "All":
    data = data[data["Sex"] == sex]

st.title("🚢 Titanic: layout")

# ------------------------------------------------------------ columns: side by side
col1, col2, col3 = st.columns(3)
col1.metric("Passengers", len(data), border=True)
col2.metric("Survival rate", f"{data['Survived'].mean():.0%}", border=True)
col3.metric("Median fare", f"£{data['Fare'].median():.2f}", border=True)

left, right = st.columns([2, 1])       # widths: the left column is twice as wide
with left:
    st.plotly_chart(px.histogram(data, x="Age", nbins=30, title="Age"))
with right:
    st.plotly_chart(px.pie(data.dropna(subset=["Embarked"]), names="Embarked", hole=0.5, title="Port (S, C, Q)"))

# ------------------------------------------------------------ tabs: one page, several views
tab_class, tab_sex = st.tabs(["By class", "By sex"])
with tab_class:
    st.bar_chart(data.groupby("Pclass")["Survived"].mean())
with tab_sex:
    st.bar_chart(data.groupby("Sex")["Survived"].mean())

# ------------------------------------------------------------ expander: hidden until clicked
with st.expander("Show the passengers"):
    st.dataframe(data, hide_index=True)

# ------------------------------------------------------------ container: a box you can fill later
box = st.container(border=True)
box.write("A container with a border. Things written into `box` appear here, even if the code comes later.")

box.write("…like this line, written at the very end of the script.")
