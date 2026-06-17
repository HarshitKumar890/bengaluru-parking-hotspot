"""Patrol recommendation response schemas."""
from typing import Optional
from pydantic import BaseModel, Field


class PatrolItem(BaseModel):
    patrol_rank: int = Field(..., description="Patrol deployment priority rank (1 = highest)")
    spatial_cell_id: str
    cell_lat: Optional[float] = None
    cell_lon: Optional[float] = None
    predicted_count: Optional[float] = Field(None, description="Forecasted violation count")
    priority_score: Optional[float] = Field(None, description="Composite patrol priority score")
    police_station: Optional[str] = None
    stability_class: Optional[str] = Field(None, description="Persistent / Seasonal / Sporadic")
    recurrence: Optional[float] = Field(None, description="Historical recurrence rate")
    cv: Optional[float] = Field(None, description="Coefficient of variation — volatility measure")
    trend_slope: Optional[float] = Field(None, description="Monthly trend slope; positive = worsening")
    congestion_risk_score: Optional[float] = None
    congestion_risk_category: Optional[str] = None
    risk_explanation: Optional[str] = Field(None, description="Human-readable risk explanation text")
