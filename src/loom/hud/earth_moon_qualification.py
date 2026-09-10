from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import math
import os

from loom.runtime import resolve_runtime_roots
from loom.spatial.celestial_state import propagate_parent_centric
from loom.spatial.sqlite_celestial_catalog import SQLiteCelestialCatalog

CONTRACT = "LOOM_HUD_EARTH_MOON_QUALIFICATION_V1"
DEFAULT_EPOCH = "2026-09-10T00:00:00Z"
EARTH_ID = "EA"
MOON_ID = "LU"


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_epoch(value: str) -> datetime:
    probe = value[:-1] + "+00:00" if value.endswith("Z") else value
    dt = datetime.fromisoformat(probe)
    if dt.tzinfo is None:
        raise ValueError("qualification epoch must include timezone")
    dt = dt.astimezone(timezone.utc)
    if dt.year != 2026:
        raise ValueError("Earth-Moon qualification epoch must be in 2026")
    return dt


def _norm(v: tuple[float, float, float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def _unit(v: tuple[float, float, float]) -> tuple[float, float, float]:
    n = _norm(v)
    if n <= 0.0:
        raise ValueError("zero vector cannot define camera axis")
    return tuple(x / n for x in v)


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def build_earth_moon_qualification(
    *,
    epoch_utc: str = DEFAULT_EPOCH,
    days: int = 30,
    data_root: Path | str | None = None,
) -> dict:
    """Build a read-only Earth-centered qualification scene from stored LOOM data.

    Moon motion is propagated from the nearest stored genuine navigation-grade
    parent-centric ephemeris anchor using the existing two-body osculating
    propagator. The result remains DERIVED / QUALIFICATION_ONLY and is never
    promoted to navigation authority. The observer is frozen at 50% of the
    initial Earth->Moon vector in the Earth-centered inertial frame.
    """
    start = _parse_epoch(epoch_utc)
    if not 1 <= int(days) <= 60:
        raise ValueError("days must be in 1..60")

    roots = resolve_runtime_roots(data_root=data_root)
    db_path = Path(os.environ.get("LOOM_SPATIAL_DB") or (roots.data_root / "LOOM_2226.sqlite3"))
    catalog = SQLiteCelestialCatalog(db_path)
    model = catalog.orbit_model_from_direct_anchor(MOON_ID, _iso(start))

    moon0, moonv0 = propagate_parent_centric(model, _iso(start))
    observer = tuple(0.5 * x for x in moon0)
    observer_velocity = (0.0, 0.0, 0.0)

    forward = _unit(tuple(moon0[i] - observer[i] for i in range(3)))
    global_up = (0.0, 0.0, 1.0)
    right_raw = _cross(global_up, forward)
    if _norm(right_raw) < 1e-9:
        global_up = (0.0, 1.0, 0.0)
        right_raw = _cross(global_up, forward)
    right = _unit(right_raw)
    up = _unit(_cross(forward, right))

    samples = []
    for day in range(int(days) + 1):
        epoch = _iso(start + timedelta(days=day))
        moon_p, moon_v = propagate_parent_centric(model, epoch)
        rel = tuple(moon_p[i] - observer[i] for i in range(3))
        rel_v = tuple(moon_v[i] - observer_velocity[i] for i in range(3))
        samples.append({
            "day": day,
            "epoch_utc": epoch,
            "earth_position_km": [0.0, 0.0, 0.0],
            "moon_position_earth_centered_km": list(moon_p),
            "moon_velocity_earth_centered_km_s": list(moon_v),
            "moon_relative_to_observer_km": list(rel),
            "moon_relative_velocity_km_s": list(rel_v),
            "earth_relative_to_observer_km": [-observer[0], -observer[1], -observer[2]],
        })

    return {
        "contract": CONTRACT,
        "status": "QUALIFICATION_ONLY",
        "authority": "DERIVED_FROM_NAV_GRADE_PARENT_CENTRIC_ANCHOR",
        "navigation_grade": False,
        "epoch_utc": _iso(start),
        "frame": "EARTH_CENTERED_J2000_ECLIPTIC_QUALIFICATION",
        "observer": {
            "semantics": "FROZEN_INERTIAL_TEST_OBSERVER",
            "position_earth_centered_km": list(observer),
            "velocity_earth_centered_km_s": list(observer_velocity),
            "initial_fraction_earth_to_moon": 0.5,
        },
        "camera_basis": {
            "semantics": "FIXED_AT_T0_POINTING_TO_MOON",
            "forward": list(forward),
            "right": list(right),
            "up": list(up),
        },
        "moon_model": {
            "model_id": model.model_id,
            "element_epoch_utc": model.element_epoch_utc,
            "semi_major_axis_km": model.semi_major_axis_km,
            "eccentricity": model.eccentricity,
            "inclination_deg": model.inclination_deg,
            "provenance": dict(model.provenance),
            "uncertainty": dict(model.uncertainty),
        },
        "samples": samples,
        "source": {
            "database": str(db_path),
            "moon_propagator": "TWO_BODY_OSCULATING_KEPLER",
            "data_access": "READ_ONLY",
        },
    }
