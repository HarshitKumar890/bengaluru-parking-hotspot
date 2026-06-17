"""Health check response schema."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="'ok' or 'degraded'")
    timestamp: datetime
    backend_version: str
    environment: str
    model_loaded: bool = Field(..., description="Whether the LightGBM model pkl is loaded")
    files_loaded: bool = Field(..., description="Whether all output CSVs were loaded at startup")
    missing_files: list[str] = Field(default_factory=list, description="Any CSV files that failed to load")
