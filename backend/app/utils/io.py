"""Safe pandas → JSON conversion helpers."""
import math
from typing import Any
import pandas as pd


def df_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Convert a DataFrame to a list of JSON-safe dicts.
    - NaN / Inf → None
    - numpy scalar types → Python native
    """
    records = df.to_dict(orient="records")
    return [_clean_record(r) for r in records]


def _clean_record(record: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for k, v in record.items():
        cleaned[k] = _safe_value(v)
    return cleaned


def _safe_value(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v):
            return None
        return round(v, 6)
    # numpy int / float types
    if hasattr(v, "item"):
        native = v.item()
        if isinstance(native, float) and (math.isnan(native) or math.isinf(native)):
            return None
        return native
    if isinstance(v, bool):
        return v
    return v
