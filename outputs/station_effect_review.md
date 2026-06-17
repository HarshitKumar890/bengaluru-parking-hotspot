# Station Effect Review
## Is Police Station a Real Signal or an Administrative Artifact?

---

## Key Numbers

| Metric | Range across 54 stations |
|---|---|
| Total cases | 105 (min) – 34,468 (max) |
| Approval rate | 21.6% – 55.2% |
| Unresolved rate | 26.1% – 63.2% |
| Avg validation delay (minutes) | 3,955 – 10,203 |
| Cells per station | 9 – 70 |
| Station std of total cases | 7,023 |
| Top-5 / Bottom-5 total ratio | 38.6× |

---

## Does Station Explain Real Variance?

**Yes, for workflow metrics.** The range in approval rate (21.6% to 55.2%) and unresolved rate (26.1% to 63.2%) is real. A station with 63% unresolved cases (KODIGEHALLI) is operationally different from one with 26% (lowest in dataset). Validation delay ranges from 66 hours to 170 hours — a 2.6× difference between best and worst stations.

**Yes, for case volume** — trivially. Station geography determines which cells fall under its jurisdiction. High-volume stations (UPPARPET, SHIVAJINAGAR) are in central Bengaluru where parking violations are denser. This is a spatial confound, not a behavioral one.

**Partially, for enforcement intensity.** UPPARPET has 9 cells and 34,468 cases. 60.3% of its cases come from a single cell. ELECTRONIC CITY has 70 cells and far fewer total cases. This means station case volume mostly reflects the geographic density of parking in its jurisdiction, not enforcement aggressiveness.

---

## Is Station Predictive?

As a raw label: weakly. If you encode station → mean count per cell, you are encoding geography, not station behavior.

As a source of workflow features (approval_rate_lag1, unresolved_rate_lag1, validation_delay_lag1): **yes, these are genuinely predictive** as Tier B features. They capture whether the station is keeping up with enforcement workflow, which indirectly signals data completeness and operational capacity.

---

## Is Station a Good Model Feature or a Bias Source?

It is **both**, depending on how it is used:
- Using raw `station_encoded` (label/target encoding) → mostly geography bias; minor predictive value beyond lat/lon
- Using `station_approval_rate_lag1`, `station_unresolved_rate_lag1`, `station_validation_delay_lag1` → real operational signals

**Recommendation**: Do not include station as a categorical identity feature. Include the 3 derived workflow metrics at station level. This separates the useful signal from the administrative artifact.

---

## Does Station Indicate Coverage, Enforcement Intensity, or Workflow Quality?

- **Coverage**: Yes — station boundaries define which cells are monitored at all. ELECTRONIC CITY covers 70 cells but with thin coverage per cell.
- **Enforcement intensity**: Only partially. UPPARPET's 60.3% top-cell concentration suggests patrol routes are fixed, not adaptive.
- **Workflow quality**: Yes — the approval rate and delay metrics are genuine quality indicators.

**Conclusion**: Station is useful as a source of 3 derived features. It should not be used as a raw categorical. The station boundary itself is not a behavioral signal.
