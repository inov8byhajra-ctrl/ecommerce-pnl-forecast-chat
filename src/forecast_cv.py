import sqlite3
import pandas as pd
from prophet import Prophet
from prophet.diagnostics import cross_validation
from revenue_sql import DAILY_REVENUE_SQL

DB_FILE = "data/processed/ecommerce.db"
conn = sqlite3.connect(DB_FILE)
d = pd.read_sql(DAILY_REVENUE_SQL, conn)
d["ds"] = pd.to_datetime(d["ds"])

# weekly revenue (weeks end on Sunday); drop the partial first and last week
w = d.set_index("ds")["y"].resample("W").sum().reset_index().iloc[1:-1]
print("Weekly points:", len(w), "|", w["ds"].min().date(), "to", w["ds"].max().date())

# ---- KNOWN sale calendar (decided in advance, NOT found from the data) ----
# Verify these against the real spikes in your data and edit if needed.
SALE_CALENDAR = [
    # 11.11
    "2016-11-11", "2017-11-11",
    # Black Friday
    "2016-11-25", "2017-11-24",
    # 12.12
    "2016-12-12", "2017-12-12",
    # 14 August (Independence Day sale)
    "2016-08-14", "2017-08-14", "2018-08-14",
    # Ramadan start
    "2016-06-06", "2017-05-27", "2018-05-16",
]

def to_week_end(date):
    d0 = pd.Timestamp(date)
    return d0 + pd.Timedelta(days=6 - d0.weekday())  # that week's Sunday

weeks = sorted({to_week_end(x) for x in SALE_CALENDAR})
weeks = [x for x in weeks if x in set(w["ds"])]
events = pd.DataFrame({"holiday": "sale_event", "ds": weeks})
print("Calendar sale weeks inside data:", len(events))

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