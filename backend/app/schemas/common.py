"""Shared/generic response models."""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: str
    message: str
    endpoint: str
    timestamp: datetime


class PaginationMeta(BaseModel):
    total: int = Field(..., description="Total records available after filtering")
    returned: int = Field(..., description="Records in this response")
    limit: int


class DataResponse(BaseModel):
    """Generic wrapper used by list endpoints."""
    meta: PaginationMeta
    data: list[Any]
