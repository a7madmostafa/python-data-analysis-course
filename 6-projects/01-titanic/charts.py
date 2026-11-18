"""charts.py · one function per chart, shared by analysis.ipynb and streamlit_app.py.

Every function takes the (filtered) clean passenger table and returns a Plotly figure.
The colours, the labels, the category orders and px.defaults are set once here, so each chart stays short.
show() puts a figure in a card on the page.
"""
import pandas as pd
import plotly.express as px
import streamlit as st

TEAL, ORANGE, RED, INK, GRAY = "#0F766E", "#E89B2D", "#D95D4A", "#152B3C", "#7C8B96"

ORDERS = {
    "class": ["1st", "2nd", "3rd"],
    "sex": ["female", "male"],
    "port": ["Southampton", "Cherbourg", "Queenstown"],
    "title": ["Mr", "Mrs", "Miss", "Master", "Rare"],
    "age_group": ["Child (0-12)", "Teen (13-17)", "Adult (18-59)", "Senior (60+)"],
    "family": ["Alone", "2-4", "5+"],
    "outcome": ["Survived", "Died"],
}
LABELS = {"class": "Class", "sex": "Sex", "port": "Port", "title": "Title", "age_group": "Age group",
          "family": "Family size", "outcome": "Outcome", "age": "Age", "fare": "Fare (£)",
          "survived": "Survival rate", "passengers": "Passengers"}
OUTCOME_COLORS = {"Survived": TEAL, "Died": RED}
GROUPS = ["sex", "class", "age_group", "title", "family", "port"]      # the columns a survival rate can be split by

px.defaults.template = "simple_white"
px.defaults.height = 360
px.defaults.labels = LABELS
px.defaults.category_orders = ORDERS
px.defaults.color_discrete_sequence = [TEAL]


def clean(fig):
    """No legend title, small margins (the card or the caller sets the title)."""
    fig.update_layout(legend_title=None, margin={"l": 10, "r": 10, "t": 30, "b": 10})
    return fig


def show(fig, title, question=""):
    """A chart card: a title, the question it answers, then the chart."""
    with st.container(border=True):
        st.markdown(f"**{title}**")
        if question:
            st.caption(question)
        st.plotly_chart(fig, config={"displayModeBar": False})


def rates(data, col):
    """Survival rate and number of passengers for each group of one column."""
    return (data.groupby(col, observed=True)["survived"].agg(survived="mean", passengers="size")
            .reindex([g for g in ORDERS[col] if g in set(data[col])]).reset_index())


# ------------------------------------------------------------ survival
def rate_bar(data, col):
    """The survival rate of each group, the passenger count on hover, the overall rate as a dashed line."""
    fig = px.bar(rates(data, col), x=col, y="survived", text_auto=".0%", hover_data=["passengers"])
    fig.add_hline(data["survived"].mean(), line_dash="dash", line_color=GRAY, annotation_text="all passengers")
    return clean(fig.update_yaxes(tickformat=".0%", range=[0, 1]))


def rate_heatmap(data, row="class", col="sex"):
    """The survival rate for every combination of two columns."""
    table = data.pivot_table(index=row, columns=col, values="survived", aggfunc="mean", observed=True)
    table = table.reindex(index=[g for g in ORDERS[row] if g in table.index],
                          columns=[g for g in ORDERS[col] if g in table.columns])
    fig = px.imshow(table, text_auto=".0%", color_continuous_scale="RdYlGn", zmin=0, zmax=1, aspect="auto",
                    labels={"color": "survived"})
    return clean(fig.update_layout(coloraxis_showscale=False))


def rate_by_two(data, col="class", color="sex"):
    """The survival rate by one column, split by a second one (grouped bars)."""
    table = (data.groupby([col, color], observed=True)["survived"].agg(survived="mean", passengers="size")
             .reset_index())
    fig = px.bar(table, x=col, y="survived", color=color, barmode="group", text_auto=".0%",
                 hover_data=["passengers"], color_discrete_sequence=[TEAL, ORANGE, RED, INK, GRAY])
    return clean(fig.update_yaxes(tickformat=".0%", range=[0, 1]))


# ------------------------------------------------------------ who was on board
def count_bar(data, col):
    fig = px.histogram(data, x=col, text_auto=True)
    return clean(fig.update_layout(yaxis_title="Passengers"))


def port_mix(data):
    """The share of each class among the passengers of each port."""
    mix = (pd.crosstab(data["port"], data["class"], normalize="index").reset_index()
           .melt(id_vars="port", var_name="class", value_name="share"))
    fig = px.bar(mix, x="share", y="port", color="class", orientation="h", text_auto=".0%",
                 color_discrete_sequence=[INK, GRAY, ORANGE])
    return clean(fig.update_xaxes(tickformat=".0%").update_yaxes(title=None))


# ------------------------------------------------------------ ages and fares
def age_hist(data):
    """Known ages only, survivors and victims overlaid."""
    known = data[data["age_known"]]
    fig = px.histogram(known, x="age", color="outcome", nbins=40, barmode="overlay", opacity=0.6,
                       color_discrete_map=OUTCOME_COLORS)
    return clean(fig.update_layout(yaxis_title="Passengers"))


def fare_box(data):
    """Fare per class on a log axis (the 15 free tickets are left out: log(0) does not exist)."""
    paid = data[data["fare"] > 0]
    fig = px.box(paid, x="class", y="fare", color="outcome", log_y=True, points=False,
                 color_discrete_map=OUTCOME_COLORS)
    return clean(fig)
