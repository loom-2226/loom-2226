from __future__ import annotations

import importlib.util
import json
import shutil
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATE = ROOT / "src" / "shipyard_migrate.py"
BASELINE = ROOT / "qualification" / "synthesis"

spec = importlib.util.spec_from_file_location("shipyard_migrate", MIGRATE)
shipyard_migrate = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(shipyard_migrate)


def _build_phase1(path: Path) -> None:
    import sys
    if str(BASELINE) not in sys.path:
        sys.path.insert(0, str(BASELINE))
    from design_ledger import build_wayfarer_phase1_ledger
    build_wayfarer_phase1_ledger(path)


def test_standalone_migration_is_idempotent(tmp_path: Path) -> None:
    db = tmp_path / "shipyard.sqlite3"
    _build_phase1(db)
    first = shipyard_migrate.apply_phase2(db)
    second = shipyard_migrate.apply_phase2(db)
    assert first["functional_region_count"] == 9
    assert first["already_applied"] is False
    assert second["already_applied"] is True
    con = sqlite3.connect(db)
    try:
        assert con.execute("SELECT COUNT(*) FROM functional_region_contract").fetchone()[0] == 9
        assert con.execute("SELECT COUNT(*) FROM shipyard_migration").fetchone()[0] == 1
        state = con.execute("SELECT state_json FROM design_state WHERE state_kind='PHASE2_FUNCTIONAL_REGION_STATE'").fetchone()
        assert state is not None
        payload = json.loads(state[0])
        assert len(payload["phase2_functional_regions"]) == 9
        assert all(row["spatial_envelope_m"] is None for row in payload["phase2_functional_regions"])
    finally:
        con.close()


def test_refuses_non_shipyard_sqlite(tmp_path: Path) -> None:
    db = tmp_path / "wrong.sqlite3"
    sqlite3.connect(db).close()
    try:
        shipyard_migrate.apply_phase2(db)
    except RuntimeError as exc:
        assert "not a LOOM Shipyard" in str(exc)
    else:
        raise AssertionError("migration accepted a non-Shipyard SQLite")
