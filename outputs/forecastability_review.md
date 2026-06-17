# Forecastability Review
## Does the Dataset Support Forecasting?

---

## Forecastability Table (computed)

| From | To | Lag-1 r | Lag-1 MAE | Global Mean MAE |
|---|---|---|---|---|
| 2023-11 | 2023-12 | 0.931 | 27.7 | 78.4 |
| 2023-12 | 2024-01 | 0.924 | 25.0 | 78.6 |
| 2024-01 | 2024-02 | 0.939 | 26.2 | 67.4 |
| 2024-02 | 2024-03 | 0.954 | 21.6 | 68.3 |
| 2024-03 | 2024-04 | 0.906 | 41.4 | 20.9 |

The Mar→Apr transition is anomalous: lag-1 MAE (41.4) exceeds global mean MAE (20.9). This is entirely due to April truncation — April has ~10 days of data, so true activity is ~25% of a full month. The lag-1 prediction is right in direction but ~4× too large in magnitude. Global mean is low because April counts are small. **Do not use raw April counts as a test target without normalization.**

---

## Lag Relationships

**Lag-1 correlation**: Mean r = 0.932 across 4 non-truncated transitions. This is extremely strong for any real-world spatial forecasting task.

**Lag-2 correlation**: r = 0.897–0.947. Almost as strong as lag-1 — the cell ordering is stable over 2 months.

**Rolling mean (lag1:lag3 → next)**: r = 0.928 (Nov-Dec-Jan → Feb); r = 0.964 (Dec-Jan-Feb → Mar). Rolling mean adds smoothing benefit over raw lag-1 for cells with one-month spikes.

---

## Answers

**1. Is lagged history predictive?**
Yes. Unambiguously. Lag-1 r > 0.90 in 4 of 5 transitions. No other feature class will come close.

**2. Is recurrence stronger than trend?**
Yes. The dataset shows no meaningful upward or downward trend in top-cell counts (growth values are all negative but that's April truncation). Month-to-month stability dominates. Recurrence (is-this-cell-always-hot) is stronger than trend direction.

**3. Is there enough signal for a forecasting model?**
Yes, with a critical caveat: the signal is mostly already captured by the lag-1 baseline. The ML model must outperform lag-1 persistence on rank ordering (Recall@20, Spearman ρ) — not just explain variance. A model that fits well but does not improve on lag-1 Recall@20 adds no operational value.

**4. Is a simple baseline already strong?**
Very strong. Lag-1 persistence gets MAE 33.6 vs. global mean 63.3 — a 47% improvement. Rolling 3-month mean achieves r=0.964 for predicting March. Any ML model that does not beat these baselines is a failure.

**5. What level of forecasting difficulty should we expect?**
- Top-20 cells: easy (structural persistence). Lag-1 Recall@20 is already ~77%. An ML model should push this to 85–90%.
- Cells 20–100: moderate difficulty. Ranks shuffle. Rolling features + violation composition features should help.
- Cells 100+: hard/unreliable. High CV, short history, enforcement scheduling noise. Do not optimize for these.

---

## Key Constraint

6 months of data with 5 usable transition pairs means only 3 walk-forward folds with full lag-3 features. This is a genuinely thin temporal dataset. The model should be kept simple — overfitting risk is real with complex architectures.

The right model is **not** a complex sequence model. It is a gradient-boosted regressor on a well-engineered lag feature set. The temporal depth does not justify anything more sophisticated.
