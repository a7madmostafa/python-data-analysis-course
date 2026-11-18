"""Generate the NileCart shop tables (orders, customers, products, governorates, fx_rates).

NileCart is an online shop in Cairo (electronics, accessories, office furniture, stationery)
that delivers across Egypt. Prices are in EGP.

Same schema idea and the same planted problems as the generator in
Raw Material/Pandas/pandas_tutorial.ipynb, plus built-in patterns so charts
have a story to tell:
  - 2 years of orders (2024-2025): order volume grows and peaks in Nov/Dec (White Friday, New Year),
    with a smaller back-to-school bump in September
  - products carry a unit_cost -> profit; big discounts on electronics lose money
  - discounts are more frequent in November (White Friday)
  - Corporate customers buy larger quantities
  - fx_rates: weekly USD->EGP rate, including the March 2024 float (about 30.9 -> 47-50)
Planted problems:
  missing quantity/discount/status, quantity -2 and 500, unit_price 0,
  a 2031 order date, a duplicated row, orphan customer ids 901/902,
  messy customer text ("cairo", "GIZA ", " alexandria"), Matrouh has no customers, Pen Set is never sold.
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd


def build(out_dir="data/nilecart", seed=42):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    products = pd.DataFrame({
        "product_id":   np.arange(101, 113),
        "product_name": ["Laptop", "Phone", "Tablet", "Monitor", "Keyboard", "Mouse", "Backpack",
                         "Desk", "Chair", "Lamp", "Notebook", "Pen Set"],
        "category":     ["Electronics"] * 4 + ["Accessories"] * 3 + ["Furniture"] * 3 + ["Stationery"] * 2,
        "list_price":   [32000, 18000, 11000, 7000, 1200, 450, 900, 6500, 3800, 750, 60, 150],
        "unit_cost":    [27200, 14600, 9000, 5700, 600, 190, 420, 3700, 2000, 370, 20, 50],
    })

    governorates = pd.DataFrame({
        "governorate":  ["Cairo", "Giza", "Qalyubia", "Alexandria", "Beheira", "Matrouh", "Dakahlia", "Sharqia",
                         "Gharbia", "Monufia", "Port Said", "Ismailia", "Suez", "Assiut", "Sohag", "Luxor", "Aswan"],
        "region":       ["Greater Cairo"] * 3 + ["Alexandria & Coast"] * 3 + ["Delta"] * 4 + ["Canal"] * 3
                        + ["Upper Egypt"] * 4,
        "delivery_fee": [50, 50, 60, 70, 80, 120, 75, 75, 75, 75, 90, 90, 90, 110, 120, 130, 140],
    })

    n_cust = 200
    first = np.array(["ahmed", "mona", "youssef", "nour", "omar", "salma", "karim", "hana", "mahmoud", "fatma",
                      "mostafa", "yasmin", "khaled", "laila", "tarek", "dina", "amr", "reem", "hossam", "mariam"])
    last = np.array(["hassan", "ibrahim", "el-sayed", "mostafa", "abdelrahman", "fawzy", "gamal", "saleh",
                     "nabil", "farouk"])
    fn, ln = rng.choice(first, n_cust), rng.choice(last, n_cust)
    gov_with_customers = governorates.loc[governorates["governorate"] != "Matrouh", "governorate"].to_numpy()
    gov_w = np.array([.28, .14, .05, .14, .03, .07, .05, .05, .03, .03, .02, .02, .03, .02, .02, .02])
    customers = pd.DataFrame({
        "customer_id": np.arange(1, n_cust + 1),
        "name":        [f"{a.title()} {b.title()}" for a, b in zip(fn, ln)],
        "email":       [f"{a}.{b.replace('-', '')}{i}@example.com" for i, (a, b) in enumerate(zip(fn, ln), start=1)],
        "governorate": rng.choice(gov_with_customers, n_cust, p=gov_w / gov_w.sum()),
        "segment":     rng.choice(["Consumer", "Corporate", "Small Business"], n_cust, p=[.60, .25, .15]),
        "signup_date": pd.Timestamp("2023-01-01") + pd.to_timedelta(rng.integers(0, 700, n_cust), unit="D"),
    })
    customers.loc[0:9, "name"] = "  " + customers.loc[0:9, "name"].str.upper() + " "
    customers.loc[[3, 15, 40], "governorate"] = ["cairo", "GIZA ", " alexandria"]
    customers.loc[[5, 6, 7, 8], "email"] = customers.loc[[5, 6, 7, 8], "email"].str.upper()

    # ---------- order dates: growth + seasonality ----------
    n = 1500
    days = pd.date_range("2024-01-01", "2025-12-31", freq="D")
    month_factor = {1: .80, 2: .75, 3: .90, 4: .90, 5: .95, 6: .95, 7: .90, 8: .95, 9: 1.10, 10: 1.05, 11: 1.55, 12: 1.75}
    trend = np.linspace(1.0, 1.35, len(days))                           # more orders over time
    weekend = np.where(days.dayofweek.isin([4, 5]), 1.15, 1.0)          # Friday + Saturday weekend
    day_w = trend * days.month.map(month_factor).to_numpy() * weekend
    order_date = rng.choice(days.to_numpy(), n, p=day_w / day_w.sum())
    order_date = np.sort(order_date)
    month = pd.DatetimeIndex(order_date).month

    # ---------- who buys what ----------
    w = np.array([2, 4, 3, 3, 6, 8, 5, 2, 3, 4, 8, 0], dtype=float); w /= w.sum()   # Pen Set is never sold
    cust_w = rng.gamma(1.0, 1.0, 180); cust_w /= cust_w.sum()                       # customers 181-200 never order
    customer_id = rng.choice(np.arange(1, 181), n, p=cust_w)
    product_id = rng.choice(products["product_id"].to_numpy(), n, p=w)
    price_map = products.set_index("product_id")["list_price"]
    unit_price = (price_map.reindex(product_id).to_numpy() * rng.choice([0.95, 1.0, 1.05], n)).round(0)

    segment = customers.set_index("customer_id")["segment"].reindex(customer_id).to_numpy()
    quantity = np.where(segment == "Corporate", rng.integers(2, 11, n), rng.integers(1, 6, n)).astype(float)

    p_normal, p_november = [.55, .20, .15, .10], [.25, .20, .20, .35]
    discount = np.where(month == 11,
                        rng.choice([0, 0.05, 0.10, 0.20], n, p=p_november),
                        rng.choice([0, 0.05, 0.10, 0.20], n, p=p_normal))

    is_elec = np.isin(product_id, [101, 102, 103, 104])                  # electronics are returned more often
    status = rng.choice(["completed", "shipped", "cancelled"], n, p=[.78, .15, .07]).astype(object)
    status = np.where(rng.random(n) < np.where(is_elec, 0.14, 0.05), "returned", status).astype(object)

    # ---------- planted problems ----------
    quantity[rng.choice(n, 30, replace=False)] = np.nan                  # 30 missing quantities
    discount[rng.choice(n, 40, replace=False)] = np.nan                  # 40 missing discounts
    status[rng.choice(n, 10, replace=False)] = None                      # 10 missing statuses
    customer_id[[10, 500, 900]] = [901, 902, 901]                        # 3 orphan orders

    orders = pd.DataFrame({
        "order_id":    np.arange(10001, 10001 + n),
        "order_date":  order_date,
        "customer_id": customer_id,
        "product_id":  product_id,
        "quantity":    quantity,
        "unit_price":  unit_price,
        "discount":    discount,
        "status":      status,
    })
    orders.loc[7, "quantity"] = -2                                       # negative quantity
    orders.loc[250, "quantity"] = 500                                    # absurd quantity
    orders.loc[900, "unit_price"] = 0.0                                  # free item?
    orders.loc[1200, "order_date"] = pd.Timestamp("2031-03-15")          # date in the future
    orders = pd.concat([orders, orders.iloc[[3]]], ignore_index=True)    # a duplicated row
    orders = orders.sample(frac=1, random_state=7).reset_index(drop=True)

    # weekly USD -> EGP rate: fixed near 30.9, then the March 2024 float
    rate_date = pd.date_range("2023-12-25", "2025-12-29", freq="W-MON")
    t = np.arange(len(rate_date))
    level = np.where(rate_date < pd.Timestamp("2024-03-06"), 30.9,
                     np.interp(t, [10, 20, 45, 70, len(t) - 1], [49.5, 47.3, 48.6, 50.6, 48.9]))
    noise = np.where(rate_date < pd.Timestamp("2024-03-06"), 0, rng.normal(0, 0.15, len(t)))
    fx_rates = pd.DataFrame({"rate_date": rate_date, "usd_egp": (level + noise).round(2)})

    tables = {"orders": orders, "customers": customers, "products": products,
              "governorates": governorates, "fx_rates": fx_rates}
    for name, frame in tables.items():
        frame.to_csv(out / f"{name}.csv", index=False)
    (out / "countries.csv").unlink(missing_ok=True)                      # replaced by governorates.csv
    return tables


def build_sales(out_dir="data/nilecart"):
    """The clean, enriched `sales` table of Session 2 (same rules), saved as sales.csv.

    Sessions 3-4 start their charts from it."""
    out = Path(out_dir)
    t = build(out)
    orders, customers, products, governorates = t["orders"].copy(), t["customers"].copy(), t["products"], t["governorates"]
    orders["order_date"] = pd.to_datetime(orders["order_date"])

    bad = ((orders["quantity"] <= 0) | (orders["quantity"] > 100) |
           (orders["unit_price"] <= 0) | (orders["order_date"] > pd.Timestamp("2025-12-31")))
    s = orders.loc[~bad].drop_duplicates().dropna(subset=["quantity"]).copy()
    s["discount"] = s["discount"].fillna(0)
    s["status"] = s["status"].fillna("unknown")
    s["gross"] = (s["quantity"] * s["unit_price"]).round(2)
    s["revenue"] = (s["gross"] * (1 - s["discount"])).round(2)

    for col in ["name", "governorate"]:
        customers[col] = customers[col].str.strip().str.title()
    s = s.merge(customers[["customer_id", "name", "governorate", "segment"]], on="customer_id", how="left",
                validate="many_to_one")
    s = s.merge(governorates[["governorate", "region"]], on="governorate", how="left", validate="many_to_one")
    s = s.merge(products[["product_id", "product_name", "category", "unit_cost"]], on="product_id", how="left",
                validate="many_to_one")
    s[["name", "governorate", "segment", "region"]] = s[["name", "governorate", "segment", "region"]].fillna("Unknown")
    s["profit"] = (s["revenue"] - s["quantity"] * s["unit_cost"]).round(2)

    s = s.sort_values("order_date").reset_index(drop=True)
    cols = ["order_id", "order_date", "customer_id", "name", "governorate", "region", "segment", "product_id",
            "product_name", "category", "quantity", "unit_price", "discount", "gross", "revenue", "unit_cost",
            "profit", "status"]
    s[cols].to_csv(out / "sales.csv", index=False)
    return s[cols]


if __name__ == "__main__":
    build_sales(sys.argv[1] if len(sys.argv) > 1 else "data/nilecart")
