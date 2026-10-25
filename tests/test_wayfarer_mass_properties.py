import math

from src.wayfarer_mass_properties import (
    angular_accel_rad_s2,
    bang_bang_slew_time_s,
    center_of_mass,
    homogeneous_cylinder_inertia,
    point_mass_inertia_tensor,
    torque_from_separated_couple,
    torque_from_thruster_pair,
    translation_accel_m_s2,
)


def test_center_of_mass_two_point_case():
    elems = [
        {"mass_t": 1.0, "x_m": 0.0, "y_m": 0.0, "z_m": 0.0},
        {"mass_t": 1.0, "x_m": 2.0, "y_m": 0.0, "z_m": 0.0},
    ]
    out = center_of_mass(elems)
    assert out["mass_kg"] == 2000.0
    assert out["com_m"] == (1.0, 0.0, 0.0)


def test_point_mass_inertia_flags_not_final():
    elems = [
        {"mass_t": 1.0, "x_m": -1.0, "y_m": 0.0, "z_m": 0.0},
        {"mass_t": 1.0, "x_m": 1.0, "y_m": 0.0, "z_m": 0.0},
    ]
    out = point_mass_inertia_tensor(elems)
    assert out["tensor_kg_m2"][0][0] == 0.0
    assert out["tensor_kg_m2"][1][1] == 2000.0
    assert out["tensor_kg_m2"][2][2] == 2000.0
    assert out["intrinsic_component_inertia_included"] is False
    assert out["qualification_status"] == "NOT_FINAL"


def test_thruster_pair_torque_and_angular_accel():
    torque = torque_from_thruster_pair(10_000.0, 4.0)
    assert torque == 80_000.0
    alpha = angular_accel_rad_s2(torque, 2_000_000.0)
    assert math.isclose(alpha, 0.04)


def test_separated_couple_25kn_at_40m_is_1mnm():
    assert torque_from_separated_couple(25_000.0, 40.0) == 1_000_000.0


def test_bang_bang_slew_scaling():
    t1 = bang_bang_slew_time_s(math.pi / 2.0, 0.01)
    t2 = bang_bang_slew_time_s(math.pi / 2.0, 0.04)
    assert math.isclose(t1 / t2, 2.0)


def test_wayfarer_reference_cylinder_envelope():
    out = homogeneous_cylinder_inertia(1_158_500.0, 57.0, 4.5)
    assert out["qualification_status"] == "NOT_FINAL"
    assert math.isclose(out["Ixx_kg_m2"], 11_729_812.5, rel_tol=1e-12)
    assert math.isclose(out["Iyy_kg_m2"], 319_528_781.25, rel_tol=1e-12)
    assert math.isclose(out["Izz_kg_m2"], 319_528_781.25, rel_tol=1e-12)


def test_100kn_translation_authority_at_reference_wet_mass():
    a = translation_accel_m_s2(100_000.0, 1_158_500.0)
    assert math.isclose(a, 0.08631851532153646, rel_tol=1e-12)


def test_reference_pitch_yaw_slew_sizing():
    inertia = homogeneous_cylinder_inertia(1_158_500.0, 57.0, 4.5)["Iyy_kg_m2"]
    torque = torque_from_separated_couple(25_000.0, 40.0)
    alpha = angular_accel_rad_s2(torque, inertia)
    assert math.isclose(alpha, 0.0031296085994631115, rel_tol=1e-12)
    assert 44.0 < bang_bang_slew_time_s(math.pi / 2.0, alpha) < 46.0
    assert 63.0 < bang_bang_slew_time_s(math.pi, alpha) < 64.0
