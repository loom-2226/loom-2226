"""Opt-in ephemeral usefulness-scaled Lambert search.

Only zero-revolution prograde low-path impulsive heliocentric transfers.
No multi-revolution, gravity assists, low-thrust, torch or local moon legs.
No persisted trajectory warehouse.
"""
from __future__ import annotations

from datetime import timedelta
from hashlib import sha256
from importlib.metadata import version
import json
import math

import numpy as np
from spiceypy.utils.exceptions import SpiceyError

from .batch import batched_izzo
from .pilot import _day, _iso, legacy

MIN_USEFUL_FLIGHT_TIME_FRACTION = 0.005  # kT-approved STARTING research value
MIN_USEFUL_FLIGHT_TIME_FLOOR_DAYS = 1.0
TRANSFER_FAMILY = "IZZO2015_M0_PROGRADE_LOW_PATH_HELIOCENTRIC"
STRATEGY = "scaled_flight_time"


def useful_flight_grid(start_days, end_days):
    """Visible proportional step plus floor; endpoints included."""
    lo, hi = float(start_days), float(end_days)
    if not (math.isfinite(lo) and math.isfinite(hi) and 0 < lo < hi):
        raise ValueError("INVALID_FLIGHT_RANGE")
    values = [round(lo, 8)]
    while values[-1] < hi:
        t = values[-1]
        nxt = round(min(hi, t + max(
            MIN_USEFUL_FLIGHT_TIME_FLOOR_DAYS,
            MIN_USEFUL_FLIGHT_TIME_FRACTION * t)), 8)
        if nxt <= t:
            raise ValueError("FLIGHT_GRID_FAILED_TO_ADVANCE")
        values.append(nxt)
    return values


def _windows(days, dep, arr, departure_limit, arrival_limit):
    mask = ((dep <= departure_limit) & (arr <= arrival_limit)
            & np.isfinite(dep) & np.isfinite(arr))
    indexes = np.flatnonzero(mask)
    if not len(indexes):
        return [], False
    groups = np.split(indexes, np.flatnonzero(np.diff(indexes) > 1) + 1)
    windows = []
    for group in groups:
        cheapest = int(group[np.argmin(dep[group] + arr[group])])
        windows.append({
            "first_sample_day": float(days[group[0]]),
            "last_sample_day": float(days[group[-1]]),
            "admitted_sample_count": len(group),
            "best_sampled_candidate": {
                "flight_days": float(days[cheapest]),
                "departure_vinf_km_s": round(float(dep[cheapest]), 7),
                "arrival_vinf_km_s": round(float(arr[cheapest]), 7),
            },
        })
    return windows, bool(mask[-1])


def _evaluate(engine, origin, destination, departure, flight_days):
    """Qualified SPICE source, same batched Izzo as existing pilot."""
    original, origin_class = engine._state(origin, departure)
    if origin_class != "DIRECT":
        raise ValueError("UNQUALIFIED_ORIGIN")
    arrival_dates = [departure + timedelta(days=float(t)) for t in flight_days]
    destination_states, source, _ = engine._batch_states(destination, arrival_dates)
    v1, v2 = batched_izzo(
        legacy.SUN_GM_KM3_S2,
        np.repeat(np.asarray(original.position_km)[None, :],
                  len(flight_days), axis=0),
        destination_states[:, :3], np.asarray(flight_days) * 86400.,
    )
    engine.solve_count += len(flight_days)
    dep_speed = np.linalg.norm(v1 - np.asarray(original.velocity_km_s), axis=1)
    arr_speed = np.linalg.norm(v2 - destination_states[:, 3:], axis=1)
    return dep_speed, arr_speed, source


def search_scaled_flight(engine, origin, destination, departure, *,
                         flight_range_days, max_flight_time_days,
                         departure_limit, arrival_limit):
    """Per-departure ephemeral summary; required authored flight horizon."""
    if flight_range_days is None or max_flight_time_days is None:
        raise ValueError("EXPLICIT_INITIAL_RANGE_AND_HORIZON_REQUIRED")
    if len(flight_range_days) != 2:
        raise ValueError("INVALID_FLIGHT_RANGE")
    lo, initial_hi = map(float, flight_range_days)
    limit = float(max_flight_time_days)
    if not (0 < lo < initial_hi <= limit and math.isfinite(limit)):
        raise ValueError("INVALID_AUTHORED_FLIGHT_HORIZON")
    if departure_limit < 0 or arrival_limit < 0:
        raise ValueError("NEGATIVE_SPEED_LIMIT")
    epoch = _day(departure)
    for body in (origin, destination):
        state = engine.endpoint(body, epoch)
        if state["status"] != "DIRECT":
            raise ValueError(state["status"] + ":" + body)

    src_orig, _ = engine.adapter.registry.source_for(origin, _iso(epoch))
    samples = useful_flight_grid(lo, initial_hi)
    extensions = []
    source = None
    fault = None
    started_solves = engine.solve_count
    while True:
        try:
            dep, arr, current_source = _evaluate(
                engine, origin, destination, epoch, samples)
            source = current_source
        except (ValueError, RuntimeError, SpiceyError) as exc:
            fault = str(exc)
            break
        windows, touching = _windows(
            np.asarray(samples), dep, arr, departure_limit, arrival_limit)
        if samples[-1] >= limit:
            status = ("FLIGHT_RANGE_OPEN_EDGE" if touching
                      else "EXTENDED_BOUNDED" if extensions else "BOUNDED")
            break
        # A closed local edge does NOT exclude a disconnected later island.
        # Continue to the caller's EXPLICIT horizon for recall, and separately
        # record whether the extension was demanded by an open feasible edge.
        # Doubling the evaluated span limits redundant re-solves; not a cap.
        new_hi = min(limit, 2 * samples[-1] - lo)
        new_grid = useful_flight_grid(samples[-1], new_hi)
        extensions.append({
            "from_days": samples[-1], "to_days": new_hi,
            "trigger": ("FEASIBLE_UPPER_EDGE" if touching
                        else "RECALL_SEARCH_TO_EXPLICIT_HORIZON")})
        samples.extend(new_grid[1:])
    if fault is not None:
        status, windows, touching = "UNKNOWN_FLIGHT_RANGE", [], None

    # Geometry signature excludes vehicle limits and price. The result
    # signature includes speed limits because feasible-window choice does.
    geom_key = {
        "route": [origin, destination], "departure_epoch": _iso(epoch),
        "strategy": STRATEGY,
        "min_useful_flight_time_fraction": MIN_USEFUL_FLIGHT_TIME_FRACTION,
        "min_useful_flight_time_floor_days": MIN_USEFUL_FLIGHT_TIME_FLOOR_DAYS,
        "initial_flight_range_days": [lo, initial_hi],
        "max_flight_time_days": limit,
        "extension_rule": "DOUBLE_EVALUATED_SPAN_TO_EXPLICIT_HORIZON",
        "initial_span_days": initial_hi - lo,
        "grid_sha256": sha256(json.dumps(samples, separators=(",", ":")).encode()).hexdigest(),
        "sample_count": len(samples),
        "extensions": extensions,
        "transfer_family": TRANSFER_FAMILY,
        "source_origin_id": src_orig.ephemeris_source_id,
        "source_origin_sha256": src_orig.sha256,
        "source_destination_id": source.ephemeris_source_id if source else None,
        "source_destination_sha256": source.sha256 if source else None,
        "solver": "lamberthub.izzo2015",
        "solver_version": version("lamberthub"),
    }
    result = {
        "status": status,
        "standing": "SAMPLED_TRANSFER_FAMILY_ONLY_NOT_GLOBAL_OPTIMUM",
        "reason": fault,
        "geometry_key": geom_key,
        "geometry_fingerprint": sha256(json.dumps(
            geom_key, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "search_limits": {"departure_vinf_km_s": departure_limit,
                          "arrival_vinf_km_s": arrival_limit},
        "evaluated_flight_range_days": [lo, samples[-1]],
        "sampled_solutions": engine.solve_count - started_solves,
        "windows": windows, "edge_open": touching,
        "not_searched": ["multi_revolution", "gravity_assists", "low_thrust",
                         "torch", "moon_local_legs"],
    }
    result["fingerprint"] = sha256(json.dumps(
        result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result
