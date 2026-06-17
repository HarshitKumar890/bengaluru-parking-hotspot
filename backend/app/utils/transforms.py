"""DataFrame filtering and transformation helpers."""
from typing import Optional
import pandas as pd


def filter_by_station(df: pd.DataFrame, station: Optional[str]) -> pd.DataFrame:
    """Case-insensitive police station filter across common column names."""
    if station is None:
        return df
    col = _find_col(df, ["police_station"])
    if col is None:
        return df
    mask = df[col].str.strip().str.lower() == station.strip().lower()
    return df[mask]


def filter_by_risk_category(df: pd.DataFrame, category: Optional[str]) -> pd.DataFrame:
    if category is None:
        return df
    col = _find_col(df, ["congestion_risk_category"])
    if col is None:
        return df
    # CSV values are uppercase (CRITICAL, HIGH, MODERATE, LOW); validator normalizes to upper
    return df[df[col].str.strip().str.upper() == category.strip().upper()]


def filter_by_stability_class(df: pd.DataFrame, stability_class: Optional[str]) -> pd.DataFrame:
    if stability_class is None:
        return df
    col = _find_col(df, ["stability_class"])
    if col is None:
        return df
    # CSV values are Title case (Persistent, Volatile, Declining, Emerging)
    return df[df[col].str.strip().str.lower() == stability_class.strip().lower()]


def filter_min_value(df: pd.DataFrame, col_name: str, min_val: Optional[float]) -> pd.DataFrame:
    if min_val is None or col_name not in df.columns:
        return df
    return df[df[col_name] >= min_val]


def sort_df(df: pd.DataFrame, col: str, ascending: bool = False) -> pd.DataFrame:
    if col not in df.columns:
        return df
    return df.sort_values(col, ascending=ascending)


def _find_col(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None
