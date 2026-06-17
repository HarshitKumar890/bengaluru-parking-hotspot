"""
Bengaluru Parking Hotspot Intelligence — FastAPI Backend
Serves precomputed ML/analytics outputs for the dashboard frontend.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.settings import settings
from app.core.logging import setup_logging, logger
from app.core.cors import configure_cors
from app.services.file_service import load_all_files
from app.services.model_service import load_model

from app.api import (
    health,
    summary,
    hotspots,
    forecast,
    patrol,
    risk,
    explainability,
    stations,
    junctions,
    stability,
    download,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    setup_logging()
    logger.info("=== Bengaluru Parking Hotspot API starting (env=%s) ===", settings.BACKEND_ENV)
    load_all_files()
    load_model()
    logger.info("=== Startup complete — API ready ===")
    yield
    logger.info("=== API shutting down ===")


app = FastAPI(
    title="Bengaluru Parking Hotspot Intelligence API",
    description=(
        "Serves ML-based parking hotspot forecasts, congestion risk rankings, "
        "patrol recommendations, and spatial analytics for Bengaluru. "
        "All predictions are based on precomputed outputs from the LightGBM pipeline."
    ),
    version=settings.BACKEND_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

configure_cors(app)

# Register all routers
app.include_router(health.router, tags=["Health"])
app.include_router(summary.router, tags=["Dashboard"])
app.include_router(hotspots.router, tags=["Hotspots"])
app.include_router(forecast.router, tags=["Forecast"])
app.include_router(patrol.router, tags=["Patrol"])
app.include_router(risk.router, tags=["Risk"])
app.include_router(explainability.router, tags=["Explainability"])
app.include_router(stations.router, tags=["Stations"])
app.include_router(junctions.router, tags=["Junctions"])
app.include_router(stability.router, tags=["Stability"])
app.include_router(download.router, tags=["Download"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all error handler — never crash silently."""
    from datetime import datetime, timezone
    logger.error("Unhandled exception at %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": str(exc),
            "endpoint": str(request.url.path),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
