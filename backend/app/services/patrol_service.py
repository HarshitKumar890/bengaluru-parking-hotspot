"""Patrol recommendation service — merges patrol data with risk and explanation data."""
from typing import Optional
import pandas as pd

from app.services.file_service import store
from app.utils.io import df_to_records
from app.utils.transforms import (
    filter_by_station,
    filter_by_risk_category,
    filter_by_stability_class,
    filter_min_value,
)


def get_patrol_data(
    limit: int,
    station: Optional[str],
    risk_category: Optional[str],
    stability_class: Optional[str],
    min_prediction: Optional[float],
) -> tuple[int, list[dict]]:
    """
    Return patrol recommendation rows from top20 list, enriched with risk scores
    and risk explanation text where available.
    Returns (total_after_filter, records).
    """
    df = store.top20
    if df is None:
        df = store.patrol  # fallback to full patrol table
    if df is None:
        return 0, []

    df = df.copy()

    # Merge congestion risk scores
    if store.risk_labels is not None:
        df = df.merge(
            store.risk_labels[["spatial_cell_id", "congestion_risk_score", "congestion_risk_category"]],
            on="spatial_cell_id",
            how="left",
        )

    # Merge risk explanation text
    if store.explanations is not None:
        df = df.merge(store.explanations, on="spatial_cell_id", how="left")

    # Rename predicted_count for uniform schema
    if "predicted_count" not in df.columns and "forecasted_count" in df.columns:
        df = df.rename(columns={"forecasted_count": "predicted_count"})

    # Filters
    df = filter_by_station(df, station)
    df = filter_by_risk_category(df, risk_category)
    df = filter_by_stability_class(df, stability_class)
    df = filter_min_value(df, "predicted_count", min_prediction)

    total = len(df)
    if "patrol_rank" in df.columns:
        df = df.sort_values("patrol_rank")
    df = df.head(limit)

    return total, df_to_records(df)
