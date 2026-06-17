"""Station and junction analytics service."""
from typing import Optional
import pandas as pd

from app.services.file_service import store
from app.utils.io import df_to_records
from app.utils.transforms import sort_df


def get_stations(limit: int, sort_by: str = "total_cases") -> tuple[int, list[dict]]:
    df = store.stations
    if df is None:
        return 0, []

    df = df.copy()

    # Enrich with active hotspot cell counts from stability / patrol data
    if store.stability is not None and "police_station" in store.stability.columns:
        cell_counts = (
            store.stability[store.stability["police_station"].notna()]
            .groupby("police_station")["spatial_cell_id"]
            .nunique()
            .reset_index()
            .rename(columns={"spatial_cell_id": "n_active_hotspot_cells"})
        )
        df = df.merge(cell_counts, on="police_station", how="left")

    df = sort_df(df, sort_by, ascending=False)
    total = len(df)
    return total, df_to_records(df.head(limit))


def get_junctions(limit: int, sort_by: str = "total_cases") -> tuple[int, list[dict]]:
    df = store.junctions
    if df is None:
        return 0, []

    df = df.copy()
    df = sort_df(df, sort_by, ascending=False)
    total = len(df)
    return total, df_to_records(df.head(limit))
