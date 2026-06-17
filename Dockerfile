# Hugging Face Docker Space entry point
# Build context: repo root
# HF default port: 7860

FROM python:3.11-slim AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends gcc libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /install /usr/local
COPY backend/ /app/
COPY outputs/ /app/data/outputs/
COPY backend/app/models/ /app/app/models/

ENV BACKEND_ENV=production
ENV OUTPUT_DIR=/app/data/outputs
ENV MODEL_DIR=/app/app/models
ENV LOG_LEVEL=INFO
ENV CORS_ORIGINS=*

EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
