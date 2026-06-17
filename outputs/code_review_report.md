# Code Review Report — ml_hotspot_forecasting.py
## Bengaluru Parking Hotspot Forecasting Pipeline

**Reviewer**: Principal ML Engineer / Senior Python Reviewer  
**Status after review**: GO with 4 mandatory fixes and 3 advisories

---

## 1. Summary Verdict

The pipeline is structurally sound. There is no critical data leakage, the walk-forward temporal split is correct, baselines are implemented honestly, and the decision logic is conservative and defensible. The script ran to completion and produced correct outputs including BASELINE_WINS as the honest result.

Four issues require fixes before the script is used in a production presentation. None are showstoppers but two affect interpretability and one affects the final patrol ranking.

---

## 2. Critical Bugs

### BUG-1 — Fold 1 LGBM Trains and Evaluates on the Same Data (MISLEADING)

**Location**: `run_walk_forward`, line handling `len(train_months) < 2`

```python
else:
    train_df = test_df.copy()
    val_df   = test_df.copy()
```

When Fold 1 has only `["2023-11"]` as training months, there is no inner-fold available. The code falls back to using `test_df` for both training and validation of the LGBM model. The result: `R@20=1.000` for LightGBM on Fold 1 — which is pure memorisation, not prediction. This is not included in primary metrics (correctly), but it appears in `model_comparison_table.csv` and `fold_predictions.csv` where a judge reading the table will see a perfect score and question it.

**Fix**: When `len(train_months) < 2`, skip LGBM training entirely for that fold and record `NaN` for LGBM metrics on that row. Or add a column `lgbm_valid=False` to flag it.

---

### BUG-2 — Final Patrol Priority Predicts April (Known Data), Not Future

**Location**: `build_final_patrol_priority`

```python
train_months = ["2023-11","2023-12","2024-01","2024-02","2024-03"]
final_df = build_fold_dataset(panel_norm, valid, train_months, "2024-04")
```

April 2024 is in the dataset. The "final patrol priority" is predicting a month that already happened. The output is labelled as a forward-looking deployment ranking but is actually Fold 5 re-run. For a competition presentation, showing April predictions as "next month forecast" is misleading.

**Fix**: Keep this as-is but rename clearly in the output file and markdown:
- Change column header from `patrol_rank` description to `"predicted_priority_for_apr2024_proxy"`
- Add a comment in `executive_results.md`: "Patrol ranking is based on April 2024 prediction (last available window). For live deployment, re-run with next calendar month as prediction target."

---

### BUG-3 — Inner Train/Test Feature Distribution Mismatch

**Location**: `run_walk_forward` inner fold construction

```python
inner_train = train_months[:-1]
inner_pred  = train_months[-1]
train_df = build_fold_dataset(panel_norm, valid, inner_train, inner_pred)
```

For Fold 3 (pred=Feb 2024, train=[Nov,Dec,Jan]):
- LGBM is **trained** on features from `inner_train=[Nov,Dec]`, `inner_pred=Jan` → `count_lag3=0` (only 2 months available)
- LGBM is **evaluated** on features from `train=[Nov,Dec,Jan]`, `pred=Feb` → `count_lag3` is from Nov (non-zero)

The feature `count_lag3` has value 0 for all training rows but a real non-zero value in test rows. The model has never seen non-zero lag-3 examples during training for this fold. This is a feature distribution shift between train and test — it degrades LightGBM's lag-3 coefficient and partially explains why LGBM underperforms rolling_mean_3m.

**This is not a leakage bug** — it's a modeling construction weakness. It is the root cause of why LightGBM's Spearman ρ (0.697) is lower than rolling mean (0.737) on primary folds.

**Fix**: Accept this limitation for now (it's inherent to the short dataset) but document it explicitly in `validation_notes.md`. Do not claim LightGBM was properly trained with full lag features for the primary folds.

---

### BUG-4 — `is_month_start` Only Flags January (Hardcoded)

**Location**: `add_temporal_features`

```python
feat_df["is_month_start"] = 1 if month_num in [1] else 0
```

The intent was "January enforcement surge". This is fine as a binary Jan/non-Jan feature but is named misleadingly — `is_month_start` implies it flags the start of every month. The name causes confusion. It is also a single binary with the same value for all cells in a given month — it provides no cell-level discrimination and adds zero signal beyond `month_index`.

**Fix**: Rename to `is_january` or drop it entirely. It contributes negligible importance.

---

## 3. Leakage Risks

### LEAKAGE-1 — Station Features: Safe ✅

`add_station_features` correctly filters `valid[valid["ym"].isin(train_months)]` before computing approval rates and validation delays. No future-month station data enters the features.

### LEAKAGE-2 — Composition Features: Safe ✅

`add_composition_features` uses `last_m = train_months[-1]`, which is the last training month, not the prediction month. This is a correct lag-1 feature.

### LEAKAGE-3 — Count Pivot Contains All Months: Technically Safe ✅

`build_pivot(panel_norm)` creates a pivot with all 6 months including the prediction month. However:
- The target is explicitly read as `count_pivot[pred_month]` — this is the label, not a feature
- All lag features (`count_lag1`, `count_lag2`, `count_lag3`) index into train months only
- `n_months_in_top100` iterates over `train_months` only

No leakage, but the code is fragile — a future contributor could accidentally add `count_pivot[pred_month]` as a feature. Add a guard comment.

### LEAKAGE-4 — `approval_ratio` in Composition Features: Risky ⚠️

```python
comp_cols = [..., "approval_ratio", ...]
```

`approval_ratio` per cell per month = `n_approved / count`. This is computed from the raw panel which uses `validation_flag_binary` from the parquet. The validation status is assigned after the fact (median 31-hour delay). For the training month (lag-1), the validation status should be available before the prediction month. This is safe for months with complete validation, but 42% of records have null validation status. The feature is noisy but not leaked.

**Assessment**: Keep it but note the 42% null caveat. The `fillna(0)` in feature construction handles nulls safely.

---

## 4. Metric Problems

### METRIC-1 — `spearman_top100` Computes Rank Among Actual Top-100, Not Predicted Top-100

```python
top_idx = np.argsort(actual)[::-1][:100]
r, _ = spearmanr(actual[top_idx], predicted[top_idx])
```

This computes Spearman ρ between actual values and predicted values **for the cells that are actually the top-100**. The predicted values for those cells may be far outside the model's top-100. This is the correct and intended definition — it measures "how well does the model rank the truly important cells" — and is the right metric for patrol prioritization. No change needed.

### METRIC-2 — `recall_at_k` Denominator is Always K, Not Min(K, N)

```python
return len(top_actual & top_predicted) / k
```

If the test set has fewer than K cells, the denominator is still K, making recall artificially low. For test folds with 600-1000 cells and K=20 or K=50, this is fine. For the April fold (606 cells) and K=50, all 606 cells are available — no issue. Safe.

### METRIC-3 — NDCG Uses Raw Counts as Gains (Appropriate but Undocumented)

The NDCG implementation uses raw violation counts as gains. This means cells with 5000 violations contribute proportionally more to DCG than cells with 100 violations. For patrol prioritization this is correct behavior — we want the model to rank the 5000-violation cell first. No change needed but add a comment.

### METRIC-4 — No Poisson Deviance Reported

The spec requested Poisson deviance as a secondary metric. It is defined in the spec but not implemented. The current secondary metrics (MAE_top200, RMSE_top200) are adequate for competition purposes. This is a minor gap.

**Fix (optional)**: Add `poisson_deviance = 2 * sum(y * log(y/yhat) - (y-yhat))` for non-zero actual cells.

---

## 5. Feature Problems

### FEAT-1 — `rolling_mean_3m` and `count_lag1` Are Nearly Identical for Fold 1

For Fold 1 (only one training month): `rolling_mean_3m = c1 = count_lag1`. The rolling mean degenerates to lag-1. This explains why both show exactly R@20=0.800 for December. Not a bug — just a degenerate case for warm-up folds.

### FEAT-2 — `volatility_score` and `rolling_std_3m` Are Redundant

```python
row["volatility_score"] = row["rolling_std_3m"] / max(row["rolling_mean_3m"], 1)
```

`volatility_score` is `rolling_std_3m` divided by `rolling_mean_3m` (coefficient of variation). LightGBM with split-based importance will use whichever is more discriminative. Both appear in the top features. There is no harm in keeping both, but they carry overlapping information. The model already showed both in top-10 importance — they are being used.

### FEAT-3 — `stn_approval_rate` at 4.51% Importance — Real Signal

This is the 6th most important feature. Station approval rate (range 21%–55%) is genuinely predictive because it correlates with enforcement intensity and jurisdiction geography. This is correctly classified as Tier B.

### FEAT-4 — `peak_h_frac_lag1` Is Defined on Night-Heavy Data

The raw `peak_h_frac` is computed from `is_peak_hour` which flags 07:00–10:59 and 17:00–20:59. But 51.1% of enforcement happens 00:00–05:59. The peak-hour feature as defined only captures 17.5% of records. It is not wrong — it captures the daytime/nighttime split — but it is weak and its importance score reflects this.

### FEAT-5 — `_train_total` Leftover Column

```python
row["_train_total"] = sum(train_vals)
```

This is computed and stored but `get_feature_cols` drops it via the `_train_total` exclusion. It never reaches the model. It is dead code — harmless but untidy.

**Fix**: Remove the `_train_total` computation entirely.

---

## 6. Validation Problems

### VAL-1 — Val Split for LGBM Early Stopping is Random, Not Temporal

```python
val_df = train_df.sample(frac=0.2, random_state=42)
train_df = train_df.drop(val_df.index)
```

The 20% validation set for LGBM early stopping is a random sample of the inner training fold. For a temporal dataset, this means earlier months can end up in the validation set while later months are in training. For early stopping purposes only (not generalization metrics), this is acceptable — it only affects when training stops, not the test evaluation. However, with only 700-900 training rows, 20% = 140-180 rows for validation is borderline thin.

**Assessment**: Acceptable for this dataset size. Document it.

### VAL-2 — Fold 1 and Fold 2 Are Warm-Up Folds but Appear in Output Table

Folds 1 and 2 are correctly marked `is_primary=False`. However, Fold 1 LGBM shows R@20=1.000 (overfitting artifact). This will confuse anyone reading `model_comparison_table.csv` without understanding the folding logic. The table needs a note or the row needs flagging.

### VAL-3 — April Normalization Applied Before Building the Panel

`normalize_april` multiplies April counts by 3.75 before any fold construction. This means:
- April lag features (used when predicting a hypothetical May) are inflated by 3.75
- The Fold 5 target (April) is also inflated by 3.75
- Both are consistently inflated → comparison between prediction and target is self-consistent

This is **correct by design**: you want April counts on the same scale as other months for lag comparability. The days_in_window feature (=8 for April, =30 for others) provides an additional normalization signal to the model. No fix needed.

### VAL-4 — Only 2 Primary Folds: Statistical Power is Very Low

Averaging over 2 folds (Feb and Mar) means each metric is the mean of 2 observations. A difference of 0.025 in Recall@20 (2 cells out of 20) across 2 folds is not statistically significant. The BASELINE_WINS decision is correct in this context — the improvement is too small to be meaningful with this sample size.

---

## 7. Output File Problems

### OUT-1 — `fold_predictions.csv` Contains Fold 1 LGBM Predictions That Are Memorized

Fold 1 LGBM predictions where `pred_lgbm` values were generated from a model trained on the same data. These rows should be flagged with `lgbm_valid=False`.

### OUT-2 — `final_ranked_patrol_priority.csv` Misleadingly Named

The file predicts April 2024, which is in the training data. The filename implies forward-looking deployment. For competition presentation, this needs a clear label.

### OUT-3 — `model_comparison_table.csv` is Correct and Complete ✅

All 5 models × 5 folds = 25 rows. Columns include fold, pred_month, is_primary, and all metrics. Correct.

### OUT-4 — `feature_importance.csv` is From Fold 5 Model Only

Feature importance from the last trained model (Fold 5 inner: trained on Nov-Mar, predicting Apr). This is the most data-rich model and a reasonable choice. However, importance may differ across folds due to the distribution shift issue (BUG-3). Document this caveat.

### OUT-5 — All Required Files Exist ✅

`model_comparison_table.csv`, `fold_predictions.csv`, `feature_importance.csv`, `final_ranked_patrol_priority.csv`, `final_model_summary.md`, `validation_notes.md`, `executive_results.md` — all written successfully.

---

## 8. Recommended Fixes (Ranked by Priority)

| Priority | Fix | Effort |
|---|---|---|
| P1 | Flag Fold 1 LGBM as invalid in comparison table and fold_predictions | 5 min |
| P2 | Add note to final_ranked_patrol_priority.csv that this is April proxy, not true future | 2 min |
| P3 | Document BUG-3 (feature distribution shift) explicitly in validation_notes.md | 5 min |
| P4 | Rename `is_month_start` to `is_january` in code | 2 min |
| P5 | Remove dead `_train_total` computation | 1 min |
| P6 | Add guard comment near count_pivot usage warning future contributors about pred_month | 2 min |
| P7 (optional) | Add Poisson deviance metric | 10 min |

---

## 9. Final Go / No-Go Decision

**GO — with P1 and P2 fixes applied before presentation.**

### What is correct
- Walk-forward temporal validation: **correct**. No random splitting. Months strictly ordered.
- Leakage safety in lag features, composition features, station features: **clean**
- April normalization (×3.75 factor): **correct and consistent**
- Baseline implementations: **correct**. Global mean uses training data only. Lag-1 uses pre-computed lag from test features (which came from prior month). Rolling mean same.
- LGBM Poisson objective with log-count sample weights: **appropriate** for count target
- Decision logic (BASELINE_WINS): **honest and correct**. Rolling mean genuinely ties or beats LightGBM on primary folds.
- All 7 required output files: **exist and are correctly formatted**

### What is broken
- Fold 1 LGBM R@20=1.000 appearing in the comparison table without a flag: **misleading**

### What is risky
- Final patrol priority predicts April (known data) and is presented as deployment output: **presentation risk**
- Feature distribution shift between inner LGBM training and actual test: **root cause of LightGBM underperformance** — not fixable with this dataset depth but must be disclosed

### Is the model likely to beat lag-1 and rolling-mean?
**No.** The data has already run. BASELINE_WINS is the honest result:
- Rolling mean Recall@20 = 0.725 (primary folds average)
- LightGBM Recall@20 = 0.700 (primary folds average)
- Margin = −2.5 pp in favor of rolling mean

This is not a pipeline failure. It is the correct finding: with only 6 months and 2 primary folds, a well-tuned gradient booster cannot out-learn a simple persistence baseline when the spatial structure is this stable.

### What should be submitted instead?
**Rolling mean + rule-based composite score ensemble** as the forecasting system, with LightGBM included as a comparison point. The narrative: "We built and evaluated a full ML pipeline. The honest result is that the baseline persistence model matches LightGBM on this dataset due to the strong structural stability of hotspots. We submit the rolling mean as the forecasting engine because it is simpler, more interpretable, and equally accurate on the available evaluation data."

This is a stronger competition answer than overselling a marginal LightGBM result.
