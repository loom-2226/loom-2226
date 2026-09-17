import math

SIGMA = 5.670374419e-8


def radiative_rejection_W(area_m2: float, temperature_K: float = 900.0, emissivity: float = 0.9) -> float:
    return emissivity * SIGMA * area_m2 * temperature_K**4


def jet_power_W(thrust_N: float, exhaust_velocity_m_s: float) -> float:
    return 0.5 * thrust_N * exhaust_velocity_m_s


def conversion_heat_W(jet_power: float, efficiency: float) -> float:
    return jet_power * (1.0 / efficiency - 1.0)


def buffer_time_s(buffer_GJ: float, net_heat_MW: float) -> float:
    return buffer_GJ * 1000.0 / net_heat_MW


def test_3000_m2_radiator_is_about_100_MW_at_900K():
    q = radiative_rejection_W(3000.0)
    assert 100e6 < q < 101e6


def test_rcs_100kN_20kms_is_1GW_jet_power():
    assert jet_power_W(100_000.0, 20_000.0) == 1.0e9


def test_rcs_95_percent_conversion_heat():
    q = conversion_heat_W(1.0e9, 0.95)
    assert math.isclose(q, 52_631_578.94736842, rel_tol=1e-12)


def test_60GJ_buffer_at_100MW_net_last_600s():
    assert buffer_time_s(60.0, 100.0) == 600.0


def test_50MW_torch_heat_is_ppm_scale_at_12_78TW():
    fraction = 50e6 / 12.78e12
    assert 3.9e-6 < fraction < 4.0e-6
