"""Forecast response schemas."""
from typing import Optional
from pydantic import BaseModel, Field


class ForecastItem(BaseModel):
    patrol_rank: Optional[int] = Field(None, description="Patrol rank in this forecast snapshot")
    spatial_cell_id: str
    cell_lat: Optional[float] = None
    cell_lon: Optional[float] = None
    pred_lgbm: Optional[float] = Field(None, description="LightGBM model prediction")
    pred_rolling: Optional[float] = Field(None, description="Rolling mean baseline prediction")
    pred_lag1: Optional[float] = Field(None, description="Lag-1 baseline prediction")
    forecasted_count: Optional[float] = Field(None, description="Final ensemble/chosen forecast count")
    priority_score: Optional[float] = None
    police_station: Optional[str] = None
    stability_class: Optional[str] = None
    congestion_risk_score: Optional[float] = None
    congestion_risk_category: Optional[str] = None
    ranking_basis: Optional[str] = Field(None, description="Which model output was used for ranking")


class ForecastResponse(BaseModel):
    model_loaded: bool = Field(..., description="Whether the live LightGBM model is available")
    snapshot_note: str = Field(
        ...,
        description="Describes the forecast source (precomputed snapshot vs live inference)",
    )
    total: int
    returned: int
    data: list[ForecastItem]
