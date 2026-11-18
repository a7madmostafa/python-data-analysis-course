"""charts.py · one function per chart, shared by analysis.ipynb and streamlit_app.py.

Every function takes the (filtered) clean table, one row per country, and returns a Plotly figure.
The colours, the labels and px.defaults are set once here, so each chart stays a few lines.
show() puts a figure in a card on the page.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

TEAL, ORANGE, RED, INK, GRAY = "#0F766E", "#E89B2D", "#D95D4A", "#152B3C", "#7C8B96"

FACTORS = ["log_gdp", "social_support", "life_expectancy", "freedom", "generosity", "corruption"]
LABELS = {
    "happiness": "Happiness (0-10)",
    "log_gdp": "log GDP per person",
    "social_support": "Social support",
    "life_expectancy": "Healthy life expectancy",
    "freedom": "Freedom",
    "generosity": "Generosity",
    "corruption": "Corruption",
    "region": "Region",
    "income_group": "Income group",
    "gdp_usd": "GDP per person (USD)",
}
ORDERS = {"income_group": ["Low", "Middle", "High"]}

px.defaults.template = "simple_white"
px.defaults.height = 380
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


def mark(fig, data, x, y, country):
    """A red dot and a label on one country, if it is in the data."""
    row = data[data["country"] == country]
    if len(row):
        fig.add_scatter(x=row[x], y=row[y], mode="markers+text", text=[country], textposition="top left",
                        marker={"color": RED, "size": 12}, textfont={"color": RED}, showlegend=False,
                        hoverinfo="skip")
    return fig


# ------------------------------------------------------------ one column
def happiness_hist(data, focus="Egypt"):
    fig = px.histogram(data, x="happiness", nbins=15)
    row = data[data["country"] == focus]
    if len(row):
        fig.add_vline(row["happiness"].iloc[0], line_color=RED, line_width=2, annotation_text=focus,
                      annotation_font_color=RED)
    return clean(fig.update_layout(yaxis_title="Countries"))


def world_map(data, column="happiness"):
    fig = px.choropleth(data, locations="country", locationmode="country names", color=column,
                        hover_name="country", color_continuous_scale="Viridis", height=480)
    return clean(fig.update_layout(margin={"l": 0, "r": 0, "t": 10, "b": 0}))


# ------------------------------------------------------------ groups
def group_means(data, by="region"):
    means = data.groupby(by, observed=True)["happiness"].mean().sort_values(ascending=False).round(2).reset_index()
    fig = px.bar(means, x="happiness", y=by, orientation="h", text_auto=".2f")
    return clean(fig.update_yaxes(autorange="reversed", title=None))


def group_spread(data, by="region"):
    """Box plot per group, every country as a dot, groups sorted by their median."""
    order = data.groupby(by, observed=True)["happiness"].median().sort_values(ascending=False).index.tolist()
    fig = px.box(data, x="happiness", y=by, points="all", hover_name="country", category_orders={by: order})
    return clean(fig.update_yaxes(title=None))


# ------------------------------------------------------------ factors
def factor_scatter(data, factor="log_gdp", focus="Egypt", trend=True):
    fig = px.scatter(data, x=factor, y="happiness", hover_name="country", opacity=0.7,
                     trendline="ols" if trend else None, trendline_color_override=GRAY)
    return clean(mark(fig, data, factor, "happiness", focus))


def corr_bars(data):
    """The correlation of each factor with happiness, strongest (by size) first."""
    r = (data[FACTORS].corrwith(data["happiness"]).round(2).rename("r").rename_axis("factor").reset_index()
         .assign(label=lambda t: t["factor"].map(LABELS)))
    r = r.reindex(r["r"].abs().sort_values(ascending=False).index)
    fig = px.bar(r, x="r", y="label", orientation="h", text_auto=".2f", color=np.where(r["r"] > 0, "+", "−"),
                 color_discrete_map={"+": TEAL, "−": RED})
    return clean(fig.update_yaxes(autorange="reversed", title=None).update_layout(showlegend=False))


def corr_heatmap(data):
    cols = ["happiness"] + FACTORS
    corr = data[cols].corr().round(2).rename(index=LABELS, columns=LABELS)
    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto",
                    height=500)
    return clean(fig)


def support_by_income(data):
    """Social support vs happiness, one panel per income group, with a trend line in each."""
    fig = px.scatter(data, x="social_support", y="happiness", facet_col="income_group", hover_name="country",
                     trendline="ols", trendline_color_override=RED, opacity=0.7)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1] + " income"))
    return clean(fig)


# ------------------------------------------------------------ one country
def parts_bars(parts):
    """A country's score cut into the report's 7 parts (a Series), as horizontal bars."""
    p = parts.sort_values().rename("points").rename_axis("part").reset_index()
    fig = px.bar(p, x="points", y="part", orientation="h", text_auto=".2f")
    return clean(fig.update_yaxes(title=None))


def compare_bars(table, column="happiness", focus="Egypt"):
    """One column for a few countries, the focus country in its own colour."""
    t = table.sort_values(column, ascending=False).assign(
        who=lambda d: np.where(d["country"] == focus, focus, "Other"))
    fig = px.bar(t, x="country", y=column, color="who", text_auto=".2f",
                 color_discrete_map={focus: RED, "Other": TEAL})
    return clean(fig.update_layout(showlegend=False, xaxis_title=None))


def to_clean(raw):
    """The report's file → the clean table used everywhere (renamed columns, rank, GDP in USD, income group)."""
    df = raw.rename(columns={
        "Country name": "country", "Regional indicator": "region", "Ladder score": "happiness",
        "Logged GDP per capita": "log_gdp", "Social support": "social_support",
        "Healthy life expectancy": "life_expectancy", "Freedom to make life choices": "freedom",
        "Generosity": "generosity", "Perceptions of corruption": "corruption",
    })[["country", "region", "happiness"] + FACTORS].copy()
    df["rank"] = df["happiness"].rank(ascending=False).astype(int)
    df["gdp_usd"] = np.exp(df["log_gdp"]).round(-1)
    df["income_group"] = pd.qcut(df["log_gdp"], 3, labels=ORDERS["income_group"])
    return df
