# Validation Plan
## Parking Violation Hotspot Forecasting — Bengaluru

---

## Core Constraint

This dataset covers 6 months (Nov 2023 – Apr 2024), with April truncated. Random train/test splitting is **strictly forbidden** because it would mix future information into training — a cell's January features would be in the test set while its February features are in the training set, producing falsely optimistic evaluation.

All validation must be **temporal** and optionally **spatial**.

---

## Temporal Split Strategy

### Primary: Walk-Forward Validation (Expanding Window)

| Fold | Train Months | Test Month | Notes |
|---|---|---|---|
| Fold 1 | Nov 2023 | Dec 2023 | 1 month train — features limited to lag-1 only |
| Fold 2 | Nov–Dec 2023 | Jan 2024 | 2 months train — lag-1, lag-2 available |
| Fold 3 | Nov 2023–Jan 2024 | Feb 2024 | Full lag-3 features available |
| Fold 4 | Nov 2023–Feb 2024 | Mar 2024 | Full features, larger training set |
| Fold 5 | Nov 2023–Mar 2024 | Apr 2024 | Partial April; normalize counts by days |

**Report metrics on Folds 3–5 only**. Folds 1–2 lack full lag features and should be treated as warm-up periods.

### Secondary: Fixed Split
Train: Nov 2023 – Feb 2024 (4 months)  
Test: Mar 2024 (full month, no truncation issues)  
This is the canonical comparison split used for the primary model evaluation table.

**Why not a single split on the last month?**  
A single fold on one month cannot distinguish whether the model learned a genuine spatial pattern or simply overfit the last month of training data. Walk-forward averages this risk across 3 folds.

---

## Spatial Split Strategy (Secondary Validation)

After temporal validation, run one additional experiment:

**Spatial hold-out**: Remove the top-20 cells from training entirely. Train on all remaining cells. Predict violation counts for the top-20 held-out cells.

**Purpose**: Tests whether the model generalizes to unseen spatial locations or merely memorizes individual cell patterns. If performance on held-out cells is substantially worse than on seen cells, the model is location-memorizing rather than learning spatial features.

**Expected outcome**: The model will degrade for the top-20 cells (which have unique density characteristics), but should still beat the global mean baseline for held-out cells. This is acceptable and expected — the goal is to verify that spatial features (neighbor activity, junction proximity) carry predictive signal.

---

## What Leakage Looks Like

| Leakage Type | Example | Detection |
|---|---|---|
| Temporal leakage | Using count(T) as a feature when predicting count(T) | Check that no feature uses the same window as the target |
| Cell-level target encoding leakage | Encoding a cell's mean count using the full dataset before splitting | Always fit target encoders on training data only |
| Partial April leakage | Treating April as a full-month observation without normalization | Use days_in_window as feature and normalize counts |
| Neighbor leakage | Neighbor's month-T count used in month-T prediction | Neighbor features must also use lag-1 |
| Station metric leakage | Using station-level stats computed on the full dataset | Compute station stats only from training months |

---

## Metrics to Report

### Primary Metrics (Count Regression)

| Metric | Formula | Why This Metric |
|---|---|---|
| MAE | mean(|y_pred - y_true|) | Interpretable: average error in violation count units |
| RMSE | sqrt(mean((y_pred-y_true)²)) | Penalizes large misses; important for top cells |
| Poisson Deviance | 2×Σ(y×log(y/ŷ) - (y-ŷ)) | Calibration metric for count models |
| Normalized MAE | MAE / mean(y_true) | Cross-fold comparability |

### Ranking Quality Metrics (Operational Relevance)

These matter more than raw count accuracy for enforcement deployment.

| Metric | Definition | Operational Interpretation |
|---|---|---|
| Recall@20 | # of actual top-20 cells appearing in predicted top-20 / 20 | What fraction of the true worst zones would a patrol cover? |
| Recall@50 | Same for top-50 | Broader patrol sweep |
| Hit@K | 1 if top-1 predicted = top-1 actual | Pinpoint accuracy |
| Spearman ρ | Rank correlation between predicted and actual orderings | Overall ranking quality |
| NDCG@K | Normalized discounted cumulative gain at K | Penalizes ranking the #1 hotspot at position #5 more than position #2 |

**Target thresholds** (competition-defensible):
- Recall@20 ≥ 0.70 (identify 14 of the 20 worst cells correctly)
- Spearman ρ ≥ 0.80 on held-out months
- MAE ≤ 200 violations/cell/month (vs. baseline MAE expected ~350–500)

---

## Baseline Comparison Table

Report the following table for each fold:

| Model | MAE | RMSE | Recall@20 | Spearman ρ |
|---|---|---|---|---|
| Global mean | — | — | — | — |
| Lag-1 persistence | — | — | — | — |
| Rolling mean (3m) | — | — | — | — |
| Poisson GLM (lag-1 only) | — | — | — | — |
| LightGBM (full features) | — | — | — | — |

Any ML model that does not beat lag-1 persistence on Recall@20 should not be submitted. Lag-1 persistence is a strong baseline for stable spatial patterns.

---

## False Positive vs. False Negative Interpretation

In enforcement priority context:

- **False Positive** (predicted hotspot, not actually a hotspot): Patrol resources are deployed to a zone that has fewer violations than predicted. Cost: wasted patrol time, minor.
- **False Negative** (actual hotspot not in predicted top-K): A high-violation zone is not visited by patrols. Cost: violations go unchecked, enforcement gap. **This is the more costly error.**

**Implication**: Optimize for high Recall@K (minimize false negatives), even at the cost of some precision. It is better to include a borderline cell in the patrol list than to miss a genuine hotspot.

This asymmetry should be made explicit in the competition presentation.

---

## Evaluation of the Composite Hotspot Score (Task 3 Baseline)

The existing `hotspot_priority_score` is a deterministic rule-based score computed on historical data. It does not forecast — it summarizes past behavior.

Evaluate it as follows:
- Use it to rank cells by their historical score
- Measure how well those ranks correlate with the actual future month's violation counts
- Compare Recall@20 of the rule-based score against the ML model's Recall@20

This comparison answers: "Does learning from data improve on a well-designed rule?" If the ML model does not clearly beat the rule, the rule-based approach is the honest recommendation.

---

## Calibration Check

For the Poisson LGBM model, run a calibration check:

- Plot predicted count vs. binned actual count
- If predictions systematically underestimate high-count cells, apply a monotonic recalibration (isotonic regression on the validation fold)
- Report calibration slope: a well-calibrated model has slope ≈ 1.0, intercept ≈ 0

Miscalibration at the top of the distribution matters most because patrol decisions are made on the top-K cells.
