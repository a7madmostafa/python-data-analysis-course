import streamlit as st

import charts as ch

data = st.session_state.data

st.title("🗺️ Where are the expensive listings?")
if data.empty:
    st.warning("No listing matches these filters.")
    st.stop()

st.caption(f"Up to 5,000 of the {len(data):,} filtered listings · colour = price per night (capped at $400)")
fig = ch.price_map(data)

ch.show(fig, "The map")
