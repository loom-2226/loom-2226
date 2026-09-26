#!/usr/bin/env python3
"""Verify and freeze the immutable SOLAR-BASELINE-01R qualification inputs."""
from __future__ import annotations
import hashlib, importlib.util, json, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent/"reports"
BASE=ROOT/"dev/solar_baseline_01"
SF=ROOT/"dev/solar_facts_multi_body/sf_promote_03_europa_ceres_67p"
BASE_DB=BASE/"LOOM_SOLAR_BASELINE_01_CANDIDATE_V20.sqlite3"
SF_DB=SF/"LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_03_EUROPA_CERES_67P.sqlite3"
ID_DOC=Path(__file__).resolve().parent/"raw/naif_ids_required_reading.html"

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    bman=json.loads((BASE/"baseline_manifest.json").read_text())
    if sha(BASE_DB)!=bman["candidate_database_sha256"]:raise RuntimeError("V20 database SHA mismatch")
    bsd=load_module("baseline_semantic_digest",BASE/"scripts/semantic_digest.py")
    if bsd.digest(str(BASE_DB))!=bman["candidate_whole_semantic_digest"]:raise RuntimeError("V20 semantic digest mismatch")
    audit=json.loads((BASE/"reports/artifact_hash_audit.json").read_text())
    artifacts=[]
    revalidated={
        "naif_ids_required_reading.html":ID_DOC,
        "jpl_satellite_physical_parameters.html":Path(__file__).resolve().parent/"raw/revalidation/jpl_satellite_physical_parameters.html",
        "jpl_sbdb_api_doc.html":Path(__file__).resolve().parent/"raw/revalidation/jpl_sbdb_api_doc.html",
        "jpl_planet_physical_parameters.html":Path(__file__).resolve().parent/"raw/revalidation/jpl_planet_physical_parameters.html",
        "jpl_sbdb_query_api_doc.html":Path(__file__).resolve().parent/"raw/revalidation/jpl_sbdb_query_api_doc.html",
    }
    for x in audit["artifacts"]:
        path=BASE/"raw"/x["raw_file"]
        if not path.exists() and Path(x["raw_file"]).name in revalidated:
            path=revalidated[Path(x["raw_file"]).name]
        actual=sha(path)
        if actual!=x["sha256"] or actual!=x["artifact_id"]:raise RuntimeError(f"baseline source artifact mismatch: {x['raw_file']}")
        artifacts.append({"raw_file":x["raw_file"],"sha256":actual,"bytes":path.stat().st_size,"source_url":x["source_url"],"product":x["product"],"verified":True})
    c=sqlite3.connect(BASE_DB);c.row_factory=sqlite3.Row
    bdb={"body_count":c.execute("select count(*) from authority_body_ref").fetchone()[0],
         "identifier_rows":c.execute("select count(*) from body_identifier_ref").fetchone()[0],
         "assertions_by_disposition":{r[0]:r[1] for r in c.execute("select disposition,count(*) from candidate_assertion group by disposition order by disposition")},
         "preferred_fact_count":c.execute("select count(*) from candidate_assertion where preferred_fact<>0").fetchone()[0],
         "unique_source_lineages":c.execute("select count(distinct source_lineage) from candidate_assertion").fetchone()[0],
         "coverage_by_disposition":{r[0]:r[1] for r in c.execute("select disposition,count(*) from coverage group by disposition order by disposition")},
         "identity_crosswalk_by_disposition":{r[0]:r[1] for r in c.execute("select disposition,count(*) from identity_crosswalk group by disposition order by disposition")},
         "integrity_check":c.execute("pragma integrity_check").fetchone()[0],"foreign_key_violations":len(c.execute("pragma foreign_key_check").fetchall())}
    held=list(map(tuple,c.execute("select body_id,external_id,source_artifact_id,notes from identity_crosswalk where disposition='HOLD' order by body_id,external_id,source_artifact_id")))
    c.close()
    sfq=json.loads((SF/"qualification.json").read_text())
    if sha(SF_DB)!=sfq["database_sha256"]:raise RuntimeError("SF-PROMOTE-03 database SHA mismatch")
    sfqmod=load_module("sf03_baseline_digest",SF/"sf03_qualify.py")
    digests={"whole":sfqmod.whole_digest(SF_DB),"CERES":sfqmod.body_digest(SF_DB,"CERES"),"COMET_67P":sfqmod.body_digest(SF_DB,"COMET_67P"),"EUROPA":sfqmod.body_digest(SF_DB,"EUROPA")}
    if digests["whole"]!=sfq["whole_database_semantic_digest"]:raise RuntimeError("SF-PROMOTE-03 semantic digest mismatch")
    for b,key in (("CERES","CERES"),("COMET_67P","COMET_67P"),("EUROPA","EUROPA")):
        if digests[b]!=sfq["body_digests"][key]:raise RuntimeError(f"SF-PROMOTE-03 {b} body digest mismatch")
    s=sqlite3.connect(SF_DB)
    sfcounts={"body_count":s.execute("select count(*) from body").fetchone()[0],"preferred_fact_count":s.execute("select count(*) from preferred_fact").fetchone()[0],"integrity_check":s.execute("pragma integrity_check").fetchone()[0],"foreign_key_violations":len(s.execute("pragma foreign_key_check").fetchall())}
    s.close()
    doc_sha=sha(ID_DOC)
    docmeta={"authority":"NASA/JPL NAIF","product":"NAIF Integer ID codes Required Reading","release_date":"2021-12-10","source_url":"https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/naif_ids.html","acquired_at_utc":"2026-09-26T15:20:48Z","acquisition_time_basis":"filesystem capture timestamp preserved at acquisition","raw_file":"raw/naif_ids_required_reading.html","sha256":doc_sha,"byte_count":ID_DOC.stat().st_size,"purpose":"identity crosswalk only; no scientific parameter assertions parsed","read_only":"true"}
    (OUT/"identity_reference_artifact.json").write_text(json.dumps(docmeta,indent=2,sort_keys=True)+"\n")
    freeze={"mission_id":"SOLAR-BASELINE-01R","starting_live_main":"fc350353a3efd1c1826b1c584d846382ff828237","change_class":"class:data","worktree":"/tmp/loom-solar-baseline-01r","branch":"data/solar-baseline-01r-reconciliation","candidate_v20":{"path":"dev/solar_baseline_01/LOOM_SOLAR_BASELINE_01_CANDIDATE_V20.sqlite3","sha256":sha(BASE_DB),"semantic_digest":bsd.digest(str(BASE_DB)),**bdb,"held_identity_crosswalks":[{"body_id":r[0],"external_id":r[1],"source_artifact_id":r[2],"notes":r[3]} for r in held]},"source_artifacts":{"count":len(artifacts),"total_bytes":sum(x["bytes"] for x in artifacts),"all_hashes_verified":True,"artifacts":artifacts},"sf_promote_03":{"path":"dev/solar_facts_multi_body/sf_promote_03_europa_ceres_67p/LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_03_EUROPA_CERES_67P.sqlite3","sha256":sha(SF_DB),"semantic_digests":digests,**sfcounts},"identity_reference":docmeta,"preferred_fact_counts":{"Solar_Baseline_01_candidate":bdb["preferred_fact_count"],"SF_PROMOTE_03_total":sfcounts["preferred_fact_count"]},"input_mutation_permitted":False,"freeze_verified_at_utc":datetime.now(timezone.utc).isoformat()}
    (OUT/"input_freeze.json").write_text(json.dumps(freeze,indent=2,sort_keys=True)+"\n")
    (OUT/"baseline_artifact_hashes.json").write_text(json.dumps({"artifact_count":len(artifacts),"all_verified":True,"artifacts":artifacts},indent=2,sort_keys=True)+"\n")
    print(json.dumps({"baseline_db_sha256":freeze["candidate_v20"]["sha256"],"baseline_digest":freeze["candidate_v20"]["semantic_digest"],"baseline_source_artifacts":len(artifacts),"sf03_sha256":freeze["sf_promote_03"]["sha256"],"sf03_digests":digests,"identity_doc_sha256":doc_sha,"preferred_facts":freeze["preferred_fact_counts"]},sort_keys=True))

if __name__=="__main__":main()
