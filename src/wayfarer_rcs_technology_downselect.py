from __future__ import annotations

"""Governed 2226 RCS technology-family downselect.

This is an architecture extrapolation, not a claim that 2026 hardware already meets
Wayfarer requirements. It selects separations of function that are supported by the
qualified vehicle demand and by demonstrated mechanism families, while refusing to
invent component performance values.
"""

from typing import Any

from src.wayfarer_rcs_physical_architecture_trade import build_physical_architecture_trade

SCHEMA = "LOOM.Wayfarer.RCSTechnologyDownselect"
SCHEMA_VERSION = "0.1"


def build_technology_downselect() -> dict[str, Any]:
    trade = build_physical_architecture_trade()
    if trade["status"] != "PASS":
        raise RuntimeError("physical architecture trade did not pass")

    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "epistemic_class": "GOVERNED_FUTURE_TECHNOLOGY_EXTRAPOLATION",
        "source_trade_claim": trade["authority"]["claim"],
        "selection": {
            "mount_architecture": "COMPOUND_COARSE_FINE_VECTORED_MOUNT",
            "coarse_actuation": "ELECTRONICALLY_METERED_THROTTLEABLE_LIQUID_THRUSTER_FAMILY",
            "fine_actuation": "DEDICATED_FAST_PULSED_FINE_AUTHORITY_ELEMENT",
            "vectoring_architecture": "INTERNAL_FLOW_VECTORING_PREFERRED_MECHANICAL_GIMBAL_RESERVE",
            "working_fluid": None,
            "exhaust_velocity_m_s": None,
            "minimum_impulse_bit_Ns": None,
            "valve_response_s": None,
            "cycle_life": None,
        },
        "design_decisions": {
            "coarse_control": "ELECTRONIC_FLOW_CONTROL_AND_VARIABLE_INJECTION_GEOMETRY_ARE_ACCEPTABLE_ANCESTOR_MECHANISMS_FOR_2226_EXTRAPOLATION",
            "fine_control": "SEPARATE_FINE_ELEMENT_UNTIL_EVIDENCE_PROVES_COARSE_ELEMENT_CAN_MEET_MIB_AND_RESPONSE_REQUIREMENT",
            "vectoring": "PREFER_INTERNAL_FLOW_OR_DIFFERENTIAL_NOZZLE_VECTOR_SYNTHESIS_TO_AVOID_DEFAULTING_TO_WHOLE_ENGINE_GIMBAL",
            "gimbal": "RETAIN_AS_RESERVE_IF_INSTALLATION_OR_DYNAMIC_EVIDENCE_DEFEATS_INTERNAL_FLOW_VECTORING",
            "propellant": "DEFER_UNTIL_MISSION_TOTAL_IMPULSE_THERMAL_PLUME_AND_STORABILITY_TRADE_IS_BOUND",
        },
        "evidence_logic": {
            "electronically_controlled_throttling_demonstrated": True,
            "fast_valve_mib_improvement_demonstrated": True,
            "mib_depends_on_valve_feed_thruster_and_control_response": True,
            "internal_fluidic_vectoring_family_supported": True,
            "wayfarer_specific_numeric_performance_demonstrated": False,
            "inference": "SEPARATION_OF_COARSE_FINE_AND_VECTORING_FUNCTIONS_IS_JUSTIFIED; NUMERIC_2226_COMPONENT_CAPABILITY_IS_NOT",
        },
        "installation_inputs": {
            "mount_count": 16,
            "candidate_vector_cone": "RECOVERED_GEOMETRIC_45_DEGREE_CONE_NOT_PHYSICALLY_CERTIFIED",
            "finite_plume_model_required": True,
            "radiator_and_external_hardware_sweep_required": True,
            "mount_load_path_required": True,
            "local_structure_required": True,
            "thermal_rejection_required": True,
        },
        "authority": {
            "claim": "RCS_ARCHITECTURE_FAMILY_DOWNSELECT_ONLY",
            "final_thruster_hardware_certified": False,
            "propellant_selected": False,
            "numeric_component_performance_certified": False,
            "installation_certified": False,
            "canon_changed": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "qualified_next_step": "RUN_RCS_PLUME_THERMAL_STRUCTURAL_INSTALLATION_FEASIBILITY",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_technology_downselect(), indent=2, sort_keys=True))
