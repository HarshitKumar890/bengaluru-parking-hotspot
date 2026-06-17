# Backend Summary — Bengaluru Parking Hotspot Intelligence API

**Project:** AI-Powered Parking Hotspot Forecasting and Congestion Risk Intelligence for Bengaluru
**Framework:** FastAPI · Python 3.11
**Status:** ✅ All 12 endpoints verified — 200 OK against real data

---

## 1. What Was Built

A production-style FastAPI backend that reads from precomputed ML and analytics
output files and exposes them as a clean, typed JSON API for a frontend dashboard.

**The backend does NOT:**
- Retrain or redesign the model
- Re-run data cleaning or feature engineering per request
- Invent or fake any data
- Claim general traffic congestion prediction

**The backend DOES:**
- Load 14 precomputed CSV outputs at startup into memory
- Serve them through 12 REST endpoints with filtering, sorting, and pagination
- Gracefully handle missing files and missing model (read-only mode)
- Return fully typed, NaN-safe JSON via Pydantic schemas

---

## 2. Directory Structure

```
backend/
├── app/
│   ├── main.py                         # App factory, lifespan, router registration
│   ├── config.py                       # Re-export of settings
│   ├── dependencies.py                 # Shared FastAPI dependency factories
│   │
│   ├── api/                            # Route handlers (thin — no business logic)
│   │   ├── health.py                   # GET /health
│   │   ├── summary.py                  # GET /summary
│   │   ├── hotspots.py                 # GET /hotspots
│   │   ├── forecast.py                 # GET /forecast
│   │   ├── patrol.py                   # GET /patrol-recommendations
│   │   ├── risk.py                     # GET /risk-zones
│   │   ├── explainability.py           # GET /feature-importance
│   │   ├── stations.py                 # GET /stations
│   │   ├── junctions.py               # GET /junctions
│   │   ├── stability.py               # GET /stability
│   │   └── download.py                # GET /download/{dataset_name}
│   │
│   ├── core/
│   │   ├── settings.py                 # Pydantic-settings config (env vars)
│   │   ├── logging.py                  # Structured logging setup
│   │   └── cors.py                     # CORS middleware configuration
│   │
│   ├── schemas/                        # Pydantic response models
│   │   ├── common.py                   # ErrorResponse, PaginationMeta, DataResponse
│   │   ├── health.py                   # HealthResponse
│   │   ├── summary.py                  # SummaryResponse
│   │   ├── hotspot.py                  # HotspotItem
│   │   ├── forecast.py                 # ForecastItem, ForecastResponse
│   │   ├── patrol.py                   # PatrolItem
│   │   ├── risk.py                     # RiskZoneItem
│   │   ├── explainability.py           # FeatureImportanceItem
│   │   ├── station.py                  # StationItem
│   │   ├── junction.py                 # JunctionItem
│   │   └── stability.py               # StabilityItem
│   │
│   ├── services/                       # All data logic lives here
│   │   ├── file_service.py             # CSV loader + in-memory DataStore
│   │   ├── model_service.py            # LightGBM pkl loader + ModelState
│   │   ├── forecast_service.py         # Forecast snapshot logic
│   │   ├── patrol_service.py           # Patrol data merge + filter
│   │   ├── risk_service.py             # Risk zone merge + filter
│   │   ├── analytics_service.py        # Station + junction analytics
│   │   └── explainability_service.py   # Feature importance ranking
│   │
│   ├── utils/
│   │   ├── io.py                       # pandas → JSON-safe dict conversion
│   │   ├── validators.py               # Query param validation helpers
│   │   └── transforms.py              # DataFrame filter/sort helpers
│   │
│   ├── models/                         # Place lightgbm_model.pkl here
│   └── data/                           # Optional — backend reads from outputs/ by default
│
├── requirements.txt
├── Dockerfile
├── .env.example
├── README.md
├── smoke_test.py                       # End-to-end endpoint verification script
└── BACKEND_SUMMARY.md                  # This file
```

**Total: 44 Python files** — all parse cleanly, all imports verified.

---

## 3. Data Loading — What Gets Loaded at Startup

The `DataStore` singleton in `file_service.py` holds all DataFrames in memory.
14 CSV files are loaded once at app startup via the FastAPI `lifespan` hook.

| Attribute | CSV File | Rows | Purpose |
|-----------|----------|------|---------|
| `patrol` | `enhanced_patrol_priority.csv` | 606 | Full patrol priority ranking with model predictions |
| `risk_labels` | `congestion_risk_labels.csv` | 606 | Congestion risk score + category per cell |
| `risk_table` | `hotspot_risk_table.csv` | 606 | Risk table with station + location data |
| `top20` | `top20_patrol_recommendations.csv` | 20 | Top 20 patrol deployment cells |
| `stability` | `hotspot_stability_labels.csv` | 1,391 | Stability class + time-series stats per cell |
| `feat_imp` | `feature_importance.csv` | 45 | LightGBM split-based feature importances |
| `model_cmp` | `model_comparison_table.csv` | 25 | Cross-fold model comparison metrics |
| `fold_preds` | `fold_predictions.csv` | 4,401 | Per-fold predictions from all models |
| `stations` | `eda_station_rankings.csv` | 54 | Station-level analytics |
| `junctions` | `eda_junction_rankings.csv` | 168 | Junction-level analytics |
| `heatmap` | `congestion_risk_heatmap.csv` | 540 | Congestion risk heatmap data |
| `explanations` | `top50_risk_explanations.csv` | 50 | Human-readable risk explanation text |
| `apr_norm` | `april_normalization_report.csv` | 606 | April partial-month normalization factors |
| `ensemble` | `ensemble_search_results.csv` | 12 | Ensemble weight search results |

**Path resolution:** `OUTPUT_DIR` defaults to `<project_root>/outputs/` automatically.
No file copying needed — just run from `backend/`.

---

## 4. API Endpoints — Complete Reference

All list endpoints return a consistent JSON envelope:
```json
{
  "meta": { "total": 606, "returned": 5, "limit": 5 },
  "data": [ ... ]
}
```

---

### GET /health

**Purpose:** Liveness and readiness check.

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"ok"` or `"degraded"` |
| `timestamp` | datetime | UTC timestamp |
| `backend_version` | string | From settings |
| `environment` | string | development / production |
| `model_loaded` | bool | Whether LightGBM pkl is present |
| `files_loaded` | bool | Whether all CSVs loaded at startup |
| `missing_files` | list | Names of any CSVs that failed to load |

**Sample response:**
```json
{
  "status": "ok",
  "timestamp": "2026-06-17T08:17:00Z",
  "backend_version": "1.0.0",
  "environment": "development",
  "model_loaded": false,
  "files_loaded": true,
  "missing_files": []
}
```

---

### GET /summary

**Purpose:** Dashboard overview metrics — all derived from preloaded DataFrames, no computation overhead.

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `total_violations` | int | Sum of all cases across stations |
| `total_spatial_cells` | int | Unique grid cells in stability table |
| `persistent_hotspots` | int | Cells with `stability_class = Persistent` |
| `seasonal_hotspots` | int | Cells with `stability_class = Seasonal` |
| `sporadic_hotspots` | int | Cells with `stability_class = Sporadic` |
| `critical_risk_zones` | int | Cells with `congestion_risk_category = Critical` |
| `high_risk_zones` | int | Cells with `congestion_risk_category = High` |
| `best_model_name` | string | Top model from comparison table |
| `best_recall_at_20` | float | Best Recall@20 from primary fold |
| `top_police_station` | string | Station with highest case volume |
| `top_junction` | string | Junction with highest case volume |
| `april_normalization_factor` | float | Median normalization factor for April |
| `total_patrol_cells` | int | Total cells in enhanced patrol table |
| `top20_patrol_cells` | int | Cells in top-20 patrol list |

---

### GET /hotspots

**Purpose:** Map data for all 606 spatial hotspot cells.

**Query parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | 200 | Max rows (1–1000) |
| `station` | string | — | Filter by police station (case-insensitive) |
| `risk_category` | string | — | Critical / High / Medium / Low |
| `stability_class` | string | — | Persistent / Seasonal / Sporadic |
| `min_prediction` | float | — | Minimum forecasted violation count |

**Data source:** `hotspot_risk_table.csv` + merged stability class from `hotspot_stability_labels.csv`

**Key response fields per record:** `spatial_cell_id`, `cell_lat`, `cell_lon`, `forecasted_count`, `police_station`, `congestion_risk_score`, `congestion_risk_category`, `priority_score`, `patrol_rank`, `stability_class`, `recurrence`

---

### GET /forecast

**Purpose:** Latest parking hotspot forecast snapshot.

**Query parameters:** `limit`, `station`, `risk_category`

**Important:** This endpoint returns the precomputed April 2024 forecast produced
by the LightGBM pipeline. Per-request live inference is not implemented because
the feature engineering requires the full cleaned dataset context.

**Response envelope (non-standard — includes metadata):**

| Field | Description |
|-------|-------------|
| `model_loaded` | Whether the LightGBM pkl file is present |
| `snapshot_note` | Human-readable explanation of the data source |
| `total` | Total matching records |
| `returned` | Records in response |
| `data` | Array of forecast records |

**Key fields per record:** `patrol_rank`, `pred_lgbm`, `pred_rolling`, `pred_lag1`, `forecasted_count`, `ranking_basis`, `congestion_risk_score`, `congestion_risk_category`

---

### GET /patrol-recommendations

**Purpose:** Top patrol deployment cells with enriched risk and explanation data.

**Default limit: 20** (the top-20 list). Max: 200.

**Query parameters:** `limit`, `station`, `risk_category`, `stability_class`, `min_prediction`

**Data sources:** `top20_patrol_recommendations.csv` (primary) → merged with `congestion_risk_labels.csv` and `top50_risk_explanations.csv`

**Key fields:** `patrol_rank`, `spatial_cell_id`, `cell_lat`, `cell_lon`, `predicted_count`, `priority_score`, `police_station`, `stability_class`, `recurrence`, `cv`, `trend_slope`, `congestion_risk_score`, `congestion_risk_category`, `risk_explanation`

---

### GET /risk-zones

**Purpose:** Cells ranked by parking-induced congestion risk score.

**Query parameters:**

| Param | Description |
|-------|-------------|
| `limit` | Max rows (default 100) |
| `category` | Critical / High / Medium / Low |
| `station` | Filter by police station |
| `min_risk_score` | Float 0.0–1.0 |

**Data source:** `hotspot_risk_table.csv` + merged station/lat-lon from patrol table + explanation text

**Sorted by:** `congestion_risk_score` descending

---

### GET /feature-importance

**Purpose:** LightGBM split-based feature importance rankings.

**Query parameters:**

| Param | Description |
|-------|-------------|
| `limit` | Max features to return (default 30) |
| `sort_order` | `asc` or `desc` (default `desc`) |

**Data source:** `feature_importance.csv` (45 features)

**Fields:** `rank`, `feature`, `importance` (raw split count), `importance_pct` (% of total)

---

### GET /stations

**Purpose:** Police station analytics enriched with active hotspot cell counts.

**Query parameters:** `limit` (default 50), `sort_by` (default `total_cases`)

**Data source:** `eda_station_rankings.csv` (54 stations) + merged cell counts from stability table

**Key fields:** `police_station`, `total_cases`, `unique_vehicles`, `approval_rate_pct`, `rejection_rate_pct`, `unresolved_rate_pct`, `avg_response_min`, `median_response_min`, `p95_response_min`, `avg_validation_min`, `peak_hour_pct`, `ops_score`, `volume_rank`, `n_active_hotspot_cells`

---

### GET /junctions

**Purpose:** Junction-level case volume and workflow analytics.

**Query parameters:** `limit` (default 50), `sort_by` (default `total_cases`)

**Data source:** `eda_junction_rankings.csv` (168 junctions)

**Key fields:** `junction_name`, `total_cases`, `unique_vehicles`, `n_approved`, `n_rejected`, `avg_response_min`, `peak_hour_violations`, `peak_hour_pct`, `n_recurrent`, `approval_rate_pct`, `volume_rank`

---

### GET /stability

**Purpose:** Hotspot stability classifications derived from 6-month time series.

**Query parameters:** `limit` (default 200), `stability_class`, `station`

**Data source:** `hotspot_stability_labels.csv` (1,391 cells) — monthly count columns stripped for clean output

**Sorted by:** `recurrence` descending

**Key fields:** `spatial_cell_id`, `stability_class`, `recurrence`, `mean_monthly`, `std_monthly`, `cv`, `trend_slope`, `n_active`, `cell_lat`, `cell_lon`, `police_station`

**Stability classes:**
- `Persistent` — high recurrence, low variance, present most months
- `Seasonal` — moderate recurrence with temporal patterns
- `Sporadic` — low recurrence, high variance

---

### GET /download/{dataset_name}

**Purpose:** Download any allowed precomputed CSV as a file attachment.

**Security:** Only filenames in the `SAFE_DOWNLOADS` allowlist are accessible.
Path traversal attempts (`../`, `\`) are rejected with 400.

**Allowed files (21 total):** All 14 loaded CSVs plus `window_granularity_comparison.csv`, `severity_forecasting_comparison.csv`, `spatial_feature_ablation.csv`, `feature_group_ablation.csv`, `risk_weight_sensitivity.csv`, `violation_frequency.csv`, `offence_frequency.csv`

**GET /download** (no filename) — returns the full list of downloadable datasets as JSON.

---

## 5. Service Layer Architecture

API route files are intentionally thin — they only parse query params, call validators,
and call a service function. All data logic lives in services.

```
API route  →  validator  →  service  →  DataStore (in-memory)  →  utils/io  →  JSON
```

### file_service.py — DataStore

- Singleton class `DataStore` holds all 14 DataFrames as class attributes
- `load_all_files()` called once in `lifespan` — never on a request path
- Missing files are logged as warnings and appended to `store.missing_files`
- Server never crashes on missing files

### model_service.py — ModelState

- `ModelState` holds the loaded model and a `loaded: bool` flag
- `load_model()` tries to load `lightgbm_model.pkl` from `MODEL_DIR`
- If absent → logs warning, sets `loaded = False`, server continues normally
- `/forecast` checks `model_state.loaded` and adjusts its `snapshot_note` accordingly

### forecast_service.py

- Returns the `enhanced_patrol_priority.csv` table as the forecast (it IS the model output)
- Merges congestion risk scores before returning
- Clear `snapshot_note` string explains the precomputed nature to the frontend

### patrol_service.py

- Starts from `top20_patrol_recommendations.csv`
- LEFT JOINs congestion risk scores + explanation text
- Falls back to full `enhanced_patrol_priority.csv` if top20 is missing

### risk_service.py

- Starts from `hotspot_risk_table.csv`
- LEFT JOINs station name and lat/lon from patrol table if missing
- LEFT JOINs explanation text from `top50_risk_explanations.csv`
- Sorted by risk score descending

### analytics_service.py

- `get_stations()` enriches station rows with `n_active_hotspot_cells` by counting cells per station in the stability table
- `get_junctions()` passes through junction data directly with optional sorting

### explainability_service.py

- Sorts by `importance` value and inserts a sequential `rank` column before returning

---

## 6. Utils Layer

### utils/io.py — df_to_records()

The single most important safety function in the codebase.

- Converts `pd.DataFrame` → `list[dict]` via `to_dict(orient="records")`
- Sanitizes every value: `NaN` → `None`, `Inf` → `None`, numpy scalar types → Python natives
- Rounds floats to 6 decimal places
- Ensures the frontend never receives `NaN`, `Infinity`, or numpy int64/float64 objects

### utils/validators.py

- `validated_limit(limit)` — raises HTTP 422 if outside 1–1000
- `validated_risk_category(cat)` — normalizes case, validates against `{Critical, High, Medium, Low}`
- `validated_stability_class(cls)` — validates against `{Persistent, Seasonal, Sporadic}`
- `validated_sort_order(order)` — validates `asc` / `desc`
- All raise `HTTPException(422)` with descriptive messages on bad input

### utils/transforms.py

- `filter_by_station(df, station)` — case-insensitive string match
- `filter_by_risk_category(df, cat)` — case-insensitive match on `congestion_risk_category`
- `filter_by_stability_class(df, cls)` — case-insensitive match on `stability_class`
- `filter_min_value(df, col, min_val)` — numeric threshold filter
- `sort_df(df, col, ascending)` — safe sort (no-op if column absent)

---

## 7. Configuration System

`app/core/settings.py` uses `pydantic-settings` with environment variable override.

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_ENV` | `development` | Environment tag, shown in /health |
| `BACKEND_VERSION` | `1.0.0` | Version string, shown in /health and OpenAPI |
| `OUTPUT_DIR` | `<project_root>/outputs` | Path to CSV outputs directory |
| `MODEL_DIR` | `backend/app/models` | Path to LightGBM pkl directory |
| `CORS_ORIGINS` | localhost:3000, :5173, :8080 | Comma-separated allowed origins |
| `LOG_LEVEL` | `INFO` | Python logging level |

Path defaults use `Path(__file__).resolve().parents[N]` — they resolve correctly
regardless of where `uvicorn` is invoked from, as long as the project structure is intact.

---

## 8. CORS Configuration

`app/core/cors.py` applies `CORSMiddleware` with:
- `allow_origins` from `settings.cors_origins_list` (split from `CORS_ORIGINS` env var)
- `allow_credentials = True`
- `allow_methods = ["*"]`
- `allow_headers = ["*"]`

For production, add the deployed frontend URL to `CORS_ORIGINS` in `.env`.

---

## 9. Error Handling

### Global handler (`main.py`)

All unhandled exceptions are caught by `@app.exception_handler(Exception)` and
return a structured JSON response:

```json
{
  "error": "internal_server_error",
  "message": "...",
  "endpoint": "/hotspots",
  "timestamp": "2026-06-17T08:17:00Z"
}
```

### Data unavailable (503)

`dependencies.py` provides `require_dataframe(attr)` — a dependency factory that
raises `HTTP 503` with a descriptive error if a required DataFrame is None.

### Invalid query params (422)

All query parameter validators in `utils/validators.py` raise `HTTP 422` with
actionable messages listing valid values.

### Download security (400 / 404)

The `/download` endpoint rejects path traversal and unknown filenames before
attempting any filesystem access.

---

## 10. Logging

`app/core/logging.py` configures `logging.basicConfig` on startup with:
- Format: `timestamp  LEVEL  logger_name  message`
- All hotspot API logs use the `hotspot_api` logger name
- `uvicorn.access` log level raised to WARNING (reduces noise)
- Log level controlled by `LOG_LEVEL` env var

What gets logged:
- Every CSV file loaded (name + row count)
- File loading summary (N/14 loaded)
- Model load success or read-only mode warning
- Startup and shutdown markers
- All unhandled exceptions with full traceback

---

## 11. Pydantic Schemas

Every endpoint has a typed Pydantic response model. All models use:
- `Optional[T]` for fields that may be absent in some CSV rows
- `Field(description=...)` for every field — appears in `/docs` automatically
- `populate_by_name = True` where column aliases are needed

**Schema inventory:**

| Schema | File | Used by |
|--------|------|---------|
| `HealthResponse` | schemas/health.py | GET /health |
| `SummaryResponse` | schemas/summary.py | GET /summary |
| `HotspotItem` | schemas/hotspot.py | GET /hotspots |
| `ForecastItem`, `ForecastResponse` | schemas/forecast.py | GET /forecast |
| `PatrolItem` | schemas/patrol.py | GET /patrol-recommendations |
| `RiskZoneItem` | schemas/risk.py | GET /risk-zones |
| `FeatureImportanceItem` | schemas/explainability.py | GET /feature-importance |
| `StationItem` | schemas/station.py | GET /stations |
| `JunctionItem` | schemas/junction.py | GET /junctions |
| `StabilityItem` | schemas/stability.py | GET /stability |
| `ErrorResponse`, `PaginationMeta` | schemas/common.py | shared |

---

## 12. Deployment

### Local

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger UI: `http://localhost:8000/docs`

### Docker

```bash
docker build -t hotspot-api .
docker run -p 8000:8000 \
  -v /path/to/outputs:/data/outputs \
  -v /path/to/models:/data/models \
  -e CORS_ORIGINS=https://your-frontend.com \
  hotspot-api
```

The Dockerfile uses a two-stage build (builder + slim runtime) and mounts data
externally via `/data/outputs` and `/data/models`.

### Render / Railway

Set start command:
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set env vars from `.env.example`. Mount or bake the `outputs/` CSV files.
Set `OUTPUT_DIR` to their mount path.

---

## 13. Smoke Test Results

Run: `python smoke_test.py` from the `backend/` directory.

```
OK  200  /health                            keys=[status, timestamp, ...]
OK  200  /summary                           keys=[total_violations, total_spatial_cells, ...]
OK  200  /hotspots?limit=5                  total=606  returned=5
OK  200  /forecast?limit=5                  keys=[model_loaded, snapshot_note, total, ...]
OK  200  /patrol-recommendations?limit=5    total=20   returned=5
OK  200  /risk-zones?limit=5                total=606  returned=5
OK  200  /feature-importance?limit=5        total=45   returned=5
OK  200  /stations?limit=5                  total=54   returned=5
OK  200  /junctions?limit=5                 total=168  returned=5
OK  200  /stability?limit=5                 total=1391 returned=5
OK  200  /download                          keys=[available_datasets]
OK  200  /download/feature_importance.csv   content-type=text/csv

Result: ALL PASSED
```

---

## 14. Frontend Integration Guide

### Recommended endpoint-to-page mapping

| Dashboard Page | Primary Endpoint | Secondary Endpoint |
|----------------|------------------|--------------------|
| Overview / KPI cards | `GET /summary` | `GET /health` |
| Hotspot map | `GET /hotspots` | `GET /risk-zones` |
| Patrol planner | `GET /patrol-recommendations` | `GET /forecast` |
| Risk analysis | `GET /risk-zones` | `GET /hotspots` |
| Station analytics | `GET /stations` | — |
| Junction analytics | `GET /junctions` | — |
| ML model insights | `GET /feature-importance` | `GET /forecast` |
| Stability explorer | `GET /stability` | — |
| Data export panel | `GET /download` + `GET /download/{name}` | — |

### Map rendering

Every record from `/hotspots`, `/patrol-recommendations`, `/risk-zones`, and `/stability`
includes `cell_lat` and `cell_lon` for direct use with Leaflet, MapboxGL, or Google Maps.

### Color coding by risk category

```
Critical  →  #d32f2f  (red)
High      →  #f57c00  (orange)
Medium    →  #fbc02d  (yellow)
Low       →  #388e3c  (green)
```

### Stability class icons

```
Persistent  →  solid circle / always-on indicator
Seasonal    →  half-circle / seasonal indicator
Sporadic    →  dashed circle / occasional indicator
```

---

*Generated: June 2026 | Bengaluru Parking Hotspot Intelligence Project*
