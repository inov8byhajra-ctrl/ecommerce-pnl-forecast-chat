# Day 2 Notes: Cleaning Decisions

**Script:** `src/clean.py` | **Output:** `data/processed/ecommerce.db`, table `sales`

## Fixes from Day 1 (pending items resolved)

| # | Issue | Decision | Status |
|---|---|---|---|
| 6 | `BI Status` has `#REF!` errors | Column dropped, not used | Fixed |
| 7 | Derived columns (`Year`, `Month`, `FY`, `MV`) are inconsistent | Dropped. `year`, `month`, `year_month` rebuilt from `order_date` | Fixed |
| 8 | Negative `grand_total`, `price` = 0 | Rows dropped (counts printed by script: see output) | Fixed |
| 9 | Outlier: quantity 1000, grand_total 17.9M | Rows with quantity > 100 dropped (`MAX_QTY` setting) | Fixed |
| 10 | Many status values, not all are sales | Added `is_sale` flag: 1 for complete, received, cod, paid. Rows kept | Fixed |
| 11 | Null `status` (19) and `category` (~8,000 incl. `\N`) | Null status rows dropped. Null category filled with "Unknown" | Fixed |
| 12 | One row with price x qty > 500,000 (Entertainment, 2017-04-20) | Dropped (`MAX_ROW_VALUE` setting) | Fixed |
| 13 | Duplicate rows (same order_id, sku, price, quantity, status) | `drop_duplicates` | Fixed |

## Other changes
- Kept 12 needed columns and renamed them (e.g. `created_at` -> `order_date`, `price` -> `unit_price`, `Customer ID` -> `customer_id`).
- Fixed data types (`item_id`, `quantity` to int, `customer_id` to nullable int).
- Saved clean data to SQLite table `sales`.

## Final numbers
- Rows before: (paste "Raw shape" here)
- Rows after: (paste "Final shape" here)
- Real sales rows: (paste here)

## Lessons
- Keep questionable rows with a flag instead of deleting them, so decisions can be changed later.
- Put settings (thresholds, status lists) at the top of the script.
- Print counts at each cleaning step so every decision is backed by numbers.

