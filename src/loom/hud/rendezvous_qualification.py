from __future__ import annotations

"""Qualification-only two-burn lunar terminal-state feasibility preview.

This module is deliberately NOT Navigator targeting authority and NOT executable
flight-control authority.  It asks a narrower engineering question: if Wayfarer
could establish the required thrust attitudes instantaneously, can a departure
burn + coast + braking burn reach a user-specified Moon-relative standoff point
with low relative velocity using the same disposable HUD flight dynamics?

The attitude transitions are explicitly UNQUALIFIED.  No RCS, inertia tensor,
flip time, torque, or control law is invented.  The live session and campaign
state are restored unchanged after every candidate evaluation.
"""

from datetime import timezone
import math
import time
from typing import Any

from loom.hud.earth_moon_qualification import _state_from_jpl
from loom.hud.realtime_flight_qualification import (
    G0_M_S2,
    MAX_INTEGRATION_STEP_S,
    MOON_RADIUS_KM,
    TORCH_CARDS,
)

CONTRACT = "LOOM_HUD_RENDEZVOUS_FEASIBILITY_QUALIFICATION_V1"


def _mag(v) -> float:
    return math.sqrt(sum(float(x) * float(x) for x in v))


def _unit(v):
    m = _mag(v)
    if m <= 0.0:
        raise ValueError("direction is undefined")
    return tuple(float(x) / m for x in v)


def _future_epoch(epoch, seconds: float):
    return epoch.fromtimestamp(epoch.timestamp() + seconds, tz=timezone.utc)


def _sub(a, b):
    return tuple(float(a[i]) - float(b[i]) for i in range(3))


def _add(a, b):
    return tuple(float(a[i]) + float(b[i]) for i in range(3))


def _scale(a, s: float):
    return tuple(float(x) * float(s) for x in a)


def _save(session):
    return (
        session.sim_epoch,
        tuple(session.ship_position),
        tuple(session.ship_velocity),
        float(session.remass_t),
        float(session.wet_mass_t),
        bool(session.torch_active),
        str(session.torch_mode),
        str(session.status),
        float(session.time_scale),
        float(session.last_wall),
        tuple(session.nose_direction),
    )


def _restore(session, saved) -> None:
    (
        session.sim_epoch,
        session.ship_position,
        session.ship_velocity,
        session.remass_t,
        session.wet_mass_t,
        session.torch_active,
        session.torch_mode,
        session.status,
        session.time_scale,
        session.last_wall,
        session.nose_direction,
    ) = saved


def _target_state(session, start_epoch, arrival_s: float, standoff_altitude_km: float):
    epoch = _future_epoch(start_epoch, arrival_s)
    moon_p, moon_v, source = _state_from_jpl(session.anchors, epoch)
    # Qualification convention only: terminal point lies on the Earth->Moon
    # outward radial line.  It is not an orbit, station location or docking point.
    radial = _unit(moon_p)
    radius = MOON_RADIUS_KM + standoff_altitude_km
    target_p = _add(moon_p, _scale(radial, radius))
    target_v = tuple(float(x) for x in moon_v)
    return epoch, target_p, target_v, moon_p, source


def _run_candidate(
    session,
    *,
    baseline,
    mode: str,
    burn1_s: float,
    coast_s: float,
    burn2_s: float,
    dir1,
    dir2,
    sample_s: float,
) -> dict[str, Any]:
    _restore(session, baseline)
    session.time_scale = 0.0
    session.torch_mode = mode
    points: list[dict[str, Any]] = []
    elapsed = 0.0
    next_sample = 0.0

    segments = (
        ("BURN", burn1_s, _unit(dir1), True),
        ("COAST", coast_s, _unit(dir1), False),
        ("BRAKE", burn2_s, _unit(dir2), True),
    )
    for phase, duration, direction, active in segments:
        session.nose_direction = direction
        session.torch_active = bool(active and duration > 0.0 and session.remass_t > 0.0)
        left = max(0.0, float(duration))
        while left > 1e-9:
            dt = min(MAX_INTEGRATION_STEP_S, left)
            session._step(dt)
            elapsed += dt
            left -= dt
            if elapsed + 1e-9 >= next_sample or left <= 1e-9:
                moon_p, _moon_v, moon_source = _state_from_jpl(session.anchors, session.sim_epoch)
                points.append({
                    "elapsed_s": elapsed,
                    "epoch_utc": session.sim_epoch.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                    "phase": phase,
                    "wayfarer_position_earth_centered_km": list(session.ship_position),
                    "wayfarer_velocity_earth_centered_km_s": list(session.ship_velocity),
                    "moon_position_earth_centered_km": list(moon_p),
                    "moon_relative_to_wayfarer_km": [float(moon_p[i]) - float(session.ship_position[i]) for i in range(3)],
                    "remass_t": float(session.remass_t),
                    "state_source": moon_source,
                })
                next_sample += sample_s
    session.torch_active = False
    return {
        "points": points,
        "final_position": tuple(session.ship_position),
        "final_velocity": tuple(session.ship_velocity),
        "final_remass_t": float(session.remass_t),
        "final_wet_mass_t": float(session.wet_mass_t),
        "final_epoch": session.sim_epoch,
    }


def solve_moon_rendezvous_feasibility(
    session,
    *,
    max_time_s: float,
    mode: str,
    standoff_altitude_km: float,
    sample_s: float = 60.0,
) -> dict[str, Any]:
    """Search a two-burn terminal-state feasibility envelope.

    Position and velocity seeds are impulsive approximations.  Candidate plans are
    evaluated with the actual qualification gravity/thrust/remass integrator.
    Results remain non-navigation-grade because the attitude transitions are not
    physically qualified and the standoff point is a synthetic qualification
    target rather than an operational lunar orbit or facility.
    """
    max_time_s = float(max_time_s)
    sample_s = float(sample_s)
    standoff_altitude_km = float(standoff_altitude_km)
    mode = str(mode).upper()
    if mode not in TORCH_CARDS:
        raise ValueError(f"unknown torch mode: {mode}")
    if not (1800.0 <= max_time_s <= 7 * 86400.0):
        raise ValueError("max_time_s must be in 1800..604800")
    if not (100.0 <= standoff_altitude_km <= 100000.0):
        raise ValueError("standoff_altitude_km must be in 100..100000")
    if not (10.0 <= sample_s <= 3600.0):
        raise ValueError("sample_s must be in 10..3600")

    with session.lock:
        session._advance_locked()
        baseline = _save(session)
        start_epoch = session.sim_epoch
        start_p = tuple(session.ship_position)
        start_v = tuple(session.ship_velocity)
        a = TORCH_CARDS[mode]["acceleration_g"] * G0_M_S2 / 1000.0
        candidates: list[dict[str, Any]] = []
        try:
            fractions = [0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]
            for frac in fractions:
                arrival_s = max(1800.0, max_time_s * frac)
                target_epoch, target_p, target_v, moon_p, source = _target_state(
                    session, start_epoch, arrival_s, standoff_altitude_km
                )
                # Impulsive seed: one velocity change establishes the mean transfer
                # velocity; the second removes the terminal velocity mismatch.
                mean_v = _scale(_sub(target_p, start_p), 1.0 / arrival_s)
                dv1 = _sub(mean_v, start_v)
                dv2 = _sub(target_v, mean_v)
                burn1_s = _mag(dv1) / a
                burn2_s = _mag(dv2) / a
                coast_s = arrival_s - burn1_s - burn2_s
                if burn1_s <= 0.0 or burn2_s <= 0.0 or coast_s < 0.0:
                    continue
                if burn1_s + burn2_s >= arrival_s:
                    continue
                trial = _run_candidate(
                    session,
                    baseline=baseline,
                    mode=mode,
                    burn1_s=burn1_s,
                    coast_s=coast_s,
                    burn2_s=burn2_s,
                    dir1=dv1,
                    dir2=dv2,
                    sample_s=sample_s,
                )
                final_p = trial["final_position"]
                final_v = trial["final_velocity"]
                pos_err = _mag(_sub(final_p, target_p))
                rel_v = _mag(_sub(final_v, target_v))
                moon_range = _mag(_sub(final_p, moon_p))
                candidates.append({
                    "arrival_s": arrival_s,
                    "burn1_s": burn1_s,
                    "coast_s": coast_s,
                    "burn2_s": burn2_s,
                    "dir1": list(_unit(dv1)),
                    "dir2": list(_unit(dv2)),
                    "position_error_km": pos_err,
                    "relative_speed_km_s": rel_v,
                    "moon_range_km": moon_range,
                    "target_epoch_utc": target_epoch.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                    "target_position_earth_centered_km": list(target_p),
                    "target_velocity_earth_centered_km_s": list(target_v),
                    "target_state_source": source,
                    "trial": trial,
                })

            if not candidates:
                raise ValueError("no feasible two-burn seed within requested horizon")

            # Prefer plans that actually reach the terminal neighborhood, then the
            # lower residual relative velocity.  Both quantities remain visible.
            best = min(candidates, key=lambda c: (c["position_error_km"], c["relative_speed_km_s"]))
            trial = best["trial"]
            return {
                "contract": CONTRACT,
                "solver": "QUALIFICATION_TWO_BURN_TERMINAL_STATE_FEASIBILITY",
                "status": "QUALIFICATION_ONLY",
                "navigation_grade": False,
                "mutates_live_state": False,
                "targeting_authority": "NONE_NOT_NAVIGATOR",
                "attitude_transition_authority": "UNQUALIFIED_INSTANTANEOUS_REORIENTATION_ASSUMED_FOR_FEASIBILITY_ONLY",
                "frame": "J2000/ECLIPTIC",
                "start_epoch_utc": start_epoch.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                "start_position_earth_centered_km": list(start_p),
                "mode": mode,
                "standoff": {
                    "altitude_km": standoff_altitude_km,
                    "radius_from_moon_center_km": MOON_RADIUS_KM + standoff_altitude_km,
                    "geometry": "EARTH_TO_MOON_OUTWARD_RADIAL_QUALIFICATION_POINT",
                    "operational_authority": "NONE",
                },
                "burn_s": best["burn1_s"],
                "burn1_s": best["burn1_s"],
                "coast_s": best["coast_s"],
                "burn2_s": best["burn2_s"],
                "arrival_elapsed_s": best["arrival_s"],
                "commanded_direction_inertial": best["dir1"],
                "braking_direction_inertial": best["dir2"],
                "target_epoch_utc": best["target_epoch_utc"],
                "target_position_earth_centered_km": best["target_position_earth_centered_km"],
                "target_velocity_earth_centered_km_s": best["target_velocity_earth_centered_km_s"],
                "integration": {
                    "method": "SEMI_IMPLICIT_EULER",
                    "max_step_s": MAX_INTEGRATION_STEP_S,
                    "gravity": "LOOM_SHARED_EARTH_PLUS_MOON_POINT_MASS",
                },
                "search": {
                    "candidate_count": len(candidates),
                    "max_time_s": max_time_s,
                    "criterion": "MINIMUM_TERMINAL_POSITION_ERROR_THEN_RELATIVE_SPEED",
                },
                "points": trial["points"],
                "final": {
                    "speed_km_s": _mag(trial["final_velocity"]),
                    "moon_range_km": best["moon_range_km"],
                    "target_position_error_km": best["position_error_km"],
                    "relative_speed_km_s": best["relative_speed_km_s"],
                    "remass_t": trial["final_remass_t"],
                    "wet_mass_t": trial["final_wet_mass_t"],
                },
            }
        finally:
            _restore(session, baseline)
            session.last_wall = time.monotonic()
