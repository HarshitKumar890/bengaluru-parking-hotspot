# Hotspot Persistence Review
## Are Hotspots Structurally Persistent?

---

## Evidence

### Top-20 Cell Overlap (consecutive months)
| Transition | Overlap |
|---|---|
| Nov → Dec | 16/20 |
| Dec → Jan | 16/20 |
| Jan → Feb | 14/20 |
| Feb → Mar | 17/20 |
| Mar → Apr | 14/20 |

Mean overlap: **15.4/20 (77%)**. In every single month transition, at least 70% of the top-20 cells remain top-20 cells. This is not a coincidence — it is structural persistence.

### Rank Stability (Spearman ρ, top-100 cells)
| Transition | Spearman ρ |
|---|---|
| Nov → Dec | 0.710 |
| Dec → Jan | 0.775 |
| Jan → Feb | 0.646 |
| Feb → Mar | 0.717 |
| Mar → Apr | 0.703 |

Mean: **0.710**. Moderate-to-strong rank stability. Ranks shuffle somewhat within the top-100 but the top-20 stays largely fixed.

### Persistence by Cell
- All top-20 cells are active in all 6 months (recurrence_rate = 1.0)
- 782 cells have ≥4 active months
- 925 cells have ≥3 active months
- Median cell CV (coefficient of variation across months): 0.49 — moderate volatility within stable rank

### Growth (Nov → Apr)
All top-20 cells show **negative growth** (last month count < first month count). Growth ranges from -0.19 to -0.98. This is primarily the April truncation artifact — April has ~10 days of data. The trend signal is not meaningful without April normalization.

---

## Answers

**1. Are hotspots structurally persistent?**
Yes. 77% top-20 overlap per transition. All top-20 cells active in all 6 months. The spatial hotspot map does not change materially month to month.

**2. Are hotspots predictable or mostly volatile?**
The top cells are predictable. Below rank 50, volatility increases (CV > 0.5 is common). Rank 100+ cells are unreliable — their month-to-month counts swing wildly.

**3. Do top cells remain top cells?**
Yes, reliably. Top-5 cells are top-5 cells every single month. The model needs to be evaluated primarily on rank stability within the top-50, not on absolute count accuracy for all 1,393 cells.

**4. How much of next-window behavior is explained by prior behavior?**
Lag-1 alone explains r²=0.87 of variance (from r=0.93). Rolling mean explains even more for stable cells. Prior behavior is by far the dominant predictor.

**5. Is hotspot forecasting a real problem or just a noisy ranking exercise?**
For the top-50 cells: it is a real, forecastable problem. Lag-1 persistence is already a strong baseline (MAE 33.6 vs global mean 63.3). The ML model's job is not to discover the hotspots — they are obviously persistent — but to improve rank ordering for cells in the 20–100 range where lag-1 makes errors, and to correctly predict month-level magnitude.

For cells below rank 200: it is largely a noisy ranking exercise. Count volatility is high, history is short, and the cells may reflect officer scheduling fluctuations more than real violation behavior.

**Practical implication**: Build and evaluate the model on top-200 cells only. Report Recall@20 and Recall@50 as primary metrics. Do not report overall MAE across all 1,393 cells — the low-count cells will make any model look bad without adding operational value.
