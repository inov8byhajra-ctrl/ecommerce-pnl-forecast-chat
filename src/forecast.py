import sqlite3
import pandas as pd
from prophet import Prophet

DB_FILE = "data/processed/ecommerce.db"
HOLDOUT = 60       # last 60 days kept for testing
SPIKE_MULT = 3     # a day above 3x its local median is a "sale event"
NAIVE_DAYS = 28    # naive baseline: median of last 28 days
HORIZON = 30       # days to forecast

conn = sqlite3.connect(DB_FILE)
d = pd.read_sql("""
    SELECT order_date AS ds, SUM(unit_price * quantity - discount) AS y
    FROM sales WHERE is_sale = 1
    GROUP BY order_date ORDER BY order_date
""", conn)
d["ds"] = pd.to_datetime(d["ds"])

# fill missing days so the series is continuous
full = pd.date_range(d["ds"].min(), d["ds"].max())
print("Missing days filled:", len(full) - len(d))
d = d.set_index("ds").reindex(full).interpolate().rename_axis("ds").reset_index()
print("Daily points:", len(d))

def find_sale_events(data):
    """Days far above their local median become Prophet 'holidays'."""
    med = data["y"].rolling(28, center=True, min_periods=7).median()
    spikes = data[data["y"] > SPIKE_MULT * med]
    return pd.DataFrame({"holiday": "sale_event", "ds": spikes["ds"],
                         "lower_window": 0, "upper_window": 0})

def new_model(events):
    return Prophet(holidays=events, growth="flat", yearly_seasonality=False,
                   weekly_seasonality=True, daily_seasonality=False)
    
# 1. Hold-out test (sale events found from training data only)
train, test = d[:-HOLDOUT], d[-HOLDOUT:]
events = find_sale_events(train)
print("Sale-event days found in training:", len(events))

model = new_model(events).fit(train)
pred = model.predict(test[["ds"]])["yhat"].clip(lower=0).values
actual = test["y"].values

naive = train["y"].tail(NAIVE_DAYS).median()

def wape(a, p):  # total error / total actual, not hurt by tiny days
    return abs(a - p).sum() / a.sum() * 100

print("\nProphet WAPE: %.1f%%" % wape(actual, pred))
print("Naive   WAPE: %.1f%%" % wape(actual, naive))
print("Prophet MAPE: %.1f%%" % ((abs(actual - pred) / actual).mean() * 100))
print("Naive   MAPE: %.1f%%" % ((abs(actual - naive) / actual).mean() * 100))
print("Test period actual: min %.0f, median %.0f, max %.0f" % (actual.min(), pd.Series(actual).median(), actual.max()))

# 2. Final model on all data, forecast next 30 days
events_all = find_sale_events(d)
final = new_model(events_all).fit(d)
future = final.make_future_dataframe(periods=HORIZON)
fc = final.predict(future)[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(HORIZON)
fc[["yhat", "yhat_lower", "yhat_upper"]] = fc[["yhat", "yhat_lower", "yhat_upper"]].clip(lower=0)
fc["ds"] = fc["ds"].dt.strftime("%Y-%m-%d")
print("\nNext 5 days:\n", fc.head(5).round(0))

fc.to_sql("forecast_daily", conn, if_exists="replace", index=False)
conn.close()