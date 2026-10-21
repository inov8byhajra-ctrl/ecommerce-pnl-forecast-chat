import sqlite3
import pandas as pd

pd.options.display.float_format = "{:,.0f}".format
conn = sqlite3.connect("data/processed/ecommerce.db")

print("Rows with price x qty > 500,000 (sales only):")
print(pd.read_sql("""
    SELECT order_id, category, unit_price, quantity, grand_total, order_date
    FROM sales WHERE is_sale = 1 AND unit_price * quantity > 500000
    ORDER BY unit_price * quantity DESC
""", conn))

print("\nDuplicate order_id + sku rows (sales only):")
print(pd.read_sql("""
    SELECT COUNT(*) AS duplicate_rows FROM (
        SELECT order_id, sku, COUNT(*) AS n FROM sales
        WHERE is_sale = 1 GROUP BY order_id, sku HAVING n > 1
    )
""", conn))
conn.close()