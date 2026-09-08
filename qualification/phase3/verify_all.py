from __future__ import annotations

import hashlib
import importlib
import json
import math
import platform
import sqlite3
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, Iterable

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
DB_PATH = OUTPUT / "LOOM_2226_SHIPCLASSES_PHASE3.sqlite3"
RESULT_PATH = OUTPUT / "phase3_verification_result.json"

SCHEMA = ROOT / "LOOM_2226_SHIPCLASSES_PROTOTYPE_SCHEMA_v0.1.sql"
SEED = ROOT / "LOOM_2226_SHIPCLASSES_WAYFARER_SEED_v0.1.sql"
OVERLAY = ROOT / "LOOM_2226_SHIPCLASSES_WAYFARER_GEOMETRY_COUPLING_v0.1.sql"

REQUIRED = [
    SCHEMA,
    SEED,
    OVERLAY,
    ROOT / "shipclasses_resolver.py",
    ROOT / "shipclasses_geometry_resolver.py",
    ROOT / "test_phase3_wayfarer.py",
    ROOT / "test_phase3_geometry_coupling.py",
]

EXPECTED = {
    "docked_wet_mass_kg": 1158500.0,
    "docked_wet_com_B_m": [26.676650841605525, 0.0, 0.14812257229175657],
    "absent_wet_mass_kg": 1125500.0,
    "absent_wet_com_B_m": [26.819635717458908, 0.0, 0.0],
    "launch_pose_B_m": [21.8, 0.0, 5.2],
    "store_mass_kg": 300000.0,
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_db_snapshot(conn: sqlite3.Connection) -> Dict[str, Any]:
    tables = [
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]
    payload: Dict[str, Any] = {}
    for table in tables:
        columns = [r[1] for r in conn.execute(f'PRAGMA table_info("{table}")')]
        rows = [list(r) for r in conn.execute(f'SELECT * FROM "{table}"')]
        rows.sort(key=lambda row: json.dumps(row, sort_keys=True, separators=(",", ":"), default=str))
        payload[table] = {"columns": columns, "rows": rows}
    return payload


def snapshot_hash(conn: sqlite3.Connection) -> str:
    blob = json.dumps(
        canonical_db_snapshot(conn), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def build_db() -> sqlite3.Connection:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    for path in (SCHEMA, SEED, OVERLAY):
        conn.executescript(path.read_text(encoding="utf-8"))
    conn.commit()
    return conn


def vector_error(actual: Iterable[float], expected: Iterable[float]) -> float:
    return max(abs(float(a) - float(e)) for a, e in zip(actual, expected))


def run_unit_suite() -> Dict[str, Any]:
    suite = unittest.defaultTestLoader.discover(str(ROOT), pattern="test_phase3_*.py")
    result = unittest.TestResult()
    suite.run(result)
    return {
        "tests_run": result.testsRun,
        "failures": [f"{test}: {text}" for test, text in result.failures],
        "errors": [f"{test}: {text}" for test, text in result.errors],
        "skipped": [f"{test}: {reason}" for test, reason in result.skipped],
        "passed": result.wasSuccessful() and result.testsRun > 0,
    }


def main() -> int:
    missing = [p.name for p in REQUIRED if not p.is_file()]
    if missing:
        print("LOOM_PHASE3_VERIFY: FAIL")
        print("Missing required files:", ", ".join(missing))
        return 2

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    resolver = importlib.import_module("shipclasses_resolver")
    geom = importlib.import_module("shipclasses_geometry_resolver")

    conn = build_db()
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    foreign_key_violations = [list(r) for r in conn.execute("PRAGMA foreign_key_check")]

    unit = run_unit_suite()

    docked = resolver.compute_mass_properties(conn, {"launch_state": "DOCKED"})
    absent = resolver.compute_mass_properties(conn, {"launch_state": "ABSENT"})
    mass_centroids = geom.resolve_mass_centroids_B(conn)
    geometry_poses = geom.resolve_geometry_primitive_poses(conn)

    launch_mass_pose = list(mass_centroids["m_planetary_launch"])
    launch_geometry_pose = list(geometry_poses["g_planetary_launch"][0])
    store_mass = sum(
        float(c["mass_kg"])
        for c in docked["contributions"]
        if str(c["source_id"]).startswith("store_")
    )

    numerics = {
        "docked_wet_mass_kg": float(docked["mass_kg"]),
        "docked_wet_com_B_m": list(docked["center_of_mass_B_m"]),
        "absent_wet_mass_kg": float(absent["mass_kg"]),
        "absent_wet_com_B_m": list(absent["center_of_mass_B_m"]),
        "launch_mass_pose_B_m": launch_mass_pose,
        "launch_geometry_pose_B_m": launch_geometry_pose,
        "store_mass_kg": store_mass,
    }

    errors = {
        "docked_mass_abs_kg": abs(numerics["docked_wet_mass_kg"] - EXPECTED["docked_wet_mass_kg"]),
        "docked_com_max_abs_m": vector_error(numerics["docked_wet_com_B_m"], EXPECTED["docked_wet_com_B_m"]),
        "absent_mass_abs_kg": abs(numerics["absent_wet_mass_kg"] - EXPECTED["absent_wet_mass_kg"]),
        "absent_com_max_abs_m": vector_error(numerics["absent_wet_com_B_m"], EXPECTED["absent_wet_com_B_m"]),
        "launch_mass_pose_max_abs_m": vector_error(launch_mass_pose, EXPECTED["launch_pose_B_m"]),
        "launch_geometry_pose_max_abs_m": vector_error(launch_geometry_pose, EXPECTED["launch_pose_B_m"]),
        "same_authority_pose_max_abs_m": vector_error(launch_mass_pose, launch_geometry_pose),
        "store_mass_abs_kg": abs(store_mass - EXPECTED["store_mass_kg"]),
    }

    checks = {
        "required_files": not missing,
        "sqlite_integrity": integrity == "ok",
        "foreign_keys": len(foreign_key_violations) == 0,
        "unit_suite": bool(unit["passed"]),
        "docked_mass_com": errors["docked_mass_abs_kg"] <= 1e-6 and errors["docked_com_max_abs_m"] <= 1e-12,
        "absent_mass_com": errors["absent_mass_abs_kg"] <= 1e-6 and errors["absent_com_max_abs_m"] <= 1e-12,
        "working_fluid_no_double_count": errors["store_mass_abs_kg"] <= 1e-6,
        "same_authority_geometry_mass": errors["same_authority_pose_max_abs_m"] <= 1e-12,
        "launch_pose_reference": errors["launch_mass_pose_max_abs_m"] <= 1e-12 and errors["launch_geometry_pose_max_abs_m"] <= 1e-12,
    }

    status = "PASS" if all(checks.values()) else "FAIL"
    input_hashes = {p.name: sha256_file(p) for p in REQUIRED}
    db_snapshot_sha256 = snapshot_hash(conn)
    conn.close()

    result = {
        "schema": "loom.phase3_shipclasses_verification.v0.1",
        "status": status,
        "checks": checks,
        "unit_suite": unit,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "offline_required": True,
        },
        "numerics": numerics,
        "errors": errors,
        "sqlite": {
            "integrity_check": integrity,
            "foreign_key_violations": foreign_key_violations,
            "canonical_snapshot_sha256": db_snapshot_sha256,
            "database_sha256": sha256_file(DB_PATH),
        },
        "input_sha256": input_hashes,
    }

    RESULT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("SHA256", RESULT_PATH.name, sha256_file(RESULT_PATH))
    print("SHA256 canonical_db_snapshot", db_snapshot_sha256)
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"LOOM_PHASE3_VERIFY: {status}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
