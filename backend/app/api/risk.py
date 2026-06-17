"""GET /risk-zones — parking-induced congestion risk zones."""
from typing import Optional
from fastapi import APIRouter, Query

from app.services.risk_service import get_risk_zones
from app.utils.validators import validated_limit, validated_risk_category

router = APIRouter()


@router.get("/risk-zones", summary="Parking-induced congestion risk zones")
def risk_zones(
    limit: int = Query(default=100, ge=1, le=1000),
    category: Optional[str] = Query(default=None, description="Risk category: Critical / High / Medium / Low"),
    station: Optional[str] = Query(default=None, description="Filter by police station"),
    min_risk_score: Optional[float] = Query(default=None, ge=0.0, le=1.0, description="Minimum congestion risk score (0–1)"),
):
    """
    Returns spatial cells ranked by parking-induced congestion risk score.

    Note: This system models *parking-related* congestion risk — not general
    traffic congestion. Risk scores are derived from violation density,
    persistence, and hotspot severity metrics.
    """
    validated_limit(limit)
    category = validated_risk_category(category)

    total, records = get_risk_zones(limit, category, station, min_risk_score)
    return {
        "meta": {"total": total, "returned": len(records), "limit": limit},
        "data": records,
    }
