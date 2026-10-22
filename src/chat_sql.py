import sqlite3
import pandas as pd

DB_FILE = "data/processed/ecommerce.db"

VIEW_SQL = """
CREATE VIEW sales_rev AS
SELECT order_id, order_date, year_month, category, payment_method,
       customer_id, quantity, unit_price, gross, disc,
       gross - disc AS revenue
FROM (
    SELECT order_id, order_date, year_month, category, payment_method,
           customer_id, quantity, unit_price,
           unit_price * quantity AS gross,
           CASE WHEN ROW_NUMBER() OVER (
                    PARTITION BY order_id ORDER BY item_id) = 1
                THEN discount ELSE 0 END AS disc
    FROM sales
    WHERE is_sale = 1 AND is_outlier = 0
)
"""


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DROP VIEW IF EXISTS sales_rev")
    conn.execute(VIEW_SQL)
    return conn


def run_sql(conn, sql):
    """Only a single SELECT is allowed."""
    s = sql.strip().rstrip(";")
    if not s.lower().startswith(("select", "with")) or ";" in s:
        raise ValueError("Only a single SELECT query is allowed.")
    return pd.read_sql(s, conn)


# ---------- 5 fixed questions, SQL written by hand ----------
QUESTIONS = {
    "1. Total revenue": """
        SELECT SUM(revenue) AS total_revenue FROM sales_rev""",
    "2. Top 5 months by revenue": """
        SELECT year_month, SUM(revenue) AS revenue FROM sales_rev
        GROUP BY year_month ORDER BY revenue DESC LIMIT 5""",
    "3. Top 5 categories by revenue": """
        SELECT category, SUM(revenue) AS revenue FROM sales_rev
        GROUP BY category ORDER BY revenue DESC LIMIT 5""",
    "4. Orders per payment method": """
        SELECT payment_method, COUNT(DISTINCT order_id) AS orders
        FROM sales_rev GROUP BY payment_method ORDER BY orders DESC""",
    "5. Average order value": """
        SELECT SUM(revenue) * 1.0 / COUNT(DISTINCT order_id) AS avg_order_value
        FROM sales_rev""",
}

if __name__ == "__main__":
    pd.options.display.float_format = "{:,.0f}".format
    conn = get_conn()
    for q, sql in QUESTIONS.items():
        print("\n" + q)
        print(run_sql(conn, sql))
    conn.close()