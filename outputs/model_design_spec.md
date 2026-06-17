# Model Design Specification
## Parking Violation Hotspot Forecasting — Bengaluru

---

## Ranked ML Task Candidates

### Task 1 — Next-Window Violation Count Forecasting (PRIMARY CHOICE)
**Target**: Predicted violation count for spatial cell in next month  
**Label construction**: Aggregate violation records to cell×month panel. Target = count in month T. Features use months ≤ T-1.  
**Feature set**: All Groups 1–8 from feature engineering plan, lag 1–3 counts, rolling stats  
**Model family**: LightGBM Regressor (primary); Poisson GLM (baseline); negative binomial GLM (robust baseline)  
**Metrics**: MAE, RMSE, Poisson deviance, Recall@K (did top-K predicted cells include the actual top-K?), Hit@20 (were the top-20 actual hotspots covered in the top-20 predictions?)  
**Strengths**: Direct operational output; naturally maps to patrol scheduling; evaluatable with held-out time windows; no label fabrication required  
**Weaknesses**: Only 5–6 time windows available; partial April must be excluded or normalized; count skew (20k vs 1 cell) requires careful treatment  
**Leakage risk**: Low, if temporal split is strict. Risk: using any same-window features.  
**Operational value**: Highest. Shift commander prints top-20 list before patrol deployment.

---

### Task 2 — Hotspot Classification (STRONG ALTERNATIVE)
**Target**: Binary: is this cell a "hotspot" in the next window? (define hotspot as top-25% or top-100 by count)  
**Label construction**: Binary label = 1 if cell count in month T exceeds threshold (e.g., 75th percentile of monthly cell counts)  
**Feature set**: Same as Task 1  
**Model family**: LightGBM Classifier; Logistic Regression (baseline)  
**Metrics**: Precision@K, Recall@K, PR-AUC, F1 at operating threshold  
**Strengths**: Simpler output; easier to explain to stakeholders; handles count skew better than regression  
**Weaknesses**: Threshold for "hotspot" is arbitrary; loses rank-ordering information within hotspot set; binary label discards useful gradient between 50-violation and 5000-violation cells  
**Leakage risk**: Same as Task 1  
**Operational value**: High. Decision becomes: "deploy here or not" rather than "how many patrols".

---

### Task 3 — Enforcement Priority Composite Score (USEFUL SUPPLEMENT)
**Target**: Rule-based composite score (already computed as `hotspot_priority_score`)  
**Label construction**: Weighted normalized composite of density, recurrence, peak-hour fraction, junction proximity, delay, severity  
**Model family**: No model required — this is a deterministic scoring function  
**Metrics**: Ranking correlation with ground-truth count, Recall@K  
**Strengths**: Immediately usable; no overfitting risk; fully explainable  
**Weaknesses**: Static — does not forecast future state, only summarizes past; weights are assumed, not learned  
**Operational value**: High as a complement; the forecast model tells you *where next*, the composite score tells you *how bad historically*

---

### Task 4 — Repeat Offender Detection (WEAK FOR THIS DATASET)
**Target**: Binary: will this vehicle appear again in the dataset within 30 days?  
**Label construction**: For each violation record, check if same vehicle appears within 30-day future window  
**Feature set**: Vehicle type, time of day, cell, violation type, prior appearance count  
**Model family**: Logistic Regression, XGBoost Classifier  
**Metrics**: Precision@K, Recall  
**Strengths**: Directly actionable for targeted enforcement letters or fines escalation  
**Weaknesses**: Vehicles are anonymized — no external linkage to real registration data; 84.7% of vehicles appear only once (extremely imbalanced); anonymization limits real-world deployment; recurrence detection works only within the 6-month window  
**Leakage risk**: High — any model that sees both past and future appearance in training will memorize IDs  
**Operational value**: Low in this dataset. Viable only if vehicle IDs are de-anonymized.

---

## Primary Target: Task 1 — Next-Window Violation Count Forecasting

**Justification for this choice over Task 2**:
- Produces a ranked ordered list, not just a binary set. Top-100 cells ranked by predicted count gives richer patrol scheduling capability than a binary hotspot flag.
- Evaluation is more rigorous: MAE and Recall@K can both be computed, and the model can be penalized for misranking, not just mislabeling.
- The count target naturally incorporates enforcement magnitude — predicting 5,000 vs 500 is operationally significant; a binary label cannot distinguish them.
- Feasible with the data: all 50 top cells have 6 complete months; even simple lag features will produce a competitive baseline.

**Justification for using LightGBM over deep learning**:
- ~6,965 rows in the monthly panel; even with biweekly windows, <15,000 rows. Deep learning adds no value at this scale.
- Tree-based models handle missing features gracefully (low-count cells with partial history).
- LightGBM natively handles count skew better than a plain regressor via `objective='poisson'` or `tweedie`.
- Feature importance from LGBM provides direct business explanation.

---

## Pipeline Architecture

### Stage 0 — Panel Construction
```
cell × month panel  (5,266 rows raw)
  → exclude NaT month (5 rows)
  → normalize April counts by days_in_window (partial month)
  → result: 5,261 clean cell×month rows
```

### Stage 1 — Feature Engineering
```
For each (cell, month_T) row:
  → lag1, lag2, lag3 counts
  → rolling mean/std/max over lag1..lag3
  → trend slope (linear fit on available lags)
  → peak_hour_fraction_lag1, weekend_fraction_lag1
  → violation_diversity_lag1, severity_score_lag1
  → vehicle_type_mix_lag1
  → station_metrics_lag1 (approval rate, validation delay, unresolved rate)
  → spatial context (is_junction_cell, neighbor activity)
  → temporal context (month_sin, month_cos)
  → days_in_window (normalization for partial April)
```

### Stage 2 — Baseline Models
**Why baselines are required**: Without a baseline, any ML model result is uninterpretable. A naïve model that predicts "next month = last month" (lag-1 persistence) is a legitimate and strong competitor for stable spatial patterns.

| Baseline | Description | Why It Matters |
|---|---|---|
| Lag-1 Persistence | Predict T = count(T-1) | Strongest naive baseline; any ML model must beat this |
| Lag-3 Rolling Mean | Predict T = mean(T-3:T-1) | Smoothed persistence; handles one-month spikes |
| Global Mean | Predict T = mean over all cells and months | Floor baseline |
| Poisson GLM with lag-1 | GLM with only lag-1 and month dummies | Statistical baseline; interpretable coefficients |

### Stage 3 — Primary Model: LightGBM
```python
import lightgbm as lgb

model = lgb.LGBMRegressor(
    objective='poisson',     # appropriate for count targets with overdispersion
    learning_rate=0.05,
    n_estimators=500,
    num_leaves=31,           # conservative — small dataset
    min_child_samples=10,    # prevent overfitting on low-count cells
    feature_fraction=0.8,
    bagging_fraction=0.8,
    bagging_freq=5,
    random_state=42,
    n_jobs=-1,
)
```

**Why Poisson objective**: Violation counts are non-negative integers. Poisson log-link prevents negative predictions and is better calibrated for count data. If the model shows underdispersion (variance < mean), Tweedie is the fallback.

**Why not `tweedie` by default**: Tweedie is for zero-inflated data. This panel has low but non-zero counts for active cells; very few true zeros in top cells.

### Stage 4 — Optional Spatial Smoothing
For cells with ≤2 months of history, the lag features are sparse. Apply a **spatial borrowing** step: augment features with weighted average of 8 neighboring cells' lag-1 counts. This reduces prediction variance for sparse cells.

---

## Class Imbalance / Count Skew Handling

The top cell has 20,798 violations; the median cell has 20. This is a 1,000× range.

**For regression (Task 1)**:
- Use `sample_weight` proportional to log(count+1) — upweight high-count cells during training
- Alternatively, model log(count+1) as target (log-transform) and evaluate in original space
- Report metrics separately for top-100, top-500, and all cells — the top-100 ranking quality is what matters operationally

**Do not delete low-count cells**: They represent real enforcement zones that may surge in future months. Their history is a valid zero-recurrence signal.

---

## Handling the Partial April Problem

April 2024 has only 15,045 records vs. 55–65k for full months (≈25% of a full month based on date range).

Options:
1. **Exclude April from training targets** — use only 5 full months; April becomes the test window with count normalized to expected full-month equivalent
2. **Normalize April counts** — multiply by (30 / actual_days_in_April_in_dataset); use as a partial prediction window
3. **Truncation flag** — include April as a feature (days_in_window=~10) and let the model learn the normalization

Recommended: Option 2 for training; evaluate specifically on April normalized counts to test generalization.

---

## Hotspot Ranking Tables (Generated from Existing Data)

Top 20 cells already ranked in `hotspot_priority_scores.csv`. For the ML model, the target ranking table is: predicted count in next window, ranked descending, with confidence interval (bootstrap or LGBM quantile regression).

Output schema:
```
spatial_cell_id | cell_lat | cell_lon | predicted_count_next_month | 
confidence_lower | confidence_upper | historical_rank | 
persistence_flag | peak_hour_flag | severity_score | 
responsible_station | priority_tier (1/2/3)
```
