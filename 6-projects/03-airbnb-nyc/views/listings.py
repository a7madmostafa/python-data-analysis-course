import streamlit as st

data = st.session_state.data

st.title("📋 Listings")

words = st.text_input("Search the listing names", placeholder="e.g. loft, park, cozy")
found = data[data["name"].str.contains(words, case=False, na=False)] if words else data
st.write(f"{len(found):,} listings")

st.dataframe(
    found[["name", "borough", "neighbourhood", "room_type", "price", "number_of_reviews", "distance_km"]],
    hide_index=True,
    column_config={
        "name": "Listing",
        "room_type": "Room type",
        "price": st.column_config.NumberColumn("Price per night", format="$%d"),
        "number_of_reviews": "Reviews",
        "distance_km": st.column_config.NumberColumn("To Times Square", format="%.1f km"),
    },
)

st.download_button("⬇️ Download these listings (CSV)", data=found.to_csv(index=False),
                   file_name="airbnb_listings.csv", mime="text/csv", on_click="ignore")
