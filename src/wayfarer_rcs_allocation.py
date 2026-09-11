from __future__ import annotations

"""Bounded Q4 RCS force-allocation screen for the Wayfarer candidate layout.

The allocator works in the already-screened sampled 45 degree vectoring space,
with a 25 kN cap per hardpoint.  In addition to wrench residuals it now exposes
the physically meaningful resultant force at each surviving hardpoint.  The
single-gimbal realizability proof establishes that this resultant can be
represented by one simultaneous direction/magnitude under the continuous
45-degree engineering assumption.
"""

import math
from typing import Any, Sequence

from wayfarer_rcs_control import build_rcs_control_candidate

STATUS = "ENGINEERING_CANDIDATE_NON_CANON"
MOUNT_THRUST_CAP_N = 25_000.0
CHARACTERISTIC_LENGTH_M = 20.0
MAX_ITERATIONS = 1_500
RELATIVE_RESIDUAL_GATE = 1.0e-4

_REQUIREMENTS = {
    "NOMINAL": {
        "translation_N": 100_000.0,
        "pitch_yaw_torque_Nm": 1_000_000.0,
        "roll_torque_Nm": 200_000.0,
    },
    "ONE_CLUSTER_OUT": {
        "translation_N": 75_000.0,
        "pitch_yaw_torque_Nm": 750_000.0,
        "roll_torque_Nm": 100_000.0,
    },
}

_AXIS_NAMES = ("FX", "FY", "FZ", "TX", "TY", "TZ")
_CLUSTER_IDS = ("A", "B", "C", "D")
_REFERENCE_COM = (26.6767, 0.0, 0.1481)


def _cross(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    return (
        float(a[1]) * float(b[2]) - float(a[2]) * float(b[1]),
        float(a[2]) * float(b[0]) - float(a[0]) * float(b[2]),
        float(a[0]) * float(b[1]) - float(a[1]) * float(b[0]),
    )


def _norm3(v: Sequence[float]) -> float:
    return math.sqrt(sum(float(x) * float(x) for x in v))


def _wrench(position: Sequence[float], force_unit: Sequence[float]) -> tuple[float, ...]:
    r = (
        float(position[0]) - _REFERENCE_COM[0],
        float(position[1]) - _REFERENCE_COM[1],
        float(position[2]) - _REFERENCE_COM[2],
    )
    torque = _cross(r, force_unit)
    return tuple(float(x) for x in force_unit) + torque


def _normalized_wrench(wrench: Sequence[float]) -> tuple[float, ...]:
    return (
        float(wrench[0]),
        float(wrench[1]),
        float(wrench[2]),
        float(wrench[3]) / CHARACTERISTIC_LENGTH_M,
        float(wrench[4]) / CHARACTERISTIC_LENGTH_M,
        float(wrench[5]) / CHARACTERISTIC_LENGTH_M,
    )


def _physical_wrench(wrench: Sequence[float]) -> tuple[float, ...]:
    return (
        float(wrench[0]),
        float(wrench[1]),
        float(wrench[2]),
        float(wrench[3]) * CHARACTERISTIC_LENGTH_M,
        float(wrench[4]) * CHARACTERISTIC_LENGTH_M,
        float(wrench[5]) * CHARACTERISTIC_LENGTH_M,
    )


def _project_capped_simplex(values: Sequence[float], cap: float) -> list[float]:
    clipped = [max(0.0, float(x)) for x in values]
    if sum(clipped) <= cap:
        return clipped
    ordered = sorted((float(x) for x in values), reverse=True)
    cumulative = 0.0
    rho = -1
    theta = 0.0
    for i, value in enumerate(ordered, start=1):
        cumulative += value
        candidate = (cumulative - cap) / i
        if value > candidate:
            rho = i
            theta = candidate
    if rho <= 0:
        return [0.0 for _ in values]
    return [max(0.0, float(x) - theta) for x in values]


def _dot6(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(a[i]) * float(b[i]) for i in range(6))


def _matvec(columns: Sequence[Sequence[float]], x: Sequence[float]) -> list[float]:
    out = [0.0] * 6
    for j, amount in enumerate(x):
        if amount == 0.0:
            continue
        col = columns[j]
        for i in range(6):
            out[i] += float(col[i]) * float(amount)
    return out


def _norm6(v: Sequence[float]) -> float:
    return math.sqrt(sum(float(x) * float(x) for x in v))


def _surviving_mounts(mounts: Sequence[dict[str, Any]], failed_cluster: str | None) -> list[dict[str, Any]]:
    return [m for m in mounts if failed_cluster is None or m["logical_cluster"] != failed_cluster]


def _build_channels(
    mounts: Sequence[dict[str, Any]], failed_cluster: str | None
) -> tuple[list[tuple[float, ...]], list[list[int]], list[str]]:
    columns: list[tuple[float, ...]] = []
    groups: list[list[int]] = []
    mount_ids: list[str] = []
    for mount in _surviving_mounts(mounts, failed_cluster):
        indices: list[int] = []
        for sample in mount["sampled_force_directions"]:
            physical = _wrench(mount["position_m"], sample["force_unit_ship"])
            indices.append(len(columns))
            columns.append(_normalized_wrench(physical))
        groups.append(indices)
        mount_ids.append(mount["id"])
    return columns, groups, mount_ids


def _resultant_mount_commands(
    mounts: Sequence[dict[str, Any]],
    groups: Sequence[Sequence[int]],
    x: Sequence[float],
    failed_cluster: str | None,
) -> dict[str, dict[str, Any]]:
    commands: dict[str, dict[str, Any]] = {}
    for mount, indices in zip(_surviving_mounts(mounts, failed_cluster), groups):
        resultant = [0.0, 0.0, 0.0]
        summed_channel_thrust = 0.0
        for local_i, channel_i in enumerate(indices):
            amount = max(0.0, float(x[channel_i]))
            summed_channel_thrust += amount
            direction = mount["sampled_force_directions"][local_i]["force_unit_ship"]
            for axis in range(3):
                resultant[axis] += amount * float(direction[axis])
        thrust = _norm3(resultant)
        commands[mount["id"]] = {
            "logical_cluster": mount["logical_cluster"],
            "commanded_thrust_N": thrust,
            "mount_utilization_fraction": thrust / MOUNT_THRUST_CAP_N,
            "summed_sample_channel_thrust_N": summed_channel_thrust,
            "commanded_force_unit_ship": (
                [component / thrust for component in resultant] if thrust > 1.0e-12 else None
            ),
        }
    return commands


def _allocate(
    mounts: Sequence[dict[str, Any]],
    target_physical: Sequence[float],
    *,
    failed_cluster: str | None,
) -> dict[str, Any]:
    columns, groups, mount_ids = _build_channels(mounts, failed_cluster)
    target = list(_normalized_wrench(target_physical))
    target_norm = max(_norm6(target), 1.0)
    frobenius_sq = sum(sum(value * value for value in col) for col in columns)
    step = 0.9 / max(2.0 * frobenius_sq, 1.0)

    x = [0.0] * len(columns)
    y = list(x)
    momentum = 1.0
    for _ in range(MAX_ITERATIONS):
        achieved_y = _matvec(columns, y)
        residual_y = [achieved_y[i] - target[i] for i in range(6)]
        gradient = [2.0 * _dot6(col, residual_y) for col in columns]
        trial = [y[j] - step * gradient[j] for j in range(len(columns))]
        projected = list(trial)
        for indices in groups:
            values = [trial[j] for j in indices]
            group_projection = _project_capped_simplex(values, MOUNT_THRUST_CAP_N)
            for local_i, channel_i in enumerate(indices):
                projected[channel_i] = group_projection[local_i]
        next_momentum = (1.0 + math.sqrt(1.0 + 4.0 * momentum * momentum)) / 2.0
        factor = (momentum - 1.0) / next_momentum
        y = [projected[j] + factor * (projected[j] - x[j]) for j in range(len(x))]
        x = projected
        momentum = next_momentum

    achieved_normalized = _matvec(columns, x)
    residual_normalized = [achieved_normalized[i] - target[i] for i in range(6)]
    relative_residual = _norm6(residual_normalized) / target_norm
    achieved_physical = _physical_wrench(achieved_normalized)

    mount_usage = {mount_id: sum(x[j] for j in indices) for mount_id, indices in zip(mount_ids, groups)}
    max_mount_thrust = max(mount_usage.values(), default=0.0)
    max_utilization = max_mount_thrust / MOUNT_THRUST_CAP_N
    physical_commands = _resultant_mount_commands(mounts, groups, x, failed_cluster)
    total_resultant_thrust = sum(item["commanded_thrust_N"] for item in physical_commands.values())
    max_physical_utilization = max(
        (item["mount_utilization_fraction"] for item in physical_commands.values()), default=0.0
    )

    return {
        "target_wrench": {axis: float(target_physical[i]) for i, axis in enumerate(_AXIS_NAMES)},
        "achieved_wrench": {axis: float(achieved_physical[i]) for i, axis in enumerate(_AXIS_NAMES)},
        "relative_normalized_residual": relative_residual,
        "residual_gate": RELATIVE_RESIDUAL_GATE,
        "max_mount_thrust_N": max_mount_thrust,
        "max_mount_utilization_fraction": max_utilization,
        "physical_mount_commands": physical_commands,
        "total_resultant_mount_thrust_N": total_resultant_thrust,
        "max_physical_mount_utilization_fraction": max_physical_utilization,
        "active_mount_count": len(groups),
        "failed_cluster": failed_cluster,
        "pass": relative_residual <= RELATIVE_RESIDUAL_GATE and max_utilization <= 1.0 + 1e-9,
    }


def _axis_targets(requirement: dict[str, float]) -> dict[str, tuple[float, ...]]:
    translation = requirement["translation_N"]
    roll = requirement["roll_torque_Nm"]
    pitch_yaw = requirement["pitch_yaw_torque_Nm"]
    magnitudes = (translation, translation, translation, roll, pitch_yaw, pitch_yaw)
    targets: dict[str, tuple[float, ...]] = {}
    for axis_i, axis in enumerate(_AXIS_NAMES):
        for label, sign in (("PLUS", 1.0), ("MINUS", -1.0)):
            vector = [0.0] * 6
            vector[axis_i] = sign * magnitudes[axis_i]
            targets[f"{axis}_{label}"] = tuple(vector)
    return targets


def _screen(mounts: Sequence[dict[str, Any]], requirement: dict[str, float], *, failed_cluster: str | None) -> dict[str, Any]:
    cases = {name: _allocate(mounts, target, failed_cluster=failed_cluster) for name, target in _axis_targets(requirement).items()}
    all_pass = all(case["pass"] for case in cases.values())
    max_utilization = max(case["max_mount_utilization_fraction"] for case in cases.values())
    worst_residual = max(case["relative_normalized_residual"] for case in cases.values())
    return {
        "failed_cluster": failed_cluster,
        "all_cases_pass": all_pass,
        "max_mount_utilization_fraction": max_utilization,
        "worst_relative_normalized_residual": worst_residual,
        "cases": cases,
        "disposition": "PASS_BOUNDED_ALLOCATION_SCREEN_NOT_FINAL_CONTROL_QUALIFICATION" if all_pass else "FAIL_BOUNDED_ALLOCATION_SCREEN",
    }


def build_rcs_allocation_screen() -> dict[str, Any]:
    control = build_rcs_control_candidate()
    mounts = control["mounts"]
    nominal = _screen(mounts, _REQUIREMENTS["NOMINAL"], failed_cluster=None)
    degraded = {
        cluster_id: _screen(mounts, _REQUIREMENTS["ONE_CLUSTER_OUT"], failed_cluster=cluster_id)
        for cluster_id in _CLUSTER_IDS
    }
    return {
        "standard_id": "WAYFARER_Q4_RCS_BOUNDED_ALLOCATION_SCREEN_V0.2",
        "status": STATUS,
        "authority": "ENGINEERING_STUDY_NON_CANON",
        "source_control_screen": control["standard_id"],
        "allocation_model": "SAMPLED_VECTORING_WITH_PER_MOUNT_THRUST_CAP_AND_PHYSICAL_RESULTANT_REPORTING",
        "mount_thrust_cap_N": MOUNT_THRUST_CAP_N,
        "characteristic_length_for_numerical_scaling_m": CHARACTERISTIC_LENGTH_M,
        "requirements": _REQUIREMENTS,
        "screens": {"NOMINAL": nominal, "ONE_CLUSTER_OUT": degraded},
        "exact_nozzle_hardware_status": "OPEN_Q4",
        "plume_interference_status": "OPEN_Q4",
        "structural_load_qualification": "OPEN_Q4",
        "minimum_impulse_bit_status": "OPEN_Q4",
        "closed_loop_control_status": "OPEN_Q4",
        "power_thermal_qualification": "OPEN_Q5",
        "notes": [
            "The reported physical mount command is the resultant of each mount's non-negative sampled allocation.",
            "Single-gimbal realizability is separately proven under the continuous 45 degree engineering assumption.",
            "The nominal/degraded targets are inherited from the existing Q4 HUD envelope; this module does not create stronger force/torque authority.",
            "Final actuator qualification still requires hardware dynamics, plume/interference closure, structural limits, minimum impulse behavior, Q5 power/thermal closure and closed-loop control qualification.",
        ],
    }
