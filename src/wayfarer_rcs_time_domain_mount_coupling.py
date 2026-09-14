from __future__ import annotations

"""Mount-resolved RCS allocation inside the coupled local-flight time loop.

This closes one specific E1 evidence gap: commanded vehicle wrench is no longer
applied directly.  At every qualification control step the demanded six-axis
wrench is passed through the requalified 16-hardpoint allocator, and only the
allocator's achieved wrench advances translation and rigid-body rotation.

The actuator contract is intentionally continuous and kinematic.  It does not
invent minimum impulse bit, valve latency, gimbal slew, plume geometry, or mount
structural compliance.  Those remain separate hardware closure axes.
"""

import math
from typing import Any, Sequence

from src.wayfarer_mass_inertia_authority import build_mass_inertia_state
from src.wayfarer_rcs_closed_loop_gnc import (
    ATTITUDE_GATE_DEG,
    RATE_GATE_DEG_S,
    _attitude_error_deg,
    _axis_angle_q,
    _cross,
    _dot,
    _inv3,
    _matvec,
    _qmul,
    _qnorm,
    _torque_command,
)
from src.wayfarer_rcs_mount_allocator import allocate_wrench

SCHEMA = "LOOM.Wayfarer.RCSTimeDomainMountCoupling"
SCHEMA_VERSION = "0.1"
CONTROL_DT_S = 1.0
MAX_TIME_S = 180.0
HOLD_TIME_S = 3.0
VELOCITY_GATE_M_S = 0.015
TRANSLATION_RESPONSE_RATE_S_INV = 0.16

_NOMINAL_FORCE_LIMIT_N = 100_000.0
_DEGRADED_FORCE_LIMIT_N = 75_000.0
_NOMINAL_TORQUE_LIMITS = {"roll": 200_000.0, "pitch": 1_000_000.0, "yaw": 1_000_000.0}
_DEGRADED_TORQUE_LIMITS = {"roll": 100_000.0, "pitch": 750_000.0, "yaw": 750_000.0}
_AXIS_INDEX = {"roll": 0, "pitch": 1, "yaw": 2}

ACTUATOR_CONTRACT = {
    "command_domain": "CONTINUOUS_MOUNT_FORCE_VECTOR",
    "allocation_location": "INSIDE_COUPLED_LOCAL_FLIGHT_TIME_LOOP",
    "allocation_cadence_s": CONTROL_DT_S,
    "allocation_cadence_authority": "NUMERICAL_QUALIFICATION_CADENCE_NOT_HARDWARE_BANDWIDTH",
    "mount_force_cap_source": "REQUALIFIED_CURRENT_CONFIGURATION_ALLOCATOR",
    "achieved_wrench_rule": "ONLY_ALLOCATOR_ACHIEVED_WRENCH_ADVANCES_STATE",
    "minimum_impulse_bit_modeled": False,
    "valve_dynamics_modeled": False,
    "gimbal_dynamics_modeled": False,
    "plume_geometry_modeled": False,
    "structural_mount_compliance_modeled": False,
    "final_thruster_hardware_certified": False,
}

_CASES = {
    "NOMINAL_MIXED_TRANSLATION_ATTITUDE": {
        "target_velocity_m_s": [0.08, 0.25, -0.12],
        "axis": "yaw",
        "angle_deg": 12.0,
        "failed_cluster": None,
    },
    "DEGRADED_MIXED_TRANSLATION_ATTITUDE_A": {
        "target_velocity_m_s": [0.05, 0.18, 0.10],
        "axis": "pitch",
        "angle_deg": 10.0,
        "failed_cluster": "A",
    },
    "DEGRADED_MIXED_TRANSLATION_ATTITUDE_B": {
        "target_velocity_m_s": [0.05, 0.18, 0.10],
        "axis": "pitch",
        "angle_deg": 10.0,
        "failed_cluster": "B",
    },
    "DEGRADED_MIXED_TRANSLATION_ATTITUDE_C": {
        "target_velocity_m_s": [0.05, 0.18, 0.10],
        "axis": "pitch",
        "angle_deg": 10.0,
        "failed_cluster": "C",
    },
    "DEGRADED_MIXED_TRANSLATION_ATTITUDE_D": {
        "target_velocity_m_s": [0.05, 0.18, 0.10],
        "axis": "pitch",
        "angle_deg": 10.0,
        "failed_cluster": "D",
    },
}


def _norm(v: Sequence[float]) -> float:
    return math.sqrt(sum(float(x) * float(x) for x in v))


def _clip_vector(v: list[float], limit: float) -> list[float]:
    mag = _norm(v)
    if mag <= limit or mag <= 1e-12:
        return v
    scale = limit / mag
    return [x * scale for x in v]


def _simulate_case(
    *,
    name: str,
    target_velocity_m_s: list[float],
    axis: str,
    angle_deg: float,
    failed_cluster: str | None,
) -> dict[str, Any]:
    state = build_mass_inertia_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
    mass_kg = float(state["mass_t"]) * 1000.0
    tensor = state["inertia_tensor_kg_m2"]
    inv_i = _inv3(tensor)
    force_limit = _DEGRADED_FORCE_LIMIT_N if failed_cluster else _NOMINAL_FORCE_LIMIT_N
    torque_limits = dict(_DEGRADED_TORQUE_LIMITS if failed_cluster else _NOMINAL_TORQUE_LIMITS)

    target_q = _axis_angle_q(_AXIS_INDEX[axis], math.radians(angle_deg))
    q = [1.0, 0.0, 0.0, 0.0]
    omega = [0.0, 0.0, 0.0]
    velocity = [0.0, 0.0, 0.0]
    position = [0.0, 0.0, 0.0]

    t = 0.0
    in_gate = 0.0
    allocation_calls = 0
    worst_residual = 0.0
    max_utilization = 0.0
    all_allocations_pass = True

    while t < MAX_TIME_S:
        vel_error = [float(target_velocity_m_s[j]) - velocity[j] for j in range(3)]
        demanded_force = _clip_vector(
            [mass_kg * TRANSLATION_RESPONSE_RATE_S_INV * e for e in vel_error],
            force_limit,
        )
        demanded_torque, _raw = _torque_command(tensor, q, target_q, omega, torque_limits)
        demanded_wrench = [*demanded_force, *demanded_torque]

        allocation = allocate_wrench(demanded_wrench, failed_cluster=failed_cluster)
        allocation_calls += 1
        worst_residual = max(worst_residual, float(allocation["relative_normalized_residual"]))
        max_utilization = max(max_utilization, float(allocation["max_mount_utilization_fraction"]))
        all_allocations_pass = all_allocations_pass and bool(allocation["pass"])
        if not allocation["pass"]:
            break

        achieved = allocation["achieved_wrench"]
        force = [float(achieved[k]) for k in ("FX", "FY", "FZ")]
        torque = [float(achieved[k]) for k in ("TX", "TY", "TZ")]

        accel = [f / mass_kg for f in force]
        velocity = [velocity[j] + accel[j] * CONTROL_DT_S for j in range(3)]
        position = [position[j] + velocity[j] * CONTROL_DT_S for j in range(3)]

        iw = _matvec(tensor, omega)
        gyro = _cross(omega, iw)
        rhs = [torque[j] - gyro[j] for j in range(3)]
        alpha = _matvec(inv_i, rhs)
        omega = [omega[j] + alpha[j] * CONTROL_DT_S for j in range(3)]
        qdot = _qmul(q, [0.0, *omega])
        q = _qnorm([q[j] + 0.5 * qdot[j] * CONTROL_DT_S for j in range(4)])

        t += CONTROL_DT_S
        velocity_error = _norm([float(target_velocity_m_s[j]) - velocity[j] for j in range(3)])
        attitude_error = _attitude_error_deg(q, target_q)
        body_rate = math.degrees(math.sqrt(_dot(omega, omega)))
        if velocity_error <= VELOCITY_GATE_M_S and attitude_error <= ATTITUDE_GATE_DEG and body_rate <= RATE_GATE_DEG_S:
            in_gate += CONTROL_DT_S
            if in_gate + 1e-12 >= HOLD_TIME_S:
                break
        else:
            in_gate = 0.0

    velocity_error = _norm([float(target_velocity_m_s[j]) - velocity[j] for j in range(3)])
    attitude_error = _attitude_error_deg(q, target_q)
    body_rate = math.degrees(math.sqrt(_dot(omega, omega)))
    passed = (
        all_allocations_pass
        and in_gate + 1e-12 >= HOLD_TIME_S
        and velocity_error <= VELOCITY_GATE_M_S
        and attitude_error <= ATTITUDE_GATE_DEG
        and body_rate <= RATE_GATE_DEG_S
        and worst_residual <= 1.0e-4
        and max_utilization <= 1.0 + 1.0e-9
    )
    return {
        "case": name,
        "failed_cluster": failed_cluster,
        "target_velocity_m_s": list(target_velocity_m_s),
        "target_attitude_axis": axis,
        "target_attitude_angle_deg": float(angle_deg),
        "duration_s": t,
        "allocation_calls": allocation_calls,
        "all_allocations_pass": all_allocations_pass,
        "worst_relative_normalized_residual": worst_residual,
        "max_mount_utilization_fraction": max_utilization,
        "terminal_velocity_error_m_s": velocity_error,
        "terminal_attitude_error_deg": attitude_error,
        "terminal_body_rate_deg_s": body_rate,
        "terminal_position_offset_m": position,
        "pass": passed,
    }


def build_time_domain_mount_coupling_qualification() -> dict[str, Any]:
    cases = {name: _simulate_case(name=name, **spec) for name, spec in _CASES.items()}
    all_pass = all(case["pass"] for case in cases.values())
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS" if all_pass else "FAIL",
        "disposition": (
            "MOUNT_LEVEL_ALLOCATION_BOUND_INTO_COUPLED_LOCAL_FLIGHT_TIME_LOOP"
            if all_pass
            else "TIME_DOMAIN_MOUNT_ALLOCATION_COUPLING_FAIL"
        ),
        "actuator_contract": dict(ACTUATOR_CONTRACT),
        "cases": cases,
        "summary": {
            "allocation_calls": sum(int(case["allocation_calls"]) for case in cases.values()),
            "worst_relative_normalized_residual": max(float(case["worst_relative_normalized_residual"]) for case in cases.values()),
            "max_mount_utilization_fraction": max(float(case["max_mount_utilization_fraction"]) for case in cases.values()),
        },
        "authority": {
            "mount_level_allocator_in_time_loop": all_pass,
            "allocated_achieved_wrench_drives_vehicle_state": all_pass,
            "configuration_aware_mass_inertia_consumed": True,
            "current_configuration_mount_allocator_consumed": True,
            "minimum_impulse_bit_certified": False,
            "valve_gimbal_dynamics_certified": False,
            "plume_interference_certified": False,
            "structural_mount_loads_certified": False,
            "final_thruster_hardware_certified": False,
            "canon_changed": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "remaining_open": [
            "minimum_impulse_bit_and_valve_gimbal_dynamics",
            "finite_plume_and_external_hardware_interference",
            "structural_rcs_mount_loads",
        ],
        "qualified_next_step": "QUALIFY_ACTUATOR_DISCRETIZATION_AND_VALVE_GIMBAL_DYNAMICS_WITHOUT_INVENTING_HARDWARE_PARAMETERS",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(build_time_domain_mount_coupling_qualification(), indent=2, sort_keys=True))
