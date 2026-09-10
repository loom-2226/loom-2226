from __future__ import annotations

"""Qualification-only moving-Moon intercept preview.

This is intentionally not Navigator targeting authority.  It numerically searches
fixed-inertial-attitude burn/coast candidates against the same JPL Moon states,
point-mass gravity and Wayfarer working torch cards used by the disposable HUD
flight session.  It never commits a maneuver and never mutates campaign state.
"""

from datetime import timezone
import math
from typing import Any

from loom.hud.earth_moon_qualification import _state_from_jpl
from loom.hud.realtime_flight_qualification import G0_M_S2, TORCH_CARDS

CONTRACT = "LOOM_HUD_INTERCEPT_PREVIEW_QUALIFICATION_V1"


def _mag(v) -> float:
    return math.sqrt(sum(float(x) * float(x) for x in v))


def _unit(v):
    m = _mag(v)
    if m <= 0.0:
        raise ValueError("intercept direction is undefined")
    return tuple(float(x) / m for x in v)


def _future_epoch(epoch, seconds: float):
    return epoch.fromtimestamp(epoch.timestamp() + seconds, tz=timezone.utc)


def _relative_speed(point: dict[str, Any], moon_velocity) -> float:
    ship_v = point["wayfarer_velocity_earth_centered_km_s"]
    return _mag([float(ship_v[i]) - float(moon_velocity[i]) for i in range(3)])


def solve_moon_intercept(session, *, max_time_s: float, mode: str, sample_s: float = 60.0) -> dict[str, Any]:
    """Find a low-miss fixed-attitude burn+coast candidate.

    The analytic seed assumes a constant acceleration burn followed by coast to a
    moving JPL endpoint.  Each seed is then evaluated with the real qualification
    propagator.  The result is useful mission-design scaffolding only.
    """
    max_time_s = float(max_time_s)
    sample_s = float(sample_s)
    mode = str(mode).upper()
    if mode not in TORCH_CARDS:
        raise ValueError(f"unknown torch mode: {mode}")
    if not (900.0 <= max_time_s <= 7 * 86400.0):
        raise ValueError("max_time_s must be in 900..604800")
    if not (10.0 <= sample_s <= 3600.0):
        raise ValueError("sample_s must be in 10..3600")

    with session.lock:
        session._advance_locked()
        start_epoch = session.sim_epoch
        start_p = tuple(session.ship_position)
        start_v = tuple(session.ship_velocity)
        saved_nose = tuple(session.nose_direction)
        saved_scale = session.time_scale
        session.time_scale = 0.0
        a = TORCH_CARDS[mode]["acceleration_g"] * G0_M_S2 / 1000.0
        candidates: list[dict[str, Any]] = []
        try:
            # Broad arrival-time search.  More density near short transfers, where
            # Wayfarer's acceleration makes geometry especially sensitive.
            fractions = [0.12,0.16,0.20,0.25,0.30,0.36,0.43,0.50,0.58,0.66,0.75,0.84,0.92,1.00]
            times = sorted({max(900.0, min(max_time_s, max_time_s*f)) for f in fractions} | {max_time_s})
            for arrival_s in times:
                moon_p, _moon_v, _src = _state_from_jpl(session.anchors, _future_epoch(start_epoch, arrival_s))
                residual = tuple(float(moon_p[i]) - start_p[i] - start_v[i]*arrival_s for i in range(3))
                distance = _mag(residual)
                # For constant acceleration a over burn b and coast T-b:
                # displacement from thrust = a*b*(T-b/2).
                disc = arrival_s*arrival_s - 2.0*distance/a
                if disc < 0.0:
                    continue
                burn_s = arrival_s - math.sqrt(disc)
                burn_s = max(1.0, min(burn_s, arrival_s))
                coast_s = max(0.0, arrival_s - burn_s)
                session.nose_direction = _unit(residual)
                trial = session.trajectory_preview(burn_s=burn_s, coast_s=coast_s, mode=mode, sample_s=sample_s)
                if not trial.get("points"):
                    continue
                last = trial["points"][-1]
                moon_v = _state_from_jpl(session.anchors, _future_epoch(start_epoch, arrival_s))[1]
                rel_v = _relative_speed(last, moon_v)
                miss = float(trial["final"]["moon_range_km"])
                candidates.append({"arrival_s": arrival_s, "burn_s": burn_s, "coast_s": coast_s, "direction": list(session.nose_direction), "miss_km": miss, "relative_speed_km_s": rel_v, "trial": trial})

            if not candidates:
                raise ValueError("no feasible fixed-attitude intercept seed within requested horizon")
            best = min(candidates, key=lambda c: (c["miss_km"], c["relative_speed_km_s"]))

            # One local timing refinement around the best broad arrival time.
            dt = max(60.0, max_time_s / 80.0)
            refined_times = [best["arrival_s"] + k*dt for k in (-2,-1,1,2)]
            for arrival_s in refined_times:
                if arrival_s < 900.0 or arrival_s > max_time_s:
                    continue
                moon_p, _moon_v, _src = _state_from_jpl(session.anchors, _future_epoch(start_epoch, arrival_s))
                residual = tuple(float(moon_p[i]) - start_p[i] - start_v[i]*arrival_s for i in range(3))
                distance = _mag(residual)
                disc = arrival_s*arrival_s - 2.0*distance/a
                if disc < 0.0:
                    continue
                burn_s = max(1.0, min(arrival_s - math.sqrt(disc), arrival_s))
                coast_s = arrival_s - burn_s
                session.nose_direction = _unit(residual)
                trial = session.trajectory_preview(burn_s=burn_s, coast_s=coast_s, mode=mode, sample_s=sample_s)
                last = trial["points"][-1]
                moon_v = _state_from_jpl(session.anchors, _future_epoch(start_epoch, arrival_s))[1]
                rel_v = _relative_speed(last, moon_v)
                miss = float(trial["final"]["moon_range_km"])
                c={"arrival_s":arrival_s,"burn_s":burn_s,"coast_s":coast_s,"direction":list(session.nose_direction),"miss_km":miss,"relative_speed_km_s":rel_v,"trial":trial}
                candidates.append(c)
                if (miss, rel_v) < (best["miss_km"], best["relative_speed_km_s"]):
                    best = c

            out = dict(best["trial"])
            out.update({
                "contract": CONTRACT,
                "solver": "QUALIFICATION_FIXED_ATTITUDE_MOVING_MOON_INTERCEPT_SEARCH",
                "status": "QUALIFICATION_ONLY",
                "navigation_grade": False,
                "mutates_live_state": False,
                "targeting_authority": "NONE_NOT_NAVIGATOR",
                "search": {"candidate_count": len(candidates), "max_time_s": max_time_s, "criterion": "MINIMUM_FINAL_MOON_RANGE_THEN_RELATIVE_SPEED"},
                "burn_s": best["burn_s"],
                "coast_s": best["coast_s"],
                "commanded_direction_inertial": best["direction"],
            })
            last = out["points"][-1]
            ranges = [(_mag(p["moon_relative_to_wayfarer_km"]), p["elapsed_s"], p["epoch_utc"]) for p in out["points"]]
            closest = min(ranges, key=lambda x: x[0])
            out["final"]["relative_speed_km_s"] = best["relative_speed_km_s"]
            out["final"]["arrival_elapsed_s"] = best["arrival_s"]
            out["closest_approach"] = {"range_km": closest[0], "elapsed_s": closest[1], "epoch_utc": closest[2]}
            return out
        finally:
            session.nose_direction = saved_nose
            session.time_scale = saved_scale
            session.last_wall = __import__('time').monotonic()
