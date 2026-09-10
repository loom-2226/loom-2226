from __future__ import annotations

"""Qualification-only lunar terminal-state feasibility preview.

This module is deliberately NOT Navigator targeting authority and NOT executable
flight-control authority. It asks a narrower engineering question: if Wayfarer
could establish the required thrust attitudes instantaneously, can a departure
burn + coast + braking burn reach a user-specified Moon-relative standoff point
with low relative velocity using the same disposable HUD flight dynamics?

The attitude transitions are explicitly UNQUALIFIED. No RCS, inertia tensor,
flip time, torque, or control law is invented. The live session and campaign
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
POSITION_TOLERANCE_KM = 50.0
RELATIVE_SPEED_TOLERANCE_KM_S = 0.05
MIN_SURFACE_CLEARANCE_KM = 100.0
CORRECTOR_ITERATIONS = 8
LINE_SEARCH_SCALES = (1.0, 0.5, 0.25)


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
    # Qualification convention only: approach from the Earth-facing side of the
    # Moon. The previous outward-radial target sat on the lunar far side, making
    # a direct two-burn transfer intersect the Moon and forcing the clearance gate
    # to fight the terminal-position objective. This target is still NOT an orbit,
    # station location, docking point, or Navigator-authoritative destination.
    earth_to_moon = _unit(moon_p)
    radius = MOON_RADIUS_KM + standoff_altitude_km
    target_p = _sub(moon_p, _scale(earth_to_moon, radius))
    target_v = tuple(float(x) for x in moon_v)
    return epoch, target_p, target_v, moon_p, source


def _classify_solution(
    *,
    position_error_km: float,
    relative_speed_km_s: float,
    min_surface_clearance_km: float,
    remass_t: float,
) -> dict[str, Any]:
    position_ok = float(position_error_km) <= POSITION_TOLERANCE_KM
    velocity_ok = float(relative_speed_km_s) <= RELATIVE_SPEED_TOLERANCE_KM_S
    surface_clearance_ok = float(min_surface_clearance_km) >= MIN_SURFACE_CLEARANCE_KM
    remass_ok = float(remass_t) > 0.0
    solved = position_ok and velocity_ok and surface_clearance_ok and remass_ok
    return {
        "status": "SOLVED_TRANSLATIONAL_FEASIBILITY" if solved else "NOT_SOLVED",
        "position_ok": position_ok,
        "velocity_ok": velocity_ok,
        "surface_clearance_ok": surface_clearance_ok,
        "remass_ok": remass_ok,
        "thresholds": {
            "position_error_km_max": POSITION_TOLERANCE_KM,
            "relative_speed_km_s_max": RELATIVE_SPEED_TOLERANCE_KM_S,
            "min_surface_clearance_km": MIN_SURFACE_CLEARANCE_KM,
            "remass_t_min_exclusive": 0.0,
        },
    }


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
    min_moon_range_km = float("inf")

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
            moon_p, _moon_v, moon_source = _state_from_jpl(session.anchors, session.sim_epoch)
            moon_rel = [float(moon_p[i]) - float(session.ship_position[i]) for i in range(3)]
            min_moon_range_km = min(min_moon_range_km, _mag(moon_rel))
            if elapsed + 1e-9 >= next_sample or left <= 1e-9:
                points.append({
                    "elapsed_s": elapsed,
                    "epoch_utc": session.sim_epoch.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                    "phase": phase,
                    "wayfarer_position_earth_centered_km": list(session.ship_position),
                    "wayfarer_velocity_earth_centered_km_s": list(session.ship_velocity),
                    "moon_position_earth_centered_km": list(moon_p),
                    "moon_relative_to_wayfarer_km": moon_rel,
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
        "min_moon_range_km": min_moon_range_km,
        "min_surface_clearance_km": min_moon_range_km - MOON_RADIUS_KM,
    }


def _score(position_error_km: float, relative_speed_km_s: float, min_surface_clearance_km: float) -> float:
    surface_penalty = 0.0
    if min_surface_clearance_km < MIN_SURFACE_CLEARANCE_KM:
        surface_penalty = 1e6 + (MIN_SURFACE_CLEARANCE_KM - min_surface_clearance_km) * 1000.0
    return (
        float(position_error_km) / POSITION_TOLERANCE_KM
        + float(relative_speed_km_s) / RELATIVE_SPEED_TOLERANCE_KM_S
        + surface_penalty
    )


def _evaluate(
    session,
    *,
    baseline,
    mode: str,
    arrival_s: float,
    target_p,
    target_v,
    moon_p,
    target_epoch,
    source: str,
    dv1,
    dv2,
    acceleration_km_s2: float,
    sample_s: float,
    iteration: int,
    line_scale: float,
) -> dict[str, Any] | None:
    burn1_s = _mag(dv1) / acceleration_km_s2
    burn2_s = _mag(dv2) / acceleration_km_s2
    coast_s = arrival_s - burn1_s - burn2_s
    if burn1_s <= 0.0 or burn2_s <= 0.0 or coast_s < 0.0:
        return None
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
    pos_residual = _sub(target_p, final_p)
    vel_residual = _sub(target_v, final_v)
    pos_err = _mag(pos_residual)
    rel_v = _mag(vel_residual)
    moon_range = _mag(_sub(final_p, moon_p))
    min_clearance = float(trial["min_surface_clearance_km"])
    quality = _classify_solution(
        position_error_km=pos_err,
        relative_speed_km_s=rel_v,
        min_surface_clearance_km=min_clearance,
        remass_t=trial["final_remass_t"],
    )
    return {
        "arrival_s": arrival_s,
        "burn1_s": burn1_s,
        "coast_s": coast_s,
        "burn2_s": burn2_s,
        "dir1": list(_unit(dv1)),
        "dir2": list(_unit(dv2)),
        "dv1": tuple(dv1),
        "dv2": tuple(dv2),
        "position_residual": pos_residual,
        "velocity_residual": vel_residual,
        "position_error_km": pos_err,
        "relative_speed_km_s": rel_v,
        "moon_range_km": moon_range,
        "min_surface_clearance_km": min_clearance,
        "iteration": iteration,
        "line_scale": line_scale,
        "quality": quality,
        "score": _score(pos_err, rel_v, min_clearance),
        "target_epoch_utc": target_epoch.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "target_position_earth_centered_km": list(target_p),
        "target_velocity_earth_centered_km_s": list(target_v),
        "target_state_source": source,
        "trial": trial,
    }


def solve_moon_rendezvous_feasibility(
    session,
    *,
    max_time_s: float,
    mode: str,
    standoff_altitude_km: float,
    sample_s: float = 60.0,
) -> dict[str, Any]:
    """Iteratively correct a two-burn terminal-state feasibility solution.

    The initial candidate is an impulsive transfer seed. Each shooting iteration
    uses the terminal position and velocity residuals together. A finite-burn
    lever-arm approximation solves the linearized two-impulse correction, then a
    bounded deterministic line search accepts only an improved propagated result.

    This remains non-navigation-grade because the attitude transitions are not
    physically qualified and the Earth-facing standoff point is a synthetic
    qualification target rather than an operational lunar orbit or facility.
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
            # Three arrival windows keep Pixel runtime bounded while giving the
            # terminal corrector materially different transfer-time seeds.
            fractions = [0.70, 0.85, 1.00]
            for frac in fractions:
                arrival_s = max(1800.0, max_time_s * frac)
                target_epoch, target_p, target_v, moon_p, source = _target_state(
                    session, start_epoch, arrival_s, standoff_altitude_km
                )
                mean_v = _scale(_sub(target_p, start_p), 1.0 / arrival_s)
                dv1 = _sub(mean_v, start_v)
                dv2 = _sub(target_v, mean_v)

                current = _evaluate(
                    session,
                    baseline=baseline,
                    mode=mode,
                    arrival_s=arrival_s,
                    target_p=target_p,
                    target_v=target_v,
                    moon_p=moon_p,
                    target_epoch=target_epoch,
                    source=source,
                    dv1=dv1,
                    dv2=dv2,
                    acceleration_km_s2=a,
                    sample_s=sample_s,
                    iteration=0,
                    line_scale=0.0,
                )
                if current is None:
                    continue
                candidates.append(current)

                for iteration in range(1, CORRECTOR_ITERATIONS):
                    if current["quality"]["status"] == "SOLVED_TRANSLATIONAL_FEASIBILITY":
                        break

                    # Linearized two-burn shooting correction. The first burn's
                    # delta-v acts for nearly the whole transfer while the second
                    # burn acts near arrival. Solve the pair of equations
                    #   dr ~= L1*d1 + L2*d2
                    #   dv ~= d1 + d2
                    # then verify every correction with the real propagator.
                    burn1_s = float(current["burn1_s"])
                    burn2_s = float(current["burn2_s"])
                    l1 = max(1.0, arrival_s - 0.5 * burn1_s)
                    l2 = max(0.0, 0.5 * burn2_s)
                    denom = max(1.0, l1 - l2)
                    pos_residual = current["position_residual"]
                    vel_residual = current["velocity_residual"]
                    delta1 = _scale(_sub(pos_residual, _scale(vel_residual, l2)), 1.0 / denom)
                    delta2 = _sub(vel_residual, delta1)

                    improved = None
                    for line_scale in LINE_SEARCH_SCALES:
                        trial_dv1 = _add(current["dv1"], _scale(delta1, line_scale))
                        trial_dv2 = _add(current["dv2"], _scale(delta2, line_scale))
                        candidate = _evaluate(
                            session,
                            baseline=baseline,
                            mode=mode,
                            arrival_s=arrival_s,
                            target_p=target_p,
                            target_v=target_v,
                            moon_p=moon_p,
                            target_epoch=target_epoch,
                            source=source,
                            dv1=trial_dv1,
                            dv2=trial_dv2,
                            acceleration_km_s2=a,
                            sample_s=sample_s,
                            iteration=iteration,
                            line_scale=line_scale,
                        )
                        if candidate is None:
                            continue
                        candidates.append(candidate)
                        if candidate["score"] + 1e-9 < current["score"]:
                            improved = candidate
                            break
                    if improved is None:
                        # Stagnation is evidence: do not manufacture further
                        # corrections once all bounded line-search steps worsen
                        # the propagated terminal state.
                        break
                    current = improved

            if not candidates:
                raise ValueError("no feasible corrected two-burn seed within requested horizon")

            solved_candidates = [
                c for c in candidates
                if c["quality"]["status"] == "SOLVED_TRANSLATIONAL_FEASIBILITY"
            ]
            pool = solved_candidates or candidates
            best = min(pool, key=lambda c: (c["score"], c["position_error_km"], c["relative_speed_km_s"]))
            trial = best["trial"]
            quality = best["quality"]
            return {
                "contract": CONTRACT,
                "solver": "QUALIFICATION_ITERATIVE_TERMINAL_STATE_CORRECTOR_V2",
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
                    "geometry": "EARTH_FACING_MOON_RADIAL_QUALIFICATION_POINT",
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
                    "arrival_windows": len(fractions),
                    "corrector_iterations_max": CORRECTOR_ITERATIONS,
                    "selected_iteration": best["iteration"],
                    "selected_line_scale": best["line_scale"],
                    "max_time_s": max_time_s,
                    "criterion": "SOLVED_FIRST_THEN_NORMALIZED_POSITION_PLUS_RELATIVE_SPEED_WITH_SURFACE_PENALTY",
                    "algorithm": "FINITE_BURN_LEVER_ARM_SHOOTING_WITH_BOUNDED_LINE_SEARCH",
                },
                "quality": quality,
                "points": trial["points"],
                "final": {
                    "speed_km_s": _mag(trial["final_velocity"]),
                    "moon_range_km": best["moon_range_km"],
                    "target_position_error_km": best["position_error_km"],
                    "relative_speed_km_s": best["relative_speed_km_s"],
                    "min_moon_range_km": trial["min_moon_range_km"],
                    "min_surface_clearance_km": trial["min_surface_clearance_km"],
                    "remass_t": trial["final_remass_t"],
                    "wet_mass_t": trial["final_wet_mass_t"],
                },
            }
        finally:
            _restore(session, baseline)
            session.last_wall = time.monotonic()
