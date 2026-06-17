"""GET /junctions — junction analytics."""
from typing import Optional
from fastapi import APIRouter, Query

from app.services.analytics_service import get_junctions
from app.utils.validators import validated_limit

router = APIRouter()


@router.get("/junctions", summary="Junction-level analytics")
def junctions(
    limit: int = Query(default=50, ge=1, le=500),
    sort_by: Optional[str] = Query(default="total_cases", description="Column to sort by"),
):
    """
    Returns case volume, peak hour fractions, recurrence metrics,
    and approval rates for each junction.
    """
    validated_limit(limit)
    total, records = get_junctions(limit, sort_by=sort_by or "total_cases")
    return {
        "meta": {"total": total, "returned": len(records), "limit": limit},
        "data": records,
    }
