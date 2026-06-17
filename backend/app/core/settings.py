"""Central configuration via environment variables with sensible local defaults."""
from pathlib import Path
from pydantic_settings import BaseSettings

# Resolve paths relative to this file:
# backend/app/core/settings.py → backend/ is 3 levels up
_BACKEND_ROOT = Path(__file__).resolve().parents[2]  # backend/
_PROJECT_ROOT = _BACKEND_ROOT.parent                  # Round 2/


class Settings(BaseSettings):
    BACKEND_ENV: str = "development"
    BACKEND_VERSION: str = "1.0.0"

    # Output CSVs live in <project_root>/outputs/ by default.
    # Override with OUTPUT_DIR env var for custom deployments.
    OUTPUT_DIR: Path = _PROJECT_ROOT / "outputs"

    # Model pkl lives in backend/app/models/ by default.
    MODEL_DIR: Path = _BACKEND_ROOT / "app" / "models"

    # Comma-separated list of allowed CORS origins
    CORS_ORIGINS: str = (
        "http://localhost:3000,"
        "http://localhost:5173,"
        "http://localhost:8080,"
        "http://127.0.0.1:3000,"
        "http://127.0.0.1:5173"
    )

    LOG_LEVEL: str = "INFO"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
