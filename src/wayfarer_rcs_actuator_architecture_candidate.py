from __future__ import annotations

"""Evidence-bounded RCS actuator architecture candidate selection.

This module does not select flight hardware. It translates the already-qualified
sampled mount demand into an architecture-class decision for the next engineering
qualification step. The vehicle-facing contract remains one resultant force vector
per hardpoint; internal implementation remains provisional.
"""

from typing import Any

SCHEMA = "LOOM.Wayfarer.RCSActuatorArchitectureCandidate"
SCHEMA_VERSION = "0.1"

QUALIFIED_DEMAND_INPUTS = {
    "maximum_sampled_thrust_N": 20844.756650298394,
    "maximum_sampled_thrust_step_N": 20137.219000175366,
    "sampled_exact_trace_mib_upper_bound_Ns": 9.281346527990696,
    "one_sample_average_direction_slew_lower_bound_deg_s": 67.30273777540819,
    "maximum_sampled_direction_step_deg": 67.30273777540819,
    "sample_period_s": 1.0,
    "source": "MERGED_E1_RCS_ACTUATOR_REQUIREMENT_ENVELOPE_PR193",
}

EVIDENCE_ANCHORS = [
    {
        "id": "NASA_JSC_67723_PROPULSION_STANDARD",
        "supports": "MIB_RESPONSE_DUTY_CYCLE_CYCLE_LIFE_ARE_SEPARATE_GNC_PROPULSION_INTERFACE_REQUIREMENTS",
        "url": "https://standards.nasa.gov/system/files/tmp/JSC-67723_Propulsion_Standard_Basic_Final%20%281%29_0.pdf",
    },
    {
        "id": "NASA_MINIMUM_IMPULSE_THRUSTER_2005",
        "supports": "FAST_VALVE_RESPONSE_CAN_REDUCE_MINIMUM_IMPULSE_WITHOUT_CHANGING_THRUSTER_CORE",
        "url": "https://ntrs.nasa.gov/citations/20070032005",
    },
    {
        "id": "NASA_MINIMUM_IMPULSE_VALVE_2003",
        "supports": "MILLISECOND_CLASS_VALVE_RESPONSE_AND_HIGH_CYCLE_LIFE_ARE_DISTINCT_HARDWARE_AXES",
        "url": "https://ntrs.nasa.gov/citations/20060043626",
    },
    {
        "id": "ESA_TLPD_2025",
        "supports": "THROTTLEABLE_LIQUID_ENGINE_WITH_ELECTRONIC_VALVES_AND_MOVABLE_PINTLE_DEMONSTRATED_10_TO_110_PERCENT_RANGE",
        "url": "https://www.esa.int/Enabling_Support/Space_Transportation/Future_space_transportation/Vary_that_thrust_longer_hot-fire_of_rocket_engine_demonstrator",
    },
    {
        "id": "NASA_SECONDARY_INJECTION_TVC",
        "supports": "FLUIDIC_THRUST_VECTORING_CAN_REDIRECT_THRUST_WITHOUT_MOVING_WHOLE_ENGINE_MASS",
        "url": "https://ntrs.nasa.gov/api/citations/19680018640/downloads/19680018640.pdf",
    },
]


def build_actuator_architecture_candidate() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "disposition": "COMPOUND_COARSE_FINE_VECTORED_MOUNT_SELECTED_AS_NEXT_ENGINEERING_CANDIDATE",
        "qualified_demand_inputs": dict(QUALIFIED_DEMAND_INPUTS),
        "selected_candidate": {
            "architecture": "COMPOUND_COARSE_FINE_VECTORED_MOUNT",
            "vehicle_interface": "SINGLE_RESULTANT_FORCE_VECTOR_PER_HARDPOINT",
            "functional_elements": [
                "COARSE_HIGH_THRUST_ELEMENT",
                "FINE_IMPULSE_VERNIER_ELEMENT",
                "INTERNAL_VECTOR_SYNTHESIS_OR_THRUST_VECTOR_CONTROL",
                "LOCAL_ACTUATOR_CONTROLLER",
            ],
            "coarse_function": "SUPPLY_KILONEWTON_CLASS_TRANSLATION_AND_TORQUE_AUTHORITY",
            "fine_function": "SUPPLY_LOW_IMPULSE_AND_TERMINAL_CONTROL_WITHOUT_FORCING_MAIN_ELEMENT_TO_REPRODUCE_SMALLEST_TRACE_SAMPLE",
            "vectoring_function": "SYNTHESIZE_REQUIRED_RESULTANT_DIRECTION_WITHOUT_DEFAULTING_TO_WHOLE_ENGINE_MECHANICAL_GIMBAL",
            "allowed_vectoring_candidates": [
                "DIFFERENTIAL_THRUST_ACROSS_INTERNAL_NOZZLES",
                "FLUIDIC_OR_SECONDARY_INJECTION_THRUST_VECTORING",
                "MECHANICAL_GIMBAL_IF_LATER_EVIDENCE_SUPPORTS_RESPONSE_AND_LIFE",
            ],
            "working_fluid": "OPEN",
            "coarse_propulsion_cycle": "OPEN",
            "fine_propulsion_cycle": "OPEN",
            "mechanism": "OPEN",
        },
        "rejected_as_default": {
            "architecture": "SINGLE_MONOLITHIC_MECHANICALLY_GIMBALLED_20_TO_25_KN_THRUSTER",
            "reason": [
                "QUALIFIED_TRACE_COMBINES_HIGH_PEAK_THRUST_WITH_LOW_IMPULSE_RESOLUTION",
                "QUALIFIED_TRACE_CONTAINS_67_DEG_ONE_SECOND_DIRECTION_CHANGE",
                "NO_EVIDENCE_YET_SUPPORTS_REQUIRED_GIMBAL_SLEW_ACCELERATION_SETTLING_AND_CYCLE_LIFE",
                "NO_EVIDENCE_YET_SUPPORTS_MAIN_THRUSTER_MINIMUM_IMPULSE_COMPATIBILITY",
            ],
            "prohibited": False,
            "status": "NOT_BASELINE_PENDING_HARDWARE_EVIDENCE",
        },
        "evidence_anchors": list(EVIDENCE_ANCHORS),
        "authority": {
            "architecture_class_selected_for_next_engineering_step": True,
            "final_thruster_hardware_certified": False,
            "working_fluid_certified": False,
            "minimum_impulse_bit_certified": False,
            "valve_dynamics_certified": False,
            "vectoring_mechanism_certified": False,
            "plume_interference_certified": False,
            "structural_mount_loads_certified": False,
            "canon_changed": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "remaining_open": [
            "allocate_coarse_vs_fine_authority_and_replay_discretized_closed_loop",
            "select_evidence_backed_valve_response_mib_and_cycle_life_envelope",
            "select_and_validate_vectoring_mechanism_response_envelope",
            "select_rcs_working_fluid_and_exhaust_velocity",
            "finite_plume_and_external_hardware_interference",
            "structural_rcs_mount_loads",
        ],
        "qualified_next_step": "DERIVE_COARSE_FINE_AUTHORITY_SPLIT_AND_TEST_DISCRETIZED_CLOSED_LOOP_WITH_PARAMETER_ENVELOPES",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(build_actuator_architecture_candidate(), indent=2, sort_keys=True))
