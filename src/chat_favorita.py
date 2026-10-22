import sqlite3
import pandas as pd
from llm_chat import ask_llm
from chat_sql import run_sql

SCHEMA = """
SQLite view: sales_rev (one row per store, day and product category)
Columns: date (YYYY-MM-DD text, 2013-01-01 to 2017-08-15), year_month (YYYY-MM),
store_nbr, city, state, store_type, category (product family), units_sold,
onpromotion (number of promoted items), is_holiday, holiday_name,
unit_price, unit_cost, revenue, cogs, gross_profit.
Rules:
- Money columns (revenue, cogs, gross_profit) are SIMULATED. Use SUM(revenue) etc.
- There are NO orders and NO customers in this data. If asked about orders,
  customers or payment methods, return exactly:
  SELECT 'Not available: this dataset has no order or customer data' AS answer
- Questions about the future (forecast, next month) cannot be answered:
  SELECT 'Not available: forecasting is not part of this chat' AS answer
- Return ONE SQLite SELECT query only. No explanation, no markdown.
"""

DB = "data/processed/favorita.db"


def answer(question, conn):
    sample = pd.read_sql("SELECT * FROM sales_rev LIMIT 3", conn).to_string()
    prompt = f"{SCHEMA}\nSample rows:\n{sample}\n\nQuestion: {question}\nSQL:"
    sql = ask_llm(prompt)
    try:
        return sql, run_sql(conn, sql)
    except Exception as e:
        retry = f"{prompt}\n\nYour SQL:\n{sql}\nFailed with error: {e}\nFix it. SQL only:"
        sql = ask_llm(retry)
        return sql, run_sql(conn, sql)


if __name__ == "__main__":
    pd.options.display.float_format = "{:,.0f}".format
    conn = sqlite3.connect(DB)
    while True:
        q = input("\nQuestion (exit to quit): ").strip()
        if q.lower() == "exit":
            break
        try:
            sql, df = answer(q, conn)
            print("SQL:", sql)
            print(df)
        except Exception as e:
            print("Failed:", e)
    conn.close()