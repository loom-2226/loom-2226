"""Wayfarer torch/remass engineering helpers.

ENGINEERING QUALIFICATION ONLY. This module does not define canon.
It deliberately separates ideal momentum/energy closure from species-specific
conditioning and materials qualification.
"""

G0_M_S2 = 9.80665


def mode_closure(ship_mass_kg: float, acceleration_g: float, exhaust_velocity_km_s: float) -> dict:
    """Return ideal torch momentum/kinetic-power closure for one operating point.

    Species identity is intentionally absent. At fixed ship mass, acceleration,
    and exhaust velocity, ideal thrust and mass flow are determined before any
    species-specific conditioner/nozzle penalties are applied.
    """
    if ship_mass_kg <= 0:
        raise ValueError("ship_mass_kg must be positive")
    if acceleration_g <= 0:
        raise ValueError("acceleration_g must be positive")
    if exhaust_velocity_km_s <= 0:
        raise ValueError("exhaust_velocity_km_s must be positive")

    acceleration_m_s2 = acceleration_g * G0_M_S2
    exhaust_velocity_m_s = exhaust_velocity_km_s * 1000.0
    thrust_N = ship_mass_kg * acceleration_m_s2
    mdot_kg_s = thrust_N / exhaust_velocity_m_s
    jet_power_W = 0.5 * mdot_kg_s * exhaust_velocity_m_s**2

    return {
        "ship_mass_kg": ship_mass_kg,
        "acceleration_g": acceleration_g,
        "exhaust_velocity_km_s": exhaust_velocity_km_s,
        "thrust_MN": thrust_N / 1e6,
        "mdot_kg_s": mdot_kg_s,
        "remass_t_per_h": mdot_kg_s * 3600.0 / 1000.0,
        "jet_power_TW": jet_power_W / 1e12,
        "specific_jet_energy_GJ_per_kg": 0.5 * exhaust_velocity_m_s**2 / 1e9,
    }
