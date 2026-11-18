"""Build 4-visualization/01_principles.ipynb, the solved notebook of the "Why visualize, and which chart" lesson.

It merges our first Visualization draft with the earlier principles notebook: why draw at all, how the
question and the variable types pick the chart, what makes a chart clear, and how a correct chart can still
mislead. The libraries get their own chapters next (02_matplotlib, 03_seaborn, 04_plotly), so here the code
stays short and every chart is a static Matplotlib / Seaborn image (renders on GitHub, Kaggle and the site).

    python website/build/build_viz.py          # write + execute
    python website/build/build_viz.py --no-run # write only
"""
from pathlib import Path
import sys

from nb import code, execute, md, write

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "4-visualization" / "01_principles.ipynb"

cells = [
md("""
# 🎨 Why Visualize, and Which Chart?

**Zero Grad · Data Analysis course · Visualization, part 1**

> 📖 **The lesson (in Arabic), with diagrams and interactive widgets:** [zero-grad.com/courses/da/viz](https://zero-grad.com/courses/da/viz/)
>
> 🗂️ **The data:** [NileCart Sales on Kaggle](https://www.kaggle.com/datasets/a7madmostafa/nilecart-sales)

Before any plotting library, four questions: **why** draw a chart at all, **which** chart answers which question,
what makes a chart **clear**, and how a correct chart can still **mislead**. The examples use the NileCart sales table
(one row per order line, 2024–2025). The code is kept short; the next three chapters explain each library in full.

| # | Part | The idea |
|---|---|---|
| 1 | Why visualize? | Summary numbers can hide the shape; tables to look up, charts to see a pattern |
| 2 | Choosing the chart | The question and the variable types pick it; position and length beat angle and colour |
| 3 | A clear chart | Zero baseline, sorted, one highlight, a title that says the finding |
| 4 | Reading charts correctly | Counts or rates, mean or median, who is missing |
| 5 | The three libraries | Matplotlib, Seaborn, Plotly: which one when |
"""),
md("""
---
# 0️⃣ Setup
"""),
code("""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (9, 4)
TEAL, AMBER, CORAL, SLATE = "#0F766E", "#E89B2D", "#D95D4A", "#9AA5B1"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# On Kaggle the data lives under /kaggle/input, locally in the repo's data/nilecart/ folder
on_kaggle = sorted(Path("/kaggle/input").glob("**/sales.csv"))
DATA = on_kaggle[0].parent if on_kaggle else Path("../data/nilecart")

sales = pd.read_csv(DATA / "sales.csv", parse_dates=["order_date"])
done = sales[sales["status"] == "completed"].copy()        # revenue counts only for completed orders
done["year"] = done["order_date"].dt.year
done["month"] = done["order_date"].dt.month
print(len(sales), "order lines,", len(done), "completed")
"""),
md("""
---
# 1️⃣ Why visualize?

## 1.1 Same numbers, different data

Four small datasets, published by the statistician Francis Anscombe in 1973 to make exactly this point:
"""),
code("""
x = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5]
anscombe = pd.DataFrame({
    "set": np.repeat(["I", "II", "III", "IV"], 11),
    "x": x * 3 + [8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8],
    "y": [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68,
          9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74,
          7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73,
          6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89],
})
summary = anscombe.groupby("set").agg(x_mean=("x", "mean"), y_mean=("y", "mean"), y_std=("y", "std"))
summary["corr"] = anscombe.groupby("set").apply(lambda g: g["x"].corr(g["y"]), include_groups=False)
summary.round(2)
"""),
md("""
Same means, same standard deviation, same correlation. By the numbers, four copies of one dataset. Now draw them:
"""),
code("""
g = sns.lmplot(data=anscombe, x="x", y="y", col="set", col_wrap=4, height=2.6, ci=None,
               scatter_kws={"s": 35, "color": TEAL}, line_kws={"color": CORAL})
g.set_titles("set {col_name}")
plt.show()
"""),
md("""
A line, a curve, a line with one outlier, and a vertical stack with one far point. Four different stories, one summary table.

## 1.2 Same statistics, different years

NileCart's revenue per month, in million EGP. Every number is there, but you have to read 24 of them to find the story:
"""),
code("""
monthly = done.pivot_table(index="month", columns="year", values="revenue", aggfunc="sum")
(monthly / 1e6).round(2).set_axis(MONTHS).T
"""),
md("""
Summarised with the usual numbers, the two years look almost identical:
"""),
code("""
(monthly.agg(["mean", "std", "median"]) / 1e6).round(2)
"""),
md("""
The same 24 numbers as a line:
"""),
code("""
fig, ax = plt.subplots()
ax.plot(MONTHS, monthly[2024] / 1e6, marker="o", color=SLATE, label="2024")
ax.plot(MONTHS, monthly[2025] / 1e6, marker="o", color=TEAL, label="2025")
ax.set(title="Monthly revenue, 2024 vs 2025", ylabel="million EGP")
ax.legend()
plt.show()
"""),
md("""
Same mean, similar spread, two different years. 2024 starts low, jumps in September and peaks in December;
2025 starts higher, stays under 0.85M through October and peaks in November. Summary numbers squeeze a column into one value each;
a chart keeps the **pattern**: trends, seasonality, clusters, outliers and errors.

## 1.3 Number, table or chart?

* **A number** for one fact: "the median completed order line is worth 3,600 EGP".
* **A table** for exact values to look up: the price list, one customer's orders, September 2025's revenue.
* **A chart** for a pattern, a shape, a comparison or an outlier.

If one sentence says it, a chart is not needed. **Tables are for looking up a value. Charts are for seeing a pattern.**

## 1.4 Explore or explain?

| | Explore (for yourself) | Explain (for others) |
|---|---|---|
| How many | many quick charts, rough is fine | one chart per message, polished |
| Goal | find patterns, errors, new questions | the reader gets the point in five seconds |
| Title | says what is plotted: "Revenue by month" | says what it means: "Nov–Dec bring a third of the revenue" |

Exploratory data analysis (EDA) is mostly exploring; a report or a dashboard is explaining.
"""),
md("""
---
# 2️⃣ Choosing the right chart

## 2.1 Start from the question

Start from the question, not from the chart type. Almost every question about a table falls into one of six families,
and each family has its own charts:
"""),
code("""
fig, axes = plt.subplots(2, 3, figsize=(13, 7))

# distribution: what do the values look like?
sns.histplot(done["revenue"], bins=40, log_scale=True, color=TEAL, ax=axes[0, 0])
axes[0, 0].set(title="Distribution: revenue per line", xlabel="EGP (log)")

# comparison: which is bigger?
reg = done.groupby("region")["revenue"].sum().drop("Unknown").sort_values() / 1e6
axes[0, 1].barh(reg.index, reg.values, color=TEAL)
axes[0, 1].set(title="Comparison: revenue by region", xlabel="million EGP")

# relationship: do two numbers move together?
axes[0, 2].scatter(done["unit_price"], done["revenue"], s=8, alpha=.4, color=TEAL)
axes[0, 2].set(xscale="log", yscale="log", title="Relationship: price and revenue", xlabel="unit price", ylabel="revenue")

# composition: what is the whole made of?
share = done.groupby("category")["revenue"].sum().sort_values(ascending=False)
share = share / share.sum() * 100
left = 0
for color, (k, v) in zip([TEAL, AMBER, CORAL, SLATE], share.items()):
    axes[1, 0].barh([0], [v], left=left, color=color, label=f"{k} {v:.0f}%")
    if v > 10:
        axes[1, 0].text(left + v / 2, 0, f"{v:.0f}%", ha="center", va="center", color="white", fontweight="bold")
    left += v
axes[1, 0].set(title="Composition: revenue by category", xlabel="% of revenue", yticks=[], xlim=(0, 100))
axes[1, 0].legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2, frameon=False)

# change over time: how does it move?
per_month = done.groupby(done["order_date"].dt.to_period("M").dt.to_timestamp())["revenue"].sum()
axes[1, 1].plot(per_month.index, per_month / 1e6, marker=".", color=TEAL)
axes[1, 1].set(title="Change over time: revenue per month", ylabel="million EGP")
axes[1, 1].tick_params(axis="x", rotation=45)

# multivariate: several variables at once
pv = done.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum").drop(index="Unknown") / 1e6
sns.heatmap(pv, annot=True, fmt=".1f", cmap="Greens", cbar=False, ax=axes[1, 2])
axes[1, 2].set(title="Multivariate: region x category (M)", xlabel="", ylabel="")

plt.tight_layout()
plt.show()
"""),
md("""
| Question | Family | Typical charts |
|---|---|---|
| What do the values look like? | Distribution | histogram, box, violin |
| Which is bigger? Who's first? | Comparison & ranking | sorted bar, dot plot |
| Do two numbers move together? | Relationship | scatter, heatmap of correlations |
| What is the whole made of? | Composition | stacked bar, treemap (pie only for a few parts) |
| How does it change over time? | Change over time | line, area |
| Several variables at once? | Multivariate | heatmap, small multiples, maps |

One question, one chart. A chart that tries to answer three questions answers none.

## 2.2 Then look at the variable types

| Type | Example in `sales` | Typical encoding |
|---|---|---|
| Numerical, continuous | `revenue`, `profit` | position on a scale (x / y) |
| Numerical, discrete | `quantity` | position, or one bar per value |
| Categorical, nominal | `category`, `region` | separate bars, colour hue |
| Categorical, ordinal | discount level 0 / 5 / 10 / 20% | bars or a line, kept in order |
| Time | `order_date`, month | x-axis from left to right, usually a line |

⚠️ An ordinal or time axis is never sorted by value: the order is part of the data.

## 2.3 Position and length beat angle and colour

People compare **positions** on a common scale and **lengths** precisely; angles, areas and colour shades much less so.
The same five numbers as a bar chart and as a pie:
"""),
code("""
reg = done.groupby("region")["revenue"].sum().drop("Unknown").sort_values(ascending=False) / 1e6

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
bars = a1.bar(reg.index.str.replace(" & Coast", ""), reg.values, color=TEAL)
a1.bar_label(bars, fmt="%.1fM")
a1.set(title="Bar: compare lengths", ylabel="million EGP")
a1.tick_params(axis="x", rotation=20)
a2.pie(reg.values, labels=reg.index, colors=[TEAL, AMBER, CORAL, SLATE, "#152B3C"], startangle=90, counterclock=False)
a2.set(title="Pie: compare angles")
fig.suptitle("Revenue by region", fontweight="bold")
plt.tight_layout()
plt.show()
"""),
md("""
On the pie, Delta, Upper Egypt and Canal look about the same size; on the bars, the ranking reads at a glance
(2.0M, 1.8M, 1.6M EGP). From most to least precise: **position → length → angle / area → colour shade → colour hue**.
A pie is acceptable only for a few parts (at most about five) of one whole, when rough shares are enough.

## 2.4 The chart selection table

| Chart | Best used for | What to read |
|---|---|---|
| Bar chart | comparing categories | differences, ranking |
| Line chart | trends over time or an ordered sequence | direction, change, seasonality |
| Histogram | the distribution of one number | shape, spread, skew |
| Scatter plot | the relationship of two numbers | association, clusters, odd points |
| Box plot | comparing distributions | median, quartiles, outliers |
| Violin plot | comparing distribution shapes | density, several peaks |
| Count plot | the frequency of categories | most and least common |
| Stacked bar | the composition of categories | totals and their parts |
| Heatmap | values across two dimensions | hot spots, patterns |
| Pair plot | several numeric variables | every pairwise relationship |
| Pie chart | a few parts of one whole | rough proportions (≤ 5 slices) |

The same question with different variables can need a different chart: *"how does revenue differ by category?"* is a bar
chart of a total, but a box plot when the question is about the spread of single order lines.
"""),
md("""
---
# 3️⃣ A clear chart

## 3.1 Fix it one rule at a time

The same data, revenue by region, drawn badly and then fixed:
"""),
code("""
reg = done.groupby("region")["revenue"].sum().drop("Unknown")

fig, ax = plt.subplots(figsize=(8, 3.6))
ax.bar(reg.index, reg.values, color=sns.color_palette("hls", len(reg)))
ax.set_ylim(1.5e6, None)
ax.set_title("Chart 1")
plt.show()
"""),
md("""
What's wrong:

* **The axis starts at 1.5M**, so Canal's bar is almost nothing: Greater Cairo looks about 75 times bigger instead of 6.
* **Alphabetical order**: you have to search for the biggest and the smallest.
* **Rainbow colours** that mean nothing: the eye looks for a meaning that isn't there.
* **No units, a title that says nothing**, and `1e7` in the corner.
"""),
code("""
reg = reg.sort_values() / 1e6                                   # sort, and use readable units
colors = [SLATE] * len(reg)
colors[-1] = TEAL                                               # one highlight: the point of the chart

fig, ax = plt.subplots(figsize=(8, 3.6))
bars = ax.barh(reg.index, reg.values, color=colors)            # horizontal: long labels read easily
ax.bar_label(bars, fmt="%.1fM", padding=3)                      # label the bars, drop the grid
ax.set_xlim(0, reg.max() * 1.15)                                # bars start at zero
ax.set(xlabel="revenue, million EGP", ylabel="")
ax.set_title("Greater Cairo brings half of NileCart's revenue", loc="left", fontweight="bold")
ax.grid(False)
sns.despine(left=True, bottom=True)
ax.set_xticks([])
plt.show()
"""),
code("""
print(f"Greater Cairo share: {reg['Greater Cairo'] / reg.sum():.0%}")
print(f"Greater Cairo / Canal: {reg['Greater Cairo'] / reg['Canal']:.1f}x, "
      f"on the cut axis: {(reg['Greater Cairo'] - 1.5) / (reg['Canal'] - 1.5):.0f}x")
"""),
md("""
| Rule | Why |
|---|---|
| Bars start at **zero** | a bar's length *is* its value; cut the axis and you lie about the ratio |
| **Sort** by value | the ranking is visible without reading |
| **One** highlight colour, grey for the rest | colour means something, so use it once, for the point |
| A **title that says the finding** | "Greater Cairo brings half" beats "Revenue by region" |
| **Units** in the label, readable numbers | 9.9M, not 9912413.2 or 1e7 |
| Label directly, remove what doesn't help | gridlines, legends and borders are ink that says nothing |

A line chart is different: it encodes by position, not length, so its axis may zoom in (and should then be clearly labelled).

## 3.2 Anatomy of an honest chart

1. a **title** that states the message,
2. **axis labels** with the unit (EGP, %, count),
3. a **scale** that starts at 0 for bars, with readable ticks,
4. a **legend** only when there are several series,
5. an **annotation** pointing at the one thing to notice,
6. a **source or note** saying where the data came from.
"""),
code("""
nov_dec = monthly.loc[[11, 12]].sum() / monthly.sum()

fig, ax = plt.subplots(figsize=(9, 4.4))
ax.plot(MONTHS, monthly[2024] / 1e6, marker="o", color=SLATE, label="2024")
ax.plot(MONTHS, monthly[2025] / 1e6, marker="o", color=TEAL, label="2025")
ax.set_ylim(0, None)
ax.set(ylabel="revenue, million EGP")
ax.set_title(f"Nov–Dec bring {nov_dec.mean():.0%} of the year's revenue, every year", loc="left", fontweight="bold")
ax.annotate("White Friday + New Year", xy=(11, monthly.loc[12, 2024] / 1e6), xytext=(6.3, 1.9),
            arrowprops=dict(arrowstyle="->", color="gray"))
ax.legend(loc="upper left", frameon=False)
fig.text(0.01, -0.02, "Source: NileCart sales, completed orders, 2024–2025", color="gray", fontsize=9)
sns.despine()
plt.show()
"""),
md("""
---
# 4️⃣ Reading charts correctly

A chart can be computed correctly and still mislead. A cut bar axis is the first trap (part 3). Three more:

## 4.1 Counts or rates?

Bigger groups have more of everything. To compare groups of different sizes, divide by the size.
Returns, over all order lines:
"""),
code("""
ret = (sales.assign(returned=sales["status"].eq("returned"))
            .groupby("category")["returned"].agg(lines="size", returns="sum", rate="mean"))
ret["rate"] = (ret["rate"] * 100).round(1)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.6))
a1.bar_label(a1.bar(ret.index, ret["returns"], color=SLATE))
a1.set(title="Number of returns")
a2.bar_label(a2.bar(ret.index, ret["rate"], color=TEAL), fmt="%.1f%%")
a2.set(title="Return rate (%)")
fig.suptitle("Returned order lines by category", fontweight="bold")
plt.tight_layout()
plt.show()
ret
"""),
md("""
Accessories have almost three times as many returns as Furniture (29 vs 10), yet the two rates are close (4.8% vs 4.0%):
Accessories simply sell more. The rate is what shows the real problem, Electronics, where one order line in seven comes back.

## 4.2 Average or median?

On a skewed column the mean and the median tell different stories, and a chart should say which one it shows:
"""),
code("""
mean, median = done["revenue"].mean(), done["revenue"].median()
print(f"mean {mean:,.0f} | median {median:,.0f} | skew {done['revenue'].skew():.1f}")

fig, ax = plt.subplots()
ax.hist(done.loc[done["revenue"] < 40_000, "revenue"], bins=60, color=SLATE)
ax.axvline(median, color=TEAL, lw=3, label=f"median {median:,.0f}")
ax.axvline(mean, color=CORAL, lw=3, label=f"mean {mean:,.0f}")
ax.set(title="A few large orders pull the mean far above the typical order",
       xlabel="revenue per order line (EGP), lines under 40,000", ylabel="order lines")
ax.legend()
plt.show()
"""),
md("""
For skewed data, report the median, or show the whole distribution. The same goes for *count* vs *%* vs *average*:
an axis label always says which one.

## 4.3 Who is missing, and how many are there?

* **Sampling bias:** the sales table only holds people who bought. Customers who never ordered, or left after one bad
  experience, are invisible. The question to ask is *who could not end up in this data?*
* **Tiny groups:** a rate or an average from a handful of rows is noise. Show the group size next to it, or leave the group out:
"""),
code("""
done.groupby("segment")["revenue"].agg(order_lines="size", mean_revenue="mean").round(0)
"""),
md("""
The *Unknown* segment (the one completed order whose customer is missing) is a single row; its average says nothing.

## 4.4 Before trusting a chart

1. **Axis:** does a bar axis start at 0? Is it linear or log?
2. **Measure:** count, %, mean or median? Per what?
3. **Shape:** would other bins or a log scale change the story?
4. **Groups:** are some groups tiny? Who is missing?
5. **Cause:** could a third factor explain the pattern? (A correlation between two columns can come from a third one,
   or reverse inside groups; the [Seaborn chapter](03_seaborn.ipynb) shows an example.)
"""),
md("""
---
# 5️⃣ The three libraries

Every chart above is Matplotlib, some drawn through Seaborn. The next three chapters take one library each:

| | [Matplotlib](02_matplotlib.ipynb) | [Seaborn](03_seaborn.ipynb) | [Plotly](04_plotly.ipynb) |
|---|---|---|---|
| Style | every detail by hand: `fig, ax = plt.subplots()` | statistical charts from a DataFrame: `data=, x=, y=, hue=` | interactive charts from a DataFrame: `px.line(df, x=, y=)` |
| Aggregates for you | no | yes (`estimator=`, the mean by default) | histogram and box yes, bar no |
| Output | image | image (drawn by Matplotlib) | web page: hover, zoom, hide a series |
| Best for | a final chart for a report, full control | exploring fast, statistics, small multiples | dashboards, sharing on the web |

Pick one for exploring (Seaborn is quickest), and know the others exist.
"""),
md("""
---
# 🧰 Summary

* **Draw before you summarise**: the same summary numbers can come from very different data.
* **Tables to look up, charts to see a pattern**; explore with many rough charts, explain with one polished chart.
* **Start from the question** (distribution, comparison, relationship, composition, change over time, multivariate),
  then the variable types. Position and length are read best; angle and colour worst.
* **A clear chart**: zero baseline for bars, sorted, one highlight, a title with the finding, units, nothing extra.
* **Read it critically**: counts or rates, mean or median, tiny groups, who is missing.

---
**Next:** [Matplotlib](02_matplotlib.ipynb), the library under most Python charts.

📚 All the lessons of the course: [zero-grad.com/courses/da](https://zero-grad.com/courses/da/)
"""),
]

if __name__ == "__main__":
    path = write(cells, OUT, "Why Visualize, and Which Chart")
    print("wrote", path)
    if "--no-run" not in sys.argv:
        execute(path)
        print("executed", path)
