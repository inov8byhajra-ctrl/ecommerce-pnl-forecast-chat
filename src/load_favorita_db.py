import sqlite3
import pandas as pd

DB = "data/processed/favorita.db"
COLS = ["date", "store_nbr", "family", "sales", "onpromotion", "city", "state",
        "store_type", "is_holiday", "holiday_name", "sim_unit_price",
        "sim_unit_cost", "sim_revenue", "sim_cogs"]

conn = sqlite3.connect(DB)
conn.execute("DROP TABLE IF EXISTS favorita_raw")
for c in pd.read_csv("data/raw/favorita.csv", usecols=COLS, chunksize=500_000):
    c.to_sql("favorita_raw", conn, if_exists="append", index=False)

conn.execute("DROP VIEW IF EXISTS sales_rev")
conn.execute("""
CREATE VIEW sales_rev AS
SELECT date, substr(date, 1, 7) AS year_month, store_nbr, city, state, store_type,
       family AS category, sales AS units_sold, onpromotion, is_holiday, holiday_name,
       sim_unit_price AS unit_price, sim_unit_cost AS unit_cost,
       sim_revenue AS revenue, sim_cogs AS cogs,
       sim_revenue - sim_cogs AS gross_profit
FROM favorita_raw
""")
conn.commit()
print("Rows:", conn.execute("SELECT COUNT(*) FROM favorita_raw").fetchone()[0])
conn.close()