# Day 1 Notes: Data Quality Issues and Fixes

**Dataset:** Pakistan Largest Ecommerce Dataset (1,048,575 rows x 26 columns raw)
**Script:** `src/clean.py`

## Issues and fixes

| # | Issue | How it was found / why it happened | Fix | Status |
|---|---|---|---|---|
| 1 | ~464,051 completely empty rows | File was saved from Excel, which has a max of 1,048,575 rows. Real data is only 584,524 rows | `df.dropna(subset=["item_id"])` | Fixed |
| 2 | 5 fully empty columns (`Unnamed: 21` to `Unnamed: 25`) | 100% null in `df.info()` | Dropped the columns | Fixed |
| 3 | Column name with extra spaces (` MV `) | Excel formatting leftover | `df.columns.str.strip()` | Fixed |
| 4 | Literal `\N` text used instead of null (4 in `status`, 7,850 in `category_name_1`) | Typical of a database export | `df.replace("\\N", pd.NA)` | Fixed |
| 5 | `created_at` stored as text, not date | CSV files read everything as text | `pd.to_datetime(format="%m/%d/%Y", errors="coerce")` | Fixed (0 parse failures) |
| 6 | `BI Status` contains `#REF!` | Excel formula error | Column is unreliable, will not be used | Pending |
| 7 | Derived columns (`Year`, `Month`, `M-Y`, `FY`, `MV`, `Working Date`) are inconsistent. Example: `created_at` = 9/9/2017 but `Year` = 2018, `Month` = 12 | Compared derived columns with `created_at` | Rebuild them from `created_at` | Pending |
| 8 | Negative `grand_total` and `price` = 0 | Example row: grand_total -1594, price 0 | Decide before Day 3 | Pending |
| 9 | Outlier: qty 1000 with grand_total 17.9 million | Likely data entry error | Decide before Day 3 | Pending |
| 10 | Many `status` values (complete, canceled, refund, cod, paid, fraud, ...) and not all are real sales | `value_counts()` on `status` | Decide which statuses count as revenue before Day 3 | Pending |
| 11 | Missing values in real rows: 19 in `status`, ~164 in `category_name_1` | Remaining nulls after cleaning | Decide before Day 3 | Pending |

## Answers to the three Day 1 questions

1. **Rows and date range:** 584,524 real rows. Date range: 2016-07-01 to 2018-08-28.
2. **Status values:** complete, canceled, received, order_refunded, refund, cod, paid, closed, payment_review, pending, processing, holded, fraud, pending_paypal, exchange (plus 19 nulls).
3. **Most null columns:** `sales_commission_code`, `category_name_1`, `sku`.

## Key takeaways

- CSVs saved from Excel can contain empty rows, messy column names and formula errors.
- Always inspect with `df.info()` and `value_counts()` before cleaning.
- Never trust pre-computed columns (`Year`, `Month`, `FY`). Derive them from the raw date.