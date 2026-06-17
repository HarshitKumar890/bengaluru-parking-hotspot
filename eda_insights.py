"""
eda_insights.py
===============
Advanced EDA and operational-intelligence layer for the Bengaluru traffic
enforcement dataset.  This script reads the cleaned parquet produced by
data_audit_and_cleaning.py and generates:

    1.  Hotspot deep-dive summaries  (top cells, ranked tables)
    2.  Temporal recurrence analysis  (by hour, day, month, peak vs off-peak)
    3.  Station-wise operational rankings
    4.  Junction-wise operational rankings
    5.  Violation taxonomy drill-down
    6.  Enforcement delay analysis
    7.  A concise markdown insight report

All charts are saved as PNG under outputs/.
The insight report is saved as outputs/insight_report.md.

Assumptions
-----------
- outputs/parking_cleaned.parquet exists (written by data_audit_and_cleaning.py)
- outputs/hotspot_priority_scores.csv exists
- outputs/violation_frequency.csv exists
- outputs/offence_frequency.csv exists

Author : Production ML / Data Engineering Team
"""

# ---------------------------------------------------------------------------
# Standard library
# ---------------------------------------------------------------------------
import json
import logging
import sys
import warnings
from pathlib import Path
from typing import List, Optional

# ---------------------------------------------------------------------------
# Third-party
# ---------------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# ── CONFIGURATION ────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

OUTPUT_DIR    = Path(r"e:\FLIPKARTGRID\Round 2\outputs")
CLEANED_PQ    = OUTPUT_DIR / "parking_cleaned.parquet"
CLEANED_CSV   = OUTPUT_DIR / "parking_cleaned.csv"

HOTSPOT_FILE  = OUTPUT_DIR / "hotspot_priority_scores.csv"
VIOL_FREQ     = OUTPUT_DIR / "violation_frequency.csv"
OFF_FREQ      = OUTPUT_DIR / "offence_frequency.csv"

RANDOM_SEED   = 42
np.random.seed(RANDOM_SEED)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# ── LOGGING ──────────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

LOG_FILE = OUTPUT_DIR / "eda_insights.log"
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


def _save_fig(fig: plt.Figure, name: str) -> None:
    """Save a matplotlib figure to outputs/ and close it."""
    path = OUTPUT_DIR / name
    try:
        fig.savefig(path, dpi=150, bbox_inches="tight")
        log.info("Saved  %s", name)
    except Exception as exc:
        log.error("FAILED to save %s: %s", name, exc)
    finally:
        plt.close(fig)


def _safe_write_csv(df: pd.DataFrame, path: Path, **kwargs) -> None:
    try:
        df.to_csv(path, index=False, **kwargs)
        log.info("Wrote  %s  (%d rows)", path.name, len(df))
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


def _bar_h(series: pd.Series, title: str, xlabel: str, fname: str,
           top_n: int = 20, color: str = "#2A6496") -> None:
    """Horizontal bar chart from a pre-counted Series (index=label, values=count)."""
    data = series.dropna().head(top_n)
    if data.empty:
        log.warning("Skipping chart '%s' — no data.", title)
        return
    fig, ax = plt.subplots(figsize=(12, max(5, top_n * 0.38)))
    ax.barh(data.index[::-1], data.values[::-1], color=color)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.tight_layout()
    _save_fig(fig, fname)


def _line_chart(series: pd.Series, title: str, xlabel: str, ylabel: str,
                fname: str, color: str = "#2A6496") -> None:
    if series.empty:
        return
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(series.index, series.values, marker="o", linewidth=2, color=color)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.tight_layout()
    _save_fig(fig, fname)


# ---------------------------------------------------------------------------
# ── DATA LOADING ─────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------


def load_cleaned_data() -> pd.DataFrame:
    """
    Load the cleaned parquet.  Falls back to CSV if parquet unavailable.
    Raises if neither file exists.
    """
    log.info("=" * 70)
    log.info("LOADING CLEANED DATASET")
    log.info("=" * 70)

    if CLEANED_PQ.exists():
        log.info("Reading  %s", CLEANED_PQ.name)
        df = pd.read_parquet(CLEANED_PQ)
    elif CLEANED_CSV.exists():
        log.warning("Parquet not found — falling back to CSV: %s", CLEANED_CSV.name)
        df = pd.read_csv(CLEANED_CSV, low_memory=False)
    else:
        raise FileNotFoundError(
            f"Neither {CLEANED_PQ} nor {CLEANED_CSV} found. "
            "Run data_audit_and_cleaning.py first."
        )

    log.info("Loaded  %d rows × %d cols  (%.1f MB)",
             len(df), df.shape[1],
             df.memory_usage(deep=True).sum() / (1024 ** 2))

    # Ensure numeric columns are numeric (parquet preserves types; CSV may not)
    for col in ["_lat_raw", "_lon_raw", "created_hour", "created_month",
                "created_year", "day_of_week", "is_peak_hour", "is_weekend",
                "valid_geo_flag", "geo_anomaly_flag", "is_exact_duplicate",
                "is_near_duplicate", "violation_count", "offence_count",
                "validation_flag_binary", "hotspot_priority_score",
                "response_delay_minutes", "closure_delay_minutes",
                "validation_delay_minutes"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Re-parse datetime cols if they are strings (CSV fallback)
    for col in ["created_datetime", "closed_datetime", "modified_datetime",
                "action_taken_timestamp", "validation_timestamp",
                "data_sent_to_scita_timestamp"]:
        if col in df.columns and df[col].dtype == object:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)

    return df


# ---------------------------------------------------------------------------
# ── SECTION 1 — HOTSPOT DEEP-DIVE ────────────────────────────────────────────
# ---------------------------------------------------------------------------


def section1_hotspot_deep_dive(df: pd.DataFrame) -> pd.DataFrame:
    """
    Load the pre-computed hotspot scores and produce ranked summaries plus charts.
    Returns the hotspot DataFrame for reuse.
    """
    log.info("=" * 70)
    log.info("SECTION 1 — HOTSPOT DEEP-DIVE")
    log.info("=" * 70)

    if not HOTSPOT_FILE.exists():
        log.warning("hotspot_priority_scores.csv not found — skipping deep-dive.")
        return pd.DataFrame()

    hs = pd.read_csv(HOTSPOT_FILE)
    log.info("Hotspot cells loaded: %d", len(hs))

    # Top 20 cells — tabular summary
    top20 = hs.head(20)[
        ["spatial_cell_id", "cell_lat_center", "cell_lon_center",
         "violation_count", "unique_vehicles", "recurrence_count",
         "peak_hour_count", "near_junction_count",
         "avg_response_delay", "hotspot_priority_score", "hotspot_rank"]
    ].copy()
    _safe_write_csv(top20, OUTPUT_DIR / "eda_hotspot_top20.csv")

    # Scatter: violation count vs priority score
    fig, ax = plt.subplots(figsize=(10, 7))
    sc = ax.scatter(
        hs["violation_count"],
        hs["hotspot_priority_score"],
        c=hs["recurrence_count"],
        cmap="YlOrRd",
        alpha=0.7,
        s=30,
        edgecolors="none",
    )
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("Recurrence Count")
    ax.set_title("Hotspot Cells — Violation Count vs Priority Score\n(colour = recurrence)",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Violation Count per Cell")
    ax.set_ylabel("Hotspot Priority Score")
    plt.tight_layout()
    _save_fig(fig, "eda_hotspot_scatter.png")

    # Spatial map: top 200 cells by priority score
    top200 = hs.head(200)
    if "cell_lat_center" in top200.columns and "cell_lon_center" in top200.columns:
        fig, ax = plt.subplots(figsize=(11, 11))
        sc2 = ax.scatter(
            top200["cell_lon_center"],
            top200["cell_lat_center"],
            c=top200["hotspot_priority_score"],
            cmap="hot_r",
            s=top200["violation_count"].clip(upper=200) * 1.2,
            alpha=0.85,
            edgecolors="white",
            linewidths=0.3,
        )
        cbar2 = fig.colorbar(sc2, ax=ax)
        cbar2.set_label("Priority Score")
        ax.set_title("Top 200 Enforcement Hotspot Cells — Bengaluru\n"
                     "(size ~ violation count, colour = priority score)",
                     fontsize=13, fontweight="bold")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        plt.tight_layout()
        _save_fig(fig, "eda_hotspot_map_top200.png")

    # Distribution of priority scores
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(hs["hotspot_priority_score"].dropna(), bins=60,
            color="#E74C3C", edgecolor="white")
    ax.set_title("Distribution of Hotspot Priority Scores", fontsize=13, fontweight="bold")
    ax.set_xlabel("Priority Score")
    ax.set_ylabel("Cell Count")
    plt.tight_layout()
    _save_fig(fig, "eda_hotspot_score_distribution.png")

    log.info("Top 5 hotspot cells:\n%s",
             top20[["spatial_cell_id", "violation_count",
                     "hotspot_priority_score"]].head(5).to_string(index=False))
    return hs


# ---------------------------------------------------------------------------
# ── SECTION 2 — TEMPORAL RECURRENCE ANALYSIS ─────────────────────────────────
# ---------------------------------------------------------------------------


def section2_temporal_recurrence(df: pd.DataFrame) -> None:
    log.info("=" * 70)
    log.info("SECTION 2 — TEMPORAL RECURRENCE ANALYSIS")
    log.info("=" * 70)

    # 2a. Violations per month
    if "created_month" in df.columns:
        monthly = df.groupby("created_month", observed=True).size()
        _line_chart(monthly, "Monthly Violation Count",
                    "Month (1=Jan … 5=May)", "Violations",
                    "eda_temporal_monthly.png", color="#2A6496")
        _safe_write_csv(
            monthly.reset_index().rename(columns={0: "count"}),
            OUTPUT_DIR / "eda_temporal_monthly.csv"
        )

    # 2b. Violations per day of week
    if "day_name" in df.columns:
        dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday",
                     "Friday", "Saturday", "Sunday"]
        dow = df["day_name"].value_counts().reindex(dow_order).dropna()
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(dow.index, dow.values,
                      color=["#E74C3C" if d in ("Saturday", "Sunday") else "#2A6496"
                             for d in dow.index])
        ax.set_title("Violations by Day of Week  (red = weekend)",
                     fontsize=13, fontweight="bold")
        ax.set_ylabel("Count")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
        plt.tight_layout()
        _save_fig(fig, "eda_temporal_dow.png")
        _safe_write_csv(
            dow.reset_index().rename(columns={"index": "day_name", "day_name": "count"}),
            OUTPUT_DIR / "eda_temporal_dow.csv"
        )

    # 2c. Hourly distribution split by peak vs off-peak
    if "created_hour" in df.columns and "is_peak_hour" in df.columns:
        hourly = df.groupby(["created_hour", "is_peak_hour"],
                             observed=True).size().reset_index(name="count")
        fig, ax = plt.subplots(figsize=(13, 5))
        for flag, colour, label in [(1, "#E74C3C", "Peak"), (0, "#2A6496", "Off-peak")]:
            sub = hourly[hourly["is_peak_hour"] == flag]
            ax.bar(sub["created_hour"] + (0.2 if flag == 1 else -0.2),
                   sub["count"], width=0.38, color=colour, label=label, alpha=0.9)
        ax.set_title("Hourly Violation Distribution — Peak vs Off-Peak",
                     fontsize=13, fontweight="bold")
        ax.set_xlabel("Hour of Day (24h)")
        ax.set_ylabel("Count")
        ax.legend()
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
        plt.tight_layout()
        _save_fig(fig, "eda_temporal_hourly_peak.png")
        _safe_write_csv(hourly, OUTPUT_DIR / "eda_temporal_hourly_peak.csv")

    # 2d. Recurrence: vehicles appearing more than once
    if "vehicle_number" in df.columns:
        veh_counts = df["vehicle_number"].value_counts()
        recurrent  = veh_counts[veh_counts > 1]
        log.info("Vehicles with >1 violation: %d / %d  (%.1f%%)",
                 len(recurrent), len(veh_counts),
                 len(recurrent) / max(len(veh_counts), 1) * 100)

        top_recurrent = recurrent.head(30)
        _bar_h(top_recurrent, "Top 30 Most Repeat-Offending Vehicles",
               "Violation Count", "eda_temporal_repeat_vehicles.png",
               top_n=30, color="#8E44AD")

        recurrence_dist = veh_counts.value_counts().sort_index().head(20)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(recurrence_dist.index.astype(str), recurrence_dist.values,
               color="#16A085")
        ax.set_title("Vehicle Recurrence Distribution\n(how many vehicles appear N times)",
                     fontsize=13, fontweight="bold")
        ax.set_xlabel("Number of violations per vehicle")
        ax.set_ylabel("Number of vehicles")
        plt.tight_layout()
        _save_fig(fig, "eda_temporal_recurrence_dist.png")

        recur_summary = pd.DataFrame({
            "n_violations_per_vehicle": recurrence_dist.index,
            "n_vehicles": recurrence_dist.values,
        })
        _safe_write_csv(recur_summary, OUTPUT_DIR / "eda_recurrence_distribution.csv")

    # 2e. Peak-hour fraction over months
    if all(c in df.columns for c in ["created_month", "is_peak_hour"]):
        peak_by_month = (
            df.groupby("created_month", observed=True)["is_peak_hour"]
            .mean()
            .mul(100)
            .round(2)
        )
        _line_chart(peak_by_month,
                    "Peak-Hour Fraction (%) by Month",
                    "Month", "% violations during peak hours",
                    "eda_temporal_peak_fraction_monthly.png",
                    color="#D35400")
        _safe_write_csv(
            peak_by_month.reset_index().rename(columns={"is_peak_hour": "peak_hour_pct"}),
            OUTPUT_DIR / "eda_temporal_peak_fraction_monthly.csv"
        )


# ---------------------------------------------------------------------------
# ── SECTION 3 — STATION-WISE RANKINGS ────────────────────────────────────────
# ---------------------------------------------------------------------------


def section3_station_rankings(df: pd.DataFrame) -> pd.DataFrame:
    log.info("=" * 70)
    log.info("SECTION 3 — STATION-WISE RANKINGS")
    log.info("=" * 70)

    if "police_station" not in df.columns:
        log.warning("police_station column missing — skipping station rankings.")
        return pd.DataFrame()

    grp = df.groupby("police_station", observed=True)

    ranks = grp.agg(
        total_cases           = ("id", "count"),
        unique_vehicles       = ("vehicle_number", "nunique"),
        n_approved            = ("validation_flag_binary", lambda x: (x == 1).sum()),
        n_rejected            = ("validation_flag_binary", lambda x: (x == 0).sum()),
        n_pending_unknown     = ("validation_status_final",
                                 lambda x: x.isin(["PENDING", "UNKNOWN"]).sum()),
        avg_response_min      = ("response_delay_minutes", "mean"),
        median_response_min   = ("response_delay_minutes", "median"),
        p95_response_min      = ("response_delay_minutes",
                                 lambda x: x.quantile(0.95)),
        avg_closure_min       = ("closure_delay_minutes", "mean"),
        avg_validation_min    = ("validation_delay_minutes", "mean"),
        peak_hour_violations  = ("is_peak_hour", lambda x: (x == 1).sum()),
    ).reset_index()

    ranks["approval_rate_pct"]   = (ranks["n_approved"]       / ranks["total_cases"] * 100).round(2)
    ranks["rejection_rate_pct"]  = (ranks["n_rejected"]       / ranks["total_cases"] * 100).round(2)
    ranks["unresolved_rate_pct"] = (ranks["n_pending_unknown"] / ranks["total_cases"] * 100).round(2)
    ranks["peak_hour_pct"]       = (ranks["peak_hour_violations"] / ranks["total_cases"] * 100).round(2)

    # Composite operational score: higher total + lower delay + higher approval
    delay_med = ranks["avg_response_min"].median()
    delay_fill = 0.0 if pd.isna(delay_med) else float(delay_med)
    delay_norm   = _minmax_series(ranks["avg_response_min"].fillna(delay_fill))
    total_norm   = _minmax_series(ranks["total_cases"].astype(float))
    approval_norm = _minmax_series(ranks["approval_rate_pct"].fillna(0))

    # High workload + high approval + low delay = high operational score
    ranks["ops_score"] = (
        0.40 * total_norm +
        0.35 * approval_norm +
        0.25 * (1 - delay_norm)  # invert: shorter delay = better
    ).round(4)

    ranks = ranks.sort_values("total_cases", ascending=False)
    ranks["volume_rank"] = range(1, len(ranks) + 1)
    ranks_by_ops = ranks.sort_values("ops_score", ascending=False).copy()
    ranks_by_ops["ops_rank"] = range(1, len(ranks_by_ops) + 1)

    _safe_write_csv(ranks.sort_values("volume_rank"),
                    OUTPUT_DIR / "eda_station_rankings.csv")

    # Charts
    _bar_h(ranks.set_index("police_station")["total_cases"],
           "Top 20 Police Stations by Case Volume",
           "Total Cases", "eda_station_volume.png", color="#2A6496")

    _bar_h(ranks.set_index("police_station")["approval_rate_pct"],
           "Top 20 Police Stations by Approval Rate (%)",
           "Approval Rate %", "eda_station_approval_rate.png",
           top_n=20, color="#27AE60")

    # Grouped bar: approval rate vs rejection rate for top 15 stations
    top15 = ranks.head(15).copy()
    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(top15))
    w = 0.35
    ax.bar(x - w/2, top15["approval_rate_pct"], width=w,
           label="Approval %", color="#27AE60", alpha=0.9)
    ax.bar(x + w/2, top15["rejection_rate_pct"], width=w,
           label="Rejection %", color="#E74C3C", alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(top15["police_station"], rotation=45, ha="right", fontsize=8)
    ax.set_title("Approval vs Rejection Rate — Top 15 Stations by Volume",
                 fontsize=13, fontweight="bold")
    ax.set_ylabel("Rate (%)")
    ax.legend()
    plt.tight_layout()
    _save_fig(fig, "eda_station_approval_vs_rejection.png")

    # Response delay boxplot for top 15 stations
    valid_delay = df[
        df["police_station"].isin(top15["police_station"].tolist()) &
        df["response_delay_minutes"].notna() &
        (df["response_delay_minutes"] >= 0)
    ].copy()
    if not valid_delay.empty:
        cap = valid_delay["response_delay_minutes"].quantile(0.97)
        valid_delay["response_delay_minutes"] = valid_delay["response_delay_minutes"].clip(upper=cap)
        order = top15["police_station"].tolist()
        fig, ax = plt.subplots(figsize=(14, 7))
        valid_delay.boxplot(column="response_delay_minutes", by="police_station",
                            ax=ax, vert=False,
                            boxprops=dict(color="#2A6496"),
                            medianprops=dict(color="#E74C3C", linewidth=2),
                            flierprops=dict(marker=".", alpha=0.3, markersize=3))
        ax.set_title("Response Delay Distribution by Station (top 15, capped 97th pctile)",
                     fontsize=12, fontweight="bold")
        plt.suptitle("")
        ax.set_xlabel("Response Delay (minutes)")
        plt.tight_layout()
        _save_fig(fig, "eda_station_response_delay_box.png")

    log.info("Top 5 stations by volume:\n%s",
             ranks[["police_station", "total_cases",
                     "approval_rate_pct"]].head(5).to_string(index=False))
    return ranks


# ---------------------------------------------------------------------------
# ── SECTION 4 — JUNCTION-WISE RANKINGS ───────────────────────────────────────
# ---------------------------------------------------------------------------


def section4_junction_rankings(df: pd.DataFrame) -> pd.DataFrame:
    log.info("=" * 70)
    log.info("SECTION 4 — JUNCTION-WISE RANKINGS")
    log.info("=" * 70)

    if "junction_name" not in df.columns or df["junction_name"].notna().sum() == 0:
        log.warning("junction_name is entirely null — skipping junction rankings.")
        return pd.DataFrame()

    jdf = df[df["junction_name"].notna()].copy()

    grp = jdf.groupby("junction_name", observed=True)

    junction_ranks = grp.agg(
        total_cases           = ("id", "count"),
        unique_vehicles       = ("vehicle_number", "nunique"),
        n_approved            = ("validation_flag_binary", lambda x: (x == 1).sum()),
        n_rejected            = ("validation_flag_binary", lambda x: (x == 0).sum()),
        avg_response_min      = ("response_delay_minutes", "mean"),
        peak_hour_violations  = ("is_peak_hour", lambda x: (x == 1).sum()),
        n_recurrent           = ("is_near_duplicate", lambda x: (x == 1).sum()
                                  if "is_near_duplicate" in df.columns else 0),
    ).reset_index()

    junction_ranks["approval_rate_pct"]  = (
        junction_ranks["n_approved"] / junction_ranks["total_cases"] * 100
    ).round(2)
    junction_ranks["peak_hour_pct"]      = (
        junction_ranks["peak_hour_violations"] / junction_ranks["total_cases"] * 100
    ).round(2)
    junction_ranks = junction_ranks.sort_values("total_cases", ascending=False)
    junction_ranks["volume_rank"] = range(1, len(junction_ranks) + 1)

    _safe_write_csv(junction_ranks, OUTPUT_DIR / "eda_junction_rankings.csv")

    _bar_h(junction_ranks.set_index("junction_name")["total_cases"],
           "Top 20 Junctions by Violation Volume",
           "Total Cases", "eda_junction_volume.png", top_n=20, color="#D35400")

    _bar_h(junction_ranks.set_index("junction_name")["peak_hour_pct"],
           "Top 20 Junctions by Peak-Hour Violation %",
           "Peak-Hour %", "eda_junction_peak_hour.png",
           top_n=20, color="#E74C3C")

    log.info("Top 5 junctions by volume:\n%s",
             junction_ranks[["junction_name", "total_cases",
                              "peak_hour_pct"]].head(5).to_string(index=False))
    return junction_ranks


# ---------------------------------------------------------------------------
# ── SECTION 5 — VIOLATION TAXONOMY DRILL-DOWN ────────────────────────────────
# ---------------------------------------------------------------------------


def section5_violation_taxonomy(df: pd.DataFrame) -> None:
    log.info("=" * 70)
    log.info("SECTION 5 — VIOLATION TAXONOMY DRILL-DOWN")
    log.info("=" * 70)

    # Load pre-computed frequency tables
    if VIOL_FREQ.exists():
        viol_freq = pd.read_csv(VIOL_FREQ)
        log.info("Violation types loaded: %d unique", len(viol_freq))
    else:
        log.warning("violation_frequency.csv not found — using primary_violation_type.")
        viol_freq = (
            df["primary_violation_type"]
            .value_counts()
            .reset_index()
            .rename(columns={"primary_violation_type": "violation_type_value",
                              "count": "frequency"})
        )

    if OFF_FREQ.exists():
        off_freq = pd.read_csv(OFF_FREQ)
        log.info("Offence codes loaded: %d unique", len(off_freq))
    else:
        log.warning("offence_frequency.csv not found — using primary_offence_code.")
        off_freq = (
            df["primary_offence_code"]
            .value_counts()
            .reset_index()
            .rename(columns={"primary_offence_code": "offence_code_value",
                             "count": "frequency"})
        )

    # Top-20 violation type bar
    if not viol_freq.empty:
        top_v = viol_freq.head(20).set_index("violation_type_value")["frequency"]
        _bar_h(top_v, "Top 20 Violation Types", "Count",
               "eda_taxonomy_violations.png", color="#2A6496")

    # Top-20 offence code bar
    if not off_freq.empty:
        top_o = off_freq.head(20).set_index("offence_code_value")["frequency"]
        _bar_h(top_o, "Top 20 Offence Codes", "Count",
               "eda_taxonomy_offences.png", color="#E74C3C")

    # Violation count distribution per record
    if "violation_count" in df.columns:
        vc_dist = df["violation_count"].value_counts().sort_index().head(15)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(vc_dist.index.astype(str), vc_dist.values, color="#1ABC9C")
        ax.set_title("Distribution of Violation Count per Record",
                     fontsize=13, fontweight="bold")
        ax.set_xlabel("# violation types per record")
        ax.set_ylabel("# records")
        plt.tight_layout()
        _save_fig(fig, "eda_taxonomy_violation_count_dist.png")

    # Violation type × vehicle type heatmap (top 10 × top 10)
    if all(c in df.columns for c in ["primary_violation_type", "vehicle_type_final"]):
        top_vt = viol_freq.head(10)["violation_type_value"].tolist() if not viol_freq.empty else []
        top_vh = df["vehicle_type_final"].value_counts().head(10).index.tolist()
        cross = (
            df[
                df["primary_violation_type"].isin(top_vt) &
                df["vehicle_type_final"].isin(top_vh)
            ]
            .groupby(["primary_violation_type", "vehicle_type_final"], observed=True)
            .size()
            .unstack(fill_value=0)
        )
        if not cross.empty:
            fig, ax = plt.subplots(figsize=(14, 6))
            sns.heatmap(cross, annot=True, fmt=",d", cmap="YlOrRd",
                        linewidths=0.3, ax=ax, cbar_kws={"shrink": 0.7})
            ax.set_title("Violation Type × Vehicle Type  (top 10 each)",
                         fontsize=13, fontweight="bold")
            ax.set_xlabel("Vehicle Type")
            ax.set_ylabel("Violation Type")
            plt.tight_layout()
            _save_fig(fig, "eda_taxonomy_violation_vehicle_heatmap.png")

    # Violations per hour for top 5 violation types
    if all(c in df.columns for c in ["primary_violation_type", "created_hour"]):
        top5_viol = viol_freq.head(5)["violation_type_value"].tolist() if not viol_freq.empty else []
        if top5_viol:
            sub = df[df["primary_violation_type"].isin(top5_viol)].copy()
            pivot = (
                sub.groupby(["created_hour", "primary_violation_type"], observed=True)
                .size()
                .unstack(fill_value=0)
            )
            fig, ax = plt.subplots(figsize=(13, 6))
            for col in pivot.columns:
                ax.plot(pivot.index, pivot[col], marker=".", label=col, linewidth=1.5)
            ax.set_title("Hourly Trend for Top 5 Violation Types",
                         fontsize=13, fontweight="bold")
            ax.set_xlabel("Hour of Day")
            ax.set_ylabel("Count")
            ax.legend(fontsize=7, loc="upper right")
            plt.tight_layout()
            _save_fig(fig, "eda_taxonomy_violation_hourly_top5.png")


# ---------------------------------------------------------------------------
# ── SECTION 6 — ENFORCEMENT DELAY ANALYSIS ───────────────────────────────────
# ---------------------------------------------------------------------------


def section6_enforcement_delay(df: pd.DataFrame) -> None:
    log.info("=" * 70)
    log.info("SECTION 6 — ENFORCEMENT DELAY ANALYSIS")
    log.info("=" * 70)

    delay_cols = {
        "response_delay_minutes"    : "Action Taken Delay",
        "closure_delay_minutes"     : "Case Closure Delay",
        "validation_delay_minutes"  : "Validation Delay",
        "scita_delay_minutes"       : "SCITA Transmission Delay",
        "modification_delay_minutes": "Record Modification Delay",
    }

    summary_rows = []
    for col, label in delay_cols.items():
        if col not in df.columns:
            continue
        s = df[col].dropna()
        pos = s[s >= 0]  # exclude anomalies
        if pos.empty:
            continue
        cap = pos.quantile(0.99)
        pos_capped = pos.clip(upper=cap)

        summary_rows.append({
            "delay_type" : label,
            "column"     : col,
            "n_valid"    : len(pos),
            "n_negative" : int((s < 0).sum()),
            "mean_min"   : round(pos.mean(), 2),
            "median_min" : round(pos.median(), 2),
            "p95_min"    : round(pos.quantile(0.95), 2),
            "p99_min"    : round(pos.quantile(0.99), 2),
            "max_min"    : round(pos.max(), 2),
        })

        # Histogram per delay type
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.hist(pos_capped, bins=60, color="#2980B9", edgecolor="white")
        ax.axvline(pos.median(), color="#E74C3C", linestyle="--",
                   linewidth=1.5, label=f"Median: {pos.median():.1f} min")
        ax.set_title(f"{label} Distribution  (capped at 99th pctile: {cap:.0f} min)",
                     fontsize=12, fontweight="bold")
        ax.set_xlabel("Minutes")
        ax.set_ylabel("Count")
        ax.legend()
        plt.tight_layout()
        _save_fig(fig, f"eda_delay_{col}.png")

    if summary_rows:
        delay_summary_df = pd.DataFrame(summary_rows)
        _safe_write_csv(delay_summary_df, OUTPUT_DIR / "eda_delay_summary.csv")
        log.info("Delay summary:\n%s",
                 delay_summary_df[["delay_type", "median_min",
                                   "p95_min", "n_negative"]].to_string(index=False))

    # Delay trend over months
    if all(c in df.columns for c in ["created_month", "response_delay_minutes"]):
        delay_monthly = (
            df[df["response_delay_minutes"] >= 0]
            .groupby("created_month", observed=True)["response_delay_minutes"]
            .median()
        )
        _line_chart(delay_monthly,
                    "Median Response Delay by Month",
                    "Month", "Median Delay (minutes)",
                    "eda_delay_response_monthly.png", color="#E74C3C")

    # Response delay by validation status
    if all(c in df.columns for c in ["validation_status_final", "response_delay_minutes"]):
        valid_rows = df[
            df["response_delay_minutes"].notna() &
            (df["response_delay_minutes"] >= 0) &
            df["validation_status_final"].notna()
        ].copy()
        cap = valid_rows["response_delay_minutes"].quantile(0.97)
        valid_rows["response_delay_minutes"] = valid_rows["response_delay_minutes"].clip(upper=cap)

        if not valid_rows.empty:
            fig, ax = plt.subplots(figsize=(9, 5))
            valid_rows.boxplot(column="response_delay_minutes",
                               by="validation_status_final", ax=ax,
                               boxprops=dict(color="#2A6496"),
                               medianprops=dict(color="#E74C3C", linewidth=2),
                               flierprops=dict(marker=".", alpha=0.3, markersize=3))
            ax.set_title("Response Delay by Validation Status",
                         fontsize=12, fontweight="bold")
            plt.suptitle("")
            ax.set_xlabel("Validation Status")
            ax.set_ylabel("Response Delay (minutes, capped 97th pctile)")
            plt.tight_layout()
            _save_fig(fig, "eda_delay_by_validation_status.png")


# ---------------------------------------------------------------------------
# ── SECTION 7 — INSIGHT REPORT ───────────────────────────────────────────────
# ---------------------------------------------------------------------------


def section7_insight_report(
    df: pd.DataFrame,
    hs_df: pd.DataFrame,
    station_ranks: pd.DataFrame,
    junction_ranks: pd.DataFrame,
) -> None:
    log.info("=" * 70)
    log.info("SECTION 7 — MARKDOWN INSIGHT REPORT")
    log.info("=" * 70)

    n_rows     = len(df)
    n_valid_geo = int(df["valid_geo_flag"].eq(1).sum()) if "valid_geo_flag" in df.columns else 0

    # Key stats
    top5_stations = (station_ranks.head(5)["police_station"].tolist()
                     if not station_ranks.empty else [])
    top5_junctions = (junction_ranks.head(5)["junction_name"].tolist()
                      if not junction_ranks.empty else [])
    top3_hotspots  = (hs_df.head(3)["spatial_cell_id"].tolist()
                      if not hs_df.empty else [])

    pct_approved = (df["validation_status_final"].eq("APPROVED").mean() * 100
                    if "validation_status_final" in df.columns else float("nan"))
    pct_rejected = (df["validation_status_final"].eq("REJECTED").mean() * 100
                    if "validation_status_final" in df.columns else float("nan"))

    median_resp   = (df["response_delay_minutes"][df["response_delay_minutes"] >= 0].median()
                     if "response_delay_minutes" in df.columns else float("nan"))
    peak_pct      = (df["is_peak_hour"].eq(1).mean() * 100
                     if "is_peak_hour" in df.columns else float("nan"))

    # Top violation
    top_viol = "N/A"
    if VIOL_FREQ.exists():
        vf = pd.read_csv(VIOL_FREQ)
        if not vf.empty:
            top_viol = vf.iloc[0]["violation_type_value"]

    lines = [
        "# Bengaluru Traffic Enforcement — EDA Insight Report",
        "",
        "> **Scope**: Jan–May enforcement records (~298 k rows).  "
        "All congestion signals are *proxy metrics* derived from enforcement data — "
        "not direct traffic-flow measurements.",
        "",
        "---",
        "",
        "## 1. Dataset Overview",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total records | {n_rows:,} |",
        f"| Records with valid GPS (within Bengaluru bbox) | {n_valid_geo:,} |",
        f"| Approval rate | {pct_approved:.1f}% |",
        f"| Rejection rate | {pct_rejected:.1f}% |",
        f"| Median response delay | {median_resp:.1f} min |",
        f"| % violations during peak hours | {peak_pct:.1f}% |",
        "",
        "---",
        "",
        "## 2. Hotspot Intelligence",
        "",
        "Hotspot priority scores combine violation density (30%), recurrence (20%), "
        "junction proximity (15%), peak-hour fraction (15%), enforcement delay (10%), "
        "and offence severity proxy (10%).",
        "",
    ]

    if not hs_df.empty:
        top10 = hs_df.head(10)[
            ["spatial_cell_id", "cell_lat_center", "cell_lon_center",
             "violation_count", "hotspot_priority_score", "hotspot_rank"]
        ].copy()
        top10.columns = ["Cell ID", "Lat", "Lon", "Violations", "Priority Score", "Rank"]
        lines.append(top10.to_markdown(index=False))
        lines.append("")
        lines.append(f"**Top 3 cells for patrol deployment**: {', '.join(top3_hotspots)}")
        lines.append("")

    lines += [
        "---",
        "",
        "## 3. Temporal Patterns",
        "",
        "- Violations are not uniformly distributed across hours.",
        f"  **{peak_pct:.1f}%** of records fall within defined peak windows "
        "(07:00–10:59 and 17:00–20:59).",
        "- Weekend enforcement volume differs from weekdays — see `eda_temporal_dow.png`.",
        "- Monthly trends reveal seasonal or operational enforcement cycles.",
        "",
        "---",
        "",
        "## 4. Station-Wise Intelligence",
        "",
    ]

    if not station_ranks.empty:
        top10_stn = station_ranks.head(10)[
            ["police_station", "total_cases", "approval_rate_pct",
             "rejection_rate_pct", "median_response_min"]
        ].copy()
        top10_stn.columns = ["Station", "Cases", "Approval %", "Rejection %", "Median Resp (min)"]
        lines.append(top10_stn.round(1).to_markdown(index=False))
        lines.append("")

    if top5_stations:
        lines.append(f"**Highest-volume stations**: {', '.join(str(s) for s in top5_stations)}")
        lines.append("")

    lines += [
        "---",
        "",
        "## 5. Junction-Wise Intelligence",
        "",
    ]

    if not junction_ranks.empty:
        top10_jn = junction_ranks.head(10)[
            ["junction_name", "total_cases", "peak_hour_pct", "approval_rate_pct"]
        ].copy()
        top10_jn.columns = ["Junction", "Cases", "Peak-Hour %", "Approval %"]
        lines.append(top10_jn.round(1).to_markdown(index=False))
        lines.append("")

    if top5_junctions:
        lines.append(f"**Highest-volume junctions**: {', '.join(str(j) for j in top5_junctions)}")
        lines.append("")

    lines += [
        "---",
        "",
        "## 6. Violation Taxonomy",
        "",
        f"- Most common violation type: **{top_viol}**",
        "- `violation_type` and `offence_code` fields contain serialised lists — "
        "a single record can carry multiple violation labels.",
        "- Multi-label parsing was applied; see `violation_frequency.csv` and "
        "`offence_frequency.csv` for full distributions.",
        "- See `eda_taxonomy_violation_vehicle_heatmap.png` for vehicle × violation breakdown.",
        "",
        "---",
        "",
        "## 7. Enforcement Delay Analysis",
        "",
        f"- **Median response delay**: {median_resp:.1f} minutes",
        "- Negative delays (anomalies) are present and have been flagged but not removed.",
        "- High p99 delays in some stations suggest chronic backlogs.",
        "- Stations with simultaneously high volume and high delay are the most urgent "
        "candidates for process improvement.",
        "- See `eda_delay_summary.csv` for a full breakdown by delay type.",
        "",
        "---",
        "",
        "## 8. Recommendations for Downstream Modeling",
        "",
        "1. **Hotspot detection** — Use `spatial_cell_id` + `hotspot_priority_score` as "
        "primary grouping and ranking keys.",
        "2. **Deduplication** — Exclude `is_exact_duplicate=1` and consider excluding "
        "`is_near_duplicate=1` from density counts.",
        "3. **Temporal features** — `is_peak_hour`, `day_of_week`, `created_month` are "
        "ready-to-use model features.",
        "4. **Label proxy** — `validation_flag_binary` (APPROVED=1, REJECTED=0) can serve "
        "as a weak supervision signal for enforcement quality models.",
        "5. **Coordinate quality** — Only use `valid_geo_flag=1` rows for spatial models.",
        "6. **External data gap** — True congestion prediction requires traffic-flow "
        "measurements (speed, density) not present in this dataset.",
        "",
        "---",
        "",
        "*Generated by eda_insights.py — Production ML / Data Engineering Team*",
    ]

    md = "\n".join(lines)
    _safe_write_text(md, OUTPUT_DIR / "insight_report.md")
    log.info("Insight report written.")


# ---------------------------------------------------------------------------
# ── UTILITY ──────────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------


def _minmax_series(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    mn, mx = s.min(), s.max()
    if pd.isna(mn) or pd.isna(mx) or mx == mn:
        return pd.Series(0.0, index=s.index)
    return (s - mn) / (mx - mn)


# ---------------------------------------------------------------------------
# ── MAIN ─────────────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------


def main() -> None:
    log.info("EDA Insights pipeline started.  Output dir: %s", OUTPUT_DIR)

    sns.set_theme(style="whitegrid", palette="muted")

    # Load cleaned data
    df = load_cleaned_data()

    # Section 1 — Hotspot deep-dive
    hs_df = section1_hotspot_deep_dive(df)

    # Section 2 — Temporal recurrence
    section2_temporal_recurrence(df)

    # Section 3 — Station rankings
    station_ranks = section3_station_rankings(df)

    # Section 4 — Junction rankings
    junction_ranks = section4_junction_rankings(df)

    # Section 5 — Violation taxonomy
    section5_violation_taxonomy(df)

    # Section 6 — Enforcement delay
    section6_enforcement_delay(df)

    # Section 7 — Insight report
    section7_insight_report(df, hs_df, station_ranks, junction_ranks)

    log.info("EDA Insights pipeline complete.  All outputs in: %s", OUTPUT_DIR)


if __name__ == "__main__":
    main()
