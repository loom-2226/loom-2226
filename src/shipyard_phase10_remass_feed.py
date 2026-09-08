#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from pathlib import Path

VERSION = "LOOM_SHIPYARD_PHASE10_REMASS_FEED_DECOMPOSITION_v0.1"
AUTHORITY = "RESEARCH_FEED_DECOMPOSITION_ONLY"
DEFAULT_DB = Path("/storage/emulated/0/Download/LOOM_SHIPYARD/shipyard_design_ledger.sqlite3")
WATER_CANDIDATE_ID = "REMASS_CANDIDATE::LIQUID_WATER_293K"
BUFFER_DURATIONS_S = (0.25, 1.0, 5.0, 10.0)
PROBE_SEMANTICS = "TRANSIENT_BUFFER_SENSITIVITY_ONLY_NOT_BURN_DURATION_OR_ADMITTED_HEADER_SIZE"
SOURCE_ALIGNMENT = "WAYFARER_3D_GEOMETRY_PLAN_PHASE2C_DISTINGUISH_MAJOR_TANKS_FROM_HEADER_RESERVE_CONDITIONING_VOLUMES"

TOPOLOGIES = (
    {
        "topology_id": "REMASS_FEED_TOPOLOGY::BULK_COMMON_HEADER",
        "family": "FOUR_BULK_TANKS_TO_COMMON_HEADER_CONDITIONER_TO_PROPULSION",
        "research_priority": "PRIORITY_NEXT_EXPERIMENT",
        "rationale": "Separates bulk-storage sizing from transient acquisition/conditioning and follows the existing Wayfarer Phase-2C instruction to distinguish major tanks from header/reserve/conditioning volumes.",
        "evidence_refs": (
            SOURCE_ALIGNMENT,
            "NASA_NTRS_20170000667_COMBINATION_PMD_HERITAGE",
            "NASA_NTRS_20100035254_PRESSURE_VS_PUMP_FED_SYSTEM_TRADE",
        ),
        "blockers": (
            "header_architecture_and_count",
            "header_pressure_and_temperature_state",
            "header_fluid_acquisition_method",
            "header_refill_rate_requirement",
            "bulk_to_header_transfer_pressure_drop",
            "propulsion_inlet_pressure_requirement",
            "propulsion_transient_duty_cycle",
            "manifold_valving_and_fault_isolation",
            "header_structural_material_and_allowables",
            "header_spatial_envelope_and_mounting",
        ),
    },
    {
        "topology_id": "REMASS_FEED_TOPOLOGY::LOCAL_COLLECTORS_COMMON_MANIFOLD",
        "family": "FOUR_BULK_TANKS_WITH_LOCAL_COLLECTOR_OR_TRAP_TO_COMMON_MANIFOLD",
        "research_priority": "PRIORITY_NEXT_EXPERIMENT",
        "rationale": "Keeps local liquid acquisition close to each bulk tank while avoiding an assumption that the four tanks share equal instantaneous flow.",
        "evidence_refs": (
            SOURCE_ALIGNMENT,
            "NASA_NTRS_20170000667_PMD_COMBINATIONS_AND_TRAPS",
            "NASA_NTRS_19780059650_PASSIVE_PMD_ACCELERATION_OUTFLOW_HERITAGE",
        ),
        "blockers": (
            "collector_architecture_and_count",
            "collector_capacity_and_refill_dynamics",
            "bulk_tank_pmd_geometry",
            "water_wetting_and_surface_tension_state",
            "propulsion_inlet_pressure_requirement",
            "propulsion_transient_duty_cycle",
            "per_tank_flow_allocation_control_law",
            "crossfeed_and_fault_isolation",
            "collector_structural_material_and_allowables",
            "collector_spatial_envelope_and_mounting",
        ),
    },
    {
        "topology_id": "REMASS_FEED_TOPOLOGY::DIRECT_BULK_FEED",
        "family": "DIRECT_FROM_FOUR_BULK_TANKS_TO_PROPULSION_MANIFOLD",
        "research_priority": "BASELINE_COMPARATOR",
        "rationale": "Retained only as a comparator. It leaves the large bulk tanks responsible for both storage and full propulsion-feed acquisition duty and therefore does not exploit the source-aligned header/reserve/conditioning decomposition.",
        "evidence_refs": (
            "PHASE9_DIRECT_TANK_ARCHITECTURE_FAMILIES",
            "NASA_NTRS_20170000667_PMD_HERITAGE",
        ),
        "blockers": (
            "bulk_tank_pmd_or_positive_expulsion_architecture",
            "propulsion_inlet_pressure_requirement",
            "propulsion_transient_duty_cycle",
            "per_tank_flow_allocation_control_law",
            "bulk_tank_flow_pressure_loss",
            "water_wetting_and_surface_tension_state",
            "bulk_tank_structural_material_and_allowables",
            "single_phase_flow_margin_at_peak_total_demand",
        ),
    },
)


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _tables(con: sqlite3.Connection) -> set[str]:
    return {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def transient_buffer_probe(*, total_flow_kg_s: float, duration_s: float, screening_density_kg_m3: float) -> dict:
    vals = (total_flow_kg_s, duration_s, screening_density_kg_m3)
    if any((not math.isfinite(v) or v <= 0.0) for v in vals):
        raise ValueError("flow, duration and density must be finite and positive")
    mass = total_flow_kg_s * duration_s
    volume = mass / screening_density_kg_m3
    return {
        "total_flow_kg_s": total_flow_kg_s,
        "buffer_duration_s": duration_s,
        "screening_density_kg_m3": screening_density_kg_m3,
        "transient_buffer_mass_kg": mass,
        "ideal_liquid_buffer_volume_m3": volume,
        "probe_semantics": PROBE_SEMANTICS,
        "engineering_input_admitted": False,
        "spatial_envelope_admitted": False,
        "authority_status": AUTHORITY,
    }


def topology_record(defn: dict, *, probe_refs: tuple[str, ...]) -> dict:
    return {
        "topology_id": defn["topology_id"],
        "family": defn["family"],
        "research_priority": defn["research_priority"],
        "rationale": defn["rationale"],
        "evidence_refs": list(defn["evidence_refs"]),
        "probe_refs": list(probe_refs),
        "blockers": list(defn["blockers"]),
        "blocker_count": len(defn["blockers"]),
        "gate_status": "BLOCKED_MISSING_ADMITTED_INTERFACE_AND_COMPONENT_MODELS",
        "selection_status": "NOT_SELECTED",
        "engineering_input_admitted": False,
        "spatial_envelope_admitted": False,
        "authority_status": AUTHORITY,
    }


def apply_phase10(db_path: Path = DEFAULT_DB) -> dict:
    db_path = db_path.expanduser().resolve()
    if not db_path.is_file():
        raise RuntimeError(f"Shipyard editing ledger not found: {db_path}")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        required = {
            "design_state", "shipyard_migration", "remass_feed_demand",
            "remass_architecture_gate", "remass_candidate_model",
        }
        if not required.issubset(_tables(con)):
            raise RuntimeError("Refusing Phase-10 migration: target is not a Phase-9 Shipyard ledger")
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript("""
        CREATE TABLE IF NOT EXISTS remass_feed_buffer_probe(
            probe_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            mode_id TEXT NOT NULL,
            probe_hash TEXT NOT NULL,
            probe_json TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS remass_feed_topology_candidate(
            topology_id TEXT NOT NULL,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            candidate_hash TEXT NOT NULL,
            candidate_json TEXT NOT NULL,
            gate_status TEXT NOT NULL,
            authority_status TEXT NOT NULL,
            PRIMARY KEY(topology_id,state_id)
        );
        """)
        existing = con.execute("SELECT result_json FROM shipyard_migration WHERE migration_id=?", (VERSION,)).fetchone()
        if existing:
            result = json.loads(existing[0]); result["already_applied"] = True; return result

        phase9 = con.execute("SELECT * FROM design_state WHERE state_kind='PHASE9_REMASS_ARCHITECTURE_GATE_STATE' ORDER BY rowid DESC LIMIT 1").fetchone()
        if phase9 is None:
            raise RuntimeError("No Phase-9 remass architecture gate state found")
        water = con.execute("SELECT model_json FROM remass_candidate_model WHERE candidate_id=?", (WATER_CANDIDATE_ID,)).fetchone()
        if water is None:
            raise RuntimeError("Phase-6 water screening candidate not found")
        density = float(json.loads(water[0])["screening_density_kg_m3"])

        demands = con.execute(
            "SELECT demand_id,mode_id,demand_json FROM remass_feed_demand WHERE state_id=? ORDER BY mode_id",
            (phase9["state_id"],),
        ).fetchall()
        if len(demands) != 6:
            raise RuntimeError(f"Expected 6 Phase-9 feed demands, found {len(demands)}")

        probes = []
        probe_ids = []
        for demand_row in demands:
            demand = json.loads(demand_row["demand_json"])
            flow = float(demand["derived_total_remass_flow_kg_s"])
            for duration in BUFFER_DURATIONS_S:
                probe = transient_buffer_probe(total_flow_kg_s=flow, duration_s=duration, screening_density_kg_m3=density)
                probe.update({
                    "mode_id": demand_row["mode_id"],
                    "feed_demand_id": demand_row["demand_id"],
                    "water_candidate_id": WATER_CANDIDATE_ID,
                })
                probe_id = f"BUFFER::{demand_row['mode_id']}::{duration:g}s::{VERSION}"
                probes.append(probe)
                probe_ids.append(probe_id)

        topology_rows = [topology_record(defn, probe_refs=tuple(probe_ids)) for defn in TOPOLOGIES]
        priority_count = sum(row["research_priority"] == "PRIORITY_NEXT_EXPERIMENT" for row in topology_rows)
        phase9_json = json.loads(phase9["state_json"])
        phase10_json = dict(phase9_json)
        phase10_json["phase10_feed_buffer_probes"] = probes
        phase10_json["phase10_feed_topology_candidates"] = topology_rows
        phase10_json["phase10_authority_status"] = AUTHORITY
        phase10_json["phase10_research_priority"] = {
            "priority_topology_count": priority_count,
            "semantics": "RESEARCH_SEQUENCE_ONLY_NOT_PHYSICAL_SELECTION_OR_AUTHORITY",
            "source_alignment": SOURCE_ALIGNMENT,
        }
        phase10_json["phase10_selection_status"] = "NO_FEED_TOPOLOGY_SELECTED"
        phase10_json["phase10_spatial_effect"] = "NONE_DECOMPOSITION_AND_BUFFER_SENSITIVITY_ONLY"
        child_text = _canonical(phase10_json)
        child_hash = _sha(child_text)
        child_state_id = phase9["state_id"].replace("PHASE9-REMASS-ARCHITECTURE-GATE-v0.1", "PHASE10-REMASS-FEED-DECOMPOSITION-v0.1")
        con.execute(
            "INSERT INTO design_state(state_id,run_id,candidate_id,parent_state_id,state_kind,state_hash,state_json,provenance_json) VALUES(?,?,?,?,?,?,?,?)",
            (
                child_state_id, phase9["run_id"], phase9["candidate_id"], phase9["state_id"],
                "PHASE10_REMASS_FEED_DECOMPOSITION_STATE", child_hash, child_text,
                json.dumps([VERSION, phase9["state_id"], SOURCE_ALIGNMENT, "NASA_PMD_AND_FEED_SYSTEM_HERITAGE_RESEARCH"]),
            ),
        )
        for probe_id, probe in zip(probe_ids, probes):
            text = _canonical(probe)
            con.execute(
                "INSERT INTO remass_feed_buffer_probe VALUES(?,?,?,?,?,?)",
                (probe_id, child_state_id, probe["mode_id"], _sha(text), text, AUTHORITY),
            )
        for row in topology_rows:
            text = _canonical(row)
            con.execute(
                "INSERT INTO remass_feed_topology_candidate VALUES(?,?,?,?,?,?)",
                (row["topology_id"], child_state_id, _sha(text), text, row["gate_status"], AUTHORITY),
            )

        peak_probe = max(probes, key=lambda p: p["transient_buffer_mass_kg"])
        result = {
            "migration_id": VERSION,
            "database": str(db_path),
            "parent_state_id": phase9["state_id"],
            "state_id": child_state_id,
            "state_hash": child_hash,
            "buffer_probe_count": len(probes),
            "feed_topology_candidate_count": len(topology_rows),
            "priority_next_experiment_count": priority_count,
            "selected_feed_topology_count": 0,
            "largest_probe_buffer_duration_s": peak_probe["buffer_duration_s"],
            "largest_probe_buffer_mass_kg": peak_probe["transient_buffer_mass_kg"],
            "largest_probe_ideal_volume_m3": peak_probe["ideal_liquid_buffer_volume_m3"],
            "live_engineering_input_admission_count": 0,
            "spatial_effect": "NONE_DECOMPOSITION_AND_BUFFER_SENSITIVITY_ONLY",
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
    print(json.dumps(apply_phase10(), indent=2, sort_keys=True))
