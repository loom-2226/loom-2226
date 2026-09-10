import math

from src.wayfarer_attitude_envelope import rate_limited_slew_time_s, build_hud_attitude_envelope


def test_rate_limited_slew_reduces_to_triangular_when_rate_not_reached():
    alpha = math.radians(0.2)
    out = rate_limited_slew_time_s(math.radians(10.0), alpha, math.radians(20.0))
    expected = 2.0 * math.sqrt(math.radians(10.0) / alpha)
    assert abs(out - expected) < 1e-9


def test_rate_limited_slew_uses_cruise_segment_when_rate_is_reached():
    alpha = math.radians(0.2)
    vmax = math.radians(2.0)
    out = rate_limited_slew_time_s(math.radians(90.0), alpha, vmax)
    assert out > 45.0
    assert out < 60.0


def test_hud_envelope_preserves_axis_specific_authority_and_degraded_case():
    env = build_hud_attitude_envelope()
    assert env["authority_status"] == "ENGINEERING_QUALIFICATION_CANDIDATE"
    assert env["inertia_model"]["final_intrinsic_tensor_available"] is False
    assert env["nominal"]["pitch"]["angular_accel_deg_s2"] < env["nominal"]["roll"]["angular_accel_deg_s2"]
    assert env["one_cluster_out"]["pitch"]["angular_accel_deg_s2"] < env["nominal"]["pitch"]["angular_accel_deg_s2"]
    assert env["one_cluster_out"]["pitch"]["slew_90_deg_s"] > env["nominal"]["pitch"]["slew_90_deg_s"]


def test_hud_envelope_carries_no_instantaneous_flip_claim():
    env = build_hud_attitude_envelope()
    assert env["instantaneous_attitude_transition_allowed"] is False
    assert env["nominal"]["pitch"]["slew_180_deg_s"] > 0.0
