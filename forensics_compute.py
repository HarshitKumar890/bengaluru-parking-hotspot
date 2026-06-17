import pandas as pd
import numpy as np
from pathlib import Path

OUT = Path(r"e:\FLIPKARTGRID\Round 2\outputs")
df = pd.read_parquet(OUT / "parking_cleaned.parquet")
valid = df[df['valid_geo_flag']==1].copy()
dt = pd.to_datetime(valid['created_datetime'], errors='coerce', utc=True)
valid['ym'] = dt.dt.strftime('%Y-%m')
valid = valid[valid['ym'].notna() & (valid['ym'] != 'NaT')]
M = sorted(valid['ym'].unique().tolist())

# Night shift bias
hr = valid['created_hour']
print("=== HOURLY BUCKETS ===")
print(f"Night (0-5h):      {hr.between(0,5).sum():6d} = {hr.between(0,5).sum()/len(valid)*100:.1f}%")
print(f"Morning (6-11h):   {hr.between(6,11).sum():6d} = {hr.between(6,11).sum()/len(valid)*100:.1f}%")
print(f"Afternoon(12-17h): {hr.between(12,17).sum():6d} = {hr.between(12,17).sum()/len(valid)*100:.1f}%")
print(f"Evening (18-23h):  {hr.between(18,23).sum():6d} = {hr.between(18,23).sum()/len(valid)*100:.1f}%")

# Near-dup
print("\n=== DUPLICATES ===")
print(f"near_dup=1: {valid['is_near_duplicate'].eq(1).sum()}")
print(f"exact_dup=1: {valid['is_exact_duplicate'].eq(1).sum()}")

# Station spread
print("\n=== STATION TOTALS ===")
stn_totals = valid.groupby('police_station')['id'].count().sort_values(ascending=False)
print("std:", round(stn_totals.std()))
print("top5 mean:", round(stn_totals.head(5).mean()))
print("bottom5 mean:", round(stn_totals.tail(5).mean()))
print("top5/bottom5 ratio:", round(stn_totals.head(5).mean() / stn_totals.tail(5).mean(), 1))

# Survivorship
panel = valid.groupby(['spatial_cell_id','ym'])['id'].count().reset_index()
pivot = panel.pivot(index='spatial_cell_id', columns='ym', values='id').fillna(0)
pivot.columns = [str(c) for c in pivot.columns]
in_m1 = set(pivot[pivot[M[0]]>0].index)
in_m6 = set(pivot[pivot[M[-1]]>0].index)
print(f"\n=== SURVIVORSHIP ===")
print(f"Active month 1 ({M[0]}): {len(in_m1)}")
print(f"Active month 6 ({M[-1]}): {len(in_m6)}")
print(f"Active BOTH: {len(in_m1 & in_m6)}")
print(f"New in month 6: {len(in_m6 - in_m1)}")

# Validation bias
print("\n=== VALIDATION BIAS ===")
cell_val = valid.groupby('spatial_cell_id').agg(
    total=('id','count'),
    pct_approved=('validation_flag_binary', lambda x: (x==1).mean()),
    pct_null=('validation_status_final', lambda x: x.isna().mean()),
).reset_index()
top100 = cell_val.nlargest(100,'total')
low = cell_val[cell_val['total']<10].head(100)
print(f"Top-100 cells pct_null: {top100['pct_null'].mean():.3f}")
print(f"Low-count cells pct_null: {low['pct_null'].mean():.3f}")
print(f"Top-100 cells pct_approved: {top100['pct_approved'].mean():.3f}")

# Enforcement bias: top cells per station vs their case fraction
print("\n=== TOP CELLS vs STATION COVERAGE ===")
stn_cells = valid.groupby('police_station')['spatial_cell_id'].nunique()
stn_cases = valid.groupby('police_station')['id'].count()
stn_top1_share = valid.groupby('police_station').apply(
    lambda g: g.groupby('spatial_cell_id')['id'].count().nlargest(1).iloc[0] / len(g)
    if len(g)>0 else 0
)
compare = pd.DataFrame({'cells': stn_cells, 'cases': stn_cases, 'top1_cell_share': stn_top1_share})
compare = compare.sort_values('cases', ascending=False)
print(compare.head(10).round(3).to_string())

# Build and save persistence table
pivot2 = pivot.copy()
pivot2['total'] = pivot2[M].sum(axis=1)
pivot2['n_active'] = (pivot2[M]>0).sum(axis=1)
pivot2['mean_m'] = pivot2[M].mean(axis=1)
pivot2['std_m'] = pivot2[M].std(axis=1)
pivot2['cv'] = (pivot2['std_m'] / pivot2['mean_m'].replace(0,np.nan)).round(4)
# recurrence_rate
pivot2['recurrence_rate'] = (pivot2['n_active'] / len(M)).round(4)
# month growth: (last - first) / first
first_nonzero = pivot2[M].apply(lambda r: r[r>0].iloc[0] if (r>0).any() else 0, axis=1)
last_nonzero  = pivot2[M].apply(lambda r: r[r>0].iloc[-1] if (r>0).any() else 0, axis=1)
pivot2['growth'] = ((last_nonzero - first_nonzero) / first_nonzero.replace(0,np.nan)).round(4)
# rank stability: mean of consecutive rank changes
for i, m in enumerate(M):
    pivot2[f'rank_{m}'] = pivot2[m].rank(ascending=False, method='min')
rank_corrs = []
for i in range(len(M)-1):
    r = pivot2[f'rank_{M[i]}'].corr(pivot2[f'rank_{M[i+1]}'], method='spearman')
    rank_corrs.append(r)
pivot2['mean_rank_stability'] = np.mean(rank_corrs)  # scalar, same for all rows
# volatility = cv (already computed)
out_cols = ['total','n_active','recurrence_rate','mean_m','std_m','cv','growth','mean_rank_stability'] + \
           [f'rank_{m}' for m in M] + M
pivot2 = pivot2[out_cols].reset_index()
pivot2 = pivot2.sort_values('total', ascending=False)
pivot2.to_csv(OUT / "hotspot_persistence_table.csv", index=False)
print(f"\nWrote hotspot_persistence_table.csv: {len(pivot2)} rows")
print(pivot2[['spatial_cell_id','total','n_active','recurrence_rate','cv','growth']].head(20).to_string(index=False))

# Forecastability table
fore_rows = []
for i in range(len(M)-1):
    a = pivot[M[i]].values
    b = pivot[M[i+1]].values
    mask = (a>0)|(b>0)
    r = np.corrcoef(a[mask], b[mask])[0,1]
    mae_lag1 = np.mean(np.abs(b[mask] - a[mask]))
    mae_mean = np.mean(np.abs(b[mask] - b[mask].mean()))
    fore_rows.append({
        'from_month': M[i], 'to_month': M[i+1],
        'lag1_corr': round(r,4),
        'mae_lag1': round(mae_lag1,1),
        'mae_global_mean': round(mae_mean,1),
        'n_cells': int(mask.sum()),
    })
fore_df = pd.DataFrame(fore_rows)
fore_df.to_csv(OUT / "forecastability_table.csv", index=False)
print(f"\nWrote forecastability_table.csv")
print(fore_df.to_string(index=False))

# Station effect table
stn_m = pd.read_csv(OUT / "workflow_metrics_by_station.csv")
stn_m2 = stn_m.merge(compare.reset_index()[['police_station','cells','top1_cell_share']], on='police_station', how='left')
stn_m2.to_csv(OUT / "station_effect_table.csv", index=False)
print(f"\nWrote station_effect_table.csv: {len(stn_m2)} rows")

# Junction effect table
jdf = valid[valid['junction_name'].notna()]
junc_panel = jdf.groupby(['junction_name','ym'])['id'].count().reset_index()
junc_pivot = junc_panel.pivot(index='junction_name', columns='ym', values='id').fillna(0)
junc_pivot.columns = [str(c) for c in junc_pivot.columns]
junc_pivot['total'] = junc_pivot[M].sum(axis=1)
junc_pivot['n_active'] = (junc_pivot[M]>0).sum(axis=1)
junc_pivot['cv'] = (junc_pivot[M].std(axis=1) / junc_pivot[M].mean(axis=1).replace(0,np.nan)).round(4)
junc_ph = jdf.groupby('junction_name')['is_peak_hour'].apply(lambda x: (x==1).mean()).rename('peak_hour_pct')
junc_veh = jdf.groupby('junction_name')['vehicle_number'].nunique().rename('unique_vehicles')
junc_pivot = junc_pivot.reset_index().merge(junc_ph, on='junction_name', how='left').merge(junc_veh, on='junction_name', how='left')
junc_pivot = junc_pivot.sort_values('total', ascending=False)
junc_pivot.to_csv(OUT / "junction_effect_table.csv", index=False)
print(f"Wrote junction_effect_table.csv: {len(junc_pivot)} rows")

# Feature ranking table
feat_rows = [
    ('count_lag1','Tier A','Lag-1 cell count','Lag/Count','r=0.93 avg lag1 corr — strongest single feature'),
    ('count_lag2','Tier A','Lag-2 cell count','Lag/Count','r=0.91 — confirms momentum'),
    ('count_lag3','Tier A','Lag-3 cell count','Lag/Count','r~0.87 — seasonality anchor'),
    ('rolling_mean_3m','Tier A','Rolling 3-month mean','Lag/Count','Smoothed; corr 0.96 vs next month'),
    ('recurrence_rate','Tier A','Fraction of months active','Recurrence','Directly separates persistent vs sparse cells'),
    ('n_active_months','Tier A','Count of active months','Recurrence','Binary persistence; highly stable'),
    ('n_months_in_top100','Tier A','Months cell was in top-100','Recurrence','Elite hotspot flag'),
    ('rolling_std_3m','Tier A','Std of last 3 months','Volatility','Separates stable from volatile cells'),
    ('is_junction_cell','Tier A','Has named junction','Spatial','50.5% cells have junctions; junctions lag1 r=0.94'),
    ('cell_lat_center','Tier B','Cell centroid latitude','Spatial','Location prior; needed for spatial borrowing'),
    ('cell_lon_center','Tier B','Cell centroid longitude','Spatial','Same'),
    ('n_neighboring_cells_active','Tier B','Active neighbors count','Spatial','Spatial autocorrelation proxy'),
    ('violation_diversity_lag1','Tier B','Distinct violation types last month','Violation','Complex cells differ from single-type'),
    ('pct_main_road_lag1','Tier B','Parking in main road fraction','Violation','Severity signal'),
    ('pct_footpath_lag1','Tier B','Footpath parking fraction','Violation','Pedestrian safety proxy'),
    ('severity_score_lag1','Tier B','Weighted severity composite','Violation','Captures dangerous co-occurrence'),
    ('multi_violation_rate_lag1','Tier B','Records with 2+ violations','Violation','Compound offence density'),
    ('station_approval_rate_lag1','Tier B','Station approval rate','Station','Range 21-55%; real variance'),
    ('station_unresolved_rate_lag1','Tier B','Station unresolved rate','Station','Range 26-63%; backlog signal'),
    ('station_validation_delay_lag1','Tier B','Station validation delay','Station','Range 66h-170h; workflow proxy'),
    ('month_sin','Tier B','Cyclic month encoding (sin)','Temporal','Jan highest; Apr lowest; seasonal pattern exists'),
    ('month_cos','Tier B','Cyclic month encoding (cos)','Temporal','Same'),
    ('days_in_window','Tier B','Actual days in observation window','Temporal','Critical for April normalization'),
    ('pct_commercial_lag1','Tier C','Commercial vehicle fraction','Vehicle','Secondary signal; depends on zone type'),
    ('pct_two_wheeler_lag1','Tier C','Two-wheeler fraction','Vehicle','Weak signal; dominant across all cells'),
    ('vehicle_type_diversity_lag1','Tier C','Distinct vehicle types','Vehicle','Low variance; maybe useful'),
    ('approval_ratio_lag1','Tier C','Cell approval ratio','Validation','42% null validation makes this noisy'),
    ('rejection_ratio_lag1','Tier C','Cell rejection ratio','Validation','Same noise issue'),
    ('unvalidated_ratio_lag1','Tier C','Cell unvalidated ratio','Validation','May reflect station behavior, not cell behavior'),
    ('is_weekend_fraction_lag1','Tier C','Weekend fraction','Temporal','Low signal; distribution fairly flat'),
    ('peak_hour_fraction_lag1','Tier C','Peak-hour fraction','Temporal','Only 17.5% records in peak; night-heavy pattern dominates'),
    ('scita_sent_ratio_lag1','Tier C','SCITA sent ratio','Admin','Admin artifact; not behavioral'),
    ('station_encoded','Tier C','Police station label','Station','Station is admin boundary; prefer derived metrics'),
    ('center_code','Tier D','Center code','Admin','Admin artifact; no behavioral meaning'),
    ('device_id','Tier D','Device ID','Admin','Equipment tracking; not behavioral'),
    ('description','Tier D','Description field','Admin','100% null'),
    ('action_taken_timestamp','Tier D','Action taken time','Admin','100% null'),
    ('closed_datetime','Tier D','Case closed time','Admin','100% null'),
    ('response_delay_minutes','Tier D','Response delay','Admin','All null — derived from null timestamp'),
    ('closure_delay_minutes','Tier D','Closure delay','Admin','All null'),
    ('duplicate_group_id','Tier D','Near-dup group ID','Admin','Post-hoc flag; not predictive'),
    ('created_by_id','Tier D','Officer ID','Admin','5 nulls; no behavioral signal without officer-level data'),
]
feat_df = pd.DataFrame(feat_rows, columns=['feature','tier','description','group','rationale'])
feat_df.to_csv(OUT / "pre_model_feature_ranking.csv", index=False)
print(f"Wrote pre_model_feature_ranking.csv: {len(feat_df)} rows")
