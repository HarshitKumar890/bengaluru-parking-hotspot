# Junction Effect Review
## Are Junctions Stronger Than Stations?

---

## Key Numbers

- Records with junction name: 150,565 / 298,277 = **50.5%**
- Total named junctions: 168
- Junctions active in all 6 months: **141 of 168 (83.9%)**
- Junction lag-1 correlation: 0.924 – 0.968 (mean 0.948) — **stronger than cell-level lag-1 (0.932)**

### Top 10 Junctions (always active, ranked by total violations)

| Junction | Total | CV |
|---|---|---|
| BTP051 - Safina Plaza Junction | 15,449 | 0.40 |
| BTP082 - KR Market Junction | 11,538 | 0.48 |
| BTP040 - Elite Junction | 10,718 | 0.35 |
| BTP044 - Sagar Theatre Junction | 10,549 | 0.36 |
| BTP211 - Central Street Junction | 5,388 | 0.60 |
| BTP058 - Subbanna Junction | 5,189 | 0.31 |
| BTP027 - Modi Bridge Junction | 4,584 | 0.39 |
| BTP020 - Hosahalli Metro Station | 4,101 | 0.60 |
| BTP057 - Anand Rao Junction | 3,935 | 0.43 |
| BTP080 - NR Road, SP Road Junction | 3,681 | 0.42 |

---

## Are Junctions Stronger Than Stations?

**Yes, as a predictive signal.** Junction-level lag-1 r = 0.948 mean vs. cell-level 0.932. Junctions aggregate over a more physically meaningful boundary (an intersection + surrounding zone) than an arbitrary 500m grid cell, which reduces noise.

However, the junction-level comparison is easier to forecast because the junctions that have names are the busiest ones — 141/168 are active all 6 months. This is selection bias: the BTP junction list captures only the most significant intersections. The 49.5% of records without junction names are not missing junctions — they are records in areas where the enforcement officer did not select a junction from the BTP list.

**Junction is a strong binary feature (is_junction_cell), not a categorical feature.** Using the 168 junction names as categories adds noise from low-count junctions. The binary flag "this cell has a named junction" is what matters.

---

## Are Some Junctions Always Hot?

Yes. The top-4 junctions (Safina Plaza, KR Market, Elite, Sagar Theatre) are consistently the highest-violation junctions in every month. CV for these ranges 0.31–0.40 — lower volatility than average. These are structurally hot.

## Are Some Junctions Only Seasonal?

The 27 junctions that are NOT active all 6 months are potentially seasonal or edge-case. CV for those is typically higher. Without longer data, it is not possible to distinguish seasonal from sporadic.

## Should Junction Be Treated as a Core Feature?

**`is_junction_cell` (binary): Yes — Tier A.**
**Junction name as categorical: No.** Too many categories, selection-biased toward busy zones, 49.5% missing.

The practical approach: use `is_junction_cell` and `junction_density` (count of named junctions within the cell) as features. Do not use junction name as a category.
