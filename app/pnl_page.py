import sqlite3
import pandas as pd
import streamlit as st

conn = sqlite3.connect("data/processed/ecommerce.db")
monthly = pd.read_sql("SELECT * FROM monthly_pnl", conn)
category = pd.read_sql("SELECT * FROM category_pnl", conn)
conn.close()

st.title("Profit & Loss")

# This dataset has no real cost column, so profit is simulated.
st.warning("SIMULATED cost (demo only). Gross profit and margin are NOT real profit. "
           "Revenue and discount figures are real.")

st.subheader("Monthly P&L")
st.dataframe(monthly)
st.bar_chart(monthly.set_index("year_month")[["revenue", "gross_profit"]])

st.subheader("Category P&L")
st.dataframe(category)
st.bar_chart(category.set_index("category")["gross_profit"])