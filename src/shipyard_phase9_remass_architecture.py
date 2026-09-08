#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from pathlib import Path

VERSION = "LOOM_SHIPYARD_PHASE9_REMASS_ARCHITECTURE_GATE_v0.1"
AUTHORITY = "RESEARCH_ARCHITECTURE_GATE_ONLY"
DEFAULT_DB = Path("/storage/emulated/0/Download/LOOM_SHIPYARD/shipyard_design_ledger.sqlite3")
STANDARD_GRAVITY_M_S2 = 9.80665
REFERENCE_WET_MASS_KG = 1_158_500.0
REFERENCE_WET_MASS_PROVENANCE = "WAYFARER_CURRENT_CANON_REFERENCE_WET_MASS_1158_5_T"
MODE_CARD_PROVENANCE = "SOURCE_DERIVED_WORKING_ENGINEERING_CARDS_NOT_UNIVERSAL_SPACECRAFT_CONSTANTS"

TORCH_MODE_CARDS = (
    ("ECON", 0.30, 3_000_000.0),
    ("CRUISE", 1.00, 2_000_000.0),
    ("EXPEDITE", 2.00, 1_000_000.0),
    ("FAST", 3.00, 700_000.0),
    ("HARD", 5.00, 450_000.0),
    ("LIMIT", 7.50, 300_000.0),
)

COMMON_BLOCKERS = (
    "fluid_identity_and_thermodynamic_state",
    "maximum_design_pressure_pa",
    "minimum_required_outlet_pressure_pa",
    "tank_temperature_range_k",
    "feed_duty_cycle_and_transient_profile",
    "allowable_unusable_fluid_fraction",
    "structural_material_system_and_allowables",
    "service_life_and_cycle_count",
)

ARCHITECTURES = (
    {
        "architecture_id": "REMASS_ARCH::METALLIC_RIGID_PASSIVE_PMD",
        "family": "RIGID_METALLIC_PRESSURE_VESSEL_WITH_PASSIVE_PMD",
        "heritage_evidence": (
            "NASA_NTRS_19920066456_SPACE_STATION_FREEDOM_WELDED_TITANIUM_PV_WITH_SURFACE_TENSION_PMD",
            "NASA_AIAA_S080A_2018_METALLIC_PRESSURE_VESSEL_BASELINE_REQUIREMENTS",
            "NASA_NTRS_20170000667_PMD_HISTORICAL_REVIEW",
        ),
        "specific_blockers": (
            "pmd_type_and_geometry",
            "water_surface_tension_vs_temperature",
            "water_contact_angle_for_wetted_materials",
            "pmd_bubble_point_margin",
            "acceleration_vector_history_during_feed",
            "required_single_phase_flow_margin",
            "fracture_control_and_inspection_plan",
        ),
    },
    {
        "architecture_id": "REMASS_ARCH::COPV_RIGID_PASSIVE_PMD",
        "family": "COPV_WITH_PASSIVE_PMD",
        "heritage_evidence": (
            "NASA_AIAA_S081B_2018_COPV_BASELINE_REQUIREMENTS",
            "NASA_NTRS_20110008406_COPV_PRIMER",
            "NASA_NTRS_20170000667_PMD_HISTORICAL_REVIEW",
        ),
        "specific_blockers": (
            "liner_material_and_thickness_model",
            "overwrap_material_system",
            "stress_rupture_life_model",
            "damage_control_and_ndi_plan",
            "pmd_type_and_geometry",
            "water_surface_tension_vs_temperature",
            "water_contact_angle_for_wetted_materials",
            "pmd_bubble_point_margin",
        ),
    },
    {
        "architecture_id": "REMASS_ARCH::DIAPHRAGM_OR_BLADDER_POSITIVE_EXPULSION",
        "family": "FLEXIBLE_SEPARATOR_POSITIVE_EXPULSION",
        "heritage_evidence": (
            "NASA_NTRS_19930013770_POSITIVE_EXPULSION_TRADE",
            "NASA_NTRS_19740027944_DIAPHRAGM_PROPULSION_STORAGE_TRADE",
        ),
        "specific_blockers": (
            "separator_material_water_compatibility",
            "separator_fold_and_deployment_geometry",
            "separator_cycle_life",
            "pressurant_architecture",
            "pressurant_inventory_and_regulation",
            "scale_effects_at_wayfarer_tank_size",
            "slosh_and_separator_dynamic_coupling",
        ),
    },
    {
        "architecture_id": "REMASS_ARCH::METALLIC_BELLOWS_POSITIVE_EXPULSION",
        "family": "METALLIC_BELLOWS_POSITIVE_EXPULSION",
        "heritage_evidence": (
            "NASA_NTRS_19930013770_POSITIVE_EXPULSION_TRADE",
            "NASA_NTRS_19710029050_METALLIC_BELLOWS_OPERATING_PARAMETERS",
        ),
        "specific_blockers": (
            "bellows_material_system",
            "bellows_nesting_ratio",
            "bellows_fatigue_and_cycle_life",
            "bellows_buckling_margin",
            "pressurant_architecture",
            "pressurant_inventory_and_regulation",
            "scale_effects_at_wayfarer_tank_size",
        ),
    },
    {
        "architecture_id": "REMASS_ARCH::RIGID_PMD_PUMP_FED",
        "family": "RIGID_TANK_WITH_LIQUID_ACQUISITION_AND_DOWNSTREAM_PUMP",
        "heritage_evidence": (
            "NASA_NTRS_20170000667_PMD_HISTORICAL_REVIEW",
            "NASA_NTRS_20110000503_LIQUID_ACQUISITION_DEVICE_FLOW_LIMITS",
        ),
        "specific_blockers": (
            "pmd_type_and_geometry",
            "pump_head_requirement",
            "pump_inlet_npsh_or_cavitation_margin",
            "water_vapor_pressure_vs_temperature",
            "water_surface_tension_vs_temperature",
            "water_contact_angle_for_wetted_materials",
            "acceleration_vector_history_during_feed",
        ),
    },
)


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _tables(con: sqlite3.Connection) -> set[str]:
    return {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def derive_feed_demand(*, wet_mass_kg: float, acceleration_g: float, exhaust_velocity_m_s: float) -> dict:
    vals = (wet_mass_kg, acceleration_g, exhaust_velocity_m_s)
    if any((not math.isfinite(v) or v <= 0) for v in vals):
        raise ValueError("wet mass, acceleration and exhaust velocity must be finite and positive")
    acceleration_m_s2 = acceleration_g * STANDARD_GRAVITY_M_S2
    thrust_n = wet_mass_kg * acceleration_m_s2
    mass_flow_kg_s = thrust_n / exhaust_velocity_m_s
    return {
        "wet_mass_kg": wet_mass_kg,
        "acceleration_g": acceleration_g,
        "acceleration_m_s2": acceleration_m_s2,
        "exhaust_velocity_m_s": exhaust_velocity_m_s,
        "derived_thrust_n": thrust_n,
        "derived_total_remass_flow_kg_s": mass_flow_kg_s,
        "derivation": "T=M*A; MDOT=T/VE",
        "demand_semantics": "REFERENCE_WET_MASS_UPPER_DEMAND_POINT_FOR_EACH_WORKING_MODE_CARD_NOT_TANK_FEED_SPLIT",
        "engineering_input_admitted": False,
        "authority_status": "DERIVED_INTERFACE_DEMAND_ONLY",
    }


def architecture_record(defn: dict, *, feed_demand_refs: tuple[str, ...]) -> dict:
    blockers = list(COMMON_BLOCKERS) + list(defn["specific_blockers"])
    return {
        "architecture_id": defn["architecture_id"],
        "family": defn["family"],
        "heritage_evidence": list(defn["heritage_evidence"]),
        "feed_demand_refs": list(feed_demand_refs),
        "blockers": blockers,
        "blocker_count": len(blockers),
        "gate_status": "BLOCKED_MISSING_ADMITTED_INTERFACE_REQUIREMENTS",
        "selection_status": "NOT_SELECTED",
        "spatial_envelope_admitted": False,
        "engineering_input_admitted": False,
        "authority_status": AUTHORITY,
    }


def apply_phase9(db_path: Path = DEFAULT_DB) -> dict:
    db_path = db_path.expanduser().resolve()
    if not db_path.is_file():
        raise RuntimeError(f"Shipyard editing ledger not found: {db_path}")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        required = {"design_state", "shipyard_migration", "remass_water_closure_frontier", "engineering_input"}
        if not required.issubset(_tables(con)):
            raise RuntimeError("Refusing Phase-9 migration: target is not a Phase-8 Shipyard ledger")
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript("""
        CREATE TABLE IF NOT EXISTS remass_feed_demand(
            demand_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            mode_id TEXT NOT NULL,
            demand_hash TEXT NOT NULL,
            demand_json TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS remass_architecture_candidate(
            architecture_id TEXT NOT NULL,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            candidate_hash TEXT NOT NULL,
            candidate_json TEXT NOT NULL,
            gate_status TEXT NOT NULL,
            authority_status TEXT NOT NULL,
            PRIMARY KEY(architecture_id,state_id)
        );
        CREATE TABLE IF NOT EXISTS remass_architecture_gate(
            gate_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            gate_hash TEXT NOT NULL,
            gate_json TEXT NOT NULL,
            gate_status TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        """)
        existing = con.execute("SELECT result_json FROM shipyard_migration WHERE migration_id=?", (VERSION,)).fetchone()
        if existing:
            result = json.loads(existing[0]); result["already_applied"] = True; return result

        phase8 = con.execute("SELECT * FROM design_state WHERE state_kind='PHASE8_WATER_CLOSURE_MAP_STATE' ORDER BY rowid DESC LIMIT 1").fetchone()
        if phase8 is None:
            raise RuntimeError("No Phase-8 water closure state found")

        demands = []
        demand_ids = []
        for mode_id, acceleration_g, exhaust_velocity_m_s in TORCH_MODE_CARDS:
            demand = derive_feed_demand(
                wet_mass_kg=REFERENCE_WET_MASS_KG,
                acceleration_g=acceleration_g,
                exhaust_velocity_m_s=exhaust_velocity_m_s,
            )
            demand.update({
                "mode_id": mode_id,
                "wet_mass_provenance": REFERENCE_WET_MASS_PROVENANCE,
                "mode_card_provenance": MODE_CARD_PROVENANCE,
            })
            demands.append(demand)
            demand_ids.append(f"FEED_DEMAND::{mode_id}::{VERSION}")

        architecture_rows = [architecture_record(defn, feed_demand_refs=tuple(demand_ids)) for defn in ARCHITECTURES]
        gate = {
            "gate_id": f"GATE::REMASS_ARCHITECTURE::{VERSION}",
            "gate_status": "BLOCKED_NO_ARCHITECTURE_READY",
            "candidate_count": len(architecture_rows),
            "ready_candidate_count": 0,
            "blocked_candidate_count": len(architecture_rows),
            "selected_candidate_count": 0,
            "common_blockers": list(COMMON_BLOCKERS),
            "decision_semantics": "EXTERNAL_HERITAGE_RAISES_CANDIDATE_PRIORITY_BUT_DOES_NOT_ADMIT_WAYFARER_PRESSURE_TANK_OR_FEED_DESIGN",
            "required_next_authority": "ADMITTED_PROPULSION_TO_TANK_INTERFACE_REQUIREMENTS_AND_TANK_STRUCTURAL_FLUID_MANAGEMENT_MODELS",
            "spatial_envelope_admitted": False,
            "authority_status": AUTHORITY,
        }

        phase8_json = json.loads(phase8["state_json"])
        phase9_json = dict(phase8_json)
        phase9_json["phase9_feed_demands"] = demands
        phase9_json["phase9_architecture_candidates"] = architecture_rows
        phase9_json["phase9_architecture_gate"] = gate
        phase9_json["phase9_authority_status"] = AUTHORITY
        phase9_json["phase9_spatial_effect"] = "NONE_ARCHITECTURE_GATE_ONLY_NO_ENVELOPE_ADMITTED"
        phase9_json["phase9_selection_status"] = "NO_TANK_ARCHITECTURE_SELECTED"
        child_text = _canonical(phase9_json)
        child_hash = _sha(child_text)
        child_state_id = phase8["state_id"].replace("PHASE8-WATER-CLOSURE-MAP-v0.1", "PHASE9-REMASS-ARCHITECTURE-GATE-v0.1")
        con.execute(
            "INSERT INTO design_state(state_id,run_id,candidate_id,parent_state_id,state_kind,state_hash,state_json,provenance_json) VALUES(?,?,?,?,?,?,?,?)",
            (child_state_id, phase8["run_id"], phase8["candidate_id"], phase8["state_id"], "PHASE9_REMASS_ARCHITECTURE_GATE_STATE", child_hash, child_text,
             json.dumps([VERSION, phase8["state_id"], REFERENCE_WET_MASS_PROVENANCE, MODE_CARD_PROVENANCE, "NASA_HERITAGE_RESEARCH_SCREENING"])),
        )

        for demand_id, demand in zip(demand_ids, demands):
            text = _canonical(demand)
            con.execute("INSERT INTO remass_feed_demand VALUES(?,?,?,?,?,?)",
                        (demand_id, child_state_id, demand["mode_id"], _sha(text), text, demand["authority_status"]))
        for row in architecture_rows:
            text = _canonical(row)
            con.execute("INSERT INTO remass_architecture_candidate VALUES(?,?,?,?,?,?)",
                        (row["architecture_id"], child_state_id, _sha(text), text, row["gate_status"], AUTHORITY))
        gate_text = _canonical(gate)
        con.execute("INSERT INTO remass_architecture_gate VALUES(?,?,?,?,?,?)",
                    (gate["gate_id"], child_state_id, _sha(gate_text), gate_text, gate["gate_status"], AUTHORITY))

        result = {
            "migration_id": VERSION,
            "database": str(db_path),
            "parent_state_id": phase8["state_id"],
            "state_id": child_state_id,
            "state_hash": child_hash,
            "feed_demand_count": len(demands),
            "peak_reference_feed_demand_kg_s": max(d["derived_total_remass_flow_kg_s"] for d in demands),
            "architecture_candidate_count": len(architecture_rows),
            "ready_architecture_count": 0,
            "blocked_architecture_count": len(architecture_rows),
            "selected_architecture_count": 0,
            "live_engineering_input_admission_count": 0,
            "spatial_effect": "NONE_ARCHITECTURE_GATE_ONLY_NO_ENVELOPE_ADMITTED",
            "canon_changed": False,
            "production_shipclasses_changed": False,
            "flight_dynamics_authority": False,
            "already_applied": False,
        }
        con.execute("INSERT INTO shipyard_migration(migration_id,source_version,result_json) VALUES(?,?,?)",
                    (VERSION, VERSION, json.dumps(result, sort_keys=True)))
        con.commit(); return result
    except Exception:
        con.rollback(); raise
    finally:
        con.close()


if __name__ == "__main__":
    print(json.dumps(apply_phase9(), indent=2, sort_keys=True))
