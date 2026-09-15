from __future__ import annotations

"""Governed plan for expensive coarse/fine RCS numerical exploration.

This module defines the exploration domain and authority boundary.  It does not
claim that any point is hardware-valid.  Full closed-loop execution belongs in
offline/CI engineering; interactive Pixel qualification replays only governed
boundary/witness points after an exploration result exists.
"""

from typing import Any

from src.wayfarer_rcs_time_domain_mount_coupling import _CASES

SCHEMA = "LOOM.Wayfarer.RCSCoarseFineOfflineExploration"
SCHEMA_VERSION = "0.1"

# Dimensionless numerical exploration coordinates, not hardware requirements.
# Include the already-qualified Pixel witness (0.20, 0.50) and independently
# vary both numerical authority-split axes around it.
_COARSE_FRACTIONS = (0.10, 0.20, 0.30)
_FINE_FRACTIONS = (0.25, 0.50, 1.00)
EXPLORATION_PARAMETERS = tuple(
    (coarse, fine)
    for coarse in _COARSE_FRACTIONS
    for fine in _FINE_FRACTIONS
)
EXPLORATION_CASES = tuple(_CASES)


def build_offline_exploration_plan() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "execution_authority": "OFFLINE_ENGINEERING_EXPLORATION",
        "parameter_contract": {
            "coarse_activation_parameter": "FRACTION_OF_CURRENT_MOUNT_THRUST_CAP",
            "fine_quantization_parameter": "FRACTION_OF_CURRENT_SAMPLED_EXACT_TRACE_MIB_UPPER_BOUND",
            "interpretation": "DIMENSIONLESS_NUMERICAL_EXPLORATION_NOT_HARDWARE_SPECIFICATION",
            "grid_policy": "INDEPENDENT_CARTESIAN_VARIATION_AROUND_EXISTING_PIXEL_WITNESS",
        },
        "parameters": [
            {"coarse_activation_fraction": coarse, "fine_quantization_fraction": fine}
            for coarse, fine in EXPLORATION_PARAMETERS
        ],
        "cases": list(EXPLORATION_CASES),
        "pixel_contract": {
            "full_sweep": "PROHIBITED",
            "qualification_mode": "BOUNDARY_AND_WITNESS_REPLAY_ONLY",
            "reason": "KEEP_EXPENSIVE_EXPLORATION_OUT_OF_INTERACTIVE_PIXEL_GATE",
        },
        "result_contract": {
            "required_per_point": [
                "pass_by_case",
                "terminal_velocity_error_m_s",
                "terminal_attitude_error_deg",
                "terminal_body_rate_deg_s",
                "max_mount_realization_error_N",
                "coarse_total_impulse_Ns",
                "fine_total_impulse_Ns",
            ],
            "derived_claim": "NUMERICAL_PASS_REGION_ONLY",
            "hardware_inference": "PROHIBITED_WITHOUT_SEPARATE_EVIDENCE",
        },
        "authority": {
            "coarse_fine_numerical_authority_envelope_qualified": False,
            "final_thruster_hardware_certified": False,
            "minimum_impulse_bit_certified": False,
            "valve_dynamics_certified": False,
            "vectoring_mechanism_certified": False,
            "working_fluid_certified": False,
            "plume_interference_certified": False,
            "structural_mount_loads_certified": False,
            "canon_changed": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "qualified_next_step": "EXECUTE_DETERMINISTIC_OFFLINE_SWEEP_AND_PERSIST_PROVENANCED_RESULT",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_offline_exploration_plan(), indent=2, sort_keys=True))
