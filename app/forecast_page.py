import sqlite3
import pandas as pd
import streamlit as st

conn = sqlite3.connect("data/processed/ecommerce.db")
actual = pd.read_sql("SELECT * FROM weekly_actual", conn)
fc = pd.read_sql("SELECT * FROM forecast_weekly", conn)
conn.close()

st.title("Revenue Forecast (weekly)")
st.warning("Sale-driven data, WAPE ~78%, sirf indicative baseline. "
           "Forecast numbers par bharosa mat karo.")

col1, col2 = st.columns(2)
col1.metric("Prophet WAPE (cross-validation)", "77.9%")
col2.metric("Naive WAPE", "84.8%")

actual = actual.rename(columns={"y": "actual"}).set_index("ds")
fc = fc.set_index("ds")
chart = actual.join(fc, how="outer")[["actual", "yhat", "yhat_lower", "yhat_upper"]]

st.subheader("Actual vs forecast")
st.line_chart(chart)

st.subheader("Next weeks forecast")
st.dataframe(fc.tail(8).round(0))