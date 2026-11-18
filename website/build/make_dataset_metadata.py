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

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "nilecart"
COVER = ROOT / "website" / "assets" / "kaggle" / "nilecart-cover.png"   # outside data/ so it is never uploaded as a data file
COURSE = json.loads((ROOT / "website" / "build" / "course.json").read_text(encoding="utf-8"))

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

## The course

This dataset is used by the **Zero Grad Data Analysis course** (in Arabic): [zero-grad.com/courses/da](https://zero-grad.com/courses/da/).
Every lesson is a page with diagrams and interactive charts, plus a solved notebook. These notebooks run on this dataset:

"""


def nilecart_notebooks():
    """The lessons whose Kaggle notebook attaches this dataset, in course order."""
    rows = []
    for slug, lesson in COURSE["lessons"].items():
        meta = ROOT / "website" / "kaggle" / f"{slug}.json"
        dataset = f"{COURSE['kaggle_user']}/{COURSE['kaggle_dataset']}"
        if lesson.get("kaggle_slug") and meta.exists() and dataset in json.loads(meta.read_text(encoding="utf-8"))["dataset_sources"]:
            rows.append(f"- [{lesson['title']}](https://www.kaggle.com/code/{COURSE['kaggle_user']}/{lesson['kaggle_slug']})")
    return "\n".join(rows) + "\n"


DESCRIPTION += nilecart_notebooks()

ORDER_FIELDS = [
    ("order_id", "integer", "Order line id (10001 and up)."),
    ("order_date", "datetime", "Date of the order, 2024-01-01 to 2025-12-31."),
    ("customer_id", "integer", "Customer who placed the order; joins to customers.csv."),
    ("product_id", "integer", "Product ordered; joins to products.csv."),
    ("quantity", "numeric", "Number of units in the order line."),
    ("unit_price", "numeric", "Price of one unit in EGP, within 5% of the list price."),
    ("discount", "numeric", "Discount as a fraction: 0, 0.05, 0.10 or 0.20."),
    ("status", "string", "completed, shipped, cancelled or returned."),
]
RAW_ORDER = {n: (t, d) for n, t, d in ORDER_FIELDS}
RAW_NOTES = {   # what is different in the raw orders.csv
    "order_date": "Date of the order, 2024-01-01 to 2025-12-31 (one is dated 2031 by mistake).",
    "quantity": "Number of units in the order line. 30 are missing, one is -2 and one is 500.",
    "unit_price": "Price of one unit in EGP, within 5% of the list price. One is 0.",
    "discount": "Discount as a fraction: 0, 0.05, 0.10 or 0.20. 40 are missing.",
    "status": "completed, shipped, cancelled or returned. 10 are missing.",
}

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
      ("discount", "numeric", "Discount as a fraction (0, 0.05, 0.10 or 0.20). Missing values set to 0."),
      ("gross", "numeric", "quantity x unit_price, in EGP, before the discount."),
      ("revenue", "numeric", "gross x (1 - discount), in EGP: what the customer pays."),
      ("unit_cost", "numeric", "What one unit costs NileCart, in EGP."),
      ("profit", "numeric", "revenue - quantity x unit_cost, in EGP. Negative when the discount is bigger than the margin."),
      ("status", "string", "completed, shipped, cancelled, returned, or unknown when it was missing.")]),
    ("orders.csv",
     "Raw orders with planted data-quality problems: missing values, impossible quantities, a zero price, a 2031 date, a duplicate, unknown customers.",
     [(n, t, RAW_NOTES.get(n, d)) for n, t, d in ORDER_FIELDS]),
    ("customers.csv",
     "Raw customers with messy text (extra spaces, capitals, inconsistent governorate names).",
     [("customer_id", "integer", "Customer id, 1 to 200."),
      ("name", "string", "Customer name (fictional). Some have extra spaces and capitals."),
      ("email", "email", "Fictional e-mail at example.com. Some are in capitals."),
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
      ("usd_egp", "numeric", "How many EGP one US dollar buys.")]),
]


def check_columns():
    """Kaggle matches the schema to the columns by position, so the lists must match the files exactly."""
    for path, _, fields in RESOURCES:
        cols = list(pd.read_csv(DATA / path, nrows=0).columns)
        assert cols == [f[0] for f in fields], (path, cols)


def palm(ax, x, y, h, lean, color, z=5):
    """A palm-tree silhouette: a curved trunk and a crown of drooping fronds."""
    t = np.linspace(0, 1, 30)
    tx, ty = x + lean * t ** 2, y + h * t
    ax.fill_betweenx(ty, tx - 3.2 * (1 - t) - 1.4, tx + 3.2 * (1 - t) + 1.4, color=color, zorder=z, lw=0)
    top = (tx[-1], ty[-1])
    for ang, length in [(15, 1.0), (45, .85), (100, .7), (150, .85), (175, 1.0), (205, .7), (-20, .8)]:
        a = np.radians(ang)
        s = np.linspace(0, 1, 20)
        L = h * .5 * length
        fx = top[0] + np.cos(a) * L * s
        fy = top[1] + np.sin(a) * L * s - (L * .55) * s ** 2           # fronds droop
        w = 4.5 * np.sin(np.pi * s) + .4
        ax.fill(np.r_[fx, fx[::-1]], np.r_[fy + w, fy[::-1] - w * .3], color=color, zorder=z, lw=0)


def make_cover():
    """An original illustration: sunset over the Nile, the pyramids, a felucca and palm trees."""
    W, H, HORIZON = 800, 400, 150
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")

    def gradient(y0, y1, stops):
        ys = np.linspace(0, 1, 256)
        cols = np.array([np.interp(ys, [p for p, _ in stops], [matplotlib.colors.to_rgb(c)[k] for _, c in stops])
                         for k in range(3)]).T
        ax.imshow(cols[:, None, :], extent=[0, W, y0, y1], origin="lower", aspect="auto", zorder=0)

    # sky: night at the top, sunset at the horizon
    gradient(HORIZON, H, [(0, "#fbbf24"), (.18, "#f97316"), (.45, "#be185d"), (.75, "#3b1f5e"), (1, "#101f40")])
    sun = (W / 2, HORIZON + 26)
    for r, a in [(70, .10), (55, .16), (44, .9)]:
        ax.add_patch(plt.Circle(sun, r, color="#fde68a", alpha=a, zorder=1, lw=0))

    # the pyramids of Giza on the far bank
    for cx, half, ht in [(95, 78, 92), (205, 70, 80), (285, 38, 44)]:
        ax.fill([cx - half, cx, cx + half], [HORIZON, HORIZON + ht, HORIZON], color="#7c2d12", zorder=2, lw=0)
        ax.fill([cx, cx + half, cx + half * .35], [HORIZON + ht, HORIZON, HORIZON], color="#9a3412", zorder=2, lw=0)
    ax.fill_between([0, W], HORIZON - 6, HORIZON + 4, color="#3b1608", zorder=3, lw=0)   # far bank
    for x, h in [(340, 34), (362, 28), (690, 40), (712, 30), (735, 36)]:
        palm(ax, x, HORIZON, h, 4, "#3b1608", z=3)

    # the Nile, with the sun's reflection
    gradient(0, HORIZON - 6, [(0, "#0b1d33"), (.7, "#1e3a5f"), (1, "#7c3a3a")])
    rng = np.random.default_rng(3)
    for i in range(14):
        y = HORIZON - 10 - i * 9.5
        half = 36 - i * 2.1 + rng.uniform(-4, 4)
        ax.plot([sun[0] - half, sun[0] + half], [y, y], color="#fbbf24", lw=2.2 - i * .1, alpha=.8 - i * .045,
                solid_capstyle="round", zorder=4)

    # a felucca
    fx, fy = 560, 70
    ax.fill([fx - 46, fx + 50, fx + 36, fx - 34], [fy + 10, fy + 10, fy, fy], color="#140c08", zorder=6, lw=0)
    ax.plot([fx + 4, fx + 4], [fy + 10, fy + 92], color="#140c08", lw=1.8, zorder=6)          # mast
    ax.fill([fx - 30, fx + 74, fx + 52], [fy + 16, fy + 134, fy + 16], color="#1c1009", zorder=6, lw=0)  # lateen sail
    ax.plot([fx - 36, fx + 78], [fy + 12, fy + 139], color="#140c08", lw=1.4, zorder=6)        # yard
    for i in range(4):                                                                          # its reflection
        ax.plot([fx - 36 + i * 8, fx + 42 - i * 8], [fy - 8 - i * 7] * 2, color="#140c08", lw=2, alpha=.5,
                solid_capstyle="round", zorder=5)
    for bx, by, bw, bh in [(fx - 34, fy + 10, 16, 12), (fx - 17, fy + 10, 14, 10), (fx - 30, fy + 22, 13, 10)]:
        ax.add_patch(plt.Rectangle((bx, by), bw, bh, facecolor="#b45309", edgecolor="#140c08", lw=1, zorder=6))
        ax.plot([bx + bw / 2] * 2, [by, by + bh], color="#fde68a", lw=1, alpha=.8, zorder=6)    # parcel tape

    # palms in front, at both edges
    for x, h, lean in [(25, 150, 22), (60, 120, 30), (770, 160, -24), (740, 115, -30)]:
        palm(ax, x, 0, h, lean, "#0a0604", z=7)

    COVER.parent.mkdir(parents=True, exist_ok=True)
    tmp = COVER.with_suffix(".big.png")
    fig.savefig(tmp)                                  # 1600 x 800, then scaled down for smooth edges
    plt.close(fig)
    from PIL import Image
    Image.open(tmp).convert("RGB").resize((W, H), Image.LANCZOS).save(COVER)
    tmp.unlink()


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
