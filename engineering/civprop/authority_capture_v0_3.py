"""Gate A: immutable LOOM runtime authority capture.

Captures promoted PostgreSQL Earth/Timeline authority, complete live Solar
authority, and governed repository-only evidence into a deterministic,
content-addressed directory.  It never writes PostgreSQL and never mutates
source bundles.

This is an authority *capture*, not a claim that every captured field is
semantically compatible with every CIVPROP runtime field.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json, shutil, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
EARTH="earth-v0-1-9934d0ac-20260925"
TIMELINE="timeline-v0-1-0232bf23494f-20260925"
FORMAT="LOOM_RUNTIME_AUTHORITY_CAPTURE_V0_3"
VERSION="0.3.0"

# Ordered exports make byte identity meaningful. PostgreSQL text/CSV is retained
# rather than reserializing millions of numeric values through Python floats.
EXPORTS=[
 ("control_import_batch","loom_control.import_batch","","snapshot_id,batch_id"),
 ("control_semantic_version","loom_control.semantic_version","","semantic_sha256"),
 ("control_source_artifact","loom_control.source_artifact","","artifact_sha256"),
 ("control_field_semantics","loom_control.field_semantics","","snapshot_id,source_database,source_table,source_column"),
 ("control_row_lineage","loom_control.row_lineage","","snapshot_id,target_schema,target_table,source_database,source_table,source_key"),
 ("control_earth_snapshot","loom_control.snapshot",f"snapshot_id='{EARTH}'","snapshot_id"),
 ("control_timeline_snapshot","loom_control.snapshot",f"snapshot_id='{TIMELINE}'","snapshot_id"),
 ("control_earth_temporal_coverage","loom_control.temporal_coverage",f"snapshot_id='{EARTH}'","fact_family,variable_key,coverage_scope"),
 ("control_earth_variable_semantics","loom_control.variable_semantics",f"snapshot_id='{EARTH}'","variable_key"),
 ("control_earth_model_context","loom_control.model_context_record",f"snapshot_id='{EARTH}'","context_key"),
 ("control_earth_snapshot_source","loom_control.snapshot_source",f"snapshot_id='{EARTH}'","source_role,artifact_sha256"),
 ("control_timeline_snapshot_source","loom_control.snapshot_source",f"snapshot_id='{TIMELINE}'","source_role,artifact_sha256"),
 ("earth_area","loom_earth.earth_area",f"snapshot_id='{EARTH}'","iso3"),
 ("earth_demographic_year","loom_earth.earth_demographic_year",f"snapshot_id='{EARTH}'","iso3,year"),
 ("earth_biological_cohort_year","loom_earth.earth_biological_cohort_year",f"snapshot_id='{EARTH}'","iso3,year,sex,age_start"),
 ("earth_derivation","loom_earth.earth_derivation",f"snapshot_id='{EARTH}'","derivation_id"),
 ("earth_economic_year","loom_earth.earth_economic_year",f"snapshot_id='{EARTH}'","iso3,year"),
 ("earth_labor_composition_year","loom_earth.earth_labor_composition_year",f"snapshot_id='{EARTH}'","iso3,year"),
 ("earth_legacy_labor_year","loom_earth.earth_legacy_labor_year",f"snapshot_id='{EARTH}'","iso3,year"),
 ("earth_sector_year","loom_earth.earth_sector_year",f"snapshot_id='{EARTH}'","iso3,sector,year"),
 ("earth_sector_asset_year","loom_earth.earth_sector_asset_year",f"snapshot_id='{EARTH}'","iso3,sector,asset_class,year"),
 ("timeline_interpretation_rule","loom_timeline.interpretation_rule",f"snapshot_id='{TIMELINE}'","rule_key"),
 ("timeline_milestone","loom_timeline.milestone",f"snapshot_id='{TIMELINE}'","sort_order,milestone_id"),
 ("timeline_milestone_alias","loom_timeline.milestone_alias",f"snapshot_id='{TIMELINE}'","milestone_id,alias_id"),
 ("timeline_milestone_source","loom_timeline.milestone_source",f"snapshot_id='{TIMELINE}'","milestone_id,source_role,source_artifact_sha256"),
 ("solar_body","loom_solar.body","","body_id"),
 ("solar_body_identifier","loom_solar.body_identifier","","body_id,authority,identifier_type,identifier_value"),
 ("solar_curated_cohort_member","loom_solar.curated_cohort_member","","cohort,supplied_entry,body_id"),
 ("solar_ephemeris_source","loom_solar.ephemeris_source","","ephemeris_source_id"),
 ("solar_ephemeris_coverage","loom_solar.ephemeris_coverage","","ephemeris_source_id,body_id,valid_from,valid_until"),
 ("solar_object_metadata","loom_solar.object_metadata","","body_id,mission_id"),
]

REPO_EVIDENCE=[
 "engineering/civprop/civprop0/actor_access_evidence.json",
 "engineering/civprop/civprop0/aus_government_access_evidence.json",
 "engineering/civprop/civprop0/roover_service_envelope.json",
 "engineering/civprop/civprop0/runs/roover_transport_mid2030_v1.json",
 "engineering/civprop/contracts/project_economics_v1.json",
 "engineering/civprop/contracts/mission_knowledge_v1.json",
 "engineering/civprop/contracts/pressure_observability_v1.json",
 "engineering/civprop/contracts/resource_mass_balance_v1.json",
 "engineering/civprop/contracts/production_accounting_v1.json",
 "engineering/civprop/contracts/power_balance_v1.json",
 "engineering/civprop/contracts/traffic_fleet_v1.json",
 "engineering/civprop/contracts/facility_site_materialization_v1.json",
 "engineering/civprop/contracts/asset_lifecycle_v1.json",
 "engineering/civprop/contracts/infrastructure_archetypes_v1.json",
 "data/postgres/migrations/004_earth_temporal_authority.sql",
 "data/postgres/evidence/LOOM_CERES_MVP_A_FIELD_QUALIFICATION_v0.1.json",
 "dev/resource_economics/dorrington_olsen/m2/DORRINGTON_OLSEN_CIVPROP_INPUT_CONTRACT.json",
 "reports/solar_civprop/DORRINGTON_OLSEN_M2_CIVPROP_ASSESSMENT.md",
 "reports/solar_civprop/NAV_READINESS_V1.json",
 "dev/solar_civprop_m4b/reports/M4B_COVERAGE_MATRIX.csv",
 "dev/solar_civprop_m4b/campaign_assertions.json",
 "dev/solar_civprop_resource_contract/RESOURCE_COVERAGE_CONTRACT_V1.json",
 "dev/solar_civprop_resource_contract/RESOURCE_STATE_CONTRACT_V1.sql",
 "data/postgres/earth_temporal_projection_manifest.json",
 "data/postgres/timeline_projection_manifest.json",
 "docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md",
]

def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open("rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
 return h.hexdigest()

def scalar(db,q):
 r=subprocess.run(["psql","-X","-d",db,"-At","-c",q],check=True,capture_output=True,text=True)
 return r.stdout.strip()

def export(db,out,name,table,where,order):
 out.mkdir(parents=True,exist_ok=True)
 dest=out/f"{name}.csv.gz"
 predicate=f" WHERE {where}" if where else ""
 query=f"COPY (SELECT * FROM {table}{predicate} ORDER BY {order}) TO STDOUT WITH (FORMAT CSV, HEADER TRUE)"
 proc=subprocess.Popen(["psql","-X","-d",db,"-q","-c",query],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 with dest.open("wb") as raw, gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0,compresslevel=6) as gz:
  assert proc.stdout
  for chunk in iter(lambda:proc.stdout.read(1024*1024),b""): gz.write(chunk)
 err=proc.stderr.read().decode() if proc.stderr else ""
 rc=proc.wait()
 if rc: raise RuntimeError(f"{table} export failed: {err}")
 count=int(scalar(db,f"SELECT count(*) FROM {table}{predicate}"))
 return {"table":table,"where":where or None,"order_by":order,"rows":count,
         "file":dest.name,"sha256":sha(dest),"bytes":dest.stat().st_size,
         "query_sha256":hashlib.sha256(query.encode()).hexdigest()}

def capture(target:Path,database="loom_dev"):
 if target.exists(): raise FileExistsError(f"refusing to overwrite immutable capture: {target}")
 target.mkdir(parents=True)
 pg=target/"postgres"; repo=target/"repository_evidence"
 pg.mkdir(); repo.mkdir()
 exports=[export(database,pg,*x) for x in EXPORTS]
 copied=[]
 for rel in REPO_EVIDENCE:
  src=ROOT/rel
  if not src.is_file(): raise FileNotFoundError(src)
  dst=repo/rel
  dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
  copied.append({"path":rel,"sha256":sha(dst),"bytes":dst.stat().st_size})
 head=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
 manifest={"format":FORMAT,"version":VERSION,"classification":"AUTHORITY_CAPTURE_NON_CANON_RUNTIME_INPUT",
  "semantics":{"read_only_postgres":True,"source_bundles_mutated":False,
   "capture_is_authority_snapshot_not_cross_domain_semantic_equivalence":True,
   "governing_canon_timeline_not_automatic_actor_capability":True,
   "scenario_frontier_not_automatic_actor_capability":True,
   "unknown_not_zero":True},
  "database":database,"source_basis_commit":head,
  "snapshot_ids":{"earth":EARTH,"timeline":TIMELINE},
  "postgres_exports":exports,"repository_evidence":copied}
 mb=json.dumps(manifest,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
 manifest["content_manifest_sha256"]=hashlib.sha256(mb).hexdigest()
 (target/"MANIFEST.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
 # Capture ID hashes the manifest describing every immutable member.
 cid=sha(target/"MANIFEST.json")
 (target/"CAPTURE_SHA256.txt").write_text(cid+"  MANIFEST.json\n")
 return manifest,cid

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--database",default="loom_dev"); ap.add_argument("--output",required=True)
 a=ap.parse_args(); m,c=capture(Path(a.output),a.database)
 print("GATE_A_CAPTURE",c); print("exports",len(m["postgres_exports"]),"repo_evidence",len(m["repository_evidence"]))
 print("rows",sum(x["rows"] for x in m["postgres_exports"]))
if __name__=="__main__": main()
