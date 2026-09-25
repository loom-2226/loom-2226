from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

from .models import RawArtifact, StagingRecord


def audit(conn: sqlite3.Connection, record: StagingRecord, raw: RawArtifact, loaded: dict[str, int | list[int]]) -> dict:
    data = Path(raw.path).read_bytes()
    actual_sha = hashlib.sha256(data).hexdigest()
    if actual_sha != raw.sha256 or len(data) != raw.byte_count:
        raise AssertionError("raw artifact changed after acquisition")
    source_id = int(loaded["source_id"])
    fact_ids = [int(i) for i in loaded["fact_ids"]]  # type: ignore[index]
    rows = []
    if fact_ids:
        rows = conn.execute("SELECT fact_id, property_code, reported_value_text, reported_unit, canonical_unit, fact_status FROM fact WHERE fact_id IN (%s)" % ",".join("?" * len(fact_ids)), fact_ids).fetchall()
    if len(rows) != len(fact_ids) or any(row[5] != "CANDIDATE" for row in rows):
        raise AssertionError("candidate facts missing or promoted")
    assertions = conn.execute("SELECT fact_id, source_id FROM source_assertion WHERE source_id=?", (source_id,)).fetchall()
    if {row[0] for row in assertions} != set(fact_ids):
        raise AssertionError("incomplete source assertion lineage")
    model_product_ids = [int(i) for i in loaded.get("model_product_ids", [])]  # type: ignore[union-attr]
    gravity_model_ids = [int(i) for i in loaded.get("gravity_model_ids", [])]  # type: ignore[union-attr]
    derived_ids = [int(i) for i in loaded.get("derived_ids", [])]  # type: ignore[union-attr]
    if model_product_ids:
        count = conn.execute("SELECT count(*) FROM body_model_product WHERE source_id=? AND model_product_id IN (%s)" % ",".join("?" * len(model_product_ids)), [source_id, *model_product_ids]).fetchone()[0]
        if count != len(model_product_ids):
            raise AssertionError("incomplete model-product provenance")
    if gravity_model_ids:
        count = conn.execute("SELECT count(*) FROM gravity_model WHERE source_id=? AND gravity_model_id IN (%s)" % ",".join("?" * len(gravity_model_ids)), [source_id, *gravity_model_ids]).fetchone()[0]
        if count != len(gravity_model_ids):
            raise AssertionError("incomplete gravity-model provenance")
    if derived_ids:
        count = conn.execute("SELECT count(*) FROM derived_quantity WHERE derived_id IN (%s)" % ",".join("?" * len(derived_ids)), derived_ids).fetchone()[0]
        if count != len(derived_ids):
            raise AssertionError("incomplete derived-quantity provenance")
    result = {
        "source_id": source_id, "raw_artifact": {"path": raw.path, "url": raw.original_url,
        "retrieved_at": raw.retrieved_at, "sha256": raw.sha256, "byte_count": raw.byte_count},
        "fact_ids": fact_ids, "model_product_ids": model_product_ids,
        "gravity_model_ids": gravity_model_ids, "derived_ids": derived_ids,
        "fact_rows": [dict(zip(("fact_id", "property_code", "reported_value_text", "reported_unit", "normalized_unit", "fact_status"), row)) for row in rows],
        "assertion_count": len(assertions), "complete": True,
    }
    manifest = Path(raw.path).parent / f"{Path(raw.path).stem}.audit.json"
    manifest.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
