"""Inject frozen GAP-014 Earth authority into an experimental scenario."""
def demographic_authority_from_capture(capture):
 earth=capture["earth"]
 rows=earth["global_demographic_2026_2226"]
 snap=earth["snapshot"]
 if snap["state"]!="VALIDATED": raise ValueError("EARTH_SNAPSHOT_NOT_VALIDATED")
 if len(rows)!=201 or int(rows[0]["year"])!=2026 or int(rows[-1]["year"])!=2226:
  raise ValueError("EARTH_DEMOGRAPHIC_HORIZON_INCOMPLETE")
 return {
  "format":"CIVPROP_DEMOGRAPHIC_AUTHORITY_V1",
  "authority_semantics":"PROMOTED_EARTH_BASELINE_PLUS_CIVPROP_CONSERVED_MIGRATION_DELTA",
  "earth_biological_population_by_year":rows,
  "provenance_refs":[
   f"postgres_snapshot:{snap['snapshot_id']}",
   f"semantic_sha256:{snap['semantic_sha256']}",
   f"contract_sha256:{snap['contract_sha256']}",
  ],
 }
def inject_demographic_authority(*,scenario,capture,migration_demand=None):
 out=dict(scenario)
 out["demographic_authority_v1"]=demographic_authority_from_capture(capture)
 out["migration_demand_v1"]=migration_demand or {
  "format":"CIVPROP_MIGRATION_DEMAND_V1","rows":[],
  "status":"NO_AUTHORIZED_MIGRATION_DEMAND"
 }
 return out
