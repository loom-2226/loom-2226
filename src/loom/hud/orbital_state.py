from __future__ import annotations

"""Deterministic Earth-centered osculating diagnostics for the HUD sandbox."""

import math
from typing import Any, Sequence

CONTRACT = "LOOM_HUD_ORBITAL_STATE_V1"
VISUAL_CONTRACT = "LOOM_HUD_ORBIT_VISUALIZATION_V1"
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


def _unit(v: Sequence[float]) -> tuple[float, float, float]:
    m = _mag(v)
    if m <= 1e-15:
        raise ValueError("cannot normalize zero vector")
    return tuple(float(x) / m for x in v)  # type: ignore[return-value]


def _scale(v: Sequence[float], s: float) -> tuple[float, float, float]:
    return tuple(float(x) * float(s) for x in v)  # type: ignore[return-value]


def _add(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    return tuple(float(a[i]) + float(b[i]) for i in range(3))  # type: ignore[return-value]


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

    operational_orbit = bool(
        classification == "BOUND_ELLIPTIC"
        and periapsis_altitude_km is not None
        and periapsis_altitude_km >= 0.0
        and ecc < 1.0
    )
    if operational_orbit:
        presentation_regime = "EARTH_ORBIT"
    elif classification == "ESCAPE_HYPERBOLIC":
        presentation_regime = "EARTH_ESCAPE"
    else:
        presentation_regime = "FREE_FLIGHT_OSCULATING"

    return {
        "contract": CONTRACT,
        "reference_body": "EARTH",
        "frame": "EARTH_CENTERED_INERTIAL",
        "classification": classification,
        "presentation_regime": presentation_regime,
        "operational_orbit": operational_orbit,
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


def earth_orbit_visualization(
    position_km: Sequence[float],
    velocity_km_s: Sequence[float],
    mu_km3_s2: float,
    *,
    samples: int = 128,
) -> dict[str, Any]:
    """Return server-derived osculating orbit geometry for presentation only.

    Geometry is emitted only for a bound orbit whose osculating periapsis stays
    above the Earth reference surface. Browser code renders these points but does
    not derive orbital mechanics itself.
    """
    if samples < 24 or samples > 720:
        raise ValueError("samples must be in 24..720")
    state = earth_orbital_state(position_km, velocity_km_s, mu_km3_s2)
    unavailable = {
        "contract": VISUAL_CONTRACT,
        "available": False,
        "authority": "QUALIFICATION_DERIVED_PRESENTATION_GEOMETRY",
        "navigation_grade": False,
        "points_earth_centered_km": [],
        "periapsis_position_earth_centered_km": None,
        "apoapsis_position_earth_centered_km": None,
    }
    if not state["operational_orbit"]:
        return unavailable

    r = tuple(float(x) for x in position_km)
    v = tuple(float(x) for x in velocity_km_s)
    mu = float(mu_km3_s2)
    h = _cross(r, v)
    hmag = _mag(h)
    if hmag <= 1e-12:
        return unavailable
    h_hat = _unit(h)
    rmag = _mag(r)
    vmag = _mag(v)
    rv = _dot(r, v)
    evec = tuple(((vmag * vmag - mu / rmag) * r[i] - rv * v[i]) / mu for i in range(3))
    ecc = _mag(evec)
    p_hat = _unit(evec) if ecc > 1e-10 else _unit(r)
    q_hat = _unit(_cross(h_hat, p_hat))
    p = hmag * hmag / mu

    points: list[list[float]] = []
    for i in range(samples + 1):
        theta = 2.0 * math.pi * i / samples
        denom = 1.0 + ecc * math.cos(theta)
        radius = p / denom
        direction = _add(_scale(p_hat, math.cos(theta)), _scale(q_hat, math.sin(theta)))
        points.append([float(x) for x in _scale(direction, radius)])

    peri_radius = p / (1.0 + ecc)
    apo_radius = p / (1.0 - ecc)
    return {
        "contract": VISUAL_CONTRACT,
        "available": True,
        "authority": "QUALIFICATION_DERIVED_PRESENTATION_GEOMETRY",
        "navigation_grade": False,
        "points_earth_centered_km": points,
        "periapsis_position_earth_centered_km": [float(x) for x in _scale(p_hat, peri_radius)],
        "apoapsis_position_earth_centered_km": [float(x) for x in _scale(p_hat, -apo_radius)],
    }
