"""Deterministic, body-neutral SF-PROMOTE-02 builder.

The frozen Ceres HCQ database is an input representation.  This adapter copies
its typed records into the generic SF-PROMOTE-01 database and records every
source scientific object in the promotion ledger.  It does not infer new
science, resolve conflicts, or populate preferred facts.
"""
from __future__ import annotations
import hashlib, json, shutil, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "dev/solar_facts_multi_body/sf_promote_01_67p/LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_01_67P.sqlite3"
CERES = ROOT / "dev/solar_facts_hcq01/v0_3_r1/LOOM_SOLAR_HCQ01_CERES_v0_3_R1.sqlite3"
OUT = Path(__file__).with_name("LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_02_CERES_67P.sqlite3")
BODY = "CERES"

def sha256(path: Path):
    h = hashlib.sha256(); n = 0
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk); n += len(chunk)
    return h.hexdigest(), n

def rows(c, table):
    c.row_factory = sqlite3.Row
    return [dict(r) for r in c.execute(f"SELECT * FROM {table}")]

def j(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)

def insert_dynamic(c, table, record):
    cols = list(record)
    marks = ",".join("?" for _ in cols)
    c.execute(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({marks})", [record[x] for x in cols])

def build(destination: Path = OUT):
    destination.parent.mkdir(parents=True, exist_ok=True)
    expected = "0bbbfd5ae2ab287900ff4e356f9571d21aff4593cc78e0cd69bf1610def9adc6"
    actual, _ = sha256(CERES)
    if actual != expected:
        raise RuntimeError(f"frozen Ceres hash mismatch: {actual}")
    shutil.copy2(BASE, destination)
    con = sqlite3.connect(destination)
    src = sqlite3.connect(CERES)
    con.row_factory = sqlite3.Row
    src.row_factory = sqlite3.Row
    try:
        con.execute("PRAGMA foreign_keys=OFF")
        with con:
            con.execute("UPDATE meta SET value=? WHERE key='schema_name'", ("LOOM_SOLAR_FACTUAL_ENRICHMENT_MULTI_BODY_v0.3-R1",))
            con.execute("UPDATE meta SET value=? WHERE key='qualification_case'", ("SF-PROMOTE-02_CERES_67P",))
            con.execute("INSERT OR REPLACE INTO meta VALUES('schema_version','MULTI_BODY_v0.3-R1')")
            con.execute("INSERT OR REPLACE INTO meta VALUES('authority_boundary','DEV_ONLY_CANDIDATE_PROMOTION')")
            con.execute("INSERT INTO body VALUES(?,?,?,?,?)", (BODY, "Ceres", "DWARF_PLANET", None, "CANDIDATE"))
            con.execute("INSERT INTO body_authority VALUES(?,?,?,?)", (BODY, "loom_solar.body", BODY, "PHASE4_IDENTITY_REFERENCE"))

            # Existing 67P source IDs occupy 1..9.  Ceres scientific source IDs
            # occupy 10..25; source 26 is only the frozen-container provenance
            # record and is never used as scientific evidence.
            source_map = {}
            for old in rows(src, "source"):
                new = old["source_id"] + 9; source_map[old["source_id"]] = new
                rec = dict(old); rec["source_id"] = new
                insert_dynamic(con, "source", rec)
            corpus_source = 26
            insert_dynamic(con, "source", {"source_id": corpus_source, "source_type": "DATA_PRODUCT", "provider": "LOOM HCQ qualification", "title": "Frozen HCQ-01 Ceres v0.3-R1 corpus container", "authors": None, "journal": None, "doi": None, "url": "repo://dev/solar_facts_hcq01/v0_3_r1/LOOM_SOLAR_HCQ01_CERES_v0_3_R1.sqlite3", "publication_date": None, "product_name": "HCQ-01_CERES", "product_version": "v0.3-R1", "persistent_identifier": "SHA256:" + actual, "retrieved_at": "2026-09-26T00:00:00Z", "citation_text": "Frozen input container; not a scientific source.", "notes": "Provenance carrier only; scientific source rows remain the 16 HCQ sources."})
            insert_dynamic(con, "source_artifact", {"artifact_id": "HCQ01-CERES-FROZEN-DB", "source_id": corpus_source, "locator": "repo://dev/solar_facts_hcq01/v0_3_r1/LOOM_SOLAR_HCQ01_CERES_v0_3_R1.sqlite3", "local_path": "dev/solar_facts_hcq01/v0_3_r1/LOOM_SOLAR_HCQ01_CERES_v0_3_R1.sqlite3", "retrieved_at": "2026-09-26T00:00:00Z", "sha256": actual, "byte_count": CERES.stat().st_size, "media_type": "application/vnd.sqlite3", "original_filename": CERES.name, "version": "v0.3-R1"})

            # Copy typed Ceres records with deterministic offsets.
            offsets = {"fact": 4, "observation": 4, "activity_fact": 2, "body_model_product": 1, "region_model_product": 0, "gravity_model": 0, "orientation_model": 0, "derived_quantity": 0, "knowledge_event": 4}
            region_map = {}
            for old in rows(src, "body_region"):
                region_map[old["region_id"]] = old["region_id"]
                rec = dict(old); rec["body_id"] = BODY
                insert_dynamic(con, "body_region", rec)
            for table in ["fact", "observation", "activity_fact", "body_model_product", "gravity_model", "orientation_model", "derived_quantity"]:
                off = offsets[table]
                for old in rows(src, table):
                    rec = dict(old)
                    key = {"fact":"fact_id", "observation":"observation_id", "activity_fact":"activity_id", "body_model_product":"model_product_id", "gravity_model":"gravity_model_id", "orientation_model":"orientation_model_id", "derived_quantity":"derived_id"}[table]
                    rec[key] = old[key] + off; rec["body_id"] = BODY
                    if "source_id" in rec and rec["source_id"] is not None: rec["source_id"] = source_map[rec["source_id"]]
                    if "region_id" in rec and rec["region_id"] is not None: rec["region_id"] = region_map[rec["region_id"]]
                    if table == "activity_fact" and rec.get("observation_id") is not None: rec["observation_id"] += 4
                    insert_dynamic(con, table, rec)
            for old in rows(src, "region_model_product"):
                insert_dynamic(con, "region_model_product", dict(old))
            for old in rows(src, "material_evidence"):
                rec = dict(old); rec["body_id"] = BODY
                rec["source_id"] = source_map[rec["source_id"]]; rec["observation_id"] += 4
                if rec["region_id"] is not None: rec["region_id"] = region_map[rec["region_id"]]
                insert_dynamic(con, "material_evidence", rec)
            for old in rows(src, "body_region"):
                pass
            for old in rows(src, "fact_observation"):
                rec = dict(old); rec["fact_id"] += 4; rec["observation_id"] += 4; insert_dynamic(con, "fact_observation", rec)
            for old in rows(src, "fact_input"):
                rec = dict(old); rec["fact_id"] += 4
                rec["fact_input_id"] += 1
                if rec["input_fact_id"] is not None: rec["input_fact_id"] += 4
                if rec["input_observation_id"] is not None: rec["input_observation_id"] += 4
                if rec["input_model_product_id"] is not None: rec["input_model_product_id"] += 1
                insert_dynamic(con, "fact_input", rec)
            for old in rows(src, "derived_input"):
                rec = dict(old); rec["derived_id"] += 0; rec["fact_id"] += 4; insert_dynamic(con, "derived_input", rec)
            for old in rows(src, "source_assertion"):
                rec = dict(old); rec["fact_id"] += 4; rec["source_id"] = source_map[rec["source_id"]]; insert_dynamic(con, "source_assertion", rec)
            for old in rows(src, "knowledge_event"):
                rec = dict(old); rec["knowledge_event_id"] += 4
                for k, off in (("target_fact_id",4),("target_observation_id",4),("target_model_product_id",1),("target_source_id",9),("source_id",9)):
                    if rec[k] is not None: rec[k] += off
                insert_dynamic(con, "knowledge_event", rec)

            # Every Ceres candidate/evidence/model/lineage object gets an
            # explicit ledger disposition. Raw rows are retained verbatim.
            ledger = []
            def add(kind, table, key, row, source_id=None, region_id=None, prop=None):
                ledger.append((kind, table, key, row, source_id, region_id, prop))
            for table, kind, key, propcol in [("fact","FACT","fact_id","property_code"),("observation","OBSERVATION","observation_id",None),("material_evidence","MATERIAL_EVIDENCE","material_evidence_id","material_family"),("activity_fact","ACTIVITY_INTERPRETATION","activity_id","activity_type"),("body_model_product","BODY_MODEL_PRODUCT","model_product_id","model_type"),("region_model_product","REGION_MODEL_PRODUCT","region_id",None),("gravity_model","GRAVITY_MODEL","gravity_model_id","model_name"),("orientation_model","ORIENTATION_MODEL","orientation_model_id","model_name"),("derived_quantity","DERIVED_QUANTITY","derived_id","property_code"),("body_region","REGION","region_id","canonical_name"),("knowledge_event","KNOWLEDGE_EVENT","knowledge_event_id","event_key"),("source_assertion","SOURCE_ASSERTION","fact_id",None)]:
                for row in rows(src, table):
                    if table == "source_assertion": sid = source_map[row["source_id"]]; rid = None
                    else: sid = source_map.get(row.get("source_id")); rid = row.get("region_id")
                    add(kind, table, row[key], row, sid, rid, row.get(propcol) if propcol else kind)
            for i, (kind, table, key, row, sid, rid, prop) in enumerate(sorted(ledger, key=lambda x:(x[0],x[2])), 1):
                pid = i + 13
                raw = j(row); assertion_id = f"CERES:{kind}:{key}:{i}"
                claim_kind = "INTERPRETATION" if kind == "ACTIVITY_INTERPRETATION" else ("DERIVATION" if kind in ("DERIVED_QUANTITY","GRAVITY_MODEL","ORIENTATION_MODEL") else kind)
                evidence = row.get("evidence_class") or "STRUCTURED_PROVENANCE"
                insert_dynamic(con, "promotion_assertion", {"promotion_assertion_id": pid, "campaign_id":"HCQ-01_CERES", "assertion_id":assertion_id, "body_id":BODY, "source_id":sid or corpus_source, "artifact_id":"HCQ01-CERES-FROZEN-DB", "property_code":str(prop or kind), "claim_kind":claim_kind, "evidence_class":evidence, "scope_type":row.get("spatial_context") or ("REGION" if rid is not None else "BODY"), "region_id":rid, "method_type":row.get("measurement_method"), "independent_lineage_id":None, "reported_value_json":j(row.get("reported_value_text")), "reported_unit":row.get("reported_unit"), "reported_uncertainty_json":None, "normalized_value_json":j(row.get("value_numeric")), "normalized_unit":row.get("canonical_unit"), "normalized_uncertainty_json":j({"plus":row.get("uncertainty_plus"),"minus":row.get("uncertainty_minus")}), "normalization_method":"STRUCTURAL_COPY_ONLY", "resolution_json":j({"spatial_context":row.get("spatial_context"),"spatial_resolution_value":row.get("spatial_resolution_value")}), "temporal_context":row.get("temporal_context") or row.get("event_time"), "status":"CANDIDATE", "raw_assertion_json":raw, "raw_sha256":hashlib.sha256(raw.encode()).hexdigest(), "notes":"HCQ frozen typed record; no scientific strengthening."})
                insert_dynamic(con, "promotion_review", {"promotion_assertion_id":pid,"disposition":"PROMOTE","reviewer":"deterministic_sf_promoter","reason":"Generic schema preserves the frozen typed record without changing scope, evidence class, uncertainty, temporal meaning, or candidate status."})
            # Derived volume lineage is explicit; Ceres fact-input rows preserve
            # the two fact dependencies in the typed destination tables.
            for row in rows(src, "derived_quantity"):
                pid = 13 + next(i for i,x in enumerate(sorted(ledger,key=lambda x:(x[0],x[2])),1) if x[0]=="DERIVED_QUANTITY" and x[2]==row["derived_id"])
                con.execute("INSERT INTO promotion_lineage VALUES(?,?,?)", (pid, j(["CERES:FACT:3", "CERES:FACT:2"]), "Frozen HCQ derived quantity lineage; input identities remain body-scoped."))
            manifest = {"campaign_id":"HCQ-01_CERES", "ceres_hcq_sha256":actual, "body_authority":"loom_solar.body:CERES", "preferred_fact_count":"0", "facts_status":"CANDIDATE_ONLY", "schema_change":"NONE", "artifact_provenance":"HCQ container artifact preserved; scientific source rows remain asymmetric to 67P", "promotion_ledger_count":str(len(ledger))}
            for k,v in manifest.items(): con.execute("INSERT OR REPLACE INTO promotion_manifest VALUES(?,?)", (k,v))
            con.execute("UPDATE meta SET value=? WHERE key='created_utc'", ("2026-09-26T00:00:00Z",))
        con.execute("PRAGMA foreign_keys=ON")
        fk = list(con.execute("PRAGMA foreign_key_check"))
        if fk: raise RuntimeError(f"foreign key errors: {fk[:3]}")
    finally:
        src.close(); con.close()
    return destination

if __name__ == "__main__": build()
