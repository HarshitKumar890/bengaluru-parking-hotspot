# Theme Alignment Report
## Bengaluru Parking Hotspot Intelligence — Challenge Alignment

---

## 1. Why Direct Congestion Prediction Is Impossible With This Dataset

The provided dataset contains **298,450 parking enforcement records** with GPS
coordinates, violation types, timestamps, and validation workflow data.

It does NOT contain:
- Traffic speed measurements
- Vehicle flow counts
- Road occupancy data
- Queue length observations
- Travel time records
- Congestion index values

Congestion is defined as a measurable reduction in traffic flow or speed.
Without any of these measurements, any claim of "congestion prediction" would be
fabricated. Generating synthetic congestion labels from enforcement counts alone
would constitute scientifically invalid label invention.

---

## 2. Why Congestion Risk Estimation Is the Correct Approach

Illegal parking creates congestion conditions through a well-documented causal chain:
1. Illegal parking → lane blockage or footpath obstruction
2. Lane blockage → reduced road capacity
3. Reduced road capacity → speed reduction and queue formation
4. Junction-adjacent parking → intersection throughput degradation

We cannot measure the END of this chain (actual congestion) with this dataset.
But we CAN estimate the BEGINNING of this chain — the spatial density, persistence,
and severity of illegal parking events.

The **Parking-Induced Congestion Risk Score** is therefore defined as:

> An evidence-based composite index that estimates the likelihood of traffic
> disruption conditions arising from parking violations at a given location,
> based on violation density, recurrence, junction proximity, and violation
> severity — NOT measured traffic flow.

---

## 3. How Hotspot Forecasting Supports Proactive Enforcement

The LightGBM forecasting model (Recall@20 = 0.775 on primary folds) predicts
which 500m spatial zones will accumulate the most parking violations in the
next calendar month. This enables:

- Pre-positioning patrol vehicles at high-probability hotspots **before** violations peak
- Shifting from reactive (respond to complaint) to predictive deployment
- Allocating limited enforcement resources to highest-impact zones

Historical analysis confirms structural persistence: all top-20 cells remained
in the top-20 across every consecutive month pair (mean overlap = 77%).
The model improves this to R@20 = 0.775, correctly identifying 15–16 of the
true 20 worst zones in advance.

---

## 4. How Congestion Risk Prioritization Improves Patrol Allocation

Two cells may have similar forecasted violation counts but different congestion
risk levels. Example:

- Cell A: 500 violations/month, all "WRONG PARKING" in a side street → LOW risk
- Cell B: 300 violations/month, "PARKING NEAR ROAD CROSSING" at a junction → HIGH risk

The congestion risk score correctly elevates Cell B despite lower volume,
because junction-adjacent road-crossing violations have higher traffic
disruption potential.

This allows enforcement commanders to distinguish between:
- High-volume, low-risk zones (fine revenue focus)
- Moderate-volume, high-risk zones (traffic safety focus)

---

## 5. Operational Decisions Enabled by This Output

| Decision | Enabled By |
|---|---|
| Where to deploy patrols next month | `enhanced_patrol_priority.csv` (LightGBM forecast) |
| Which zones are structurally persistent | `hotspot_stability_labels.csv` |
| Which zones pose highest congestion risk | `congestion_risk_labels.csv` |
| Why a specific zone is high-risk | `top50_risk_explanations.csv` |
| Geographic distribution of risk | `congestion_risk_heatmap.csv` |
| Combined patrol + risk ranking | `hotspot_risk_table.csv` |

---

## 6. What This System Does NOT Claim

- It does NOT predict traffic speed or flow
- It does NOT predict queue lengths
- It does NOT replace traffic sensors or probe vehicle data
- It does NOT produce congestion indices comparable to Google Maps or HERE
- It DOES produce an enforcement-priority ranking backed by historical violation data
  and a scientifically justified risk proxy

---

*This report is part of the Bengaluru Parking Hotspot Intelligence project.
All claims are bounded by the available data and validated against held-out
temporal folds using Recall@K and Spearman rank correlation.*
