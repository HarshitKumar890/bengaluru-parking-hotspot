# Structural Audit Summary

- **Total rows**: 298,450
- **Total columns**: 24
- **Duplicate rows**: 0
- **Duplicate IDs**: 0
- **Rows with ≥50% null fields**: 0

## Columns with >50% missing
None

## Columns that appear to be serialised lists
violation_type, offence_code

## Per-Column Detail
| column                       |   pct_missing |   n_unique |   n_literal_null | looks_like_list   |
|:-----------------------------|--------------:|-----------:|-----------------:|:------------------|
| id                           |          0    |     298450 |                0 | False             |
| latitude                     |          0    |     177983 |                0 | False             |
| longitude                    |          0    |     177378 |                0 | False             |
| location                     |          1.02 |      10943 |                0 | False             |
| vehicle_number               |          0    |     231890 |                0 | False             |
| vehicle_type                 |          0    |         22 |                0 | False             |
| description                  |          0    |          1 |           298450 | False             |
| violation_type               |          0    |        991 |                0 | True              |
| offence_code                 |          0    |        991 |                0 | True              |
| created_datetime             |          0    |      94417 |                0 | False             |
| closed_datetime              |          0    |          1 |           298450 | False             |
| modified_datetime            |          0    |     298450 |                0 | False             |
| device_id                    |          0    |       3070 |                0 | False             |
| created_by_id                |          0    |       2667 |                5 | False             |
| center_code                  |          0    |         53 |            11260 | False             |
| police_station               |          0    |         55 |                5 | False             |
| data_sent_to_scita           |          0    |          2 |                0 | False             |
| junction_name                |          0    |        170 |                5 | False             |
| action_taken_timestamp       |          0    |          1 |           298450 | False             |
| data_sent_to_scita_timestamp |          0    |      42162 |           256289 | False             |
| updated_vehicle_number       |          0    |     143134 |           125254 | False             |
| updated_vehicle_type         |          0    |         23 |           125254 | False             |
| validation_status            |          0    |          6 |           125254 | False             |
| validation_timestamp         |          0    |     170116 |           125254 | False             |