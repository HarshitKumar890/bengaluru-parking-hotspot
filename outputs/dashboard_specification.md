# Dashboard Specification
## Bengaluru Parking Hotspot Intelligence — Streamlit Dashboard

---

## Page 1: Executive Overview

**Purpose**: One-screen summary for decision-makers.

Components:
- KPI tiles: Total hotspots monitored | Top-20 CRITICAL risk zones | Persistent cells count | Top station by volume
- Bar chart: Top-10 patrol priority cells by forecasted count
- Pie chart: Risk category distribution (LOW / MODERATE / HIGH / CRITICAL)
- Text box: "This system predicts parking violation hotspots and estimates
  parking-induced congestion risk. It does not measure actual traffic flow."

Data source: `hotspot_risk_table.csv`, `congestion_risk_labels.csv`

---

## Page 2: Hotspot Map

**Purpose**: Geographic view of all forecasted hotspots.

Components:
- Interactive Folium/Pydeck scatter map of Bengaluru
- Point size proportional to `forecasted_count`
- Colour by `stability_class`: Persistent=red, Volatile=orange, Emerging=green, Declining=grey
- Hover tooltip: cell_id, forecasted_count, stability_class, police_station
- Filter panel: Police station | Stability class | Min forecasted count

Data source: `top50_hotspots.csv`, `hotspot_heatmap.csv`

---

## Page 3: Congestion Risk Map

**Purpose**: Geographic view of parking-induced congestion risk.

Components:
- Choropleth or heatmap layer on Bengaluru map
- Colour by `congestion_risk_score` (green→red gradient)
- Overlay: junction locations (from junction_name field)
- Risk category legend: LOW / MODERATE / HIGH / CRITICAL
- **Disclaimer banner**: "Congestion risk is estimated from parking data only.
  It is not a measured traffic congestion index."
- Hover: spatial_cell_id, risk_score, risk_category, police_station

Data source: `congestion_risk_heatmap.csv`

---

## Page 4: Top Patrol Recommendations

**Purpose**: Actionable patrol deployment list.

Components:
- Ranked table: Top-20 cells sorted by priority_score
- Columns: Rank | Cell | Predicted Violations | Risk Category | Stability | Station | Explanation
- Highlight CRITICAL risk cells in red
- Export button: Download as PDF / CSV
- Risk explanation column from `top50_risk_explanations.csv`

Data source: `top20_patrol_recommendations.csv`, `hotspot_risk_table.csv`, `top50_risk_explanations.csv`

---

## Page 5: Station Analytics

**Purpose**: Performance comparison across police stations.

Components:
- Bar chart: Cases by station (top 15)
- Grouped bar: Approval rate vs Rejection rate by station
- Line chart: Monthly case volume trend by station (top 5 stations)
- Table: Station | Cases | Approval% | Unresolved% | Median Validation Delay | # Active Cells
- Selector: Click on station to see its hotspot cells on map

Data source: `eda_station_rankings.csv`, `workflow_metrics_by_station.csv`

---

## Page 6: Hotspot Stability Analytics

**Purpose**: Understand long-term hotspot behavior.

Components:
- Donut chart: Stability class distribution
- Scatter plot: recurrence_rate (x) vs mean_monthly count (y), coloured by stability_class
- Line chart: Monthly count trend for top-5 Persistent cells
- Table: Cell | Stability | Active Months | Mean Monthly | Trend | Risk Category
- Filter: Show only CRITICAL risk Persistent cells

Data source: `hotspot_stability_labels.csv`, `congestion_risk_labels.csv`

---

## Technical Stack
- Streamlit (Python)
- Folium or Pydeck for maps
- Plotly for charts
- Pandas for data loading
- All data from `outputs/` directory — no live database required

## Disclaimer Component (all pages)
```
⚠️ This system estimates parking-induced congestion risk from enforcement records.
It does not measure or predict actual traffic congestion, speed, or flow.
```
