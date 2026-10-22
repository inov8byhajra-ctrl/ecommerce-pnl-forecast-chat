"""P&L engine.

Use as a library (InsightFlow):
    from pnl import build_pnl
    result = build_pnl(df, mapping, cost_mode="auto", cost_pct=None)

mapping = {"date": "Order Date", "price": "Unit Price", "quantity": "Qty",
           "discount": "Discount", "cost": "Unit Cost", "category": "Category"}
- Required: "date" + ("amount" OR "price")
- Optional: "quantity" (default 1), "discount" (default 0),
            "cost" (UNIT cost), "category" (default "All")

cost_mode:
- "auto"   : cost column if mapped, else cost_pct if given, else no profit
- "column" : use the real cost column
- "pct"    : COGS = cost_pct% of gross sales (labelled as an estimate)
- "none"   : no COGS / profit, only revenue and discount
- "demo"   : random category-wise cost ratios (for test datasets ONLY)
"""
import sqlite3
import numpy as np
import pandas as pd

DB_FILE = "data/processed/ecommerce.db"
SEED = 42


def _prepare(df, mapping):
    m = mapping
    if "date" not in m:
        raise ValueError("Date column is required.")
    if "amount" not in m and "price" not in m:
        raise ValueError("Need an 'amount' column or a 'price' column.")
    missing = [c for c in m.values() if c not in df.columns]
    if missing:
        raise ValueError(f"Columns not found in file: {missing}")

    d = pd.DataFrame(index=df.index)
    d["date"] = pd.to_datetime(df[m["date"]], errors="coerce")
    d["quantity"] = pd.to_numeric(df[m["quantity"]], errors="coerce") if "quantity" in m else 1.0
    if "amount" in m:
        d["gross"] = pd.to_numeric(df[m["amount"]], errors="coerce")
    else:
        d["gross"] = pd.to_numeric(df[m["price"]], errors="coerce") * d["quantity"]
    d["discount"] = pd.to_numeric(df[m["discount"]], errors="coerce").fillna(0) if "discount" in m else 0.0
    if "order_id" in m:
        # discount is an ORDER-level value repeated on every item row:
        # keep it on the first row of each order only, so it is counted once
        d["order_id"] = df[m["order_id"]]
        first = ~d.duplicated("order_id")
        d["discount"] = d["discount"].where(first, 0)
    d["category"] = df[m["category"]].fillna("Unknown").astype(str) if "category" in m else "All"
    d["unit_cost"] = pd.to_numeric(df[m["cost"]], errors="coerce") if "cost" in m else np.nan
    d["revenue"] = d["gross"] - d["discount"]
    return d


def _add_cogs(d, cost_mode, cost_pct, has_cost_col, seed):
    """Returns (data, note). Adds 'cogs' column unless there is no cost info."""
    if cost_mode == "auto":
        if has_cost_col:
            cost_mode = "column"
        elif cost_pct is not None:
            cost_mode = "pct"
        else:
            cost_mode = "none"

    if cost_mode == "column":
        if not has_cost_col:
            raise ValueError("cost_mode='column' but no cost column is mapped.")
        d["cogs"] = d["unit_cost"] * d["quantity"]
        return d, "Real cost from the uploaded file."
    if cost_mode == "pct":
        if cost_pct is None:
            raise ValueError("cost_mode='pct' needs cost_pct (e.g. 75).")
        d["cogs"] = d["gross"] * cost_pct / 100
        return d, f"ESTIMATED: cost assumed at {cost_pct}% of gross sales (user assumption)."
    if cost_mode == "demo":
        rng = np.random.default_rng(seed)
        cats = sorted(d["category"].unique())
        ratios = dict(zip(cats, rng.uniform(0.70, 0.85, len(cats))))
        d["cogs"] = d["gross"] * d["category"].map(ratios)
        return d, "SIMULATED cost (demo only). Not real profit."
    if cost_mode == "none":
        return d, "No cost data: profit and margin are not shown."
    raise ValueError(f"Unknown cost_mode: {cost_mode}")


def _make_pnl(data, by):
    cols = ["gross", "discount", "revenue"] + (["cogs", "gross_profit"] if "cogs" in data else [])
    pnl = data.groupby(by)[cols].sum()
    if "gross_profit" in pnl:
        pnl["margin_pct"] = (pnl["gross_profit"] / pnl["revenue"] * 100).round(1)
    return pnl.round(0).reset_index()


def build_pnl(df, mapping, cost_mode="auto", cost_pct=None,
              negative_rows="keep", seed=SEED):
    """negative_rows: "keep" = leave rows with revenue < 0 inside the P&L,
                      "separate" = move them to result["adjustments"]."""
    d = _prepare(df, mapping)
    rows_in = len(d)

    bad_date = d["date"].isna() | d["gross"].isna()
    d = d[~bad_date].copy()
    if d.empty:
        raise ValueError("No usable rows: check the date and amount/price columns.")

    d, cost_note = _add_cogs(d, cost_mode, cost_pct, "cost" in mapping, seed)

    rows_missing_cost = 0
    if "cogs" in d and cost_mode in ("auto", "column") and "cost" in mapping:
        rows_missing_cost = int(d["cogs"].isna().sum())
        d["cogs"] = d["cogs"].fillna(0)

    if "cogs" in d:
        d["gross_profit"] = d["revenue"] - d["cogs"]

    negative = d["revenue"] < 0
    adjustments = d[negative].copy()
    if negative_rows == "separate":
        d = d[~negative].copy()

    d["year_month"] = d["date"].dt.strftime("%Y-%m")

    validation = {
        "rows_in": rows_in,
        "rows_dropped_bad_date_or_amount": int(bad_date.sum()),
        "rows_used": len(d),
        "negative_revenue_rows": int(negative.sum()),
        "negative_revenue_amount": round(float(adjustments["revenue"].sum())),
        "negative_rows_handling": negative_rows,
        "rows_missing_cost": rows_missing_cost,
        "cost_note": cost_note,
    }
    return {
        "monthly": _make_pnl(d, "year_month"),
        "by_category": _make_pnl(d, "category").sort_values("revenue", ascending=False),
        "adjustments": adjustments,
        "validation": validation,
        "total_revenue": round(float(d["revenue"].sum())),
    }


# ---------- CLI: run on the Pakistan e-commerce DB ----------
if __name__ == "__main__":
    conn = sqlite3.connect(DB_FILE)
    sales = pd.read_sql("SELECT * FROM sales WHERE is_sale = 1 AND is_outlier = 0", conn)

    mapping = {"date": "order_date", "price": "unit_price", "quantity": "quantity",
               "discount": "discount", "category": "category", "order_id": "order_id"}
    result = build_pnl(sales, mapping, cost_mode="demo")  # no real cost in this dataset

    print("Validation:")
    for k, v in result["validation"].items():
        print(f"  {k}: {v}")
    print("\nMonthly P&L:\n", result["monthly"])
    print("\nCategory P&L:\n", result["by_category"])
    print("\nOur revenue total:", result["total_revenue"])


    result["monthly"].to_sql("monthly_pnl", conn, if_exists="replace", index=False)
    result["by_category"].to_sql("category_pnl", conn, if_exists="replace", index=False)
    conn.close()