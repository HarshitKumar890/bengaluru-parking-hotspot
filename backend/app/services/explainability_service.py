"""Feature importance / explainability service."""
from typing import Literal
from app.services.file_service import store
from app.utils.io import df_to_records


def get_feature_importance(
    limit: int,
    sort_order: Literal["asc", "desc"] = "desc",
) -> tuple[int, list[dict]]:
    df = store.feat_imp
    if df is None:
        return 0, []

    df = df.copy()
    ascending = sort_order == "asc"
    df = df.sort_values("importance", ascending=ascending).reset_index(drop=True)
    df.insert(0, "rank", range(1, len(df) + 1))

    total = len(df)
    return total, df_to_records(df.head(limit))
