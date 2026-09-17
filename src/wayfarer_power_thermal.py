from __future__ import annotations

SIGMA_SB = 5.670374419e-8


def radiative_flux_W_m2(temperature_K: float, emissivity: float = 1.0) -> float:
    if temperature_K <= 0:
        raise ValueError("temperature_K must be positive")
    if not 0 < emissivity <= 1:
        raise ValueError("emissivity must be in (0, 1]")
    return emissivity * SIGMA_SB * temperature_K ** 4


def radiator_area_m2(waste_heat_W: float, temperature_K: float, emissivity: float = 1.0) -> float:
    if waste_heat_W < 0:
        raise ValueError("waste_heat_W must be non-negative")
    return waste_heat_W / radiative_flux_W_m2(temperature_K, emissivity)


def kinetic_jet_power_W(thrust_N: float, exhaust_velocity_m_s: float) -> float:
    if thrust_N < 0 or exhaust_velocity_m_s < 0:
        raise ValueError("thrust and exhaust velocity must be non-negative")
    return 0.5 * thrust_N * exhaust_velocity_m_s


def conversion_waste_heat_W(output_power_W: float, efficiency: float) -> float:
    if output_power_W < 0:
        raise ValueError("output_power_W must be non-negative")
    if not 0 < efficiency <= 1:
        raise ValueError("efficiency must be in (0, 1]")
    input_power = output_power_W / efficiency
    return input_power - output_power_W


def coupling_fraction(waste_heat_W: float, source_power_W: float) -> float:
    if waste_heat_W < 0 or source_power_W <= 0:
        raise ValueError("invalid powers")
    return waste_heat_W / source_power_W
