# Final Problem Formulation
## AI-Powered Parking Violation Hotspot Intelligence — Bengaluru

---

## 1. What Problem Are We Solving?

Bengaluru's traffic enforcement teams operate with finite patrol vehicles and personnel. They do not have a systematic method to decide **where to deploy patrols at what times**. Decisions are currently driven by officer intuition, fixed beats, and reactive dispatch.

The dataset is a 298,450-record enforcement log covering November 2023 to April 2024, capturing GPS coordinates, vehicle details, violation type, offence code, police station, junction name, and validation workflow timestamps.

**The core operational question is:**

> Given historical enforcement records, which spatial zones will accumulate the most parking violations in the next observation window, and in what order should patrols be dispatched to address them?

This is not a generic congestion prediction problem. There are no traffic-flow labels, speed sensors, or density measurements in this dataset. Any congestion claim would be fabricated. The correct framing is **enforcement-priority hotspot forecasting using recurrent spatial violation patterns**.

---

## 2. What the Data Actually Supports

| Capability | Supported? | Basis |
|---|---|---|
| Spatial hotspot identification | ✅ Strong | 298k geo records, 1,393 spatial cells, extreme concentration |
| Temporal recurrence analysis | ✅ Strong | 6 months of data, monthly panels per cell visible |
| Violation type classification | ✅ Strong | 27 violation types, clean multi-label structure |
| Enforcement priority ranking | ✅ Strong | Recurrence, density, junction proximity computable |
| Next-month violation forecasting | ✅ Feasible | 6-month cell×month panel (5,266 rows, all top-50 cells active all 6 months) |
| Repeat offender detection | ⚠️ Partial | 15.3% of vehicles reappear; max 55 appearances; anonymized IDs limit use |
| True congestion prediction | ❌ Not supported | No speed/flow/density data; enforcement ≠ congestion |
| Patrol route optimization | ❌ Out of scope | No road network or travel-time data |

---

## 3. Key Dataset Facts

- **298,450 records**; 298,282 with valid GPS coordinates within Bengaluru bounding box
- **1,393 spatial cells** (~500 m grid); extreme Pareto concentration:
  - Top 1 cell (CELL_2595_15515): 20,798 violations (7.0% of all records)
  - Top 10 cells: ~30% of all records
  - Median cell: 20 violations; 75th pctile: 103 violations
- **6 months of data**: Nov 2023, Dec 2023, Jan 2024, Feb 2024, Mar 2024, Apr 2024
  - April 2024 is partial (~15k records vs 55-65k for full months) — must be treated as incomplete
  - All top-50 cells have data in all 6 months — strong basis for temporal features
- **Timestamps critical**: `action_taken_timestamp` is 100% null; `closed_datetime` is 100% null. Response and closure delays cannot be computed. Validation delay (median 31 hours) and SCITA delay (median 17.9 days) are available.
- **Validation status**: 38.7% APPROVED, 16.7% REJECTED, 2.7% UNKNOWN, 42.0% NULL (never validated)
- **Violation distribution**: "WRONG PARKING" (165k) and "NO PARKING" (139k) dominate — >87% of all violations. 40,110 records carry 2+ violation labels simultaneously.
- **Hourly paradox**: Peak enforcement happens between 00:00–06:00, not during peak commute hours (07:00–10:00, 17:00–20:00). Only 17.5% of records fall in defined peak windows. This either reflects officer scheduling (nighttime rounds) or genuinely night-heavy violation patterns — requires domain clarification but must be acknowledged in model.

---

## 4. What the Model Will Do

The model produces a **ranked list of spatial cells with predicted violation intensity for the next observation window** (next 2-week block or next month), together with a confidence band.

Outputs for the enforcement agency:
1. **Top-K hotspot list**: Sorted by predicted violation count for the next period
2. **Persistence flag**: Is this cell historically recurrent or a one-time surge?
3. **Peak-hour flag**: Does this cell concentrate violations during traffic peak hours?
4. **Severity composite**: Does this cell show dangerous co-occurring violations (main road, road crossing, footpath)?
5. **Station assignment**: Which police station is responsible, and what is that station's current case backlog?

---

## 5. What This Enables Operationally

- Shift commanders can print a daily hotspot priority list before deploying patrols
- Resource allocation shifts from reactive (respond to complaints) to predictive (pre-position at ranked cells)
- Station performance can be tracked: cells with persistent high violations under a given station indicate coverage gaps
- Monthly review: if a cell drops off the top-K list, enforcement may have been effective — or the violation shifted elsewhere (spatial displacement)

---

## 6. Honest Limitations

- Dataset is enforcement-activity driven, not sensor-driven. Low-count cells may be underenforced, not violation-free.
- April 2024 is truncated — any model trained through March must be evaluated on a partial April or held out entirely.
- Vehicle IDs are anonymized; vehicle-level recurrence features are real but carry no PII-linkable value.
- Validation status is null for 42% of records — the APPROVED/REJECTED signal is available but not universal.
- No road-segment, pedestrian, or traffic-flow ground truth exists. The model scores enforcement priority, not congestion severity.
