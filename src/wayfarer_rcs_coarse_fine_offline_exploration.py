from __future__ import annotations

"""Governed deterministic coarse/fine RCS numerical exploration.

The full Cartesian sweep is an offline/CI engineering workload. It reuses the
qualified realized-wrench closed-loop simulator but does not convert numerical
coordinates into hardware requirements. Interactive Pixel qualification is
reserved for later boundary/witness replay of a persisted result.
"""

from typing import Any

from src.wayfarer_rcs_actuator_requirement_envelope import build_actuator_requirement_envelope
from src.wayfarer_rcs_coarse_fine_authority_envelope import _simulate_case
from src.wayfarer_rcs_time_domain_mount_coupling import _CASES

SCHEMA = "LOOM.Wayfarer.RCSCoarseFineOfflineExploration"
SCHEMA_VERSION = "0.2"

_COARSE_FRACTIONS = (0.10, 0.20, 0.30)
_FINE_FRACTIONS = (0.25, 0.50, 1.00)
EXPLORATION_PARAMETERS = tuple((coarse, fine) for coarse in _COARSE_FRACTIONS for fine in _FINE_FRACTIONS)
EXPLORATION_CASES = tuple(_CASES)


def _authority(*, claim: str = "PLAN_ONLY") -> dict[str, Any]:
    return {
        "claim": claim,
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
    }


def build_offline_exploration_plan() -> dict[str, Any]:
    return {
        "schema": SCHEMA, "schema_version": SCHEMA_VERSION,
        "execution_authority": "OFFLINE_ENGINEERING_EXPLORATION",
        "parameter_contract": {
            "coarse_activation_parameter": "FRACTION_OF_CURRENT_MOUNT_THRUST_CAP",
            "fine_quantization_parameter": "FRACTION_OF_CURRENT_SAMPLED_EXACT_TRACE_MIB_UPPER_BOUND",
            "interpretation": "DIMENSIONLESS_NUMERICAL_EXPLORATION_NOT_HARDWARE_SPECIFICATION",
            "grid_policy": "INDEPENDENT_CARTESIAN_VARIATION_AROUND_EXISTING_PIXEL_WITNESS",
        },
        "parameters": [{"coarse_activation_fraction": c, "fine_quantization_fraction": f}
                       for c, f in EXPLORATION_PARAMETERS],
        "cases": list(EXPLORATION_CASES),
        "pixel_contract": {"full_sweep": "PROHIBITED",
            "qualification_mode": "BOUNDARY_AND_WITNESS_REPLAY_ONLY",
            "reason": "KEEP_EXPENSIVE_EXPLORATION_OUT_OF_INTERACTIVE_PIXEL_GATE"},
        "result_contract": {"required_per_point": ["pass_by_case", "terminal_velocity_error_m_s",
            "terminal_attitude_error_deg", "terminal_body_rate_deg_s", "max_mount_realization_error_N",
            "coarse_total_impulse_Ns", "fine_total_impulse_Ns"],
            "derived_claim": "NUMERICAL_PASS_REGION_ONLY",
            "hardware_inference": "PROHIBITED_WITHOUT_SEPARATE_EVIDENCE"},
        "authority": _authority(),
        "qualified_next_step": "EXECUTE_DETERMINISTIC_OFFLINE_SWEEP_AND_PERSIST_PROVENANCED_RESULT",
    }


def execute_offline_exploration() -> dict[str, Any]:
    demand = build_actuator_requirement_envelope()["aggregate_sampled_actuator_demand"]
    trace_mib_ns = float(demand["sampled_exact_trace_mib_upper_bound_Ns"])
    points: list[dict[str, Any]] = []
    for coarse, fine in EXPLORATION_PARAMETERS:
        cases = {name: _simulate_case(name, _CASES[name], coarse_fraction=coarse,
                                      fine_fraction=fine, trace_mib_ns=trace_mib_ns)
                 for name in EXPLORATION_CASES}
        points.append({"coarse_activation_fraction": coarse,
                       "fine_quantization_fraction": fine,
                       "pass": all(bool(case["pass"]) for case in cases.values()),
                       "pass_by_case": {name: bool(case["pass"]) for name, case in cases.items()},
                       "cases": cases})
    pass_region = [{"coarse_activation_fraction": p["coarse_activation_fraction"],
                    "fine_quantization_fraction": p["fine_quantization_fraction"]}
                   for p in points if p["pass"]]
    return {
        "schema": SCHEMA, "schema_version": SCHEMA_VERSION,
        "status": "COMPLETE",
        "execution_authority": "OFFLINE_ENGINEERING_EXPLORATION",
        "execution": {"point_count": len(points),
                      "case_runs": len(points) * len(EXPLORATION_CASES),
                      "deterministic_source": "CURRENT_GOVERNED_REALIZED_WRENCH_CLOSED_LOOP_SIMULATOR"},
        "source_demand": {"sampled_exact_trace_mib_upper_bound_Ns": trace_mib_ns,
                          "transition_series_identity": "QUALIFICATION_CASE_PLUS_MOUNT_ID"},
        "points": points,
        "pass_region": pass_region,
        "authority": _authority(claim="NUMERICAL_PASS_REGION_ONLY"),
        "pixel_contract": {"full_sweep": "PROHIBITED", "qualification_mode": "BOUNDARY_AND_WITNESS_REPLAY_ONLY"},
        "qualified_next_step": "PERSIST_PROVENANCED_RESULT_AND_SELECT_BOUNDARY_WITNESSES_FOR_PIXEL_REPLAY",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(execute_offline_exploration(), indent=2, sort_keys=True))
