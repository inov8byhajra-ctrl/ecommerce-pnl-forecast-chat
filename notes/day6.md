# Day 6: Second dataset (Favorita)

## Dataset
- data/raw/favorita.csv is a pre-processed version of the Kaggle Favorita data, not the
  original train.csv. 3,000,888 rows, 2013-01-01 to 2017-08-15.
- Columns include: date, store_nbr, family, sales, onpromotion, city, state, store_type,
  is_holiday, holiday_name, sim_unit_price, sim_unit_cost, sim_revenue, sim_cogs.
- The sim_* money columns are simulated. There are no orders and no customers.

## 1. Forecast (weekly, 240 weeks, 45 cross-validation folds)
| Dataset / setup | Prophet WAPE | Naive WAPE |
|---|---|---|
| Pakistan, weekly + sale calendar | 77.9% | 84.8% |
| Favorita, weekly | 12.6% | 11.6% |
| Favorita, weekly + yearly seasonality | 12.9% | 11.6% |
| Favorita, weekly + holidays (49 of 240 weeks) | 12.5% | 11.6% |

- Forecast error depends mostly on the dataset: Favorita is smooth (about 12%), Pakistan is
  spike-driven (78%).
- On Favorita, Prophet did not beat the naive baseline (median of the last 8 weeks).
  Yearly seasonality and holidays did not change that.
- Lesson: always compare against a naive baseline. A model that runs is not the same as a
  model that helps.

## 2. P&L engine on Favorita (cost_mode="column")
- Mapping: price=sim_unit_price, quantity=sales, cost=sim_unit_cost, category=family.
- COGS matched the file: 1,834,255,279 vs 1,834,255,276 (rounding).
- Revenue differed by about 3%: 2,442.7M (price x qty) vs 2,371.6M (file sim_revenue).
  Cause not verified (possibly a promotion discount in the file).
- pnl.py ran on 3,000,888 rows in about 40 seconds without code changes.

## 3. Text-to-SQL chat on Favorita
- Needed a separate SQLite DB (favorita.db), a new sales_rev view and a new schema prompt.
  ask_llm() was reused as is.
- Total revenue = 2,371,598,615, equal to the file's sim_revenue total.
- "Which category has the highest revenue" -> GROCERY I.
- "Total revenue per year" worked (2013: 348.5M ... 2016: 608.9M; 2017 is partial).
- "How many customers" -> "Not available" (schema rule worked).

## What broke
- Expected train.csv with unit_sales and item_nbr; the file had sales and family.
- revenue_sql.py (reads the "sales" table) and the sales_rev view for Pakistan only work
  for the Pakistan dataset.
- SALE_CALENDAR (11.11, 14 August) is Pakistan-specific and not valid for Ecuador.
- The 3M-row file needed chunked reading and a cached daily series.

## For InsightFlow
- Read only from the business_data table, never from raw files or dataset-specific tables.
- Column mapping, sale statuses, cost mode and event calendar come from the user.
- If a feature cannot work (no cost, no order_id, too little history), turn it off with a
  clear message instead of crashing.
- Show naive vs model WAPE next to every forecast; if the model is not better, say so.
- In the mapping step, ask whether the amount column is money or quantity.
- Keep Superstore, Pakistan and Favorita as regression test datasets.