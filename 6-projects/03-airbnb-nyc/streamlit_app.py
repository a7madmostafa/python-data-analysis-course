"""NYC Airbnb dashboard.

    uv run streamlit run 6-projects/03-airbnb-nyc/streamlit_app.py

The data, the sidebar filters and the navigation; the pages are in views/, the charts in charts.py.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="NYC Airbnb", page_icon="🗽", layout="wide")

DATA = Path(__file__).resolve().parents[2] / "data" / "airbnb" / "airbnb_cleaned.csv"


@st.cache_data
def load_data(path):
    return pd.read_csv(path)


df = load_data(DATA)

with st.sidebar.form("filters"):
    st.header("Filters")
    boroughs = st.multiselect("Borough", ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"],
                              placeholder="All boroughs")
    rooms = st.multiselect("Room type", ["Entire home", "Private room", "Shared room"], placeholder="All room types")
    prices = st.slider("Price per night ($)", 0, 1000, (0, 1000), step=10)
    st.form_submit_button("Apply", type="primary")
st.sidebar.caption("Inside Airbnb, July 2019 · cleaned in analysis.ipynb")

mask = df["price"].between(*prices)
if boroughs:
    mask &= df["borough"].isin(boroughs)
if rooms:
    mask &= df["room_type"].isin(rooms)
st.session_state.data = df[mask]

pages = [
    st.Page("views/overview.py", title="Overview", icon=":material/dashboard:", default=True),
    st.Page("views/prices.py", title="Prices", icon=":material/payments:"),
    st.Page("views/map.py", title="Map", icon=":material/map:"),
    st.Page("views/listings.py", title="Listings", icon=":material/table:"),
]
st.navigation(pages, position="top").run()
