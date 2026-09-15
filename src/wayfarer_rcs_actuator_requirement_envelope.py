from __future__ import annotations

"""Derive sampled actuator-demand bounds from qualified mount-resolved E1 flight.

This module does NOT select or certify actuator hardware. It replays the already
qualified mixed translation/attitude cases and records the physical mount commands
emitted by the current allocator. Transition metrics are computed only within one
continuous qualification case and mount series; separate case clocks are never
joined into an artificial actuator transition.
"""

import math
from collections import defaultdict
from typing import Any, Sequence

from src.wayfarer_mass_inertia_authority import build_mass_inertia_state
from src.wayfarer_rcs_closed_loop_gnc import (
    ATTITUDE_GATE_DEG, RATE_GATE_DEG_S, _attitude_error_deg, _axis_angle_q,
    _cross, _dot, _inv3, _matvec, _qmul, _qnorm, _torque_command,
)
from src.wayfarer_rcs_mount_allocator import allocate_wrench
from src.wayfarer_rcs_time_domain_mount_coupling import (
    CONTROL_DT_S, HOLD_TIME_S, MAX_TIME_S, TRANSLATION_RESPONSE_RATE_S_INV,
    VELOCITY_GATE_M_S, _AXIS_INDEX, _CASES, _DEGRADED_FORCE_LIMIT_N,
    _DEGRADED_TORQUE_LIMITS, _NOMINAL_FORCE_LIMIT_N, _NOMINAL_TORQUE_LIMITS,
)

SCHEMA = "LOOM.Wayfarer.RCSActuatorRequirementEnvelope"
SCHEMA_VERSION = "0.2"

REQUIREMENT_CONTRACT = {
    "source": "QUALIFIED_RCS_MOUNT_LEVEL_TIME_DOMAIN_COMMAND_HISTORY",
    "sample_cadence_source": "E1_NUMERICAL_QUALIFICATION_CADENCE",
    "transition_series_identity": "QUALIFICATION_CASE_PLUS_MOUNT_ID",
    "interpretation": "SAMPLED_DEMAND_REQUIREMENTS_NOT_HARDWARE_QUALIFICATION",
    "minimum_impulse_interpretation": "SMALLEST_NONZERO_THRUST_TIMES_SAMPLE_PERIOD_IS_AN_EXACT_TRACE_REPRODUCTION_UPPER_BOUND_ONLY",
    "gimbal_interpretation": "MAX_DIRECTION_STEP_DIVIDED_BY_SAMPLE_PERIOD_IS_A_ONE_SAMPLE_AVERAGE_SLEW_LOWER_BOUND_ONLY",
    "valve_interpretation": "THRUST_STEP_HISTORY_IS_DEMAND_EVIDENCE_NOT_VALVE_LATENCY_OR_BANDWIDTH_AUTHORITY",
    "gimbal_acceleration_derived": False,
    "hardware_selected": False,
}


def requirement_authority_contract() -> dict[str, Any]:
    return {"sampled_flight_demand_envelope_derivable": True, "minimum_impulse_bit_certified": False,
            "valve_dynamics_certified": False, "gimbal_dynamics_certified": False,
            "working_fluid_certified": False, "final_thruster_hardware_certified": False,
            "plume_interference_certified": False, "structural_mount_loads_certified": False,
            "canon_changed": False, "campaign_state_mutation": "ZERO", "llm_calculation_authority": "ZERO"}


def _norm(v: Sequence[float]) -> float:
    return math.sqrt(sum(float(x) * float(x) for x in v))


def _clip_vector(v: list[float], limit: float) -> list[float]:
    mag = _norm(v)
    if mag <= limit or mag <= 1e-12:
        return v
    scale = limit / mag
    return [float(x) * scale for x in v]


def _direction_step_deg(a: Sequence[float], b: Sequence[float]) -> float:
    na, nb = _norm(a), _norm(b)
    if na <= 1e-12 or nb <= 1e-12:
        return 0.0
    cosine = sum(float(a[i]) * float(b[i]) for i in range(3)) / (na * nb)
    return math.degrees(math.acos(max(-1.0, min(1.0, cosine))))


def summarize_mount_command_trace(trace: list[dict[str, Any]], *, sample_period_s: float) -> dict[str, Any]:
    if sample_period_s <= 0.0:
        raise ValueError("sample_period_s must be positive")
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    mount_ids: set[str] = set()
    for row in trace:
        mount_id = str(row["mount_id"])
        case_id = str(row.get("case", "UNSPECIFIED_CASE"))
        mount_ids.add(mount_id)
        grouped[(case_id, mount_id)].append(row)

    nonzero_impulses: list[float] = []
    max_thrust_step = max_direction_step = max_thrust = 0.0
    on_off_transitions = 0
    for rows in grouped.values():
        rows.sort(key=lambda x: float(x["t_s"]))
        previous: dict[str, Any] | None = None
        for row in rows:
            thrust = max(0.0, float(row["thrust_N"]))
            max_thrust = max(max_thrust, thrust)
            if thrust > 1e-12:
                nonzero_impulses.append(thrust * sample_period_s)
            if previous is not None:
                prev_thrust = max(0.0, float(previous["thrust_N"]))
                max_thrust_step = max(max_thrust_step, abs(thrust - prev_thrust))
                if (prev_thrust <= 1e-12) != (thrust <= 1e-12):
                    on_off_transitions += 1
                prev_dir, curr_dir = previous.get("force_unit"), row.get("force_unit")
                if prev_thrust > 1e-12 and thrust > 1e-12 and prev_dir is not None and curr_dir is not None:
                    max_direction_step = max(max_direction_step, _direction_step_deg(prev_dir, curr_dir))
            previous = row

    minimum_impulse = min(nonzero_impulses) if nonzero_impulses else 0.0
    return {"sample_period_s": float(sample_period_s), "mount_count_observed": len(mount_ids),
            "command_series_count": len(grouped), "command_samples": len(trace),
            "minimum_nonzero_sampled_impulse_Ns": minimum_impulse,
            "sampled_exact_trace_mib_upper_bound_Ns": minimum_impulse,
            "maximum_sampled_thrust_N": max_thrust, "maximum_sampled_thrust_step_N": max_thrust_step,
            "maximum_sampled_direction_step_deg": max_direction_step,
            "one_sample_average_direction_slew_lower_bound_deg_s": max_direction_step / sample_period_s,
            "on_off_transitions": on_off_transitions, "hardware_selected": False}


def _simulate_case_with_trace(*, name: str, target_velocity_m_s: list[float], axis: str, angle_deg: float,
                              failed_cluster: str | None) -> dict[str, Any]:
    state = build_mass_inertia_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
    mass_kg = float(state["mass_t"]) * 1000.0
    tensor, inv_i = state["inertia_tensor_kg_m2"], _inv3(state["inertia_tensor_kg_m2"])
    force_limit = _DEGRADED_FORCE_LIMIT_N if failed_cluster else _NOMINAL_FORCE_LIMIT_N
    torque_limits = dict(_DEGRADED_TORQUE_LIMITS if failed_cluster else _NOMINAL_TORQUE_LIMITS)
    target_q = _axis_angle_q(_AXIS_INDEX[axis], math.radians(angle_deg))
    q, omega, velocity, position = [1.0, 0.0, 0.0, 0.0], [0.0]*3, [0.0]*3, [0.0]*3
    t = in_gate = max_util = worst_residual = 0.0
    trace: list[dict[str, Any]] = []
    all_allocations_pass = True
    while t < MAX_TIME_S:
        vel_error = [float(target_velocity_m_s[j]) - velocity[j] for j in range(3)]
        demanded_force = _clip_vector([mass_kg * TRANSLATION_RESPONSE_RATE_S_INV * e for e in vel_error], force_limit)
        demanded_torque, _raw = _torque_command(tensor, q, target_q, omega, torque_limits)
        allocation = allocate_wrench([*demanded_force, *demanded_torque], failed_cluster=failed_cluster)
        all_allocations_pass = all_allocations_pass and bool(allocation["pass"])
        max_util = max(max_util, float(allocation["max_mount_utilization_fraction"]))
        worst_residual = max(worst_residual, float(allocation["relative_normalized_residual"]))
        if not allocation["pass"]: break
        for mount_id, command in allocation["mount_commands"].items():
            trace.append({"case": name, "t_s": t, "mount_id": mount_id,
                          "thrust_N": float(command["commanded_thrust_N"]),
                          "force_unit": command["commanded_force_unit_ship"]})
        achieved = allocation["achieved_wrench"]
        force = [float(achieved[k]) for k in ("FX", "FY", "FZ")]
        torque = [float(achieved[k]) for k in ("TX", "TY", "TZ")]
        velocity = [velocity[j] + force[j] / mass_kg * CONTROL_DT_S for j in range(3)]
        position = [position[j] + velocity[j] * CONTROL_DT_S for j in range(3)]
        iw = _matvec(tensor, omega); gyro = _cross(omega, iw)
        alpha = _matvec(inv_i, [torque[j] - gyro[j] for j in range(3)])
        omega = [omega[j] + alpha[j] * CONTROL_DT_S for j in range(3)]
        qdot = _qmul(q, [0.0, *omega]); q = _qnorm([q[j] + 0.5*qdot[j]*CONTROL_DT_S for j in range(4)])
        t += CONTROL_DT_S
        velocity_error = _norm([float(target_velocity_m_s[j]) - velocity[j] for j in range(3)])
        attitude_error = _attitude_error_deg(q, target_q); body_rate = math.degrees(math.sqrt(_dot(omega, omega)))
        if velocity_error <= VELOCITY_GATE_M_S and attitude_error <= ATTITUDE_GATE_DEG and body_rate <= RATE_GATE_DEG_S:
            in_gate += CONTROL_DT_S
            if in_gate + 1e-12 >= HOLD_TIME_S: break
        else: in_gate = 0.0
    velocity_error = _norm([float(target_velocity_m_s[j]) - velocity[j] for j in range(3)])
    attitude_error = _attitude_error_deg(q, target_q); body_rate = math.degrees(math.sqrt(_dot(omega, omega)))
    passed = all_allocations_pass and in_gate + 1e-12 >= HOLD_TIME_S and velocity_error <= VELOCITY_GATE_M_S and attitude_error <= ATTITUDE_GATE_DEG and body_rate <= RATE_GATE_DEG_S
    return {"case": name, "failed_cluster": failed_cluster, "duration_s": t, "pass": passed,
            "terminal_velocity_error_m_s": velocity_error, "terminal_attitude_error_deg": attitude_error,
            "terminal_body_rate_deg_s": body_rate, "max_mount_utilization_fraction": max_util,
            "worst_relative_normalized_residual": worst_residual, "trace": trace}


def build_actuator_requirement_envelope() -> dict[str, Any]:
    case_results = {name: _simulate_case_with_trace(name=name, **spec) for name, spec in _CASES.items()}
    all_pass = all(bool(result["pass"]) for result in case_results.values())
    all_trace: list[dict[str, Any]] = []; case_summaries: dict[str, Any] = {}
    for name, result in case_results.items():
        trace = list(result.pop("trace")); summary = summarize_mount_command_trace(trace, sample_period_s=CONTROL_DT_S)
        all_trace.extend(trace); case_summaries[name] = {**result, "sampled_actuator_demand": summary}
    aggregate = summarize_mount_command_trace(all_trace, sample_period_s=CONTROL_DT_S)
    return {"schema": SCHEMA, "schema_version": SCHEMA_VERSION, "status": "PASS" if all_pass else "FAIL",
            "disposition": "SAMPLED_ACTUATOR_DEMAND_ENVELOPE_DERIVED_HARDWARE_UNQUALIFIED" if all_pass else "ACTUATOR_DEMAND_ENVELOPE_DERIVATION_FAIL",
            "requirement_contract": dict(REQUIREMENT_CONTRACT), "cases": case_summaries,
            "aggregate_sampled_actuator_demand": aggregate, "authority": requirement_authority_contract(),
            "remaining_open": ["minimum_impulse_bit_hardware_value_and_discretized_closed_loop_validation",
                               "valve_latency_response_and_cycle_life_evidence",
                               "gimbal_slew_acceleration_settle_and_mechanism_evidence",
                               "rcs_working_fluid_and_final_exhaust_velocity",
                               "finite_plume_and_external_hardware_interference", "structural_rcs_mount_loads"],
            "qualified_next_step": "SELECT_OR_RESEARCH_ACTUATOR_ARCHITECTURE_AGAINST_DERIVED_SAMPLED_DEMAND_ENVELOPE"}


if __name__ == "__main__":
    import json
    print(json.dumps(build_actuator_requirement_envelope(), indent=2, sort_keys=True))
