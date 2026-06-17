"""Hotspot map response schemas."""
from typing import Optional
from pydantic import BaseModel, Field


class HotspotItem(BaseModel):
    patrol_rank: Optional[int] = Field(None, description="Patrol priority rank")
    spatial_cell_id: str = Field(..., description="Unique spatial grid cell identifier")
    cell_lat: Optional[float] = Field(None, description="Cell centroid latitude")
    cell_lon: Optional[float] = Field(None, description="Cell centroid longitude")
    forecasted_count: Optional[float] = Field(None, description="ML forecasted violation count")
    police_station: Optional[str] = Field(None, description="Responsible police station")
    congestion_risk_score: Optional[float] = Field(None, description="Parking-induced congestion risk score (0–1)")
    congestion_risk_category: Optional[str] = Field(None, description="Risk category: Critical / High / Medium / Low")
    priority_score: Optional[float] = Field(None, description="Combined patrol priority score")
    stability_class: Optional[str] = Field(None, description="Hotspot stability: Persistent / Seasonal / Sporadic")
    recurrence: Optional[float] = Field(None, description="Recurrence rate across observed months")
