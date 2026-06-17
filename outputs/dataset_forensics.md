# Dataset Forensics
## Bengaluru Parking Enforcement — Skeptical Signal Review

---

## 1. Strongest Predictive Signals

**Lag-1 cell count** is the dominant signal. Across all 5 consecutive month pairs, lag-1 Pearson r ranges from 0.906 to 0.954 (mean 0.932). This is not subtle — the cell that was busiest last month is almost certainly the busiest this month. This alone beats global-mean and predict-zero baselines by a factor of 2× on MAE (lag-1 MAE: 33.6 vs global-mean MAE: 63.3).

**Recurrence / persistence** is equally strong. All top-20 cells are active in all 6 months. Top-20 consecutive overlap is 14–17 out of 20 every single month transition. The hotspot map is structurally stable.

**Rolling 3-month mean** correlated at r=0.964 with March from Dec-Jan-Feb inputs. This is better than lag-1 alone for cells with moderate volatility.

**Junction presence** (50.5% of records have a named junction) carries lag-1 r=0.924–0.968 at junction level — slightly stronger than raw cell-level. Junction-level aggregation is more stable than raw grid cells.

---

## 2. Weakest Signals

**Peak-hour fraction**: Only 17.5% of records fall in defined peak windows (07:00–10:59, 17:00–20:59). The actual enforcement distribution is 51.1% night (00:00–05:59) and 30.1% evening (18:00–23:59). The peak-hour flag as defined captures the *wrong* peak for this enforcement dataset. It measures daytime commute windows but enforcement happens at night.

**Vehicle type mix**: Two-wheelers (SCOOTER + TWO WHEELER) dominate in virtually every cell type — no discriminating power between zone types.

**Approval/rejection ratio per cell**: 42% of records have null validation status, uniformly across cell sizes (top-100 cells pct_null = 0.417; low-count cells = 0.414). This signal is not meaningfully correlated with cell quality or type.

**Weekday distribution**: Monday–Sunday counts range only 38,931 to 46,863 — a 20% spread, not a strong predictor of spatial concentration.

---

## 3. Fields That Are Useless

| Field | Reason |
|---|---|
| `description` | 100% null |
| `action_taken_timestamp` | 100% null |
| `closed_datetime` | 100% null |
| `response_delay_minutes` | Derived from null timestamp; all null |
| `closure_delay_minutes` | Same |
| `center_code` | 11,260 nulls (3.8%); no behavioral meaning; administrative boundary code |
| `device_id` | Camera/device equipment tracking; not behavioral |
| `created_by_id` | Officer ID; 5 nulls; no behavioral pattern detectable without officer-level ground truth |
| `duplicate_group_id` | Post-hoc label; not a predictive feature |

---

## 4. Useful but Risky Fields

**`validation_status_final`**: Real variance (approval rates range 34%–55% across stations) but 42% null coverage makes any cell-level validation feature unreliable. Safe to use at station level; risky at cell level.

**`police_station`**: Strong administrative grouping but heavily confounded with geographic coverage territory. UPPARPET has 9 cells and 34,468 cases; ELECTRONIC CITY has 70 cells and far fewer total cases. Station is more a proxy for geography than for enforcement intensity.

**`junction_name`**: 49.5% of records have no junction. The "No Junction" → NA mapping was correct but creates a missing-value-based split that may not reflect true geography. Junctions were manually assigned; absence of junction name does not mean absence of junction.

**`scita_delay_minutes`**: Median 17.9 days. This is a system transmission metric, not a field measurement. High values reflect IT infrastructure delays, not enforcement quality.

---

## 5. Leakage Risks

**Month-T feature construction**: Any feature that uses information from month T to predict month T is leakage. The risk is real when computing station-level approval rates or junction-level aggregates without strict temporal cutoffs.

**Target encoding**: If `police_station` or `spatial_cell_id` is target-encoded using the full dataset mean count, it leaks future months into training. Must encode using training-months-only mean.

**April normalization**: April has ~10 days of data. If April is used as a test target with raw counts (not normalized by days), any model will appear to predict a "drop" — which is just the truncation. The model did not learn seasonality; the test label is wrong.

**Near-duplicate rows**: 10,926 near-duplicate records (~3.7%). If these remain in training, the model over-counts enforcement activity at specific cells. For count forecasting targets, near-duplicates inflate the target and the lag features equally — the leakage is symmetric and may be tolerable — but should be explicitly noted.

---

## 6. Administrative Artifacts vs. Behavioral Signals

| Administrative Artifact | Behavioral Signal |
|---|---|
| `police_station` (boundary assignment) | `station_approval_rate` (workflow quality) |
| `center_code` | `violation_type` (what offence occurred) |
| `device_id` | `junction_name` (physical location characteristic) |
| `created_by_id` | `created_hour` (when enforcement happened) |
| `data_sent_to_scita` flag | `recurrence_rate` (cell-level behavior pattern) |
| `scita_delay_minutes` | `lag-1 cell count` (strongest behavioral signal) |

The key error to avoid: treating `police_station` as a behavioral feature when it is primarily a spatial partition artifact. The station does not cause violations; it merely defines a reporting boundary.

---

## 7. Biases

**Enforcement bias (most critical)**: The dataset records where officers *went*, not where violations *occurred*. Low-count cells may be underenforced, not violation-free. The model trained on this data will learn enforcement patterns, not underlying parking behavior patterns. A prediction that "Cell X will have 100 violations next month" means "enforcement officers will visit Cell X 100 times next month" — which may be influenced by patrol habits rather than actual violations.

**Night-shift bias**: 51.1% of records fall between 00:00–05:59. This is a shift-scheduling artifact. Any model that treats enforcement time as a behavioral signal is modeling officer patrol schedules, not parking behavior. The "peak-hour" feature as defined (07:00–10:59 and 17:00–20:59) captures at most 17.5% of records and likely misses the actual enforcement intensity pattern.

**Station concentration bias**: The top 5 stations generate 24,635 cases/month on average; the bottom 5 generate 638. This 38.6× ratio means station-level features are dominated by a handful of high-volume stations. The model will be implicitly tuned to those stations' behavior.

**UPPARPET top-cell dominance**: UPPARPET police station has only 9 distinct spatial cells but 34,468 total cases. 60.3% of UPPARPET cases come from a single cell. This is not generalisable behavior — it reflects geographic concentration in UPPARPET's jurisdiction.

**Hotspot survivorship bias**: 853 cells were active in November 2023. Only 606 were active in April 2024 (which is truncated). 521 cells were active in both. 85 cells appeared for the first time in April. The persistence analysis is biased toward cells that were consistently active — cells that emerge or disappear cannot be predicted by lag features alone.

**Junction assignment bias**: Junctions are named for ~50% of records. The assignment appears to follow an officer-lookup from a predefined BTP junction list. Absence of a junction name does not mean the incident occurred outside a junction. It likely means the officer did not select a junction from the dropdown. This makes `is_junction_cell` a noisy signal — 50% cells missing it may still be near junctions.

**Validation bias**: Top-100 cells have pct_null=0.417 and pct_approved=0.698 (i.e., of the 58.3% validated records in high-count cells, 69.8% were approved). This is not a meaningful quality signal for those cells — it just means validated records in high-volume zones tend to be approved. The null 42% are uniformly distributed and uninformative.

**Duplicate bias**: 10,926 near-duplicates (3.7%). These inflate counts for cells where multiple officers attend the same violation. No correction was made to the target variable in the current pipeline — raw counts include near-duplicates.
