# Bengaluru Parking Hotspot Intelligence

AI-powered parking hotspot forecasting and congestion risk system for Bengaluru.
Built for Flipkart Grid Round 2.

> **Scientific framing**: This system predicts parking hotspots and estimates
> *parking-induced* congestion risk. It does NOT predict actual traffic congestion.

---

## What's in this repo

```
Round 2/
├── backend/                    # FastAPI backend (production-ready)
│   ├── app/                    # Application code
│   │   ├── api/                # 11 route handlers
│   │   ├── core/               # Settings, logging, CORS
│   │   ├── schemas/            # Pydantic response models
│   │   ├── services/           # Data + model loading logic
│   │   ├── utils/              # IO, validators, transforms
│   │   ├── models/             # lightgbm_model.pkl
│   │   └── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
├── outputs/                    # Precomputed ML artifacts (served by backend)
├── ml_hotspot_forecasting.py   # V1 LightGBM pipeline
├── hotspot_v2_improvements.py  # V2 ensemble + ablation pipeline
├── congestion_risk_layer.py    # Risk scoring layer
├── data_audit_and_cleaning.py  # Data cleaning pipeline
└── eda_insights.py             # EDA pipeline
```

---

## Model Performance (V2)

| Metric | Value |
|--------|-------|
| LightGBM Recall@20 | **0.775** |
| Best Ensemble Recall@50 | **0.820** (EnsH: 50%Roll+30%Lag1+20%Sev) |
| Evaluation | Walk-forward temporal, 2 primary folds (Feb + Mar) |

---

## Local Run

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API: `http://localhost:8000`
Docs: `http://localhost:8000/docs`

---

## Docker Run

Build from **project root** (`Round 2/`):

```bash
docker build -f backend/Dockerfile -t hotspot-api .
docker run -p 8000:8000 -e CORS_ORIGINS=http://localhost:3000 hotspot-api
```

API: `http://localhost:8000`

---

## Environment Variables

| Variable | Default | Required |
|----------|---------|----------|
| `BACKEND_ENV` | `development` | No |
| `OUTPUT_DIR` | auto-resolved | No |
| `MODEL_DIR` | auto-resolved | No |
| `CORS_ORIGINS` | `http://localhost:3000,...` | For prod |
| `LOG_LEVEL` | `INFO` | No |

Copy `backend/.env.example` to `backend/.env` for local overrides.

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Status, model loaded, files loaded |
| `GET /summary` | Dashboard KPIs |
| `GET /hotspots` | Map data (all 606 cells with lat/lon) |
| `GET /forecast` | Latest forecast snapshot |
| `GET /patrol-recommendations` | Top-20 patrol cells |
| `GET /risk-zones` | Congestion risk zones |
| `GET /feature-importance` | LightGBM feature rankings |
| `GET /stations` | Station analytics |
| `GET /junctions` | Junction analytics |
| `GET /stability` | Hotspot stability labels |
| `GET /download/{name}` | CSV export |

All list endpoints support `limit`, `station`, `risk_category` filters.
Risk categories: `CRITICAL / HIGH / MODERATE / LOW`
Stability classes: `Persistent / Volatile / Declining / Emerging`

---

## Deploy to Render

1. Push this repo to GitHub.
2. New Web Service → connect repo.
3. Build command: `pip install -r backend/requirements.txt`
4. Start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Root directory: leave blank (project root).
6. Set env vars: `OUTPUT_DIR=/opt/render/project/src/outputs`, `MODEL_DIR=/opt/render/project/src/backend/app/models`, `CORS_ORIGINS=https://your-frontend.com`

---

## Deploy to Hugging Face Docker Space

1. Create a new Space → Docker SDK.
2. Push this repo (or copy `backend/` + `outputs/` into the Space repo).
3. The `backend/Dockerfile` is the entry point — HF uses it automatically if placed at root, OR set `Dockerfile` path in Space settings.
4. Set Space secrets: `CORS_ORIGINS`, `LOG_LEVEL`.
5. Port: `7860` (HF default) — update `EXPOSE` and CMD port, or set `APP_PORT=7860`.

For HF, update CMD:
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

---

## Verify after deploy

```bash
curl https://your-deployed-url/health
curl https://your-deployed-url/summary
curl "https://your-deployed-url/hotspots?limit=5&risk_category=CRITICAL"
```
