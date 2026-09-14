from __future__ import annotations

"""Closed-loop Wayfarer RCS attitude-control engineering qualification.

This model closes the gap between the recovered Q4 torque envelope and an actual
rigid-body response. It uses quaternion attitude, body angular velocity, the full
configuration-aware inertia tensor, Euler rotational dynamics and axis-saturated
RCS torque authority. It remains an engineering qualification model rather than
final flight software or final actuator hardware authority.
"""

import math
from typing import Any, Sequence

from src.wayfarer_mass_inertia_authority import build_mass_inertia_state

SCHEMA = "LOOM.Wayfarer.RCSClosedLoopGNC"
SCHEMA_VERSION = "0.1"
DT_S = 0.05
MAX_TIME_S = 240.0
HOLD_TIME_S = 2.0
ATTITUDE_GATE_DEG = 0.25
RATE_GATE_DEG_S = 0.05
NATURAL_FREQUENCY_RAD_S = 0.12
DAMPING_RATIO = 0.90

_NOMINAL_LIMITS = {"roll": 200_000.0, "pitch": 1_000_000.0, "yaw": 1_000_000.0}
_DEGRADED_LIMITS = {"roll": 100_000.0, "pitch": 750_000.0, "yaw": 750_000.0}
_AXIS_INDEX = {"roll": 0, "pitch": 1, "yaw": 2}


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(a[i]) * float(b[i]) for i in range(len(a)))


def _cross(a: Sequence[float], b: Sequence[float]) -> list[float]:
    return [
        float(a[1]) * float(b[2]) - float(a[2]) * float(b[1]),
        float(a[2]) * float(b[0]) - float(a[0]) * float(b[2]),
        float(a[0]) * float(b[1]) - float(a[1]) * float(b[0]),
    ]


def _matvec(m: Sequence[Sequence[float]], v: Sequence[float]) -> list[float]:
    return [sum(float(m[i][j]) * float(v[j]) for j in range(3)) for i in range(3)]


def _inv3(m: Sequence[Sequence[float]]) -> list[list[float]]:
    a, b, c = (float(x) for x in m[0])
    d, e, f = (float(x) for x in m[1])
    g, h, i = (float(x) for x in m[2])
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    if abs(det) <= 1e-18:
        raise ValueError("singular inertia tensor")
    return [
        [(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det],
        [(f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det],
        [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det],
    ]


def _qmul(a: Sequence[float], b: Sequence[float]) -> list[float]:
    aw, ax, ay, az = (float(x) for x in a)
    bw, bx, by, bz = (float(x) for x in b)
    return [
        aw * bw - ax * bx - ay * by - az * bz,
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
    ]


def _qconj(q: Sequence[float]) -> list[float]:
    return [float(q[0]), -float(q[1]), -float(q[2]), -float(q[3])]


def _qnorm(q: Sequence[float]) -> list[float]:
    n = math.sqrt(sum(float(x) * float(x) for x in q))
    if n <= 0.0:
        raise ValueError("zero quaternion")
    return [float(x) / n for x in q]


def _axis_angle_q(axis_index: int, angle_rad: float) -> list[float]:
    v = [0.0, 0.0, 0.0]
    v[axis_index] = math.sin(angle_rad / 2.0)
    return [math.cos(angle_rad / 2.0), *v]


def _error_rotvec_body(current_q: Sequence[float], target_q: Sequence[float]) -> list[float]:
    # Relative target attitude expressed from current/body orientation.
    qerr = _qnorm(_qmul(_qconj(current_q), target_q))
    if qerr[0] < 0.0:
        qerr = [-x for x in qerr]
    w = max(-1.0, min(1.0, qerr[0]))
    angle = 2.0 * math.acos(w)
    s = math.sqrt(max(0.0, 1.0 - w * w))
    if s < 1e-10 or angle < 1e-10:
        return [0.0, 0.0, 0.0]
    return [angle * qerr[k] / s for k in (1, 2, 3)]


def _attitude_error_deg(current_q: Sequence[float], target_q: Sequence[float]) -> float:
    qerr = _qnorm(_qmul(_qconj(current_q), target_q))
    return math.degrees(2.0 * math.acos(max(-1.0, min(1.0, abs(qerr[0])))))


def _clip(value: float, limit: float) -> float:
    return max(-limit, min(limit, value))


def _torque_command(
    tensor: Sequence[Sequence[float]],
    q: Sequence[float],
    target_q: Sequence[float],
    omega: Sequence[float],
    limits: dict[str, float],
) -> tuple[list[float], list[float]]:
    err = _error_rotvec_body(q, target_q)
    kp = NATURAL_FREQUENCY_RAD_S**2
    kd = 2.0 * DAMPING_RATIO * NATURAL_FREQUENCY_RAD_S
    alpha_cmd = [kp * err[j] - kd * float(omega[j]) for j in range(3)]
    iw = _matvec(tensor, omega)
    gyro = _cross(omega, iw)
    raw = [x + y for x, y in zip(_matvec(tensor, alpha_cmd), gyro)]
    axis_limits = [limits["roll"], limits["pitch"], limits["yaw"]]
    return [_clip(raw[j], axis_limits[j]) for j in range(3)], raw


def simulate_axis_slew(
    axis: str,
    angle_deg: float,
    *,
    failed_cluster: str | None = None,
    normal_remass_t: float = 250.0,
    protected_water_t: float = 50.0,
    launch_docked: bool = True,
) -> dict[str, Any]:
    if axis not in _AXIS_INDEX:
        raise ValueError(f"unknown axis: {axis}")
    if angle_deg <= 0.0 or angle_deg > 180.0:
        raise ValueError("angle_deg must be in (0, 180]")
    if failed_cluster is not None and failed_cluster not in "ABCD":
        raise ValueError("failed_cluster must be A, B, C, D or None")

    state = build_mass_inertia_state(
        normal_remass_t=normal_remass_t,
        protected_water_t=protected_water_t,
        launch_docked=launch_docked,
    )
    tensor = state["inertia_tensor_kg_m2"]
    inv_i = _inv3(tensor)
    limits = dict(_DEGRADED_LIMITS if failed_cluster else _NOMINAL_LIMITS)
    target_q = _axis_angle_q(_AXIS_INDEX[axis], math.radians(angle_deg))
    q = [1.0, 0.0, 0.0, 0.0]
    omega = [0.0, 0.0, 0.0]

    t = 0.0
    in_gate_time = 0.0
    peak_fraction = 0.0
    peak_rate = 0.0
    saturated_steps = 0
    steps = 0
    while t < MAX_TIME_S:
        torque, raw = _torque_command(tensor, q, target_q, omega, limits)
        axis_limits = [limits["roll"], limits["pitch"], limits["yaw"]]
        fraction = max(abs(torque[j]) / axis_limits[j] for j in range(3))
        peak_fraction = max(peak_fraction, fraction)
        if any(abs(raw[j]) > axis_limits[j] + 1e-9 for j in range(3)):
            saturated_steps += 1

        iw = _matvec(tensor, omega)
        rhs = [torque[j] - _cross(omega, iw)[j] for j in range(3)]
        alpha = _matvec(inv_i, rhs)
        omega = [omega[j] + alpha[j] * DT_S for j in range(3)]
        peak_rate = max(peak_rate, math.sqrt(_dot(omega, omega)))

        qdot = _qmul(q, [0.0, *omega])
        q = _qnorm([q[j] + 0.5 * qdot[j] * DT_S for j in range(4)])
        t += DT_S
        steps += 1

        err_deg = _attitude_error_deg(q, target_q)
        rate_deg_s = math.degrees(math.sqrt(_dot(omega, omega)))
        if err_deg <= ATTITUDE_GATE_DEG and rate_deg_s <= RATE_GATE_DEG_S:
            in_gate_time += DT_S
            if in_gate_time + 1e-12 >= HOLD_TIME_S:
                break
        else:
            in_gate_time = 0.0

    terminal_error = _attitude_error_deg(q, target_q)
    terminal_rate = math.degrees(math.sqrt(_dot(omega, omega)))
    passed = (
        in_gate_time + 1e-12 >= HOLD_TIME_S
        and terminal_error <= ATTITUDE_GATE_DEG
        and terminal_rate <= RATE_GATE_DEG_S
        and peak_fraction <= 1.0 + 1e-9
    )
    return {
        "case": f"{axis.upper()}_{int(angle_deg)}_DEG",
        "axis": axis,
        "command_angle_deg": float(angle_deg),
        "failed_cluster": failed_cluster,
        "duration_s": t,
        "terminal_attitude_error_deg": terminal_error,
        "terminal_rate_deg_s": terminal_rate,
        "peak_body_rate_deg_s": math.degrees(peak_rate),
        "peak_torque_fraction": peak_fraction,
        "saturated_step_fraction": saturated_steps / max(steps, 1),
        "torque_limit_Nm": limits,
        "inertia_tensor_kg_m2": tensor,
        "center_of_mass_m": state["center_of_mass_m"],
        "mass_t": state["mass_t"],
        "integration_step_s": DT_S,
        "terminal_hold_gate_s": HOLD_TIME_S,
        "attitude_gate_deg": ATTITUDE_GATE_DEG,
        "rate_gate_deg_s": RATE_GATE_DEG_S,
        "dynamics_model": "FULL_RIGID_BODY_EULER_PLUS_QUATERNION_KINEMATICS",
        "controller_model": "QUATERNION_ERROR_PD_WITH_GYROSCOPIC_FEEDFORWARD_AND_AXIS_TORQUE_SATURATION",
        "pass": passed,
    }


def qualify_attitude_cases(*, failed_cluster: str | None) -> dict[str, Any]:
    cases: dict[str, Any] = {}
    for axis in ("roll", "pitch", "yaw"):
        for angle in (90.0, 180.0):
            result = simulate_axis_slew(axis, angle, failed_cluster=failed_cluster)
            cases[result["case"]] = result
    all_pass = all(case["pass"] for case in cases.values())
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "failed_cluster": failed_cluster,
        "cases": cases,
        "all_cases_pass": all_pass,
        "qualification_scope": "REFERENCE_WET_DOCKED_FIXED_AXIS_ATTITUDE_COMMANDS",
        "authority": {
            "closed_loop_rigid_body_attitude_response_simulated": True,
            "full_inertia_tensor_consumed": True,
            "actuator_torque_envelope_recovered_from_pr96": True,
            "final_flight_software_certified": False,
            "final_thruster_hardware_certified": False,
            "minimum_impulse_bit_certified": False,
            "plume_interference_certified": False,
            "canon_changed": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
    }


def build_closed_loop_gnc_qualification() -> dict[str, Any]:
    nominal = qualify_attitude_cases(failed_cluster=None)
    degraded = {cluster: qualify_attitude_cases(failed_cluster=cluster) for cluster in "ABCD"}
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "nominal": nominal,
        "one_cluster_out": degraded,
        "all_cases_pass": nominal["all_cases_pass"] and all(x["all_cases_pass"] for x in degraded.values()),
        "disposition": "CLOSED_LOOP_RCS_ATTITUDE_ENGINEERING_RESPONSE_QUALIFIED" if nominal["all_cases_pass"] and all(x["all_cases_pass"] for x in degraded.values()) else "CLOSED_LOOP_RCS_ATTITUDE_ENGINEERING_RESPONSE_FAIL",
        "remaining_open": [
            "mount_level_force_allocation_in_the_time_loop",
            "minimum_impulse_bit_and_valve_gimbal_dynamics",
            "finite_plume_and_external_hardware_interference",
            "structural_mount_loads",
            "translation_plus_rotation_coupled_maneuvers",
        ],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_closed_loop_gnc_qualification(), indent=2, sort_keys=True))
