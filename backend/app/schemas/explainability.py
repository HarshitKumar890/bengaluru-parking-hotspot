"""Feature importance / explainability response schemas."""
from typing import Optional
from pydantic import BaseModel, Field


class FeatureImportanceItem(BaseModel):
    rank: int = Field(..., description="Importance rank (1 = most important)")
    feature: str = Field(..., description="Feature name")
    importance: int = Field(..., description="Raw LightGBM split-based importance score")
    importance_pct: float = Field(..., description="Importance as percentage of total")
