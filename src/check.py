import sqlite3
import pandas as pd

pd.options.display.float_format = "{:,.0f}".format
conn = sqlite3.connect("data/processed/ecommerce.db")

print("Top 10 rows by revenue (sales only):")
print(pd.read_sql("""
    SELECT category, unit_price, quantity, discount, grand_total, order_date
    FROM sales WHERE is_sale = 1
    ORDER BY unit_price * quantity DESC LIMIT 10
""", conn))

print("\nDiscount as % of price x quantity, per category:")
print(pd.read_sql("""
    SELECT category,
           SUM(discount) * 100.0 / SUM(unit_price * quantity) AS discount_pct
    FROM sales WHERE is_sale = 1
    GROUP BY category ORDER BY discount_pct DESC
""", conn))

print("\nTop 5 days by revenue in 2017-11:")
print(pd.read_sql("""
    SELECT order_date, SUM(unit_price * quantity - discount) AS revenue
    FROM sales WHERE is_sale = 1 AND year_month = '2017-11'
    GROUP BY order_date ORDER BY revenue DESC LIMIT 5
""", conn))
conn.close()