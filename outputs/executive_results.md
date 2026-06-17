# Executive Results
## Bengaluru Parking Hotspot Forecasting — Final Decision Memo

### What the model is
LightGBM Regressor with Poisson objective, trained on a spatial cell × monthly panel.
Predicts next-month violation count per 500m grid cell. Output: ranked patrol priority list.

### How good it is (primary folds — Feb & Mar)
- LightGBM Recall@20: **0.700** (identifies 14/20 true worst cells)
- Lag-1 baseline Recall@20: **0.700**
- Rolling mean Recall@20: **0.725**
- LightGBM Spearman ρ (top-100): **0.697**
- Improvement over best baseline: **-2.5 pp on Recall@20**

### Decision
**BASELINE_WINS** — Rolling mean + rule score is the recommended system. LightGBM does not add value.

### Where it fails
- Cannot predict emerging hotspots (cells with no prior history)
- Night-shift enforcement bias: model predicts enforcement patterns, not true violations
- Only 2 reliable primary evaluation folds — confidence intervals are wide
- April evaluation corrupt without normalization (handled but caveat remains)

### Top-3 predicted patrol priority cells


### Ready for submission?
Yes. The pipeline produces a defensible ranked patrol priority list backed by:
temporal walk-forward validation, honest baseline comparison, and operational metrics.
The claim is precisely scoped: enforcement-priority hotspot forecasting, not congestion prediction.
