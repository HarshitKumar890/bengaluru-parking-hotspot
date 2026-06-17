# Bengaluru Parking Hotspot Intelligence — Backend API

FastAPI backend that serves precomputed ML and analytics outputs for the
**AI-Powered Parking Hotspot Forecasting and Congestion Risk Intelligence** dashboard.

> **Important framing**: This system models *parking-related* congestion risk — not
> general traffic congestion. Predictions come from a LightGBM model trained on
> Bengaluru traffic enforcement records (Nov 2023 – Apr 2024).

---

## Project Structure

```
backend/
├── app/
│   ├── main.py               # FastAPI app, lifespan, router registration
│   ├── config.py             # Re-export of settings
│   ├── dependencies.py       # Shared FastAPI dependencies
│   ├── api/                  # Route handlers (thin — no business logic)
│   │   ├── health.py
│   │   ├── summary.py
│   │   ├── hotspots.py
│   │   ├── forecast.py
│   │   ├── patrol.py
│   │   ├── risk.py
│   │   ├── explainability.py
│   │   ├── stations.py
│   │   ├── junctions.py
│   │   ├── stability.py
│   │   └── download.py
│   ├── core/                 # Settings, logging, CORS
│   ├── schemas/              # Pydantic response models
│   ├── services/             # All data loading and business logic
│   ├── models/               # Place lightgbm_model.pkl here
│   └── utils/                # io, validators, transforms
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

---

## Prerequisites

- Python 3.11+
- The `outputs/` directory from the ML pipeline (relative to the project root)
- Optionally: `app/models/lightgbm_model.pkl` for model metadata

---

## Local Installation

```bash
cd backend
pip install -r requirements.txt
```

---

## Running Locally

```bash
cd backend
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

ReDoc: `http://localhost:8000/redoc`

---

## Data Setup

The backend reads from the `outputs/` folder at the project root by default.
No copying required — just run from the `backend/` directory and the path resolves automatically.

To use a custom outputs path:

```bash
OUTPUT_DIR=/path/to/your/outputs uvicorn app.main:app --reload
```

To enable the LightGBM model (optional — backend works without it):

```bash
cp /path/to/lightgbm_model.pkl backend/app/models/lightgbm_model.pkl
```

---

## Environment Configuration

Copy `.env.example` to `.env` and adjust as needed:

```bash
cp .env.example .env
```

Key variables:

| Variable         | Default                          | Description                          |
|-----------------|----------------------------------|--------------------------------------|
| `BACKEND_ENV`   | `development`                    | Environment tag                      |
| `OUTPUT_DIR`    | `<project_root>/outputs`         | Path to CSV outputs directory        |
| `MODEL_DIR`     | `backend/app/models`             | Path to LightGBM model pkl directory |
| `CORS_ORIGINS`  | `http://localhost:3000,...`      | Allowed frontend origins (comma-sep) |
| `LOG_LEVEL`     | `INFO`                           | Logging verbosity                    |

---

## API Endpoints

| Method | Endpoint                    | Description                                      |
|--------|-----------------------------|--------------------------------------------------|
| GET    | `/health`                   | Liveness check — model + file status             |
| GET    | `/summary`                  | Dashboard summary metrics                        |
| GET    | `/hotspots`                 | Hotspot map data (filterable)                    |
| GET    | `/forecast`                 | Latest hotspot forecast snapshot                 |
| GET    | `/patrol-recommendations`   | Top patrol deployment cells                      |
| GET    | `/risk-zones`               | Parking-induced congestion risk zones            |
| GET    | `/feature-importance`       | LightGBM feature importance rankings             |
| GET    | `/stations`                 | Police station analytics                         |
| GET    | `/junctions`                | Junction analytics                               |
| GET    | `/stability`                | Hotspot stability labels                         |
| GET    | `/download/{dataset_name}`  | Download a precomputed CSV                       |
| GET    | `/download`                 | List all downloadable datasets                   |

### Common Query Parameters

Most list endpoints support:

- `limit` — max rows to return (default varies, max 1000)
- `station` — filter by police station name
- `risk_category` — `Critical` / `High` / `Medium` / `Low`
- `stability_class` — `Persistent` / `Seasonal` / `Sporadic`

---

## Frontend Integration

Point your frontend at `http://localhost:8000` in development.

For map rendering, use `GET /hotspots` — every record includes `cell_lat` and `cell_lon`.

Suggested data-to-page mapping:

| Page               | Primary endpoint            | Secondary endpoints              |
|--------------------|-----------------------------|----------------------------------|
| Overview dashboard | `/summary`                  | `/health`                        |
| Hotspot map        | `/hotspots`                 | `/risk-zones`                    |
| Patrol planner     | `/patrol-recommendations`   | `/forecast`                      |
| Risk analysis      | `/risk-zones`               | `/hotspots`                      |
| Station analytics  | `/stations`                 | —                                |
| Junction analytics | `/junctions`                | —                                |
| Model insights     | `/feature-importance`       | `/forecast`                      |
| Stability explorer | `/stability`                | —                                |

---

## Docker Deployment

```bash
# Build
docker build -t hotspot-api .

# Run (mount your outputs directory)
docker run -p 8000:8000 \
  -v /path/to/outputs:/data/outputs \
  -v /path/to/models:/data/models \
  -e CORS_ORIGINS=https://your-frontend.com \
  hotspot-api
```

---

## Deploying to Render / Railway

1. Push the `backend/` directory to a Git repo.
2. Set the start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add environment variables from `.env.example`.
4. Mount or upload the `outputs/` CSV files — set `OUTPUT_DIR` to their path.

> If your platform supports persistent disk (Render), mount the outputs directory
> and set `OUTPUT_DIR` accordingly. If not, bake the CSVs into the Docker image.

---

## Model Availability

The backend operates in two modes:

- **Full mode**: `app/models/lightgbm_model.pkl` exists → `/health` reports `model_loaded: true`
- **Read-only mode**: No pkl file → all endpoints still work using precomputed CSV outputs.
  `/forecast` returns the latest snapshot with a note explaining the model is unavailable.

The server **never crashes** due to a missing model file.
