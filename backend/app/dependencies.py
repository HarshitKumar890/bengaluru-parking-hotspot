"""
Shared FastAPI dependencies.
Provides the in-memory data store and model state to route handlers.
"""
from fastapi import HTTPException
from app.services.file_service import store
from app.services.model_service import model_state


def get_store():
    """Return the global DataStore instance."""
    return store


def get_model_state():
    """Return the global ModelState instance."""
    return model_state


def require_dataframe(attr: str):
    """
    Dependency factory — raises 503 if a required DataFrame is not loaded.
    Usage: df = Depends(require_dataframe("patrol"))
    """
    def _inner():
        df = getattr(store, attr, None)
        if df is None:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "data_unavailable",
                    "message": f"Dataset '{attr}' is not loaded. Check server startup logs.",
                },
            )
        return df
    return _inner
