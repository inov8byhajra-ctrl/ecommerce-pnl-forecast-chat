import sqlite3
import pandas as pd
import streamlit as st

conn = sqlite3.connect("data/processed/ecommerce.db")
monthly = pd.read_sql("SELECT * FROM monthly_pnl", conn)
category = pd.read_sql("SELECT * FROM category_pnl", conn)

st.title("Profit & Loss")

st.subheader("Monthly P&L")
st.dataframe(monthly)
st.bar_chart(monthly.set_index("year_month")[["revenue", "gross_profit"]])

st.subheader("Category P&L")
st.dataframe(category)
st.bar_chart(category.set_index("category")["gross_profit"])