import sqlite3
import pandas as pd

# ---------- Settings (change here if needed) ----------
RAW_FILE = "data/raw/Pakistan Largest Ecommerce Dataset.csv"
DB_FILE = "data/processed/ecommerce.db"
MAX_QTY = 100  # quantity above this is treated as a data-entry error
SALE_STATUSES = ["complete", "received", "cod", "paid"]  # statuses counted as real sales

# old column name -> new column name
COLUMN_MAP = {
    "item_id": "item_id",
    "increment_id": "order_id",
    "created_at": "order_date",
    "sku": "sku",
    "qty_ordered": "quantity",
    "price": "unit_price",
    "discount_amount": "discount",
    "grand_total": "grand_total",
    "category_name_1": "category",
    "status": "status",
    "payment_method": "payment_method",
    "Customer ID": "customer_id",
}

# ---------- 1. Load ----------
df = pd.read_csv(RAW_FILE, low_memory=False)
print("Raw shape:", df.shape)

# ---------- 2. Basic cleaning (from before) ----------
df.columns = df.columns.str.strip()
df = df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")])
df = df.dropna(subset=["item_id"])
df = df.replace("\\N", pd.NA)
df["created_at"] = pd.to_datetime(df["created_at"], format="%m/%d/%Y", errors="coerce")

# ---------- 3. Keep only needed columns and rename ----------
df = df[list(COLUMN_MAP.keys())].rename(columns=COLUMN_MAP)

# ---------- 4. Rebuild year/month from order_date ----------
df["year"] = df["order_date"].dt.year
df["month"] = df["order_date"].dt.month
df["year_month"] = df["order_date"].dt.strftime("%Y-%m")

# ---------- 5. Missing values ----------
before = len(df)
df = df.dropna(subset=["status"])
print("Dropped (null status):", before - len(df))

df["category"] = df["category"].fillna("Unknown")

# ---------- 6. Bad numbers ----------
print("price <= 0:", (df["unit_price"] <= 0).sum())
print("grand_total <= 0:", (df["grand_total"] <= 0).sum())
print("quantity <= 0:", (df["quantity"] <= 0).sum())
print(f"quantity > {MAX_QTY}:", (df["quantity"] > MAX_QTY).sum())
MAX_ROW_VALUE = 500000  # unit_price x quantity above this is treated as an outlier

print(f"price x qty > {MAX_ROW_VALUE}:", (df["unit_price"] * df["quantity"] > MAX_ROW_VALUE).sum())

bad = (
    (df["unit_price"] <= 0)
    | (df["grand_total"] <= 0)
    | (df["quantity"] <= 0)
    | (df["quantity"] > MAX_QTY)
    | (df["unit_price"] * df["quantity"] > MAX_ROW_VALUE)
)
print("Dropped (bad numbers, total):", bad.sum())
df = df[~bad]
before = len(df)
df = df.drop_duplicates(subset=["order_id", "sku", "unit_price", "quantity", "status"])
print("Dropped (duplicates):", before - len(df))

# ---------- 7. Flag real sales (rows are kept, not deleted) ----------
df["is_sale"] = df["status"].isin(SALE_STATUSES).astype(int)

# ---------- 8. Fix data types ----------
df["item_id"] = df["item_id"].astype("int64")
df["customer_id"] = df["customer_id"].astype("Int64")
df["quantity"] = df["quantity"].astype("int64")
df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")  # text date for SQLite

# ---------- 9. Save to SQLite ----------
conn = sqlite3.connect(DB_FILE)
df.to_sql("sales", conn, if_exists="replace", index=False)

# ---------- 10. Verify ----------
print("\nFinal shape:", df.shape)
print("Rows in SQLite:", pd.read_sql("SELECT COUNT(*) AS n FROM sales", conn)["n"][0])
print("Real sales rows:", df["is_sale"].sum())
print(df["status"].value_counts())
print(df[["unit_price", "quantity", "grand_total"]].describe())
conn.close()