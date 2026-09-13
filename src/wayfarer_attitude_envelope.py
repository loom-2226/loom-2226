from __future__ import annotations

import math


REFERENCE_WET_MASS_KG = 1_158_500.0
PITCH_YAW_DESIGN_INERTIA_KG_M2 = 320_000_000.0
ROLL_DESIGN_INERTIA_KG_M2 = 12_000_000.0
RCS_UNIT_THRUST_N = 25_000.0
PITCH_YAW_COUPLE_SEPARATION_M = 40.0
ROLL_EFFECTIVE_ARM_M = 4.0


def rate_limited_slew_time_s(angle_rad: float, angular_accel_rad_s2: float, max_rate_rad_s: float) -> float:
    """Minimum symmetric rest-to-rest slew with acceleration and rate limits.

    This is a kinematic envelope for qualification, not a closed-loop attitude-control law.
    """
    if angle_rad < 0:
        raise ValueError("angle_rad must be non-negative")
    if angular_accel_rad_s2 <= 0 or max_rate_rad_s <= 0:
        raise ValueError("angular acceleration and rate limit must be positive")
    if angle_rad == 0:
        return 0.0
    t_to_rate = max_rate_rad_s / angular_accel_rad_s2
    accel_decel_angle = angular_accel_rad_s2 * t_to_rate * t_to_rate
    if angle_rad <= accel_decel_angle:
        return 2.0 * math.sqrt(angle_rad / angular_accel_rad_s2)
    cruise_angle = angle_rad - accel_decel_angle
    return 2.0 * t_to_rate + cruise_angle / max_rate_rad_s


def _axis_card(*, inertia: float, torque: float, rate_deg_s: float, settle_s: float) -> dict:
    alpha = torque / inertia
    alpha_deg = math.degrees(alpha)
    rate = math.radians(rate_deg_s)
    return {
        "design_inertia_kg_m2": inertia,
        "available_torque_Nm": torque,
        "angular_accel_rad_s2": alpha,
        "angular_accel_deg_s2": alpha_deg,
        "max_slew_rate_deg_s": rate_deg_s,
        "settle_allowance_s": settle_s,
        "slew_90_deg_s": rate_limited_slew_time_s(math.radians(90.0), alpha, rate) + settle_s,
        "slew_180_deg_s": rate_limited_slew_time_s(math.radians(180.0), alpha, rate) + settle_s,
    }


def build_hud_attitude_envelope() -> dict:
    """Return the Q4 HUD-facing candidate control envelope.

    The inertia values are deliberately conservative design surrogates until the
    component intrinsic tensor closes. The object exists so HUD/local-flight can
    replace instantaneous flips with bounded transitions without becoming the
    engineering authority.
    """
    pitch_yaw_torque = RCS_UNIT_THRUST_N * PITCH_YAW_COUPLE_SEPARATION_M
    roll_torque = 2.0 * RCS_UNIT_THRUST_N * ROLL_EFFECTIVE_ARM_M
    degraded_pitch_yaw_torque = 0.5 * pitch_yaw_torque
    degraded_roll_torque = 0.5 * roll_torque
    nominal = {
        "pitch": _axis_card(inertia=PITCH_YAW_DESIGN_INERTIA_KG_M2, torque=pitch_yaw_torque, rate_deg_s=3.0, settle_s=8.0),
        "yaw": _axis_card(inertia=PITCH_YAW_DESIGN_INERTIA_KG_M2, torque=pitch_yaw_torque, rate_deg_s=3.0, settle_s=8.0),
        "roll": _axis_card(inertia=ROLL_DESIGN_INERTIA_KG_M2, torque=roll_torque, rate_deg_s=6.0, settle_s=8.0),
    }
    degraded = {
        "pitch": _axis_card(inertia=PITCH_YAW_DESIGN_INERTIA_KG_M2, torque=degraded_pitch_yaw_torque, rate_deg_s=1.5, settle_s=12.0),
        "yaw": _axis_card(inertia=PITCH_YAW_DESIGN_INERTIA_KG_M2, torque=degraded_pitch_yaw_torque, rate_deg_s=1.5, settle_s=12.0),
        "roll": _axis_card(inertia=ROLL_DESIGN_INERTIA_KG_M2, torque=degraded_roll_torque, rate_deg_s=3.0, settle_s=12.0),
    }
    return {
        "contract": "WAYFARER_HUD_ATTITUDE_ENVELOPE_V0.3",
        "authority_status": "ENGINEERING_QUALIFICATION_CANDIDATE",
        "canon_status": "NON_CANON",
        "reference_mass_kg": REFERENCE_WET_MASS_KG,
        "instantaneous_attitude_transition_allowed": False,
        "inertia_model": {
            "pitch_yaw_design_inertia_kg_m2": PITCH_YAW_DESIGN_INERTIA_KG_M2,
            "roll_design_inertia_kg_m2": ROLL_DESIGN_INERTIA_KG_M2,
            "model_quality": "CONSERVATIVE_DESIGN_ENVELOPE",
            "final_intrinsic_tensor_available": False,
        },
        "actuator_model": {
            "rcs_unit_thrust_N": RCS_UNIT_THRUST_N,
            "pitch_yaw_couple_separation_m": PITCH_YAW_COUPLE_SEPARATION_M,
            "roll_effective_arm_m": ROLL_EFFECTIVE_ARM_M,
            "fine_pointing": "INTERNAL_MOMENTUM_STORAGE",
            "large_angle_transition": "DISTRIBUTED_RCS_COUPLES",
        },
        "nominal": nominal,
        "one_cluster_out": degraded,
        "hud_usage": {
            "may_bound_attitude_transition_time": True,
            "may_replace_instantaneous_flip_qualification_assumption": True,
            "may_claim_closed_loop_control_law": False,
            "may_claim_final_actuator_canon": False,
        },
        "open_gates": [
            "component_intrinsic_inertia_tensor",
            "final_rcs_station_and_plume_interference_matrix",
            "closed_loop_settling_and_pointing_qualification",
        ],
    }
