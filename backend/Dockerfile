# Build context: project root (Round 2/)
# docker build -f backend/Dockerfile -t hotspot-api .

# ── Stage 1: Build ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Runtime ─────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

# Backend source
COPY backend/ /app/

# Bake output CSVs — build context must be project root
COPY outputs/ /app/data/outputs/

# Bake model if present (optional — backend runs without it)
COPY backend/app/models/ /app/app/models/

ENV BACKEND_ENV=development
ENV OUTPUT_DIR=/app/data/outputs
ENV MODEL_DIR=/app/app/models
ENV LOG_LEVEL=INFO
ENV CORS_ORIGINS=http://localhost:3000

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
