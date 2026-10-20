import pandas as pd

df = pd.read_csv("data/raw/Pakistan Largest Ecommerce Dataset.csv", low_memory=False)

# print(df.shape)
# print(df.columns.tolist())
# print(df.head())
# df.info()
# print(df.isna().sum().sort_values(ascending=False))

# print(df.min(), df.max())
# print(df["status"].value_counts(dropna=False))
# print(df["category_name_1"].value_counts(dropna=False))