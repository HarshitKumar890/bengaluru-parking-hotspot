# Feature Engineering Plan
## Parking Violation Hotspot Forecasting — Bengaluru

---

## Unit of Analysis

The primary modeling unit is the **spatial cell × time window** observation.

Each row in the model dataset = one spatial cell in one time window (e.g., one month or one biweekly block).

This gives a structured panel with ~1,393 cells × 5 usable months = ~6,965 rows for training (excluding partial April and using first 5 months as input windows with appropriate lag structure).

---

## Feature Groups

### Group 1 — Spatial Identity Features
*Why: The model must distinguish persistent high-violation zones from one-time events. Spatial location is a strong prior.*

| Feature | Construction | Notes |
|---|---|---|
| `spatial_cell_id` | Grid cell identifier | Used as entity ID in panel models |
| `cell_lat_center` | Mean lat of cell | For spatial decay features |
| `cell_lon_center` | Mean lon of cell | For spatial decay features |
| `n_neighboring_cells_active` | Count of adjacent cells with >0 violations in window | Spatial autocorrelation proxy |
| `is_junction_cell` | 1 if any record in cell has a named junction | Binary proximity signal |
| `junction_density` | Count of unique junction names in cell | Higher = more regulated intersection |

---

### Group 2 — Lagged and Rolling Violation Counts
*Why: Historical violation count is the single strongest predictor of future violation count. Temporal lags capture momentum and seasonality.*

| Feature | Construction | Notes |
|---|---|---|
| `count_lag1` | Violation count in previous month | Direct lag |
| `count_lag2` | Count 2 months prior | Momentum check |
| `count_lag3` | Count 3 months prior | Seasonality anchor |
| `rolling_mean_3m` | Mean of last 3 months | Smoothed trend |
| `rolling_std_3m` | Std of last 3 months | Volatility — high std = unreliable cell |
| `rolling_max_3m` | Max of last 3 months | Spike detector |
| `trend_slope` | Linear slope over available history | Rising vs declining enforcement zone |
| `count_lag1_peak_hour` | Peak-hour violations in previous month | Time-of-day persistence signal |
| `count_lag1_weekend` | Weekend violations in previous month | Day-type persistence |

**Critical constraint**: When predicting month T, use only features from months ≤ T-1. No data from month T leaks into features.

---

### Group 3 — Recurrence and Persistence Features
*Why: A cell that has appeared in the top-K for 5 consecutive months is qualitatively different from a cell that spiked once. Persistence is a strong enforcement-priority signal.*

| Feature | Construction | Notes |
|---|---|---|
| `n_active_months` | How many of the prior N months had count > 0 | Persistence indicator |
| `n_months_in_top100` | How many months the cell was in the top-100 | Elite hotspot flag |
| `recurrence_rate` | n_active_months / total_months | Normalized persistence |
| `repeat_vehicle_count_lag1` | Count of vehicles seen in this cell in ≥2 months | Location-specific repeat offending |
| `unique_vehicle_ratio_lag1` | unique_vehicles / total_violations | Low ratio = same vehicles returning |

---

### Group 4 — Violation Composition Features
*Why: A cell dominated by "WRONG PARKING" is different from one mixing "ROAD CROSSING" + "FOOTPATH" + "WRONG PARKING". Severity and diversity of violations matter for enforcement priority.*

| Feature | Construction | Notes |
|---|---|---|
| `top_violation_type_lag1` | Mode violation type in previous month | Label-encoded |
| `violation_diversity_lag1` | Count of distinct violation types in previous month | High diversity = complex hotspot |
| `pct_wrong_parking_lag1` | Fraction of "WRONG PARKING" in previous month | Dominant violation share |
| `pct_no_parking_lag1` | Fraction of "NO PARKING" in previous month | |
| `pct_main_road_lag1` | Fraction of "PARKING IN A MAIN ROAD" in previous month | Severity indicator |
| `pct_footpath_lag1` | Fraction of "PARKING ON FOOTPATH" in previous month | Pedestrian safety proxy |
| `pct_road_crossing_lag1` | Fraction of "PARKING NEAR ROAD CROSSING" in previous month | High-risk location |
| `multi_violation_rate_lag1` | Records with ≥2 violations / total records | Compound offence density |
| `severity_score_lag1` | Weighted sum: high-risk violations × their frequency | Custom composite |

**Severity weight rationale**: Road crossing (weight 3) > footpath (weight 2.5) > main road (weight 2) > double parking (weight 1.5) > wrong/no parking (weight 1). Weights represent pedestrian safety risk, not fine amount.

---

### Group 5 — Temporal Context Features
*Why: Month-of-year and day-structure effects are real. Jan 2024 was the highest-volume month. These features help the model learn seasonal patterns.*

| Feature | Construction | Notes |
|---|---|---|
| `month_of_year` | 1–12 | Cyclically encoded: sin/cos |
| `month_sin` | sin(2π × month / 12) | Cyclic encoding |
| `month_cos` | cos(2π × month / 12) | Cyclic encoding |
| `is_month_start` | 1 if first 3 days of month | Enforcement surge flag |
| `days_in_window` | Actual days in window | Normalizes partial months (April) |
| `count_per_day_lag1` | count_lag1 / days_in_lag_window | Normalized rate |

---

### Group 6 — Police Station and Jurisdiction Features
*Why: Station-level operational capacity and case backlog affect how violations are processed. A station with 63% unresolved rate (KODIGEHALLI) behaves differently from one with 41% (UPPARPET).*

| Feature | Construction | Notes |
|---|---|---|
| `station_total_cases_lag1` | Total cases filed at responsible station in previous month | Volume proxy |
| `station_approval_rate_lag1` | Station-level approval rate in previous month | Data quality / workflow speed |
| `station_unresolved_rate_lag1` | Station-level unresolved rate in previous month | Backlog proxy |
| `station_validation_delay_lag1` | Station median validation delay in previous month | Operational efficiency |
| `station_n_cells` | Number of distinct cells under this station | Territory size |
| `station_encoded` | Label or target-encoded police station | Categorical identity |

---

### Group 7 — Enforcement Outcome Features
*Why: High rejection rate in a cell may indicate enforcement quality issues or that violations in that cell are harder to prove. High approval rate indicates clean enforcement workflow.*

| Feature | Construction | Notes |
|---|---|---|
| `approval_ratio_lag1` | n_approved / total in cell, previous month | Validation quality signal |
| `rejection_ratio_lag1` | n_rejected / total in cell, previous month | |
| `unvalidated_ratio_lag1` | n_null_status / total in cell, previous month | Missing = never reviewed |
| `scita_sent_ratio_lag1` | Records sent to SCITA / total | Data governance proxy |

---

### Group 8 — Vehicle Type Mix Features
*Why: Commercial vehicles (MAXI CAB, LGV, GOODS AUTO) violating in the same cell as two-wheelers suggests a structurally congested zone vs. a zone with sporadic personal vehicle offenses.*

| Feature | Construction | Notes |
|---|---|---|
| `pct_commercial_lag1` | (MAXI CAB + LGV + GOODS AUTO + LORRY) / total | Commercial vehicle loading |
| `pct_two_wheeler_lag1` | (SCOOTER + TWO WHEELER + MOPED) / total | Two-wheeler dominance |
| `pct_car_lag1` | CAR / total | Car-type dominance |
| `vehicle_type_diversity_lag1` | Count of distinct vehicle types | Mixed vs. single-type zone |

---

## Features Explicitly Excluded

| Excluded Feature | Reason |
|---|---|
| `action_taken_timestamp` | 100% null — cannot be used |
| `closed_datetime` | 100% null |
| `response_delay_minutes` | Derived from null timestamp — all null |
| `closure_delay_minutes` | Same |
| `description` | 100% null |
| Raw vehicle_number counts as ID | Anonymized, PII-sensitive; only aggregated recurrence is used |
| Month T information in features predicting month T | Strict no-leakage constraint |

---

## Feature Matrix Dimensions

For the primary model (monthly panel, top cells only):
- ~782 cells with ≥4 months of data = ~3,910 training rows (5 prediction windows with 3-lag features)
- ~60 features after encoding
- This is a small, clean, well-structured dataset — suitable for gradient boosted trees

For a biweekly panel:
- ~12 windows × 782 cells = ~9,384 rows
- More stable for recency features; recommended for final model
