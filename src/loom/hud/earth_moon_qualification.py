from __future__ import annotations

from bisect import bisect_right
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import math
import os

from loom.runtime import resolve_runtime_roots
from loom.spatial.celestial_state import propagate_parent_centric
from loom.spatial.ephemeris_interpolation import EphemerisAnchor, hermite_state, validate_uniform_anchors
from loom.spatial.sqlite_celestial_catalog import SQLiteCelestialCatalog

CONTRACT = "LOOM_HUD_EARTH_MOON_QUALIFICATION_V2"
DEFAULT_EPOCH = "2026-09-10T00:00:00Z"
EARTH_ID = "EA"
MOON_ID = "LU"
CACHE_RELATIVE = Path("qualification/earth_moon_2026_hourly.json")
DISPLAY_STEP_MINUTES = 5


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


def _load_jpl_cache(path: Path) -> tuple[list[EphemerisAnchor], dict] | None:
    if not path.is_file():
        return None
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("contract") != "LOOM_EXTERNAL_EPHEMERIS_CACHE_V1":
        raise ValueError("unsupported Earth-Moon ephemeris cache contract")
    if doc.get("source") != "JPL_HORIZONS_DIRECT":
        raise ValueError("Earth-Moon cache is not source-labelled JPL Horizons direct")
    if doc.get("reference_frame") != "J2000/ECLIPTIC":
        raise ValueError("Earth-Moon cache frame mismatch")
    if doc.get("units") != "KM-S":
        raise ValueError("Earth-Moon cache units mismatch")
    anchors = [
        EphemerisAnchor(
            epoch_utc=str(row["epoch_utc"]),
            position_km=tuple(float(v) for v in row["position_km"]),
            velocity_km_s=tuple(float(v) for v in row["velocity_km_s"]),
        )
        for row in doc.get("anchors", [])
    ]
    validate_uniform_anchors(anchors, expected_step_s=3600.0)
    return anchors, doc


def _state_from_jpl(anchors: list[EphemerisAnchor], epoch: datetime) -> tuple[tuple[float, float, float], tuple[float, float, float], str]:
    target = _iso(epoch)
    times = [_parse_epoch(a.epoch_utc) for a in anchors]
    if epoch < times[0] or epoch > times[-1]:
        raise ValueError("requested epoch outside cached JPL Horizons coverage")
    idx = bisect_right(times, epoch)
    if idx > 0 and times[idx - 1] == epoch:
        a = anchors[idx - 1]
        return a.position_km, a.velocity_km_s, "DIRECT_JPL_SAMPLE"
    if idx == 0 or idx >= len(anchors):
        raise ValueError("unable to bracket cached JPL Horizons epoch")
    p, v = hermite_state(anchors[idx - 1], anchors[idx], target)
    return p, v, "INTERPOLATED_JPL_HERMITE"


def build_earth_moon_qualification(
    *,
    epoch_utc: str = DEFAULT_EPOCH,
    days: int = 30,
    data_root: Path | str | None = None,
) -> dict:
    """Build a read-only Earth-centered qualification scene.

    Preferred source is a dense local cache of direct Earth-centered Moon vectors
    acquired from JPL Horizons. Five-minute display states are reconstructed in
    Python with cubic Hermite interpolation between hourly position+velocity
    anchors. If no cache exists, the previous single-anchor two-body solution is
    retained as an explicit DERIVED fallback. Neither mode is silently promoted
    to canonical campaign/navigation authority.
    """
    start = _parse_epoch(epoch_utc)
    if not 1 <= int(days) <= 60:
        raise ValueError("days must be in 1..60")

    roots = resolve_runtime_roots(data_root=data_root)
    db_path = Path(os.environ.get("LOOM_SPATIAL_DB") or (roots.data_root / "LOOM_2226.sqlite3"))
    cache_path = roots.data_root / CACHE_RELATIVE
    cached = _load_jpl_cache(cache_path)

    model = None
    if cached is not None:
        anchors, cache_doc = cached
        moon0, moonv0, _ = _state_from_jpl(anchors, start)
        source_mode = "JPL_HORIZONS_HOURLY_PLUS_HERMITE"
        authority = "EXTERNAL_DIRECT_PLUS_INTERPOLATED"
        source_detail = {
            "cache": str(cache_path),
            "anchor_count": len(anchors),
            "anchor_step_s": 3600,
            "interpolator": "CUBIC_HERMITE_POSITION_VELOCITY",
            "display_step_minutes": DISPLAY_STEP_MINUTES,
            "jpl_source": cache_doc.get("source"),
            "corrections": cache_doc.get("corrections"),
        }
    else:
        catalog = SQLiteCelestialCatalog(db_path)
        model = catalog.orbit_model_from_direct_anchor(MOON_ID, _iso(start))
        moon0, moonv0 = propagate_parent_centric(model, _iso(start))
        source_mode = "TWO_BODY_OSCULATING_KEPLER_FALLBACK"
        authority = "DERIVED_FROM_NAV_GRADE_PARENT_CENTRIC_ANCHOR"
        source_detail = {
            "database": str(db_path),
            "fallback_reason": "JPL hourly qualification cache absent",
            "moon_propagator": "TWO_BODY_OSCULATING_KEPLER",
        }

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
    if cached is not None:
        sample_count = int(days) * 24 * (60 // DISPLAY_STEP_MINUTES) + 1
        for index in range(sample_count):
            when = start + timedelta(minutes=index * DISPLAY_STEP_MINUTES)
            moon_p, moon_v, state_source = _state_from_jpl(anchors, when)
            rel = tuple(moon_p[i] - observer[i] for i in range(3))
            rel_v = tuple(moon_v[i] for i in range(3))
            samples.append({
                "sample_index": index,
                "elapsed_hours": index * DISPLAY_STEP_MINUTES / 60.0,
                "epoch_utc": _iso(when),
                "state_source": state_source,
                "earth_position_km": [0.0, 0.0, 0.0],
                "moon_position_earth_centered_km": list(moon_p),
                "moon_velocity_earth_centered_km_s": list(moon_v),
                "moon_relative_to_observer_km": list(rel),
                "moon_relative_velocity_km_s": list(rel_v),
                "earth_relative_to_observer_km": [-observer[0], -observer[1], -observer[2]],
            })
    else:
        for day in range(int(days) + 1):
            epoch = _iso(start + timedelta(days=day))
            moon_p, moon_v = propagate_parent_centric(model, epoch)
            rel = tuple(moon_p[i] - observer[i] for i in range(3))
            samples.append({
                "sample_index": day,
                "elapsed_hours": day * 24.0,
                "epoch_utc": epoch,
                "state_source": "PROPAGATED_TWO_BODY_FALLBACK",
                "earth_position_km": [0.0, 0.0, 0.0],
                "moon_position_earth_centered_km": list(moon_p),
                "moon_velocity_earth_centered_km_s": list(moon_v),
                "moon_relative_to_observer_km": list(rel),
                "moon_relative_velocity_km_s": list(moon_v),
                "earth_relative_to_observer_km": [-observer[0], -observer[1], -observer[2]],
            })

    moon_model = {
        "mode": source_mode,
        "navigation_grade": False,
    }
    if model is not None:
        moon_model.update({
            "model_id": model.model_id,
            "element_epoch_utc": model.element_epoch_utc,
            "semi_major_axis_km": model.semi_major_axis_km,
            "eccentricity": model.eccentricity,
            "inclination_deg": model.inclination_deg,
            "provenance": dict(model.provenance),
            "uncertainty": dict(model.uncertainty),
        })
    else:
        moon_model.update({
            "model_id": "JPL_HORIZONS_2026_HOURLY_HERMITE",
            "provenance": {"source": "JPL Horizons", "cache": str(cache_path)},
            "uncertainty": {"qualification": "INTERPOLATED_NON_NAVIGATION_GRADE"},
        })

    return {
        "contract": CONTRACT,
        "status": "QUALIFICATION_ONLY",
        "authority": authority,
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
        "moon_model": moon_model,
        "samples": samples,
        "source": {
            **source_detail,
            "mode": source_mode,
            "data_access": "READ_ONLY",
        },
    }
