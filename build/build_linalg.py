"""Build notebooks/linalg/linalg.ipynb (the solved companion notebook of the Light linear algebra lesson).

    python build/build_linalg.py          # write + execute
    python build/build_linalg.py --no-run # write only
"""
from pathlib import Path
import sys

from nb import code, execute, md, write

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks" / "linalg" / "linalg.ipynb"

cells = [
md("""
# 🧮 Light Linear Algebra: a table is a matrix

**Zero Grad · Data Analysis course · Foundations**

> 📖 **The lesson (in Arabic), with diagrams and interactive widgets:** [zero-grad.com/courses/da/linalg](https://zero-grad.com/courses/da/linalg/)
>
> 🗂️ **The data:** [NileCart Sales on Kaggle](https://www.kaggle.com/datasets/a7madmostafa/nilecart-sales)

This is the solved notebook of the *Light linear algebra* lesson.
No proofs and no formulas to memorise: just the few ideas that every data tool is built on, each one done on NileCart.

We use NumPy here, because it's the library that does linear algebra in Python.
The next lesson is all about NumPy, so for now read the code and look at what comes out.

| # | Part | The idea |
|---|---|---|
| 1 | Scalar, vector, matrix | A number, a list of numbers, a table of numbers |
| 2 | Vector arithmetic | Whole columns at once: `quantity * unit_price` |
| 3 | The dot product | Multiply, then add: a basket's total |
| 4 | A table as a matrix | Rows, columns, shape, transpose |
| 5 | Matrix multiplication | Many dot products at once, and the shape rule |
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
np.set_printoptions(suppress=True, linewidth=110)

# On Kaggle the data lives under /kaggle/input, locally in the repo's data/ folder
on_kaggle = sorted(Path("/kaggle/input").glob("**/sales.csv"))
DATA = on_kaggle[0].parent if on_kaggle else Path("../../data")

sales = pd.read_csv(DATA / "sales.csv", parse_dates=["order_date"])
products = pd.read_csv(DATA / "products.csv")
done = sales[sales["status"] == "completed"]
"""),
md("""
---
# 1️⃣ Scalar, vector, matrix

Three words for three shapes of numbers:

| Name | What it is | NileCart example | `ndim` | `shape` |
|---|---|---|---|---|
| **Scalar** | one number | the VAT rate, 0.14 | 0 | `()` |
| **Vector** | a list of numbers | the `revenue` column | 1 | `(n,)` |
| **Matrix** | a table of numbers | `sales` with its number columns | 2 | `(rows, columns)` |
"""),
code("""
vat = np.array(0.14)
revenue = sales["revenue"].to_numpy()
X = sales[["quantity", "unit_price", "discount", "revenue", "profit"]].to_numpy()

for name, a in [("vat", vat), ("revenue", revenue), ("X", X)]:
    print(f"{name:8} ndim={a.ndim}  shape={a.shape}")
"""),
md("""
**A column is a vector** of 1,466 numbers, one per order line.
**A row is a vector too**: one order line, described by 5 numbers.
"""),
code("""
X[1]
"""),
md("""
Row 1 is the order we met in the Introduction: 9 laptops at 30,400 EGP each, 5% discount, 259,920 EGP of revenue and 15,120 EGP of profit.

The order of the numbers matters. `X[1]` only makes sense because we know the columns are
`quantity, unit_price, discount, revenue, profit`, in that order.
A vector is an **ordered** list.
"""),
md("""
---
# 2️⃣ Vector arithmetic: whole columns at once

Two vectors of the same length can be added, subtracted, multiplied and divided **element by element**:
the first with the first, the second with the second, and so on.

That's how every derived column in NileCart was made:
"""),
code("""
q = sales["quantity"].to_numpy()
p = sales["unit_price"].to_numpy()
d = sales["discount"].to_numpy()

gross = q * p                    # element by element
rev = gross * (1 - d)

print(q[:4], "*", p[:4], "=", gross[:4])
print("same as the gross column:  ", np.allclose(gross, sales["gross"]))
print("same as the revenue column:", np.allclose(rev, sales["revenue"]))
"""),
md("""
No loop. One line works on all 1,466 rows.
The two vectors must have the **same length**: element 7 of `q` pairs with element 7 of `p`.

## 2.1 A vector and a scalar

A scalar meets every element of the vector. Adding 14% VAT to every order:
"""),
code("""
with_vat = rev * (1 + vat)
print(rev[:4])
print(with_vat[:4])
"""),
md("""
The same works for a currency. The last dollar rate in `fx_rates.csv`:
"""),
code("""
fx = pd.read_csv(DATA / "fx_rates.csv")
usd_egp = fx["usd_egp"].iloc[-1]
print("1 USD =", usd_egp, "EGP")
(rev / usd_egp)[:4].round(2)
"""),
md("""
Multiplying a vector by a scalar **scales** it: every element grows or shrinks by the same factor.
"""),
md("""
---
# 3️⃣ The dot product: multiply, then add

The **dot product** of two vectors of the same length:
multiply them element by element, then add everything up.

$$\\mathbf{q} \\cdot \\mathbf{p} = q_1 p_1 + q_2 p_2 + \\dots + q_n p_n$$

It's the most common calculation in data analysis, even when nobody calls it that.
A basket: a monitor, two keyboards, three mice and ten notebooks.
"""),
code("""
items = ["Monitor", "Keyboard", "Mouse", "Notebook"]
basket = np.array([1, 2, 3, 10])                                   # how many of each
price = products.set_index("product_name").loc[items, "list_price"].to_numpy()

print("quantities:", basket)
print("prices:    ", price)
print("products:  ", basket * price)
print("total:     ", basket @ price)                              # @ is the dot product
"""),
md("""
`basket @ price` is the dot product: the bill of the basket.

## 3.1 The whole table in one dot product

The quantity vector dotted with the price vector gives the gross value of **all** the orders:
"""),
code("""
print(f"q @ p           = {q @ p:,.0f}")
print(f"gross.sum()     = {sales['gross'].sum():,.0f}")
"""),
md("""
---
# 4️⃣ A table as a matrix

`X` from Part 1 is the number part of `sales` as a matrix: 1,466 rows and 5 columns.
"""),
code("""
cols = ["quantity", "unit_price", "discount", "revenue", "profit"]
print("shape:", X.shape)
X[:5]
"""),
md("""
## 4.1 Rows, columns, one cell

`X[i, j]` is row `i`, column `j`. A whole row is `X[i]`, a whole column is `X[:, j]`.
"""),
code("""
print("one cell, X[1, 3]: ", X[1, 3])                 # row 1, column 3 = revenue
print("one row, X[1]:     ", X[1])
print("one column, X[:, 3]:", X[:5, 3], "...")
"""),
md("""
## 4.2 Transpose

The **transpose** `X.T` turns rows into columns: shape `(1466, 5)` becomes `(5, 1466)`.
"""),
code("""
print(X.shape, "->", X.T.shape)
"""),
md("""
## 4.3 Column sums are a matrix product

A vector of ones, multiplied by the matrix, adds up every column:
"""),
code("""
ones = np.ones(len(X))
pd.Series(ones @ X, index=cols)
"""),
code("""
sales[cols].sum()
"""),
md("""
Same numbers. Divide by the number of rows and you have the column means.
(A sum of prices or of discounts means nothing, but the calculation is the same for every column.)
`sum()` and `mean()` in Pandas are this calculation, done fast.
"""),
md("""
---
# 5️⃣ Matrix multiplication

A matrix times a vector is one dot product **per row**.
A matrix times a matrix is one dot product **per pair (row of the first, column of the second)**.

## 5.1 A matrix times a vector

The four Electronics products, units sold in each quarter of 2025 (completed orders):
"""),
code("""
elec = ["Laptop", "Phone", "Tablet", "Monitor"]
d25 = done[(done["order_date"].dt.year == 2025) & done["product_name"].isin(elec)]
Q = d25.pivot_table(index=d25["order_date"].dt.quarter, columns="product_name",
                    values="quantity", aggfunc="sum").reindex(columns=elec).astype(int)
Q.index = ["Q1", "Q2", "Q3", "Q4"]
Q
"""),
md("""
`Q` is a 4 × 4 matrix: quarters × products. The list price is a vector of 4, one per product.
`Q @ price` dots every quarter's row with the prices: the sales of each quarter, at list price.
"""),
code("""
P = products.set_index("product_name").loc[elec, ["list_price", "unit_cost"]]
list_price = P["list_price"].to_numpy()

pd.Series(Q.to_numpy() @ list_price, index=Q.index, name="sales at list price")
"""),
md("""
Q4 sold the most by far: White Friday and New Year.

## 5.2 A matrix times a matrix

Put the price **and** the cost side by side: `P` is 4 products × 2 columns.
`Q @ P` does both dot products for every quarter at once:
"""),
code("""
P
"""),
code("""
QP = pd.DataFrame(Q.to_numpy() @ P.to_numpy(), index=Q.index, columns=["sales", "cost"])
QP["margin"] = QP["sales"] - QP["cost"]
QP
"""),
md("""
Each cell of the result is one row of `Q` dotted with one column of `P`. Q4's sales, by hand:
"""),
code("""
print(Q.loc["Q4"].to_numpy(), "@", P["list_price"].to_numpy())
print(f"= {Q.loc['Q4'].to_numpy() @ P['list_price'].to_numpy():,.0f}")
"""),
md("""
## 5.3 The shape rule

$$(m \\times n) \\; @ \\; (n \\times k) = (m \\times k)$$

The **inside** numbers must match (the columns of the first = the rows of the second),
and the **outside** numbers give the shape of the result.

`Q` is (4 × 4) and `P` is (4 × 2), so `Q @ P` is (4 × 2). The other way round doesn't work:
"""),
code("""
print("Q:", Q.shape, " P:", P.shape, " Q @ P:", (Q.to_numpy() @ P.to_numpy()).shape)

try:
    P.to_numpy() @ Q.to_numpy()
except ValueError as e:
    print("P @ Q ->", e)
"""),
md("""
(4 × **2**) @ (**4** × 4): the inside numbers are 2 and 4, they don't match.
Order matters in matrix multiplication: `A @ B` and `B @ A` are not the same thing, and often only one of them exists.

When you get a *shapes not aligned* error, print the two shapes and check the inside numbers.
"""),
md("""
## 5.4 The whole year

The same calculation on all 11 products and all 8 quarters of the two years: (8 × 11) @ (11 × 2).
"""),
code("""
Qall = done.pivot_table(index=done["order_date"].dt.to_period("Q"), columns="product_name",
                        values="quantity", aggfunc="sum", fill_value=0)
Pall = products.set_index("product_name").loc[Qall.columns, ["list_price", "unit_cost"]]
print("Q:", Qall.shape, " P:", Pall.shape)

year = pd.DataFrame(Qall.to_numpy() @ Pall.to_numpy(), index=Qall.index.astype(str), columns=["sales", "cost"])
ax = year.plot(kind="bar", color=["#2563eb", "#9ca3af"], rot=0)
ax.set(title="Q @ P: sales and cost per quarter, at list price (EGP)", xlabel="")
plt.show()
"""),
md("""
Every Q4 towers over the other quarters. That's the November–December peak from the Introduction, now from one matrix product.

*At list price:* real revenue is a bit different, because prices moved ±5% and some orders had a discount.
`Q @ P` answers "how much would this have been at list price?", which is still a useful number for planning.
"""),
md("""
---
# 🧰 Summary

| Idea | In one line | NumPy |
|---|---|---|
| Scalar · vector · matrix | a number · a list · a table | `ndim`, `shape` |
| Element-wise | same length, first with first | `q * p` |
| Scalar × vector | every element, same factor | `rev * 1.14` |
| Dot product | multiply, then add | `q @ p` |
| A table as a matrix | rows × columns, `X[i, j]` | `df.to_numpy()` |
| Transpose | rows ↔ columns | `X.T` |
| Matrix product | a dot product per (row, column) | `Q @ P` |
| Shape rule | (m × **n**) @ (**n** × k) = (m × k) | |

**Next lesson:** NumPy: arrays, and computing on a whole column at once.

📚 All the lessons of the course: [zero-grad.com/courses/da](https://zero-grad.com/courses/da/)
"""),
]

if __name__ == "__main__":
    path = write(cells, OUT, "Light Linear Algebra")
    print("wrote", path)
    if "--no-run" not in sys.argv:
        execute(path)
        print("executed", path)
