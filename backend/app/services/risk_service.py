"""Congestion risk zone service."""
from typing import Optional
import pandas as pd

from app.services.file_service import store
from app.utils.io import df_to_records
from app.utils.transforms import (
    filter_by_station,
    filter_by_risk_category,
    filter_min_value,
    sort_df,
)


def get_risk_zones(
    limit: int,
    category: Optional[str],
    station: Optional[str],
    min_risk_score: Optional[float],
) -> tuple[int, list[dict]]:
    """
    Return congestion risk zones from the hotspot_risk_table, enriched with
    explanation text.  Falls back to risk_labels if hotspot_risk_table is absent.
    """
    df = store.risk_table
    if df is None:
        df = store.risk_labels
    if df is None:
        return 0, []

    df = df.copy()

    # Merge station data if not already present
    if "police_station" not in df.columns and store.patrol is not None:
        df = df.merge(
            store.patrol[["spatial_cell_id", "police_station"]].drop_duplicates(),
            on="spatial_cell_id",
            how="left",
        )

    # Merge lat/lon
    if "cell_lat" not in df.columns and store.patrol is not None:
        df = df.merge(
            store.patrol[["spatial_cell_id", "cell_lat", "cell_lon"]].drop_duplicates(),
            on="spatial_cell_id",
            how="left",
        )

    # Merge explanations
    if store.explanations is not None:
        df = df.merge(store.explanations, on="spatial_cell_id", how="left")

    df = filter_by_risk_category(df, category)
    df = filter_by_station(df, station)
    df = filter_min_value(df, "congestion_risk_score", min_risk_score)
    df = sort_df(df, "congestion_risk_score", ascending=False)

    total = len(df)
    return total, df_to_records(df.head(limit))
