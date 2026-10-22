import pandas as pd

RAW_FILE = "data/raw/Pakistan Largest Ecommerce Dataset.csv"
SALE_STATUSES = ["complete", "received", "cod", "paid"]

df = pd.read_csv(RAW_FILE, low_memory=False)
df.columns = df.columns.str.strip()
df = df.dropna(subset=["item_id"])
df = df.replace("\\N", pd.NA)
df = df.dropna(subset=["status"])

gt = pd.to_numeric(df["grand_total"], errors="coerce")
bad = df[gt <= 0]

print("grand_total <= 0 rows:", len(bad))
print("\nStatus breakdown:")
print(bad["status"].value_counts())
print("\nShare that are real-sale statuses: %.1f%%" %
      (bad["status"].isin(SALE_STATUSES).mean() * 100))
print("\nSample:")
print(bad[["increment_id", "status", "price", "qty_ordered",
           "discount_amount", "grand_total"]].head(10))