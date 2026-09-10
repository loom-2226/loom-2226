import math

from src.wayfarer_power_thermal import (
    conversion_waste_heat_W,
    coupling_fraction,
    kinetic_jet_power_W,
    radiator_area_m2,
    radiative_flux_W_m2,
)


def test_900k_blackbody_flux():
    flux = radiative_flux_W_m2(900.0)
    assert math.isclose(flux, 37200.8577, rel_tol=1e-5)


def test_50mw_radiator_area_at_900k_e09():
    area = radiator_area_m2(50e6, 900.0, 0.9)
    assert 1490.0 < area < 1500.0


def test_rcs_power_scaling():
    assert math.isclose(kinetic_jet_power_W(25_000.0, 20_000.0), 250e6)
    assert math.isclose(kinetic_jet_power_W(25_000.0, 50_000.0), 625e6)
    assert math.isclose(kinetic_jet_power_W(25_000.0, 100_000.0), 1.25e9)


def test_efficiency_waste_heat():
    waste = conversion_waste_heat_W(1e9, 0.9)
    assert math.isclose(waste, 111_111_111.11111116, rel_tol=1e-12)


def test_torch_coupling_fraction_is_tiny_for_100mw_heat():
    frac = coupling_fraction(100e6, 12e12)
    assert frac < 1e-5
