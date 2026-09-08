from __future__ import annotations

import sqlite3
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


def resolve_wayfarer_mass_com(conn: sqlite3.Connection, launch_state: str = "DOCKED") -> Mapping[str, object]:
    from qualification.phase3.shipclasses_resolver import compute_mass_properties
    return compute_mass_properties(conn, {"launch_state": launch_state})


def resolve_wayfarer_mass_properties_for_6dof(conn: sqlite3.Connection, state: VehicleState) -> MassProperties:
    _ = resolve_wayfarer_mass_com(
        conn,
        state.configuration if state.configuration in {"DOCKED", "EXTRACTING", "ABSENT"} else "DOCKED",
    )
    raise DynamicsError(WAYFARER_INERTIA_OPEN_CODE)
