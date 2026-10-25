from __future__ import annotations

"""Mission-relevant combined-wrench screen for the Wayfarer Q4 RCS candidate.

This module deliberately reuses the existing bounded allocation model rather
than creating another actuator model. It asks whether representative coupled
translation + attitude commands fit inside the current Q4 nominal/degraded
engineering envelope and 25 kN per-mount cap.

The cases are engineering screen cases, not flight-control commands, guidance
laws, or canon maneuver requirements.
"""

from typing import Any, Sequence

from wayfarer_rcs_allocation import _allocate
from wayfarer_rcs_control import build_rcs_control_candidate

STATUS = "ENGINEERING_CANDIDATE_NON_CANON"
_CLUSTER_IDS = ("A", "B", "C", "D")
_AXIS_NAMES = ("FX", "FY", "FZ", "TX", "TY", "TZ")

# Wrench ordering: FX,FY,FZ [N], TX,TY,TZ [N m].
# These deliberately stay below the existing pure-axis Q4 envelope because the
# point of the screen is simultaneous authority, not silently creating a
# stronger vehicle requirement.
_NOMINAL_CASES: dict[str, tuple[float, ...]] = {
    "DOCKING_CORRECTION": (
        10_000.0,
        20_000.0,
        -15_000.0,
        40_000.0,
        180_000.0,
        -160_000.0,
    ),
    "COLLISION_AVOIDANCE_SIDESTEP_SLEW": (
        15_000.0,
        45_000.0,
        25_000.0,
        -60_000.0,
        350_000.0,
        420_000.0,
    ),
    "TORCH_AXIS_ACQUISITION": (
        5_000.0,
        10_000.0,
        -10_000.0,
        25_000.0,
        450_000.0,
        -450_000.0,
    ),
    "PROXIMITY_BRAKE_AND_ALIGN": (
        -35_000.0,
        25_000.0,
        20_000.0,
        50_000.0,
        -300_000.0,
        300_000.0,
    ),
}

_DEGRADED_CASES: dict[str, tuple[float, ...]] = {
    "ONE_CLUSTER_OUT_APPROACH_CORRECTION": (
        -15_000.0,
        25_000.0,
        -20_000.0,
        35_000.0,
        220_000.0,
        -220_000.0,
    ),
    "ONE_CLUSTER_OUT_ABORT_SIDESTEP": (
        10_000.0,
        35_000.0,
        20_000.0,
        -45_000.0,
        260_000.0,
        280_000.0,
    ),
}


def _case_payload(target: Sequence[float]) -> dict[str, float]:
    return {axis: float(target[i]) for i, axis in enumerate(_AXIS_NAMES)}


def _screen_case(
    mounts: Sequence[dict[str, Any]],
    target: Sequence[float],
    *,
    failed_cluster: str | None,
) -> dict[str, Any]:
    result = _allocate(mounts, target, failed_cluster=failed_cluster)
    return {
        "requested_wrench": _case_payload(target),
        **result,
    }


def build_rcs_combined_maneuver_screen() -> dict[str, Any]:
    control = build_rcs_control_candidate()
    mounts = control["mounts"]

    nominal = {
        name: _screen_case(mounts, target, failed_cluster=None)
        for name, target in _NOMINAL_CASES.items()
    }

    degraded: dict[str, Any] = {}
    for cluster_id in _CLUSTER_IDS:
        degraded[cluster_id] = {
            name: _screen_case(mounts, target, failed_cluster=cluster_id)
            for name, target in _DEGRADED_CASES.items()
        }

    all_nominal_pass = all(case["pass"] for case in nominal.values())
    all_degraded_pass = all(
        case["pass"]
        for cluster_cases in degraded.values()
        for case in cluster_cases.values()
    )

    evaluated = list(nominal.values()) + [
        case for cluster_cases in degraded.values() for case in cluster_cases.values()
    ]
    max_utilization = max(
        (case["max_mount_utilization_fraction"] for case in evaluated),
        default=0.0,
    )
    worst_residual = max(
        (case["relative_normalized_residual"] for case in evaluated),
        default=0.0,
    )

    return {
        "standard_id": "WAYFARER_Q4_RCS_COMBINED_MANEUVER_SCREEN_V0.1",
        "status": STATUS,
        "authority": "ENGINEERING_STUDY_NON_CANON",
        "source_control_screen": control["standard_id"],
        "source_allocator": "WAYFARER_Q4_RCS_BOUNDED_ALLOCATION_SCREEN_V0.1",
        "scope": "REPRESENTATIVE_COMBINED_WRENCH_FEASIBILITY_ONLY",
        "nominal_cases": nominal,
        "one_cluster_out_cases": degraded,
        "summary": {
            "all_nominal_cases_pass": all_nominal_pass,
            "all_one_cluster_out_cases_pass": all_degraded_pass,
            "max_mount_utilization_fraction": max_utilization,
            "worst_relative_normalized_residual": worst_residual,
            "disposition": (
                "PASS_COMBINED_WRENCH_SCREEN_NOT_FINAL_CONTROL_QUALIFICATION"
                if all_nominal_pass and all_degraded_pass
                else "FAIL_COMBINED_WRENCH_SCREEN_REQUIRES_Q4_REWORK"
            ),
        },
        "authority_limits": {
            "simultaneous_exact_gimbal_solution": "NOT_QUALIFIED",
            "closed_loop_guidance_control": "OPEN_Q4",
            "physical_plume_cone": "OPEN_Q4_Q5",
            "structural_loads": "OPEN_Q4",
            "power_thermal_duty": "OPEN_Q5",
            "minimum_impulse_bit": "OPEN_Q4",
            "docking_contact_dynamics": "OPEN_Q4",
        },
        "notes": [
            "Case magnitudes are bounded engineering screen loads below the existing pure-axis Q4 nominal/degraded envelope; they are not new canon maneuver requirements.",
            "The same convexified sampled-vectoring allocator and 25 kN per-mount cap are reused; no parallel actuator physics is introduced.",
            "Passing these cases supports operational plausibility but does not prove arbitrary simultaneous-wrench feasibility or closed-loop control stability.",
            "A failing case is a design signal: adjust mount placement, vectoring, thrust class or maneuver doctrine rather than weakening the test silently.",
        ],
    }
