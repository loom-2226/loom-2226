from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Tuple

from design_ledger import build_wayfarer_phase1_ledger
from wayfarer_s1_solver import solve

VERSION = "LOOM_SHIPYARD_PHASE2_FUNCTIONAL_REGIONS_v0.1"
AUTHORITY = "FUNCTIONAL_REGION_REQUIREMENTS_ONLY"
SPATIAL_STATUS = "OPEN_NO_ADMITTED_SPATIAL_SIZING_RULE"
STATUS = ("ENGINEERING_RESEARCH", "NON_CANON", "NON_PRODUCTION")

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


class Phase2FunctionalRegionError(ValueError):
    pass


@dataclass(frozen=True)
class FunctionalRegionPlacementContract:
    version: str
    region_id: str
    source_id: str
    function_class: str
    anchor_position_m: Tuple[float, float, float]
    spatial_envelope_m: None
    spatial_status: str
    required_functions: Tuple[str, ...]
    load_interfaces: Tuple[str, ...]
    thermal_interfaces: Tuple[str, ...]
    fluid_interfaces: Tuple[str, ...]
    electrical_interfaces: Tuple[str, ...]
    adjacency_requirements: Tuple[str, ...]
    separation_requirements: Tuple[str, ...]
    unresolved_sizing_inputs: Tuple[str, ...]
    provenance_refs: Tuple[str, ...]
    authority_status: str = AUTHORITY
    flight_dynamics_authority: bool = False
    canon_changed: bool = False
    production_shipclasses_changed: bool = False


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(asdict(value), sort_keys=True, separators=(",", ":"), allow_nan=False)


def _spec(source_id: str) -> dict:
    if source_id == "propulsion":
        return dict(function_class="PROPULSION", required_functions=("generate_primary_thrust",), load_interfaces=("primary_thrust_load_path",), thermal_interfaces=("propulsion_waste_heat",), fluid_interfaces=("remass_supply",), electrical_interfaces=("propulsion_power_control",), adjacency_requirements=("structure", "normal_remass_tank_1", "normal_remass_tank_2", "normal_remass_tank_3", "normal_remass_tank_4"), separation_requirements=("habitation_life_support",), unresolved_sizing_inputs=("propulsion_hardware_envelope", "service_clearance", "thermal_rejection_coupling"))
    if source_id.startswith("normal_remass_tank_"):
        return dict(function_class="REMASS_STORAGE", required_functions=("store_normal_remass", "feed_propulsion"), load_interfaces=("tank_support_load_path",), thermal_interfaces=("tank_thermal_control",), fluid_interfaces=("remass_supply", "fill_drain_service"), electrical_interfaces=("tank_instrumentation",), adjacency_requirements=("propulsion", "structure"), separation_requirements=("habitation_life_support",), unresolved_sizing_inputs=("remass_density", "tankage_fraction", "ullage_fraction", "pressure_temperature_state", "tank_geometry_rule"))
    if source_id == "thermal_radiators":
        return dict(function_class="THERMAL_REJECTION", required_functions=("reject_waste_heat",), load_interfaces=("radiator_deployment_support",), thermal_interfaces=("thermal_bus",), fluid_interfaces=("coolant_loop",), electrical_interfaces=("deployment_control", "thermal_instrumentation"), adjacency_requirements=("propulsion", "electrical", "structure"), separation_requirements=("fixed_shield_keepout",), unresolved_sizing_inputs=("waste_heat_load", "radiator_temperature", "emissivity", "view_factor_constraints", "deployment_geometry"))
    if source_id == "habitation_life_support":
        return dict(function_class="HABITATION", required_functions=("crew_habitation", "life_support"), load_interfaces=("pressure_volume_support",), thermal_interfaces=("habitation_heat_rejection",), fluid_interfaces=("water", "atmosphere", "waste"), electrical_interfaces=("habitation_power", "life_support_power"), adjacency_requirements=("protected_water", "structure"), separation_requirements=("propulsion", "normal_remass_tank_1", "normal_remass_tank_2", "normal_remass_tank_3", "normal_remass_tank_4"), unresolved_sizing_inputs=("crew_count_to_volume_rule", "endurance_to_consumables_rule", "pressure_volume_geometry", "service_access"))
    if source_id == "protected_water":
        return dict(function_class="WATER_AND_SHIELDING", required_functions=("store_water", "crew_radiation_shielding_candidate"), load_interfaces=("water_mass_support",), thermal_interfaces=(), fluid_interfaces=("potable_water", "life_support_water"), electrical_interfaces=("tank_instrumentation",), adjacency_requirements=("habitation_life_support", "structure"), separation_requirements=(), unresolved_sizing_inputs=("water_inventory", "shielding_geometry", "tank_geometry_rule"))
    if source_id == "structure":
        return dict(function_class="PRIMARY_STRUCTURE", required_functions=("carry_primary_loads", "support_functional_regions"), load_interfaces=("primary_thrust_load_path", "distributed_component_support"), thermal_interfaces=("structural_thermal_path",), fluid_interfaces=(), electrical_interfaces=("structural_health_monitoring_candidate",), adjacency_requirements=("propulsion", "habitation_life_support", "protected_water", "thermal_radiators"), separation_requirements=(), unresolved_sizing_inputs=("qualified_load_cases", "material_system", "allowables", "buckling_model", "joint_model", "manufacturing_process"))
    raise Phase2FunctionalRegionError(f"unsupported target source {source_id}")


def build_contracts(seed: int = 2226) -> Tuple[FunctionalRegionPlacementContract, ...]:
    candidate = solve(seed).candidate
    points = {p.source_id: p for p in candidate.point_masses}
    contracts = []
    for source_id in TARGET_SOURCES:
        point = points.get(source_id)
        if point is None:
            raise Phase2FunctionalRegionError(f"candidate missing required point mass {source_id}")
        spec = _spec(source_id)
        contract = FunctionalRegionPlacementContract(
            version=VERSION,
            region_id=f"FUNC::{source_id}",
            source_id=source_id,
            function_class=spec["function_class"],
            anchor_position_m=tuple(float(v) for v in point.centroid_m),
            spatial_envelope_m=None,
            spatial_status=SPATIAL_STATUS,
            required_functions=spec["required_functions"],
            load_interfaces=spec["load_interfaces"],
            thermal_interfaces=spec["thermal_interfaces"],
            fluid_interfaces=spec["fluid_interfaces"],
            electrical_interfaces=spec["electrical_interfaces"],
            adjacency_requirements=spec["adjacency_requirements"],
            separation_requirements=spec["separation_requirements"],
            unresolved_sizing_inputs=spec["unresolved_sizing_inputs"],
            provenance_refs=(candidate.candidate_id, source_id, "WAYFARER_S1_POINT_MASS_CENTROID"),
        )
        contracts.append(contract)
    return tuple(contracts)


def validate_contract(contract: FunctionalRegionPlacementContract) -> None:
    if contract.version != VERSION or contract.authority_status != AUTHORITY:
        raise Phase2FunctionalRegionError("authority/version escalation")
    if contract.spatial_envelope_m is not None or contract.spatial_status != SPATIAL_STATUS:
        raise Phase2FunctionalRegionError("Phase 2 may not invent an admitted envelope")
    if len(contract.anchor_position_m) != 3:
        raise Phase2FunctionalRegionError("anchor must be vec3")
    if not contract.required_functions or not contract.unresolved_sizing_inputs:
        raise Phase2FunctionalRegionError("functions and unresolved sizing inputs are required")
    if contract.flight_dynamics_authority or contract.canon_changed or contract.production_shipclasses_changed:
        raise Phase2FunctionalRegionError("authority escalation")


def phase2_open_item(contract: FunctionalRegionPlacementContract) -> str:
    return f"FUNCTIONAL_REGION_ENVELOPE_OPEN::{contract.source_id}::{','.join(contract.unresolved_sizing_inputs)}"


def build_phase2_ledger(path: str | Path, seed: int = 2226) -> dict:
    path = Path(path)
    baseline = build_wayfarer_phase1_ledger(path, seed=seed)
    contracts = build_contracts(seed)
    for row in contracts:
        validate_contract(row)
    con = sqlite3.connect(path)
    try:
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
        """)
        parent = con.execute("SELECT state_id,state_json FROM design_state ORDER BY rowid DESC LIMIT 1").fetchone()
        if parent is None:
            raise Phase2FunctionalRegionError("Phase 1 ledger has no state")
        parent_state_id, parent_json_text = parent
        parent_json = json.loads(parent_json_text)
        old_open = list(parent_json.get("packaging", {}).get("open_items", []))
        targeted = set(TARGET_SOURCES)
        kept = [item for item in old_open if not (item.startswith("NO_ADMITTED_VOLUME::") and item.split("::",1)[1] in targeted)]
        new_open = kept + [phase2_open_item(c) for c in contracts]
        parent_json.setdefault("packaging", {})["open_items"] = new_open
        parent_json["phase2_functional_regions"] = [asdict(c) for c in contracts]
        parent_json["phase2_status"] = list(STATUS)
        parent_json["phase2_authority_status"] = AUTHORITY
        child_state_id = parent_state_id.replace("SYNTH-v0.1", "PHASE2-FUNCTIONAL-REGIONS-v0.1")
        child_text = json.dumps(parent_json, sort_keys=True, separators=(",", ":"), allow_nan=False)
        child_hash = _sha(child_text)
        con.execute("INSERT INTO design_state(state_id,run_id,candidate_id,parent_state_id,state_kind,state_hash,state_json,provenance_json) SELECT ?,run_id,candidate_id,?, ?, ?, ?, ? FROM design_state WHERE state_id=?", (child_state_id,parent_state_id,"PHASE2_FUNCTIONAL_REGION_STATE",child_hash,child_text,json.dumps((VERSION,parent_state_id)),parent_state_id))
        for c in contracts:
            text = canonical_json(c)
            con.execute("INSERT INTO functional_region_contract(region_id,state_id,source_id,function_class,spatial_status,anchor_json,contract_hash,contract_json,authority_status) VALUES(?,?,?,?,?,?,?,?,?)", (c.region_id,child_state_id,c.source_id,c.function_class,c.spatial_status,json.dumps(c.anchor_position_m),_sha(text),text,c.authority_status))
        con.commit()
        return {
            "version": VERSION,
            "parent_state_id": parent_state_id,
            "state_id": child_state_id,
            "state_hash": child_hash,
            "functional_region_count": len(contracts),
            "replaced_no_admitted_volume_count": len(contracts),
            "remaining_open_count": len(new_open),
            "spatial_status": SPATIAL_STATUS,
            "authority_status": AUTHORITY,
            "flight_dynamics_authority": False,
            "canon_changed": False,
            "production_shipclasses_changed": False,
            "phase1": baseline,
        }
    finally:
        con.close()
