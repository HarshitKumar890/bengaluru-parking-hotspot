# Forensic Audit Report — Bengaluru Parking Hotspot Intelligence
**Date:** June 2026 | **Auditor:** Principal ML/Backend/MLOps Review

---

# CRITICAL ISSUES

---

[CRITICAL-1]
Problem: **Risk category value mismatch — backend validators vs actual CSV data.**
Pipeline produces: `CRITICAL`, `HIGH`, `MODERATE`, `LOW` (uppercase, MODERATE not Medium).
Backend `validators.py` checks against: `Critical`, `High`, `Medium`, `Low` (Title case, Medium not MODERATE).
Double failure: (1) case mismatch means `?risk_category=Critical` returns 0 results even though 153 CRITICAL cells exist.
(2) `MODERATE` never matches `Medium` — the 4th tier is completely unreachable.
All filter queries on `/hotspots`, `/risk-zones`, `/patrol-recommendations`, `/forecast` return empty when `risk_category` is supplied.
Impact: Every risk_category filter silently returns 0 results. Demo with category filter fails. Judge filters fail.
Fix: In `validators.py`, change `VALID_RISK_CATEGORIES` to `{"CRITICAL", "HIGH", "MODERATE", "LOW"}` and remove `.capitalize()` normalization. Apply `.upper()` instead of `.capitalize()` in `validated_risk_category()`. Update all schemas and README to show CRITICAL/HIGH/MODERATE/LOW.

---

[CRITICAL-2]
Problem: **Stability class mismatch — backend validates against wrong set.**
Actual CSV values: `Persistent`, `Volatile`, `Declining`, `Emerging`.
Backend `validators.py` `VALID_STABILITY_CLASSES`: `{"Persistent", "Seasonal", "Sporadic"}`.
`Seasonal` and `Sporadic` do not exist in any CSV. `Volatile`, `Declining`, `Emerging` cannot be filtered.
All `?stability_class=Volatile` queries return 422 validation error. All `?stability_class=Seasonal` queries return 0 results.
Impact: Every stability filter on `/hotspots`, `/stability`, `/patrol-recommendations` either errors or returns empty. Demo broken.
Fix: Change `VALID_STABILITY_CLASSES` to `{"Persistent", "Volatile", "Declining", "Emerging"}`. Update all schemas, README, and BACKEND_SUMMARY.md accordingly.

---

[CRITICAL-3]
Problem: **LightGBM model is never saved to disk anywhere in the pipeline.**
`ml_hotspot_forecasting.py` trains the model but contains zero `joblib.dump`, `pickle.dump`, or `save_model` calls.
`hotspot_v2_improvements.py` also contains zero model-save calls.
`backend/app/models/lightgbm_model.pkl` does not exist.
Backend runs in read-only mode permanently. The `/health` endpoint will always return `model_loaded: false`.
Impact: `/health` always shows degraded model status. Any judge or evaluator checking health will see model not loaded. Cannot demonstrate live model state.
Fix: Add `joblib.dump(last_model, OUT / "lightgbm_model.pkl")` in `ml_hotspot_forecasting.py` after `build_final_patrol_priority()`. Copy resulting pkl to `backend/app/models/`. Document this one-time step in README.

---

[CRITICAL-4]
Problem: **`hotspot_risk_table.csv` is sorted by `priority_score` DESC in the pipeline, but `priority_score` is not present in the file after rename.**
In `congestion_risk_layer.py part5_hotspot_risk_table()`, `congestion_risk_score_100` is renamed to `congestion_risk_score`. The `sort_values("priority_score")` call uses `priority_score` from `master` — but `master` was built from `enhanced_patrol_priority.csv` which does contain `priority_score`. This is fine.
However, `stability_class` is included in `cols` only if present in master — and master is a merge of `enhanced_patrol_priority` + `hotspot_stability_labels`. If the merge fails silently (no matching `spatial_cell_id`), `stability_class` will be absent from the risk table.
Impact: `/hotspots` endpoint returns records without `stability_class`. Stability filter on `/hotspots` operates on a joined column that may be fully NaN if IDs don't match.
Fix: Add explicit assertion after merge: `assert master['stability_class'].notna().sum() > 0, "Stability merge failed"`. Verify `spatial_cell_id` type consistency (str vs int) between all three source files.

---

# HIGH PRIORITY ISSUES

---

[HIGH-1]
Problem: **Fold 1 LGBM has `lgbm_valid=False` and `recall@20=1.0` (perfect score) — trained and tested on identical data.**
This 1.0 is stored in `model_comparison_table.csv` and loaded by the backend `/summary` endpoint.
`/summary` derives `best_recall_at_20` by filtering `is_primary=True` only, which correctly excludes Fold 1.
BUT the `model_comparison_table.csv` downloadable via `/download` contains the 1.0 row with no visible warning to judges examining the raw file.
Impact: Judge opens CSV, sees `recall@20 = 1.0` for LightGBM, flags fabricated results. Immediate credibility loss.
Fix: Add a `note` column to the comparison table for `lgbm_valid=False` rows: `"INVALID: trained and tested on same data (only 1 training month available)"`. This is already flagged in logs but not in the artifact.

---

[HIGH-2]
Problem: **April normalization factor is hardcoded as `APRIL_DAYS = 8` in `ml_hotspot_forecasting.py` but dynamically computed as `observed_days` in `hotspot_v2_improvements.py part2_april_normalization()`.**
If `observed_days` differs from 8 (it was confirmed as 8 in the run), there is no discrepancy now. But the hardcoded value creates a silent inconsistency risk if data is updated.
More critically: `april_normalization_report.csv` shows `normalization_factor = 3.75` (30/8). The `/summary` endpoint returns this as `april_normalization_factor`. This is correct — but the `ranking_basis` column in patrol priority says `"April-2024-proxy (last observed window)"`. The forecast is labeled as April 2024 but is actually a normalized proxy. This framing is factually accurate but needs to be surfaced clearly in the frontend to prevent judge confusion.
Impact: Mild — framing risk during presentation Q&A.
Fix: Ensure `/forecast` response and frontend display prominently show `ranking_basis: "April-2024-proxy (last observed window)"`. Already in API response — verify frontend renders it.

---

[HIGH-3]
Problem: **Docker image does not include output CSVs — mounts them as external volume.**
`Dockerfile` sets `OUTPUT_DIR=/data/outputs` and creates mount point but does not `COPY outputs/ /data/outputs`.
On Render/Railway, persistent disk may not be available or may require manual upload of 14 CSV files.
Impact: Docker deployment is non-functional without separate CSV provisioning. Demo deployment fails if judge tries to run the Docker image standalone.
Fix: Either (A) `COPY outputs/ /app/outputs` in Dockerfile and set `ENV OUTPUT_DIR=/app/outputs` — bakes CSVs into image (increases size ~5MB, acceptable). Or (B) add explicit note in README that CSVs must be mounted and provide exact `docker run -v` command. Option A is safer for demo.

---

[HIGH-4]
Problem: **`httpx` is not in `requirements.txt` but is required by FastAPI's `TestClient` (used in `smoke_test.py`).**
`smoke_test.py` is included in the repo. Any judge or evaluator running `smoke_test.py` after fresh install will get `ImportError: No module named 'httpx'`.
Impact: Smoke test fails on fresh environment. Looks unprofessional.
Fix: Add `httpx==0.27.0` to `requirements.txt` or create a separate `requirements-dev.txt`.

---

[HIGH-5]
Problem: **`/summary` endpoint's `total_violations` is computed as sum of `total_cases` from `eda_station_rankings.csv` (54 stations × their case counts).**
Station rankings aggregate by station. If any violations are unassigned to a station (NULL `police_station`), they are excluded from the sum. More importantly, this double-counts cases that may appear in both station and junction aggregations in the EDA.
The cleaned parquet has a definitive row count. The station sum may under-report total violations.
Impact: Dashboard KPI shows wrong total violation count. Judges may compare against raw data.
Fix: Add `spatial_cells.csv` row count or fold prediction count as a cross-check. Alternatively compute total from `fold_predictions.csv` actual counts for the training dataset size, or note the caveat explicitly in the API response field description.

---

# MEDIUM PRIORITY ISSUES

---

[MEDIUM-1]
Problem: **Inner validation for LGBM early stopping uses `sample(frac=0.2, random_state=42)` — a random split of the inner training fold.**
The inner fold is already temporally safe (inner_pred is a past month). The random 20% split for early stopping is acceptable in practice but technically means the validation set for early stopping is not strictly temporal.
Impact: Marginal — early stopping may fire slightly too early or late. Recall@20 error is within noise.
Fix: If defending to judges: use last chronological month of inner_train as early stopping val instead of random split. Not required for submission but is a cleaner methodology claim.

---

[MEDIUM-2]
Problem: **`require_dataframe()` dependency factory in `dependencies.py` is defined but never used by any route handler.**
All routes access `store.X` directly through service functions. The dependency is dead code.
Impact: None on functionality. Confusing for code reviewers.
Fix: Either use it in route handlers via `Depends(require_dataframe("patrol"))` or remove it. Not critical for submission.

---

[MEDIUM-3]
Problem: **`/stations` and `/junctions` endpoints accept a free-text `sort_by` parameter with no validation.**
A request like `?sort_by=malicious_column` silently falls back (no-op in `sort_df()`) but could be used to probe column names or trigger unexpected behavior.
Impact: Low security risk — worst case is unsorted results. No injection possible since it's just a column lookup.
Fix: Whitelist valid sort columns per endpoint (e.g., `sort_by` must be one of `["total_cases", "ops_score", "approval_rate_pct"]`).

---

[MEDIUM-4]
Problem: **`congestion_risk_layer.py` explanation generator (`part7_explanations`) checks for stability class `"Volatile"` and `"Emerging"` but the explanation text references `"Declining"` with "enforcement may be taking effect" framing.**
`"Declining"` is a real class (82 cells in stability CSV). The explanation text is correct.
But the risk explanation for `"Volatile"` says "irregular enforcement activity" — which conflates enforcement inconsistency with actual parking behavior. Judges may challenge this as confounding.
Impact: Low — presentation risk only.
Fix: Change `"Volatile"` explanation to: `"Hotspot with high variance in monthly violations — enforcement activity is irregular or violations are seasonally clustered."`

---

[MEDIUM-5]
Problem: **`persistence_score.1` duplicate column in `enhanced_patrol_priority.csv`.**
The CSV has both `persistence_score` and `persistence_score.1` — a pandas auto-rename artifact from a duplicate column during DataFrame assembly in `hotspot_v2_improvements.py`.
Impact: Frontend receives a confusing duplicate column. Minor.
Fix: In the v2 pipeline, identify the double-assignment of `persistence_score` and deduplicate before writing CSV.

---

[MEDIUM-6]
Problem: **`/forecast` endpoint `snapshot_note` correctly says the forecast is precomputed, but the Swagger `/docs` description says "optionally support live inference."**
The `forecast.py` API docstring contains: "If the model is loaded, optionally support live inference" — copied from the spec but never implemented. This is misleading in the interactive docs.
Impact: Judge reads docs, tries to trigger live inference, gets confused.
Fix: Update the `/forecast` route docstring to: "Returns the April 2024 precomputed forecast snapshot. Live per-request inference is not available. The `model_loaded` flag indicates model presence only."

---

# VERIFIED CORRECT

✓ Walk-forward temporal validation structure
Reason: Folds use strictly past months as training data. No future data leaks into features. `pred_month` data is used ONLY as target label, confirmed by code inspection of `build_features_for_fold()`.

✓ April normalization applied before lag feature construction
Reason: `normalize_april()` is called before `run_walk_forward()`. Fold 5 uses normalized April counts as both features (lag1) and target. Normalization factor 3.75 is consistent across pipeline.

✓ Station features computed per-fold from training months only
Reason: `add_station_features()` filters `valid[valid["ym"].isin(train_months)]` before any aggregation. No test-month data enters station features.

✓ Near-duplicate exclusion from targets
Reason: `is_near_duplicate != 1` filter applied to count aggregation. Near-dups excluded from `target` column construction.

✓ FastAPI lifespan startup pattern
Reason: Uses `asynccontextmanager` lifespan correctly. `load_all_files()` and `load_model()` called at startup, not at request time.

✓ NaN/Inf sanitization in API responses
Reason: `utils/io.py df_to_records()` converts all NaN/Inf to None, numpy scalars to Python natives, before JSON serialization.

✓ Model graceful degradation (read-only mode)
Reason: `load_model()` catches missing file with warning, sets `loaded=False`, server continues. No crash. All CSV-based endpoints functional.

✓ Download endpoint path traversal protection
Reason: `download.py` rejects `"/"`, `"\\"`, `".."` in filename. Only allowlisted filenames served.

✓ CORS configuration (environment-driven)
Reason: Origins loaded from `CORS_ORIGINS` env var. Default covers common local dev ports. No hardcoded single origin.

✓ Congestion risk score formula (defensible)
Reason: Four-component composite (count 40%, persistence 25%, junction 20%, severity 15%) with min-max normalization. Weight sensitivity analysis confirms top-20 stability across weight sets. Explicitly labeled as proxy indicator throughout codebase.

✓ Theme framing — no overclaiming
Reason: `congestion_risk_layer.py` contains explicit scientific disclaimer at top. `part8_theme_alignment()` documents exactly what is and is not claimed. `part10_final_summary()` has a judge-facing table with correct claim status.

✓ Evaluation metrics (Recall@K, Spearman, NDCG, MAE)
Reason: Implementations verified against standard definitions. `recall_at_k()` correctly computes set intersection of top-K actual vs top-K predicted. No off-by-one errors found.

✓ Fold 1 LGBM overfit correctly flagged
Reason: `lgbm_valid=False` set and logged. Primary fold filter correctly excludes Fold 1 from metric averages. `/summary` best_recall_at_20 uses `is_primary=True` filter.

✓ CORS credentials + wildcard methods
Reason: `allow_credentials=True` with specific origins list (not `"*"`) is valid. FastAPI/Starlette will reject `allow_origins=["*"]` + `allow_credentials=True` combination — this project correctly uses a specific origins list.

---

# FINAL DECISION

**FIX_BEFORE_DEPLOY**

---

## Top 5 Actions by Impact

**1. Fix risk_category case + MODERATE/Medium mismatch (CRITICAL-1)**
Every risk category filter query is broken. 5-minute fix in `validators.py`. Highest demo impact.

**2. Fix stability_class validator set (CRITICAL-2)**
Every stability filter query either errors (422) or returns empty. 2-minute fix in `validators.py`. Directly breaks map filtering demo.

**3. Save LightGBM model to disk (CRITICAL-3)**
Add `joblib.dump()` call at end of `ml_hotspot_forecasting.py`, copy pkl to `backend/app/models/`. Without this, `/health` permanently shows `model_loaded: false`. 10-minute fix.

**4. Add `httpx` to `requirements.txt` and bake CSVs into Docker image (HIGH-4 + HIGH-3)**
Fresh installs fail smoke test. Docker standalone fails. Combined 5-minute fix.

**5. Add note column to `model_comparison_table.csv` for Fold 1 LGBM row (HIGH-1)**
Prevents judges from seeing `recall@20=1.0` without explanation. Protects evaluation credibility during raw data inspection.
