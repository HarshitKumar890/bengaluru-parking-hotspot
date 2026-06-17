# Final Model Recommendation
## Bengaluru Parking Hotspot Forecasting

---

## Ranked ML Tasks

### 1. Next-Window Violation Count Forecasting
- **Feasibility**: High. Lag features are extremely strong (r=0.932). Panel structure is clean.
- **Data support**: Strong. 6-month cell×month panel; all top-50 cells have full history.
- **Business value**: Highest. Produces a ranked patrol priority list. Directly deployable.
- **Competition value**: High. Quantitative evaluation with multiple metrics. Clear baselines.
- **Complexity**: Low-medium. LightGBM on ~24 features, ~4,000 rows.
- **Risk**: April truncation must be handled. Only 3 reliable test folds.
- **Leakage risk**: Moderate. Station features and target encoding must use training-only computation.
- **Interpretability**: High. Feature importance from LightGBM; lag features are self-explanatory.
- **Verdict**: **Winner.**

---

### 2. Hotspot Binary Classification
- **Feasibility**: High.
- **Data support**: Strong. Same feature set as count forecasting.
- **Business value**: High. "Deploy here or not" decision.
- **Competition value**: Medium-high. PR-AUC and Recall@K are clear metrics.
- **Complexity**: Low.
- **Risk**: Threshold for "hotspot" is arbitrary. Loses magnitude information.
- **Leakage risk**: Same as count forecasting.
- **Interpretability**: High.
- **Verdict**: Strong fallback if count model underperforms. But inferior to count forecasting because it discards the 5000 vs 500 distinction that matters for patrol allocation.

---

### 3. Hotspot Priority Ranking (rule-based composite score)
- **Feasibility**: Already done. `hotspot_priority_score` exists.
- **Data support**: Complete.
- **Business value**: High as a baseline and operational reference.
- **Competition value**: Low. No ML; no evaluation beyond rank correlation.
- **Complexity**: Zero (deterministic formula).
- **Risk**: None for this task. Weights are assumed, not learned.
- **Leakage risk**: None.
- **Interpretability**: Highest.
- **Verdict**: Use as Baseline 2 in the count forecasting evaluation. Not a standalone ML task.

---

### 4. Repeat-Offender Detection
- **Feasibility**: Low.
- **Data support**: Weak. 84.7% of vehicles appear only once. Vehicle IDs are anonymized.
- **Business value**: Conditional. Only valuable if vehicle IDs can be de-anonymized.
- **Competition value**: Low. Class imbalance 85:15; no real signal from anonymized IDs.
- **Complexity**: Low.
- **Risk**: Memorizes vehicle IDs from training window; no generalization.
- **Leakage risk**: High.
- **Interpretability**: Low.
- **Verdict**: Do not build.

---

### 5. Recurrence / Persistence Scoring
- **Feasibility**: High. Already computed in `hotspot_persistence_table.csv`.
- **Data support**: Strong.
- **Business value**: Medium. Useful for classifying cells as "always hot" vs "sometimes hot."
- **Competition value**: Low. It is a descriptive label, not a prediction.
- **Complexity**: Zero (rule-based).
- **Leakage risk**: None.
- **Verdict**: Use as a feature in count forecasting, not as a separate ML task.

---

## Winner: Task 1 — Next-Window Violation Count Forecasting

---

## Full Specification for the Winning Task

### Target Variable
`violation_count_next_month` — total violation records for a spatial cell in month T.

### Aggregation Level
Spatial cell (`spatial_cell_id`) × calendar month. Unit of analysis: one row per (cell, month) pair.

### Panel Size
- Raw: 5,261 cell×month rows (6 months, excluding NaT and normalizing April)
- Usable for training (cells with ≥3 months history): ~4,600 rows
- Usable for walk-forward evaluation (Folds 3–4): ~2,200 test rows

### Feature Set (24 features)
**Tier A** (9): count_lag1, count_lag2, count_lag3, rolling_mean_3m, rolling_std_3m, recurrence_rate, n_active_months, n_months_in_top100, is_junction_cell

**Tier B** (13): cell_lat_center, cell_lon_center, n_neighboring_cells_active, violation_diversity_lag1, pct_main_road_lag1, severity_score_lag1, multi_violation_rate_lag1, station_approval_rate_lag1, station_unresolved_rate_lag1, station_validation_delay_lag1, month_sin, month_cos, days_in_window

**Selected Tier C** (2): peak_hour_fraction_lag1 (redefined to 00:00–05:59 night window), station_n_cells

### Train/Test Strategy
Walk-forward expanding window:
- Fold 3: Train Nov–Jan → Test Feb (first reliable fold with full lag-3)
- Fold 4: Train Nov–Feb → Test Mar (canonical evaluation fold)
- Fold 5: Train Nov–Mar → Test Apr (normalized, treat as secondary)
- Report Folds 3–4 as primary. Fold 5 secondary with normalization caveat.

**April normalization**: multiply raw April cell counts by (30 / n_days_with_data_in_april) before using as target or in lag features.

### Baselines
1. Lag-1 persistence: predict(T) = count(T-1)
2. Rolling 3-month mean: predict(T) = mean(T-3:T-1)
3. Global mean: predict(T) = mean of all cell-months in training set
4. Rule-based composite score rank (current hotspot_priority_score as ranking baseline)

### Primary Model Family
LightGBM with `objective='poisson'`:
- `num_leaves=31`, `min_child_samples=10`, `learning_rate=0.05`, `n_estimators=300`
- `feature_fraction=0.8`, `bagging_fraction=0.8`, `bagging_freq=5`
- `sample_weight=log(count+1)` to upweight high-count cells
- Early stopping on validation fold

### Metrics
**Primary (ranking quality)**:
- Recall@20: fraction of true top-20 cells in predicted top-20
- Recall@50: same for top-50
- Spearman ρ (top-100 cells)

**Secondary (count accuracy)**:
- MAE on top-200 cells only (not all 1,393)
- Poisson deviance

**Do not report**: overall MAE across all 1,393 cells (dominated by meaningless low-count cells).

### Operational Value
Output is a ranked list of cells with predicted violation count for the upcoming month. Includes persistence flag, responsible station, and severity composite. Shift commanders use it as a patrol priority list.

### Expected Weaknesses
1. Only 3 reliable test folds — statistical confidence in metric improvement over baselines will be thin
2. Cannot predict emerging hotspots (cells with no prior history)
3. Model learns enforcement patterns, not underlying violation patterns — deployment decisions must acknowledge this
4. April evaluation is inherently noisy due to truncation; count on March as the definitive test
5. Marginal improvement over lag-1 persistence may be small — a 3-cell improvement in Recall@20 (77% → 92%) is a 15pp gain but represents only 3 cells in the patrol list
