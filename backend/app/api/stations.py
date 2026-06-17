"""GET /stations — police station analytics."""
from typing import Optional
from fastapi import APIRouter, Query

from app.services.analytics_service import get_stations
from app.utils.validators import validated_limit

router = APIRouter()


@router.get("/stations", summary="Police station analytics")
def stations(
    limit: int = Query(default=50, ge=1, le=500),
    sort_by: Optional[str] = Query(default="total_cases", description="Column to sort by"),
):
    """
    Returns analytics for each police station including case volumes,
    approval rates, validation delays, operational scores, and active hotspot cell counts.
    """
    validated_limit(limit)
    total, records = get_stations(limit, sort_by=sort_by or "total_cases")
    return {
        "meta": {"total": total, "returned": len(records), "limit": limit},
        "data": records,
    }
