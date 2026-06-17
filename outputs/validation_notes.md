# Validation Notes

## Walk-Forward Folds
| Fold | Train | Test | Primary |
|------|-------|------|---------|
| 1 | Nov 2023 | Dec 2023 | No (only lag-1 features) |
| 2 | Nov-Dec 2023 | Jan 2024 | No (lag-2 features only) |
| 3 | Nov 2023–Jan 2024 | Feb 2024 | **Yes** |
| 4 | Nov 2023–Feb 2024 | Mar 2024 | **Yes** |
| 5 | Nov 2023–Mar 2024 | Apr 2024 | No (April truncated) |

## Leakage Controls
- All features use only data from months ≤ T-1 when predicting month T
- Station-level metrics recomputed per fold using training months only
- No target encoding applied
- Near-duplicate records (is_near_duplicate=1) excluded from target count aggregation

## April Handling
- April 2024 has 8 days of data vs 30-day full months
- April raw counts multiplied by (30/8) = 3.75 before any lag/target use
- April fold reported separately; excluded from primary metric averages

## Spatial Sanity
- Neighbour activity features computed per fold
- Cell lat/lon used as location priors but not as direct ID features
