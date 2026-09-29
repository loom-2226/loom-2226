import math

from src.wayfarer_mission_regression import (
    delta_v_from_propellant_km_s,
    reserve_after_burn_t,
    rocket_propellant_required_t,
)


def test_29_1kms_cruise_burn_is_about_16_7t_from_full_wet_mass():
    prop = rocket_propellant_required_t(1158.5, 29.1, 2000.0)
    assert 16.7 < prop < 16.8


def test_round_trip_delta_v_inverse():
    dv = 100.0
    ve = 2000.0
    m0 = 1158.5
    prop = rocket_propellant_required_t(m0, dv, ve)
    recovered = delta_v_from_propellant_km_s(m0, prop, ve)
    assert math.isclose(recovered, dv, rel_tol=1e-12)


def test_250t_at_cruise_gives_hundreds_of_kms_delta_v():
    dv = delta_v_from_propellant_km_s(1158.5, 250.0, 2000.0)
    assert 480.0 < dv < 490.0


def test_reserve_after_burn():
    assert reserve_after_burn_t(250.0, 16.75) == 233.25
