"""GET /feature-importance — LightGBM feature importance rankings."""
from typing import Optional
from fastapi import APIRouter, Query

from app.services.explainability_service import get_feature_importance
from app.utils.validators import validated_limit, validated_sort_order

router = APIRouter()


@router.get("/feature-importance", summary="LightGBM feature importance rankings")
def feature_importance(
    limit: int = Query(default=30, ge=1, le=200),
    sort_order: Optional[str] = Query(default="desc", description="Sort direction: 'asc' or 'desc'"),
):
    """
    Returns LightGBM split-based feature importance scores, ranked from most
    to least important by default.  Use sort_order=asc to reverse.
    """
    validated_limit(limit)
    order = validated_sort_order(sort_order)

    total, records = get_feature_importance(limit, order)
    return {
        "meta": {"total": total, "returned": len(records), "limit": limit},
        "data": records,
    }
