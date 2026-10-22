# Day 3: P&L engine

## What I built
- pnl.py: a P&L engine that works from a column mapping, so it is not tied to one dataset.
  Required: date + (amount or price). Optional: quantity, discount, cost, category, order_id.
- Outputs: monthly P&L, category P&L, adjustments (negative revenue rows), validation dict,
  total revenue.
- pnl_page.py (Streamlit): monthly and category tables with bar charts.

## Cost modes
- column: real unit cost from the file (used later on Favorita).
- pct: cost = a given % of gross sales, labelled ESTIMATED.
- none: no cost, no profit or margin.
- demo: random category-wise cost ratio between 70% and 85% (seed 42). Test data only.
- The Pakistan dataset has no cost column, so profit here is SIMULATED (demo mode).
  The Streamlit page shows a warning for this.

## Revenue rules
- Only rows with is_sale = 1 and is_outlier = 0 are used.
- Revenue = price x quantity - discount.
- Discount is an order-level value, so it is counted once per order (first item row);
  with order_id mapped, the other rows get discount 0.
- check_discount.py confirmed the rule: against grand_total (counted once), the gap was
  +3.6% with "discount once" and -9.6% with "discount summed over rows".
  The remaining 3.6% is probably shipping or other charges (not verified).
- Single-row orders: gap only 0.2%.

## Results (Pakistan dataset, 306,661 rows used)
- Total revenue: 1,202,706,887.
- Biggest month: 2017-11 (revenue 303.9M, sale month). Normal months are about 15-30M.
- Biggest category: Mobiles & Tablets (540.4M after discount), then Appliances (205.0M) and
  Entertainment (181.9M).
- Negative revenue rows: 1,060 rows, total -2,075,736. Kept in the P&L by default
  (negative_rows="keep"), or moved to "adjustments" with negative_rows="separate".
- Margins (9% to 26% by category) come from random cost, so they are NOT real profit.

## What went wrong
- The comparison "our revenue total vs sum of grand_total" is not valid: grand_total repeats
  on every item row of an order, so its sum is inflated (1.59B vs our 1.20B).
  Compare with grand_total counted once per order instead.
- check_discount.py first failed because the gap() function was defined after its first use.

## Lessons
- With no cost column, profit can only be an estimate and must be labelled.
- Check which values are order-level (discount, grand_total) before summing anything.
- Return a validation dict with every P&L (rows used, rows dropped, negative revenue,
  cost note) so a user can see what was assumed.