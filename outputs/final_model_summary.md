# Final Model Summary
## Bengaluru Parking Hotspot Forecasting

### Primary Fold Results (Feb & Mar)

| Model               | Recall@20 | Recall@50 | Spearman ρ | MAE (top-200) |
|---------------------|-----------|-----------|------------|---------------|
| global_mean         | 0.025 | — | — | — |
| lag1_persistence    | 0.700 | 0.800 | 0.720 | 90 |
| rolling_mean_3m     | 0.725 | 0.770 | 0.737 | 78 |
| rule_score          | 0.725 | 0.800 | 0.736 | 78 |
| lightgbm_poisson    | 0.700 | 0.780 | 0.697 | 110 |

### Decision: BASELINE_WINS

LightGBM does NOT beat baselines. Use rolling_mean_3m + rule score.

### Top-5 Features by Importance
- rolling_mean_3m
- rolling_std_3m
- count_lag1
- volatility_score
- count_lag3

### Known Limitations
- Only 2 primary evaluation folds (Feb, Mar). Statistical confidence is thin.
- Dataset records enforcement activity, not actual parking violations.
- April fold excluded from primary metrics (truncated to 8 days).
- Lag-1 persistence is a strong baseline (r=0.932). ML improvement is incremental.
- Near-duplicates excluded from targets but may still affect feature computation.
