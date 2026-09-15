from __future__ import annotations

"""Translate qualified RCS flight demand into a hardware-neutral requirement envelope.

This deliberately stops before hardware selection. Sampled numerical trace quantities
remain evidence/bounds; they are not silently promoted into valve, MIB, gimbal,
propellant, plume, structural, or life certification values.
"""

from typing import Any

from src.wayfarer_rcs_actuator_requirement_envelope import build_actuator_requirement_envelope

SCHEMA = "LOOM.Wayfarer.RCSPhysicalRequirementEnvelope"
SCHEMA_VERSION = "0.1"


def build_physical_requirement_envelope() -> dict[str, Any]:
    source = build_actuator_requirement_envelope()
    if source["status"] != "PASS":
        raise RuntimeError("qualified actuator-demand source did not pass")
    demand = dict(source["aggregate_sampled_actuator_demand"])

    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "source": {
            "schema": source["schema"],
            "schema_version": source["schema_version"],
            "interpretation": source["requirement_contract"]["interpretation"],
            "transition_series_identity": source["requirement_contract"]["transition_series_identity"],
        },
        "sampled_demand_basis": demand,
        "requirements": {
            "mount_peak_thrust": "COVER_QUALIFIED_SAMPLED_DEMAND_WITH_ENGINEERING_MARGIN_TO_BE_SELECTED_IN_HARDWARE_TRADE",
            "minimum_impulse_control": "RESOLVE_AT_OR_BELOW_SAMPLED_EXACT_TRACE_UPPER_BOUND_THEN_REQUALIFY_DISCRETIZED_LOOP",
            "response": "MEET_CLOSED_LOOP_DEMAND_WITH_EVIDENCE_BACKED_RESPONSE_MODEL_THEN_REQUALIFY",
            "vectoring": "REALIZE_REQUIRED_MOUNT_FORCE_VECTOR_WITH_EVIDENCE_BACKED_DYNAMIC_RESPONSE_THEN_REQUALIFY",
            "duty_cycle": "DERIVE_FROM_QUALIFIED_MOUNT_COMMAND_HISTORY_AND_MISSION_MANEUVER_SET",
            "total_impulse": "DERIVE_FROM_MISSION_MANEUVER_SET_BEFORE_COMPONENT_LIFE_SELECTION",
            "cycle_life": "DERIVE_FROM_MISSION_DUTY_AND_TOTAL_IMPULSE_PROFILE",
            "plume": "FINITE_PLUME_CLEARANCE_AND_EXTERNAL_HARDWARE_INTERFERENCE_REQUIRED",
            "structure": "MOUNT_LOAD_PATH_AND_LOCAL_STRUCTURE_QUALIFICATION_REQUIRED",
            "thermal_power": "DERIVE_AFTER_WORKING_FLUID_CYCLE_AND_ACTUATOR_ARCHITECTURE_SELECTION",
            "selected_working_fluid": None,
            "selected_exhaust_velocity_m_s": None,
            "selected_vectoring_mechanism": None,
            "selected_valve_response_s": None,
            "selected_cycle_life": None,
        },
        "authority": {
            "claim": "PHYSICAL_REQUIREMENT_ENVELOPE_ONLY",
            "sampled_demand_source_qualified": True,
            "continuous_mission_envelope_certified": False,
            "minimum_impulse_bit_certified": False,
            "valve_dynamics_certified": False,
            "vectoring_mechanism_certified": False,
            "working_fluid_certified": False,
            "final_thruster_hardware_certified": False,
            "plume_interference_certified": False,
            "structural_mount_loads_certified": False,
            "canon_changed": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "remaining_open": [
            "mission_duty_total_impulse_and_cycle_life_derivation",
            "evidence_backed_mib_and_valve_response_selection",
            "propellant_cycle_and_exhaust_velocity_trade",
            "vectoring_mechanism_trade_and_dynamic_response",
            "finite_plume_external_hardware_interference",
            "mount_load_path_and_local_structure",
        ],
        "qualified_next_step": "TRADE_PROPELLANT_ACTUATOR_AND_VECTORING_CANDIDATES_AGAINST_REQUIREMENT_ENVELOPE",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_physical_requirement_envelope(), indent=2, sort_keys=True))
