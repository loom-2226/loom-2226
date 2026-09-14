from __future__ import annotations

"""Net-wrench coupled local-flight qualification for Wayfarer RCS.

This model integrates translational velocity and full rigid-body rotational state in
the same time loop. It deliberately operates at the net-wrench vehicle level: the
current recovered RCS force/torque envelope is consumed, but mount-level pulse,
gimbal, plume and structural hardware are not silently promoted to authority.
"""

import math
from typing import Any

from src.wayfarer_mass_inertia_authority import build_mass_inertia_state
from src.wayfarer_rcs_closed_loop_gnc import (
    DT_S,
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

SCHEMA = "LOOM.Wayfarer.RCSCoupledLocalFlight"
SCHEMA_VERSION = "0.1"
MAX_TIME_S = 240.0
HOLD_TIME_S = 2.0
VELOCITY_GATE_M_S = 0.01
TRANSLATION_RESPONSE_RATE_S_INV = 0.18

_NOMINAL_FORCE_LIMIT_N = 100_000.0
_DEGRADED_FORCE_LIMIT_N = 75_000.0
_NOMINAL_TORQUE_LIMITS = {"roll": 200_000.0, "pitch": 1_000_000.0, "yaw": 1_000_000.0}
_DEGRADED_TORQUE_LIMITS = {"roll": 100_000.0, "pitch": 750_000.0, "yaw": 750_000.0}
_AXIS_INDEX = {"roll": 0, "pitch": 1, "yaw": 2}

_NOMINAL_CASES = {
    "DOCKING_BRAKE_AND_ALIGN": {"target_velocity_m_s": [-0.35, 0.22, -0.18], "axis": "yaw", "angle_deg": 12.0},
    "COLLISION_AVOIDANCE_SIDESTEP_SLEW": {"target_velocity_m_s": [0.15, 0.85, 0.40], "axis": "pitch", "angle_deg": 35.0},
    "TORCH_AXIS_ACQUISITION": {"target_velocity_m_s": [0.10, -0.20, 0.12], "axis": "pitch", "angle_deg": 50.0},
}

_DEGRADED_CASES = {
    "ONE_CLUSTER_OUT_APPROACH_CORRECTION": {"target_velocity_m_s": [-0.20, 0.35, -0.25], "axis": "yaw", "angle_deg": 18.0},
    "ONE_CLUSTER_OUT_ABORT_SIDESTEP": {"target_velocity_m_s": [0.10, 0.55, 0.30], "axis": "roll", "angle_deg": 28.0},
}


def _norm(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def _clip_vector(v: list[float], limit: float) -> tuple[list[float], float]:
    mag = _norm(v)
    if mag <= limit or mag <= 1e-12:
        return v, mag / max(limit, 1.0)
    scale = limit / mag
    return [x * scale for x in v], 1.0


def simulate_coupled_case(
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
    peak_force_fraction = 0.0
    peak_torque_fraction = 0.0
    while t < MAX_TIME_S:
        vel_error = [float(target_velocity_m_s[j]) - velocity[j] for j in range(3)]
        raw_force = [mass_kg * TRANSLATION_RESPONSE_RATE_S_INV * e for e in vel_error]
        force, force_fraction = _clip_vector(raw_force, force_limit)
        peak_force_fraction = max(peak_force_fraction, force_fraction)
        accel = [f / mass_kg for f in force]
        velocity = [velocity[j] + accel[j] * DT_S for j in range(3)]
        position = [position[j] + velocity[j] * DT_S for j in range(3)]

        torque, _raw = _torque_command(tensor, q, target_q, omega, torque_limits)
        limits = [torque_limits["roll"], torque_limits["pitch"], torque_limits["yaw"]]
        peak_torque_fraction = max(peak_torque_fraction, max(abs(torque[j]) / limits[j] for j in range(3)))
        iw = _matvec(tensor, omega)
        gyro = _cross(omega, iw)
        rhs = [torque[j] - gyro[j] for j in range(3)]
        alpha = _matvec(inv_i, rhs)
        omega = [omega[j] + alpha[j] * DT_S for j in range(3)]
        qdot = _qmul(q, [0.0, *omega])
        q = _qnorm([q[j] + 0.5 * qdot[j] * DT_S for j in range(4)])

        t += DT_S
        terminal_velocity_error = _norm([float(target_velocity_m_s[j]) - velocity[j] for j in range(3)])
        terminal_attitude_error = _attitude_error_deg(q, target_q)
        terminal_rate = math.degrees(math.sqrt(_dot(omega, omega)))
        if (
            terminal_velocity_error <= VELOCITY_GATE_M_S
            and terminal_attitude_error <= ATTITUDE_GATE_DEG
            and terminal_rate <= RATE_GATE_DEG_S
        ):
            in_gate += DT_S
            if in_gate + 1e-12 >= HOLD_TIME_S:
                break
        else:
            in_gate = 0.0

    terminal_velocity_error = _norm([float(target_velocity_m_s[j]) - velocity[j] for j in range(3)])
    terminal_attitude_error = _attitude_error_deg(q, target_q)
    terminal_rate = math.degrees(math.sqrt(_dot(omega, omega)))
    passed = (
        in_gate + 1e-12 >= HOLD_TIME_S
        and terminal_velocity_error <= VELOCITY_GATE_M_S
        and terminal_attitude_error <= ATTITUDE_GATE_DEG
        and terminal_rate <= RATE_GATE_DEG_S
        and peak_force_fraction <= 1.0 + 1e-9
        and peak_torque_fraction <= 1.0 + 1e-9
    )
    return {
        "case": name,
        "failed_cluster": failed_cluster,
        "target_velocity_m_s": list(target_velocity_m_s),
        "terminal_velocity_m_s": velocity,
        "terminal_position_offset_m": position,
        "terminal_velocity_error_m_s": terminal_velocity_error,
        "target_attitude_axis": axis,
        "target_attitude_angle_deg": float(angle_deg),
        "terminal_attitude_error_deg": terminal_attitude_error,
        "terminal_body_rate_deg_s": terminal_rate,
        "duration_s": t,
        "force_limit_N": force_limit,
        "torque_limits_Nm": torque_limits,
        "peak_force_fraction": peak_force_fraction,
        "peak_torque_fraction": peak_torque_fraction,
        "mass_t": state["mass_t"],
        "center_of_mass_m": state["center_of_mass_m"],
        "inertia_tensor_kg_m2": tensor,
        "dynamics_model": "COUPLED_TRANSLATION_PLUS_FULL_RIGID_BODY_ROTATION",
        "translation_model": "NET_INERTIAL_FORCE_VELOCITY_TRACKING_WITH_FORCE_SATURATION",
        "rotation_model": "QUATERNION_PD_FULL_EULER_DYNAMICS_WITH_TORQUE_SATURATION",
        "pass": passed,
    }


def _qualify(cases: dict[str, dict[str, Any]], failed_cluster: str | None) -> dict[str, Any]:
    results = {
        name: simulate_coupled_case(name=name, failed_cluster=failed_cluster, **spec)
        for name, spec in cases.items()
    }
    return {"failed_cluster": failed_cluster, "cases": results, "all_cases_pass": all(x["pass"] for x in results.values())}


def build_coupled_local_flight_qualification() -> dict[str, Any]:
    nominal = _qualify(_NOMINAL_CASES, None)
    degraded = {cluster: _qualify(_DEGRADED_CASES, cluster) for cluster in "ABCD"}
    all_pass = nominal["all_cases_pass"] and all(x["all_cases_pass"] for x in degraded.values())
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "nominal": nominal,
        "one_cluster_out": degraded,
        "all_cases_pass": all_pass,
        "disposition": "COUPLED_TRANSLATION_ROTATION_NET_WRENCH_ENGINEERING_QUALIFIED" if all_pass else "COUPLED_TRANSLATION_ROTATION_NET_WRENCH_ENGINEERING_FAIL",
        "authority": {
            "coupled_translation_rotation_time_domain_simulated": True,
            "configuration_aware_mass_inertia_consumed": True,
            "net_force_torque_envelope_consumed": True,
            "mount_level_allocator_in_time_loop": False,
            "minimum_impulse_bit_certified": False,
            "plume_interference_certified": False,
            "structural_mount_loads_certified": False,
            "final_flight_software_certified": False,
            "final_thruster_hardware_certified": False,
            "canon_changed": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "remaining_open": [
            "mount_level_force_allocation_in_the_time_loop",
            "minimum_impulse_bit_and_valve_gimbal_dynamics",
            "finite_plume_and_external_hardware_interference",
            "structural_mount_loads",
        ],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_coupled_local_flight_qualification(), indent=2, sort_keys=True))
