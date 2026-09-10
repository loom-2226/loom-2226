import math

from src.wayfarer_mass_properties import (
    angular_accel_rad_s2,
    bang_bang_slew_time_s,
    center_of_mass,
    point_mass_inertia_tensor,
    torque_from_thruster_pair,
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


def test_bang_bang_slew_scaling():
    t1 = bang_bang_slew_time_s(math.pi / 2.0, 0.01)
    t2 = bang_bang_slew_time_s(math.pi / 2.0, 0.04)
    assert math.isclose(t1 / t2, 2.0)
