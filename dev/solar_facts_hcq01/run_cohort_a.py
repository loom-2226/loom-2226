from __future__ import annotations

import json
import shutil
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from ingest.acquire import acquire
from ingest.audit import audit
from ingest.extract.research_json import extract_payload
from ingest.load import ensure_identity_anchor, load_candidate
from ingest.normalize import normalize
from ingest.validate import validate
from dataclasses import replace

ROOT = Path(__file__).resolve().parent
DB = ROOT / "LOOM_SOLAR_HCQ01_CERES.sqlite3"
RECORDS = ROOT / "cohort_a_records.json"
RAW_DIR = ROOT / "artifacts" / "acquired"


def main() -> int:
    payload = json.loads(RECORDS.read_text(encoding="utf-8"))
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    summary = Counter()
    loaded_sources = []
    with sqlite3.connect(DB) as conn:
        conn.execute("PRAGMA foreign_keys=ON")
        ensure_identity_anchor(conn)
        for index, item in enumerate(payload["records"], 1):
            source_path = ROOT / item["artifact_path"]
            destination = RAW_DIR / f"{index:02d}_{source_path.name}"
            artifact = acquire(f"file://{source_path}", destination,
                               retrieved_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"))
            record = normalize(extract_payload(item, artifact=artifact, extractor_name="cohort_a_json"))
            products = []
            for product_index, product in enumerate(record.model_products, 1):
                if product.artifact_path:
                    product_source = ROOT / product.artifact_path
                    product_artifact = acquire(
                        f"file://{product_source}",
                        RAW_DIR / f"{index:02d}_product_{product_index}_{product_source.name}",
                        retrieved_at=artifact.retrieved_at,
                    )
                    product = replace(product, sha256=product_artifact.sha256, byte_count=product_artifact.byte_count)
                products.append(product)
            gravity_models = []
            for model_index, model in enumerate(record.gravity_models, 1):
                if model.artifact_path:
                    model_source = ROOT / model.artifact_path
                    model_artifact = acquire(
                        f"file://{model_source}",
                        RAW_DIR / f"{index:02d}_gravity_{model_index}_{model_source.name}",
                        retrieved_at=artifact.retrieved_at,
                    )
                    model = replace(model, sha256=model_artifact.sha256, byte_count=model_artifact.byte_count)
                gravity_models.append(model)
            record = replace(record, model_products=tuple(products), gravity_models=tuple(gravity_models))
            report = validate(conn, record)
            summary[report.decision] += 1
            if report.decision != "PASS":
                summary.update(f"reason:{finding.code}" for finding in report.findings)
                continue
            loaded = load_candidate(conn, record)
            result = audit(conn, record, record.source.raw_artifact, loaded)
            loaded_sources.append(result)
        (ROOT / "cohort_a_run_report.json").write_text(json.dumps({
            "qualification_case": "HCQ-01_CERES",
            "cohort": "A",
            "decisions": dict(summary),
            "sources": loaded_sources,
            "cutoff": "2025-12-31T23:59:59Z"
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(dict(summary), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
