from __future__ import annotations

"""Q4 continuous-gimbal realizability proof for the Wayfarer RCS candidate.

The existing bounded allocator represents each mount with non-negative thrust
weights on five sample directions inside a 45 degree gimbal cone. At first
that looks like a relaxation because one physical mount cannot point in five
directions simultaneously.

For this specific model, however, any positive weighted sum of those sampled
force vectors is exactly realizable by one continuously gimballed actuator at
the same mount:

* force contributions at one mount add linearly;
* torque is r x F, so replacing several same-origin force vectors by their
  resultant preserves the exact wrench;
* the circular cone with half-angle <= 90 degrees is convex;
* every sampled direction lies inside the 45 degree cone, so every non-negative
  resultant also lies inside that cone;
* resultant magnitude is no greater than the sum of sample-channel thrusts,
  therefore the existing 25 kN per-mount cap remains conservative.

This closes the narrow mathematical question of simultaneous one-vector-per-
mount realizability *under the assumed continuous 45 degree gimbal envelope*.
It does not qualify physical gimbal hardware, slew rate, minimum impulse bit,
plume cone, structural loads, working fluid, power/thermal duty or closed-loop
control.
"""

import math
from typing import Any, Sequence

from wayfarer_rcs_allocation import MOUNT_THRUST_CAP_N
from wayfarer_rcs_control import VECTORING_HALF_ANGLE_DEG, build_rcs_control_candidate

STATUS = "ENGINEERING_CANDIDATE_NON_CANON"
_TOL = 1.0e-10


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(a[i]) * float(b[i]) for i in range(3))


def _norm(v: Sequence[float]) -> float:
    return math.sqrt(_dot(v, v))


def _scale(v: Sequence[float], s: float) -> tuple[float, float, float]:
    return tuple(float(x) * float(s) for x in v)  # type: ignore[return-value]


def _add(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    return tuple(float(a[i]) + float(b[i]) for i in range(3))  # type: ignore[return-value]


def _unit(v: Sequence[float]) -> tuple[float, float, float]:
    n = _norm(v)
    if n <= _TOL:
        raise ValueError("zero resultant has no unique gimbal direction")
    return tuple(float(x) / n for x in v)  # type: ignore[return-value]


def _angle_deg(a: Sequence[float], b: Sequence[float]) -> float:
    na = _norm(a)
    nb = _norm(b)
    if na <= _TOL or nb <= _TOL:
        return 0.0
    c = max(-1.0, min(1.0, _dot(a, b) / (na * nb)))
    return math.degrees(math.acos(c))


def collapse_sample_mix_to_single_gimbal(
    mount: dict[str, Any], sample_thrusts_N: Sequence[float]
) -> dict[str, Any]:
    """Collapse one mount's non-negative sampled thrust mix to one force vector.

    ``sample_thrusts_N`` must align with ``mount['sampled_force_directions']``.
    The function is deterministic and purely geometric; it does not command a
    physical actuator.
    """

    samples = mount["sampled_force_directions"]
    if len(sample_thrusts_N) != len(samples):
        raise ValueError("sample thrust count does not match sampled directions")
    if any(float(value) < -_TOL for value in sample_thrusts_N):
        raise ValueError("sample thrusts must be non-negative")

    summed_channel_thrust = sum(max(0.0, float(value)) for value in sample_thrusts_N)
    if summed_channel_thrust > MOUNT_THRUST_CAP_N + 1.0e-8:
        raise ValueError("sample thrust sum exceeds mount thrust cap")

    resultant = (0.0, 0.0, 0.0)
    for amount, sample in zip(sample_thrusts_N, samples):
        resultant = _add(resultant, _scale(sample["force_unit_ship"], max(0.0, float(amount))))

    resultant_thrust = _norm(resultant)
    inward = _scale(mount["surface_normal"], -1.0)

    if resultant_thrust <= _TOL:
        return {
            "mount_id": mount["id"],
            "commanded_thrust_N": 0.0,
            "commanded_force_unit_ship": None,
            "gimbal_angle_deg": 0.0,
            "within_45_deg_cone": True,
            "within_mount_thrust_cap": True,
            "summed_sample_channel_thrust_N": summed_channel_thrust,
            "resultant_force_N": [0.0, 0.0, 0.0],
        }

    force_unit = _unit(resultant)
    angle = _angle_deg(inward, force_unit)
    return {
        "mount_id": mount["id"],
        "commanded_thrust_N": resultant_thrust,
        "commanded_force_unit_ship": list(force_unit),
        "gimbal_angle_deg": angle,
        "within_45_deg_cone": angle <= VECTORING_HALF_ANGLE_DEG + 1.0e-9,
        "within_mount_thrust_cap": resultant_thrust <= MOUNT_THRUST_CAP_N + 1.0e-8,
        "summed_sample_channel_thrust_N": summed_channel_thrust,
        "resultant_force_N": list(resultant),
    }


def build_gimbal_realizability_proof() -> dict[str, Any]:
    control = build_rcs_control_candidate()
    cos_limit = math.cos(math.radians(VECTORING_HALF_ANGLE_DEG))

    mount_checks: list[dict[str, Any]] = []
    for mount in control["mounts"]:
        inward = _scale(mount["surface_normal"], -1.0)
        sample_checks = []
        for sample in mount["sampled_force_directions"]:
            force = sample["force_unit_ship"]
            sample_checks.append(
                {
                    "sample": sample["name"],
                    "unit_norm_error": abs(_norm(force) - 1.0),
                    "inward_dot": _dot(inward, force),
                    "inside_cone": _dot(inward, force) >= cos_limit - 1.0e-12,
                }
            )

        # Representative positive mixtures exercise the collapse numerically.
        mixtures = (
            (5_000.0, 0.0, 0.0, 0.0, 0.0),
            (5_000.0, 5_000.0, 5_000.0, 5_000.0, 5_000.0),
            (1_000.0, 6_000.0, 3_000.0, 8_000.0, 7_000.0),
            (0.0, 12_500.0, 0.0, 12_500.0, 0.0),
        )
        collapsed = [collapse_sample_mix_to_single_gimbal(mount, mix) for mix in mixtures]
        mount_checks.append(
            {
                "mount_id": mount["id"],
                "all_samples_inside_cone": all(item["inside_cone"] for item in sample_checks),
                "sample_checks": sample_checks,
                "representative_collapses": collapsed,
                "all_collapses_inside_cone": all(item["within_45_deg_cone"] for item in collapsed),
                "all_collapses_under_cap": all(item["within_mount_thrust_cap"] for item in collapsed),
            }
        )

    all_samples = all(item["all_samples_inside_cone"] for item in mount_checks)
    all_collapses = all(
        item["all_collapses_inside_cone"] and item["all_collapses_under_cap"]
        for item in mount_checks
    )

    return {
        "standard_id": "WAYFARER_Q4_RCS_SINGLE_GIMBAL_REALIZABILITY_V0.1",
        "status": STATUS,
        "authority": "ENGINEERING_STUDY_NON_CANON",
        "source_control_screen": control["standard_id"],
        "continuous_gimbal_half_angle_deg": VECTORING_HALF_ANGLE_DEG,
        "mount_thrust_cap_N": MOUNT_THRUST_CAP_N,
        "proof_basis": {
            "same_origin_force_linearity": True,
            "same_origin_torque_linearity": True,
            "cone_convex_for_half_angle_le_90_deg": VECTORING_HALF_ANGLE_DEG <= 90.0,
            "resultant_norm_le_sum_channel_thrust": True,
        },
        "mount_checks": mount_checks,
        "all_sample_directions_inside_continuous_cone": all_samples,
        "representative_positive_mixtures_collapse_inside_cone_and_cap": all_collapses,
        "allocation_implication": (
            "ANY_FEASIBLE_NONNEGATIVE_SAMPLED_MIX_AT_ONE_MOUNT_COLLAPSES_TO_ONE_SIMULTANEOUS_GIMBAL_VECTOR"
            if all_samples
            else "NOT_PROVEN"
        ),
        "disposition": (
            "PASS_SINGLE_GIMBAL_REALIZABILITY_UNDER_CONTINUOUS_45_DEG_ASSUMPTION"
            if all_samples and all_collapses
            else "FAIL_GIMBAL_REALIZABILITY_SCREEN"
        ),
        "authority_limits": {
            "physical_gimbal_hardware": "OPEN_Q4",
            "gimbal_slew_rate": "OPEN_Q4",
            "minimum_impulse_bit": "OPEN_Q4",
            "physical_plume_cone": "OPEN_Q4_Q5",
            "structural_loads": "OPEN_Q4",
            "working_fluid_exhaust_velocity": "OPEN_Q2_Q4",
            "power_thermal_duty": "OPEN_Q5",
            "closed_loop_guidance_control": "OPEN_Q4",
        },
        "notes": [
            "This result removes the need to interpret sampled-channel mixing as multiple simultaneous nozzles at one hardpoint.",
            "The proof is conditional on a continuously vectorable force direction anywhere inside the assumed 45 degree circular cone.",
            "The sampled allocator remains conservative in direction coverage because it searches only the convex hull of five directions, a subset of the full continuous cone.",
            "Passing does not select a gimbal mechanism or certify its dynamics, plume, structure, fluid, power, thermal or control implementation.",
        ],
    }
