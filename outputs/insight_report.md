# Bengaluru Traffic Enforcement — EDA Insight Report

> **Scope**: Jan–May enforcement records (~298 k rows).  All congestion signals are *proxy metrics* derived from enforcement data — not direct traffic-flow measurements.

---

## 1. Dataset Overview

| Metric | Value |
|--------|-------|
| Total records | 298,450 |
| Records with valid GPS (within Bengaluru bbox) | 298,282 |
| Approval rate | 38.7% |
| Rejection rate | 16.7% |
| Median response delay | <NA> min |
| % violations during peak hours | 17.5% |

---

## 2. Hotspot Intelligence

Hotspot priority scores combine violation density (30%), recurrence (20%), junction proximity (15%), peak-hour fraction (15%), enforcement delay (10%), and offence severity proxy (10%).

| Cell ID         |     Lat |     Lon |   Violations |   Priority Score |   Rank |
|:----------------|--------:|--------:|-------------:|-----------------:|-------:|
| CELL_2595_15515 | 12.9772 | 77.5772 |        20798 |         0.78528  |      1 |
| CELL_2592_15515 | 12.964  | 77.577  |        10409 |         0.454029 |      2 |
| CELL_2596_15521 | 12.9819 | 77.6079 |         9209 |         0.411855 |      3 |
| CELL_2596_15522 | 12.9816 | 77.6108 |         8674 |         0.35995  |      4 |
| CELL_2586_15538 | 12.9335 | 77.6911 |         6705 |         0.337245 |      5 |
| CELL_2594_15515 | 12.973  | 77.5783 |         6833 |         0.326213 |      6 |
| CELL_2595_15514 | 12.9776 | 77.5732 |         5144 |         0.272296 |      7 |
| CELL_2596_15520 | 12.9835 | 77.6033 |         4836 |         0.260844 |      8 |
| CELL_2599_15509 | 12.9986 | 77.5489 |         4611 |         0.259637 |      9 |
| CELL_2614_15517 | 13.0711 | 77.588  |         5378 |         0.254935 |     10 |

**Top 3 cells for patrol deployment**: CELL_2595_15515, CELL_2592_15515, CELL_2596_15521

---

## 3. Temporal Patterns

- Violations are not uniformly distributed across hours.
  **17.5%** of records fall within defined peak windows (07:00–10:59 and 17:00–20:59).
- Weekend enforcement volume differs from weekdays — see `eda_temporal_dow.png`.
- Monthly trends reveal seasonal or operational enforcement cycles.

---

## 4. Station-Wise Intelligence

| Station           |   Cases |   Approval % |   Rejection % | Median Resp (min)   |
|:------------------|--------:|-------------:|--------------:|:--------------------|
| UPPARPET          |   34468 |         44.7 |          13.9 | <NA>                |
| SHIVAJINAGAR      |   28044 |         39.3 |          20.2 | <NA>                |
| MALLESHWARAM      |   22200 |         38.2 |          13.9 | <NA>                |
| HAL OLD AIRPORT   |   20819 |         37.2 |          17.4 | <NA>                |
| CITY MARKET       |   17646 |         34.9 |          16.8 | <NA>                |
| VIJAYANAGARA      |   14652 |         42.6 |          20.5 | <NA>                |
| RAJAJINAGAR       |   10998 |         36.7 |          17.1 | <NA>                |
| KODIGEHALLI       |   10916 |         21.6 |          15.2 | <NA>                |
| MAGADI ROAD       |    8558 |         38.6 |          19.9 | <NA>                |
| JEEVANBHEEMANAGAR |    6736 |         46.1 |          13   | <NA>                |

**Highest-volume stations**: UPPARPET, SHIVAJINAGAR, MALLESHWARAM, HAL OLD AIRPORT, CITY MARKET

---

## 5. Junction-Wise Intelligence

| Junction                           |   Cases |   Peak-Hour % |   Approval % |
|:-----------------------------------|--------:|--------------:|-------------:|
| BTP051 - Safina Plaza Junction     |   15449 |          13.7 |         38.1 |
| BTP082 - KR Market Junction        |   11538 |          35.3 |         32.8 |
| BTP040 - Elite Junction            |   10718 |          14.9 |         43.9 |
| BTP044 - Sagar Theatre Junction    |   10549 |          12.6 |         42.4 |
| BTP211 - Central Street Junction   |    5388 |          18.1 |         41.8 |
| BTP058 - Subbanna Junction         |    5189 |          42.8 |         44.7 |
| BTP027 - Modi Bridge Junction      |    4584 |           7.1 |         34.6 |
| BTP020 - Hosahalli Metro Station   |    4101 |           4.8 |         44.4 |
| BTP057 - Anand Rao Junction        |    3935 |          24.4 |         46.1 |
| BTP080 - NR Road, SP Road Junction |    3681 |           6.6 |         34.7 |

**Highest-volume junctions**: BTP051 - Safina Plaza Junction, BTP082 - KR Market Junction, BTP040 - Elite Junction, BTP044 - Sagar Theatre Junction, BTP211 - Central Street Junction

---

## 6. Violation Taxonomy

- Most common violation type: **WRONG PARKING**
- `violation_type` and `offence_code` fields contain serialised lists — a single record can carry multiple violation labels.
- Multi-label parsing was applied; see `violation_frequency.csv` and `offence_frequency.csv` for full distributions.
- See `eda_taxonomy_violation_vehicle_heatmap.png` for vehicle × violation breakdown.

---

## 7. Enforcement Delay Analysis

- **Median response delay**: <NA> minutes
- Negative delays (anomalies) are present and have been flagged but not removed.
- High p99 delays in some stations suggest chronic backlogs.
- Stations with simultaneously high volume and high delay are the most urgent candidates for process improvement.
- See `eda_delay_summary.csv` for a full breakdown by delay type.

---

## 8. Recommendations for Downstream Modeling

1. **Hotspot detection** — Use `spatial_cell_id` + `hotspot_priority_score` as primary grouping and ranking keys.
2. **Deduplication** — Exclude `is_exact_duplicate=1` and consider excluding `is_near_duplicate=1` from density counts.
3. **Temporal features** — `is_peak_hour`, `day_of_week`, `created_month` are ready-to-use model features.
4. **Label proxy** — `validation_flag_binary` (APPROVED=1, REJECTED=0) can serve as a weak supervision signal for enforcement quality models.
5. **Coordinate quality** — Only use `valid_geo_flag=1` rows for spatial models.
6. **External data gap** — True congestion prediction requires traffic-flow measurements (speed, density) not present in this dataset.

---

*Generated by eda_insights.py — Production ML / Data Engineering Team*