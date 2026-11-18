import streamlit as st

import charts as ch

data = st.session_state.data

st.title("💵 Prices")
if data.empty:
    st.warning("No listing matches these filters.")
    st.stop()

ch.show(ch.price_histogram(data), "Price distribution", "What does a typical listing cost?")

labels = {"room_type": "Room type", "borough": "Borough", "distance_band": "Distance to Times Square",
          "host_type": "Host type"}
col = st.radio("Compare the median price by", list(labels), format_func=labels.get, horizontal=True)
ch.show(ch.median_bar(data, col), f"Median price by {labels[col].lower()}",
        "The dashed line is the median of all the filtered listings.")

n = st.slider("How many neighbourhoods?", 5, 20, 10)
ch.show(ch.top_neighbourhoods(data, n=n), f"The {n} most expensive neighbourhoods",
        "Median price, neighbourhoods with 20+ listings only")
