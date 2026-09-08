#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

VERSION = "LOOM_SHIPYARD_PHASE2_FUNCTIONAL_REGIONS_v0.1"
AUTHORITY = "FUNCTIONAL_REGION_REQUIREMENTS_ONLY"
SPATIAL_STATUS = "OPEN_NO_ADMITTED_SPATIAL_SIZING_RULE"
DEFAULT_DB = Path("/storage/emulated/0/Download/LOOM_SHIPYARD/shipyard_design_ledger.sqlite3")
TARGET_SOURCES = (
    "propulsion",
    "normal_remass_tank_1",
    "normal_remass_tank_2",
    "normal_remass_tank_3",
    "normal_remass_tank_4",
    "thermal_radiators",
    "habitation_life_support",
    "protected_water",
    "structure",
)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _spec(source_id: str) -> dict:
    if source_id == "propulsion":
        return dict(function_class="PROPULSION", required_functions=["generate_primary_thrust"], load_interfaces=["primary_thrust_load_path"], thermal_interfaces=["propulsion_waste_heat"], fluid_interfaces=["remass_supply"], electrical_interfaces=["propulsion_power_control"], adjacency_requirements=["structure", "normal_remass_tank_1", "normal_remass_tank_2", "normal_remass_tank_3", "normal_remass_tank_4"], separation_requirements=["habitation_life_support"], unresolved_sizing_inputs=["propulsion_hardware_envelope", "service_clearance", "thermal_rejection_coupling"])
    if source_id.startswith("normal_remass_tank_"):
        return dict(function_class="REMASS_STORAGE", required_functions=["store_normal_remass", "feed_propulsion"], load_interfaces=["tank_support_load_path"], thermal_interfaces=["tank_thermal_control"], fluid_interfaces=["remass_supply", "fill_drain_service"], electrical_interfaces=["tank_instrumentation"], adjacency_requirements=["propulsion", "structure"], separation_requirements=["habitation_life_support"], unresolved_sizing_inputs=["remass_density", "tankage_fraction", "ullage_fraction", "pressure_temperature_state", "tank_geometry_rule"])
    if source_id == "thermal_radiators":
        return dict(function_class="THERMAL_REJECTION", required_functions=["reject_waste_heat"], load_interfaces=["radiator_deployment_support"], thermal_interfaces=["thermal_bus"], fluid_interfaces=["coolant_loop"], electrical_interfaces=["deployment_control", "thermal_instrumentation"], adjacency_requirements=["propulsion", "electrical", "structure"], separation_requirements=["fixed_shield_keepout"], unresolved_sizing_inputs=["waste_heat_load", "radiator_temperature", "emissivity", "view_factor_constraints", "deployment_geometry"])
    if source_id == "habitation_life_support":
        return dict(function_class="HABITATION", required_functions=["crew_habitation", "life_support"], load_interfaces=["pressure_volume_support"], thermal_interfaces=["habitation_heat_rejection"], fluid_interfaces=["water", "atmosphere", "waste"], electrical_interfaces=["habitation_power", "life_support_power"], adjacency_requirements=["protected_water", "structure"], separation_requirements=["propulsion", "normal_remass_tank_1", "normal_remass_tank_2", "normal_remass_tank_3", "normal_remass_tank_4"], unresolved_sizing_inputs=["crew_count_to_volume_rule", "endurance_to_consumables_rule", "pressure_volume_geometry", "service_access"])
    if source_id == "protected_water":
        return dict(function_class="WATER_AND_SHIELDING", required_functions=["store_water", "crew_radiation_shielding_candidate"], load_interfaces=["water_mass_support"], thermal_interfaces=[], fluid_interfaces=["potable_water", "life_support_water"], electrical_interfaces=["tank_instrumentation"], adjacency_requirements=["habitation_life_support", "structure"], separation_requirements=[], unresolved_sizing_inputs=["water_inventory", "shielding_geometry", "tank_geometry_rule"])
    if source_id == "structure":
        return dict(function_class="PRIMARY_STRUCTURE", required_functions=["carry_primary_loads", "support_functional_regions"], load_interfaces=["primary_thrust_load_path", "distributed_component_support"], thermal_interfaces=["structural_thermal_path"], fluid_interfaces=[], electrical_interfaces=["structural_health_monitoring_candidate"], adjacency_requirements=["propulsion", "habitation_life_support", "protected_water", "thermal_radiators"], separation_requirements=[], unresolved_sizing_inputs=["qualified_load_cases", "material_system", "allowables", "buckling_model", "joint_model", "manufacturing_process"])
    raise RuntimeError(f"Unsupported Shipyard Phase-2 target: {source_id}")


def _table_names(con: sqlite3.Connection) -> set[str]:
    return {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def _source_positions(parent_json: dict) -> dict[str, list[float]]:
    state = parent_json.get("design_state", {})
    out: dict[str, list[float]] = {}
    for node in state.get("nodes", []):
        if node.get("source_kind") == "POINT_MASS" and node.get("source_id") in TARGET_SOURCES:
            pos = node.get("position_m")
            if isinstance(pos, list) and len(pos) == 3:
                out[node["source_id"]] = [float(x) for x in pos]
    return out


def apply_phase2(db_path: Path = DEFAULT_DB) -> dict:
    db_path = db_path.expanduser().resolve()
    if not db_path.is_file():
        raise RuntimeError(f"Shipyard editing ledger not found: {db_path}")

    con = sqlite3.connect(db_path)
    try:
        required = {"design_run", "design_state", "discipline_result", "dependency_graph", "derived_artifact"}
        if not required.issubset(_table_names(con)):
            raise RuntimeError("Refusing migration: target SQLite is not a LOOM Shipyard design ledger")
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript("""
        CREATE TABLE IF NOT EXISTS functional_region_contract(
            region_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL,
            source_id TEXT NOT NULL,
            function_class TEXT NOT NULL,
            spatial_status TEXT NOT NULL,
            anchor_json TEXT NOT NULL,
            contract_hash TEXT NOT NULL,
            contract_json TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS shipyard_migration(
            migration_id TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            source_version TEXT NOT NULL,
            result_json TEXT NOT NULL
        );
        """)
        existing = con.execute("SELECT result_json FROM shipyard_migration WHERE migration_id=?", (VERSION,)).fetchone()
        if existing:
            result = json.loads(existing[0]); result["already_applied"] = True; return result

        parent = con.execute("SELECT state_id,state_json FROM design_state WHERE state_kind='GOVERNED_SYNTHESIS_STATE' ORDER BY rowid DESC LIMIT 1").fetchone()
        if parent is None:
            raise RuntimeError("No Phase-1 governed synthesis state found in Shipyard editing ledger")
        parent_state_id, parent_text = parent
        parent_json = json.loads(parent_text)
        positions = _source_positions(parent_json)
        missing = [source_id for source_id in TARGET_SOURCES if source_id not in positions]
        if missing:
            raise RuntimeError("Phase-1 state is missing admitted point-mass anchors: " + ", ".join(missing))

        contracts = []
        for source_id in TARGET_SOURCES:
            spec = _spec(source_id)
            contract = {
                "version": VERSION,
                "region_id": f"FUNC::{source_id}",
                "source_id": source_id,
                "function_class": spec["function_class"],
                "anchor_position_m": positions[source_id],
                "spatial_envelope_m": None,
                "spatial_status": SPATIAL_STATUS,
                "required_functions": spec["required_functions"],
                "load_interfaces": spec["load_interfaces"],
                "thermal_interfaces": spec["thermal_interfaces"],
                "fluid_interfaces": spec["fluid_interfaces"],
                "electrical_interfaces": spec["electrical_interfaces"],
                "adjacency_requirements": spec["adjacency_requirements"],
                "separation_requirements": spec["separation_requirements"],
                "unresolved_sizing_inputs": spec["unresolved_sizing_inputs"],
                "provenance_refs": [parent_json["design_state"]["candidate_id"], source_id, "WAYFARER_S1_POINT_MASS_CENTROID"],
                "authority_status": AUTHORITY,
                "flight_dynamics_authority": False,
                "canon_changed": False,
                "production_shipclasses_changed": False,
            }
            contracts.append(contract)

        old_open = list(parent_json.get("packaging", {}).get("open_items", []))
        targeted = set(TARGET_SOURCES)
        kept = [item for item in old_open if not (item.startswith("NO_ADMITTED_VOLUME::") and item.split("::", 1)[1] in targeted)]
        new_open = kept + [f"FUNCTIONAL_REGION_ENVELOPE_OPEN::{c['source_id']}::{','.join(c['unresolved_sizing_inputs'])}" for c in contracts]
        parent_json.setdefault("packaging", {})["open_items"] = new_open
        parent_json["phase2_functional_regions"] = contracts
        parent_json["phase2_status"] = ["ENGINEERING_RESEARCH", "NON_CANON", "NON_PRODUCTION"]
        parent_json["phase2_authority_status"] = AUTHORITY
        child_state_id = parent_state_id.replace("SYNTH-v0.1", "PHASE2-FUNCTIONAL-REGIONS-v0.1")
        child_text = json.dumps(parent_json, sort_keys=True, separators=(",", ":"), allow_nan=False)
        child_hash = _sha(child_text)
        con.execute("INSERT OR IGNORE INTO design_state(state_id,run_id,candidate_id,parent_state_id,state_kind,state_hash,state_json,provenance_json) SELECT ?,run_id,candidate_id,?,'PHASE2_FUNCTIONAL_REGION_STATE',?,?,? FROM design_state WHERE state_id=?", (child_state_id, parent_state_id, child_hash, child_text, json.dumps([VERSION, parent_state_id]), parent_state_id))
        for contract in contracts:
            text = json.dumps(contract, sort_keys=True, separators=(",", ":"), allow_nan=False)
            con.execute("INSERT OR REPLACE INTO functional_region_contract(region_id,state_id,source_id,function_class,spatial_status,anchor_json,contract_hash,contract_json,authority_status) VALUES(?,?,?,?,?,?,?,?,?)", (contract["region_id"], child_state_id, contract["source_id"], contract["function_class"], SPATIAL_STATUS, json.dumps(contract["anchor_position_m"]), _sha(text), text, AUTHORITY))
        result = {"migration_id": VERSION, "database": str(db_path), "parent_state_id": parent_state_id, "state_id": child_state_id, "state_hash": child_hash, "functional_region_count": len(contracts), "remaining_open_count": len(new_open), "authority_status": AUTHORITY, "canon_changed": False, "production_shipclasses_changed": False, "flight_dynamics_authority": False, "already_applied": False}
        con.execute("INSERT INTO shipyard_migration(migration_id,source_version,result_json) VALUES(?,?,?)", (VERSION, VERSION, json.dumps(result, sort_keys=True)))
        con.commit()
        return result
    except Exception:
        con.rollback(); raise
    finally:
        con.close()


if __name__ == "__main__":
    print(json.dumps(apply_phase2(), indent=2, sort_keys=True))
