"""GET /patrol-recommendations — top patrol deployment cells."""
from typing import Optional
from fastapi import APIRouter, Query

from app.services.patrol_service import get_patrol_data
from app.utils.validators import validated_limit, validated_risk_category, validated_stability_class

router = APIRouter()


@router.get("/patrol-recommendations", summary="Top patrol deployment recommendations")
def patrol_recommendations(
    limit: int = Query(default=20, ge=1, le=200),
    station: Optional[str] = Query(default=None, description="Filter by police station"),
    risk_category: Optional[str] = Query(default=None, description="Filter by congestion risk category"),
    stability_class: Optional[str] = Query(default=None, description="Filter by stability class"),
    min_prediction: Optional[float] = Query(default=None, description="Minimum predicted violation count"),
):
    """
    Returns top patrol cell recommendations ranked by priority score.
    Each record includes predicted counts, stability, risk category,
    and where available, a human-readable explanation of the risk factors.
    """
    validated_limit(limit)
    risk_category = validated_risk_category(risk_category)
    stability_class = validated_stability_class(stability_class)

    total, records = get_patrol_data(limit, station, risk_category, stability_class, min_prediction)
    return {
        "meta": {"total": total, "returned": len(records), "limit": limit},
        "data": records,
    }
