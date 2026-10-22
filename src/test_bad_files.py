import pandas as pd
from pnl import build_pnl

good = pd.DataFrame({"d": ["2024-01-01", "2024-01-02"], "p": [100, 200], "q": [1, 2]})
m = {"date": "d", "price": "p", "quantity": "q"}

cases = {
    "missing column":  (good, {**m, "price": "nope"}),
    "no date mapped":  (good, {"price": "p"}),
    "no price/amount": (good, {"date": "d"}),
    "empty file":      (good.iloc[0:0], m),
    "text in price":   (good.assign(p=["abc", "xyz"]), m),
    "all bad dates":   (good.assign(d=["x", "y"]), m),
    "negative price":  (good.assign(p=[-100, 200]), m),
}
for name, (df, mp) in cases.items():
    try:
        r = build_pnl(df, mp, cost_mode="none")
        v = r["validation"]
        print(f"{name}: OK | used {v['rows_used']}, dropped {v['rows_dropped_bad_date_or_amount']}")
    except Exception as e:
        print(f"{name}: ERROR -> {e}")