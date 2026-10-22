import os
import pandas as pd
from prophet import Prophet
from prophet.diagnostics import cross_validation

FILE = "data/raw/favorita.csv"
CACHE = "data/processed/favorita_daily.csv"

# 1. Daily total sales (all stores). Saved once, so the big file is read only once.
if os.path.exists(CACHE):
    d = pd.read_csv(CACHE, parse_dates=["ds"])
else:
    parts = []
    for chunk in pd.read_csv(FILE, usecols=["date", "sales"],
                             parse_dates=["date"], chunksize=500_000):
        parts.append(chunk.groupby("date")["sales"].sum())
    d = pd.concat(parts).groupby(level=0).sum().reset_index()
    d.columns = ["ds", "y"]
    d.to_csv(CACHE, index=False)

print("Days:", len(d), "|", d["ds"].min().date(), "to", d["ds"].max().date())

# 2. Weekly series, drop partial first and last week
w = d.set_index("ds")["y"].resample("W").sum().reset_index().iloc[1:-1]
print("Weekly points:", len(w))


def wape(a, p):
    return abs(a - p).sum() / a.sum() * 100


# 3. Cross-validation: Prophet vs naive
for name, yearly in [("no yearly seasonality", False), ("yearly seasonality", True)]:
    m = Prophet(growth="linear", yearly_seasonality=yearly,
                weekly_seasonality=False, daily_seasonality=False)
    m.fit(w)
    cv = cross_validation(m, initial="365 days", period="28 days", horizon="56 days")
    cv["naive"] = cv["cutoff"].map(lambda c: w[w["ds"] <= c]["y"].tail(8).median())
    print(f"\n-- {name} | folds: {cv['cutoff'].nunique()} --")
    print("Prophet WAPE: %.1f%%" % wape(cv["y"], cv["yhat"]))
    print("Naive   WAPE: %.1f%%" % wape(cv["y"], cv["naive"]))