"""LightGBM model loader. Server stays up if model is missing (read-only mode)."""
import joblib
from pathlib import Path
from typing import Optional, Any
from app.core.logging import logger
from app.core.settings import settings


class ModelState:
    model: Optional[Any] = None
    loaded: bool = False
    model_path: Optional[Path] = None


model_state = ModelState()


def load_model() -> None:
    path = settings.MODEL_DIR / "lightgbm_model.pkl"
    if not path.exists():
        logger.warning("LightGBM model not found at %s — running in read-only mode", path)
        return
    try:
        model_state.model = joblib.load(path)
        model_state.loaded = True
        model_state.model_path = path
        logger.info("LightGBM model loaded from %s", path)
    except Exception as exc:
        logger.error("Failed to load model: %s", exc)


def is_model_loaded() -> bool:
    return model_state.loaded
