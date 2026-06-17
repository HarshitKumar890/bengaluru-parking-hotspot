# Executive Decision Memo
## Bengaluru Parking Hotspot Intelligence — Build Decision

---

**1. What should we build?**

Build a next-window violation count forecasting model on the spatial cell × monthly panel. LightGBM with Poisson objective, 24 features, walk-forward validation on Folds 3–4. Evaluate with Recall@20 and Spearman ρ on top-100 cells. Output: ranked patrol priority table for the upcoming month.

The persistence and forecastability analyses confirm this is viable. Lag-1 r = 0.932, top-20 overlap = 77%, rolling mean r = 0.964 — the signal is real and strong.

---

**2. What should we NOT build?**

- Do not build a congestion prediction model. There is no traffic flow data. Any congestion claim is fabricated.
- Do not build a repeat-offender model. 84.7% of vehicles appear once; IDs are anonymized.
- Do not build a deep time-series model (LSTM, Transformer, etc.). 6 months and ~4,000 panel rows do not justify it.
- Do not report MAE across all 1,393 cells. Low-count cells swamp the metric and obscure what matters.

---

**3. What is the strongest story for judges?**

The city has a spatially concentrated, temporally persistent enforcement problem: top-1% of cells generate 20% of violations, and those same cells are hot every single month. A simple reactive patrol system misses this structure. The model quantifies the persistence, ranks cells by predicted next-month intensity, and produces a printable patrol priority list. The evaluation is rigorous: walk-forward temporal splits, Recall@K, and an honest comparison against the lag-1 persistence baseline.

That is the story. It is specific, supported by data, and operationally credible.

---

**4. What is the biggest technical risk?**

The lag-1 persistence baseline is already very strong. If the ML model achieves Recall@20 = 80% and lag-1 achieves 77%, the improvement is 3 cells. That is not impressive. The model must improve on rank ordering for the 20–100 range (where violation composition, severity mix, and station workflow features may add signal) or the ML component is redundant.

The fallback position: present the rule-based composite score + persistence analysis as the primary deliverable, and the ML model as an incremental improvement. This is defensible even if the improvement is small.

---

**5. What is the biggest opportunity?**

The violation composition and co-occurrence features are unexploited. The top co-occurrence pair (PARKING IN MAIN ROAD + WRONG PARKING: 15,641 co-occurrences) suggests some cells attract structurally more dangerous violations. A severity-weighted target (count × severity_score_lag1) rather than raw count may produce a more operationally useful ranking — one that prioritizes cells with dangerous violation mixes even if absolute count is moderate. This is a differentiation opportunity that no shallow EDA submission will have.

---

**6. What should happen next?**

1. Build `ml_hotspot_forecasting.py` — panel construction, feature engineering, LightGBM walk-forward, evaluation table
2. Normalize April counts before any use as target or lag feature
3. Exclude near-duplicates from target count aggregation (flag: is_near_duplicate=1)
4. Compute station-level features per fold (training months only — no leakage)
5. Report Recall@20 for: lag-1 baseline, rolling-mean baseline, rule-based score, LightGBM model
6. If LightGBM Recall@20 ≤ rolling-mean baseline on Fold 4, use rolling mean + rule-based score as final submission and explain why honestly

Do not skip step 6. Honesty about model performance versus baselines is the mark of a defensible project.
