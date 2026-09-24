# Earth/CIVSTATE PostgreSQL namespace separation

Change class: `class:data`.

This change moves the nine longitudinal Earth authority base tables from
`loom_civ` to `loom_earth` with PostgreSQL `ALTER TABLE ... SET SCHEMA`.
Rows are not copied, regenerated, normalized, or transformed. `civ_*` tables
remain in `loom_civ`; control/provenance remains in `loom_control`; narrator
views remain in `loom_narrator`.

## Objects moved

`earth_area`, `earth_biological_cohort_year`, `earth_demographic_year`,
`earth_derivation`, `earth_economic_year`, `earth_labor_composition_year`,
`earth_legacy_labor_year`, `earth_sector_asset_year`, and `earth_sector_year`.

## Audit result

Before the move, every Earth table contained only snapshot
`earth-v0-1-9934d0ac-20260925`; every `civ_*` table contained only
`ceres-v1-0231e5f7da744728ab5021268b6f239b`. No Earth/CIV rows were blended.
Foreign keys are preserved by PostgreSQL and narrator view dependencies are
updated by the catalog when the tables change schema.

The pre-move counts were 237, 2,657,718, 47,637, 7, 16,080, 10,160, 6,000,
643,200, and 160,800 respectively in the object order above. The qualification
tool checks these counts, snapshot membership, CIVSTATE snapshot membership,
the exact namespace object set, and narrator view availability after migration.

Historical migrations 004–007 retain their original SQL as applied-history
records. Runtime import/verification code uses `loom_earth`.
