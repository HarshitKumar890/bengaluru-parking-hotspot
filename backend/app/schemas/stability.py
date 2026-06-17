"""Hotspot stability label response schemas."""
from typing import Optional
from pydantic import BaseModel, Field


class StabilityItem(BaseModel):
    spatial_cell_id: str
    stability_class: str = Field(..., description="Persistent / Seasonal / Sporadic")
    recurrence: Optional[float] = Field(None, description="Fraction of months with violations")
    mean_monthly: Optional[float] = Field(None, description="Average monthly violation count")
    std_monthly: Optional[float] = Field(None, description="Standard deviation of monthly counts")
    cv: Optional[float] = Field(None, description="Coefficient of variation")
    trend_slope: Optional[float] = Field(None, description="OLS trend slope across months")
    n_active: Optional[int] = Field(None, alias="active_months", description="Number of active months")
    cell_lat: Optional[float] = None
    cell_lon: Optional[float] = None
    police_station: Optional[str] = None

    class Config:
        populate_by_name = True
