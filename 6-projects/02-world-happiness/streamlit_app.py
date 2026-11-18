"""World Happiness 2021 dashboard.

    uv run streamlit run 6-projects/02-world-happiness/streamlit_app.py

Reads data/world_happiness_clean.csv (written by analysis.ipynb). The charts are in charts.py.
The Overview, Groups and Factors tabs show the countries that pass the sidebar filters.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

import charts as ch

st.set_page_config(page_title="World Happiness 2021", page_icon="😊", layout="wide")
DATA = Path(__file__).resolve().parents[2] / "data" / "world_happiness_clean.csv"


@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df["income_group"] = pd.Categorical(df["income_group"], ch.ORDERS["income_group"], ordered=True)
    return df


df = load_data(DATA)
st.title("😊 World Happiness 2021")
st.caption("149 countries · World Happiness Report 2021 (Gallup World Poll, 2018–2020) · cleaned in analysis.ipynb")

# ------------------------------------------------------------ filters (applied only when the button is pressed)
regions = sorted(df["region"].unique())
with st.sidebar.form("filters"):
    st.header("Filters")
    pick_regions = st.multiselect("Regions", regions, default=regions)
    pick_income = st.multiselect("Income group", ch.ORDERS["income_group"], default=ch.ORDERS["income_group"])
    low, high = st.slider("Happiness range", 2.0, 8.0, (2.0, 8.0), step=0.1)
    focus = st.selectbox("Focus country", sorted(df["country"]), index=sorted(df["country"]).index("Egypt"))
    st.form_submit_button("Apply", type="primary")

data = df[df["region"].isin(pick_regions) & df["income_group"].isin(pick_income) & df["happiness"].between(low, high)]
if data.empty:
    st.warning("No country passes these filters. Change them and press Apply.")
    st.stop()

overview, groups, factors, compare = st.tabs(["🌍 Overview", "📊 Groups", "🔍 Factors", "⚖️ Compare"])

with overview:
    ranks = data["happiness"].rank(ascending=False, method="min").astype(int)
    focus_rank = ranks[data["country"] == focus]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Countries", len(data), border=True)
    col2.metric("Average happiness", f"{data['happiness'].mean():.2f}", border=True)
    col3.metric("Happiest country", data.loc[data["happiness"].idxmax(), "country"], border=True)
    col4.metric(f"{focus}'s rank", f"{focus_rank.iloc[0]} / {len(data)}" if len(focus_rank) else "—", border=True)
    colour = st.selectbox("Map colour", ["happiness"] + ch.FACTORS, format_func=ch.LABELS.get)
    ch.show(ch.world_map(data, colour), "The world map", ch.LABELS[colour])
    ch.show(ch.happiness_hist(data, focus), "How happiness is spread", f"The red line is {focus}")

with groups:
    by = st.radio("Group by", ["region", "income_group"], horizontal=True, format_func=ch.LABELS.get)
    left, right = st.columns(2)
    with left:
        ch.show(ch.group_means(data, by), "Average happiness")
    with right:
        ch.show(ch.group_spread(data, by), "The spread", "Every dot is a country")

with factors:
    factor = st.selectbox("Factor", ch.FACTORS, format_func=ch.LABELS.get)
    left, right = st.columns([3, 1])
    with left:
        ch.show(ch.factor_scatter(data, factor, focus), f"{ch.LABELS[factor]} and happiness")
    with right:
        st.metric("Correlation", f"{data[factor].corr(data['happiness']):.2f}", border=True)
    ch.show(ch.corr_bars(data), "What goes with happiness, in these countries?", "Correlation with happiness")

with compare:
    others = st.multiselect(f"Compare {focus} with", sorted(df.loc[df["country"] != focus, "country"]),
                            default=["Finland"] if focus != "Finland" else ["Denmark"])
    column = st.radio("Compare by", ["happiness"] + ch.FACTORS, horizontal=True, format_func=ch.LABELS.get)
    picked = df[df["country"].isin([focus] + others)]
    ch.show(ch.compare_bars(picked, column, focus), f"{focus} vs the others: {ch.LABELS[column]}")
    table = picked[["country", "region", "rank", "happiness"] + ch.FACTORS].sort_values("rank")
    st.dataframe(table, hide_index=True, column_config={"happiness": st.column_config.NumberColumn(format="%.2f")})
    st.download_button("Download CSV", table.to_csv(index=False), "happiness_compare.csv", "text/csv")
