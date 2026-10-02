"""Read-only PostgreSQL authority surface required by GAP-014.

This module declares which existing loom_earth relations are authoritative inputs.
It does not create tables, mutate PostgreSQL, or derive replacement Earth trajectories.
"""
EARTH_GAP014_REQUIRED_RELATIONS=(
 "earth_demographic_year",
 "earth_biological_cohort_year",
 "earth_labor_composition_year",
 "earth_derivation",
)
EARTH_GAP014_SUPPORTING_RELATIONS=(
 "earth_area","earth_economic_year","earth_sector_year","earth_sector_asset_year",
)
CONTROL_REQUIRED_RELATIONS=(
 "snapshot","snapshot_source","source_artifact","temporal_coverage","row_lineage",
)

def gap014_postgres_queries(*,snapshot_id,year):
 if not snapshot_id: raise ValueError("MISSING_EARTH_SNAPSHOT_ID")
 if not isinstance(year,int): raise TypeError("YEAR_MUST_BE_INTEGER")
 return {
  "demographic":f"SELECT * FROM loom_earth.earth_demographic_year WHERE snapshot_id='{snapshot_id}' AND year={year} ORDER BY iso3",
  "cohorts":f"SELECT * FROM loom_earth.earth_biological_cohort_year WHERE snapshot_id='{snapshot_id}' AND year={year} ORDER BY iso3,sex,age_start",
  "labor":f"SELECT * FROM loom_earth.earth_labor_composition_year WHERE snapshot_id='{snapshot_id}' AND year={year} ORDER BY iso3",
  "derivations":f"SELECT * FROM loom_earth.earth_derivation WHERE snapshot_id='{snapshot_id}' ORDER BY derivation_id",
 }

def postgres_surface_status(*,available_relations):
 available=set(available_relations)
 missing=[x for x in EARTH_GAP014_REQUIRED_RELATIONS if x not in available]
 return {"status":"READY" if not missing else "INCOMPLETE","missing":tuple(missing)}
