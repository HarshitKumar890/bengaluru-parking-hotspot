"""GET /hotspots — hotspot map data with optional filters."""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timezone

from app.services.file_service import store
from app.schemas.hotspot import HotspotItem
from app.schemas.common import PaginationMeta
from app.utils.io import df_to_records
from app.utils.validators import validated_limit, validated_risk_category, validated_stability_class
from app.utils.transforms import (
    filter_by_station,
    filter_by_risk_category,
    filter_by_stability_class,
    filter_min_value,
)

router = APIRouter()


@router.get("/hotspots", summary="Hotspot map data")
def get_hotspots(
    limit: int = Query(default=200, ge=1, le=1000, description="Max rows to return"),
    station: Optional[str] = Query(default=None, description="Filter by police station name"),
    risk_category: Optional[str] = Query(default=None, description="Filter by congestion risk category: CRITICAL / HIGH / MODERATE / LOW"),
    stability_class: Optional[str] = Query(default=None, description="Filter by stability class: Persistent / Volatile / Declining / Emerging"),
    min_prediction: Optional[float] = Query(default=None, description="Minimum forecasted violation count"),
):
    """
    Returns spatial hotspot records suitable for map rendering.
    Each record includes coordinates, forecast counts, risk scores, and station assignments.
    """
    validated_limit(limit)
    risk_category = validated_risk_category(risk_category)
    stability_class = validated_stability_class(stability_class)

    df = store.risk_table
    if df is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "data_unavailable",
                "message": "Hotspot risk table is not loaded.",
                "endpoint": "/hotspots",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    df = df.copy()

    # Enrich with stability class only if not already present in risk_table
    if store.stability is not None and "stability_class" not in df.columns:
        stab_cols = ["spatial_cell_id", "stability_class", "recurrence"]
        stab_cols = [c for c in stab_cols if c in store.stability.columns]
        df = df.merge(
            store.stability[stab_cols].drop_duplicates("spatial_cell_id"),
            on="spatial_cell_id", how="left",
        )

    df = filter_by_station(df, station)
    df = filter_by_risk_category(df, risk_category)
    df = filter_by_stability_class(df, stability_class)
    df = filter_min_value(df, "forecasted_count", min_prediction)

    if "patrol_rank" in df.columns:
        df = df.sort_values("patrol_rank")

    total = len(df)
    records = df_to_records(df.head(limit))

    return {
        "meta": {"total": total, "returned": len(records), "limit": limit},
        "data": records,
    }
