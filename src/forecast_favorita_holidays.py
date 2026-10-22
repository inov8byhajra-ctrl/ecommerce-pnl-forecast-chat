import os
import pandas as pd
from prophet import Prophet
from prophet.diagnostics import cross_validation

FILE = "data/raw/favorita.csv"
CACHE = "data/processed/favorita_daily_hol.csv"

# daily sales + share of rows flagged as holiday (national holiday = most stores flagged)
if os.path.exists(CACHE):
    d = pd.read_csv(CACHE, parse_dates=["ds"])
else:
    parts = []
    for c in pd.read_csv(FILE, usecols=["date", "sales", "is_holiday"],
                         parse_dates=["date"], chunksize=500_000):
        c["hol"] = c["is_holiday"].astype(str).str.lower().isin(["1", "1.0", "true"]).astype(int)
        g = c.groupby("date").agg(y=("sales", "sum"), hol=("hol", "sum"), n=("hol", "size"))
        parts.append(g)
    d = pd.concat(parts).groupby(level=0).sum().reset_index().rename(columns={"date": "ds"})
    d.to_csv(CACHE, index=False)

d["hol_share"] = d["hol"] / d["n"]
print("Days:", len(d), "| holiday days (share > 0.5):", (d["hol_share"] > 0.5).sum())

w = d.set_index("ds")["y"].resample("W").sum().reset_index().iloc[1:-1]

hol_days = d.loc[d["hol_share"] > 0.5, "ds"]
week_end = hol_days.map(lambda x: x + pd.Timedelta(days=6 - x.weekday()))
weeks = sorted(set(week_end) & set(w["ds"]))
events = pd.DataFrame({"holiday": "holiday_week", "ds": weeks})
print("Holiday weeks inside data:", len(events), "of", len(w))


def wape(a, p):
    return abs(a - p).sum() / a.sum() * 100


for name, ev in [("no holidays", None), ("with holidays", events)]:
    m = Prophet(holidays=ev, growth="linear", yearly_seasonality=False,
                weekly_seasonality=False, daily_seasonality=False)
    m.fit(w)
    cv = cross_validation(m, initial="365 days", period="28 days", horizon="56 days")
    cv["naive"] = cv["cutoff"].map(lambda c: w[w["ds"] <= c]["y"].tail(8).median())
    print(f"\n-- {name} | folds: {cv['cutoff'].nunique()} --")
    print("Prophet WAPE: %.1f%%" % wape(cv["y"], cv["yhat"]))
    print("Naive   WAPE: %.1f%%" % wape(cv["y"], cv["naive"]))