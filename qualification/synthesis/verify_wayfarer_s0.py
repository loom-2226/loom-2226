from __future__ import annotations

import hashlib
import json
import math
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHASE3 = ROOT / "qualification" / "phase3"
PHASE4 = ROOT / "qualification" / "phase4"
MANIFEST_PATH = HERE / "WAYFARER_S0_AUTHORITY_MANIFEST_v0.1.json"

if str(PHASE3) not in sys.path:
    sys.path.insert(0, str(PHASE3))

from shipclasses_resolver import compute_mass_properties  # noqa: E402

SCHEMA = PHASE3 / "LOOM_2226_SHIPCLASSES_PROTOTYPE_SCHEMA_v0.1.sql"
SEED = PHASE3 / "LOOM_2226_SHIPCLASSES_WAYFARER_SEED_v0.1.sql"
COUPLING = PHASE3 / "LOOM_2226_SHIPCLASSES_WAYFARER_GEOMETRY_COUPLING_v0.1.sql"
PHASE4_GEOMETRY = PHASE4 / "LOOM_2226_SHIPCLASSES_WAYFARER_PHASE4_GEOMETRY_v0.1.sql"


class S0VerificationError(RuntimeError):
    pass


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _load_manifest() -> Dict[str, Any]:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if data.get("schema") != "LOOM_2226_WAYFARER_S0_AUTHORITY_MANIFEST":
        raise S0VerificationError("Unexpected S0 manifest schema")
    if data.get("flight_dynamics_authority") is not False:
        raise S0VerificationError("S0 must not claim flight dynamics authority")
    return data


def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    for path in (SCHEMA, SEED, COUPLING, PHASE4_GEOMETRY):
        conn.executescript(path.read_text(encoding="utf-8"))
    return conn


def _assert_close(actual: float, expected: float, tol: float, label: str) -> None:
    if not math.isfinite(actual) or abs(actual - expected) > tol:
        raise S0VerificationError(f"{label}: expected {expected!r}, got {actual!r}")


def _assert_vec(actual: Iterable[float], expected: Iterable[float], tol: float, label: str) -> None:
    a = list(actual)
    e = list(expected)
    if len(a) != len(e):
        raise S0VerificationError(f"{label}: vector length mismatch")
    for i, (x, y) in enumerate(zip(a, e)):
        _assert_close(float(x), float(y), tol, f"{label}[{i}]")


def _verify_source_hashes(manifest: Dict[str, Any]) -> None:
    for source in manifest["sources"]:
        path = ROOT / source["path"]
        if not path.is_file():
            raise S0VerificationError(f"Missing frozen source: {source['path']}")
        actual = _git_blob_sha(path)
        expected = source["git_blob_sha"]
        if actual != expected:
            raise S0VerificationError(
                f"Frozen source hash mismatch for {source['path']}: expected {expected}, got {actual}"
            )
        if source.get("mutable") is not False:
            raise S0VerificationError(f"Frozen source not marked immutable: {source['path']}")


def _dry_mass(conn: sqlite3.Connection, launch_state: str) -> float:
    launch_active = launch_state != "ABSENT"
    return sum(
        float(row[0])
        for row in conn.execute(
            "SELECT reference_mass_kg FROM mass_element "
            "WHERE component_id <> 'planetary_launch' OR ?",
            (1 if launch_active else 0,),
        )
    )


def _verify_reference_states(manifest: Dict[str, Any], conn: sqlite3.Connection) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    for state in ("DOCKED", "ABSENT"):
        expected = manifest["reference_states"][state]
        resolved = compute_mass_properties(conn, {"launch_state": state})
        _assert_close(float(resolved["mass_kg"]), float(expected["wet_mass_kg"]), 1e-6, f"{state} wet mass")
        _assert_vec(resolved["center_of_mass_B_m"], expected["wet_com_B_m"], 1e-12, f"{state} wet CoM")
        dry = _dry_mass(conn, state)
        _assert_close(dry, float(expected["dry_mass_kg"]), 1e-6, f"{state} dry mass")
        results[state] = {
            "dry_mass_kg": dry,
            "wet_mass_kg": float(resolved["mass_kg"]),
            "wet_com_B_m": list(resolved["center_of_mass_B_m"]),
        }
    return results


def _verify_mass_accounting(manifest: Dict[str, Any], conn: sqlite3.Connection) -> None:
    ledger_total = sum(float(v) for v in manifest["mass_ledger"].values())
    _assert_close(ledger_total, 1158500.0, 1e-6, "manifest DOCKED wet ledger")

    result = compute_mass_properties(conn, {"launch_state": "DOCKED"})
    store_mass = sum(
        float(c["mass_kg"])
        for c in result["contributions"]
        if str(c["source_id"]).startswith("store_")
    )
    _assert_close(store_mass, 300000.0, 1e-6, "working-fluid/water inventory")
    _assert_close(
        float(manifest["stores"]["normal_remass"]["mass_kg"]),
        250000.0,
        1e-6,
        "normal remass inventory",
    )
    _assert_close(
        float(manifest["stores"]["protected_water"]["mass_kg"]),
        50000.0,
        1e-6,
        "protected water inventory",
    )


def _verify_open_firewall(manifest: Dict[str, Any], conn: sqlite3.Connection) -> None:
    fields = {row["field"]: row for row in manifest["field_inventory"]}
    for key in ("radiator.panel_geometry", "docking.geometry", "full_wayfarer_centroidal_inertia"):
        row = fields.get(key)
        if row is None or row.get("classification") != "OPEN" or row.get("value") is not None:
            raise S0VerificationError(f"OPEN firewall not explicit for {key}")

    open_geometry = dict(
        conn.execute(
            "SELECT primitive_id, authority_status FROM geometry_primitive "
            "WHERE primitive_id LIKE 'p_radiator_root_%' OR primitive_id='p_docking_marker'"
        ).fetchall()
    )
    expected_ids = {f"p_radiator_root_{i}" for i in range(1, 5)} | {"p_docking_marker"}
    if set(open_geometry) != expected_ids:
        raise S0VerificationError("Expected OPEN radiator/docking markers are incomplete")
    bad = {pid: status for pid, status in open_geometry.items() if status != "OPEN"}
    if bad:
        raise S0VerificationError(f"OPEN geometry was promoted: {bad}")

    if manifest["inertia_firewall"].get("mode") != "A":
        raise S0VerificationError("S0/S1 must begin in Mode A")
    if manifest["inertia_firewall"].get("candidate_full_flight_inertia_authority") is not False:
        raise S0VerificationError("Mode A cannot claim full flight inertia authority")


def verify() -> Dict[str, Any]:
    manifest = _load_manifest()
    _verify_source_hashes(manifest)
    conn = _db()
    try:
        states = _verify_reference_states(manifest, conn)
        _verify_mass_accounting(manifest, conn)
        _verify_open_firewall(manifest, conn)
    finally:
        conn.close()

    return {
        "S0_AUTHORITY_EXTRACTION": "PASS",
        "source_head": manifest["source_head"],
        "reference_states": states,
        "working_fluid_water_total_kg": manifest["stores"]["working_fluid_water_total_kg"],
        "flight_dynamics_authority": False,
        "canon_changed": False,
        "production_shipclasses_changed": False,
    }


def main() -> int:
    try:
        result = verify()
    except Exception as exc:
        print("S0_AUTHORITY_EXTRACTION = FAIL")
        print(f"{type(exc).__name__}: {exc}")
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
