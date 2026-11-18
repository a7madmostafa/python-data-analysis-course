"""Build 2-numpy/numpy.ipynb (the solved companion notebook of the NumPy lesson).

    python build/build_numpy.py          # write + execute
    python build/build_numpy.py --no-run # write only
"""
from pathlib import Path
import sys

from nb import code, execute, md, write

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "2-numpy" / "numpy.ipynb"

cells = [
md("""
# 🔢 NumPy: computing on a whole column at once

**Zero Grad · Data Analysis course · Foundations**

> 📖 **The lesson (in Arabic), with diagrams and interactive widgets:** [zero-grad.com/courses/da/numpy](https://zero-grad.com/courses/da/numpy/)
>
> 🗂️ **The data:** [NileCart Sales on Kaggle](https://www.kaggle.com/datasets/a7madmostafa/nilecart-sales)

This is the solved notebook of the *NumPy* lesson.
Pandas is built on NumPy: every column of a DataFrame is a NumPy array underneath.
Learn the array once, and filtering, `sum()`, `mean()` and `groupby` in Pandas will all make sense.

| # | Part | The idea |
|---|---|---|
| 1 | Why NumPy | A list is a container, an array is a column of numbers |
| 2 | Making arrays and `dtype` | One type per array, and `NaN` is a float |
| 3 | Shape and `reshape` | 24 months become a (2 × 12) table |
| 4 | Indexing and slicing | `M[row, column]`, and a slice is a view |
| 5 | Boolean masks | Filter with a condition: `r[r > 100_000]` |
| 6 | Aggregation and `axis` | Collapse rows, or collapse columns |
| 7 | Broadcasting | Different shapes that still work together |
| 8 | Sorting | `sort`, and `argsort` to reorder another array |
"""),
md("""
---
# 0️⃣ Setup
"""),
code("""
from pathlib import Path
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.figsize"] = (9, 4)
pd.options.display.float_format = "{:,.2f}".format
np.set_printoptions(suppress=True, linewidth=110)

# On Kaggle the data lives under /kaggle/input, locally in the repo's data/nilecart/ folder
on_kaggle = sorted(Path("/kaggle/input").glob("**/sales.csv"))
DATA = on_kaggle[0].parent if on_kaggle else Path("../data/nilecart")

sales = pd.read_csv(DATA / "sales.csv", parse_dates=["order_date"])
done = sales[sales["status"] == "completed"]

r = done["revenue"].to_numpy()          # the revenue of every completed order line
cat = done["category"].to_numpy()       # and its category, in the same order
prod = done["product_name"].to_numpy()
print(len(r), "completed order lines")
"""),
md("""
---
# 1️⃣ Why NumPy?

## 1.1 A list is not a column of numbers

The same `* 2` means two different things:
"""),
code("""
prices_list = [63, 30400, 57]
prices = np.array(prices_list)

print("list * 2: ", prices_list * 2)     # repeats the list
print("array * 2:", prices * 2)          # doubles every number
"""),
code("""
try:
    prices_list * 1.14
except TypeError as e:
    print("list * 1.14 ->", e)
print("array * 1.14 ->", prices * 1.14)
"""),
md("""
A list is a **container**: it holds anything, and `*` repeats it.
An array is a **column of numbers**: arithmetic happens to every element, with no loop.

## 1.2 It's fast

A loop over a list, against one line on an array, for a million numbers:
"""),
code("""
n = 1_000_000
big_list = list(range(n))
big_arr = np.arange(n)

def best(f, k=5):                          # the fastest of k runs, in seconds
    times = []
    for _ in range(k):
        t = time.perf_counter(); f(); times.append(time.perf_counter() - t)
    return min(times)

t_list = best(lambda: [v * 1.14 for v in big_list])
t_arr = best(lambda: big_arr * 1.14)

print(f"list loop: {t_list * 1000:6.1f} ms")
print(f"array:     {t_arr * 1000:6.1f} ms   ->  about {t_list / t_arr:.0f}x faster")
"""),
md("""
The exact numbers depend on the machine; the gap is always large.
An array keeps its numbers side by side in memory, all of the same type,
so the loop runs in compiled C code instead of in Python.
"""),
md("""
---
# 2️⃣ Making arrays, and `dtype`

## 2.1 From a column, from a list, from a pattern
"""),
code("""
a = np.array([5, 9, 10, 5])           # from a list
q = sales["quantity"].to_numpy()      # from a DataFrame column (the usual way in this course)

print(np.arange(1, 13))               # 1 .. 12: month numbers
print(np.linspace(0, 1, 5))           # 5 evenly spaced numbers from 0 to 1
print(np.zeros(4), np.ones(4))        # placeholders
print(np.full(4, 0.14))               # the same value 4 times
"""),
md("""
Random numbers, with a **seed** so you get the same ones every time you run the notebook
(NileCart itself was generated with seed 42):
"""),
code("""
rng = np.random.default_rng(42)
print(rng.integers(1, 11, size=8))          # 8 order quantities between 1 and 10
print(rng.normal(1000, 50, size=4).round(1))  # 4 prices around 1,000
"""),
md("""
## 2.2 One array, one type

Every array has a `dtype`, and all its elements share it.
"""),
code("""
for name, arr in [("order_id", sales["order_id"].to_numpy()), ("revenue", r),
                  ("revenue > 100k", r > 100_000), ("category", cat)]:
    print(f"{name:15} dtype={str(arr.dtype):8} first={arr[0]!r}")
"""),
md("""
| `dtype` | What it holds | NileCart |
|---|---|---|
| `int64` | whole numbers | `order_id`, `unit_cost` |
| `float64` | numbers with a decimal point (and `NaN`) | `revenue`, `discount` |
| `bool` | `True` / `False` | the answer to a condition |
| `object` | anything, as Python objects (slow) | text columns |

Mix types and NumPy picks one type that fits them all:
"""),
code("""
print(np.array([1, 2, 3]).dtype)
print(np.array([1, 2, 3.5]).dtype)      # one float turns everything into float
print(np.array([1, "2", 3]).dtype)      # one string turns everything into text
"""),
md("""
## 2.3 Why is `quantity` a float? `NaN` is a float

A quantity is a whole number, but in `sales.csv` it reads `5.0`, not `5`.
The reason is in the raw `orders.csv`: some quantities are missing.
"""),
code("""
orders = pd.read_csv(DATA / "orders.csv")
oq = orders["quantity"].to_numpy()
print("dtype:", oq.dtype, "  missing:", np.isnan(oq).sum(), "of", len(oq))
print(oq[np.isnan(oq)][:5])
"""),
md("""
A missing value is `np.nan` ("not a number"), and `np.nan` **is a float**.
An `int64` array has no way to hold it, so the whole column becomes `float64`.

`NaN` also spreads: any calculation that touches it gives `NaN`.
"""),
code("""
print("sum:       ", oq.sum())          # nan
print("nansum:    ", np.nansum(oq))      # skips the missing values
print("nanmean:   ", round(np.nanmean(oq), 2))
print("nan == nan:", np.nan == np.nan)   # so use np.isnan, never == np.nan
"""),
md("""
## 2.4 Converting: `astype`
"""),
code("""
print(q[:5], q.dtype)
print(q.astype(int)[:5], q.astype(int).dtype)    # sales.csv has no NaN left, so this works

with np.errstate(invalid="ignore"):        # NumPy only warns, so hide the warning to see what comes out
    oq_int = oq.astype(int)
print(oq_int[np.isnan(oq)][:3], "<- what a NaN became")
"""),
md("""
`astype(int)` on a `NaN` doesn't stop you: it silently writes a meaningless number.
Deal with the missing values first (the cleaning lesson), then convert.
"""),
md("""
---
# 3️⃣ Shape and `reshape`

## 3.1 24 months become a table

Revenue per month, from January 2024 to December 2025: a vector of 24 numbers.
"""),
code("""
monthly = done.groupby(done["order_date"].dt.to_period("M"))["revenue"].sum()
m = monthly.to_numpy()
print(m.shape)
print((m / 1000).round())
"""),
md("""
24 numbers in a row are hard to compare. `reshape(2, 12)` lays the same 24 numbers out as
**2 rows (years) × 12 columns (months)**, filling row by row:
"""),
code("""
M = m.reshape(2, 12)
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
pd.DataFrame((M / 1000).round().astype(int), index=[2024, 2025], columns=MONTHS)     # thousands of EGP
"""),
md("""
Same data, new shape. Now each column is the same month in both years.

The sizes must agree: 2 × 12 = 24. `-1` means "work it out":
"""),
code("""
print(m.reshape(2, -1).shape)    # (2, 12)
print(m.reshape(-1, 3).shape)    # (8, 3): 8 quarters x 3 months
print(M.ravel().shape)           # back to one row of 24

try:
    m.reshape(5, 5)
except ValueError as e:
    print("reshape(5, 5) ->", e)
"""),
md("""
---
# 4️⃣ Indexing and slicing

## 4.1 One dimension

Positions start at 0, and negative positions count from the end.
"""),
code("""
print("first:", r[0], "  last:", r[-1])
print("first 5:", r[:5])
print("every 200th:", r[::200])
"""),
md("""
## 4.2 Two dimensions: `M[row, column]`
"""),
code("""
print("Nov 2025:       ", M[1, 10])        # row 1 = 2025, column 10 = November
print("2024, all year: ", M[0].round())    # a whole row
print("December, both: ", M[:, 11])        # a whole column
print("Q4 2024:        ", M[0, 9:])        # Oct, Nov, Dec of 2024
"""),
md("""
## 4.3 A slice is a view ⚠️

A slice doesn't copy the numbers: it's a **view** of the same memory.
Change the view and the original changes too.
"""),
code("""
a = np.array([10, 20, 30, 40, 50])
first3 = a[:3]
first3[0] = 999
print("a after changing the slice:", a)

a = np.array([10, 20, 30, 40, 50])
first3 = a[:3].copy()            # an independent copy
first3[0] = 999
print("a after changing a copy:   ", a)
"""),
md("""
Views keep NumPy fast on big data. When you want to change a piece without touching the original, call `.copy()`.
(Pandas 2 had the same issue, behind its `SettingWithCopyWarning`. Pandas 3 avoids it: every selection behaves like a copy.)
"""),
md("""
---
# 5️⃣ Boolean masks: filtering with a condition

A comparison on an array gives an array of `True` / `False`, one per element: a **mask**.
"""),
code("""
mask = r > 100_000
print(r[:8])
print(mask[:8])
"""),
md("""
Put the mask inside the brackets and you keep only the `True` elements.
And because `True` counts as 1, `mask.sum()` counts them:
"""),
code("""
big = r[mask]
print("big orders:      ", mask.sum(), "of", len(r))
print("their revenue:   ", f"{big.sum():,.0f}")
print("share of revenue:", f"{big.sum() / r.sum():.1%}")
print("share of orders: ", f"{mask.mean():.1%}")
"""),
md("""
4% of the order lines bring in more than a third of the revenue. That's the long right tail from the Introduction.

## 5.1 Combining conditions: `&`, `|`, `~`

`and` / `or` / `not` don't work on arrays. Use `&` (and), `|` (or), `~` (not), with **brackets** around each condition:
"""),
code("""
elec = cat == "Electronics"
print("big AND Electronics:", ((r > 100_000) & elec).sum())
print("big AND not Electr.:", ((r > 100_000) & ~elec).sum())
print("Stationery OR Furniture:", ((cat == "Stationery") | (cat == "Furniture")).sum())
"""),
code("""
try:
    r > 100_000 and elec
except ValueError as e:
    print("`and` ->", e)
"""),
md("""
Every big order is Electronics: no other category has a product expensive enough.

## 5.2 `np.isin`: one of several values
"""),
code("""
phones_laptops = np.isin(prod, ["Laptop", "Phone"])
print(phones_laptops.sum(), "lines,", f"{r[phones_laptops].sum() / r.sum():.0%} of revenue")
"""),
md("""
## 5.3 `np.where`: if / else on a whole column
"""),
code("""
size = np.where(r >= 10_000, "big", "small")
print(size[:8])
print(pd.Series(size).value_counts())
"""),
md("""
## 5.4 Changing values with a mask
"""),
code("""
capped = r.copy()
capped[capped > 100_000] = 100_000          # cap the extreme orders (for a chart, say)
print("max before:", r.max(), "  after:", capped.max())
"""),
md("""
---
# 6️⃣ Aggregation and `axis`

## 6.1 One number from a whole column
"""),
code("""
print(f"sum     {r.sum():>14,.0f}")
print(f"mean    {r.mean():>14,.0f}")
print(f"median  {np.median(r):>14,.0f}")
print(f"std     {r.std():>14,.0f}")
print(f"min     {r.min():>14,.0f}")
print(f"max     {r.max():>14,.0f}")
print(f"90th %  {np.percentile(r, 90):>14,.0f}")
"""),
md("""
The mean is five times the median: a few huge orders pull it up.
Which one to report is what we settled in *Descriptive statistics*.

## 6.2 `axis`: which direction to collapse

On a 2-D array, `axis` says which dimension disappears:

* `axis=0` collapses the **rows**: one result per column (per month).
* `axis=1` collapses the **columns**: one result per row (per year).
* no `axis`: everything, one number.
"""),
code("""
print("M.sum()       ", f"{M.sum():,.0f}", "  shape ()")
print("M.sum(axis=1) ", M.sum(axis=1).round(), "  shape", M.sum(axis=1).shape, "<- one per year")
print("M.sum(axis=0) ", (M.sum(axis=0) / 1000).round(), "  shape", M.sum(axis=0).shape, "<- one per month (k)")
"""),
md("""
The two years are almost equal: 9.74M in 2024 and 9.67M in 2025.

`argmax` gives the **position** of the largest value, not the value:
"""),
code("""
peak = M.argmax(axis=1)
for year, p in zip([2024, 2025], peak):
    print(year, "peak month:", MONTHS[p], f"({M[year - 2024, p]:,.0f} EGP)")
print("best month over both years:", MONTHS[M.sum(axis=0).argmax()])
"""),
code("""
fig, ax = plt.subplots()
ax.plot(MONTHS, M[0] / 1e6, marker="o", label="2024")
ax.plot(MONTHS, M[1] / 1e6, marker="o", label="2025")
ax.plot(MONTHS, M.mean(axis=0) / 1e6, ls="--", color="gray", label="mean, axis=0")
ax.set(title="Revenue per month (million EGP)", ylabel="")
ax.legend()
plt.show()
"""),
md("""
---
# 7️⃣ Broadcasting

Two arrays of different shapes can still work together, when NumPy can **stretch** one to match the other.
You've already seen the simplest case: an array times a scalar, `r * 1.14`.

## 7.1 Each month's share of its year

Divide the (2 × 12) table by each year's total. The totals have shape (2,); with `keepdims=True` they stay (2 × 1),
a column, and NumPy stretches that column across the 12 months:
"""),
code("""
totals = M.sum(axis=1, keepdims=True)
print("M:", M.shape, "  totals:", totals.shape)

share = M / totals                      # (2, 12) / (2, 1) -> (2, 12)
pd.DataFrame(share * 100, index=[2024, 2025], columns=MONTHS).round(1)     # % of the year
"""),
code("""
print(share.sum(axis=1))     # every row adds up to 1
"""),
md("""
November and December together are about 35% of the year, in both years.

## 7.2 A row against every row

Every row divided by 2024's row: a (12,) row stretched down both years.
The 2024 row becomes all ones, and the 2025 row says how each month did against the same month a year earlier:
"""),
code("""
base = M[0]                             # shape (12,)
print("M:", M.shape, "  base:", base.shape)
pd.DataFrame(M / base, index=[2024, 2025], columns=MONTHS).round(2)     # 1.00 = same as 2024
"""),
md("""
January to March 2025 were about 50% above 2024. July and September fell by 40–45%, and December by a fifth.
"""),
md("""
## 7.3 The rule

Line the shapes up **from the right**. Each pair of sizes must be equal, or one of them must be 1 (that one stretches).

| A | B | Result |
|---|---|---|
| (2, 12) | () scalar | (2, 12) |
| (2, 12) | (12,) | (2, 12) |
| (2, 12) | (2, 1) | (2, 12) |
| (2, 12) | (2,) | ❌ 12 vs 2 |
"""),
code("""
try:
    M / M.sum(axis=1)              # (2, 12) / (2,): lined up from the right, 12 vs 2
except ValueError as e:
    print(e)
"""),
md("""
That's the most common broadcasting error, and `keepdims=True` (or `[:, None]`) is the fix.
"""),
md("""
---
# 8️⃣ Sorting

## 8.1 `np.sort`
"""),
code("""
print("smallest 5:", np.sort(r)[:5])
print("largest 5: ", np.sort(r)[-5:])
print("largest 5, biggest first:", np.sort(r)[::-1][:5])
"""),
md("""
## 8.2 `argsort`: sort one array, reorder another

`argsort` returns the **positions** that would sort the array.
Use them on any other array of the same length, and the two stay lined up:
"""),
code("""
top = np.argsort(r)[::-1][:5]          # positions of the 5 largest revenues
print(top)
for i in top:
    print(f"{prod[i]:8} {r[i]:>10,.0f}")
"""),
md("""
The months of 2025, best to worst:
"""),
code("""
order = np.argsort(M[1])[::-1]
print([MONTHS[i] for i in order])
"""),
md("""
---
# 🧰 Summary

| Idea | In one line | NumPy |
|---|---|---|
| Array, not list | arithmetic on every element | `np.array`, `df["col"].to_numpy()` |
| `dtype` | one type per array; `NaN` is a float | `arr.dtype`, `astype`, `np.isnan` |
| Missing values | `NaN` spreads | `np.nansum`, `np.nanmean` |
| Shape | same data, new layout | `reshape(2, 12)`, `reshape(-1)`, `ravel` |
| Indexing | row, column; a slice is a view | `M[1, 10]`, `M[:, 11]`, `.copy()` |
| Boolean mask | filter with a condition | `r[r > 100_000]`, `&`, `\\|`, `~`, `np.isin` |
| If / else | on a whole column | `np.where(cond, a, b)` |
| Aggregation | `axis` is the dimension that disappears | `M.sum(axis=0)`, `argmax` |
| Broadcasting | sizes equal, or one of them is 1 | `M / M.sum(axis=1, keepdims=True)` |
| Sorting | values, or the positions that sort | `np.sort`, `np.argsort` |

**Next part of the course:** Pandas: reading, inspecting, selecting and filtering tables.

📚 All the lessons of the course: [zero-grad.com/courses/da](https://zero-grad.com/courses/da/)
"""),
]

if __name__ == "__main__":
    path = write(cells, OUT, "NumPy")
    print("wrote", path)
    if "--no-run" not in sys.argv:
        execute(path)
        print("executed", path)
