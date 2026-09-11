from __future__ import annotations

"""Deterministic Earth-centered osculating diagnostics for the HUD sandbox."""

import math
from typing import Any, Sequence

CONTRACT = "LOOM_HUD_ORBITAL_STATE_V1"
EARTH_RADIUS_KM = 6378.137


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(a[i]) * float(b[i]) for i in range(3))


def _cross(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    return (
        float(a[1]) * float(b[2]) - float(a[2]) * float(b[1]),
        float(a[2]) * float(b[0]) - float(a[0]) * float(b[2]),
        float(a[0]) * float(b[1]) - float(a[1]) * float(b[0]),
    )


def _mag(v: Sequence[float]) -> float:
    return math.sqrt(_dot(v, v))


def earth_orbital_state(position_km: Sequence[float], velocity_km_s: Sequence[float], mu_km3_s2: float) -> dict[str, Any]:
    if len(position_km) != 3 or len(velocity_km_s) != 3:
        raise ValueError("position and velocity must be three-vectors")
    mu = float(mu_km3_s2)
    if mu <= 0:
        raise ValueError("mu_km3_s2 must be positive")
    r = tuple(float(x) for x in position_km)
    v = tuple(float(x) for x in velocity_km_s)
    rmag = _mag(r)
    vmag = _mag(v)
    if rmag <= 0:
        raise ValueError("position magnitude must be positive")

    h = _cross(r, v)
    hmag = _mag(h)
    energy = 0.5 * vmag * vmag - mu / rmag
    rv = _dot(r, v)
    evec = tuple(((vmag * vmag - mu / rmag) * r[i] - rv * v[i]) / mu for i in range(3))
    ecc = _mag(evec)
    inclination_deg = None if hmag <= 1e-12 else math.degrees(math.acos(max(-1.0, min(1.0, h[2] / hmag))))

    semimajor_km = None
    period_s = None
    periapsis_altitude_km = None
    apoapsis_altitude_km = None
    classification = "PARABOLIC_OR_DEGENERATE"

    if abs(energy) > 1e-15:
        semimajor_km = -mu / (2.0 * energy)
    if hmag <= 1e-12:
        classification = "DEGENERATE_RADIAL"
    elif energy < 0 and semimajor_km is not None:
        classification = "BOUND_ELLIPTIC"
        periapsis_altitude_km = semimajor_km * (1.0 - ecc) - EARTH_RADIUS_KM
        apoapsis_altitude_km = semimajor_km * (1.0 + ecc) - EARTH_RADIUS_KM
        period_s = 2.0 * math.pi * math.sqrt(semimajor_km ** 3 / mu)
    elif energy > 0:
        classification = "ESCAPE_HYPERBOLIC"

    return {
        "contract": CONTRACT,
        "reference_body": "EARTH",
        "frame": "EARTH_CENTERED_INERTIAL",
        "classification": classification,
        "radius_km": rmag,
        "altitude_km": rmag - EARTH_RADIUS_KM,
        "speed_km_s": vmag,
        "specific_orbital_energy_km2_s2": energy,
        "specific_angular_momentum_km2_s": hmag,
        "eccentricity": ecc,
        "inclination_deg": inclination_deg,
        "semimajor_axis_km": semimajor_km,
        "periapsis_altitude_km": periapsis_altitude_km,
        "apoapsis_altitude_km": apoapsis_altitude_km,
        "period_s": period_s,
        "navigation_grade": False,
        "authority": "QUALIFICATION_DERIVED_DISPLAY_STATE",
    }
