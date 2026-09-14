from __future__ import annotations

"""Current-configuration bounded Wayfarer RCS mount allocator.

This recovers the useful PR #96 sampled-vectoring allocator, but removes its
hard-coded center of mass and binds the wrench calculation to the current E1
mass/inertia state plus the recovered 16-hardpoint candidate.  It is an
engineering allocation qualification, not final thruster hardware authority.
"""

import math
from typing import Any, Sequence

from src.wayfarer_mass_inertia_authority import build_mass_inertia_state
from src.wayfarer_recovered_rcs_candidate import build_recovered_rcs_candidate

SCHEMA = "LOOM.Wayfarer.RCSMountAllocator"
SCHEMA_VERSION = "0.1"
MOUNT_THRUST_CAP_N = 25_000.0
CHARACTERISTIC_LENGTH_M = 20.0
MAX_ITERATIONS = 1_500
RELATIVE_RESIDUAL_GATE = 1.0e-4
_CLUSTER_IDS = ("A", "B", "C", "D")
_AXIS_NAMES = ("FX", "FY", "FZ", "TX", "TY", "TZ")

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


def _dot3(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(a[i]) * float(b[i]) for i in range(3))


def _norm3(v: Sequence[float]) -> float:
    return math.sqrt(_dot3(v, v))


def _unit(v: Sequence[float]) -> tuple[float, float, float]:
    n = _norm3(v)
    if n <= 0.0:
        raise ValueError("zero vector")
    return tuple(float(x) / n for x in v)  # type: ignore[return-value]


def _cross(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    return (
        float(a[1]) * float(b[2]) - float(a[2]) * float(b[1]),
        float(a[2]) * float(b[0]) - float(a[0]) * float(b[2]),
        float(a[0]) * float(b[1]) - float(a[1]) * float(b[0]),
    )


def _sample_force_directions(position_m: Sequence[float]) -> list[dict[str, Any]]:
    y, z = float(position_m[1]), float(position_m[2])
    r = math.hypot(y, z)
    if r <= 0.0:
        raise ValueError("RCS mount cannot lie on ship axis")
    outward = (0.0, y / r, z / r)
    inward = (0.0, -outward[1], -outward[2])
    tangent = (0.0, -outward[2], outward[1])
    axial = (1.0, 0.0, 0.0)
    raw = (
        ("RADIAL_IN", inward),
        ("AXIAL_PLUS", (inward[0] + axial[0], inward[1], inward[2])),
        ("AXIAL_MINUS", (inward[0] - axial[0], inward[1], inward[2])),
        ("TANGENT_PLUS", (inward[0], inward[1] + tangent[1], inward[2] + tangent[2])),
        ("TANGENT_MINUS", (inward[0], inward[1] - tangent[1], inward[2] - tangent[2])),
    )
    return [{"name": name, "force_unit_ship": list(_unit(vector))} for name, vector in raw]


def _mount_model() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    recovered = build_recovered_rcs_candidate()
    state = build_mass_inertia_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
    mounts: list[dict[str, Any]] = []
    for i, source in enumerate(recovered["mounts"]):
        mounts.append(
            {
                "id": source["id"],
                "band": source["band"],
                "logical_cluster": _CLUSTER_IDS[i % 4],
                "position_m": list(source["position_m"]),
                "sampled_force_directions": _sample_force_directions(source["position_m"]),
            }
        )
    return mounts, state


def _wrench(position: Sequence[float], force_unit: Sequence[float], com: Sequence[float]) -> tuple[float, ...]:
    r = tuple(float(position[i]) - float(com[i]) for i in range(3))
    torque = _cross(r, force_unit)
    return tuple(float(x) for x in force_unit) + torque


def _normalized_wrench(wrench: Sequence[float]) -> tuple[float, ...]:
    return (
        float(wrench[0]), float(wrench[1]), float(wrench[2]),
        float(wrench[3]) / CHARACTERISTIC_LENGTH_M,
        float(wrench[4]) / CHARACTERISTIC_LENGTH_M,
        float(wrench[5]) / CHARACTERISTIC_LENGTH_M,
    )


def _physical_wrench(wrench: Sequence[float]) -> tuple[float, ...]:
    return (
        float(wrench[0]), float(wrench[1]), float(wrench[2]),
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
    theta = 0.0
    rho = 0
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


def _norm6(v: Sequence[float]) -> float:
    return math.sqrt(sum(float(x) * float(x) for x in v))


def _matvec(columns: Sequence[Sequence[float]], x: Sequence[float]) -> list[float]:
    out = [0.0] * 6
    for j, amount in enumerate(x):
        if amount == 0.0:
            continue
        for i in range(6):
            out[i] += float(columns[j][i]) * float(amount)
    return out


def _surviving_mounts(mounts: Sequence[dict[str, Any]], failed_cluster: str | None) -> list[dict[str, Any]]:
    return [m for m in mounts if failed_cluster is None or m["logical_cluster"] != failed_cluster]


def _build_channels(
    mounts: Sequence[dict[str, Any]], com: Sequence[float], failed_cluster: str | None
) -> tuple[list[tuple[float, ...]], list[list[int]], list[dict[str, Any]]]:
    columns: list[tuple[float, ...]] = []
    groups: list[list[int]] = []
    survivors = _surviving_mounts(mounts, failed_cluster)
    for mount in survivors:
        indices: list[int] = []
        for sample in mount["sampled_force_directions"]:
            indices.append(len(columns))
            columns.append(_normalized_wrench(_wrench(mount["position_m"], sample["force_unit_ship"], com)))
        groups.append(indices)
    return columns, groups, survivors


def allocate_wrench(
    target_physical: Sequence[float], *, failed_cluster: str | None = None
) -> dict[str, Any]:
    mounts, state = _mount_model()
    com = state["center_of_mass_m"]
    columns, groups, survivors = _build_channels(mounts, com, failed_cluster)
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
            projection = _project_capped_simplex(values, MOUNT_THRUST_CAP_N)
            for local_i, channel_i in enumerate(indices):
                projected[channel_i] = projection[local_i]
        next_momentum = (1.0 + math.sqrt(1.0 + 4.0 * momentum * momentum)) / 2.0
        factor = (momentum - 1.0) / next_momentum
        y = [projected[j] + factor * (projected[j] - x[j]) for j in range(len(x))]
        x = projected
        momentum = next_momentum

    achieved_normalized = _matvec(columns, x)
    achieved_physical = _physical_wrench(achieved_normalized)
    residual_normalized = [achieved_normalized[i] - target[i] for i in range(6)]
    relative_residual = _norm6(residual_normalized) / target_norm

    commands: dict[str, Any] = {}
    for mount, indices in zip(survivors, groups):
        resultant = [0.0, 0.0, 0.0]
        for local_i, channel_i in enumerate(indices):
            amount = max(0.0, float(x[channel_i]))
            direction = mount["sampled_force_directions"][local_i]["force_unit_ship"]
            for axis in range(3):
                resultant[axis] += amount * float(direction[axis])
        thrust = _norm3(resultant)
        commands[mount["id"]] = {
            "logical_cluster": mount["logical_cluster"],
            "position_m": mount["position_m"],
            "commanded_thrust_N": thrust,
            "utilization_fraction": thrust / MOUNT_THRUST_CAP_N,
            "commanded_force_unit_ship": [x / thrust for x in resultant] if thrust > 1e-12 else None,
        }

    max_util = max((float(c["utilization_fraction"]) for c in commands.values()), default=0.0)
    return {
        "target_wrench": {axis: float(target_physical[i]) for i, axis in enumerate(_AXIS_NAMES)},
        "achieved_wrench": {axis: float(achieved_physical[i]) for i, axis in enumerate(_AXIS_NAMES)},
        "relative_normalized_residual": relative_residual,
        "residual_gate": RELATIVE_RESIDUAL_GATE,
        "failed_cluster": failed_cluster,
        "mount_commands": commands,
        "active_mount_count": len(commands),
        "max_mount_utilization_fraction": max_util,
        "pass": relative_residual <= RELATIVE_RESIDUAL_GATE and max_util <= 1.0 + 1e-9,
    }


def _axis_targets(requirement: dict[str, float]) -> dict[str, tuple[float, ...]]:
    magnitudes = (
        requirement["translation_N"], requirement["translation_N"], requirement["translation_N"],
        requirement["roll_torque_Nm"], requirement["pitch_yaw_torque_Nm"], requirement["pitch_yaw_torque_Nm"],
    )
    targets: dict[str, tuple[float, ...]] = {}
    for axis_i, axis in enumerate(_AXIS_NAMES):
        for label, sign in (("PLUS", 1.0), ("MINUS", -1.0)):
            vector = [0.0] * 6
            vector[axis_i] = sign * magnitudes[axis_i]
            targets[f"{axis}_{label}"] = tuple(vector)
    return targets


def _screen(requirement: dict[str, float], failed_cluster: str | None) -> dict[str, Any]:
    cases = {name: allocate_wrench(target, failed_cluster=failed_cluster) for name, target in _axis_targets(requirement).items()}
    return {
        "failed_cluster": failed_cluster,
        "all_cases_pass": all(case["pass"] for case in cases.values()),
        "worst_relative_normalized_residual": max(case["relative_normalized_residual"] for case in cases.values()),
        "max_mount_utilization_fraction": max(case["max_mount_utilization_fraction"] for case in cases.values()),
        "cases": cases,
    }


def build_mount_allocation_qualification() -> dict[str, Any]:
    mounts, state = _mount_model()
    nominal = _screen(_REQUIREMENTS["NOMINAL"], None)
    degraded = {cluster: _screen(_REQUIREMENTS["ONE_CLUSTER_OUT"], cluster) for cluster in _CLUSTER_IDS}
    all_screens = [nominal, *degraded.values()]
    all_pass = all(screen["all_cases_pass"] for screen in all_screens)
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS" if all_pass else "FAIL",
        "disposition": "CURRENT_CONFIGURATION_MOUNT_LEVEL_BOUNDED_ALLOCATION_REQUALIFIED" if all_pass else "MOUNT_LEVEL_ALLOCATION_REQUALIFICATION_FAIL",
        "reference_state": {
            "mass_t": state["mass_t"],
            "center_of_mass_m": state["center_of_mass_m"],
            "launch_state": state["launch_state"],
        },
        "mount_count": len(mounts),
        "mount_thrust_cap_N": MOUNT_THRUST_CAP_N,
        "vectoring_model": "RECOVERED_PR96_45_DEG_SAMPLED_VECTORING_RECOMPUTED_AT_CURRENT_COM",
        "nominal": nominal,
        "one_cluster_out": degraded,
        "summary": {
            "worst_relative_normalized_residual": max(s["worst_relative_normalized_residual"] for s in all_screens),
            "max_mount_utilization_fraction": max(s["max_mount_utilization_fraction"] for s in all_screens),
        },
        "authority": {
            "mount_level_bounded_allocation_requalified": all_pass,
            "current_configuration_com_consumed": True,
            "recovered_hardpoint_geometry_consumed": True,
            "minimum_impulse_bit_certified": False,
            "finite_plume_clearance_certified": False,
            "structural_mount_loads_certified": False,
            "final_thruster_hardware_certified": False,
            "canon_changed": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "remaining_open": [
            "mount_level_force_allocation_in_the_time_loop",
            "minimum_impulse_bit_and_valve_gimbal_dynamics",
            "finite_plume_and_external_hardware_interference",
            "structural_rcs_mount_loads",
        ],
        "qualified_next_step": "BIND_THIS_ALLOCATOR_INTO_COUPLED_LOCAL_FLIGHT_TIME_LOOP_WITH_EXPLICIT_ACTUATOR_CONTRACT",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_mount_allocation_qualification(), indent=2, sort_keys=True))
