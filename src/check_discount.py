import sqlite3
import pandas as pd

pd.options.display.float_format = "{:,.2f}".format
conn = sqlite3.connect("data/processed/ecommerce.db")

s = pd.read_sql("""
    SELECT order_id, unit_price, quantity, discount, grand_total
    FROM sales WHERE is_sale = 1 AND is_outlier = 0
""", conn)
conn.close()

s["gross"] = s["unit_price"] * s["quantity"]

o = s.groupby("order_id").agg(
    n_rows=("gross", "size"),
    n_disc=("discount", "nunique"),
    n_gt=("grand_total", "nunique"),
    gross=("gross", "sum"),
    disc_sum=("discount", "sum"),
    disc_max=("discount", "max"),
    gt_sum=("grand_total", "sum"),
    gt_max=("grand_total", "max"),
)

single = o[o["n_rows"] == 1]
multi = o[o["n_rows"] > 1]
print("Orders:", len(o), "| single-row:", len(single), "| multi-row:", len(multi))

# 1. In multi-row orders, is the same discount / grand_total repeated on every row?
m_disc = multi[multi["disc_max"] > 0]
print("\nMulti-row orders with a discount:", len(m_disc))
print("  same discount on every row: %.1f%%" % ((m_disc["n_disc"] == 1).mean() * 100))
print("Multi-row orders: same grand_total on every row: %.1f%%" % ((multi["n_gt"] == 1).mean() * 100))
# 2. How far is (gross - discount) from grand_total? (gap % of grand_total)
def gap(a, b):
    return (a.sum() - b.sum()) / b.sum() * 100

print("  multi-row, discount summed, grand_total once :", gap(multi["gross"] - multi["disc_sum"], multi["gt_max"]))
print("\nGap between (gross - discount) and grand_total:")
print("  single-row orders : %.1f%%" % gap(single["gross"] - single["disc_sum"], single["gt_sum"]))
print("  multi-row, discount summed over rows : %.1f%%" % gap(multi["gross"] - multi["disc_sum"], multi["gt_sum"]))
print("  multi-row, discount counted once     : %.1f%%" % gap(multi["gross"] - multi["disc_max"], multi["gt_sum"]))
print("  multi-row, grand_total counted once  : %.1f%%" % gap(multi["gross"] - multi["disc_max"], multi["gt_max"]))

print("""
How to read this:
- If 'same discount on every row' is high and the 'counted once' gap is much
  closer to 0 than the 'summed' gap, discount is an ORDER-level value repeated
  on each item row. Then revenue = price*qty - discount is wrong for
  multi-item orders (discount must be counted once per order).
- If grand_total is the same on every row, it is also an order-level value
  (never SUM it across rows).
- If single-row orders still show a big gap, the gap comes from shipping,
  tax or other charges, not from the discount repeat.
""")