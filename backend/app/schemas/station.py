"""Police station analytics response schemas."""
from typing import Optional
from pydantic import BaseModel, Field


class StationItem(BaseModel):
    police_station: str
    total_cases: int
    unique_vehicles: Optional[int] = None
    n_approved: Optional[int] = None
    n_rejected: Optional[int] = None
    n_pending_unknown: Optional[int] = None
    approval_rate_pct: Optional[float] = Field(None, description="Case approval rate (%)")
    rejection_rate_pct: Optional[float] = None
    unresolved_rate_pct: Optional[float] = Field(None, description="Pending/unknown cases (%)")
    avg_response_min: Optional[float] = Field(None, description="Average response time (minutes)")
    median_response_min: Optional[float] = None
    p95_response_min: Optional[float] = Field(None, description="95th-percentile response time (minutes)")
    avg_validation_min: Optional[float] = Field(None, description="Average validation delay (minutes)")
    peak_hour_violations: Optional[int] = None
    peak_hour_pct: Optional[float] = Field(None, description="Fraction of violations in peak hours (%)")
    ops_score: Optional[float] = Field(None, description="Composite operational performance score")
    volume_rank: Optional[int] = Field(None, description="Station rank by total case volume")
    n_active_hotspot_cells: Optional[int] = Field(None, description="Number of spatial cells assigned to this station with active hotspot status")
