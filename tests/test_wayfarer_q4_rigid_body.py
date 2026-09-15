from __future__ import annotations

import math

from src.wayfarer_q4_rigid_body import build_q4_rigid_body_state, evaluate_rcs_control_case


def test_reference_wet_state_closes_mass_and_has_finite_tensor():
    state = build_q4_rigid_body_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
    assert math.isclose(state["mass_t"], 1158.5, rel_tol=0.0, abs_tol=1e-9)
    diag = state["inertia_diag_kg_m2"]
    assert all(v > 0.0 for v in diag)
    assert state["model_quality"] == "ENGINEERING_BOUNDED_RIGID_BODY_APPROXIMATION"
    assert state["qualification_scope"] == "HUD_FINITE_ATTITUDE_TRANSITION"


def test_balanced_tank_depletion_preserves_near_zero_lateral_com():
    full = build_q4_rigid_body_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=False)
    depleted = build_q4_rigid_body_state(normal_remass_t=0.0, protected_water_t=50.0, launch_docked=False)
    assert abs(full["center_of_mass_m"][1]) < 1e-9
    assert abs(full["center_of_mass_m"][2]) < 1e-9
    assert abs(depleted["center_of_mass_m"][1]) < 1e-9
    assert abs(depleted["center_of_mass_m"][2]) < 1e-9


def test_launch_offset_changes_docked_com_but_not_mass_identity():
    docked = build_q4_rigid_body_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
    absent = build_q4_rigid_body_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=False)
    assert math.isclose(docked["mass_t"] - absent["mass_t"], 33.0, abs_tol=1e-9)
    assert docked["center_of_mass_m"][2] > absent["center_of_mass_m"][2]


def test_nominal_rcs_case_has_three_axis_control():
    state = build_q4_rigid_body_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
    control = evaluate_rcs_control_case(state, failed_cluster=None)
    assert control["three_axis_control_retained"] is True
    assert control["translation_control_retained"] is True
    assert control["pitch_yaw_torque_Nm"] > 0.0
    assert control["roll_torque_Nm"] > 0.0


def test_one_cluster_out_retains_degraded_three_axis_control():
    state = build_q4_rigid_body_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
    control = evaluate_rcs_control_case(state, failed_cluster="FORE_DORSAL")
    assert control["three_axis_control_retained"] is True
    assert control["translation_control_retained"] is True
    assert control["degraded"] is True
    assert control["pitch_yaw_torque_Nm"] < control["nominal_pitch_yaw_torque_Nm"]
    assert control["roll_torque_Nm"] < control["nominal_roll_torque_Nm"]


def test_unknown_cluster_fails_closed():
    state = build_q4_rigid_body_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
    try:
        evaluate_rcs_control_case(state, failed_cluster="NOT_A_CLUSTER")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown failed cluster must fail closed")
