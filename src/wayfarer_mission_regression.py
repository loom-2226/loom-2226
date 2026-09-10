from __future__ import annotations

import math


def rocket_propellant_required_t(initial_mass_t: float, delta_v_km_s: float, exhaust_velocity_km_s: float) -> float:
    """Ideal Tsiolkovsky propellant requirement for one burn.

    This is a mission-regression primitive, not a full Navigator replacement.
    It assumes fixed effective exhaust velocity and no external force during burn.
    """
    if initial_mass_t <= 0:
        raise ValueError("initial_mass_t must be positive")
    if delta_v_km_s < 0:
        raise ValueError("delta_v_km_s must be non-negative")
    if exhaust_velocity_km_s <= 0:
        raise ValueError("exhaust_velocity_km_s must be positive")
    mass_ratio = math.exp(delta_v_km_s / exhaust_velocity_km_s)
    final_mass_t = initial_mass_t / mass_ratio
    return initial_mass_t - final_mass_t


def delta_v_from_propellant_km_s(initial_mass_t: float, propellant_t: float, exhaust_velocity_km_s: float) -> float:
    if initial_mass_t <= 0 or exhaust_velocity_km_s <= 0:
        raise ValueError("mass and exhaust velocity must be positive")
    if propellant_t < 0 or propellant_t >= initial_mass_t:
        raise ValueError("propellant_t must be >=0 and < initial mass")
    final_mass_t = initial_mass_t - propellant_t
    return exhaust_velocity_km_s * math.log(initial_mass_t / final_mass_t)


def reserve_after_burn_t(available_remass_t: float, burn_remass_t: float) -> float:
    if available_remass_t < 0 or burn_remass_t < 0:
        raise ValueError("remass values must be non-negative")
    return available_remass_t - burn_remass_t
