"""GET /download/{dataset_name} — safe CSV export endpoint."""
from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import FileResponse
from datetime import datetime, timezone

from app.services.file_service import SAFE_DOWNLOADS
from app.core.settings import settings

router = APIRouter()


@router.get(
    "/download/{dataset_name}",
    summary="Download a precomputed CSV dataset",
    response_class=FileResponse,
)
def download_dataset(
    dataset_name: str = Path(..., description="CSV filename (e.g. feature_importance.csv)"),
):
    """
    Downloads one of the allowed precomputed CSV output files.
    Only filenames in the safe list are accessible — this endpoint does not
    expose arbitrary filesystem paths.
    """
    # Sanitize — reject anything with path separators
    if "/" in dataset_name or "\\" in dataset_name or ".." in dataset_name:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_filename",
                "message": "Dataset name must be a plain filename with no path components.",
                "endpoint": f"/download/{dataset_name}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    if dataset_name not in SAFE_DOWNLOADS:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "dataset_not_found",
                "message": f"'{dataset_name}' is not in the list of downloadable datasets.",
                "available": sorted(SAFE_DOWNLOADS),
                "endpoint": f"/download/{dataset_name}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    file_path = settings.OUTPUT_DIR / dataset_name
    if not file_path.exists():
        raise HTTPException(
            status_code=503,
            detail={
                "error": "file_missing",
                "message": f"File '{dataset_name}' is registered but not found on disk.",
                "endpoint": f"/download/{dataset_name}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    return FileResponse(
        path=str(file_path),
        media_type="text/csv",
        filename=dataset_name,
    )


@router.get("/download", summary="List downloadable datasets")
def list_downloads():
    """Returns the list of all CSV files available for download."""
    return {"available_datasets": sorted(SAFE_DOWNLOADS)}
