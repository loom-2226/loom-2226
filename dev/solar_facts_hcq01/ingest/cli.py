from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from .acquire import acquire
from .audit import audit
from .extract.research_json import extract
from .load import ensure_identity_anchor, load_candidate
from .normalize import normalize
from .validate import validate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--raw", required=True, type=Path)
    args = parser.parse_args()
    artifact = acquire(args.source, args.raw)
    record = normalize(extract(args.raw, artifact=artifact))
    with sqlite3.connect(args.database) as conn:
        conn.execute("PRAGMA foreign_keys=ON")
        ensure_identity_anchor(conn)
        report = validate(conn, record)
        if report.decision != "PASS":
            print(json.dumps({"decision": report.decision, "findings": [f.__dict__ for f in report.findings]}, indent=2))
            return 2 if report.decision == "REJECT" else 3
        loaded = load_candidate(conn, record)
        result = audit(conn, record, artifact, loaded)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
