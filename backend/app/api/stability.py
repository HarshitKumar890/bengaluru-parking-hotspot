"""GET /stability — hotspot stability label data."""
from typing import Optional
from fastapi import APIRouter, Query

from app.services.file_service import store
from app.utils.io import df_to_records
from app.utils.transforms import filter_by_station, filter_by_stability_class
from app.utils.validators import validated_limit, validated_stability_class

router = APIRouter()


@router.get("/stability", summary="Hotspot stability classifications")
def stability(
    limit: int = Query(default=200, ge=1, le=1000),
    stability_class: Optional[str] = Query(default=None, description="Persistent / Seasonal / Sporadic"),
    station: Optional[str] = Query(default=None, description="Filter by police station"),
):
    """
    Returns hotspot stability labels derived from the 6-month (Nov 2023 – Apr 2024)
    violation time series.  Includes recurrence rates, trend slopes, and coefficient
    of variation for each spatial cell.
    """
    validated_limit(limit)
    stability_class = validated_stability_class(stability_class)

    if store.stability is None:
        return {"meta": {"total": 0, "returned": 0, "limit": limit}, "data": []}

    df = store.stability.copy()

    # Keep only the stable analytics columns; drop month columns for cleaner output
    month_cols = [c for c in df.columns if c.startswith("20")]
    keep_cols = [c for c in df.columns if c not in month_cols]
    df = df[keep_cols]

    df = filter_by_stability_class(df, stability_class)
    df = filter_by_station(df, station)

    if "recurrence" in df.columns:
        df = df.sort_values("recurrence", ascending=False)

    total = len(df)
    records = df_to_records(df.head(limit))

    return {
        "meta": {"total": total, "returned": len(records), "limit": limit},
        "data": records,
    }
