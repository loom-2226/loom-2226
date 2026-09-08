#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from pathlib import Path

VERSION = "LOOM_SHIPYARD_PHASE8_WATER_CLOSURE_MAP_v0.1"
AUTHORITY = "ANALYTIC_CLOSURE_BUDGET_ONLY"
DEFAULT_DB = Path("/storage/emulated/0/Download/LOOM_SHIPYARD/shipyard_design_ledger.sqlite3")
WATER_CANDIDATE_ID = "REMASS_CANDIDATE::LIQUID_WATER_293K"
PROBE_ULLAGE = (0.00, 0.02, 0.05, 0.08, 0.10)
PROBE_INTERNAL_DIAMETERS_M = (3.00, 2.95, 2.90, 2.85, 2.80)
PROBE_SEMANTICS = "SENSITIVITY_PROBES_ONLY_NOT_DESIGN_ASSUMPTIONS_OR_ADMITTED_INPUTS"


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _tables(con: sqlite3.Connection) -> set[str]:
    return {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def evaluate_closure(*, mass_kg: float, density_kg_m3: float, max_external_length_m: float,
                     internal_diameter_m: float, ullage_fraction: float) -> dict:
    vals = (mass_kg, density_kg_m3, max_external_length_m, internal_diameter_m)
    if any((not math.isfinite(v) or v <= 0) for v in vals):
        raise ValueError("mass, density, max length and internal diameter must be finite and positive")
    if not math.isfinite(ullage_fraction) or not (0.0 <= ullage_fraction < 1.0):
        raise ValueError("ullage_fraction must be finite and in [0,1)")
    fluid_volume = mass_kg / density_kg_m3
    required_internal_volume = fluid_volume / (1.0 - ullage_fraction)
    area = math.pi * (internal_diameter_m / 2.0) ** 2
    internal_length = required_internal_volume / area
    max_axial_end_allowance = max_external_length_m - internal_length
    return {
        "fluid_volume_m3": fluid_volume,
        "required_internal_volume_m3": required_internal_volume,
        "internal_diameter_m": internal_diameter_m,
        "ullage_fraction": ullage_fraction,
        "required_internal_cylindrical_length_m": internal_length,
        "max_axial_end_allowance_m": max_axial_end_allowance,
        "geometric_budget_status": "FEASIBLE_BY_GEOMETRIC_BUDGET_ONLY" if max_axial_end_allowance >= 0 else "INFEASIBLE_BY_GEOMETRIC_BUDGET",
        "spatial_envelope_admitted": False,
        "engineering_input_admitted": False,
        "authority_status": AUTHORITY,
    }


def summarize_frontier(*, mass_kg: float, density_kg_m3: float, external_diameter_m: float,
                       max_external_length_m: float) -> dict:
    fluid_volume = mass_kg / density_kg_m3
    outer_volume = math.pi * (external_diameter_m / 2.0) ** 2 * max_external_length_m
    max_total_volume_penalty_fraction = 1.0 - fluid_volume / outer_volume
    min_internal_diameter_zero_ullage_zero_ends = math.sqrt(4.0 * fluid_volume / (math.pi * max_external_length_m))
    max_ullage_full_diameter_zero_ends = 1.0 - fluid_volume / outer_volume
    max_radial_allocation_zero_ullage_zero_ends = (external_diameter_m - min_internal_diameter_zero_ullage_zero_ends) / 2.0
    return {
        "mass_kg": mass_kg,
        "screening_density_kg_m3": density_kg_m3,
        "external_diameter_m": external_diameter_m,
        "max_external_length_m": max_external_length_m,
        "ideal_fluid_volume_m3": fluid_volume,
        "ideal_outer_volume_m3": outer_volume,
        "max_total_volume_penalty_fraction": max_total_volume_penalty_fraction,
        "minimum_internal_diameter_m_at_zero_ullage_zero_end_allowance": min_internal_diameter_zero_ullage_zero_ends,
        "maximum_ullage_fraction_at_full_diameter_zero_end_allowance": max_ullage_full_diameter_zero_ends,
        "maximum_uniform_radial_allocation_m_at_zero_ullage_zero_end_allowance": max_radial_allocation_zero_ullage_zero_ends,
        "radial_allocation_semantics": "GEOMETRIC_BUDGET_ONLY_NOT_WALL_THICKNESS_OR_INSULATION_DESIGN",
        "frontier_semantics": "EXACT_GEOMETRIC_CLOSURE_BOUND_USING_PHASE6_WATER_SCREENING_DENSITY_NO_TANK_STRUCTURE_OR_SERVICE_MODEL",
        "spatial_envelope_admitted": False,
        "engineering_input_admitted": False,
        "authority_status": AUTHORITY,
    }


def apply_phase8(db_path: Path = DEFAULT_DB) -> dict:
    db_path = db_path.expanduser().resolve()
    if not db_path.is_file():
        raise RuntimeError(f"Shipyard editing ledger not found: {db_path}")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        required = {"design_state", "shipyard_migration", "remass_feasibility_bound", "remass_candidate_model", "remass_candidate_comparison", "engineering_input"}
        if not required.issubset(_tables(con)):
            raise RuntimeError("Refusing Phase-8 migration: target is not a Phase-6 Shipyard ledger")
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript("""
        CREATE TABLE IF NOT EXISTS remass_water_closure_frontier(
            frontier_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            source_id TEXT NOT NULL,
            frontier_hash TEXT NOT NULL,
            frontier_json TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS remass_water_closure_probe(
            probe_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            source_id TEXT NOT NULL,
            probe_hash TEXT NOT NULL,
            probe_json TEXT NOT NULL,
            geometric_budget_status TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        """)
        existing = con.execute("SELECT result_json FROM shipyard_migration WHERE migration_id=?", (VERSION,)).fetchone()
        if existing:
            result = json.loads(existing[0]); result["already_applied"] = True; return result

        phase6 = con.execute("SELECT * FROM design_state WHERE state_kind='PHASE6_REMASS_CANDIDATE_SCREEN_STATE' ORDER BY rowid DESC LIMIT 1").fetchone()
        if phase6 is None:
            raise RuntimeError("No Phase-6 remass candidate screen state found")
        water = con.execute("SELECT model_json FROM remass_candidate_model WHERE candidate_id=?", (WATER_CANDIDATE_ID,)).fetchone()
        if water is None:
            raise RuntimeError("Phase-6 water screening candidate not found")
        water_model = json.loads(water[0])
        density = float(water_model["screening_density_kg_m3"])
        child_state_id = phase6["state_id"].replace("PHASE6-REMASS-CANDIDATE-SCREEN-v0.1", "PHASE8-WATER-CLOSURE-MAP-v0.1")
        phase6_json = json.loads(phase6["state_json"])

        bounds = con.execute("SELECT source_id,bound_json FROM remass_feasibility_bound ORDER BY source_id").fetchall()
        if len(bounds) != 4:
            raise RuntimeError(f"Expected 4 remass feasibility bounds, found {len(bounds)}")

        frontiers = []
        probes = []
        feasible_probes = 0
        infeasible_probes = 0
        for row in bounds:
            bound = json.loads(row["bound_json"])
            mass_row = con.execute(
                "SELECT value_json FROM engineering_input WHERE source_id=? AND input_name='remass_mass_kg' ORDER BY rowid DESC LIMIT 1",
                (row["source_id"],),
            ).fetchone()
            if mass_row is None:
                raise RuntimeError(f"Missing remass mass for {row['source_id']}")
            mass = float(json.loads(mass_row[0]))
            max_len = float(bound["max_centered_external_length_m"])
            external_diameter = float(bound["external_diameter_m"])
            frontier = summarize_frontier(mass_kg=mass, density_kg_m3=density, external_diameter_m=external_diameter, max_external_length_m=max_len)
            frontier["source_id"] = row["source_id"]
            frontier["candidate_id"] = WATER_CANDIDATE_ID
            frontiers.append(frontier)
            for ullage in PROBE_ULLAGE:
                for internal_diameter in PROBE_INTERNAL_DIAMETERS_M:
                    probe = evaluate_closure(mass_kg=mass, density_kg_m3=density, max_external_length_m=max_len,
                                             internal_diameter_m=internal_diameter, ullage_fraction=ullage)
                    probe.update({"source_id": row["source_id"], "candidate_id": WATER_CANDIDATE_ID, "probe_semantics": PROBE_SEMANTICS})
                    probes.append(probe)
                    if probe["geometric_budget_status"].startswith("FEASIBLE"):
                        feasible_probes += 1
                    else:
                        infeasible_probes += 1

        phase8_json = dict(phase6_json)
        phase8_json["phase8_water_closure_frontiers"] = frontiers
        phase8_json["phase8_water_closure_probes"] = probes
        phase8_json["phase8_authority_status"] = AUTHORITY
        phase8_json["phase8_selection_status"] = "WATER_NOT_SELECTED_SCREENING_SURVIVOR_ONLY"
        phase8_json["phase8_spatial_effect"] = "NONE_CLOSURE_MAP_ONLY_NO_ENVELOPE_ADMITTED"
        child_text = _canonical(phase8_json)
        child_hash = _sha(child_text)
        con.execute(
            "INSERT INTO design_state(state_id,run_id,candidate_id,parent_state_id,state_kind,state_hash,state_json,provenance_json) VALUES(?,?,?,?,?,?,?,?)",
            (child_state_id, phase6["run_id"], phase6["candidate_id"], phase6["state_id"], "PHASE8_WATER_CLOSURE_MAP_STATE", child_hash, child_text,
             json.dumps([VERSION, phase6["state_id"], WATER_CANDIDATE_ID, "ANALYTIC_GEOMETRIC_CLOSURE_FRONTIER"])),
        )
        for frontier in frontiers:
            text = _canonical(frontier)
            con.execute("INSERT INTO remass_water_closure_frontier VALUES(?,?,?,?,?,?)",
                        (f"FRONTIER::{frontier['source_id']}::{VERSION}", child_state_id, frontier["source_id"], _sha(text), text, AUTHORITY))
        for idx, probe in enumerate(probes):
            text = _canonical(probe)
            con.execute("INSERT INTO remass_water_closure_probe VALUES(?,?,?,?,?,?,?)",
                        (f"PROBE::{probe['source_id']}::{idx:03d}::{VERSION}", child_state_id, probe["source_id"], _sha(text), text, probe["geometric_budget_status"], AUTHORITY))

        result = {
            "migration_id": VERSION,
            "database": str(db_path),
            "parent_state_id": phase6["state_id"],
            "state_id": child_state_id,
            "state_hash": child_hash,
            "tank_count": len(frontiers),
            "frontier_count": len(frontiers),
            "probe_count": len(probes),
            "feasible_probe_count": feasible_probes,
            "infeasible_probe_count": infeasible_probes,
            "water_selected": False,
            "live_engineering_input_admission_count": 0,
            "spatial_effect": "NONE_CLOSURE_MAP_ONLY_NO_ENVELOPE_ADMITTED",
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
    print(json.dumps(apply_phase8(), indent=2, sort_keys=True))
