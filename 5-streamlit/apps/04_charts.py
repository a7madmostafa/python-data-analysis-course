"""04 · Charts

    uv run streamlit run 5-streamlit/apps/04_charts.py

Three kinds of charts:
  1. Streamlit's own quick charts: one line, from a table
  2. Plotly figures                       -> st.plotly_chart(fig)
  3. Matplotlib / Seaborn figures         -> st.pyplot(fig)
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st

DATA = Path(__file__).resolve().parents[2] / "data" / "titanic.csv"
df = pd.read_csv(DATA)
df["Outcome"] = df["Survived"].map({1: "Survived", 0: "Died"})

st.title("Charts in Streamlit")

# ------------------------------------------------------------ 1. Streamlit's own charts
st.header("1. Quick charts")
st.caption("Give them a table: the index becomes the x-axis and every column becomes a series.")

st.subheader("Passengers by class and outcome: st.bar_chart")
counts = pd.crosstab(df["Pclass"], df["Outcome"])
st.bar_chart(counts, color=["#D95D4A", "#0F766E"])   # one colour per column (Died, Survived)

st.subheader("Survival rate by age (10-year groups): st.line_chart")
by_age = df.groupby(df["Age"] // 10 * 10)["Survived"].mean()   # 0 = ages 0-9, 10 = ages 10-19, ...
st.line_chart(by_age, x_label="Age group", y_label="Survival rate")

st.subheader("Age against fare: st.scatter_chart")
st.scatter_chart(df, x="Age", y="Fare", color="Outcome")

# st.map wants latitude and longitude columns: here, the three ports where people boarded
st.subheader("Where they boarded: st.map")
ports = pd.DataFrame({"port": ["Southampton", "Cherbourg", "Queenstown"], "Embarked": ["S", "C", "Q"],
                      "lat": [50.897, 49.645, 51.850], "lon": [-1.404, -1.616, -8.294]})
ports["passengers"] = ports["Embarked"].map(df["Embarked"].value_counts())
st.map(ports, size="passengers", zoom=4)

# ------------------------------------------------------------ 2. Plotly
st.header("2. Plotly figures")
fig = px.histogram(df, x="Age", color="Outcome", nbins=40, barmode="overlay",
                   color_discrete_map={"Died": "#D95D4A", "Survived": "#0F766E"})
st.plotly_chart(fig)   # hover, zoom and legend clicks still work inside the app

# ------------------------------------------------------------ 3. Matplotlib / Seaborn
st.header("3. Matplotlib and Seaborn figures")
fig, ax = plt.subplots(figsize=(8, 3.5))
sns.boxplot(df, x="Pclass", y="Fare", color="#0F766E", ax=ax)
ax.set(xlabel="Class", ylabel="Fare (£)", title="First class paid much more, and the spread is huge")
sns.despine()
st.pyplot(fig)   # a picture: no hover, no zoom
