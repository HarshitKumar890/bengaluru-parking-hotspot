"""Congestion risk zone response schemas."""
from typing import Optional
from pydantic import BaseModel, Field


class RiskZoneItem(BaseModel):
    spatial_cell_id: str
    congestion_risk_score: float = Field(..., description="Parking-induced congestion risk score (0–1)")
    congestion_risk_category: str = Field(..., description="Critical / High / Medium / Low")
    police_station: Optional[str] = None
    cell_lat: Optional[float] = None
    cell_lon: Optional[float] = None
    forecasted_count: Optional[float] = None
    patrol_rank: Optional[int] = None
    risk_explanation: Optional[str] = None
