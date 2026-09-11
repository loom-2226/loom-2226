from __future__ import annotations

"""Qualification-only orbital sandbox adapters for the Earth-Moon HUD.

This module deliberately does not own gravity, propulsion, campaign persistence,
or Navigator targeting. It only seeds a physically consistent test state into the
existing realtime qualification session and derives display diagnostics from that
live state.
"""

import math
import time
from typing import Any

from loom.hud.orbital_state import EARTH_RADIUS_KM, earth_orbital_state

CONTRACT = "LOOM_HUD_ORBITAL_SANDBOX_V1"


def initialize_earth_circular_orbit(
    session: Any,
    *,
    altitude_km: float = 400.0,
    inclination_deg: float = 0.0,
) -> dict[str, Any]:
    """Seed the disposable qualification session into a circular Earth orbit.

    The state is Earth-centered inertial with position on +X and prograde velocity
    in the Y/Z plane. It mutates only the in-memory qualification session.
    """

    altitude_km = float(altitude_km)
    inclination_deg = float(inclination_deg)
    if not (160.0 <= altitude_km <= 100000.0):
        raise ValueError("qualification Earth orbit altitude must be in 160..100000 km")
    if not (0.0 <= inclination_deg <= 180.0):
        raise ValueError("inclination_deg must be in 0..180")
    mu = float(session.earth_mu)
    if mu <= 0.0:
        raise ValueError("Earth GM must be positive")

    radius_km = EARTH_RADIUS_KM + altitude_km
    circular_speed_km_s = math.sqrt(mu / radius_km)
    inc = math.radians(inclination_deg)
    position = (radius_km, 0.0, 0.0)
    velocity = (0.0, circular_speed_km_s * math.cos(inc), circular_speed_km_s * math.sin(inc))
    speed = math.sqrt(sum(x * x for x in velocity))
    nose = tuple(x / speed for x in velocity)

    with session.lock:
        session.ship_position = position
        session.ship_velocity = velocity
        session.nose_direction = nose
        session.torch_active = False
        session.status = "RUNNING"
        session.last_wall = time.monotonic()
        session.sandbox_state = "EARTH_CIRCULAR_ORBIT"
        session.sandbox_seed = {
            "altitude_km": altitude_km,
            "inclination_deg": inclination_deg,
            "reference_body": "EARTH",
            "authority": "QUALIFICATION_ONLY",
        }

    return {
        "contract": CONTRACT,
        "sandbox_state": "EARTH_CIRCULAR_ORBIT",
        "campaign_mutation": False,
        "authority": "QUALIFICATION_ONLY",
        "reference_body": "EARTH",
        "altitude_km": altitude_km,
        "inclination_deg": inclination_deg,
        "circular_speed_km_s": circular_speed_km_s,
    }


def attach_orbital_state(payload: dict[str, Any], session: Any) -> dict[str, Any]:
    """Attach deterministic osculating Earth-orbit diagnostics to a live payload."""

    stamped = dict(payload)
    orbit = earth_orbital_state(session.ship_position, session.ship_velocity, session.earth_mu)
    orbit["mu_source"] = session.earth_mu_source
    orbit["sandbox_state"] = getattr(session, "sandbox_state", "FREE_FLIGHT_QUALIFICATION")
    seed = getattr(session, "sandbox_seed", None)
    if seed is not None:
        orbit["sandbox_seed"] = dict(seed)
    stamped["orbital_state"] = orbit
    return stamped
