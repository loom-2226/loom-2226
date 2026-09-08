#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from pathlib import Path

VERSION = "LOOM_SHIPYARD_PHASE5_REMASS_INPUT_AUDIT_v0.1"
AUTHORITY = "FEASIBILITY_BOUND_EVIDENCE_ONLY"
DEFAULT_DB = Path("/storage/emulated/0/Download/LOOM_SHIPYARD/shipyard_design_ledger.sqlite3")
REMASS_SOURCES = tuple(f"normal_remass_tank_{i}" for i in range(1, 5))
TANK_X_REGION_M = (18.0, 32.0)
TANK_CENTER_RADIUS_M = 2.7
TECHNICAL_CORE_DIAMETER_M = 1.4
COMPLETE_REQUIRED_INPUTS = (
    "remass_density_kg_m3",
    "ullage_fraction",
    "pressure_temperature_state",
    "tankage_fraction_semantics",
    "internal_diameter_m",
    "axial_end_allowance_m",
    "tank_geometry_rule",
)
INPUT_CLASSIFICATION = {
    "remass_density_kg_m3": "OPEN_REMASS_MATERIAL_AND_STATE_NOT_SPECIFIED",
    "ullage_fraction": "OPEN_ENGINEERING_POLICY_NOT_SPECIFIED",
    "pressure_temperature_state": "OPEN_REMASS_MATERIAL_AND_STATE_NOT_SPECIFIED",
    "tankage_fraction_semantics": "OPEN_TERM_SEMANTICS_NOT_DEFINED",
    "internal_diameter_m": "OPEN_REQUIRES_WALL_STRUCTURE_AND_INSULATION_MODEL",
    "axial_end_allowance_m": "OPEN_REQUIRES_END_GEOMETRY_AND_SERVICE_MODEL",
    "tank_geometry_rule": "MODEL_RULE_AVAILABLE_NOT_PHYSICALLY_ADMITTED",
}


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _tables(con: sqlite3.Connection) -> set[str]:
    return {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def _input(con: sqlite3.Connection, state_id: str, source_id: str, name: str):
    row = con.execute(
        "SELECT value_json FROM engineering_input WHERE state_id=? AND source_id=? AND input_name=?",
        (state_id, source_id, name),
    ).fetchone()
    if row is None:
        raise RuntimeError(f"Missing Phase-4 support input {source_id}::{name}")
    return json.loads(row[0])


def _bounds(mass_kg: float, external_diameter_m: float, anchor: list[float]) -> dict:
    x = float(anchor[0])
    x0, x1 = TANK_X_REGION_M
    if not x0 <= x <= x1:
        raise RuntimeError("tank anchor outside admitted tank x region")
    max_length = 2.0 * min(x - x0, x1 - x)
    if max_length <= 0:
        raise RuntimeError("tank anchor leaves no positive centered axial envelope")
    radius = external_diameter_m * 0.5
    max_outer_volume = math.pi * radius * radius * max_length
    minimum_bulk_density = mass_kg / max_outer_volume
    core_clearance = TANK_CENTER_RADIUS_M - radius - TECHNICAL_CORE_DIAMETER_M * 0.5
    adjacent_center_distance = TANK_CENTER_RADIUS_M * math.sqrt(2.0)
    adjacent_clearance = adjacent_center_distance - external_diameter_m
    return {
        "anchor_x_m": x,
        "tank_region_x_m": [x0, x1],
        "external_diameter_m": external_diameter_m,
        "max_centered_external_length_m": max_length,
        "max_idealized_outer_cylinder_volume_m3": max_outer_volume,
        "minimum_equivalent_bulk_density_kg_m3": minimum_bulk_density,
        "minimum_density_bound_semantics": "STRICT_LOWER_BOUND_FROM_OUTER_ENVELOPE_ONLY_ACTUAL_FLUID_DENSITY_MUST_BE_HIGHER_IF_WALLS_ULLAGE_ENDS_REDUCE_VOLUME",
        "technical_core_radial_clearance_m": core_clearance,
        "adjacent_tank_surface_clearance_m": adjacent_clearance,
        "spatial_envelope_admitted": False,
        "authority_status": AUTHORITY,
    }


def apply_phase5(db_path: Path = DEFAULT_DB) -> dict:
    db_path = db_path.expanduser().resolve()
    if not db_path.is_file():
        raise RuntimeError(f"Shipyard editing ledger not found: {db_path}")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        required = {"design_state", "engineering_input", "discipline_execution_attempt", "shipyard_migration"}
        if not required.issubset(_tables(con)):
            raise RuntimeError("Refusing Phase-5 migration: target is not a Phase-4 Shipyard ledger")
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript("""
        CREATE TABLE IF NOT EXISTS remass_input_audit(
            audit_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            source_id TEXT NOT NULL,
            audit_hash TEXT NOT NULL,
            audit_json TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS remass_feasibility_bound(
            bound_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            source_id TEXT NOT NULL,
            bound_hash TEXT NOT NULL,
            bound_json TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS discipline_contract_revision(
            revision_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            source_id TEXT NOT NULL,
            required_inputs_json TEXT NOT NULL,
            open_inputs_json TEXT NOT NULL,
            execution_status TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        """)
        existing = con.execute("SELECT result_json FROM shipyard_migration WHERE migration_id=?", (VERSION,)).fetchone()
        if existing:
            result = json.loads(existing[0]); result["already_applied"] = True; return result

        phase4 = con.execute("SELECT * FROM design_state WHERE state_kind='PHASE4_REMASS_SIZING_STATE' ORDER BY rowid DESC LIMIT 1").fetchone()
        if phase4 is None:
            raise RuntimeError("No Phase-4 remass sizing state found")
        child_state_id = phase4["state_id"].replace("PHASE4-REMASS-SIZING-v0.1", "PHASE5-REMASS-INPUT-AUDIT-v0.1")
        phase4_json = json.loads(phase4["state_json"])
        audits, bounds = [], []
        for source_id in REMASS_SOURCES:
            mass = float(_input(con, phase4["state_id"], source_id, "remass_mass_kg"))
            diameter = float(_input(con, phase4["state_id"], source_id, "external_diameter_m"))
            anchor = [float(v) for v in _input(con, phase4["state_id"], source_id, "anchor_position_m")]
            bound = _bounds(mass, diameter, anchor)
            audit = {
                "source_id": source_id,
                "complete_required_inputs": list(COMPLETE_REQUIRED_INPUTS),
                "input_classification": INPUT_CLASSIFICATION,
                "repository_authority_findings": {
                    "remass_mass_kg": "ADMITTED_62500_KG_PER_TANK",
                    "external_diameter_m": "ADMITTED_NOMINAL_3_0_M_DESIGN_BASELINE",
                    "anchor_position_m": "ADMITTED_FROM_S1_GENERATED_LAYOUT",
                    "tank_region_x_m": "ADMITTED_DESIGN_BASELINE_18_TO_32_M",
                    "remass_composition": "OPEN_CURRENT_AUTHORITY_DOES_NOT_SPECIFY_EXACT_WAYFARER_NORMAL_REMASS_COMPOSITION",
                    "water_relationship": "CURRENT_AUTHORITY_SAYS_250_T_NORMAL_REMASS_IS_WITHIN_300_T_WORKING_FLUID_WATER_INVENTORY_BUT_DOES_NOT_DEFINE_IDENTICAL_MATERIAL_STATE",
                },
                "can_execute_live_sizing": False,
                "spatial_envelope_admitted": False,
                "authority_status": AUTHORITY,
            }
            audits.append(audit); bounds.append({"source_id": source_id, **bound})

        phase5_json = dict(phase4_json)
        phase5_json["phase5_remass_input_audits"] = audits
        phase5_json["phase5_remass_feasibility_bounds"] = bounds
        phase5_json["phase5_authority_status"] = AUTHORITY
        phase5_json["phase5_spatial_effect"] = "NONE_FEASIBILITY_BOUNDS_ONLY"
        child_text = _canonical(phase5_json)
        child_hash = _sha(child_text)
        con.execute(
            "INSERT INTO design_state(state_id,run_id,candidate_id,parent_state_id,state_kind,state_hash,state_json,provenance_json) VALUES(?,?,?,?,?,?,?,?)",
            (child_state_id, phase4["run_id"], phase4["candidate_id"], phase4["state_id"], "PHASE5_REMASS_INPUT_AUDIT_STATE", child_hash, child_text, json.dumps([VERSION, phase4["state_id"], "geometry/wayfarer_geometry_seed.sql", "engineering/current/LOOM_2226_Wayfarer_3D_Geometry_and_Physical_Packaging_Plan_v0.1.md"])),
        )
        for audit, bound in zip(audits, bounds):
            at = _canonical(audit); bt = _canonical(bound); source_id = audit["source_id"]
            con.execute("INSERT INTO remass_input_audit VALUES(?,?,?,?,?,?)", (f"AUDIT::{source_id}::{VERSION}", child_state_id, source_id, _sha(at), at, AUTHORITY))
            con.execute("INSERT INTO remass_feasibility_bound VALUES(?,?,?,?,?,?)", (f"BOUND::{source_id}::{VERSION}", child_state_id, source_id, _sha(bt), bt, AUTHORITY))
            con.execute("INSERT INTO discipline_contract_revision VALUES(?,?,?,?,?,?,?)", (f"REV::{source_id}::{VERSION}", child_state_id, source_id, json.dumps(COMPLETE_REQUIRED_INPUTS), json.dumps(COMPLETE_REQUIRED_INPUTS), "BLOCKED_MISSING_ADMITTED_INPUTS", "DISCIPLINE_CONTRACT_REVISION_ONLY"))

        result = {
            "migration_id": VERSION,
            "database": str(db_path),
            "parent_state_id": phase4["state_id"],
            "state_id": child_state_id,
            "state_hash": child_hash,
            "audited_tank_count": len(audits),
            "feasibility_bound_count": len(bounds),
            "corrected_required_input_count_per_tank": len(COMPLETE_REQUIRED_INPUTS),
            "live_sizing_ready_count": 0,
            "spatial_effect": "NONE_FEASIBILITY_BOUNDS_ONLY",
            "canon_changed": False,
            "production_shipclasses_changed": False,
            "flight_dynamics_authority": False,
            "already_applied": False,
        }
        con.execute("INSERT INTO shipyard_migration(migration_id,source_version,result_json) VALUES(?,?,?)", (VERSION, VERSION, json.dumps(result, sort_keys=True)))
        con.commit(); return result
    except Exception:
        con.rollback(); raise
    finally:
        con.close()


if __name__ == "__main__":
    print(json.dumps(apply_phase5(), indent=2, sort_keys=True))
