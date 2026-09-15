from __future__ import annotations

"""Evidence-bounded RCS actuator architecture candidate selection.

Demand inputs are derived from the current case-bounded actuator requirement
envelope rather than duplicated numeric literals. This module still selects only
an architecture class for the next engineering step, never flight hardware.
"""

from typing import Any
from src.wayfarer_rcs_actuator_requirement_envelope import build_actuator_requirement_envelope

SCHEMA = "LOOM.Wayfarer.RCSActuatorArchitectureCandidate"
SCHEMA_VERSION = "0.2"

EVIDENCE_ANCHORS = [
    {"id":"NASA_JSC_67723_PROPULSION_STANDARD","supports":"MIB_RESPONSE_DUTY_CYCLE_CYCLE_LIFE_ARE_SEPARATE_GNC_PROPULSION_INTERFACE_REQUIREMENTS","url":"https://standards.nasa.gov/system/files/tmp/JSC-67723_Propulsion_Standard_Basic_Final%20%281%29_0.pdf"},
    {"id":"NASA_MINIMUM_IMPULSE_THRUSTER_2005","supports":"FAST_VALVE_RESPONSE_CAN_REDUCE_MINIMUM_IMPULSE_WITHOUT_CHANGING_THRUSTER_CORE","url":"https://ntrs.nasa.gov/citations/20070032005"},
    {"id":"NASA_MINIMUM_IMPULSE_VALVE_2003","supports":"MILLISECOND_CLASS_VALVE_RESPONSE_AND_HIGH_CYCLE_LIFE_ARE_DISTINCT_HARDWARE_AXES","url":"https://ntrs.nasa.gov/citations/20060043626"},
    {"id":"ESA_TLPD_2025","supports":"THROTTLEABLE_LIQUID_ENGINE_WITH_ELECTRONIC_VALVES_AND_MOVABLE_PINTLE_DEMONSTRATED_10_TO_110_PERCENT_RANGE","url":"https://www.esa.int/Enabling_Support/Space_Transportation/Future_space_transportation/Vary_that_thrust_longer_hot-fire_of_rocket_engine_demonstrator"},
    {"id":"NASA_SECONDARY_INJECTION_TVC","supports":"FLUIDIC_THRUST_VECTORING_CAN_REDIRECT_THRUST_WITHOUT_MOVING_WHOLE_ENGINE_MASS","url":"https://ntrs.nasa.gov/api/citations/19680018640/downloads/19680018640.pdf"},
]


def _qualified_demand_inputs() -> dict[str, Any]:
    envelope = build_actuator_requirement_envelope()
    aggregate = envelope["aggregate_sampled_actuator_demand"]
    keys = ("maximum_sampled_thrust_N", "maximum_sampled_thrust_step_N",
            "sampled_exact_trace_mib_upper_bound_Ns", "one_sample_average_direction_slew_lower_bound_deg_s",
            "maximum_sampled_direction_step_deg", "sample_period_s")
    out = {key: aggregate[key] for key in keys}
    out["transition_series_identity"] = envelope["requirement_contract"]["transition_series_identity"]
    out["source"] = "CURRENT_CASE_BOUNDED_E1_RCS_ACTUATOR_REQUIREMENT_ENVELOPE"
    return out


def build_actuator_architecture_candidate() -> dict[str, Any]:
    demand = _qualified_demand_inputs()
    return {
        "schema": SCHEMA, "schema_version": SCHEMA_VERSION, "status": "PASS",
        "disposition": "COMPOUND_COARSE_FINE_VECTORED_MOUNT_SELECTED_AS_NEXT_ENGINEERING_CANDIDATE",
        "qualified_demand_inputs": demand,
        "selected_candidate": {
            "architecture": "COMPOUND_COARSE_FINE_VECTORED_MOUNT",
            "vehicle_interface": "SINGLE_RESULTANT_FORCE_VECTOR_PER_HARDPOINT",
            "functional_elements": ["COARSE_HIGH_THRUST_ELEMENT", "FINE_IMPULSE_VERNIER_ELEMENT",
                                    "INTERNAL_VECTOR_SYNTHESIS_OR_THRUST_VECTOR_CONTROL", "LOCAL_ACTUATOR_CONTROLLER"],
            "coarse_function": "SUPPLY_KILONEWTON_CLASS_TRANSLATION_AND_TORQUE_AUTHORITY",
            "fine_function": "SUPPLY_LOW_IMPULSE_AND_TERMINAL_CONTROL_WITHOUT_FORCING_MAIN_ELEMENT_TO_REPRODUCE_SMALLEST_TRACE_SAMPLE",
            "vectoring_function": "SYNTHESIZE_REQUIRED_RESULTANT_DIRECTION_WITHOUT_DEFAULTING_TO_WHOLE_ENGINE_MECHANICAL_GIMBAL",
            "allowed_vectoring_candidates": ["DIFFERENTIAL_THRUST_ACROSS_INTERNAL_NOZZLES", "FLUIDIC_OR_SECONDARY_INJECTION_THRUST_VECTORING",
                                             "MECHANICAL_GIMBAL_IF_LATER_EVIDENCE_SUPPORTS_RESPONSE_AND_LIFE"],
            "working_fluid": "OPEN", "coarse_propulsion_cycle": "OPEN", "fine_propulsion_cycle": "OPEN", "mechanism": "OPEN"},
        "rejected_as_default": {
            "architecture": "SINGLE_MONOLITHIC_MECHANICALLY_GIMBALLED_20_TO_25_KN_THRUSTER",
            "reason": ["QUALIFIED_TRACE_COMBINES_HIGH_PEAK_THRUST_WITH_LOW_IMPULSE_RESOLUTION",
                       "QUALIFIED_TRACE_REQUIRES_NONTRIVIAL_DIRECTION_TRANSIENT_RESPONSE",
                       "NO_EVIDENCE_YET_SUPPORTS_REQUIRED_GIMBAL_SLEW_ACCELERATION_SETTLING_AND_CYCLE_LIFE",
                       "NO_EVIDENCE_YET_SUPPORTS_MAIN_THRUSTER_MINIMUM_IMPULSE_COMPATIBILITY"],
            "prohibited": False, "status": "NOT_BASELINE_PENDING_HARDWARE_EVIDENCE"},
        "evidence_anchors": list(EVIDENCE_ANCHORS),
        "authority": {"architecture_class_selected_for_next_engineering_step": True, "final_thruster_hardware_certified": False,
                      "working_fluid_certified": False, "minimum_impulse_bit_certified": False, "valve_dynamics_certified": False,
                      "vectoring_mechanism_certified": False, "plume_interference_certified": False,
                      "structural_mount_loads_certified": False, "canon_changed": False,
                      "campaign_state_mutation": "ZERO", "llm_calculation_authority": "ZERO"},
        "remaining_open": ["allocate_coarse_vs_fine_authority_and_replay_discretized_closed_loop",
                           "select_evidence_backed_valve_response_mib_and_cycle_life_envelope",
                           "select_and_validate_vectoring_mechanism_response_envelope", "select_rcs_working_fluid_and_exhaust_velocity",
                           "finite_plume_and_external_hardware_interference", "structural_rcs_mount_loads"],
        "qualified_next_step": "DERIVE_COARSE_FINE_AUTHORITY_SPLIT_AND_TEST_DISCRETIZED_CLOSED_LOOP_WITH_PARAMETER_ENVELOPES"}


if __name__ == "__main__":
    import json
    print(json.dumps(build_actuator_architecture_candidate(), indent=2, sort_keys=True))
