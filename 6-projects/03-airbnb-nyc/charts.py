"""charts.py · one function per chart.

Every function takes the FILTERED data and returns a Plotly figure.
The colours, the category orders and px.defaults are set once here, so each chart stays a few lines long.
show() puts a figure in a card on the page.
"""
import plotly.express as px
import streamlit as st

BLUE, ORANGE, GREEN, GRAY = "#0F766E", "#E89B2D", "#D95D4A", "#7C8B96"

ORDERS = {
    "room_type": ["Entire home", "Private room", "Shared room"],
    "borough": ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"],
    "distance_band": ["< 2 km", "2-5 km", "5-10 km", "10+ km"],
    "host_type": ["1 listing", "2-5 listings", "6+ listings"],
}

px.defaults.template = "simple_white"
px.defaults.height = 340
px.defaults.category_orders = ORDERS
px.defaults.color_discrete_sequence = [BLUE]
px.defaults.color_discrete_map = dict(zip(ORDERS["room_type"], [BLUE, ORANGE, GREEN]))


def clean(fig):
    """No axis or legend titles (the card shows the title), small margins."""
    fig.update_layout(xaxis_title=None, yaxis_title=None, legend_title=None,
                      margin={"l": 10, "r": 10, "t": 30, "b": 10})
    return fig


def show(fig, title, question=""):
    """A chart card: a title, the question it answers, then the chart."""
    with st.container(border=True):
        st.markdown(f"**{title}**")
        if question:
            st.caption(question)
        st.plotly_chart(fig, config={"displayModeBar": False})


# ------------------------------------------------------------ counts and shares
def listings_by_borough(data):
    return clean(px.histogram(data, x="borough", text_auto=","))


def room_donut(data):
    counts = data["room_type"].value_counts().reset_index()     # 3 rows instead of every listing
    return clean(px.pie(counts, names="room_type", values="count", color="room_type", hole=0.6))


def median_bar(data, col):
    """Median price per group + a dashed line at the overall median."""
    medians = data.groupby(col, as_index=False)["price"].median()
    fig = px.bar(medians, x=col, y="price", text_auto="$.0f")
    fig.add_hline(data["price"].median(), line_dash="dash", line_color=GRAY, annotation_text="overall median")
    return clean(fig)


# ------------------------------------------------------------ prices
def price_histogram(data):
    fig = px.histogram(data, x="price", nbins=60)
    fig.add_vline(data["price"].median(), line_dash="dash", line_color=GRAY, annotation_text="median")
    return clean(fig)


def borough_room_heatmap(data):
    table = data.pivot_table(index="borough", columns="room_type", values="price", aggfunc="median")
    table = table.reindex(index=ORDERS["borough"], columns=ORDERS["room_type"]).dropna(how="all")
    fig = px.imshow(table, text_auto="$.0f", color_continuous_scale="Blues", aspect="auto")
    return clean(fig.update_layout(coloraxis_showscale=False))


def top_neighbourhoods(data, n=10, min_listings=20):
    stats = data.groupby("neighbourhood")["price"].agg(["median", "size"])
    top = stats[stats["size"] >= min_listings].nlargest(n, "median").reset_index()
    fig = px.bar(top, x="median", y="neighbourhood", orientation="h", text_auto="$.0f",
                 height=max(340, 28 * len(top)))
    return clean(fig.update_yaxes(autorange="reversed"))


def price_map(data, sample_size=5000):
    sample = data.sample(min(sample_size, len(data)), random_state=1)
    fig = px.scatter_map(sample, lat="latitude", lon="longitude", color="price",
                         color_continuous_scale="Blues", range_color=[0, 400],
                         hover_name="name", hover_data=["room_type", "neighbourhood"],
                         zoom=10, height=560, map_style="carto-positron")
    return clean(fig)
