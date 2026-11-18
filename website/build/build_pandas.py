"""Build 3-pandas/01_pandas_basics.ipynb (the solved companion notebook of the Pandas basics lesson).

    python build/build_pandas.py          # write + execute
    python build/build_pandas.py --no-run # write only
"""
from pathlib import Path
import sys

from nb import code, execute, md, write

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "3-pandas" / "01_pandas_basics.ipynb"

cells = [
md("""
# 🐼 Pandas Basics: read, look, select, filter

**Zero Grad · Data Analysis course · Pandas**

> 📖 **The lesson (in Arabic), with diagrams and interactive widgets:** [zero-grad.com/courses/da/pandas](https://zero-grad.com/courses/da/pandas/)
>
> 🗂️ **The data:** [NileCart Sales on Kaggle](https://www.kaggle.com/datasets/a7madmostafa/nilecart-sales)

This is the solved notebook of the *Pandas basics* lesson.
NumPy gave us arrays of one type. Pandas puts many of them side by side, gives every column a name
and every row a label: a **table**. Most of a data analyst's day is spent in it.

| # | Part | The question |
|---|---|---|
| 1 | Series and DataFrame | What is a table in Pandas? |
| 2 | Reading and writing | How does a CSV become a table? |
| 3 | A first look | What's in this table? |
| 4 | Columns | Pick, add, rename, convert, drop |
| 5 | `loc` and `iloc` | Rows by label, or by position? |
| 6 | Filtering | Which rows match a condition? |
| 7 | Sorting | What's on top? |
"""),
md("""
---
# 0️⃣ Setup
"""),
code("""
from pathlib import Path

import numpy as np
import pandas as pd

pd.options.display.float_format = "{:,.2f}".format
pd.options.display.max_columns = 20

# On Kaggle the data lives under /kaggle/input, locally in the repo's data/nilecart/ folder
on_kaggle = sorted(Path("/kaggle/input").glob("**/sales.csv"))
DATA = on_kaggle[0].parent if on_kaggle else Path("../data/nilecart")
print(pd.__version__)
"""),
md("""
---
# 1️⃣ Series and DataFrame

A **Series** is one column: a NumPy array of values, plus an **index** (a label for every value).
"""),
code("""
price = pd.Series([1200, 450, 900], index=["Keyboard", "Mouse", "Backpack"], name="list_price")
price
"""),
code("""
print(price["Mouse"])          # by label
print(price.to_numpy())        # the NumPy array underneath
print(price * 1.14)            # vectorised, like NumPy, and the labels come along
"""),
md("""
A **DataFrame** is a table: several Series that share the same index, one per column.
"""),
code("""
df = pd.DataFrame({
    "product": ["Keyboard", "Mouse", "Backpack"],
    "list_price": [1200, 450, 900],
    "category": ["Accessories"] * 3,
})
df
"""),
code("""
print("index:  ", df.index)
print("columns:", df.columns.tolist())
print("one column is a Series:", type(df["list_price"]).__name__)
"""),
md("""
| Part | What it is | `df.` |
|---|---|---|
| index | the row labels (by default 0, 1, 2, …) | `index` |
| columns | the column names | `columns` |
| values | the data, one NumPy array per column | `to_numpy()` |
| a column | a Series | `df["col"]` |
"""),
md("""
---
# 2️⃣ Reading and writing

## 2.1 `read_csv`
"""),
code("""
sales = pd.read_csv(DATA / "sales.csv")
print(sales.shape)
print(sales["order_date"].dtype)      # text! a CSV has no types, Pandas guesses
"""),
md("""
A CSV file is only text. Pandas guesses each column's type: numbers become numbers,
everything else stays text (`object`), dates included. Tell it which columns are dates:
"""),
code("""
sales = pd.read_csv(DATA / "sales.csv", parse_dates=["order_date"])
print(sales["order_date"].dtype)
print(sales["order_date"].min(), "->", sales["order_date"].max())
"""),
md("""
A few `read_csv` arguments you'll use often:
"""),
code("""
small = pd.read_csv(DATA / "sales.csv", usecols=["order_id", "product_name", "revenue"], nrows=5)
small
"""),
md("""
| Argument | Does |
|---|---|
| `parse_dates=["col"]` | read these columns as dates |
| `usecols=[...]` | read only these columns |
| `nrows=5` | read only the first rows (peek at a huge file) |
| `index_col="col"` | use a column as the index |
| `sep=";"` | another separator (many European files use `;`) |
| `encoding="utf-8"` | the text encoding (Arabic text needs the right one) |

## 2.2 `to_csv`
"""),
code("""
big = sales[sales["revenue"] > 100_000]
big.to_csv("big_orders.csv", index=False)       # index=False: don't write 0, 1, 2 ... as a column
print(pd.read_csv("big_orders.csv").shape)
Path("big_orders.csv").unlink()                   # tidy up
"""),
md("""
Forget `index=False` and the next read gets an extra column called `Unnamed: 0`.
"""),
md("""
---
# 3️⃣ A first look

Before any analysis, the same handful of questions, every time.

## 3.1 How big, and what does a row look like?
"""),
code("""
print(sales.shape)        # (rows, columns)
sales.head()              # the first 5 rows; tail() for the last, sample(5) for random ones
"""),
md("""
## 3.2 What type is each column, and is anything missing? `info()`
"""),
code("""
sales.info()
"""),
md("""
`info()` answers three questions in one go: how many rows (1,466), each column's type, and how many values are **non-null**.
1,466 everywhere: `sales.csv` has no missing values. Its raw source does:
"""),
code("""
orders = pd.read_csv(DATA / "orders.csv")
orders.isna().sum()
"""),
md("""
`isna().sum()` counts the missing values per column. The cleaning lesson deals with them.

## 3.3 Numbers: `describe()`
"""),
code("""
sales.describe().T
"""),
md("""
(The *Descriptive statistics* lesson is about reading this table.)

## 3.4 Categories: `nunique()` and `value_counts()`
"""),
code("""
sales.nunique()
"""),
code("""
sales["status"].value_counts()
"""),
code("""
sales["status"].value_counts(normalize=True).round(3)       # shares instead of counts
"""),
md("""
Things worth noticing already:
* Only 73% of order lines are `completed`: revenue analysis should use those.
* `status` has an `unknown` value, and `region` and `segment` have `Unknown` (2 rows each): dirty data to remember.
* 1,466 order lines but only 160 customers: about 9 lines each.
"""),
md("""
---
# 4️⃣ Columns

## 4.1 Selecting
"""),
code("""
print(type(sales["revenue"]).__name__)                 # one name -> a Series
sales[["name", "product_name", "revenue"]].head(3)     # a list of names -> a DataFrame
"""),
md("""
Note the double brackets: the outer ones select, the inner ones make a list.

## 4.2 New columns

Arithmetic on columns works element by element, like NumPy:
"""),
code("""
sales["margin"] = sales["profit"] / sales["revenue"]
sales["year"] = sales["order_date"].dt.year
sales["month"] = sales["order_date"].dt.month
sales[["order_date", "year", "month", "revenue", "profit", "margin"]].head(3)
"""),
md("""
`.dt` gives date parts (`year`, `month`, `day_name()`, …), `.str` gives text tools. Both work on the whole column:
"""),
code("""
sales["first_name"] = sales["name"].str.split().str[0]
sales[["name", "first_name"]].head(3)
"""),
md("""
## 4.3 Renaming, converting, dropping
"""),
code("""
tidy = (sales
        .rename(columns={"product_name": "product"})
        .astype({"quantity": "int64"})              # sales.csv has no NaN, so this is safe
        .drop(columns=["first_name"]))
print(tidy.columns.tolist())
print(tidy["quantity"].dtype)
"""),
md("""
None of these change `sales` itself: they return a **new** DataFrame. Assign the result (`tidy = ...`) to keep it.
"""),
md("""
---
# 5️⃣ `loc` and `iloc`: rows by label, or by position

* `iloc[...]` uses **positions**: 0, 1, 2, … like a list.
* `loc[...]` uses **labels**: whatever is in the index.

With the default index (0, 1, 2, …) they look the same. Make `order_id` the index and the difference shows:
"""),
code("""
s = sales.set_index("order_id")
s[["name", "product_name", "revenue", "status"]].head(4)
"""),
md("""
The file isn't sorted by `order_id`: the first row is order **10002**, the second is **10001**.
"""),
code("""
print("iloc[0]     ->", s.iloc[0]["name"], "  (position 0: order", s.index[0], ")")
print("loc[10001]  ->", s.loc[10001, "name"], "  (label 10001)")
"""),
md("""
## 5.1 Rows and columns together: `[rows, columns]`
"""),
code("""
s.loc[10001, ["product_name", "quantity", "revenue"]]
"""),
code("""
s.iloc[:3, :4]          # the first 3 rows, the first 4 columns
"""),
md("""
## 5.2 ⚠️ Slices: `loc` includes the end, `iloc` doesn't
"""),
code("""
print(len(s.iloc[0:3]), "rows with iloc[0:3]   (positions 0, 1, 2)")
print(len(s.loc[10002:10003]), "rows with loc[10002:10003]  (from label 10002 to label 10003, both included)")
s.loc[10002:10003, ["name", "product_name"]]
"""),
md("""
`iloc` slices like Python: the end is left out. `loc` slices by label, and includes both ends.
A `loc` slice also follows the order the rows are **in**, not the order of the numbers:
10002, 10001, 10004, 10003 are the rows between those two labels.

## 5.3 Changing values: always through `loc`
"""),
code("""
fix = sales.copy()
fix.loc[fix["region"] == "Unknown", "region"] = "Not given"
fix["region"].value_counts().tail(2)
"""),
md("""
`df.loc[rows, column] = value` is the one safe way to change part of a table.
The chained form `df[cond]["col"] = value` changes a temporary copy, not `df`.
In Pandas 2 it *sometimes* worked and raised a `SettingWithCopyWarning`;
from Pandas 3 on it never changes `df`, and Pandas warns with a `ChainedAssignmentError`.
"""),
md("""
---
# 6️⃣ Filtering

The NumPy boolean mask, with column names:
"""),
code("""
mask = sales["status"] == "completed"
print(mask.head(4).tolist())
done = sales[mask]
print(len(done), "of", len(sales), "rows")
"""),
md("""
## 6.1 Several conditions: `&`, `|`, `~`, in brackets
"""),
code("""
print("completed Electronics: ", len(sales[(sales["status"] == "completed") & (sales["category"] == "Electronics")]))
print("returned or cancelled: ", len(sales[(sales["status"] == "returned") | (sales["status"] == "cancelled")]))
print("not completed:         ", len(sales[~mask]))
"""),
md("""
## 6.2 Shortcuts: `isin`, `between`, `.str.contains`
"""),
code("""
print("isin:     ", len(sales[sales["status"].isin(["returned", "cancelled"])]))
print("between:  ", len(done[done["revenue"].between(1_000, 5_000)]), "completed lines between 1,000 and 5,000 EGP (both ends included)")
print("contains: ", len(sales[sales["name"].str.contains("Mostafa")]), "lines for customers with Mostafa in the name")
"""),
md("""
## 6.3 `query`: the condition as a string
"""),
code("""
sales.query("status == 'completed' and revenue > 100_000")[["order_id", "name", "product_name", "revenue"]].head()
"""),
code("""
cutoff = 100_000
len(sales.query("status == 'completed' and revenue > @cutoff"))      # @ uses a Python variable
"""),
md("""
`query` reads well for long conditions; brackets work everywhere. Use whichever is clearer.

## 6.4 Filter, then pick columns, in one `loc`
"""),
code("""
sales.loc[(sales["status"] == "completed") & (sales["region"] == "Canal"), ["order_date", "name", "product_name", "revenue"]].head()
"""),
md("""
---
# 7️⃣ Sorting
"""),
code("""
done.sort_values("revenue", ascending=False)[["order_id", "name", "product_name", "revenue"]].head()
"""),
md("""
The three biggest order lines are all laptops, the same answer `argsort` gave in the NumPy lesson.
`sort_values` is that `argsort`, applied to every column at once so the rows stay whole.

Sort by several columns: the second breaks ties in the first.
"""),
code("""
(done.sort_values(["category", "revenue"], ascending=[True, False])
     .groupby("category").head(1)[["category", "product_name", "revenue"]])
"""),
code("""
done.nlargest(3, "profit")[["name", "product_name", "profit"]]          # shortcut for sort + head
"""),
code("""
s.sort_index().head(3)[["name", "product_name"]]                        # sort by the index labels
"""),
md("""
---
# 🧰 Summary

| Task | Code |
|---|---|
| Read a CSV, with dates | `pd.read_csv(path, parse_dates=["order_date"])` |
| Write a CSV | `df.to_csv(path, index=False)` |
| Size, first rows | `df.shape`, `df.head()`, `df.sample(5)` |
| Types and missing | `df.info()`, `df.isna().sum()` |
| Numbers, categories | `df.describe()`, `df.nunique()`, `df["col"].value_counts()` |
| One column / several | `df["col"]` (Series) / `df[["a", "b"]]` (DataFrame) |
| New column | `df["margin"] = df["profit"] / df["revenue"]`, `.dt.year`, `.str.split()` |
| Rename, convert, drop | `rename(columns=...)`, `astype(...)`, `drop(columns=...)` |
| By position / by label | `df.iloc[0:3, :4]` (end excluded) / `df.loc[10001, "name"]` (end included) |
| Change values | `df.loc[cond, "col"] = value` |
| Filter | `df[(cond1) & (cond2)]`, `isin`, `between`, `.str.contains`, `query` |
| Sort | `sort_values(cols, ascending=...)`, `nlargest`, `sort_index` |

**Next lesson:** grouping and joining: `groupby`, `pivot_table` and `merge`.

📚 All the lessons of the course: [zero-grad.com/courses/da](https://zero-grad.com/courses/da/)
"""),
]

if __name__ == "__main__":
    path = write(cells, OUT, "Pandas Basics")
    print("wrote", path)
    if "--no-run" not in sys.argv:
        execute(path)
        print("executed", path)
