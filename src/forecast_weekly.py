import sqlite3
import pandas as pd
from prophet import Prophet
from revenue_sql import DAILY_REVENUE_SQL

DB_FILE = "data/processed/ecommerce.db"
HORIZON_WEEKS = 8

SALE_CALENDAR = [
    "2016-11-11", "2017-11-11",
    "2016-11-25", "2017-11-24",
    "2016-12-12", "2017-12-12",
    "2016-08-14", "2017-08-14", "2018-08-14",
    "2016-06-06", "2017-05-27", "2018-05-16",
]

def to_week_end(date):
    d0 = pd.Timestamp(date)
    return d0 + pd.Timedelta(days=6 - d0.weekday())

conn = sqlite3.connect(DB_FILE)
d = pd.read_sql(DAILY_REVENUE_SQL, conn)
d["ds"] = pd.to_datetime(d["ds"])

# weekly revenue, drop partial first and last week
w = d.set_index("ds")["y"].resample("W").sum().reset_index().iloc[1:-1]

weeks = sorted({to_week_end(x) for x in SALE_CALENDAR})
events = pd.DataFrame({"holiday": "sale_event",
                       "ds": [x for x in weeks if x in set(w["ds"])]})

model = Prophet(holidays=events, growth="flat", yearly_seasonality=False,
                weekly_seasonality=False, daily_seasonality=False)
model.fit(w)

future = model.make_future_dataframe(periods=HORIZON_WEEKS, freq="W")
fc = model.predict(future)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
fc[["yhat", "yhat_lower", "yhat_upper"]] = fc[["yhat", "yhat_lower", "yhat_upper"]].clip(lower=0)
fc["ds"] = fc["ds"].dt.strftime("%Y-%m-%d")

w_out = w.copy()
w_out["ds"] = w_out["ds"].dt.strftime("%Y-%m-%d")

w_out.to_sql("weekly_actual", conn, if_exists="replace", index=False)
fc.to_sql("forecast_weekly", conn, if_exists="replace", index=False)
conn.close()
print("Saved weekly_actual and forecast_weekly. Forecast rows:", len(fc))