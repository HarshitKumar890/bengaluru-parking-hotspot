"""Input validation helpers for query parameters."""
from fastapi import HTTPException

VALID_RISK_CATEGORIES = {"CRITICAL", "HIGH", "MODERATE", "LOW"}
VALID_STABILITY_CLASSES = {"Persistent", "Volatile", "Declining", "Emerging"}
VALID_SORT_ORDERS = {"asc", "desc"}

MAX_LIMIT = 1000
DEFAULT_LIMIT = 100


def validated_limit(limit: int) -> int:
    if limit < 1:
        raise HTTPException(status_code=422, detail="limit must be >= 1")
    if limit > MAX_LIMIT:
        raise HTTPException(status_code=422, detail=f"limit must be <= {MAX_LIMIT}")
    return limit


def validated_risk_category(category: str | None) -> str | None:
    if category is None:
        return None
    normalized = category.strip().upper()
    if normalized not in VALID_RISK_CATEGORIES:
        raise HTTPException(
            status_code=422,
            detail=f"risk_category must be one of {sorted(VALID_RISK_CATEGORIES)}",
        )
    return normalized


def validated_stability_class(stability_class: str | None) -> str | None:
    if stability_class is None:
        return None
    # Capitalize only first letter to match CSV values: Persistent, Volatile, etc.
    normalized = stability_class.strip().capitalize()
    if normalized not in VALID_STABILITY_CLASSES:
        raise HTTPException(
            status_code=422,
            detail=f"stability_class must be one of {sorted(VALID_STABILITY_CLASSES)}",
        )
    return normalized


def validated_sort_order(order: str | None) -> str:
    if order is None:
        return "desc"
    order = order.strip().lower()
    if order not in VALID_SORT_ORDERS:
        raise HTTPException(status_code=422, detail="sort_order must be 'asc' or 'desc'")
    return order
