from __future__ import annotations

"""Bounded numerical coarse/fine RCS qualification probe.

Pixel qualification proves the realization model is coupled into the real mount
allocator/time loop for one nominal and one degraded case. It deliberately does
NOT execute the wider exploratory parameter sweep.
"""

import math
from typing import Any, Sequence

from src.wayfarer_mass_inertia_authority import build_mass_inertia_state
from src.wayfarer_rcs_actuator_requirement_envelope import build_actuator_requirement_envelope
from src.wayfarer_rcs_closed_loop_gnc import (
    ATTITUDE_GATE_DEG, RATE_GATE_DEG_S, _attitude_error_deg, _axis_angle_q,
    _cross, _dot, _inv3, _matvec, _qmul, _qnorm, _torque_command,
)
from src.wayfarer_rcs_mount_allocator import MOUNT_THRUST_CAP_N, allocate_wrench
from src.wayfarer_rcs_time_domain_mount_coupling import (
    CONTROL_DT_S, HOLD_TIME_S, MAX_TIME_S, TRANSLATION_RESPONSE_RATE_S_INV,
    VELOCITY_GATE_M_S, _AXIS_INDEX, _CASES, _DEGRADED_FORCE_LIMIT_N,
    _DEGRADED_TORQUE_LIMITS, _NOMINAL_FORCE_LIMIT_N, _NOMINAL_TORQUE_LIMITS,
)

SCHEMA = "LOOM.Wayfarer.RCSCoarseFineAuthorityEnvelope"
SCHEMA_VERSION = "0.3"
PIXEL_QUALIFICATION_PARAMETERS = ((0.20, 0.50),)
# Bind directly to the canonical case identifiers owned by the coupled-flight module.
PIXEL_QUALIFICATION_CASES = (
    "NOMINAL_MIXED_TRANSLATION_ATTITUDE",
    "DEGRADED_MIXED_TRANSLATION_ATTITUDE_A",
)


def _norm(v: Sequence[float]) -> float:
    return math.sqrt(sum(float(x) * float(x) for x in v))


def _clip(v: list[float], limit: float) -> list[float]:
    n = _norm(v)
    if n <= limit or n <= 1e-12:
        return v
    return [float(x) * limit / n for x in v]


def _cross3(a: Sequence[float], b: Sequence[float]) -> list[float]:
    return [float(a[1])*float(b[2])-float(a[2])*float(b[1]),
            float(a[2])*float(b[0])-float(a[0])*float(b[2]),
            float(a[0])*float(b[1])-float(a[1])*float(b[0])]


def _realize_mount_wrench(commands: dict[str, Any], *, com: Sequence[float],
                           coarse_activation_fraction: float, fine_quantization_fraction: float,
                           trace_mib_upper_bound_ns: float) -> tuple[list[float], dict[str, float]]:
    threshold_n = coarse_activation_fraction * MOUNT_THRUST_CAP_N
    fine_quantum_n = fine_quantization_fraction * trace_mib_upper_bound_ns / CONTROL_DT_S
    wrench = [0.0] * 6
    coarse_total = fine_total = max_error = 0.0
    for command in commands.values():
        requested = max(0.0, float(command["commanded_thrust_N"]))
        direction = command["commanded_force_unit_ship"]
        if requested <= 1e-12 or direction is None:
            continue
        coarse = max(0.0, requested - threshold_n)
        fine_target = requested - coarse
        fine = round(fine_target / fine_quantum_n) * fine_quantum_n if fine_quantum_n > 0.0 else fine_target
        fine = max(0.0, min(threshold_n, fine))
        realized = min(MOUNT_THRUST_CAP_N, coarse + fine)
        coarse_total += coarse
        fine_total += fine
        max_error = max(max_error, abs(realized - requested))
        force = [realized * float(direction[i]) for i in range(3)]
        arm = [float(command["position_m"][i]) - float(com[i]) for i in range(3)]
        torque = _cross3(arm, force)
        for i in range(3):
            wrench[i] += force[i]
            wrench[i + 3] += torque[i]
    return wrench, {"coarse_total_impulse_Ns": coarse_total * CONTROL_DT_S,
                    "fine_total_impulse_Ns": fine_total * CONTROL_DT_S,
                    "max_mount_realization_error_N": max_error,
                    "fine_force_quantum_N": fine_quantum_n,
                    "coarse_activation_threshold_N": threshold_n}


def _simulate_case(name: str, spec: dict[str, Any], *, coarse_fraction: float,
                   fine_fraction: float, trace_mib_ns: float) -> dict[str, Any]:
    state = build_mass_inertia_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
    mass_kg = float(state["mass_t"]) * 1000.0
    com = state["center_of_mass_m"]
    tensor = state["inertia_tensor_kg_m2"]
    inv_i = _inv3(tensor)
    failed_cluster = spec["failed_cluster"]
    force_limit = _DEGRADED_FORCE_LIMIT_N if failed_cluster else _NOMINAL_FORCE_LIMIT_N
    torque_limits = dict(_DEGRADED_TORQUE_LIMITS if failed_cluster else _NOMINAL_TORQUE_LIMITS)
    target_velocity = [float(x) for x in spec["target_velocity_m_s"]]
    target_q = _axis_angle_q(_AXIS_INDEX[spec["axis"]], math.radians(float(spec["angle_deg"])))
    q, omega, velocity = [1.0, 0.0, 0.0, 0.0], [0.0] * 3, [0.0] * 3
    t = in_gate = max_error = coarse_impulse = fine_impulse = 0.0
    allocator_pass = True
    while t < MAX_TIME_S:
        vel_error = [target_velocity[j] - velocity[j] for j in range(3)]
        demanded_force = _clip([mass_kg * TRANSLATION_RESPONSE_RATE_S_INV * e for e in vel_error], force_limit)
        demanded_torque, _ = _torque_command(tensor, q, target_q, omega, torque_limits)
        allocation = allocate_wrench([*demanded_force, *demanded_torque], failed_cluster=failed_cluster)
        allocator_pass = allocator_pass and bool(allocation["pass"])
        if not allocation["pass"]:
            break
        achieved, telemetry = _realize_mount_wrench(allocation["mount_commands"], com=com,
            coarse_activation_fraction=coarse_fraction, fine_quantization_fraction=fine_fraction,
            trace_mib_upper_bound_ns=trace_mib_ns)
        max_error = max(max_error, telemetry["max_mount_realization_error_N"])
        coarse_impulse += telemetry["coarse_total_impulse_Ns"]
        fine_impulse += telemetry["fine_total_impulse_Ns"]
        force, torque = achieved[:3], achieved[3:]
        velocity = [velocity[j] + force[j] / mass_kg * CONTROL_DT_S for j in range(3)]
        iw = _matvec(tensor, omega)
        gyro = _cross(omega, iw)
        alpha = _matvec(inv_i, [torque[j] - gyro[j] for j in range(3)])
        omega = [omega[j] + alpha[j] * CONTROL_DT_S for j in range(3)]
        qdot = _qmul(q, [0.0, *omega])
        q = _qnorm([q[j] + 0.5 * qdot[j] * CONTROL_DT_S for j in range(4)])
        t += CONTROL_DT_S
        velocity_error = _norm([target_velocity[j] - velocity[j] for j in range(3)])
        attitude_error = _attitude_error_deg(q, target_q)
        body_rate = math.degrees(math.sqrt(_dot(omega, omega)))
        if velocity_error <= VELOCITY_GATE_M_S and attitude_error <= ATTITUDE_GATE_DEG and body_rate <= RATE_GATE_DEG_S:
            in_gate += CONTROL_DT_S
            if in_gate + 1e-12 >= HOLD_TIME_S:
                break
        else:
            in_gate = 0.0
    velocity_error = _norm([target_velocity[j] - velocity[j] for j in range(3)])
    attitude_error = _attitude_error_deg(q, target_q)
    body_rate = math.degrees(math.sqrt(_dot(omega, omega)))
    passed = allocator_pass and in_gate + 1e-12 >= HOLD_TIME_S and velocity_error <= VELOCITY_GATE_M_S and attitude_error <= ATTITUDE_GATE_DEG and body_rate <= RATE_GATE_DEG_S
    return {"pass": passed, "duration_s": t, "terminal_velocity_error_m_s": velocity_error,
            "terminal_attitude_error_deg": attitude_error, "terminal_body_rate_deg_s": body_rate,
            "max_mount_realization_error_N": max_error, "coarse_total_impulse_Ns": coarse_impulse,
            "fine_total_impulse_Ns": fine_impulse}


def build_coarse_fine_authority_envelope() -> dict[str, Any]:
    demand = build_actuator_requirement_envelope()["aggregate_sampled_actuator_demand"]
    trace_mib_ns = float(demand["sampled_exact_trace_mib_upper_bound_Ns"])
    rows = []
    for coarse_fraction, fine_fraction in PIXEL_QUALIFICATION_PARAMETERS:
        cases = {name: _simulate_case(name, _CASES[name], coarse_fraction=coarse_fraction,
                                      fine_fraction=fine_fraction, trace_mib_ns=trace_mib_ns)
                 for name in PIXEL_QUALIFICATION_CASES}
        rows.append({"coarse_activation_fraction": coarse_fraction,
                     "fine_quantization_fraction": fine_fraction,
                     "pass": all(case["pass"] for case in cases.values()), "cases": cases})
    probe_pass = all(row["pass"] for row in rows)
    return {
        "schema": SCHEMA, "schema_version": SCHEMA_VERSION,
        "status": "PASS" if probe_pass else "FAIL",
        "disposition": "COARSE_FINE_AUTHORITY_PIXEL_PROBE_QUALIFIED_HARDWARE_OPEN" if probe_pass else "COARSE_FINE_AUTHORITY_PIXEL_PROBE_FAILED",
        "parameter_contract": {"coarse_activation_parameter": "FRACTION_OF_CURRENT_MOUNT_THRUST_CAP",
            "fine_quantization_parameter": "FRACTION_OF_CURRENT_SAMPLED_EXACT_TRACE_MIB_UPPER_BOUND",
            "interpretation": "NUMERICAL_AUTHORITY_SPLIT_PROBE_NOT_HARDWARE_SPECIFICATION",
            "selected_hardware_threshold": False},
        "closed_loop_contract": {"allocator_location": "INSIDE_COUPLED_LOCAL_FLIGHT_TIME_LOOP",
            "state_advance_wrench": "REALIZED_COARSE_PLUS_FINE_MOUNT_WRENCH_ONLY",
            "sample_period_s": CONTROL_DT_S,
            "sample_period_authority": "NUMERICAL_QUALIFICATION_CADENCE_NOT_HARDWARE_BANDWIDTH",
            "pixel_cases": list(PIXEL_QUALIFICATION_CASES)},
        "exploration_contract": {"full_parameter_sweep_authority": "NOT_EXECUTED_BY_PIXEL_QUALIFICATION",
            "reason": "SEPARATE_EXPENSIVE_ENGINEERING_EXPLORATION_FROM_GOVERNED_INTERACTIVE_GATE",
            "qualification_claim": "BOUNDED_COUPLING_PROBE_ONLY"},
        "source_demand": {"sampled_exact_trace_mib_upper_bound_Ns": trace_mib_ns,
            "transition_series_identity": "QUALIFICATION_CASE_PLUS_MOUNT_ID"},
        "parameter_sweep": rows,
        "authority": {"coarse_fine_numerical_authority_envelope_qualified": False,
            "coarse_fine_pixel_coupling_probe_qualified": probe_pass,
            "final_thruster_hardware_certified": False, "minimum_impulse_bit_certified": False,
            "valve_dynamics_certified": False, "vectoring_mechanism_certified": False,
            "working_fluid_certified": False, "plume_interference_certified": False,
            "structural_mount_loads_certified": False, "canon_changed": False,
            "campaign_state_mutation": "ZERO", "llm_calculation_authority": "ZERO"},
        "remaining_open": ["execute_offline_coarse_fine_parameter_envelope_exploration",
            "select_evidence_backed_valve_response_mib_and_cycle_life_envelope",
            "select_and_validate_vectoring_mechanism_response_envelope",
            "select_rcs_working_fluid_and_exhaust_velocity",
            "finite_plume_and_external_hardware_interference", "structural_rcs_mount_loads"],
        "qualified_next_step": "EXECUTE_OFFLINE_COARSE_FINE_PARAMETER_ENVELOPE_EXPLORATION",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_coarse_fine_authority_envelope(), indent=2, sort_keys=True))
