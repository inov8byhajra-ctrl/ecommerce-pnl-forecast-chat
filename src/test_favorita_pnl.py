import pandas as pd
from pnl import build_pnl

cols = ["date", "family", "sales", "sim_unit_price", "sim_unit_cost",
        "sim_revenue", "sim_cogs"]
df = pd.read_csv("data/raw/favorita.csv", usecols=cols)
print("Rows:", len(df))

mapping = {"date": "date", "price": "sim_unit_price", "quantity": "sales",
           "cost": "sim_unit_cost", "category": "family"}
r = build_pnl(df, mapping, cost_mode="column")

print("\nValidation:")
for k, v in r["validation"].items():
    print(f"  {k}: {v}")

print("\nOur revenue:", r["total_revenue"], "| file sim_revenue:", round(df["sim_revenue"].sum()))
print("Our COGS   :", round(r["monthly"]["cogs"].sum()), "| file sim_cogs   :", round(df["sim_cogs"].sum()))
print("\nBy category:\n", r["by_category"].head(10))