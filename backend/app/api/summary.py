"""GET /summary — dashboard summary metrics."""
from fastapi import APIRouter

from app.schemas.summary import SummaryResponse
from app.services.file_service import store

router = APIRouter()


@router.get("/summary", response_model=SummaryResponse, summary="Dashboard summary metrics")
def summary() -> SummaryResponse:
    """
    Aggregated summary statistics for the dashboard overview panel.
    Derived from precomputed output files — no heavy computation at request time.
    """
    # --- violation totals from station rankings ---
    total_violations: int | None = None
    top_station: str | None = None
    if store.stations is not None:
        total_violations = int(store.stations["total_cases"].sum())
        if "volume_rank" in store.stations.columns:
            top_row = store.stations.sort_values("volume_rank").iloc[0]
            top_station = str(top_row["police_station"])

    # --- top junction ---
    top_junction: str | None = None
    if store.junctions is not None and "volume_rank" in store.junctions.columns:
        top_junction = str(store.junctions.sort_values("volume_rank").iloc[0]["junction_name"])

    # --- spatial cells ---
    total_cells: int | None = None
    persistent: int | None = None
    volatile: int | None = None
    declining: int | None = None
    emerging: int | None = None
    if store.stability is not None:
        total_cells = int(store.stability["spatial_cell_id"].nunique())
        vc = store.stability["stability_class"].value_counts()
        persistent = int(vc.get("Persistent", 0))
        volatile   = int(vc.get("Volatile", 0))
        declining  = int(vc.get("Declining", 0))
        emerging   = int(vc.get("Emerging", 0))

    # --- risk zone counts (CSV uses UPPERCASE: CRITICAL, HIGH, MODERATE, LOW) ---
    critical: int | None = None
    high: int | None = None
    moderate: int | None = None
    low: int | None = None
    if store.risk_labels is not None:
        vc = store.risk_labels["congestion_risk_category"].value_counts()
        critical = int(vc.get("CRITICAL", 0))
        high     = int(vc.get("HIGH", 0))
        moderate = int(vc.get("MODERATE", 0))
        low      = int(vc.get("LOW", 0))

    # --- model comparison — use ensemble_search_results for V2 best metrics ---
    best_model: str | None = None
    best_recall: float | None = None
    best_recall_50: float | None = None
    if store.ensemble is not None and "recall@20" in store.ensemble.columns:
        row = store.ensemble.sort_values("recall@20", ascending=False).iloc[0]
        best_model = str(row["ensemble"])
        best_recall = float(round(row["recall@20"], 4))
        best_recall_50 = float(round(row["recall@50"], 4)) if "recall@50" in row.index else None
    elif store.model_cmp is not None:
        # Fallback: average across valid primary folds
        valid_primary = store.model_cmp[
            (store.model_cmp["is_primary"] == True) &
            (store.model_cmp["lgbm_valid"] == True)
        ]
        if len(valid_primary) == 0:
            valid_primary = store.model_cmp[store.model_cmp["is_primary"] == True]
        if len(valid_primary) > 0:
            avg = valid_primary.groupby("model")["recall@20"].mean()
            best_model = str(avg.idxmax())
            best_recall = float(round(avg.max(), 4))
            best_recall_50 = None

    # --- April normalization factor (median) ---
    apr_factor: float | None = None
    if store.apr_norm is not None and "normalization_factor" in store.apr_norm.columns:
        apr_factor = float(store.apr_norm["normalization_factor"].median())

    # --- patrol counts ---
    patrol_cells: int | None = None
    top20_cells: int | None = None
    if store.patrol is not None:
        patrol_cells = len(store.patrol)
    if store.top20 is not None:
        top20_cells = len(store.top20)

    return SummaryResponse(
        total_violations=total_violations,
        total_spatial_cells=total_cells,
        persistent_hotspots=persistent,
        volatile_hotspots=volatile,
        declining_hotspots=declining,
        emerging_hotspots=emerging,
        critical_risk_zones=critical,
        high_risk_zones=high,
        moderate_risk_zones=moderate,
        low_risk_zones=low,
        best_model_name=best_model,
        best_recall_at_20=best_recall,
        best_recall_at_50=best_recall_50,
        top_police_station=top_station,
        top_junction=top_junction,
        april_normalization_factor=apr_factor,
        total_patrol_cells=patrol_cells,
        top20_patrol_cells=top20_cells,
    )
