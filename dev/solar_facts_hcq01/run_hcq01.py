from __future__ import annotations

import json
import shutil
import sqlite3
from collections import Counter
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from ingest.acquire import acquire
from ingest.audit import audit
from ingest.extract.research_json import extract_payload
from ingest.load import ensure_identity_anchor, load_candidate
from ingest.normalize import normalize
from ingest.validate import validate

ROOT = Path(__file__).resolve().parent
DB = ROOT / "LOOM_SOLAR_HCQ01_CERES.sqlite3"
SCHEMA = ROOT / "schema.sql"
RAW_DIR = ROOT / "artifacts" / "acquired"


def reset_candidate_tables(conn: sqlite3.Connection) -> None:
    for table in (
        "fact_observation", "source_assertion", "preferred_fact", "derived_input", "derived_quantity",
        "gravity_model", "orientation_model", "body_model_product", "region_model_product", "activity_fact",
        "material_evidence", "observation", "body_region", "fact", "source", "body",
    ):
        conn.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.execute("VACUUM")


def now() -> str:
    return "2026-09-26T00:00:00Z"


def main() -> int:
    a = json.loads((ROOT / "cohort_a_records.json").read_text(encoding="utf-8"))["records"]
    bh = json.loads((ROOT / "cohort_bh_records.json").read_text(encoding="utf-8"))["records"]
    records = [("A", item) for item in a] + [(item["cohort"], item) for item in bh]
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    summary = Counter()
    reports = []
    if DB.exists():
        DB.unlink()
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    contract_db = sqlite3.connect(ROOT / "round1_qualification_artifact/LOOM_SOLAR_HCQ01_CERES.sqlite3")
    conn.executemany("INSERT INTO meta(key,value) VALUES(?,?)", contract_db.execute("SELECT key,value FROM meta"))
    conn.executemany("INSERT INTO property_definition(property_code,property_group,canonical_name,description,canonical_unit,expected_value_kind,derivable,notes) VALUES(?,?,?,?,?,?,?,?)", contract_db.execute("SELECT property_code,property_group,canonical_name,description,canonical_unit,expected_value_kind,derivable,notes FROM property_definition"))
    contract_db.close()
    ensure_identity_anchor(conn)
    for index, (cohort, item) in enumerate(records, 1):
        source_path = ROOT / item["artifact_path"]
        destination = RAW_DIR / f"{index:02d}_{cohort}_{source_path.name}"
        artifact = acquire(f"file://{source_path}", destination, retrieved_at=now())
        record = normalize(extract_payload(item, artifact=artifact, extractor_name=f"hcq01_cohort_{cohort.lower()}"))
        products = []
        for product_index, product in enumerate(record.model_products, 1):
            if product.artifact_path:
                product_source = ROOT / product.artifact_path
                product_artifact = acquire(f"file://{product_source}", RAW_DIR / f"{index:02d}_product_{product_index}_{product_source.name}", retrieved_at=artifact.retrieved_at)
                product = replace(product, sha256=product_artifact.sha256, byte_count=product_artifact.byte_count)
            products.append(product)
        gravity_models = []
        for model_index, model in enumerate(record.gravity_models, 1):
            if model.artifact_path:
                model_source = ROOT / model.artifact_path
                model_artifact = acquire(f"file://{model_source}", RAW_DIR / f"{index:02d}_gravity_{model_index}_{model_source.name}", retrieved_at=artifact.retrieved_at)
                model = replace(model, sha256=model_artifact.sha256, byte_count=model_artifact.byte_count)
            gravity_models.append(model)
        record = replace(record, model_products=tuple(products), gravity_models=tuple(gravity_models))
        report = validate(conn, record)
        summary[report.decision] += 1
        for finding in report.findings:
            summary[f"reason:{finding.code}"] += 1
        entry = {"cohort": cohort, "title": record.source.title, "decision": report.decision,
                 "findings": [finding.__dict__ for finding in report.findings]}
        if report.decision == "PASS":
            loaded = load_candidate(conn, record)
            entry["audit"] = audit(conn, record, record.source.raw_artifact, loaded)
            entry["loaded"] = loaded
        reports.append(entry)
    conn.commit()
    (ROOT / "hcq01_run_report.json").write_text(json.dumps({"qualification_case":"HCQ-01_CERES","cutoff":"2025-12-31T23:59:59Z","decisions":dict(summary),"records":reports}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    counts = {}
    for table in ("body","source","observation","body_region","fact","source_assertion","material_evidence","activity_fact","body_model_product","gravity_model","orientation_model","derived_quantity","derived_input","preferred_fact"):
        counts[table] = conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
    print(json.dumps({"decisions":dict(summary),"counts":counts,"integrity":conn.execute("PRAGMA integrity_check").fetchone()[0],"foreign_keys":conn.execute("PRAGMA foreign_key_check").fetchall()}, indent=2, sort_keys=True))
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
