"""Startup file loader — reads all CSVs once and caches in memory."""
import pandas as pd
from pathlib import Path
from typing import Optional
from app.core.logging import logger
from app.core.settings import settings


class DataStore:
    """Singleton in-memory store for all precomputed output DataFrames."""

    patrol:       Optional[pd.DataFrame] = None
    risk_labels:  Optional[pd.DataFrame] = None
    risk_table:   Optional[pd.DataFrame] = None
    top20:        Optional[pd.DataFrame] = None
    stability:    Optional[pd.DataFrame] = None
    feat_imp:     Optional[pd.DataFrame] = None
    model_cmp:    Optional[pd.DataFrame] = None
    fold_preds:   Optional[pd.DataFrame] = None
    stations:     Optional[pd.DataFrame] = None
    junctions:    Optional[pd.DataFrame] = None
    heatmap:      Optional[pd.DataFrame] = None
    explanations: Optional[pd.DataFrame] = None
    apr_norm:     Optional[pd.DataFrame] = None
    ensemble:     Optional[pd.DataFrame] = None

    files_loaded: bool = False
    missing_files: list[str] = []


store = DataStore()

_FILE_MAP: dict[str, str] = {
    "patrol":       "enhanced_patrol_priority.csv",
    "risk_labels":  "congestion_risk_labels.csv",
    "risk_table":   "hotspot_risk_table.csv",
    "top20":        "top20_patrol_recommendations.csv",
    "stability":    "hotspot_stability_labels.csv",
    "feat_imp":     "feature_importance.csv",
    "model_cmp":    "model_comparison_table.csv",
    "fold_preds":   "fold_predictions.csv",
    "stations":     "eda_station_rankings.csv",
    "junctions":    "eda_junction_rankings.csv",
    "heatmap":      "congestion_risk_heatmap.csv",
    "explanations": "top50_risk_explanations.csv",
    "apr_norm":     "april_normalization_report.csv",
    "ensemble":     "ensemble_search_results.csv",
}

SAFE_DOWNLOADS: set[str] = set(_FILE_MAP.values()) | {
    "window_granularity_comparison.csv",
    "severity_forecasting_comparison.csv",
    "spatial_feature_ablation.csv",
    "feature_group_ablation.csv",
    "risk_weight_sensitivity.csv",
    "hotspot_stability_labels.csv",
    "violation_frequency.csv",
    "offence_frequency.csv",
}


def _load(name: str, path: Path) -> Optional[pd.DataFrame]:
    if not path.exists():
        logger.warning("Missing file: %s", path)
        store.missing_files.append(name)
        return None
    try:
        df = pd.read_csv(path, low_memory=False)
        logger.info("Loaded %-35s  %d rows", path.name, len(df))
        return df
    except Exception as exc:
        logger.error("Failed to load %s: %s", path.name, exc)
        store.missing_files.append(name)
        return None


def load_all_files() -> None:
    d = settings.OUTPUT_DIR
    for attr, filename in _FILE_MAP.items():
        df = _load(attr, d / filename)
        setattr(store, attr, df)
    store.files_loaded = True
    n_ok = sum(1 for a in _FILE_MAP if getattr(store, a) is not None)
    logger.info("File loading complete: %d/%d files loaded", n_ok, len(_FILE_MAP))
