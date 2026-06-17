"""GET /forecast — latest hotspot forecast snapshot."""
from typing import Optional
from fastapi import APIRouter, Query

from app.schemas.forecast import ForecastResponse
from app.services.forecast_service import get_forecast
from app.utils.validators import validated_limit, validated_risk_category

router = APIRouter()


@router.get("/forecast", response_model=ForecastResponse, summary="Latest hotspot forecast")
def forecast(
    limit: int = Query(default=100, ge=1, le=1000),
    station: Optional[str] = Query(default=None, description="Filter by police station"),
    risk_category: Optional[str] = Query(default=None, description="Filter by congestion risk category"),
):
    """
    Returns the April 2024 precomputed parking hotspot forecast snapshot.

    Live per-request inference is not available — the model requires full
    feature-engineering context from the cleaned dataset. Re-run the
    ml_hotspot_forecasting.py pipeline to refresh the forecast.

    The `model_loaded` flag indicates whether the LightGBM pkl file is present
    on the server (does not affect the data returned).
    The `snapshot_note` field explains the data source.
    """
    validated_limit(limit)
    risk_category = validated_risk_category(risk_category)

    loaded, note, total, records = get_forecast(limit, station, risk_category)
    return ForecastResponse(
        model_loaded=loaded,
        snapshot_note=note,
        total=total,
        returned=len(records),
        data=records,
    )
