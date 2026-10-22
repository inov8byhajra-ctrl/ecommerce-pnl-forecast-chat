import pandas as pd
from dotenv import load_dotenv
from google import genai
from chat_sql import get_conn, run_sql
import time 
load_dotenv()
client = genai.Client()
MODELS = ["gemini-3.6-flash"]  # from list_models.py

SCHEMA = """
SQLite view: sales_rev (one row per item; only real sales, outliers removed)
Columns: order_id, order_date (YYYY-MM-DD text), year_month (YYYY-MM),
category, payment_method, customer_id, quantity, unit_price,
gross, disc, revenue.
Rules:
- This data has NO cost information. Profit, loss and margin cannot be computed.
  If the question asks about profit, loss or margin, return exactly:
  SELECT 'Not available: this dataset has no cost data' AS answer
- Discount (disc) is not a loss. Never treat discount as loss or profit.
- Revenue = SUM(revenue). Never compute price*qty yourself.
- Number of orders = COUNT(DISTINCT order_id), not COUNT(*).
- Return ONE SQLite SELECT query only. No explanation, no markdown.
"""


def clean_sql(text):
    t = text.strip()
    t = t.replace("```sql", "").replace("```", "").strip()
    return t


def ask_llm(prompt):
    last_err = None
    for model in MODELS:
        for attempt in range(3):
            try:
                r = client.models.generate_content(model=model, contents=prompt)
                return clean_sql(r.text)
            except Exception as e:
                last_err = e
                if "503" in str(e) or "429" in str(e):
                    time.sleep(2 * (attempt + 1))   # wait 2s, 4s, 6s
                else:
                    raise
    raise last_err


def answer(question, conn):
    sample = pd.read_sql("SELECT * FROM sales_rev LIMIT 3", conn).to_string()
    prompt = f"{SCHEMA}\nSample rows:\n{sample}\n\nQuestion: {question}\nSQL:"
    sql = ask_llm(prompt)
    try:
        return sql, run_sql(conn, sql)
    except Exception as e:
        # one retry: send the error back to the model
        retry = f"{prompt}\n\nYour SQL:\n{sql}\nFailed with error: {e}\nFix it. SQL only:"
        sql = ask_llm(retry)
        return sql, run_sql(conn, sql)


if __name__ == "__main__":
    pd.options.display.float_format = "{:,.0f}".format
    conn = get_conn()
    while True:
        q = input("\nSawal (exit likhne par band): ").strip()
        if q.lower() == "exit":
            break
        try:
            sql, df = answer(q, conn)
            print("SQL:", sql)
            print(df)
        except Exception as e:
            print("Failed:", e)
    conn.close()