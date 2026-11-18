import streamlit as st

import charts as ch

data = st.session_state.data

st.title("🗽 New York City · Airbnb listings")
st.caption("What drives the price of an Airbnb? Use the filters on the left, then click Apply.")

if data.empty:
    st.warning("No listing matches these filters.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Listings", f"{len(data):,}", border=True)
col2.metric("Hosts", f"{data['host_id'].nunique():,}", border=True)
col3.metric("Median price", f"${data['price'].median():.0f}", border=True)
col4.metric("Entire homes", f"{(data['room_type'] == 'Entire home').mean():.0%}", border=True)

left, right = st.columns(2)
with left:
    ch.show(ch.listings_by_borough(data), "Listings by borough", "Where are the listings?")
with right:
    ch.show(ch.room_donut(data), "Room types", "What do people rent?")

ch.show(ch.borough_room_heatmap(data), "Median price: borough × room type",
        "Which segment is the most and the least expensive?")
