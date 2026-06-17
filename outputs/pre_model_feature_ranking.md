# Pre-Model Feature Ranking
## Feature Prioritization Before Training

---

## Tier A — Almost Certainly Useful

These features have direct empirical support from the forecastability analysis. Include all of them.

| Feature | Group | Evidence |
|---|---|---|
| `count_lag1` | Lag/Count | r=0.932 avg; strongest single predictor |
| `count_lag2` | Lag/Count | r=0.910 avg; confirms momentum beyond lag-1 |
| `count_lag3` | Lag/Count | r~0.87; seasonality anchor |
| `rolling_mean_3m` | Lag/Count | r=0.964 rolling mean → next month; outperforms raw lag-1 |
| `rolling_std_3m` | Volatility | Directly separates high-CV (volatile) from low-CV (stable) cells |
| `recurrence_rate` | Recurrence | Top cells = 1.0; low-count cells = 0.17–0.50; strong rank separator |
| `n_active_months` | Recurrence | Integer count; lossless version of recurrence_rate |
| `n_months_in_top100` | Recurrence | Identifies elite persistent cells; orthogonal to raw count |
| `is_junction_cell` | Spatial | Binary; junction lag-1 r=0.948 > cell lag-1 r=0.932; named junction = real infrastructure |

---

## Tier B — Likely Useful

Include, but expect moderate importance. Worth testing with feature ablation.

| Feature | Group | Rationale |
|---|---|---|
| `cell_lat_center`, `cell_lon_center` | Spatial | Location prior; needed for spatial borrowing in sparse cells; also implicit geographic cluster |
| `n_neighboring_cells_active` | Spatial | Spatial autocorrelation; violations cluster geographically |
| `violation_diversity_lag1` | Violation | Complex cells differ from single-violation-type cells; diversity may predict future severity mix |
| `pct_main_road_lag1` | Violation | High-severity violation; spatial signal distinct from WRONG PARKING |
| `severity_score_lag1` | Violation | Captures dangerous co-occurrence pattern; not fully redundant with diversity |
| `multi_violation_rate_lag1` | Violation | Compound offence density; related to severity but distinct |
| `station_approval_rate_lag1` | Station | Range 21%–55%; genuine operational variance; use with lag to prevent leakage |
| `station_unresolved_rate_lag1` | Station | Range 26%–63%; backlog signal; may affect data completeness |
| `station_validation_delay_lag1` | Station | Range 66h–170h; 2.6× range is real operational difference |
| `month_sin`, `month_cos` | Temporal | Jan was highest volume month; Apr is lowest (but truncated); seasonal pattern present |
| `days_in_window` | Temporal | CRITICAL for April: prevents magnitude leakage from truncation |
| `count_per_day_lag1` | Temporal | Normalized rate; more comparable across partial months |

---

## Tier C — Maybe Useful

Test with feature importance. Drop if importance < 0.01.

| Feature | Group | Caveat |
|---|---|---|
| `pct_commercial_lag1` | Vehicle | Secondary to count signal; varies across zone types but low cell-level variance |
| `pct_two_wheeler_lag1` | Vehicle | Two-wheelers dominate everywhere; low discriminating power |
| `vehicle_type_diversity_lag1` | Vehicle | May add marginal signal for mixed-use zones |
| `approval_ratio_lag1` | Validation | 42% null validation makes this noisy at cell level; use with caution |
| `rejection_ratio_lag1` | Validation | Same noise issue |
| `unvalidated_ratio_lag1` | Validation | Uniform nullness across cell sizes; mostly noise |
| `peak_hour_fraction_lag1` | Temporal | 17.5% of records in peak windows; night-heavy pattern dominates; redefine night peak (00:00–05:59) if used |
| `is_weekend_fraction_lag1` | Temporal | Flat distribution; Mon–Sun range only 20%; low signal |
| `is_month_start` | Temporal | Weak enforcement-surge signal |
| `repeat_vehicle_count_lag1` | Recurrence | Vehicle IDs anonymized; pattern may not be behaviorally meaningful |
| `station_n_cells` | Station | Territory size proxy; useful for normalizing station metrics |

---

## Tier D — Remove

These are administrative artifacts, nulled-out fields, or post-hoc labels with no predictive value.

| Feature | Reason |
|---|---|
| `description` | 100% null |
| `action_taken_timestamp` | 100% null |
| `closed_datetime` | 100% null |
| `response_delay_minutes` | All null |
| `closure_delay_minutes` | All null |
| `center_code` | Admin boundary code; no behavioral meaning |
| `device_id` | Equipment tracking |
| `created_by_id` | Officer ID; no useful pattern |
| `duplicate_group_id` | Post-hoc flag; not predictive |
| `station_encoded` (raw label) | Replace with derived Tier B station features |
| `scita_sent_ratio_lag1` | IT system flag; not behavioral |
| `data_sent_to_scita` | Boolean flag; same |
| `geo_anomaly_flag` | Quality control flag; not predictive for forecasting |
| `is_exact_duplicate` | 0 for all rows; useless |

---

## Final Feature Set Recommendation

For the primary model, use:
- All Tier A (9 features)
- All Tier B (13 features)
- Selected Tier C: `peak_hour_fraction_lag1` (redefined to night window), `station_n_cells`

Total: ~24 features. This is appropriate for a panel with ~4,000–6,000 training rows. Adding more features at this sample size risks overfitting.
