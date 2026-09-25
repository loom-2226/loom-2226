#!/usr/bin/env python3
"""Build and qualify the durable Ceres PostgreSQL forensic archive."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

SCHEMAS = ("loom_control", "loom_world", "loom_civ", "loom_media", "loom_ceres")
CERES = "ceres-v1-0231e5f7da744728ab5021268b6f239b"


def psql(db: str, sql: str) -> str:
    r = subprocess.run(["psql", "-X", "-qAt", "-v", "ON_ERROR_STOP=1", "-d", db, "-c", sql], capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()


def tables(db: str, schema: str) -> list[str]:
    return psql(db, f"SELECT table_name FROM information_schema.tables WHERE table_schema={schema!r} AND table_type='BASE TABLE' ORDER BY table_name").splitlines()


def fingerprint(db: str, schema: str, table: str) -> dict:
    cols = psql(db, f"SELECT column_name FROM information_schema.columns WHERE table_schema={schema!r} AND table_name={table!r} ORDER BY ordinal_position").splitlines()
    qi = lambda x: '"' + x.replace('"', '""') + '"'
    names = ", ".join(qi(c) for c in cols)
    q = f"COPY (SELECT row_to_json(x)::text FROM (SELECT {names} FROM {qi(schema)}.{qi(table)} ORDER BY {names}) x) TO STDOUT"
    r = subprocess.Popen(["psql", "-X", "-qAt", "-v", "ON_ERROR_STOP=1", "-d", db, "-c", q], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    h, count = hashlib.sha256(), 0
    assert r.stdout is not None
    for line in r.stdout: h.update(line); count += 1
    err = r.stderr.read().decode(); code = r.wait()
    if code: raise RuntimeError(err.strip())
    return {"schema": schema, "table": table, "columns": cols, "row_count": count, "content_sha256": h.hexdigest()}


def build(db: str) -> dict:
    inventory = [fingerprint(db, s, t) for s in SCHEMAS for t in tables(db, s)]
    state = psql(db, f"SELECT state FROM loom_control.snapshot WHERE snapshot_id={CERES!r}")
    return {"archive_contract": "1", "database": db, "snapshot_id": CERES, "snapshot_state": state,
            "tables": inventory,
            "overall_sha256": hashlib.sha256(json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode()).hexdigest()}


def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("--database", required=True); p.add_argument("--output", type=Path, required=True); p.add_argument("--compare", type=Path)
    a = p.parse_args(); out = build(a.database)
    if out["snapshot_id"] != CERES or out["snapshot_state"] != "VALIDATED": raise SystemExit("Ceres snapshot identity/state failed")
    if a.compare:
        prior = json.loads(a.compare.read_text())
        if prior["overall_sha256"] != out["overall_sha256"]: raise SystemExit(json.dumps({"status":"FAIL","pre":prior["overall_sha256"],"post":out["overall_sha256"]}))
        out["comparison"] = "EXACT_PAYLOAD_PASS"
    a.output.parent.mkdir(parents=True, exist_ok=True); a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status":"PASS", "overall_sha256":out["overall_sha256"], "output":str(a.output)}))


if __name__ == "__main__": main()
