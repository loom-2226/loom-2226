from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path
from typing import Mapping

from portable_dynamics import DynamicsError, MassProperties, VehicleState

WAYFARER_INERTIA_OPEN_CODE = "WAYFARER_INERTIA_OPEN_NOT_QUALIFIED"


def build_wayfarer_connection(repo_root: Path) -> sqlite3.Connection:
    p3 = repo_root / "qualification" / "phase3"
    conn = sqlite3.connect(":memory:")
    conn.executescript((p3 / "LOOM_2226_SHIPCLASSES_PROTOTYPE_SCHEMA_v0.1.sql").read_text(encoding="utf-8"))
    conn.executescript((p3 / "LOOM_2226_SHIPCLASSES_WAYFARER_SEED_v0.1.sql").read_text(encoding="utf-8"))
    conn.executescript((p3 / "LOOM_2226_SHIPCLASSES_WAYFARER_GEOMETRY_COUPLING_v0.1.sql").read_text(encoding="utf-8"))
    return conn


def _load_phase3_resolver(repo_root: Path):
    """Load the Phase-3 resolver by file path so Pixel execution does not depend on package layout."""
    p3 = repo_root / "qualification" / "phase3"
    resolver_path = p3 / "shipclasses_resolver.py"
    spec = importlib.util.spec_from_file_location("loom_phase3_shipclasses_resolver", resolver_path)
    if spec is None or spec.loader is None:
        raise DynamicsError(f"PHASE3_RESOLVER_IMPORT_FAILED:{resolver_path}")

    module = importlib.util.module_from_spec(spec)
    inserted = False
    p3_text = str(p3)
    if p3_text not in sys.path:
        sys.path.insert(0, p3_text)
        inserted = True
    try:
        spec.loader.exec_module(module)
    finally:
        if inserted:
            try:
                sys.path.remove(p3_text)
            except ValueError:
                pass
    return module


def resolve_wayfarer_mass_com(
    conn: sqlite3.Connection,
    launch_state: str = "DOCKED",
    repo_root: Path | None = None,
) -> Mapping[str, object]:
    root = repo_root or Path(__file__).resolve().parents[2]
    resolver = _load_phase3_resolver(root)
    return resolver.compute_mass_properties(conn, {"launch_state": launch_state})


def resolve_wayfarer_mass_properties_for_6dof(
    conn: sqlite3.Connection,
    state: VehicleState,
    repo_root: Path | None = None,
) -> MassProperties:
    _ = resolve_wayfarer_mass_com(
        conn,
        state.configuration if state.configuration in {"DOCKED", "EXTRACTING", "ABSENT"} else "DOCKED",
        repo_root=repo_root,
    )
    raise DynamicsError(WAYFARER_INERTIA_OPEN_CODE)
