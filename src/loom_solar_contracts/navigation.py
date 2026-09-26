"""Consumer-derived minimum Solar navigation readiness contract."""
from __future__ import annotations
import json, sqlite3
from datetime import datetime
from pathlib import Path

CONTRACT_VERSION = "NAV_MINIMUM_INPUT_CONTRACT_V1"
NAV1_EPOCH_UTC = "2226-08-22T00:00:00Z"
NAV1_REQUIRED = ("LOOM_BODY_IDENTITY","ACTIVE_NAIF_ID","QUALIFIED_POSITION_VELOCITY_EPHEMERIS_AT_EPOCH","REFERENCE_FRAME_AND_UNITS","VALIDITY_INTERVAL","SOURCE_PROVENANCE")
NAV1_NOT_REQUIRED_BY_CURRENT_DIRECT_SOLVER = ("GM","MASS","RADIUS","ROTATION","ORIENTATION","SHAPE_MODEL")

def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def load_phase4_coverage(manifest_dir: Path) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for path in sorted(manifest_dir.glob("*.json")):
        try: doc=json.loads(path.read_text())
        except (json.JSONDecodeError,UnicodeDecodeError): continue
        pools=[]
        if isinstance(doc.get("coverage"),list): pools.extend(doc["coverage"])
        registry=doc.get("registry") or {}
        if isinstance(registry.get("coverage"),list): pools.extend(registry["coverage"])
        for row in pools:
            if row.get("body_id") and row.get("status")=="QUALIFIED":
                out.setdefault(row["body_id"],[]).append({**row,"manifest":str(path)})
        if doc.get("manifest_id")=="SOLAR_PHASE4_EARNED_AUTHORITY_V1":
            horizon=doc["horizon_contract"]
            for row in doc.get("targets",[]):
                if row.get("full_2250"):
                    out.setdefault(row["body_id"],[]).append({
                        "ephemeris_source_id":row["source"],"body_id":row["body_id"],
                        "valid_from":horizon["modeled_start"],"valid_until":horizon["full_2250_gate"],
                        "reference_frame":"ECLIPJ2000","units":"km,km/s",
                        "coverage_class":"EARNED_AUTHORITY_TARGET","status":"QUALIFIED","manifest":str(path)})
    return out

def assess(db_path: Path, manifest_dir: Path, epoch_utc: str=NAV1_EPOCH_UTC) -> dict:
    db=sqlite3.connect(db_path)
    bodies={r[0]:{"body_id":r[0],"canonical_name":r[1],"body_class":r[2],"parent_body_id":r[3]} for r in db.execute("SELECT body_id,canonical_name,body_class,parent_body_id FROM authority_body_ref")}
    ids={}
    for body_id,value in db.execute("SELECT body_id,identifier_value FROM body_identifier_ref WHERE authority='NAIF' AND identifier_type='NAIF_ID' AND identifier_status='ACTIVE'"):
        ids.setdefault(body_id,[]).append(value)
    coverage=load_phase4_coverage(manifest_dir); epoch=_dt(epoch_utc); rows=[]
    for body_id in sorted(bodies):
        active=ids.get(body_id,[])
        valid=[r for r in coverage.get(body_id,[]) if _dt(r["valid_from"])<=epoch<=_dt(r["valid_until"])]
        nav0="SUPPORTED" if len(active)==1 else ("AMBIGUOUS" if len(active)>1 else "MISSING")
        nav1="SUPPORTED" if nav0=="SUPPORTED" and valid else "MISSING"
        rows.append({**bodies[body_id],"nav0":nav0,"nav1":nav1,"active_naif_ids":active,"qualified_ephemeris_at_epoch":len(valid),"ephemeris_sources":[r.get("ephemeris_source_id") for r in valid]})
    return {"contract":CONTRACT_VERSION,"assessment_epoch_utc":epoch_utc,"authority_rule":"MEASURE_EXISTING_AUTHORITY_ONLY_NO_PROMOTION","nav1_required":list(NAV1_REQUIRED),"nav1_not_required_by_current_direct_solver":list(NAV1_NOT_REQUIRED_BY_CURRENT_DIRECT_SOLVER),"counts":{"bodies":len(rows),"nav0_supported":sum(r["nav0"]=="SUPPORTED" for r in rows),"nav1_supported":sum(r["nav1"]=="SUPPORTED" for r in rows),"nav1_missing":sum(r["nav1"]!="SUPPORTED" for r in rows)},"bodies":rows}
