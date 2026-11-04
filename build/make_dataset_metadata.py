"""Write data/dataset-metadata.json (About text, file and column descriptions) and the Kaggle cover image.

Run after make_orders_data.py. To push only the metadata and the cover to Kaggle:
    python build/make_dataset_metadata.py --push
(it copies the two files to a temp folder, because the CLI cannot take an image path outside -p).
"""
import shutil
import subprocess
import sys
import tempfile
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
COVER = ROOT / "assets" / "kaggle" / "nilecart-cover.png"   # outside data/ so it is never uploaded as a data file
COURSE = json.loads((ROOT / "build" / "course.json").read_text(encoding="utf-8"))

DESCRIPTION = """\
**NileCart** is a fictional online shop in Cairo that sells electronics, accessories, office furniture and stationery, and delivers all over Egypt.
Prices are in Egyptian pounds (EGP). The data covers two years of orders, **January 2024 to December 2025**.

This is synthetic teaching data for the **Zero Grad Data Analysis course**.
It is made by a script (seed 42), so every number is reproducible, and it has patterns built in so the charts have a story to tell.

## Which file should I use?

| File | Rows | Use it for |
|---|---|---|
| `sales.csv` | 1,466 | **Start here.** One clean row per order line, already joined with the customer, the product and the region, with `revenue` and `profit` ready. |
| `orders.csv` | 1,501 | The raw orders, with data-quality problems left in on purpose (see below). |
| `customers.csv` | 200 | The raw customer table, with messy text. |
| `products.csv` | 12 | The product catalogue: category, list price and unit cost. |
| `governorates.csv` | 17 | Egypt's governorates in the data: region and delivery fee. |
| `fx_rates.csv` | 106 | Weekly USD to EGP rate, including the March 2024 float. |

Most charts in the course use only the **completed** orders of `sales.csv` (1,074 rows): `sales[sales["status"] == "completed"]`.

## Patterns you can find

- Order volume grows over the two years and peaks in **November and December** (White Friday, New Year), with a smaller back-to-school bump in September.
- Discounts are more frequent in November.
- Big discounts on electronics lose money: some order lines have a **negative profit**.
- **Corporate** customers buy larger quantities.
- Electronics are returned more often than other categories.
- The four categories live on very different price levels, so revenue is strongly **right-skewed** (try a log scale).
- The USD to EGP rate jumps from about 30.9 to about 49 in March 2024.

## Problems left in the raw tables (for cleaning practice)

- `orders.csv`: 30 missing `quantity`, 40 missing `discount`, 10 missing `status`; a quantity of -2 and one of 500; a `unit_price` of 0; an order dated 2031; one duplicated row; 3 orders from customer ids (901, 902) that do not exist.
- `customers.csv`: names with extra spaces and capitals, governorates written as "cairo", "GIZA " and " alexandria", some e-mails in capitals.
- Matrouh has no customers, customers 181 to 200 never ordered, and the Pen Set is never sold.

`sales.csv` is the result of cleaning these: bad rows dropped, the duplicate removed, a missing discount set to 0, a missing status set to `unknown`, and text tidied.
Orders from unknown customers keep `Unknown` in the customer columns.

## Notebooks

The solved notebooks of the Zero Grad Data Analysis course run on this dataset, one per lesson.
"""

ORDER_FIELDS = [
    ("order_id", "integer", "Order line id (10001 and up)."),
    ("order_date", "datetime", "Date of the order, 2024-01-01 to 2025-12-31."),
    ("customer_id", "integer", "Customer who placed the order; joins to customers.csv."),
    ("product_id", "integer", "Product ordered; joins to products.csv."),
    ("quantity", "number", "Number of units in the order line."),
    ("unit_price", "number", "Price of one unit in EGP, within 5% of the list price."),
    ("discount", "number", "Discount as a fraction: 0, 0.05, 0.10 or 0.20."),
    ("status", "string", "completed, shipped, cancelled or returned."),
]
RAW_ORDER = {n: (t, d) for n, t, d in ORDER_FIELDS}

RESOURCES = [
    ("sales.csv",
     "Clean order lines joined with customers, products and governorates, with revenue and profit. Start here.",
     [("order_id", *RAW_ORDER["order_id"]),
      ("order_date", *RAW_ORDER["order_date"]),
      ("customer_id", *RAW_ORDER["customer_id"]),
      ("name", "string", "Customer name, tidied. Unknown when the customer id does not exist."),
      ("governorate", "string", "Customer's governorate, tidied. Unknown when the customer id does not exist."),
      ("region", "string", "Greater Cairo, Alexandria & Coast, Delta, Canal or Upper Egypt."),
      ("segment", "string", "Consumer, Corporate or Small Business."),
      ("product_id", *RAW_ORDER["product_id"]),
      ("product_name", "string", "Product name, e.g. Laptop, Mouse, Desk, Notebook."),
      ("category", "string", "Electronics, Accessories, Furniture or Stationery."),
      ("quantity", *RAW_ORDER["quantity"]),
      ("unit_price", *RAW_ORDER["unit_price"]),
      ("discount", "number", "Discount as a fraction (0, 0.05, 0.10 or 0.20). Missing values set to 0."),
      ("gross", "number", "quantity x unit_price, in EGP, before the discount."),
      ("revenue", "number", "gross x (1 - discount), in EGP: what the customer pays."),
      ("unit_cost", "number", "What one unit costs NileCart, in EGP."),
      ("profit", "number", "revenue - quantity x unit_cost, in EGP. Negative when the discount is bigger than the margin."),
      ("status", "string", "completed, shipped, cancelled, returned, or unknown when it was missing.")]),
    ("orders.csv",
     "Raw orders with planted data-quality problems: missing values, impossible quantities, a zero price, a 2031 date, a duplicate, unknown customers.",
     [(n, t, d) for n, t, d in ORDER_FIELDS]),
    ("customers.csv",
     "Raw customers with messy text (extra spaces, capitals, inconsistent governorate names).",
     [("customer_id", "integer", "Customer id, 1 to 200."),
      ("name", "string", "Customer name (fictional). Some have extra spaces and capitals."),
      ("email", "string", "Fictional e-mail at example.com. Some are in capitals."),
      ("governorate", "string", "Where the customer lives. A few are written inconsistently."),
      ("segment", "string", "Consumer, Corporate or Small Business."),
      ("signup_date", "datetime", "When the customer signed up, 2023 to 2024.")]),
    ("products.csv",
     "The 12 products NileCart sells.",
     [("product_id", "integer", "Product id, 101 to 112."),
      ("product_name", "string", "Product name."),
      ("category", "string", "Electronics, Accessories, Furniture or Stationery."),
      ("list_price", "integer", "Catalogue price of one unit, in EGP."),
      ("unit_cost", "integer", "What one unit costs NileCart, in EGP.")]),
    ("governorates.csv",
     "The 17 governorates NileCart delivers to.",
     [("governorate", "string", "Governorate name."),
      ("region", "string", "Greater Cairo, Alexandria & Coast, Delta, Canal or Upper Egypt."),
      ("delivery_fee", "integer", "Delivery fee to this governorate, in EGP.")]),
    ("fx_rates.csv",
     "Weekly US dollar to Egyptian pound rate (every Monday), with the March 2024 float.",
     [("rate_date", "datetime", "Monday of the week."),
      ("usd_egp", "number", "How many EGP one US dollar buys.")]),
]


def check_columns():
    """Kaggle matches the schema to the columns by position, so the lists must match the files exactly."""
    for path, _, fields in RESOURCES:
        cols = list(pd.read_csv(DATA / path, nrows=0).columns)
        assert cols == [f[0] for f in fields], (path, cols)


def make_cover():
    sales = pd.read_csv(DATA / "sales.csv")
    done = sales[sales["status"] == "completed"]
    cats = ["Stationery", "Accessories", "Furniture", "Electronics"]
    colors = ["#2dd4bf", "#60a5fa", "#fbbf24", "#c084fc"]
    bins = np.logspace(np.log10(40), np.log10(400000), 46)

    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor="#101f40")
    ax = fig.add_axes([0.06, 0.1, 0.88, 0.48], facecolor="#101f40")
    ax.hist([done.loc[done["category"] == c, "revenue"] for c in cats], bins=bins, stacked=True,
            color=colors, edgecolor="#101f40", linewidth=1.2)
    ax.set_xscale("log")
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#f5f2ea80")
    ax.tick_params(colors="#f5f2eacc", labelsize=13, left=False, labelleft=False)
    ax.set_xticks([100, 1000, 10000, 100000], ["100", "1,000", "10,000", "100,000"])
    ax.set_xlabel("order revenue, EGP (log scale)", color="#f5f2eacc", fontsize=14)
    for i, (c, col) in enumerate(zip(cats, colors)):
        fig.text(0.06 + i * 0.16, 0.64, "■ " + c, color=col, fontsize=17, fontweight="bold")

    fig.text(0.06, 0.84, "NileCart Sales", color="#f5f2ea", fontsize=64, fontweight="bold")
    fig.text(0.06, 0.76, "A fictional online shop in Cairo  ·  2024–2025  ·  prices in EGP",
             color="#f5f2eacc", fontsize=22)
    fig.text(0.94, 0.86, "Zero Grad", color="#fbbf24", fontsize=26, fontweight="bold", ha="right")
    fig.text(0.94, 0.81, "Data Analysis course", color="#f5f2eacc", fontsize=17, ha="right")
    COVER.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(COVER, facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    check_columns()
    make_cover()
    meta = {
        "title": "NileCart Sales (Zero Grad)",
        "id": f"{COURSE['kaggle_user']}/{COURSE['kaggle_dataset']}",
        "subtitle": "A fictional online shop in Cairo: orders, customers, products, EGP",
        "description": DESCRIPTION,
        "licenses": [{"name": "CC0-1.0"}],
        "keywords": ["beginner", "data visualization", "exploratory data analysis", "data cleaning"],
        "expectedUpdateFrequency": "never",
        "userSpecifiedSources": "Generated by `build/make_orders_data.py` in the Zero Grad Data Analysis course repo (seed 42).",
        "image": COVER.name,
        "resources": [
            {"path": path, "description": desc,
             "schema": {"fields": [{"name": n, "type": t, "description": d} for n, t, d in fields]}}
            for path, desc, fields in RESOURCES
        ],
    }
    out = DATA / "dataset-metadata.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", out, "and", COVER)
    if "--push" in sys.argv:
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copy(out, tmp)
            shutil.copy(COVER, tmp)
            subprocess.run(["kaggle", "datasets", "metadata", meta["id"], "--update", "-p", tmp], check=True)


if __name__ == "__main__":
    main()
