#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from pathlib import Path

VERSION = "LOOM_SHIPYARD_PHASE11_REMASS_FEED_PHYSICS_BOUNDS_v0.1"
AUTHORITY = "ANALYTIC_FEED_BOUND_EVIDENCE_ONLY"
DEFAULT_DB = Path("/storage/emulated/0/Download/LOOM_SHIPYARD/shipyard_design_ledger.sqlite3")
WATER_CANDIDATE_ID = "REMASS_CANDIDATE::LIQUID_WATER_293K"
PRESSURE_RISE_PROBES_PA = (100_000.0, 1_000_000.0, 5_000_000.0, 10_000_000.0)
PRESSURE_PROBE_SEMANTICS = "HYDRAULIC_POWER_SENSITIVITY_ONLY_NOT_PROPULSION_INLET_PRESSURE_OR_PUMP_DESIGN"
INERTIAL_HEAD_SEMANTICS = "MAX_LENGTH_BOUND_RHO_A_L_NOT_ADMITTED_TANK_GEOMETRY_OR_OUTLET_ORIENTATION"


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _tables(con: sqlite3.Connection) -> set[str]:
    return {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def inertial_head_bound(*, density_kg_m3: float, acceleration_m_s2: float, max_length_m: float) -> dict:
    vals = (density_kg_m3, acceleration_m_s2, max_length_m)
    if any((not math.isfinite(v) or v <= 0.0) for v in vals):
        raise ValueError("density, acceleration and length must be finite and positive")
    dp = density_kg_m3 * acceleration_m_s2 * max_length_m
    return {
        "screening_density_kg_m3": density_kg_m3,
        "acceleration_m_s2": acceleration_m_s2,
        "max_length_bound_m": max_length_m,
        "maximum_inertial_pressure_span_pa": dp,
        "derivation": "DELTA_P=RHO*A*L",
        "bound_semantics": INERTIAL_HEAD_SEMANTICS,
        "engineering_input_admitted": False,
        "spatial_envelope_admitted": False,
        "authority_status": AUTHORITY,
    }


def hydraulic_power_probe(*, mass_flow_kg_s: float, density_kg_m3: float, pressure_rise_pa: float) -> dict:
    vals = (mass_flow_kg_s, density_kg_m3, pressure_rise_pa)
    if any((not math.isfinite(v) or v <= 0.0) for v in vals):
        raise ValueError("mass flow, density and pressure rise must be finite and positive")
    q = mass_flow_kg_s / density_kg_m3
    p = q * pressure_rise_pa
    return {
        "mass_flow_kg_s": mass_flow_kg_s,
        "screening_density_kg_m3": density_kg_m3,
        "pressure_rise_probe_pa": pressure_rise_pa,
        "ideal_volumetric_flow_m3_s": q,
        "ideal_hydraulic_power_w": p,
        "efficiency_assumed": None,
        "probe_semantics": PRESSURE_PROBE_SEMANTICS,
        "engineering_input_admitted": False,
        "authority_status": AUTHORITY,
    }


def apply_phase11(db_path: Path = DEFAULT_DB) -> dict:
    db_path = db_path.expanduser().resolve()
    if not db_path.is_file():
        raise RuntimeError(f"Shipyard editing ledger not found: {db_path}")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        required = {
            "design_state", "shipyard_migration", "remass_feed_demand",
            "remass_feed_topology_candidate", "remass_feasibility_bound",
            "remass_candidate_model",
        }
        if not required.issubset(_tables(con)):
            raise RuntimeError("Refusing Phase-11 migration: target is not a Phase-10 Shipyard ledger")
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript("""
        CREATE TABLE IF NOT EXISTS remass_inertial_head_bound(
            bound_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            mode_id TEXT NOT NULL,
            source_id TEXT NOT NULL,
            bound_hash TEXT NOT NULL,
            bound_json TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS remass_hydraulic_power_probe(
            probe_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            mode_id TEXT NOT NULL,
            probe_hash TEXT NOT NULL,
            probe_json TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        """)
        existing = con.execute("SELECT result_json FROM shipyard_migration WHERE migration_id=?", (VERSION,)).fetchone()
        if existing:
            result = json.loads(existing[0]); result["already_applied"] = True; return result

        phase10 = con.execute("SELECT * FROM design_state WHERE state_kind='PHASE10_REMASS_FEED_DECOMPOSITION_STATE' ORDER BY rowid DESC LIMIT 1").fetchone()
        if phase10 is None:
            raise RuntimeError("No Phase-10 remass feed decomposition state found")
        water = con.execute("SELECT model_json FROM remass_candidate_model WHERE candidate_id=?", (WATER_CANDIDATE_ID,)).fetchone()
        if water is None:
            raise RuntimeError("Phase-6 water screening candidate not found")
        density = float(json.loads(water[0])["screening_density_kg_m3"])
        demands = con.execute(
            "SELECT demand_id,mode_id,demand_json FROM remass_feed_demand ORDER BY mode_id"
        ).fetchall()
        if len(demands) != 6:
            raise RuntimeError(f"Expected 6 feed demands, found {len(demands)}")
        bounds = con.execute("SELECT source_id,bound_json FROM remass_feasibility_bound ORDER BY source_id").fetchall()
        if len(bounds) != 4:
            raise RuntimeError(f"Expected 4 remass feasibility bounds, found {len(bounds)}")

        inertial_rows = []
        for demand_row in demands:
            demand = json.loads(demand_row["demand_json"])
            a = float(demand["acceleration_m_s2"])
            for bound_row in bounds:
                bound = json.loads(bound_row["bound_json"])
                r = inertial_head_bound(
                    density_kg_m3=density,
                    acceleration_m_s2=a,
                    max_length_m=float(bound["max_centered_external_length_m"]),
                )
                r.update({
                    "mode_id": demand_row["mode_id"],
                    "feed_demand_id": demand_row["demand_id"],
                    "source_id": bound_row["source_id"],
                    "water_candidate_id": WATER_CANDIDATE_ID,
                })
                inertial_rows.append(r)

        hydraulic_rows = []
        for demand_row in demands:
            demand = json.loads(demand_row["demand_json"])
            mdot = float(demand["derived_total_remass_flow_kg_s"])
            for dp in PRESSURE_RISE_PROBES_PA:
                r = hydraulic_power_probe(mass_flow_kg_s=mdot, density_kg_m3=density, pressure_rise_pa=dp)
                r.update({
                    "mode_id": demand_row["mode_id"],
                    "feed_demand_id": demand_row["demand_id"],
                    "water_candidate_id": WATER_CANDIDATE_ID,
                })
                hydraulic_rows.append(r)

        interpretation = {
            "pressure_fed_vs_pump_fed_evidence": "NASA_NTRS_20100035254_PRESSURE_FED_SIMPLE_LOW_PRESSURE_SMALL_QUANTITY_VS_PUMP_FED_HIGH_PRESSURE_HIGH_PERFORMANCE_TRADE",
            "pmd_acceleration_flow_evidence": "NASA_NTRS_20130000453_LAD_FLOW_RATE_FILL_AND_ACCELERATION_ARE_MAJOR_DRIVERS",
            "research_priority": "PUMP_OR_HEADER_CONDITIONED_FEED_DESERVES_NEXT_MODELING_PRIORITY",
            "priority_semantics": "RESEARCH_SEQUENCE_ONLY_NOT_FEED_ARCHITECTURE_SELECTION",
            "reason": "Wayfarer combines large stored remass inventory with a derived total-flow envelope reaching hundreds of kg/s, while the propulsion inlet pressure and transient duty cycle remain OPEN. The appropriate next step is to model a downstream pump/header interface rather than force the four bulk tanks to become an assumed high-pressure engine-feed system.",
            "selected_topology": None,
            "propulsion_inlet_pressure_admitted": False,
            "pump_efficiency_admitted": False,
            "authority_status": AUTHORITY,
        }

        phase10_json = json.loads(phase10["state_json"])
        phase11_json = dict(phase10_json)
        phase11_json["phase11_inertial_head_bounds"] = inertial_rows
        phase11_json["phase11_hydraulic_power_probes"] = hydraulic_rows
        phase11_json["phase11_interpretation"] = interpretation
        phase11_json["phase11_authority_status"] = AUTHORITY
        phase11_json["phase11_selection_status"] = "NO_FEED_ARCHITECTURE_SELECTED"
        phase11_json["phase11_spatial_effect"] = "NONE_ANALYTIC_FEED_BOUNDS_ONLY"
        child_text = _canonical(phase11_json)
        child_hash = _sha(child_text)
        child_state_id = phase10["state_id"].replace("PHASE10-REMASS-FEED-DECOMPOSITION-v0.1", "PHASE11-REMASS-FEED-PHYSICS-BOUNDS-v0.1")
        con.execute(
            "INSERT INTO design_state(state_id,run_id,candidate_id,parent_state_id,state_kind,state_hash,state_json,provenance_json) VALUES(?,?,?,?,?,?,?,?)",
            (
                child_state_id, phase10["run_id"], phase10["candidate_id"], phase10["state_id"],
                "PHASE11_REMASS_FEED_PHYSICS_BOUNDS_STATE", child_hash, child_text,
                json.dumps([VERSION, phase10["state_id"], WATER_CANDIDATE_ID, "NASA_NTRS_20100035254", "NASA_NTRS_20130000453"]),
            ),
        )
        for idx, row in enumerate(inertial_rows):
            text = _canonical(row)
            con.execute(
                "INSERT INTO remass_inertial_head_bound VALUES(?,?,?,?,?,?,?)",
                (f"HEAD::{idx:03d}::{VERSION}", child_state_id, row["mode_id"], row["source_id"], _sha(text), text, AUTHORITY),
            )
        for idx, row in enumerate(hydraulic_rows):
            text = _canonical(row)
            con.execute(
                "INSERT INTO remass_hydraulic_power_probe VALUES(?,?,?,?,?,?)",
                (f"HYD::{idx:03d}::{VERSION}", child_state_id, row["mode_id"], _sha(text), text, AUTHORITY),
            )

        max_head = max(row["maximum_inertial_pressure_span_pa"] for row in inertial_rows)
        max_power = max(row["ideal_hydraulic_power_w"] for row in hydraulic_rows)
        result = {
            "migration_id": VERSION,
            "database": str(db_path),
            "parent_state_id": phase10["state_id"],
            "state_id": child_state_id,
            "state_hash": child_hash,
            "inertial_head_bound_count": len(inertial_rows),
            "hydraulic_power_probe_count": len(hydraulic_rows),
            "maximum_inertial_pressure_span_pa": max_head,
            "maximum_ideal_hydraulic_power_probe_w": max_power,
            "research_priority": interpretation["research_priority"],
            "selected_feed_architecture_count": 0,
            "live_engineering_input_admission_count": 0,
            "spatial_effect": "NONE_ANALYTIC_FEED_BOUNDS_ONLY",
            "canon_changed": False,
            "production_shipclasses_changed": False,
            "flight_dynamics_authority": False,
            "already_applied": False,
        }
        con.execute(
            "INSERT INTO shipyard_migration(migration_id,source_version,result_json) VALUES(?,?,?)",
            (VERSION, VERSION, json.dumps(result, sort_keys=True)),
        )
        con.commit(); return result
    except Exception:
        con.rollback(); raise
    finally:
        con.close()


if __name__ == "__main__":
    print(json.dumps(apply_phase11(), indent=2, sort_keys=True))
