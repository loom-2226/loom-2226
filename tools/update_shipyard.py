from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from design_ledger import build_wayfarer_phase1_ledger  # noqa: E402
from phase2_functional_regions import (  # noqa: E402
    AUTHORITY,
    STATUS,
    TARGET_SOURCES,
    VERSION,
    _sha,
    asdict,
    build_contracts,
    canonical_json,
    phase2_open_item,
    validate_contract,
)

DEFAULT_DB = Path("/storage/emulated/0/Download/LOOM_SHIPYARD/shipyard_design_ledger.sqlite3")
PHASE1_STATE_SUFFIX = "SYNTH-v0.1"
PHASE2_STATE_SUFFIX = "PHASE2-FUNCTIONAL-REGIONS-v0.1"


def _table_names(con: sqlite3.Connection) -> set[str]:
    return {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def _ensure_phase1(path: Path, seed: int) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        build_wayfarer_phase1_ledger(path, seed=seed)
        return
    con = sqlite3.connect(path)
    try:
        required = {"design_run", "design_state", "discipline_result", "dependency_graph", "derived_artifact"}
        if not required.issubset(_table_names(con)):
            raise RuntimeError("Existing SQLite is not a LOOM Shipyard design ledger")
    finally:
        con.close()


def apply_phase2(path: Path, seed: int = 2226) -> dict:
    _ensure_phase1(path, seed)
    contracts = build_contracts(seed)
    for row in contracts:
        validate_contract(row)

    con = sqlite3.connect(path)
    try:
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS functional_region_contract(
                region_id TEXT PRIMARY KEY,
                state_id TEXT NOT NULL,
                source_id TEXT NOT NULL,
                function_class TEXT NOT NULL,
                spatial_status TEXT NOT NULL,
                anchor_json TEXT NOT NULL,
                contract_hash TEXT NOT NULL,
                contract_json TEXT NOT NULL,
                authority_status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS shipyard_migration(
                migration_id TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                source_version TEXT NOT NULL,
                result_json TEXT NOT NULL
            );
            """
        )

        existing = con.execute(
            "SELECT result_json FROM shipyard_migration WHERE migration_id=?",
            (VERSION,),
        ).fetchone()
        if existing:
            result = json.loads(existing[0])
            result["already_applied"] = True
            return result

        parent = con.execute(
            "SELECT state_id,state_json FROM design_state WHERE state_id LIKE ? ORDER BY rowid DESC LIMIT 1",
            (f"%::{PHASE1_STATE_SUFFIX}",),
        ).fetchone()
        if parent is None:
            raise RuntimeError("No Phase-1 governed synthesis state found in editing ledger")

        parent_state_id, parent_json_text = parent
        parent_json = json.loads(parent_json_text)
        old_open = list(parent_json.get("packaging", {}).get("open_items", []))
        targeted = set(TARGET_SOURCES)
        kept = [
            item
            for item in old_open
            if not (
                item.startswith("NO_ADMITTED_VOLUME::")
                and item.split("::", 1)[1] in targeted
            )
        ]
        new_open = kept + [phase2_open_item(c) for c in contracts]
        parent_json.setdefault("packaging", {})["open_items"] = new_open
        parent_json["phase2_functional_regions"] = [asdict(c) for c in contracts]
        parent_json["phase2_status"] = list(STATUS)
        parent_json["phase2_authority_status"] = AUTHORITY

        child_state_id = parent_state_id.replace(PHASE1_STATE_SUFFIX, PHASE2_STATE_SUFFIX)
        child_text = json.dumps(parent_json, sort_keys=True, separators=(",", ":"), allow_nan=False)
        child_hash = _sha(child_text)

        con.execute(
            """
            INSERT OR IGNORE INTO design_state(
                state_id,run_id,candidate_id,parent_state_id,state_kind,state_hash,state_json,provenance_json
            )
            SELECT ?,run_id,candidate_id,?, ?, ?, ?, ?
            FROM design_state WHERE state_id=?
            """,
            (
                child_state_id,
                parent_state_id,
                "PHASE2_FUNCTIONAL_REGION_STATE",
                child_hash,
                child_text,
                json.dumps((VERSION, parent_state_id)),
                parent_state_id,
            ),
        )

        for c in contracts:
            text = canonical_json(c)
            con.execute(
                """
                INSERT OR REPLACE INTO functional_region_contract(
                    region_id,state_id,source_id,function_class,spatial_status,
                    anchor_json,contract_hash,contract_json,authority_status
                ) VALUES(?,?,?,?,?,?,?,?,?)
                """,
                (
                    c.region_id,
                    child_state_id,
                    c.source_id,
                    c.function_class,
                    c.spatial_status,
                    json.dumps(c.anchor_position_m),
                    _sha(text),
                    text,
                    c.authority_status,
                ),
            )

        result = {
            "migration_id": VERSION,
            "database": str(path),
            "parent_state_id": parent_state_id,
            "state_id": child_state_id,
            "state_hash": child_hash,
            "functional_region_count": len(contracts),
            "remaining_open_count": len(new_open),
            "authority_status": AUTHORITY,
            "canon_changed": False,
            "production_shipclasses_changed": False,
            "flight_dynamics_authority": False,
            "already_applied": False,
        }
        con.execute(
            "INSERT INTO shipyard_migration(migration_id,source_version,result_json) VALUES(?,?,?)",
            (VERSION, VERSION, json.dumps(result, sort_keys=True)),
        )
        con.commit()
        return result
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Apply governed LOOM Shipyard migrations to the persistent local editing SQLite")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--seed", type=int, default=2226)
    args = parser.parse_args(argv)
    result = apply_phase2(args.db.expanduser().resolve(), args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
