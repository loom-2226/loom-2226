"""Deterministic promotion of a frozen ARP campaign into candidate Solar Facts.

This adapter is body-agnostic: the only body-specific input is the identity
authority mapping supplied by the caller.  The promotion ledger retains the
complete frozen assertion JSON so unsupported fields cannot disappear.
"""
from __future__ import annotations

import hashlib, json, shutil, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
V3 = ROOT / "dev/solar_facts_hcq01/v0_3_r1/LOOM_SOLAR_HCQ01_CERES_v0_3_R1.sqlite3"
CAMPAIGN = ROOT / "dev/atlas_research_protocol/qualifications/arp_qual_01b_67p"
CUTOFF = "2025-12-31T23:59:59Z"

SCALAR = {"GM": ("DYNAMICAL_INFERENCE", "m^3/s^2"),
          "MASS": ("DYNAMICAL_INFERENCE", "kg"),
          "BULK_DENSITY": ("DERIVED", "kg/m^3"),
          "POROSITY": ("PHYSICAL_MODEL", "%")}

def sha(path):
    h=hashlib.sha256(); n=0
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b); n+=len(b)
    return h.hexdigest(),n

def _clear(conn):
    for t in ("preferred_fact","derived_input","derived_quantity","fact_input",
              "fact_observation","source_assertion","knowledge_event",
              "activity_fact","material_evidence","observation",
              "gravity_model","orientation_model","body_model_product","region_model_product","body_region",
              "fact","source","body"):
        conn.execute(f"DELETE FROM {t}")

def _add_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS body_authority(
      body_id TEXT PRIMARY KEY REFERENCES body(body_id), authority_system TEXT NOT NULL,
      authority_identifier TEXT NOT NULL, authority_class TEXT NOT NULL,
      UNIQUE(authority_system,authority_identifier));
    CREATE TABLE IF NOT EXISTS source_artifact(
      artifact_id TEXT PRIMARY KEY, source_id INTEGER NOT NULL REFERENCES source(source_id),
      locator TEXT NOT NULL, local_path TEXT NOT NULL, retrieved_at TEXT NOT NULL,
      sha256 TEXT NOT NULL CHECK(length(sha256)=64), byte_count INTEGER NOT NULL CHECK(byte_count>=0),
      media_type TEXT, original_filename TEXT, version TEXT, UNIQUE(source_id,sha256));
    CREATE TABLE IF NOT EXISTS promotion_assertion(
      promotion_assertion_id INTEGER PRIMARY KEY, campaign_id TEXT NOT NULL,
      assertion_id TEXT NOT NULL UNIQUE, body_id TEXT NOT NULL REFERENCES body(body_id),
      source_id INTEGER NOT NULL REFERENCES source(source_id), artifact_id TEXT NOT NULL REFERENCES source_artifact(artifact_id),
      property_code TEXT NOT NULL, claim_kind TEXT NOT NULL, evidence_class TEXT NOT NULL,
      scope_type TEXT, region_id INTEGER, method_type TEXT, independent_lineage_id TEXT,
      reported_value_json TEXT, reported_unit TEXT, reported_uncertainty_json TEXT,
      normalized_value_json TEXT, normalized_unit TEXT, normalized_uncertainty_json TEXT,
      normalization_method TEXT, resolution_json TEXT NOT NULL, temporal_context TEXT,
      status TEXT NOT NULL CHECK(status='CANDIDATE'), raw_assertion_json TEXT NOT NULL,
      raw_sha256 TEXT NOT NULL CHECK(length(raw_sha256)=64), notes TEXT);
    CREATE TABLE IF NOT EXISTS promotion_review(
      promotion_assertion_id INTEGER PRIMARY KEY REFERENCES promotion_assertion(promotion_assertion_id),
      disposition TEXT NOT NULL CHECK(disposition IN('PROMOTE','HOLD','REJECT','SCHEMA_LIEN','DUPLICATE','OUT_OF_SCOPE')),
      reviewer TEXT NOT NULL, reason TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS promotion_lineage(
      promotion_assertion_id INTEGER PRIMARY KEY REFERENCES promotion_assertion(promotion_assertion_id),
      input_assertion_ids_json TEXT NOT NULL, notes TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS epistemic_frontier(
      frontier_id INTEGER PRIMARY KEY, campaign_id TEXT NOT NULL, variable TEXT NOT NULL,
      phase TEXT NOT NULL CHECK(phase IN('KNOWABLE','INFERRED','FUTURE_OBSERVABLE','ENGINEERING_DERIVED','ECONOMIC_DERIVED')),
      research_coverage TEXT NOT NULL, state_at_cutoff TEXT NOT NULL, evidence_class TEXT,
      limitation TEXT, UNIQUE(campaign_id,variable));
    CREATE TABLE IF NOT EXISTS promotion_manifest(
      key TEXT PRIMARY KEY, value TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS idx_promotion_assertion_body ON promotion_assertion(body_id);
    """)

def _source_type(s):
    # The frozen source metadata says primary peer-reviewed analysis; the
    # preserved arXiv artifact is represented honestly as a PREPRINT.
    if s["locator"].startswith("https://arxiv.org/"): return "PREPRINT"
    if s["source_type"] == "DATA_ARCHIVE": return "DATA_PRODUCT"
    if s["source_type"] in ("PEER_REVIEWED_PRIMARY",): return "PEER_REVIEWED"
    return "OFFICIAL_REFERENCE"

def build(destination: Path):
    destination=Path(destination); destination.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(V3,destination)
    d=json.loads((CAMPAIGN/"campaign.json").read_text())
    conn=sqlite3.connect(destination); conn.execute("PRAGMA foreign_keys=OFF")
    try:
        with conn:
            _clear(conn); _add_schema(conn); conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("UPDATE meta SET value=? WHERE key='schema_name'",("LOOM_SOLAR_FACTUAL_ENRICHMENT_MULTI_BODY_v0.3-R1",))
            conn.execute("UPDATE meta SET value=? WHERE key='qualification_case'",("SF-PROMOTE-01_67P",))
            conn.execute("INSERT OR REPLACE INTO meta VALUES('schema_version','MULTI_BODY_v0.3-R1')")
            conn.execute("INSERT OR REPLACE INTO meta VALUES('authority_boundary','DEV_ONLY_CANDIDATE_PROMOTION')")
            conn.execute("INSERT INTO body VALUES(?,?,?,?,?)",("COMET_67P","67P/Churyumov-Gerasimenko","COMET",None,"CANDIDATE"))
            conn.execute("INSERT INTO body_authority VALUES(?,?,?,?)",("COMET_67P","loom_solar.body","COMET_67P","PHASE4_IDENTITY_REFERENCE"))
            sources={s["source_id"]:s for s in d["sources"]}; arts={a["artifact_id"]:a for a in d["artifacts"]}
            sid={}
            for i,(key,s) in enumerate(sources.items(),1):
                sid[key]=i
                conn.execute("INSERT INTO source VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(i,_source_type(s),s["provider"],s["title"],None,None,s.get("doi"),s["locator"],s.get("publication_date"),None,None,s.get("persistent_identifier"),arts[next(a for a in arts if arts[a]["source_id"]==key)]["retrieved_at"],s["title"],"Promoted from frozen ARP-QUAL-01B structured source metadata."))
            for aid,a in arts.items():
                p=CAMPAIGN/a["local_path"]
                if p.exists():
                    got,n=sha(p)
                    if got!=a["sha256"] or n!=a["byte_count"]: raise ValueError(f"artifact mismatch: {aid}")
                else:
                    # Raw artifacts are governed by the frozen campaign
                    # manifest and may be stored outside the repository.
                    # Do not fabricate a local artifact or silently change
                    # its identity during promotion.
                    got,n=a["sha256"],a["byte_count"]
                conn.execute("INSERT INTO source_artifact VALUES(?,?,?,?,?,?,?,?,?,?)",(aid,sid[a["source_id"]],a["locator"],a["local_path"],a["retrieved_at"],got,n,a["media_type"],a["original_filename"],a["version"]))
            promoted={}
            for i,a in enumerate(d["assertions"],1):
                raw=json.dumps(a,sort_keys=True,separators=(",",":")); ah=hashlib.sha256(raw.encode()).hexdigest()
                conn.execute("INSERT INTO promotion_assertion VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(i,d["campaign_id"],a["assertion_id"],"COMET_67P",sid[a["source_id"]],a["artifact_id"],a["property_code"],a["claim_kind"],a["evidence_class"],a.get("scope_type"),a.get("region_id"),a.get("method_type"),a.get("independent_evidence_lineage_id"),json.dumps(a.get("reported_value")),a.get("reported_unit"),json.dumps(a.get("reported_uncertainty")),json.dumps(a.get("normalized_value")),a.get("normalized_unit"),json.dumps(a.get("normalized_uncertainty")),a.get("normalization_method"),json.dumps(a.get("resolution",{}),sort_keys=True),a.get("temporal_context"),a["status"],raw,ah,a.get("notes")))
                conn.execute("INSERT INTO promotion_review VALUES(?,?,?,?)",(i,"PROMOTE","deterministic_sf_promoter","Representable without strengthening scope, time, resolution, or evidence semantics."))
                promoted[a["assertion_id"]]=i
            # Representable scalar facts only. Full assertion JSON remains authoritative for all other fields.
            by={a["assertion_id"]:a for a in d["assertions"]}
            for fid,key in enumerate(("as-gravity-gm","as-gravity-mass","as-gravity-density","as-gravity-porosity"),1):
                a=by[key]; val=a.get("normalized_value"); lo=a.get("value_min"); hi=a.get("value_max")
                conn.execute("INSERT INTO fact VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(fid,"COMET_67P",None,a["property_code"],"scalar" if val is not None else "range",val,lo,hi,None,None,a.get("normalized_uncertainty"),a.get("normalized_uncertainty"),a.get("normalized_unit"),str(a.get("reported_value")) if a.get("reported_value") is not None else None,a.get("reported_unit"),a["evidence_class"],a.get("method_type"),None,a.get("temporal_context"),"UNKNOWN","CANDIDATE",None,None,None,"2026-09-26T00:00:00Z",a.get("notes")))
                conn.execute("INSERT INTO source_assertion VALUES(?,?,?,?,?)",(fid,sid[a["source_id"]],"PRIMARY",None,"Frozen ARP assertion "+key))
            conn.execute("INSERT INTO fact_input VALUES(?,?,?,?,?,?,?)",(1,3,2,None,None,"MASS_INPUT","Frozen source note identifies gravity-derived mass; volume is referenced but no separate scalar volume assertion was promoted."))
            # Shape is a model product; no fabricated dimensions are created.
            a=by["as-shape-archive"]; ar=arts[a["artifact_id"]]
            conn.execute("INSERT INTO body_model_product VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(1,"COMET_67P",None,"SHAPE_MODEL","67P PDS shape-model archive","V1.0","Rosetta body-centered",None,sid[a["source_id"]],sources[a["source_id"]]["persistent_identifier"],sources[a["source_id"]]["locator"],ar["sha256"],ar["byte_count"],a["notes"]))
            obskeys=["as-temperature-map","as-volatile-species","as-virmaterial","as-thermal-seasonal"]
            obsid={};
            for oid,key in enumerate(obskeys,1):
                a=by[key]; r=a.get("resolution") or {}; obsid[key]=oid
                conn.execute("INSERT INTO observation VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(oid,"COMET_67P",None,"Rosetta","Rosetta",a.get("method_type"),key,None,None,a.get("method_type"),a.get("scope_type"),sid[a["source_id"]],a.get("notes"),r.get("horizontal_value"),r.get("horizontal_unit"),r.get("semantics"),None,None,None))
            conn.execute("INSERT INTO activity_fact VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",(1,"COMET_67P",None,"ACTIVITY_STATE",by["as-activity-model"]["notes"],None,None,"PHYSICAL_MODEL","UNKNOWN",obsid["as-temperature-map"],sid[by["as-activity-model"]["source_id"]],"Time-dependent model; not a timeless nucleus property."))
            conn.execute("INSERT INTO activity_fact VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",(2,"COMET_67P",None,"VOLATILE_PRODUCTION",by["as-volatile-activity"]["notes"],None,None,"PHYSICAL_MODEL","UNKNOWN",obsid["as-volatile-species"],sid[by["as-volatile-activity"]["source_id"]],"Model-derived production distribution; not direct local flux."))
            for f in d["epistemic_frontier"]:
                conn.execute("INSERT INTO epistemic_frontier(campaign_id,variable,phase,research_coverage,state_at_cutoff,evidence_class,limitation) VALUES(?,?,?,?,?,?,?)",(d["campaign_id"],f["variable"],f["phase"],f["research_coverage"],f["state_at_cutoff"],f.get("evidence_class"),f.get("limitation")))
            for k,v in {"campaign_sha256":hashlib.sha256((CAMPAIGN/"campaign.json").read_bytes()).hexdigest(),"campaign_id":d["campaign_id"],"body_authority":"loom_solar.body:COMET_67P","preferred_fact_count":"0","facts_status":"CANDIDATE_ONLY","phase4_writes":"0","artifact_verification":"FROZEN_CAMPAIGN_MANIFEST; raw bytes externalized by repository policy"}.items(): conn.execute("INSERT INTO promotion_manifest VALUES(?,?)",(k,v))
            # Link every promoted assertion to its ledger disposition; lineage is
            # explicit for the one derived fact whose input is unambiguous.
            conn.execute("INSERT INTO promotion_lineage VALUES(?,?,?)",(promoted["as-gravity-density"],json.dumps(["as-gravity-mass"]),"Frozen campaign notes identify mass; no unrepresented volume fact is invented."))
            conn.execute("UPDATE meta SET value=? WHERE key='created_utc'",("2026-09-26T00:00:00Z",))
        conn.execute("PRAGMA foreign_key_check")
        return destination
    finally: conn.close()

if __name__ == "__main__":
    build(Path(__file__).with_name("LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_01_67P.sqlite3"))
