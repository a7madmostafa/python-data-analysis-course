"""03 · Data: tables and big numbers

    uv run streamlit run 5-streamlit/apps/03_data.py

The passenger list three ways: an interactive table, a static table, and metrics.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path(__file__).resolve().parents[2] / "data" / "titanic.csv"
df = pd.read_csv(DATA)

st.title("Titanic passengers: the data")

# 1) st.dataframe: interactive. Click a header to sort; hover for search, full screen and CSV download.
st.subheader("st.dataframe: the interactive table")
st.dataframe(df, hide_index=True)

# column_config changes how a column LOOKS (name, format), not the data
st.dataframe(
    df[["Name", "Pclass", "Sex", "Age", "Fare", "Survived"]].head(20),
    hide_index=True,
    column_config={
        "Pclass": "Class",
        "Age": st.column_config.NumberColumn("Age", format="%d years"),
        "Fare": st.column_config.NumberColumn("Fare", format="£%.2f"),
        "Survived": "Survived (1 = yes)",
    },
)

# 2) st.table: static. Good for a small summary you want printed as it is.
st.subheader("st.table: a small summary")
summary = df.groupby("Pclass").agg(passengers=("Survived", "size"), survival_rate=("Survived", "mean")).round(2)
st.table(summary)

# 3) st.metric: one big number, with an optional delta (a change, or a difference to something)
st.subheader("st.metric: the numbers people look at first")
women = df.loc[df["Sex"] == "female", "Survived"].mean()
men = df.loc[df["Sex"] == "male", "Survived"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Passengers", len(df), border=True)
col2.metric("Survival rate", f"{df['Survived'].mean():.0%}", border=True)
col3.metric("Women who survived", f"{women:.0%}", delta=f"{women - men:+.0%} vs men", border=True)
