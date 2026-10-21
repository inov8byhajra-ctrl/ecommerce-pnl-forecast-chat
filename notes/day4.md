# Day 4 Notes: Forecasting

| Approach | Prophet error | Naive error |
|---|---|---|
| Monthly (26 points), raw | MAPE 291.4% | not measured |
| Daily, auto-detected sale events, 60-day hold-out | WAPE 82.6% (MAPE 133%) | WAPE 94.4% (MAPE 217%) |
| Weekly, 13-fold cross-validation, no events | WAPE 84.7% | WAPE 85.1% |
| Weekly, 13-fold cross-validation, known sale weeks | WAPE 60.1% | WAPE 85.1% |

## Findings
- Sale events (Nov 2017: 302M, Feb/Mar/May 2018: 112-139M) drive most of the revenue swings. Without them the model is no better than a naive baseline.
- With a known sale calendar the error drops from about 85% to about 60%. Caveat: sale weeks were detected from the full data, so this is optimistic. It is only valid if sale dates are known in advance.
- MAPE breaks on daily data with tiny days. WAPE (total error / total actual) is more stable.
- Only 26 months of history: yearly seasonality cannot be learned, and the same sale cannot be predicted from last year.
- Flat trend was needed, otherwise Prophet predicted a falling trend and zero revenue.

## Lessons
- Always compare against a naive baseline.
- Use cross-validation instead of one test period.
- For InsightFlow: show the error metric next to every forecast, and let the user mark sale dates.