import sqlite3
import numpy as np
import pandas as pd

DB_FILE = "data/processed/ecommerce.db"
SEED = 42  # fixed, so the same costs are generated every run

conn = sqlite3.connect(DB_FILE)
df = pd.read_sql("SELECT * FROM sales WHERE is_sale = 1", conn)
print("Sales rows:", len(df))

# 1. Simulate cost: each category gets a fixed ratio between 70% and 85% of price
rng = np.random.default_rng(SEED)
categories = sorted(df["category"].unique())
ratios = dict(zip(categories, rng.uniform(0.70, 0.85, len(categories))))
df["unit_cost"] = df["unit_price"] * df["category"].map(ratios)

# 2. P&L numbers per row
df["revenue"] = df["unit_price"] * df["quantity"] - df["discount"]
df["cogs"] = df["unit_cost"] * df["quantity"]
df["gross_profit"] = df["revenue"] - df["cogs"]

# 3. Monthly and category P&L
def make_pnl(data, by):
    pnl = data.groupby(by)[["revenue", "cogs", "gross_profit"]].sum()
    pnl["margin_pct"] = (pnl["gross_profit"] / pnl["revenue"] * 100).round(1)
    return pnl.round(0).reset_index()

monthly = make_pnl(df, "year_month")
by_category = make_pnl(df, "category").sort_values("revenue", ascending=False)

print("\nMonthly P&L:\n", monthly)
print("\nCategory P&L:\n", by_category)

# 4. Sanity check: our revenue vs grand_total
print("\nOur revenue total:", round(df["revenue"].sum()))
print("grand_total sum:  ", round(df["grand_total"].sum()))
print("Negative revenue rows:", (df["revenue"] <= 0).sum())

# 5. Save for the Streamlit page
monthly.to_sql("monthly_pnl", conn, if_exists="replace", index=False)
by_category.to_sql("category_pnl", conn, if_exists="replace", index=False)
conn.close()