"""GET /health — liveness and readiness check."""
from datetime import datetime, timezone
from fastapi import APIRouter

from app.schemas.health import HealthResponse
from app.services.file_service import store
from app.services.model_service import model_state
from app.core.settings import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health() -> HealthResponse:
    """
    Returns backend status, model availability, and file loading status.
    Use this endpoint to verify the API is alive before making data requests.
    """
    all_ok = store.files_loaded and len(store.missing_files) == 0
    return HealthResponse(
        status="ok" if all_ok else "degraded",
        timestamp=datetime.now(timezone.utc),
        backend_version=settings.BACKEND_VERSION,
        environment=settings.BACKEND_ENV,
        model_loaded=model_state.loaded,
        files_loaded=store.files_loaded,
        missing_files=store.missing_files,
    )
