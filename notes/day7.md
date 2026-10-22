# Day 7: Cleanup and lessons

## Error handling test (7 bad inputs on build_pnl)
- Clear error: missing column, no date mapped, no price/amount mapped.
- Silent problem: text in price and all-bad dates both returned "OK | used 0 rows".
  The P&L would be empty without any warning.
- Fix identified, not applied: raise "No usable rows" when nothing is left after cleaning
  (a check on d.empty right after dropping bad dates).
- Negative price rows are kept by design (treated as adjustments).

## Large file
- Favorita, 3,000,888 rows, full P&L: 40 seconds.
- Reading the file needed chunks and a cached daily series.

## Forecast page
- Streamlit page shows weekly actual vs forecast, an 8-week table, a warning and both WAPE
  numbers. Pakistan data only. Forecast is flat (same value every week) and the interval is
  very wide, so it is only an indicative baseline.

## What I learned
- Data: order-level values (discount, grand_total) repeat on every item row. Flag bad rows
  instead of deleting them.
- P&L: with no cost column, profit is only an estimate and must be labelled.
- Forecast: error depends on the dataset (Favorita 12%, Pakistan 78%). A model is useful
  only if it beats a naive baseline. Prophet did not on Favorita.
- Text-to-SQL: the model answers wrong or unanswerable questions with confidence. Schema
  rules and a view with the business logic fix most of it. Check meaning, not only numbers.
- Generality: code tied to column names or table names breaks on a new dataset.

## What changes in InsightFlow
- Read only from business_data; mapping, sale statuses, cost mode and event calendar come
  from the user.
- Turn features off with a clear message instead of crashing; fail clearly on empty input.
- Show a validation report after every upload.
- Show naive vs model WAPE next to every forecast.
- Keep Superstore, Pakistan and Favorita as regression test datasets.

## Not done
- 10-question chat test (test_questions.py) not run.
- "No usable rows" fix not applied to pnl.py.
- Holiday and Favorita results are not shown in the Streamlit forecast page.