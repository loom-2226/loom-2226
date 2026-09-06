from __future__ import annotations

import json
import math
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

STATUS_VALUES = {
    "CANON", "DESIGN_BASELINE", "DERIVED", "LEGACY_COMPATIBLE",
    "VISUAL_REFERENCE", "OPEN", "CANON_MASS_DESIGN_POSITION",
}

@dataclass(frozen=True)
class Parameter:
    key: str
    value: Any
    unit: Optional[str]
    status: str
    source: str
    source_version: Optional[str]
    notes: Optional[str]

    def payload(self) -> Dict[str, Any]:
        return {
            "value": self.value, "unit": self.unit, "status": self.status,
            "source": self.source, "source_version": self.source_version,
            "notes": self.notes,
        }

class ParameterStore:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._cache: Dict[str, Parameter] = {}
        rows = conn.execute(
            "SELECT key,value_real,value_text,unit,status,source,source_version,notes FROM geometry_parameters"
        ).fetchall()
        for row in rows:
            value = row[1] if row[1] is not None else row[2]
            p = Parameter(row[0], value, row[3], row[4], row[5], row[6], row[7])
            if p.status not in STATUS_VALUES:
                raise ValueError(f"Unknown provenance status {p.status!r} for {p.key}")
            self._cache[p.key] = p

    def p(self, key: str) -> Parameter:
        try:
            return self._cache[key]
        except KeyError as exc:
            raise KeyError(f"Missing geometry parameter: {key}") from exc

    def n(self, key: str) -> float:
        value = self.p(key).value
        if not isinstance(value, (int, float)):
            raise TypeError(f"Parameter {key} is not numeric: {value!r}")
        return float(value)

    def all_payload(self) -> Dict[str, Dict[str, Any]]:
        return {key: self._cache[key].payload() for key in sorted(self._cache)}

def init_db(db_path: Path, seed_sql_path: Path, reset: bool = False) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if reset and db_path.exists():
        db_path.unlink()
    first_create = not db_path.exists()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    if first_create:
        conn.executescript(seed_sql_path.read_text(encoding="utf-8"))
        conn.commit()
    else:
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "geometry_parameters" not in tables or "mass_elements" not in tables:
            conn.executescript(seed_sql_path.read_text(encoding="utf-8"))
            conn.commit()
    return conn

def _component(cid: str, kind: str, center: Iterable[float], dimensions: Mapping[str, Any],
               status: str, source: str, group: str, **extra: Any) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "id": cid, "kind": kind, "center_m": list(center), "dimensions": dict(dimensions),
        "status": status, "source": source, "group": group,
    }
    payload.update(extra)
    return payload

def build_components(ps: ParameterStore) -> List[Dict[str, Any]]:
    parts: List[Dict[str, Any]] = []
    hull_x0, hull_x1 = ps.n("pressure_hull.x_start_m"), ps.n("pressure_hull.x_end_m")
    parts.append(_component(
        "pressure_hull", "cylinder_x", ((hull_x0+hull_x1)/2, 0, 0),
        {"length_m": hull_x1-hull_x0, "diameter_m": ps.n("pressure_hull.diameter_m")},
        ps.p("pressure_hull.diameter_m").status, "pressure_hull.diameter_m", "habitat"))

    tank_x0, tank_x1 = ps.n("tank.x_start_m"), ps.n("tank.x_end_m")
    tank_r, tank_d = ps.n("tank.center_radius_m"), ps.n("tank.external_diameter_m")
    for idx, angle in enumerate((45.0, 135.0, 225.0, 315.0), 1):
        a = math.radians(angle)
        y, z = tank_r * math.cos(a), tank_r * math.sin(a)
        parts.append(_component(
            f"tank_{idx}", "cylinder_x", ((tank_x0+tank_x1)/2, y, z),
            {"length_m": tank_x1-tank_x0, "diameter_m": tank_d, "azimuth_deg": angle},
            "DESIGN_BASELINE", "tank.*", "tanks", mass_inventory_t=ps.n("tank.normal_inventory_each_t")))

    lx0, lx1, lr = ps.n("longeron.x_start_m"), ps.n("longeron.x_end_m"), ps.n("longeron.center_radius_m")
    for idx, angle in enumerate((0.0, 90.0, 180.0, 270.0), 1):
        a = math.radians(angle)
        y, z = lr * math.cos(a), lr * math.sin(a)
        parts.append(_component(
            f"longeron_{idx}", "box", ((lx0+lx1)/2, y, z),
            {"x_m": lx1-lx0, "y_m": 0.28, "z_m": 0.28, "azimuth_deg": angle},
            "DESIGN_BASELINE", "longeron.*", "structure"))

    parts.append(_component(
        "technical_core", "cylinder_x", (26.0, 0, 0),
        {"length_m": 24.0, "diameter_m": ps.n("technical_core.diameter_m")},
        "DESIGN_BASELINE", "technical_core.diameter_m", "structure"))

    bx0, bx1 = ps.n("launch_bay.x_start_m"), ps.n("launch_bay.x_end_m")
    bw, bd, floor = ps.n("launch_bay.clear_width_m"), ps.n("launch_bay.radial_depth_m"), ps.n("launch_bay.inner_floor_radius_m")
    parts.append(_component(
        "launch_bay", "box", ((bx0+bx1)/2, 0, floor+bd/2),
        {"x_m": bx1-bx0, "y_m": bw, "z_m": bd},
        "DESIGN_BASELINE", "launch_bay.*", "launch_bay"))
    parts.append(_component(
        "planetary_launch", "box", ((bx0+bx1)/2, 0, floor+ps.n("launch.height_m")/2),
        {"x_m": ps.n("launch.length_m"), "y_m": ps.n("launch.width_m"), "z_m": ps.n("launch.height_m")},
        "DESIGN_BASELINE", "launch.*", "launch", state_visibility=["DOCKED", "EXTRACTING"]))

    rx0, rx1, rr = ps.n("radiator.root_x_start_m"), ps.n("radiator.root_x_end_m"), ps.n("ship.main_body_diameter_m")/2
    for idx, angle in enumerate((0.0, 90.0, 180.0, 270.0), 1):
        a = math.radians(angle)
        y, z = rr * math.cos(a), rr * math.sin(a)
        parts.append(_component(
            f"radiator_{idx}", "radiator_placeholder", ((rx0+rx1)/2, y, z),
            {"root_length_m": rx1-rx0, "panel_span_m": 8.0, "panel_chord_m": 5.0, "azimuth_deg": angle},
            "OPEN", "radiator physical panel geometry OPEN", "radiators",
            state_visibility=["STOWED", "DEPLOYED"]))

    sx0, sx1 = ps.n("shield.x_start_m"), ps.n("shield.x_end_m")
    parts.append(_component(
        "propulsion_shadow_shield", "cylinder_x", ((sx0+sx1)/2, 0, 0),
        {"length_m": sx1-sx0, "diameter_m": ps.n("shield.diameter_m")},
        "DESIGN_BASELINE", "shield.*", "propulsion"))

    rx0, rx1 = ps.n("reactor.x_start_m"), ps.n("reactor.x_end_m")
    parts.append(_component(
        "reactor_torch_envelope", "cylinder_x", ((rx0+rx1)/2, 0, 0),
        {"length_m": rx1-rx0, "diameter_m": ps.n("reactor.diameter_m")},
        "DESIGN_BASELINE", "reactor.*", "propulsion"))

    nx0, nx1 = ps.n("nozzle.x_start_m"), ps.n("nozzle.x_end_m")
    parts.append(_component(
        "magnetic_nozzle", "nozzle_x", ((nx0+nx1)/2, 0, 0),
        {"length_m": nx1-nx0, "aperture_diameter_m": ps.n("nozzle.aperture_diameter_m"), "count": 1},
        "DESIGN_BASELINE", "nozzle.*", "propulsion"))

    parts.append(_component(
        "docking_collar", "collar_z", (ps.n("docking.x_center_m"), 0, -ps.n("ship.main_body_diameter_m")/2),
        {"diameter_m": 1.6, "depth_m": 0.7}, "OPEN",
        "docking diameter OPEN; placeholder for interference", "docking"))
    return parts

def compute_mass_state(conn: sqlite3.Connection, ps: ParameterStore, launch_present: bool = True) -> Dict[str, Any]:
    rows = conn.execute("SELECT id,mass_t,x_m,y_m,z_m,status,notes FROM mass_elements").fetchall()
    elems = [dict(r) for r in rows if launch_present or r[0] != "planetary_launch"]
    dry_mass = sum(float(r["mass_t"]) for r in elems)
    moment = [sum(float(r["mass_t"]) * float(r[k]) for r in elems) for k in ("x_m", "y_m", "z_m")]
    dry_com = [m / dry_mass for m in moment]
    normal_fluid, protected = ps.n("mass.normal_remass_t"), ps.n("mass.protected_water_t")
    fluid_elements = [
        {"id": "normal_remass_inventory", "mass_t": normal_fluid, "x_m": 25.0, "y_m": 0.0, "z_m": 0.0, "status": "DESIGN_BASELINE"},
        {"id": "protected_water", "mass_t": protected, "x_m": 12.5, "y_m": 0.0, "z_m": 0.0, "status": "DESIGN_BASELINE"},
    ]
    wet_mass = dry_mass + normal_fluid + protected
    wet_moment = moment[:]
    for f in fluid_elements:
        for i, k in enumerate(("x_m", "y_m", "z_m")):
            wet_moment[i] += f["mass_t"] * f[k]
    return {
        "launch_present": launch_present, "dry_mass_t": dry_mass,
        "dry_com_m": dry_com, "wet_mass_t": wet_mass,
        "wet_com_m": [m / wet_mass for m in wet_moment],
        "elements": elems, "fluid_elements": fluid_elements,
    }

def compute_validation(ps: ParameterStore, mass_docked: Dict[str, Any], mass_absent: Dict[str, Any]) -> Dict[str, Any]:
    length, diameter = ps.n("ship.length_m"), ps.n("ship.main_body_diameter_m")
    radius = diameter / 2
    cylinder_area = math.pi * diameter * length + 2 * math.pi * radius * radius
    projection = max(0.0, ps.n("launch_bay.inner_floor_radius_m") + ps.n("launch_bay.radial_depth_m") - radius)
    blister_delta = 2 * projection * ((ps.n("launch_bay.x_end_m") - ps.n("launch_bay.x_start_m")) + ps.n("launch_bay.clear_width_m"))
    proxy = cylinder_area + blister_delta
    target, tol = ps.n("loom.normal_boundary_target_m2"), ps.n("validation.normal_boundary_tolerance_fraction")
    boundary_pass = abs(proxy - target) <= target * tol
    mass_pass = abs(mass_docked["dry_mass_t"] - ps.n("mass.dry_reference_t")) < 1e-9 and abs(mass_docked["wet_mass_t"] - ps.n("mass.wet_reference_t")) < 1e-9
    return {
        "normal_boundary_proxy_m2": proxy, "normal_boundary_target_m2": target,
        "normal_boundary_delta_m2": proxy-target, "normal_boundary_delta_fraction": (proxy-target)/target,
        "normal_boundary_pass": boundary_pass,
        "extended_boundary_target_m2": ps.n("loom.extended_boundary_target_m2"),
        "effective_patch_target": ps.n("loom.effective_patch_target"),
        "node_count": int(ps.n("relational.node_count")),
        "effective_patches_per_node": ps.n("loom.effective_patch_target") / ps.n("relational.node_count"),
        "boundary_m2_per_node": target / ps.n("relational.node_count"),
        "mass_ledger_pass": mass_pass,
        "docked_dry_com_m": mass_docked["dry_com_m"], "docked_wet_com_m": mass_docked["wet_com_m"],
        "launch_absent_dry_com_m": mass_absent["dry_com_m"], "launch_absent_wet_com_m": mass_absent["wet_com_m"],
        "overall_pass": boundary_pass and mass_pass,
        "notes": [
            "Boundary proxy is a Phase-3 regression surrogate, not a literal Loom domain solution.",
            "Radiator physical panel area is intentionally excluded from the enclosing-domain surrogate.",
            "Launch-absent mass state is design-baseline pending canon mass provenance reconciliation.",
        ],
    }

def compile_geometry(conn: sqlite3.Connection) -> Dict[str, Any]:
    ps = ParameterStore(conn)
    docked, absent = compute_mass_state(conn, ps, True), compute_mass_state(conn, ps, False)
    return {
        "schema": "LOOM.Wayfarer.Geometry", "schema_version": "0.1",
        "coordinate_system": {
            "x": "forward-to-aft; bow datum x=0 m, aftmost permanent structure x=57 m",
            "y": "transverse", "z": "transverse; +Z launch-bay side, -Z docking side",
        },
        "parameters": ps.all_payload(),
        "states": {
            "launch": ["DOCKED", "EXTRACTING", "ABSENT"],
            "radiators": ["STOWED", "DEPLOYING", "DEPLOYED"],
            "docking": ["FREE", "APPROACH", "SOFT_CAPTURE", "HARD_DOCKED"],
            "torch": ["OFF", "SAFE", "ACTIVE"],
        },
        "components": build_components(ps),
        "mass_states": {"DOCKED": docked, "ABSENT": absent},
        "validation": compute_validation(ps, docked, absent),
    }

def write_geometry(conn: sqlite3.Connection, output_path: Path) -> Dict[str, Any]:
    payload = compile_geometry(conn)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload
