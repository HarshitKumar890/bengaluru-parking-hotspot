"""Junction analytics response schemas."""
from typing import Optional
from pydantic import BaseModel, Field


class JunctionItem(BaseModel):
    junction_name: str
    total_cases: int
    unique_vehicles: Optional[int] = None
    n_approved: Optional[int] = None
    n_rejected: Optional[int] = None
    avg_response_min: Optional[float] = Field(None, description="Average response time (minutes)")
    peak_hour_violations: Optional[int] = None
    peak_hour_pct: Optional[float] = Field(None, description="Fraction of violations during peak hours (%)")
    n_recurrent: Optional[int] = Field(None, description="Number of recurrent/repeat vehicles")
    approval_rate_pct: Optional[float] = Field(None, description="Case approval rate (%)")
    volume_rank: Optional[int] = Field(None, description="Junction rank by total case volume")
