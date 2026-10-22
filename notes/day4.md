# Day 4 Notes: Forecasting

| Approach | Prophet error | Naive error |
|---|---|---|
| Monthly (26 points), raw | MAPE 291.4% | not measured |
| Daily, auto-detected sale events, 60-day hold-out | WAPE 83.0% (MAPE 135.4%) | WAPE 94.2% (MAPE 217.1%) |
| Weekly, 13-fold cross-validation, no events | WAPE 84.0% | WAPE 84.8% |
| Weekly, 13-fold CV, sale weeks found from the full data (earlier run) | WAPE 60.1% | WAPE 85.1% |
| Weekly, 13-fold CV, sale calendar decided in advance | WAPE 77.9% | WAPE 84.8% |

## Findings
- Sale events (Nov 2017: 304M, Feb/Mar/May 2018: 118-141M) drive most of the revenue swings.
  Without them the model is no better than a naive baseline (84.0% vs 84.8%).
- The 60.1% result is not valid: sale weeks were detected from the full data (leakage).
  With a sale calendar decided in advance the error is 77.9%, a small but real gain over naive.
- MAPE breaks on daily data with tiny days. WAPE (total error / total actual) is more stable.
- Only 26 months of history: yearly seasonality cannot be learned, and the same sale cannot be
  predicted from last year.
- Flat trend was needed, otherwise Prophet predicted a falling trend and zero revenue.
- Final weekly forecast (next 8 weeks) is the same value every week (about 8.6M) with a very
  wide interval (0 to about 35M): only an indicative baseline.

## Lessons
- Always compare against a naive baseline.
- Use cross-validation instead of one test period.
- Decide sale dates before testing, never find them in the same data you test on.
- For InsightFlow: show the error metric next to every forecast, and let the user mark sale dates.