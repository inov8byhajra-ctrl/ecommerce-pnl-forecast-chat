import sqlite3
import pandas as pd
from prophet import Prophet
from prophet.diagnostics import cross_validation

DB_FILE = "data/processed/ecommerce.db"
conn = sqlite3.connect(DB_FILE)
d = pd.read_sql("""
    SELECT order_date AS ds, SUM(unit_price * quantity - discount) AS y
    FROM sales WHERE is_sale = 1 GROUP BY order_date
""", conn)
d["ds"] = pd.to_datetime(d["ds"])

# weekly revenue (weeks end on Sunday); drop the partial first and last week
w = d.set_index("ds")["y"].resample("W").sum().reset_index().iloc[1:-1]
print("Weekly points:", len(w))

# weeks far above their local median = sale-event weeks
med = w["y"].rolling(9, center=True, min_periods=4).median()
spikes = w[w["y"] > 2 * med]
events = pd.DataFrame({"holiday": "sale_event", "ds": spikes["ds"]})
print("Sale-event weeks:", len(events))

def wape(a, p):
    return abs(a - p).sum() / a.sum() * 100

for name, ev in [("no events", None), ("known sale calendar", events)]:
    model = Prophet(holidays=ev, growth="flat", yearly_seasonality=False,
                    weekly_seasonality=False, daily_seasonality=False)
    model.fit(w)
    cv = cross_validation(model, initial="365 days", period="28 days", horizon="56 days")
    cv["naive"] = cv["cutoff"].map(lambda c: w[w["ds"] <= c]["y"].tail(8).median())
    print("\n--", name, "| folds:", cv["cutoff"].nunique(), "--")
    print("Prophet WAPE: %.1f%%" % wape(cv["y"], cv["yhat"]))
    print("Naive   WAPE: %.1f%%" % wape(cv["y"], cv["naive"]))

conn.close()