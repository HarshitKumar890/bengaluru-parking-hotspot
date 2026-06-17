"""
Forecast service.

Returns the latest precomputed patrol-ranked forecast snapshot.
Live inference from the LightGBM model is not implemented because the
feature engineering pipeline requires the full cleaned dataset context.
The patrol priority table IS the latest forecast output — it was produced
by the final LightGBM pipeline run.
"""
from typing import Optional

from app.services.file_service import store
from app.services.model_service import model_state
from app.utils.io import df_to_records
from app.utils.transforms import (
    filter_by_station,
    filter_by_risk_category,
)

SNAPSHOT_NOTE = (
    "This is the latest precomputed forecast snapshot produced by the LightGBM pipeline. "
    "Live per-request inference is not available — the model requires full dataset context "
    "for feature engineering. The patrol priority ranking represents the April 2024 forecast."
)

READ_ONLY_NOTE = (
    "LightGBM model file not loaded. Returning latest precomputed forecast snapshot from CSV."
)


def get_forecast(
    limit: int,
    station: Optional[str],
    risk_category: Optional[str],
) -> tuple[bool, str, int, list[dict]]:
    """
    Returns (model_loaded, snapshot_note, total, records).
    """
    df = store.patrol
    if df is None:
        return model_state.loaded, SNAPSHOT_NOTE, 0, []

    df = df.copy()

    # Merge congestion risk
    if store.risk_labels is not None:
        df = df.merge(
            store.risk_labels[["spatial_cell_id", "congestion_risk_score", "congestion_risk_category"]],
            on="spatial_cell_id",
            how="left",
        )

    df = filter_by_station(df, station)
    df = filter_by_risk_category(df, risk_category)

    if "patrol_rank" in df.columns:
        df = df.sort_values("patrol_rank")

    total = len(df)
    note = SNAPSHOT_NOTE if model_state.loaded else READ_ONLY_NOTE
    return model_state.loaded, note, total, df_to_records(df.head(limit))
