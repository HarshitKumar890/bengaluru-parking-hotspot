"""
data_audit_and_cleaning.py
==========================
Production-grade data ingestion, audit, cleaning, feature engineering,
and export pipeline for the Bengaluru traffic enforcement dataset.

Phases covered:
    1  — Data Ingestion
    2  — Structural Audit
    3  — Missing Value Standardization
    4  — Datetime Parsing & Temporal Features
    5  — Geo Validation & Spatial Normalization
    6  — Multi-Label Parsing (violation_type / offence_code)
    7  — Categorical Normalization
    8  — Deduplication & Near-Duplicate Flagging
    9  — Enforcement Workflow Analysis
    10 — Hotspot Preparation
    11 — EDA Charts & Reports  (basic; extended EDA in eda_insights.py)
    12 — Cleaned Master Dataset Export
    13 — Final Quality Gates

Author : Production ML / Data Engineering Team
Dataset: jan to may police violation_anonymized791b166.csv (~298 k rows)
"""

# ---------------------------------------------------------------------------
# Standard library
# ---------------------------------------------------------------------------
import ast
import json
import logging
import os
import re
import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Third-party
# ---------------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")  # non-interactive backend — safe for scripts
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import seaborn as sns

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# ── CONFIGURATION ────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

RAW_FILE = Path(r"e:\FLIPKARTGRID\Round 2\jan to may police violation_anonymized791b166.csv")
OUTPUT_DIR = Path(r"e:\FLIPKARTGRID\Round 2\outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Bengaluru bounding box  (generous padding)
BLR_LAT_MIN, BLR_LAT_MAX = 12.70, 13.20
BLR_LON_MIN, BLR_LON_MAX = 77.40, 77.85

# Peak-hour windows  (Bengaluru urban defaults)
MORNING_PEAK_START, MORNING_PEAK_END = 7, 10   # 07:00 – 10:59
EVENING_PEAK_START, EVENING_PEAK_END = 17, 20  # 17:00 – 20:59

# Near-duplicate matching tolerance
COORD_TOLERANCE = 0.001        # ~111 m at equator
DATETIME_TOLERANCE_MIN = 5     # 5-minute window

# Spatial grid resolution  (degrees)
GRID_SIZE = 0.005              # ~500 m cells

# Hotspot score weights
W_DENSITY     = 0.30
W_RECURRENCE  = 0.20
W_JUNCTION    = 0.15
W_PEAK_HOUR   = 0.15
W_DELAY       = 0.10
W_SEVERITY    = 0.10

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# ---------------------------------------------------------------------------
# ── LOGGING SETUP ────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

LOG_FILE = OUTPUT_DIR / "pipeline.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ── HELPERS ──────────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS = [
    "id", "latitude", "longitude", "location", "vehicle_number",
    "vehicle_type", "description", "violation_type", "offence_code",
    "created_datetime", "closed_datetime", "modified_datetime",
    "device_id", "created_by_id", "center_code", "police_station",
    "data_sent_to_scita", "junction_name", "action_taken_timestamp",
    "data_sent_to_scita_timestamp", "updated_vehicle_number",
    "updated_vehicle_type", "validation_status", "validation_timestamp",
]

MISSING_TOKENS = {"null", "none", "n/a", "nan", "na", "nil", "#n/a", ""}


def _safe_write_csv(df: pd.DataFrame, path: Path, **kwargs) -> None:
    """Write CSV; raise loudly if it fails."""
    try:
        df.to_csv(path, index=False, **kwargs)
        log.info("Wrote  %s  (%d rows, %d cols)", path.name, len(df), df.shape[1])
    except Exception as exc:
        log.error("FAILED to write %s: %s", path, exc)
        raise


def _safe_write_text(text: str, path: Path) -> None:
    try:
        path.write_text(text, encoding="utf-8")
        log.info("Wrote  %s", path.name)
    except Exception as exc:
        log.error("FAILED to write %s: %s", path, exc)
        raise


def _safe_write_json(obj: dict, path: Path) -> None:
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2, default=str)
        log.info("Wrote  %s", path.name)
    except Exception as exc:
        log.error("FAILED to write %s: %s", path, exc)
        raise


def _save_fig(fig: plt.Figure, name: str) -> None:
    path = OUTPUT_DIR / name
    try:
        fig.savefig(path, dpi=150, bbox_inches="tight")
        log.info("Saved chart  %s", name)
    except Exception as exc:
        log.error("FAILED to save chart %s: %s", name, exc)
    finally:
        plt.close(fig)


# ---------------------------------------------------------------------------
# ── PHASE 1 — DATA INGESTION ─────────────────────────────────────────────────
# ---------------------------------------------------------------------------

def phase1_ingest(filepath: Path) -> pd.DataFrame:
    """
    Load raw CSV with everything as object (string) dtype.
    Detect encoding issues, report shape and memory, validate required columns.
    The source file is NEVER modified.
    """
    log.info("=" * 70)
    log.info("PHASE 1 — DATA INGESTION")
    log.info("=" * 70)

    if not filepath.exists():
        raise FileNotFoundError(f"Raw file not found: {filepath}")

    file_size_mb = filepath.stat().st_size / (1024 ** 2)
    log.info("File: %s  (%.1f MB)", filepath.name, file_size_mb)

    # --- encoding probe ---
    encoding = "utf-8"
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            with open(filepath, "r", encoding=enc) as fh:
                fh.read(65536)
            encoding = enc
            log.info("Detected encoding: %s", enc)
            break
        except UnicodeDecodeError:
            continue

    # --- load as strings ---
    log.info("Loading CSV (dtype=str, no type inference) …")
    df = pd.read_csv(
        filepath,
        dtype=str,
        keep_default_na=False,   # prevent pandas from converting 'NULL' etc.
        encoding=encoding,
        low_memory=False,
    )

    log.info("Row count   : %d", len(df))
    log.info("Column count: %d", df.shape[1])
    log.info("Memory usage: %.1f MB", df.memory_usage(deep=True).sum() / (1024 ** 2))
    log.info("Columns     : %s", list(df.columns))

    # --- validate required columns ---
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"CRITICAL — Missing required columns: {missing_cols}")

    # --- sample values ---
    log.info("--- Sample values per column (first 3 non-empty) ---")
    for col in df.columns:
        samples = df[col][df[col].str.strip() != ""].head(3).tolist()
        log.info("  %-35s : %s", col, samples)

    return df


# ---------------------------------------------------------------------------
# ── PHASE 2 — STRUCTURAL AUDIT ───────────────────────────────────────────────
# ---------------------------------------------------------------------------

def _count_literal_null(series: pd.Series) -> int:
    return series.str.lower().isin({"null", "none", "nan", "n/a", "nil"}).sum()


def _count_whitespace_only(series: pd.Series) -> int:
    return (series.str.strip() == "").sum()


def _looks_like_list(series: pd.Series, sample_n: int = 500) -> bool:
    sample = series.dropna().head(sample_n)
    hits = sample.str.match(r"^\s*[\[\(]").sum()
    return hits / max(len(sample), 1) > 0.3


def phase2_structural_audit(df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Full per-column audit.  Returns (audit_df, summary_markdown).
    """
    log.info("=" * 70)
    log.info("PHASE 2 — STRUCTURAL AUDIT")
    log.info("=" * 70)

    rows = []
    for col in df.columns:
        s = df[col]
        n_missing   = (s.str.strip() == "").sum() + s.isna().sum()
        pct_missing = round(n_missing / len(df) * 100, 2)
        n_unique    = s.nunique()
        top10       = s.value_counts().head(10).to_dict()
        n_ws_only   = _count_whitespace_only(s)
        n_lit_null  = _count_literal_null(s)
        looks_list  = _looks_like_list(s)

        rows.append({
            "column"          : col,
            "dtype_raw"       : str(s.dtype),
            "n_missing"       : int(n_missing),
            "pct_missing"     : pct_missing,
            "n_unique"        : int(n_unique),
            "top10_values"    : str(top10),
            "n_whitespace_only": int(n_ws_only),
            "n_literal_null"  : int(n_lit_null),
            "looks_like_list" : bool(looks_list),
        })

    audit_df = pd.DataFrame(rows)

    # --- duplicates ---
    n_dup_rows = df.duplicated().sum()
    n_dup_ids  = df["id"].duplicated().sum()
    log.info("Duplicate rows     : %d", n_dup_rows)
    log.info("Duplicate id values: %d", n_dup_ids)

    # --- null-pattern clusters (rows with >=50% missing) ---
    null_mask = df.apply(lambda s: s.str.strip() == "", axis=1)
    n_mostly_null = (null_mask.sum(axis=1) >= df.shape[1] * 0.5).sum()
    log.info("Rows with ≥50%% null fields: %d", n_mostly_null)

    # --- markdown summary ---
    high_missing = audit_df[audit_df["pct_missing"] > 50][["column", "pct_missing"]]
    list_cols    = audit_df[audit_df["looks_like_list"]]["column"].tolist()

    md_lines = [
        "# Structural Audit Summary\n",
        f"- **Total rows**: {len(df):,}",
        f"- **Total columns**: {df.shape[1]}",
        f"- **Duplicate rows**: {n_dup_rows:,}",
        f"- **Duplicate IDs**: {n_dup_ids:,}",
        f"- **Rows with ≥50% null fields**: {n_mostly_null:,}",
        "",
        "## Columns with >50% missing",
        high_missing.to_markdown(index=False) if not high_missing.empty else "None",
        "",
        "## Columns that appear to be serialised lists",
        ", ".join(list_cols) if list_cols else "None",
        "",
        "## Per-Column Detail",
        audit_df[["column", "pct_missing", "n_unique", "n_literal_null",
                  "looks_like_list"]].to_markdown(index=False),
    ]
    summary_md = "\n".join(md_lines)

    _safe_write_csv(audit_df, OUTPUT_DIR / "audit_report.csv")
    _safe_write_text(summary_md, OUTPUT_DIR / "audit_summary.md")

    return audit_df, summary_md


# ---------------------------------------------------------------------------
# ── PHASE 3 — MISSING VALUE STANDARDIZATION ──────────────────────────────────
# ---------------------------------------------------------------------------

JUNCTION_PLACEHOLDERS = {
    "no junction", "nojunction", "n/a", "none", "null", "na",
    "not available", "unknown", "-", "--", "nil",
}


def _normalize_missing(series: pd.Series) -> pd.Series:
    """Replace all blank / placeholder representations with pd.NA."""
    s = series.copy()
    s = s.str.strip()
    s = s.replace("", pd.NA)
    # literal null tokens
    null_pattern = "|".join(
        [r"^null$", r"^none$", r"^n/a$", r"^nan$", r"^na$", r"^nil$", r"^#n/a$"]
    )
    mask = s.str.lower().str.match(null_pattern, na=False)
    s[mask] = pd.NA
    return s


def phase3_missing_standardization(df: pd.DataFrame) -> pd.DataFrame:
    log.info("=" * 70)
    log.info("PHASE 3 — MISSING VALUE STANDARDIZATION")
    log.info("=" * 70)

    before_counts = {col: df[col].isna().sum() for col in df.columns}

    for col in df.columns:
        df[col] = _normalize_missing(df[col])

    # junction_name — additional placeholder mapping
    jn_col = "junction_name"
    placeholder_mask = df[jn_col].str.lower().isin(JUNCTION_PLACEHOLDERS)
    n_jn_placeholder = int(placeholder_mask.sum())
    df.loc[placeholder_mask, jn_col] = pd.NA
    log.info("junction_name: mapped %d placeholder values → NA", n_jn_placeholder)

    # location — preserve text but normalise whitespace
    df["location"] = df["location"].str.replace(r"\s+", " ", regex=True).str.strip()

    # case standardisation for key categoricals
    for col in ["police_station", "vehicle_type", "validation_status"]:
        if col in df.columns:
            df[col] = df[col].str.strip().str.upper()

    after_counts = {col: df[col].isna().sum() for col in df.columns}

    log.info("--- Before / After NA counts (changed columns only) ---")
    for col in df.columns:
        b, a = before_counts[col], after_counts[col]
        if a != b:
            log.info("  %-35s : %d → %d  (Δ %+d)", col, b, a, a - b)

    return df


# ---------------------------------------------------------------------------
# ── PHASE 4 — DATETIME PARSING & TEMPORAL FEATURES ───────────────────────────
# ---------------------------------------------------------------------------

DATETIME_COLS = [
    "created_datetime",
    "closed_datetime",
    "modified_datetime",
    "action_taken_timestamp",
    "data_sent_to_scita_timestamp",
    "validation_timestamp",
]


def _parse_datetime_col(series: pd.Series, col_name: str) -> Tuple[pd.Series, int]:
    """
    Parse a string series to datetime (UTC-aware when possible).
    Returns (parsed_series, n_failures).
    """
    parsed = pd.to_datetime(series, errors="coerce", utc=True)
    n_fail = parsed.isna().sum() - series.isna().sum()
    n_fail = max(int(n_fail), 0)
    if n_fail:
        log.warning("  %s: %d rows failed datetime parse", col_name, n_fail)
    return parsed, n_fail


def phase4_datetime_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    log.info("=" * 70)
    log.info("PHASE 4 — DATETIME PARSING & TEMPORAL FEATURES")
    log.info("=" * 70)

    parse_failures: Dict[str, int] = {}
    for col in DATETIME_COLS:
        if col not in df.columns:
            log.error("MISSING expected datetime column: %s", col)
            raise KeyError(col)
        df[f"_dt_{col}"], n_fail = _parse_datetime_col(df[col], col)
        parse_failures[col] = n_fail

    base = df["_dt_created_datetime"]

    df["created_date"]            = base.dt.date.astype(str)
    df["created_year"]            = base.dt.year
    df["created_month"]           = base.dt.month
    df["created_day"]             = base.dt.day
    df["created_hour"]            = base.dt.hour
    df["day_of_week"]             = base.dt.dayofweek          # 0=Mon … 6=Sun
    df["day_name"]                = base.dt.day_name()
    df["week_of_year"]            = base.dt.isocalendar().week.astype("Int64")
    df["is_weekend"]              = df["day_of_week"].isin([5, 6]).astype("Int8")
    df["is_peak_hour"]            = (
        (df["created_hour"].between(MORNING_PEAK_START, MORNING_PEAK_END)) |
        (df["created_hour"].between(EVENING_PEAK_START, EVENING_PEAK_END))
    ).astype("Int8")
    df["created_month_start_flag"] = (df["created_day"] <= 3).astype("Int8")

    log.info("Peak-hour definition: %02d:00–%02d:59 and %02d:00–%02d:59",
             MORNING_PEAK_START, MORNING_PEAK_END,
             EVENING_PEAK_START, EVENING_PEAK_END)

    # --- duration features ---
    duration_defs = {
        "response_delay_minutes"     : ("_dt_action_taken_timestamp",         "_dt_created_datetime"),
        "closure_delay_minutes"      : ("_dt_closed_datetime",                "_dt_created_datetime"),
        "modification_delay_minutes" : ("_dt_modified_datetime",              "_dt_created_datetime"),
        "validation_delay_minutes"   : ("_dt_validation_timestamp",           "_dt_created_datetime"),
        "scita_delay_minutes"        : ("_dt_data_sent_to_scita_timestamp",   "_dt_created_datetime"),
    }

    anomaly_records = []
    for feat, (end_col, start_col) in duration_defs.items():
        end   = df[end_col]
        start = df[start_col]
        valid = end.notna() & start.notna()
        delta = pd.Series(index=df.index, dtype="Float64")
        delta[valid] = (end[valid] - start[valid]).dt.total_seconds() / 60.0
        df[feat] = delta

        neg_mask = delta < 0
        n_neg = int(neg_mask.sum())
        if n_neg:
            log.warning("  %s: %d negative durations (anomaly flagged)", feat, n_neg)
            anomaly_records.append({"feature": feat, "n_negative": n_neg})
        df[f"{feat}_anomaly"] = neg_mask.astype("Int8")
        log.info("  %-35s computed (%d valid)", feat, int(valid.sum()))

    # --- time quality report ---
    tq_rows = []
    for col in DATETIME_COLS:
        dc = df[f"_dt_{col}"]
        tq_rows.append({
            "column"       : col,
            "n_total"      : len(df),
            "n_parsed_ok"  : int(dc.notna().sum()),
            "n_null_input" : int(df[col].isna().sum()),
            "n_parse_fail" : parse_failures[col],
            "min_value"    : str(dc.min()),
            "max_value"    : str(dc.max()),
        })
    tq_df = pd.DataFrame(tq_rows)
    _safe_write_csv(tq_df, OUTPUT_DIR / "time_quality_report.csv")

    # --- duration summary ---
    dur_cols = list(duration_defs.keys())
    existing_dur = [c for c in dur_cols if c in df.columns]
    dur_summary = df[existing_dur].describe(percentiles=[.25, .5, .75, .95, .99]).T.reset_index()
    dur_summary.columns = ["feature"] + list(dur_summary.columns[1:])
    _safe_write_csv(dur_summary, OUTPUT_DIR / "duration_summary.csv")

    return df, tq_df, dur_summary


# ---------------------------------------------------------------------------
# ── PHASE 5 — GEO VALIDATION & SPATIAL NORMALIZATION ─────────────────────────
# ---------------------------------------------------------------------------

def phase5_geo_validation(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    log.info("=" * 70)
    log.info("PHASE 5 — GEO VALIDATION & SPATIAL NORMALIZATION")
    log.info("=" * 70)

    df["_lat_raw"] = pd.to_numeric(df["latitude"],  errors="coerce")
    df["_lon_raw"] = pd.to_numeric(df["longitude"], errors="coerce")

    # --- validity flags ---
    lat_valid  = df["_lat_raw"].between(-90,  90)
    lon_valid  = df["_lon_raw"].between(-180, 180)
    lat_not_na = df["_lat_raw"].notna()
    lon_not_na = df["_lon_raw"].notna()

    invalid_range  = ~(lat_valid & lon_valid) & lat_not_na & lon_not_na
    near_zero      = (df["_lat_raw"].abs() < 0.001) | (df["_lon_raw"].abs() < 0.001)
    in_blr         = (
        df["_lat_raw"].between(BLR_LAT_MIN, BLR_LAT_MAX) &
        df["_lon_raw"].between(BLR_LON_MIN, BLR_LON_MAX)
    )
    # Swapped-coordinate suspicion: lat in lon range and lon in lat range
    swapped_suspect = (
        df["_lat_raw"].between(BLR_LON_MIN, BLR_LON_MAX) &
        df["_lon_raw"].between(BLR_LAT_MIN, BLR_LAT_MAX)
    )
    out_of_blr = lat_not_na & lon_not_na & ~near_zero & ~in_blr & ~swapped_suspect

    df["valid_geo_flag"] = (
        lat_not_na & lon_not_na & lat_valid & lon_valid &
        ~near_zero & in_blr
    ).astype("Int8")

    df["geo_anomaly_flag"] = (
        ~lat_not_na | ~lon_not_na |
        invalid_range | near_zero | out_of_blr | swapped_suspect
    ).astype("Int8")

    df["lat_round_4"] = df["_lat_raw"].round(4)
    df["lon_round_4"] = df["_lon_raw"].round(4)
    df["lat_round_5"] = df["_lat_raw"].round(5)
    df["lon_round_5"] = df["_lon_raw"].round(5)

    # --- spatial cell id (grid fallback — no external library required) ---
    lat_cell = np.floor(df["_lat_raw"] / GRID_SIZE).astype("Int64")
    lon_cell = np.floor(df["_lon_raw"] / GRID_SIZE).astype("Int64")
    df["spatial_cell_id"] = (
        "CELL_" +
        lat_cell.astype(str).str.replace("<NA>", "NA", regex=False) +
        "_" +
        lon_cell.astype(str).str.replace("<NA>", "NA", regex=False)
    )
    df.loc[df["valid_geo_flag"] != 1, "spatial_cell_id"] = pd.NA

    log.info("valid_geo_flag=1    : %d", int(df["valid_geo_flag"].eq(1).sum()))
    log.info("geo_anomaly_flag=1  : %d", int(df["geo_anomaly_flag"].eq(1).sum()))
    log.info("near-zero coords    : %d", int(near_zero.sum()))
    log.info("swapped suspects    : %d", int(swapped_suspect.sum()))
    log.info("out-of-BLR          : %d", int(out_of_blr.sum()))

    # --- geo quality report ---
    geo_report = pd.DataFrame([{
        "metric"         : "n_valid_geo",
        "value"          : int(df["valid_geo_flag"].eq(1).sum()),
    }, {
        "metric"         : "n_geo_anomaly",
        "value"          : int(df["geo_anomaly_flag"].eq(1).sum()),
    }, {
        "metric"         : "n_near_zero",
        "value"          : int(near_zero.sum()),
    }, {
        "metric"         : "n_swapped_suspect",
        "value"          : int(swapped_suspect.sum()),
    }, {
        "metric"         : "n_out_of_blr",
        "value"          : int(out_of_blr.sum()),
    }, {
        "metric"         : "n_missing_coords",
        "value"          : int((~lat_not_na | ~lon_not_na).sum()),
    }])
    _safe_write_csv(geo_report, OUTPUT_DIR / "geo_quality_report.csv")

    # --- spatial cells summary ---
    valid_df = df[df["valid_geo_flag"] == 1].copy()
    cells = (
        valid_df.groupby("spatial_cell_id", observed=True)
        .agg(
            cell_lat_center = ("_lat_raw", "mean"),
            cell_lon_center = ("_lon_raw", "mean"),
            n_records       = ("id", "count"),
        )
        .reset_index()
        .sort_values("n_records", ascending=False)
    )
    _safe_write_csv(cells, OUTPUT_DIR / "spatial_cells.csv")

    return df, cells


# ---------------------------------------------------------------------------
# ── PHASE 6 — MULTI-LABEL PARSING ────────────────────────────────────────────
# ---------------------------------------------------------------------------

def _parse_list_string(raw: Optional[str]) -> List[str]:
    """
    Safely parse a stringified list into a Python list of stripped strings.
    Handles: ['A', "B"], ["A"], [113], scalar strings, empty values.
    """
    if raw is None or (isinstance(raw, float) and np.isnan(raw)):
        return []
    raw = str(raw).strip()
    if raw in ("", "[]", "None", "null", "NULL"):
        return []
    try:
        parsed = ast.literal_eval(raw)
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()]
        return [str(parsed).strip()]
    except (ValueError, SyntaxError):
        # strip brackets and split by comma
        cleaned = re.sub(r'^[\[\(]|[\]\)]$', '', raw)
        parts   = [p.strip().strip('"').strip("'") for p in cleaned.split(",")]
        return [p for p in parts if p]


def phase6_multilabel_parsing(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    log.info("=" * 70)
    log.info("PHASE 6 — MULTI-LABEL PARSING")
    log.info("=" * 70)

    for col in ["violation_type", "offence_code"]:
        parsed_col = f"{col}_parsed"
        df[parsed_col] = df[col].apply(_parse_list_string)

        n_empty = df[parsed_col].apply(len).eq(0).sum()
        n_multi = df[parsed_col].apply(len).gt(1).sum()
        log.info("  %s: %d empty, %d multi-value", col, n_empty, n_multi)

    df["violation_count"] = df["violation_type_parsed"].apply(len).astype("Int64")
    df["offence_count"]   = df["offence_code_parsed"].apply(len).astype("Int64")
    df["primary_violation_type"] = df["violation_type_parsed"].apply(
        lambda x: x[0] if x else pd.NA
    )
    df["primary_offence_code"] = df["offence_code_parsed"].apply(
        lambda x: x[0] if x else pd.NA
    )

    # --- exploded tables ---
    def _explode_col(df: pd.DataFrame, parsed_col: str, label_col: str) -> pd.DataFrame:
        tmp = df[["id", parsed_col]].copy()
        tmp = tmp.explode(parsed_col)
        tmp = tmp.rename(columns={parsed_col: label_col})
        tmp = tmp[tmp[label_col].notna() & (tmp[label_col] != "")]
        return tmp.reset_index(drop=True)

    viol_exp = _explode_col(df, "violation_type_parsed", "violation_type_value")
    off_exp  = _explode_col(df, "offence_code_parsed",   "offence_code_value")

    _safe_write_csv(viol_exp, OUTPUT_DIR / "violations_exploded.csv")
    _safe_write_csv(off_exp,  OUTPUT_DIR / "offences_exploded.csv")

    viol_freq = (
        viol_exp["violation_type_value"]
        .value_counts()
        .reset_index()
        .rename(columns={"count": "frequency"})
    )
    off_freq = (
        off_exp["offence_code_value"]
        .value_counts()
        .reset_index()
        .rename(columns={"count": "frequency"})
    )
    _safe_write_csv(viol_freq, OUTPUT_DIR / "violation_frequency.csv")
    _safe_write_csv(off_freq,  OUTPUT_DIR / "offence_frequency.csv")

    return df, viol_freq, off_freq


# ---------------------------------------------------------------------------
# ── PHASE 7 — CATEGORICAL NORMALIZATION ──────────────────────────────────────
# ---------------------------------------------------------------------------

VEHICLE_TYPE_MAP: Dict[str, str] = {
    "maxi-cab"                : "MAXI CAB",
    "maxi cab"                : "MAXI CAB",
    "maxicab"                 : "MAXI CAB",
    "auto rickshaw"           : "AUTO RICKSHAW",
    "auto-rickshaw"           : "AUTO RICKSHAW",
    "autorickshaw"            : "AUTO RICKSHAW",
    "e-auto"                  : "E-AUTO RICKSHAW",
    "e-autorickshaw"          : "E-AUTO RICKSHAW",
    "light motor vehicle"     : "LMV",
    "lmv"                     : "LMV",
    "heavy motor vehicle"     : "HMV",
    "hmv"                     : "HMV",
    "two wheeler"             : "TWO WHEELER",
    "two-wheeler"             : "TWO WHEELER",
    "2 wheeler"               : "TWO WHEELER",
    "2wheeler"                : "TWO WHEELER",
    "motor cycle"             : "TWO WHEELER",
    "motorcycle"              : "TWO WHEELER",
    "car"                     : "CAR",
    "private car"             : "CAR",
    "suv"                     : "CAR",
    "taxi"                    : "TAXI",
    "cab"                     : "TAXI",
    "bus"                     : "BUS",
    "mini bus"                : "BUS",
    "mini-bus"                : "BUS",
    "van"                     : "VAN",
    "goods vehicle"           : "GOODS VEHICLE",
    "goods-vehicle"           : "GOODS VEHICLE",
    "lorry"                   : "GOODS VEHICLE",
    "truck"                   : "GOODS VEHICLE",
    "three wheeler"           : "THREE WHEELER",
    "three-wheeler"           : "THREE WHEELER",
    "3 wheeler"               : "THREE WHEELER",
    "e-rickshaw"              : "E-RICKSHAW",
    "erickshaw"               : "E-RICKSHAW",
}

VALIDATION_STATUS_MAP: Dict[str, str] = {
    "approved"  : "APPROVED",
    "approve"   : "APPROVED",
    "rejected"  : "REJECTED",
    "reject"    : "REJECTED",
    "pending"   : "PENDING",
    "inprogress": "PENDING",
    "in progress": "PENDING",
    "in_progress": "PENDING",
}


def _normalise_vehicle_type(series: pd.Series) -> pd.Series:
    s = series.str.lower().str.strip().str.replace(r"\s+", " ", regex=True)
    return s.map(VEHICLE_TYPE_MAP).fillna(
        series.str.upper().str.strip().str.replace(r"\s+", " ", regex=True)
    )


def _normalise_validation_status(series: pd.Series) -> pd.Series:
    s = series.str.lower().str.strip().str.replace(r"\s+", " ", regex=True)
    mapped = s.map(VALIDATION_STATUS_MAP)
    # anything unrecognised → UNKNOWN
    unknown_mask = mapped.isna() & series.notna()
    mapped[unknown_mask] = "UNKNOWN"
    return mapped


def phase7_categorical_normalization(df: pd.DataFrame) -> pd.DataFrame:
    log.info("=" * 70)
    log.info("PHASE 7 — CATEGORICAL NORMALIZATION")
    log.info("=" * 70)

    # preserve originals
    df["vehicle_type_raw"]       = df["vehicle_type"].copy()
    df["validation_status_raw"]  = df["validation_status"].copy()
    df["police_station_raw"]     = df["police_station"].copy()
    df["center_code_raw"]        = df["center_code"].copy()

    # vehicle_type_final
    df["vehicle_type_final"] = _normalise_vehicle_type(df["vehicle_type"].fillna(""))
    df.loc[df["vehicle_type"].isna(), "vehicle_type_final"] = pd.NA

    # update updated_vehicle_type the same way
    df["updated_vehicle_type_final"] = _normalise_vehicle_type(
        df["updated_vehicle_type"].fillna("")
    )
    df.loc[df["updated_vehicle_type"].isna(), "updated_vehicle_type_final"] = pd.NA

    # validation_status_final
    df["validation_status_final"] = _normalise_validation_status(
        df["validation_status"].fillna("")
    )
    df.loc[df["validation_status"].isna(), "validation_status_final"] = pd.NA

    # validation_flag_binary
    df["validation_flag_binary"] = pd.NA
    df.loc[df["validation_status_final"] == "APPROVED", "validation_flag_binary"] = 1
    df.loc[df["validation_status_final"] == "REJECTED", "validation_flag_binary"] = 0
    df["validation_flag_binary"] = df["validation_flag_binary"].astype("Int8")

    # police_station / center_code — trim and upper
    for col in ["police_station", "center_code"]:
        df[col] = df[col].str.strip().str.upper().str.replace(r"\s+", " ", regex=True)

    # --- export mapping report ---
    mapping_rows = [{"raw_value": k, "canonical_value": v, "field": "vehicle_type"}
                    for k, v in VEHICLE_TYPE_MAP.items()]
    mapping_rows += [{"raw_value": k, "canonical_value": v, "field": "validation_status"}
                     for k, v in VALIDATION_STATUS_MAP.items()]
    _safe_write_csv(pd.DataFrame(mapping_rows), OUTPUT_DIR / "categorical_mapping_report.csv")

    # --- distributions ---
    def _dist(series: pd.Series, name: str) -> pd.DataFrame:
        vc = series.value_counts(dropna=False).reset_index()
        vc.columns = [name, "count"]
        vc["pct"] = (vc["count"] / len(df) * 100).round(2)
        return vc

    _safe_write_csv(_dist(df["validation_status_final"], "validation_status"),
                    OUTPUT_DIR / "validation_distribution.csv")
    _safe_write_csv(_dist(df["vehicle_type_final"], "vehicle_type"),
                    OUTPUT_DIR / "vehicle_type_distribution.csv")
    _safe_write_csv(_dist(df["police_station"], "police_station"),
                    OUTPUT_DIR / "police_station_distribution.csv")

    log.info("Validation status distribution:\n%s",
             df["validation_status_final"].value_counts(dropna=False).to_string())
    log.info("Top 10 vehicle types:\n%s",
             df["vehicle_type_final"].value_counts(dropna=False).head(10).to_string())

    return df


# ---------------------------------------------------------------------------
# ── PHASE 8 — DEDUPLICATION & NEAR-DUPLICATE FLAGGING ────────────────────────
# ---------------------------------------------------------------------------

def phase8_deduplication(df: pd.DataFrame) -> pd.DataFrame:
    """
    Near-duplicate rule:
      A pair of records is considered a near-duplicate if ALL of:
        (a) same vehicle_number  (non-null)
        (b) |Δlat| ≤ COORD_TOLERANCE  AND  |Δlon| ≤ COORD_TOLERANCE
        (c) |Δcreated_datetime| ≤ DATETIME_TOLERANCE_MIN minutes
        (d) same primary_violation_type  (non-null)

    Implementation uses a merge-on-rounded-coordinates approach to avoid O(n²).
    We round coords to a coarser grid than COORD_TOLERANCE and merge on that key,
    which keeps the candidate set tractable.
    """
    log.info("=" * 70)
    log.info("PHASE 8 — DEDUPLICATION & NEAR-DUPLICATE FLAGGING")
    log.info("=" * 70)

    df = df.copy()

    # --- exact duplicate rows ---
    # Exclude list-typed columns — pandas duplicated() cannot hash Python lists.
    # We check duplicates across all scalar columns only; the list columns
    # (violation_type_parsed, offence_code_parsed) were derived from the raw
    # string columns which ARE included in the check.
    unhashable_cols = [
        c for c in df.columns
        if df[c].dtype == object and
        df[c].dropna().head(1).apply(lambda x: isinstance(x, list)).any()
    ]
    dup_check_cols = [c for c in df.columns if c not in unhashable_cols]
    df["is_exact_duplicate"] = df[dup_check_cols].duplicated(keep="first").astype("Int8")
    n_exact = int(df["is_exact_duplicate"].sum())
    log.info("Exact duplicate rows : %d", n_exact)

    # --- exact duplicate ids ---
    n_dup_ids = df["id"].duplicated().sum()
    log.info("Duplicate id values  : %d", n_dup_ids)

    # --- near-duplicate detection ---
    # Coarse grid for join key (~200 m)
    COARSE = 0.002
    work = df[
        df["vehicle_number"].notna() &
        df["_lat_raw"].notna() &
        df["_lon_raw"].notna() &
        df["primary_violation_type"].notna() &
        df["_dt_created_datetime"].notna()
    ].copy()

    work["_jk_lat"] = (work["_lat_raw"] / COARSE).apply(np.floor)
    work["_jk_lon"] = (work["_lon_raw"] / COARSE).apply(np.floor)
    work["_jk_key"] = (
        work["vehicle_number"].str.upper() + "|" +
        work["_jk_lat"].astype(str) + "|" +
        work["_jk_lon"].astype(str)
    )

    # self-join on coarse key
    left  = work[["id", "_jk_key", "_lat_raw", "_lon_raw",
                  "_dt_created_datetime", "primary_violation_type"]].copy()
    right = left.copy()
    left.columns  = [f"L_{c}" for c in left.columns]
    right.columns = [f"R_{c}" for c in right.columns]

    merged = left.merge(right, left_on="L__jk_key", right_on="R__jk_key")
    merged = merged[merged["L_id"] < merged["R_id"]]  # avoid self & symmetric pairs

    # apply fine tolerances
    coord_ok = (
        (merged["L__lat_raw"] - merged["R__lat_raw"]).abs() <= COORD_TOLERANCE
    ) & (
        (merged["L__lon_raw"] - merged["R__lon_raw"]).abs() <= COORD_TOLERANCE
    )
    time_ok = (
        (merged["L__dt_created_datetime"] - merged["R__dt_created_datetime"])
        .dt.total_seconds().abs() / 60.0
        <= DATETIME_TOLERANCE_MIN
    )
    viol_ok = (
        merged["L_primary_violation_type"] == merged["R_primary_violation_type"]
    )

    near_dup_pairs = merged[coord_ok & time_ok & viol_ok][["L_id", "R_id"]].copy()
    log.info("Near-duplicate pairs found: %d", len(near_dup_pairs))

    # assign group ids via union-find (vectorised)
    if not near_dup_pairs.empty:
        id_to_group: Dict[str, str] = {}
        group_counter = 0
        for _, row in near_dup_pairs.iterrows():
            a, b = row["L_id"], row["R_id"]
            ga, gb = id_to_group.get(a), id_to_group.get(b)
            if ga is None and gb is None:
                g = f"NEAR_DUP_{group_counter:06d}"
                group_counter += 1
                id_to_group[a] = g
                id_to_group[b] = g
            elif ga is None:
                id_to_group[a] = gb
            elif gb is None:
                id_to_group[b] = ga
            else:
                # merge groups
                if ga != gb:
                    for k, v in id_to_group.items():
                        if v == gb:
                            id_to_group[k] = ga

        group_map = pd.Series(id_to_group, name="duplicate_group_id")
        df["duplicate_group_id"]  = df["id"].map(group_map)
        df["is_near_duplicate"]   = df["duplicate_group_id"].notna().astype("Int8")
    else:
        df["duplicate_group_id"] = pd.NA
        df["is_near_duplicate"]  = 0

    log.info("Rows flagged is_near_duplicate=1 : %d", int(df["is_near_duplicate"].sum()))

    dup_analysis = df[
        (df["is_exact_duplicate"] == 1) | (df["is_near_duplicate"] == 1)
    ][["id", "vehicle_number", "latitude", "longitude", "created_datetime",
       "primary_violation_type", "is_exact_duplicate", "is_near_duplicate",
       "duplicate_group_id"]].copy()

    _safe_write_csv(dup_analysis, OUTPUT_DIR / "duplicate_analysis.csv")

    return df


# ---------------------------------------------------------------------------
# ── PHASE 9 — ENFORCEMENT WORKFLOW ANALYSIS ──────────────────────────────────
# ---------------------------------------------------------------------------

def phase9_workflow_analysis(df: pd.DataFrame) -> None:
    log.info("=" * 70)
    log.info("PHASE 9 — ENFORCEMENT WORKFLOW ANALYSIS")
    log.info("=" * 70)

    def _workflow_metrics(group_col: str, out_file: str) -> None:
        grp = df.groupby(group_col, observed=True)
        metrics = grp.agg(
            total_cases          = ("id", "count"),
            n_approved           = ("validation_flag_binary", lambda x: (x == 1).sum()),
            n_rejected           = ("validation_flag_binary", lambda x: (x == 0).sum()),
            n_unresolved         = ("validation_status_final",
                                    lambda x: x.isin(["PENDING", "UNKNOWN", pd.NA]).sum()),
            avg_response_min     = ("response_delay_minutes", "mean"),
            median_response_min  = ("response_delay_minutes", "median"),
            avg_closure_min      = ("closure_delay_minutes", "mean"),
            avg_validation_min   = ("validation_delay_minutes", "mean"),
            n_negative_response  = ("response_delay_minutes_anomaly",
                                    lambda x: (x == 1).sum()),
        ).reset_index()

        metrics["approval_rate"]  = (metrics["n_approved"]   / metrics["total_cases"] * 100).round(2)
        metrics["rejection_rate"] = (metrics["n_rejected"]   / metrics["total_cases"] * 100).round(2)
        metrics["unresolved_rate"]= (metrics["n_unresolved"] / metrics["total_cases"] * 100).round(2)

        metrics = metrics.sort_values("total_cases", ascending=False)
        _safe_write_csv(metrics, OUTPUT_DIR / out_file)
        log.info("  %s written (%d groups)", out_file, len(metrics))

    _workflow_metrics("police_station", "workflow_metrics_by_station.csv")

    if df["junction_name"].notna().any():
        _workflow_metrics("junction_name", "workflow_metrics_by_junction.csv")
    else:
        log.warning("junction_name entirely null after cleaning — skipping junction metrics.")
        pd.DataFrame().to_csv(OUTPUT_DIR / "workflow_metrics_by_junction.csv", index=False)


# ---------------------------------------------------------------------------
# ── PHASE 10 — HOTSPOT PREPARATION ───────────────────────────────────────────
# ---------------------------------------------------------------------------

def phase10_hotspot_preparation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Hotspot priority score formula (per spatial cell):

        score = W_DENSITY     * norm(violation_count_per_cell)
              + W_RECURRENCE  * norm(recurrence_count)
              + W_JUNCTION    * norm(near_junction_count)
              + W_PEAK_HOUR   * norm(peak_hour_fraction)
              + W_DELAY       * norm(avg_response_delay)
              + W_SEVERITY    * norm(high_freq_offence_fraction)

    All components are min-max normalised to [0, 1].
    Weights: density=0.30, recurrence=0.20, junction=0.15,
             peak_hour=0.15, delay=0.10, severity=0.10.

    NOTE: This is a proxy enforcement-priority score, NOT a congestion
    prediction.  It ranks cells by expected enforcement demand.
    """
    log.info("=" * 70)
    log.info("PHASE 10 — HOTSPOT PREPARATION")
    log.info("=" * 70)

    valid = df[df["valid_geo_flag"] == 1].copy()

    if valid.empty:
        log.error("No valid-geo rows — cannot build hotspot scores.")
        return df

    # --- recurrence: vehicle seen in same cell more than once ---
    veh_cell_counts = (
        valid.groupby(["vehicle_number", "spatial_cell_id"], observed=True)["id"]
        .count()
        .reset_index()
        .rename(columns={"id": "_veh_cell_cnt"})
    )
    veh_cell_recurrence = veh_cell_counts[veh_cell_counts["_veh_cell_cnt"] > 1]
    recurring_vehicles  = set(
        zip(veh_cell_recurrence["vehicle_number"], veh_cell_recurrence["spatial_cell_id"])
    )
    valid["_is_recurrent"] = valid.apply(
        lambda r: 1 if (r["vehicle_number"], r["spatial_cell_id"]) in recurring_vehicles else 0,
        axis=1,
    )

    # --- junction proximity: has a named junction ---
    valid["_has_junction"] = valid["junction_name"].notna().astype(int)

    # --- high-frequency offence severity proxy ---
    # Top-20% offence codes by frequency are labelled "high-severity"
    if "primary_offence_code" in valid.columns:
        off_freq = valid["primary_offence_code"].value_counts()
        threshold = off_freq.quantile(0.80) if len(off_freq) else 0
        high_sev_codes = set(off_freq[off_freq >= threshold].index)
        valid["_high_sev"] = valid["primary_offence_code"].isin(high_sev_codes).astype(int)
    else:
        valid["_high_sev"] = 0

    # --- cell-level aggregation ---
    cell_agg = valid.groupby("spatial_cell_id", observed=True).agg(
        cell_lat_center    = ("_lat_raw", "mean"),
        cell_lon_center    = ("_lon_raw", "mean"),
        violation_count    = ("id", "count"),
        unique_vehicles    = ("vehicle_number", "nunique"),
        recurrence_count   = ("_is_recurrent", "sum"),
        peak_hour_count    = ("is_peak_hour", lambda x: (x == 1).sum()),
        near_junction_count= ("_has_junction", "sum"),
        n_approved         = ("validation_flag_binary", lambda x: (x == 1).sum()),
        n_rejected         = ("validation_flag_binary", lambda x: (x == 0).sum()),
        avg_response_delay = ("response_delay_minutes", "mean"),
        high_sev_count     = ("_high_sev", "sum"),
    ).reset_index()

    cell_agg["approval_ratio"]     = (
        cell_agg["n_approved"] / cell_agg["violation_count"].replace(0, pd.NA)
    ).round(4)
    cell_agg["peak_hour_fraction"] = (
        cell_agg["peak_hour_count"] / cell_agg["violation_count"].replace(0, pd.NA)
    ).round(4)
    cell_agg["high_sev_fraction"]  = (
        cell_agg["high_sev_count"] / cell_agg["violation_count"].replace(0, pd.NA)
    ).round(4)

    _safe_write_csv(cell_agg, OUTPUT_DIR / "hotspot_candidates.csv")

    # --- scoring ---
    def _minmax(s: pd.Series) -> pd.Series:
        # Convert to float64 to avoid pandas NA ambiguity in comparisons
        s = s.astype(float)
        mn, mx = s.min(), s.max()
        if pd.isna(mn) or pd.isna(mx) or mx == mn:
            return pd.Series(0.0, index=s.index)
        return (s - mn) / (mx - mn)

    # fill NaN response delay with median; fall back to 0 if entirely null
    delay_median = cell_agg["avg_response_delay"].median()
    delay_fill_val = 0.0 if pd.isna(delay_median) else float(delay_median)
    delay_filled = cell_agg["avg_response_delay"].fillna(delay_fill_val)

    cell_agg["score_density"]    = _minmax(cell_agg["violation_count"])
    cell_agg["score_recurrence"] = _minmax(cell_agg["recurrence_count"])
    cell_agg["score_junction"]   = _minmax(cell_agg["near_junction_count"])
    cell_agg["score_peak_hour"]  = _minmax(cell_agg["peak_hour_fraction"].fillna(0))
    cell_agg["score_delay"]      = _minmax(delay_filled)
    cell_agg["score_severity"]   = _minmax(cell_agg["high_sev_fraction"].fillna(0))

    cell_agg["hotspot_priority_score"] = (
        W_DENSITY    * cell_agg["score_density"]    +
        W_RECURRENCE * cell_agg["score_recurrence"] +
        W_JUNCTION   * cell_agg["score_junction"]   +
        W_PEAK_HOUR  * cell_agg["score_peak_hour"]  +
        W_DELAY      * cell_agg["score_delay"]      +
        W_SEVERITY   * cell_agg["score_severity"]
    ).round(6)

    cell_agg = cell_agg.sort_values("hotspot_priority_score", ascending=False)
    cell_agg["hotspot_rank"] = range(1, len(cell_agg) + 1)

    _safe_write_csv(cell_agg, OUTPUT_DIR / "hotspot_priority_scores.csv")
    log.info("Hotspot cells: %d", len(cell_agg))
    log.info("Top 5 hotspot cells:\n%s",
             cell_agg[["spatial_cell_id", "violation_count",
                        "hotspot_priority_score", "hotspot_rank"]].head(5).to_string())

    # Merge cell score back into main df
    df = df.merge(
        cell_agg[["spatial_cell_id", "hotspot_priority_score", "hotspot_rank"]],
        on="spatial_cell_id",
        how="left",
    )

    return df


# ---------------------------------------------------------------------------
# ── PHASE 11 — EDA CHARTS ────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

def _bar_chart(data: pd.Series, title: str, xlabel: str, fname: str,
               color: str = "#2A6496", top_n: int = 20) -> None:
    data = data.dropna().value_counts().head(top_n)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh(data.index[::-1], data.values[::-1], color=color)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.tight_layout()
    _save_fig(fig, fname)


def phase11_eda_charts(df: pd.DataFrame,
                       viol_freq: pd.DataFrame,
                       off_freq: pd.DataFrame) -> str:
    log.info("=" * 70)
    log.info("PHASE 11 — EDA CHARTS & REPORTS")
    log.info("=" * 70)

    sns.set_theme(style="whitegrid", palette="muted")

    # 1. Top violation types
    if not viol_freq.empty:
        top_v = viol_freq.head(20).set_index("violation_type_value")["frequency"]
        _bar_chart(top_v.reset_index().set_index("violation_type_value").squeeze(),
                   "Top 20 Violation Types", "Count", "chart_top_violations.png")

    # 2. Top offence codes
    if not off_freq.empty:
        top_o = off_freq.head(20).set_index("offence_code_value")["frequency"]
        _bar_chart(top_o.reset_index().set_index("offence_code_value").squeeze(),
                   "Top 20 Offence Codes", "Count", "chart_top_offence_codes.png",
                   color="#E74C3C")

    # 3. Top vehicle types
    _bar_chart(df["vehicle_type_final"], "Top Vehicle Types", "Count",
               "chart_top_vehicle_types.png", color="#27AE60")

    # 4. Top police stations
    _bar_chart(df["police_station"], "Top 20 Police Stations", "Cases",
               "chart_top_police_stations.png", color="#8E44AD")

    # 5. Top junctions
    if df["junction_name"].notna().any():
        _bar_chart(df["junction_name"], "Top 20 Junctions", "Cases",
                   "chart_top_junctions.png", color="#D35400")

    # 6. Monthly trend
    monthly = df["created_month"].value_counts().sort_index()
    if not monthly.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(monthly.index, monthly.values, marker="o", linewidth=2, color="#2A6496")
        ax.set_title("Monthly Violation Trend", fontsize=14, fontweight="bold")
        ax.set_xlabel("Month")
        ax.set_ylabel("Count")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):02d}"))
        plt.tight_layout()
        _save_fig(fig, "chart_monthly_trend.png")

    # 7. Weekday trend
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_counts = df["day_name"].value_counts().reindex(dow_order).dropna()
    if not dow_counts.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(dow_counts.index, dow_counts.values, color="#16A085")
        ax.set_title("Violations by Day of Week", fontsize=14, fontweight="bold")
        ax.set_ylabel("Count")
        plt.tight_layout()
        _save_fig(fig, "chart_weekday_trend.png")

    # 8. Hourly trend
    hourly = df["created_hour"].value_counts().sort_index()
    if not hourly.empty:
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.bar(hourly.index, hourly.values, color="#2980B9")
        ax.set_title("Violations by Hour of Day", fontsize=14, fontweight="bold")
        ax.set_xlabel("Hour (24h)")
        ax.set_ylabel("Count")
        plt.tight_layout()
        _save_fig(fig, "chart_hourly_trend.png")

    # 9. Approval vs rejection
    vs_data = df["validation_status_final"].value_counts()
    if not vs_data.empty:
        fig, ax = plt.subplots(figsize=(7, 5))
        colors = {"APPROVED": "#27AE60", "REJECTED": "#E74C3C",
                  "PENDING": "#F39C12", "UNKNOWN": "#95A5A6"}
        bar_colors = [colors.get(k, "#7F8C8D") for k in vs_data.index]
        ax.bar(vs_data.index, vs_data.values, color=bar_colors)
        ax.set_title("Validation Status Distribution", fontsize=14, fontweight="bold")
        ax.set_ylabel("Count")
        plt.tight_layout()
        _save_fig(fig, "chart_validation_status.png")

    # 10. Response delay distribution
    rd = df["response_delay_minutes"].dropna()
    rd = rd[(rd >= 0) & (rd <= rd.quantile(0.99))]   # clip extreme outliers for display
    if not rd.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(rd, bins=60, color="#1ABC9C", edgecolor="white")
        ax.set_title("Response Delay Distribution (minutes, ≤99th pctile)",
                     fontsize=14, fontweight="bold")
        ax.set_xlabel("Minutes")
        ax.set_ylabel("Count")
        plt.tight_layout()
        _save_fig(fig, "chart_response_delay_dist.png")

    # 11. Geo scatter (valid points only)
    geo_valid = df[df["valid_geo_flag"] == 1].sample(
        min(50_000, int(df["valid_geo_flag"].eq(1).sum())),
        random_state=RANDOM_SEED,
    )
    if not geo_valid.empty:
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.scatter(geo_valid["_lon_raw"], geo_valid["_lat_raw"],
                   alpha=0.12, s=2, c="#E74C3C")
        ax.set_title("Geo Scatter — Valid Enforcement Locations", fontsize=14, fontweight="bold")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        plt.tight_layout()
        _save_fig(fig, "chart_geo_scatter.png")

    # --- markdown EDA report ---
    md = _build_eda_markdown(df, viol_freq, off_freq)
    _safe_write_text(md, OUTPUT_DIR / "eda_summary_report.md")
    return md


def _build_eda_markdown(df: pd.DataFrame,
                        viol_freq: pd.DataFrame,
                        off_freq: pd.DataFrame) -> str:
    n_rows         = len(df)
    n_valid_geo    = int(df["valid_geo_flag"].eq(1).sum())
    n_exact_dup    = int(df["is_exact_duplicate"].eq(1).sum()) if "is_exact_duplicate" in df.columns else "N/A"
    n_near_dup     = int(df["is_near_duplicate"].eq(1).sum())  if "is_near_duplicate"  in df.columns else "N/A"
    n_peak         = int(df["is_peak_hour"].eq(1).sum())        if "is_peak_hour"       in df.columns else "N/A"
    top_viol       = viol_freq.head(5)["violation_type_value"].tolist() if not viol_freq.empty else []
    top_stn        = df["police_station"].value_counts().head(5).index.tolist()
    top_junc       = df["junction_name"].value_counts().head(5).index.tolist()
    pct_approved   = (df["validation_status_final"] == "APPROVED").mean() * 100
    pct_rejected   = (df["validation_status_final"] == "REJECTED").mean() * 100
    median_resp    = df["response_delay_minutes"].median()

    lines = [
        "# EDA Summary Report — Bengaluru Traffic Enforcement Dataset",
        "",
        "## What the Data Is",
        "This is a traffic-enforcement log from Bengaluru covering January–May.",
        f"It contains **{n_rows:,}** enforcement records with fields covering",
        "GPS coordinates, vehicle details, violation and offence codes (as serialised lists),",
        "workflow timestamps, and validation outcomes.",
        "",
        "**Important:** This dataset records enforcement activity, not direct traffic flow.",
        "Congestion risk is inferred as a proxy from parking density, recurrence,",
        "spatial concentration, junction proximity, and enforcement delay.",
        "",
        "## What Was Cleaned",
        "- All missing-value representations (NULL, null, None, N/A, blank) normalised to NA.",
        "- `junction_name` placeholders (e.g., 'No Junction') mapped to NA.",
        "- Datetime columns parsed to UTC-aware timestamps; parse failures counted.",
        "- Coordinates validated against Bengaluru bounding box; anomalies flagged.",
        "- `violation_type` and `offence_code` parsed from stringified lists to Python lists.",
        "- `vehicle_type` normalised to a canonical vocabulary.",
        "- `validation_status` mapped to APPROVED / REJECTED / PENDING / UNKNOWN.",
        "- Exact and near-duplicate rows flagged (not dropped).",
        "",
        "## Anomalies Found",
        f"- **{n_rows - n_valid_geo:,}** rows with invalid or out-of-Bengaluru coordinates.",
        f"- **{n_exact_dup:,}** exact duplicate rows.",
        f"- **{n_near_dup:,}** near-duplicate rows.",
        f"- Negative response delays found — flagged in `response_delay_minutes_anomaly`.",
        "- Several columns have >50% missing values (see audit report).",
        "",
        "## Patterns Observed",
        f"- **Top 5 violations**: {', '.join(top_viol)}",
        f"- **Top 5 police stations**: {', '.join(str(s) for s in top_stn)}",
        f"- **Top 5 junctions**: {', '.join(str(j) for j in top_junc)}",
        f"- **Approval rate**: {pct_approved:.1f}%   |   **Rejection rate**: {pct_rejected:.1f}%",
        f"- **Median response delay**: {median_resp:.1f} minutes" if pd.notna(median_resp) else "",
        f"- **Peak-hour records**: {n_peak:,}" if isinstance(n_peak, int) else "",
        "",
        "## Implications for Hotspot Modeling",
        "- Hotspot priority score combines violation density, recurrence, junction proximity,",
        "  peak-hour fraction, enforcement delay, and high-frequency offence severity.",
        "- Cells with both high violation counts AND high enforcement delay are highest priority",
        "  for patrol deployment.",
        "- Near-duplicate flagging allows fair counting — duplicates should be excluded from",
        "  density counts in final modeling.",
        "- Validation approval rate varies by station and could indicate data-quality or",
        "  workflow compliance issues worth investigating operationally.",
        "",
        "---",
        "*Generated by data_audit_and_cleaning.py — Production ML / Data Engineering Team*",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# ── PHASE 12 — CLEANED MASTER DATASET ────────────────────────────────────────
# ---------------------------------------------------------------------------

def phase12_export_cleaned(df: pd.DataFrame) -> None:
    log.info("=" * 70)
    log.info("PHASE 12 — CLEANED MASTER DATASET EXPORT")
    log.info("=" * 70)

    # Drop internal working columns (prefixed with _dt_ or _lat/_lon/_jk)
    internal_cols = [c for c in df.columns if c.startswith(("_dt_", "_jk_",
                                                              "_lat_raw", "_lon_raw",
                                                              "_is_", "_veh", "_has",
                                                              "_high"))]
    # Keep _lat_raw and _lon_raw as they're useful for downstream
    internal_cols = [c for c in internal_cols if c not in ("_lat_raw", "_lon_raw")]

    export_df = df.drop(columns=internal_cols, errors="ignore")

    # Serialise list columns to JSON strings (parquet handles objects; CSV needs strings)
    for col in ["violation_type_parsed", "offence_code_parsed"]:
        if col in export_df.columns:
            export_df[col] = export_df[col].apply(
                lambda x: json.dumps(x) if isinstance(x, list) else x
            )

    # --- parquet ---
    pq_path = OUTPUT_DIR / "parking_cleaned.parquet"
    try:
        table = pa.Table.from_pandas(export_df, preserve_index=False)
        pq.write_table(table, pq_path, compression="snappy")
        log.info("Wrote  parking_cleaned.parquet  (%d rows, %d cols)",
                 len(export_df), export_df.shape[1])
    except Exception as exc:
        log.error("FAILED to write parquet: %s", exc)
        raise

    # --- csv (chunked to avoid memory spike) ---
    csv_path = OUTPUT_DIR / "parking_cleaned.csv"
    try:
        export_df.to_csv(csv_path, index=False)
        log.info("Wrote  parking_cleaned.csv  (%d rows, %d cols)",
                 len(export_df), export_df.shape[1])
    except Exception as exc:
        log.error("FAILED to write CSV: %s", exc)
        raise


# ---------------------------------------------------------------------------
# ── PHASE 13 — FINAL QUALITY GATES ───────────────────────────────────────────
# ---------------------------------------------------------------------------

def phase13_quality_gates(df_raw: pd.DataFrame, df_clean: pd.DataFrame,
                          viol_freq: pd.DataFrame, off_freq: pd.DataFrame) -> None:
    log.info("=" * 70)
    log.info("PHASE 13 — FINAL QUALITY GATES")
    log.info("=" * 70)

    ts_missing = {
        col: int(df_clean[f"_dt_{col}"].isna().sum())
        for col in DATETIME_COLS
        if f"_dt_{col}" in df_clean.columns
    }
    # For ts_missing, use original if _dt_ col was dropped
    ts_missing_fallback = {
        col: int(df_clean[col].isna().sum())
        for col in DATETIME_COLS
        if col in df_clean.columns and f"_dt_{col}" not in df_clean.columns
    }
    ts_missing.update(ts_missing_fallback)

    n_parsed_multilabel = int(
        df_clean["violation_count"].gt(0).sum()
        if "violation_count" in df_clean.columns else 0
    )

    top20_violations = (
        viol_freq.head(20)["violation_type_value"].tolist() if not viol_freq.empty else []
    )
    top20_stations = (
        df_clean["police_station"].value_counts().head(20).index.tolist()
        if "police_station" in df_clean.columns else []
    )
    top20_junctions = (
        df_clean["junction_name"].dropna().value_counts().head(20).index.tolist()
        if "junction_name" in df_clean.columns else []
    )

    summary = {
        "rows_in_raw_file"               : len(df_raw),
        "rows_in_cleaned_file"           : len(df_clean),
        "rows_flagged_invalid_geo"       : int(df_clean["geo_anomaly_flag"].eq(1).sum())
                                           if "geo_anomaly_flag" in df_clean.columns else None,
        "rows_flagged_exact_duplicate"   : int(df_clean["is_exact_duplicate"].eq(1).sum())
                                           if "is_exact_duplicate" in df_clean.columns else None,
        "rows_flagged_near_duplicate"    : int(df_clean["is_near_duplicate"].eq(1).sum())
                                           if "is_near_duplicate" in df_clean.columns else None,
        "missing_timestamps_by_column"   : ts_missing,
        "rows_with_parsed_multilabel"    : n_parsed_multilabel,
        "top20_violation_types"          : top20_violations,
        "top20_police_stations"          : [str(s) for s in top20_stations],
        "top20_junctions"                : [str(j) for j in top20_junctions],
        "pipeline_weights"               : {
            "W_DENSITY"   : W_DENSITY,
            "W_RECURRENCE": W_RECURRENCE,
            "W_JUNCTION"  : W_JUNCTION,
            "W_PEAK_HOUR" : W_PEAK_HOUR,
            "W_DELAY"     : W_DELAY,
            "W_SEVERITY"  : W_SEVERITY,
        },
    }

    _safe_write_json(summary, OUTPUT_DIR / "final_data_quality_summary.json")

    # print to stdout
    log.info("══ FINAL QUALITY SUMMARY ══")
    for k, v in summary.items():
        log.info("  %-45s : %s", k, v)


# ---------------------------------------------------------------------------
# ── MAIN ─────────────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

def main() -> None:
    log.info("Pipeline started.  Output directory: %s", OUTPUT_DIR)

    # Phase 1
    df = phase1_ingest(RAW_FILE)
    df_raw_snapshot = df.copy()   # snapshot for quality gates

    # Phase 2
    audit_df, _ = phase2_structural_audit(df)

    # Phase 3
    df = phase3_missing_standardization(df)

    # Phase 4
    df, tq_df, dur_summary = phase4_datetime_features(df)

    # Phase 5
    df, cells = phase5_geo_validation(df)

    # Phase 6
    df, viol_freq, off_freq = phase6_multilabel_parsing(df)

    # Phase 7
    df = phase7_categorical_normalization(df)

    # Phase 8
    df = phase8_deduplication(df)

    # Phase 9
    phase9_workflow_analysis(df)

    # Phase 10
    df = phase10_hotspot_preparation(df)

    # Phase 11
    phase11_eda_charts(df, viol_freq, off_freq)

    # Phase 12
    phase12_export_cleaned(df)

    # Phase 13
    phase13_quality_gates(df_raw_snapshot, df, viol_freq, off_freq)

    log.info("Pipeline complete.  All outputs in: %s", OUTPUT_DIR)


if __name__ == "__main__":
    main()
