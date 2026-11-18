"""Build 3-pandas/02_grouping_joining.ipynb (the solved companion notebook of the Grouping & joining lesson).

    python build/build_grouping.py          # write + execute
    python build/build_grouping.py --no-run # write only
"""
from pathlib import Path
import sys

from nb import code, execute, md, write

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "3-pandas" / "02_grouping_joining.ipynb"

cells = [
md("""
# 🧩 Grouping & Joining: groupby, pivot_table, merge

**Zero Grad · Data Analysis course · Pandas**

> 📖 **The lesson (in Arabic), with diagrams and interactive widgets:** [zero-grad.com/courses/da/grouping](https://zero-grad.com/courses/da/grouping/)
>
> 🗂️ **The data:** [NileCart Sales on Kaggle](https://www.kaggle.com/datasets/a7madmostafa/nilecart-sales)

This is the solved notebook of the *Grouping & joining* lesson.
Most business questions are "per something": revenue **per** category, orders **per** customer, sales **per** month.
And the answer is rarely in one table: the order has the `customer_id`, the customer's name is in another file.

| # | Part | The question |
|---|---|---|
| 1 | `groupby` | One number per group |
| 2 | `agg` | Several numbers per group, with names |
| 3 | `transform` | The group's number, back on every row |
| 4 | `pivot_table` and `crosstab` | A two-way table |
| 5 | `concat` | Stack tables |
| 6 | `merge` | Join tables on a key |
| 7 | Join types | inner, left, right, outer |
| 8 | Merge traps | Keys that don't match, keys that repeat |
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

sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.figsize"] = (9, 4)
pd.options.display.float_format = "{:,.2f}".format

# On Kaggle the data lives under /kaggle/input, locally in the repo's data/nilecart/ folder
on_kaggle = sorted(Path("/kaggle/input").glob("**/sales.csv"))
DATA = on_kaggle[0].parent if on_kaggle else Path("../data/nilecart")

sales = pd.read_csv(DATA / "sales.csv", parse_dates=["order_date"])
done = sales[sales["status"] == "completed"]
print(len(done), "completed order lines")
"""),
md("""
---
# 1️⃣ `groupby`: one number per group

`groupby` does three things: **split** the rows into groups, **apply** a calculation to each group, **combine** the answers into one table.
"""),
code("""
done.groupby("category")["revenue"].sum()
"""),
md("""
Read it as: *group the rows by `category`, take the `revenue` column, and `sum` it in each group.*
The result is a Series whose index is the groups.

The same, done by hand, to see the three steps:
"""),
code("""
answers = {}
for cat, rows in done.groupby("category"):          # split: one small DataFrame per category
    answers[cat] = rows["revenue"].sum()             # apply
pd.Series(answers)                                   # combine
"""),
md("""
## 1.1 Any calculation, any column
"""),
code("""
print(done.groupby("region")["revenue"].sum().sort_values(ascending=False))
"""),
code("""
done.groupby("product_name")["quantity"].sum().sort_values(ascending=False).head(5)
"""),
code("""
done.groupby("segment").size()          # size(): how many rows per group
"""),
md("""
## 1.2 Several group columns
"""),
code("""
by_year_cat = done.groupby([done["order_date"].dt.year, "category"])["revenue"].sum()
by_year_cat
"""),
md("""
Two group columns give a two-level index (a `MultiIndex`). `unstack()` turns the inner level into columns:
"""),
code("""
by_year_cat.unstack()
"""),
md("""
## 1.3 `as_index=False`: the groups as a column
"""),
code("""
done.groupby("category", as_index=False)["revenue"].sum()
"""),
md("""
---
# 2️⃣ `agg`: several numbers per group

The previous lesson's rule: never a group statistic without its `count`.
"""),
code("""
done.groupby("category")["revenue"].agg(["count", "sum", "mean", "median"]).sort_values("sum", ascending=False)
"""),
md("""
## 2.1 Named aggregation: one column per result, any input column
"""),
code("""
per_customer = (done.groupby(["customer_id", "name"])
                    .agg(orders=("order_id", "nunique"),
                         units=("quantity", "sum"),
                         revenue=("revenue", "sum"),
                         first=("order_date", "min"),
                         last=("order_date", "max"))
                    .sort_values("revenue", ascending=False))
print(len(per_customer), "customers with a completed order")
per_customer.head()
"""),
md("""
`new_name=("column", "function")`: the result gets a clear name, and each one can use a different column.
The best customer bought for more than a million EGP in 24 order lines.
"""),
code("""
top10 = per_customer["revenue"].head(10).sum() / per_customer["revenue"].sum()
print(f"the top 10 customers bring {top10:.0%} of the revenue")
"""),
md("""
---
# 3️⃣ `transform`: the group's number, back on every row

`agg` gives **one row per group**. `transform` gives **one value per original row**: the group's answer, repeated on each of its rows.
That lets you compare a row with its group.
"""),
code("""
d = done.copy()
d["category_total"] = d.groupby("category")["revenue"].transform("sum")
d["share_of_category"] = d["revenue"] / d["category_total"]
d[["order_id", "category", "revenue", "category_total", "share_of_category"]].head()
"""),
code("""
print(len(d), "rows, the same as done")
d.loc[d["share_of_category"].idxmax(), ["name", "product_name", "revenue", "share_of_category"]]
"""),
md("""
Another common one: each line against the median of its category.
"""),
code("""
d["vs_median"] = d["revenue"] / d.groupby("category")["revenue"].transform("median")
d.groupby("category")["vs_median"].max().round(1)
"""),
md("""
The biggest Electronics and Furniture lines are about 8 times their category's typical line; the biggest Accessories line about 5 times.
(The outlier rule *within each category* from the statistics lesson used exactly this idea.)
"""),
md("""
---
# 4️⃣ Two-way tables: `pivot_table` and `crosstab`

## 4.1 `pivot_table`: rows × columns, one number in each cell
"""),
code("""
pv = done.pivot_table(index="region", columns="category", values="revenue",
                      aggfunc="sum", fill_value=0, margins=True, margins_name="Total")
(pv / 1000).round()          # thousands of EGP
"""),
md("""
* `index`: the rows, `columns`: the columns, `values` + `aggfunc`: what goes in each cell.
* `fill_value=0`: a combination with no orders shows 0 instead of NaN.
* `margins=True`: row and column totals.

It's the same as a `groupby` on two columns followed by `unstack`:
"""),
code("""
same = done.groupby(["region", "category"])["revenue"].sum().unstack(fill_value=0)
np.allclose(same, pv.drop(index="Total", columns="Total"))
"""),
code("""
share = done.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum", fill_value=0)
share = share.div(share.sum(axis=1), axis=0)        # each row as % of its region
ax = (share.drop(index="Unknown") * 100).plot(kind="barh", stacked=True, figsize=(9, 3.6))
ax.set(title="Revenue mix by region (%)", xlabel="%", ylabel="")
ax.legend(bbox_to_anchor=(1, 1))
plt.show()
"""),
md("""
Electronics is the bulk everywhere, from 72% of the revenue in the Delta (which buys more furniture) to 87% in Alexandria & Coast.
Greater Cairo is the biggest region, but its mix is close to the average.

## 4.2 `crosstab`: counts of two categories
"""),
code("""
pd.crosstab(done["segment"], done["category"])
"""),
code("""
pd.crosstab(done["segment"], done["category"], normalize="index").round(2)      # each row adds up to 1
"""),
md("""
Consumers, corporates and small businesses buy the same mix of categories (by number of lines).
Corporates differ in *how many* units they buy per line, not *what* they buy.
"""),
md("""
---
# 5️⃣ `concat`: stack tables

Tables with the same columns, one under the other: monthly exports, yearly files.
"""),
code("""
y2024 = done[done["order_date"].dt.year == 2024]
y2025 = done[done["order_date"].dt.year == 2025]
both = pd.concat([y2024, y2025], ignore_index=True)       # ignore_index: number the rows 0..n-1 again
print(len(y2024), "+", len(y2025), "=", len(both))
"""),
md("""
`concat` matches columns **by name**. A column that one table doesn't have is filled with NaN:
"""),
code("""
a = pd.DataFrame({"product": ["Mouse"], "units": [3]})
b = pd.DataFrame({"product": ["Lamp"], "units": [1], "colour": ["black"]})
pd.concat([a, b], ignore_index=True)
"""),
md("""
---
# 6️⃣ `merge`: join tables on a key

`sales.csv` doesn't exist in a real shop. What exists is the raw tables:
"""),
code("""
orders = pd.read_csv(DATA / "orders.csv", parse_dates=["order_date"])
customers = pd.read_csv(DATA / "customers.csv")
products = pd.read_csv(DATA / "products.csv")
governorates = pd.read_csv(DATA / "governorates.csv")
for name, t in [("orders", orders), ("customers", customers), ("products", products), ("governorates", governorates)]:
    print(f"{name:13} {t.shape}  {t.columns.tolist()}")
"""),
md("""
An order knows its `customer_id` and `product_id`, nothing else. The name is in `customers`, the category in `products`.
The shared column is the **key**.
"""),
code("""
op = orders.merge(products[["product_id", "product_name", "category", "unit_cost"]], on="product_id", how="left")
print(orders.shape, "->", op.shape)
op[["order_id", "product_id", "product_name", "category", "unit_price", "unit_cost"]].head()
"""),
md("""
Each order found its product: same number of rows, 3 new columns. That's what a good lookup join looks like.
"""),
md("""
---
# 7️⃣ Join types: which rows survive?

When a key is on one side only, the `how=` argument decides what happens.
"""),
code("""
orphans = orders[~orders["customer_id"].isin(customers["customer_id"])]
print("orders whose customer isn't in customers.csv:")
print(orphans[["order_id", "customer_id"]].to_string(index=False))
silent = customers[~customers["customer_id"].isin(orders["customer_id"])]
print("customers with no order:", len(silent))
"""),
code("""
for how in ["inner", "left", "right", "outer"]:
    m = orders.merge(customers, on="customer_id", how=how)
    print(f"{how:6} {len(m):5} rows")
"""),
md("""
| `how=` | Keeps | Here |
|---|---|---|
| `inner` | only keys on **both** sides | 1,498: the 3 orphan orders are gone |
| `left` | every row of the **left** table | 1,501: the orphans stay, with NaN for the customer |
| `right` | every row of the **right** table | 1,540: plus the 42 customers who never ordered |
| `outer` | everything | 1,543: orphans and silent customers |

`indicator=True` adds a `_merge` column that says where each row came from:
"""),
code("""
m = orders.merge(customers, on="customer_id", how="outer", indicator=True)
m["_merge"].value_counts()
"""),
md("""
`left` is the usual choice for adding information to a table: you keep all your orders, and see which ones didn't find a match.
An `inner` join would have dropped 3 orders without a word.

## 7.1 What was never sold?

A left join from the other side, then keep the rows with no match:
"""),
code("""
pm = products.merge(orders[["product_id", "order_id"]], on="product_id", how="left", indicator=True)
pm.loc[pm["_merge"] == "left_only", ["product_id", "product_name", "list_price"]]
"""),
md("""
---
# 8️⃣ Merge traps

## 8.1 Keys that don't match exactly

The governorate names in `customers.csv` came from a sign-up form:
"""),
code("""
cg = customers.merge(governorates, on="governorate", how="left")
print("customers with no region:", cg["region"].isna().sum())
cg.loc[cg["region"].isna(), ["customer_id", "governorate"]].assign(shown=lambda x: "'" + x["governorate"] + "'")
"""),
md("""
`"cairo"`, `"GIZA "` and `" alexandria"` are not `"Cairo"`, `"Giza"`, `"Alexandria"`: a key must match **character for character**.
Clean the keys first:
"""),
code("""
customers["governorate"] = customers["governorate"].str.strip().str.title()
customers["name"] = customers["name"].str.strip().str.title()
print("after cleaning:", customers.merge(governorates, on="governorate", how="left")["region"].isna().sum(), "without a region")
"""),
md("""
## 8.2 ⚠️ Keys that repeat: the row explosion

Join on a key that isn't unique on the "lookup" side and every match becomes a row.
Here's a mistake that looks reasonable: adding the segment by the customer's **name** instead of the id.
"""),
code("""
oc = orders.merge(customers[["customer_id", "name"]], on="customer_id")
print("unique names:", customers["name"].nunique(), "for", len(customers), "customers")

wrong = oc.merge(customers[["name", "segment"]], on="name")
print(len(oc), "rows ->", len(wrong), "rows")
"""),
md("""
No error, no warning. 1,498 orders became 2,824 rows, and every sum on the result is now wrong:
"""),
code("""
oc["gross"] = oc["quantity"] * oc["unit_price"]
wrong["gross"] = wrong["quantity"] * wrong["unit_price"]
print(f"real gross:   {oc['gross'].sum():>14,.0f}")
print(f"after merge:  {wrong['gross'].sum():>14,.0f}")
"""),
md("""
**The fix: `validate=`.** Tell Pandas what the join *should* be, and it checks:
"""),
code("""
try:
    oc.merge(customers[["name", "segment"]], on="name", validate="many_to_one")
except pd.errors.MergeError as e:
    print("MergeError:", e)
"""),
code("""
right = orders.merge(customers[["customer_id", "name", "segment"]], on="customer_id",
                     how="left", validate="many_to_one")
print(len(orders), "->", len(right), "rows: one customer per order, as it should be")
"""),
md("""
| `validate=` | Means |
|---|---|
| `"one_to_one"` | the key is unique on both sides |
| `"many_to_one"` | many rows on the left, one match on the right (the usual lookup) |
| `"one_to_many"` | the other way |

Three checks after every merge: **the row count**, **`indicator=True`** for unmatched keys, and **`validate=`**.

## 8.3 Building `sales` from the raw tables

The whole recipe (the cleaning steps come in the next lesson):
"""),
code("""
s = (orders
     .merge(customers[["customer_id", "name", "governorate", "segment"]], on="customer_id", how="left", validate="many_to_one")
     .merge(governorates[["governorate", "region"]], on="governorate", how="left", validate="many_to_one")
     .merge(products[["product_id", "product_name", "category", "unit_cost"]], on="product_id", how="left", validate="many_to_one"))
print(orders.shape, "->", s.shape)
s[["order_id", "name", "region", "product_name", "category", "status"]].head()
"""),
md("""
1,501 rows in, 1,501 rows out: every merge was a lookup, none of them added or dropped an order.

---
# 🧰 Summary

| Task | Code |
|---|---|
| One number per group | `df.groupby("g")["col"].sum()` |
| Rows per group | `df.groupby("g").size()` |
| Several groups | `groupby(["g1", "g2"])`, then `unstack()` |
| Several numbers, named | `agg(orders=("order_id", "nunique"), revenue=("revenue", "sum"))` |
| Group value on every row | `df.groupby("g")["col"].transform("sum")` |
| Two-way table of a number | `pivot_table(index=, columns=, values=, aggfunc=, fill_value=0, margins=True)` |
| Two-way table of counts | `pd.crosstab(a, b, normalize="index")` |
| Stack tables | `pd.concat([a, b], ignore_index=True)` |
| Join on a key | `a.merge(b, on="key", how="left", validate="many_to_one", indicator=True)` |

* `inner` drops unmatched rows silently; `left` keeps them so you can see them.
* Keys must match character for character: clean them before the merge.
* A repeated key multiplies rows. Check the row count, and use `validate=`.

**Next lesson:** light cleaning: missing values, duplicates, types and simple outliers.

📚 All the lessons of the course: [zero-grad.com/courses/da](https://zero-grad.com/courses/da/)
"""),
]

if __name__ == "__main__":
    path = write(cells, OUT, "Grouping & Joining")
    print("wrote", path)
    if "--no-run" not in sys.argv:
        execute(path)
        print("executed", path)
