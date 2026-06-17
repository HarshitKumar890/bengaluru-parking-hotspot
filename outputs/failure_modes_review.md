# Failure Mode Review
## Attack the Project — What Can Break It

---

## Data Failure Modes

**1. The model learns enforcement patterns, not parking patterns.**
The dataset records where officers went and what they ticketed. Low-violation cells may simply be unpatrolled, not violation-free. Any prediction the model makes is a prediction of future enforcement activity — not future illegal parking. A judge who asks "how do you know there are actually more violations there?" cannot be answered with this data alone.

**2. Near-duplicate records inflate cell counts.**
10,926 near-duplicate records (3.7%) are not deduplicated from the training targets. The model learns inflated counts for cells with duplicate-prone behavior. This is a systematic upward bias for high-activity cells. Fix: flag and exclude near-duplicates before aggregating cell counts.

**3. April truncation corrupts the test fold.**
April 2024 has ~10 days of data. Raw April counts are ~25% of full-month expected values. Any model that predicts March-level counts for April will look wildly wrong. This is not a model failure — it is a data construction failure. Must normalize by days_in_window before any April evaluation.

**4. UPPARPET's single-cell concentration is not generalisable.**
60.3% of UPPARPET's cases come from one cell. This cell dominates the top-1 hotspot ranking. If UPPARPET's patrol routing changes (or if the data collection device in that cell fails), the model loses its top prediction entirely. The model cannot generalize this pattern to other stations.

**5. 42% of records have null validation status.**
Any feature derived from validation status (approval ratio, rejection ratio) is computed on the 58% of records that were validated. If validation assignment is non-random (e.g., more complex cases get validated first), then cell-level validation ratios carry selection bias.

---

## Forecasting Failure Modes

**6. 6 months is not enough for seasonality.**
The data spans Nov 2023–Apr 2024 — one partial season. There is no second November, no second January, to confirm seasonal patterns. The month features (sin/cos encoding) cannot be validated against a second cycle. Any claimed seasonal pattern is a hypothesis, not evidence.

**7. Lag-1 is already 93% of the signal.**
The ML model's marginal improvement over lag-1 persistence may be small enough to be undetectable given only 5 test transitions. If the model achieves Recall@20 = 80% and lag-1 achieves 77%, the difference is 3 cells out of 20. That is statistically and practically marginal.

**8. Trend features are corrupt.**
All growth values for top cells are negative (ranging from -0.19 to -0.98). This is April truncation, not a genuine declining trend. Any trend slope or growth feature computed with April data will be wrong. Must exclude April from trend computation or normalize first.

**9. The model cannot predict emerging hotspots.**
By construction, lag-based features cannot predict a cell that was dormant in all prior months suddenly activating. 85 cells were active in April but not in November. These "new" hotspots are unpredictable with the current feature set.

---

## Evaluation Failure Modes

**10. Using the wrong metric.**
If MAE is reported across all 1,393 cells, low-count cells (median = 20 violations) dominate the metric while contributing no operational value. A model that perfectly predicts the top-50 cells but is wrong about all 1,343 low-count cells will look bad on overall MAE. Report Recall@20 and Spearman ρ for the top-100 cells.

**11. Only 3 usable walk-forward folds.**
With 5 month transitions and the first 2 excluded (insufficient lag features), there are only 3 folds (Feb, Mar, Apr) for evaluation. Apr is truncated. Effectively 2 reliable test months. That is too thin to draw strong statistical conclusions. Error bars on any reported metric will be wide.

**12. Evaluating on both train and test transitions.**
If Recall@20 is reported on all 5 transitions including the 2 warm-up folds (which use the same cells for training and testing), the metric will be inflated. Report only on held-out folds.

---

## Leakage Failure Modes

**13. April normalization done incorrectly.**
If days_in_window for April is computed as calendar days rather than actual days with data (which may be ~8–10 days), the normalization factor will be wrong, and the test target will remain corrupt.

**14. Station-level features computed on full dataset.**
If station approval_rate is computed using all 6 months and then used as a feature for month-2 prediction, it leaks months 3–6 into the feature. Must compute station features on training months only, per fold.

**15. Target encoding the spatial_cell_id.**
If cell-level mean count is used as a feature (e.g., "historical average count for this cell") and that average is computed using the full 6-month dataset, it leaks the test month into the feature for all cells.

---

## Presentation Failure Modes

**16. Claiming congestion prediction.**
There is zero traffic flow data. Any sentence that says "this predicts where congestion will occur" is false. It predicts where enforcement officers will find violations. A judge with domain knowledge will call this out immediately.

**17. Calling lag-1 persistence a "baseline" when it is actually competitive.**
If the ML model's Recall@20 is 80% and lag-1 is 77%, presenting the model as a major advance over the baseline is not credible. Be honest about how marginal the improvement is.

**18. Overclaiming 6-month temporal depth.**
Saying "our model uses 6 months of historical data" implies rich temporal patterns. In reality, there are 5 observable month-to-month transitions. Calling this a time-series forecasting system overstates the temporal sophistication.

---

## Deployment Failure Modes

**19. The model output requires enforcement officer buy-in.**
A ranked patrol priority list is only useful if officers actually follow it. If enforcement patterns are driven by officer familiarity with routes (which UPPARPET's concentration suggests), the model's recommendations may be ignored.

**20. The model has no signal for the bottom 1,300 cells.**
If the enforcement agency deploys patrols to low-count cells based on model output, there is no historical evidence those cells have real violations vs. just being unpatrolled. The model confidently predicts low counts — but "low count because no one went there" is indistinguishable from "low count because nothing happens there."
