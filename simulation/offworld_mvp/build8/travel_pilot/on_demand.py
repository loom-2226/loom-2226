"""Offline, non-runtime, demand-driven Lambert geometry for the existing pilot routes.

Only zero-revolution prograde impulsive heliocentric transfers and qualified SPICE.
Neither vehicle limits nor prices participate in geometry generation or cache keys.
"""
from __future__ import annotations

from datetime import timedelta
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path
import bisect
import json
import math

import numpy as np
from src.loom_spice_ephemeris_adapter import SpiceEphemerisAdapter
from .pilot import (
    ASSET_ROOT, TOF_BRACKETS, _day, _iso, state_registry, legacy,
)
from .batch import BatchTravelPilot, batched_izzo

# Authored resolution policy. One day is the minimum useful launch window.
MIN_USEFUL_LAUNCH_WINDOW_DAYS = 1.0
HALF_WINDOW_FACTOR = 0.5
DEFAULT_DEPARTURE_STEP_DAYS = 1.0
DENSE_FLIGHT_STEP_DAYS = 0.25
MERCURY_REFERENCE_AU_2026_01_01 = 0.46254878387561266
EARTH_REFERENCE_AU_2026_01_01 = 0.9833266687787967
AU_KM = 149597870.7
TRANSFER_FAMILY = "IZZO2015_M0_PROGRADE_LOW_PATH_HELIOCENTRIC"
ROUTES = {
    ("EARTH", "MERCURY"), ("EARTH", "MARS"), ("MARS", "CERES"),
    ("MERCURY", "EARTH"), ("MARS", "EARTH"), ("CERES", "MARS"),
    ("EARTH", "CERES"), ("CERES", "EARTH"),
}


def pareto_geometry(rows):
    """Discard only records dominated in all three useful dimensions.

    Earlier arrival (shorter flight duration) and smaller *both* endpoint
    speeds are preferred. The retained set preserves feasibility and the
    minimum flight duration under ANY pair of endpoint-speed upper bounds,
    and any objective monotone nondecreasing in these three quantities.
    Arbitrary nonmonotone future prices are NOT covered by that proof.
    """
    ordered = sorted(rows, key=lambda x: (
        x["flight_days"], x["departure_vinf_km_s"], x["arrival_vinf_km_s"]))
    departures = sorted({r["departure_vinf_km_s"] for r in ordered})
    tree = [math.inf] * (len(departures) + 1)

    def smallest_arrival(index):
        best = math.inf
        while index:
            best = min(best, tree[index])
            index -= index & -index
        return best

    def remember(index, arrival):
        while index < len(tree):
            tree[index] = min(tree[index], arrival)
            index += index & -index

    kept = []
    for row in ordered:
        idx = bisect.bisect_left(departures, row["departure_vinf_km_s"]) + 1
        if smallest_arrival(idx) <= row["arrival_vinf_km_s"]:
            continue
        kept.append(row)
        remember(idx, row["arrival_vinf_km_s"])
    return kept


class OnDemandTravel(BatchTravelPilot):
    def __init__(self, *, asset_root=ASSET_ROOT, cache_dir=None):
        # Geometry has no dependence on Build 7 price tables or vehicle rows.
        self.adapter = SpiceEphemerisAdapter(state_registry(asset_root))
        self.allow_approximation = False
        self._state_cache = {}
        self._geometry = {}
        self.cache_dir = Path(cache_dir) if cache_dir is not None else None
        self.solve_count = 0
        self.sample_seconds = 0.0
        self.batch_seconds = 0.0
        self.state_bulk_seconds = 0.0
        self.state_bulk_calls = 0
        self.bulk_calls = 0

    @staticmethod
    def _times(step, flight_range_days=None):
        if not 0 < step <= 5000:
            raise ValueError("INVALID_FLIGHT_STEP")
        if flight_range_days is not None:
            if (len(flight_range_days) != 2 or not
                    0 < float(flight_range_days[0]) < float(flight_range_days[1]) <= 5000):
                raise ValueError("INVALID_FLIGHT_RANGE")
            brackets = (tuple(map(float, flight_range_days)),)
        else:
            brackets = TOF_BRACKETS
        times = set()
        for lo, hi in brackets:
            n = math.ceil((hi - lo) / step)
            times.update(round(min(hi, lo + i * step), 8) for i in range(n))
            times.add(hi)
        return sorted(times)

    def steps_at(self, origin, destination, departure):
        """Selectable research hypothesis; distances are at the actual epoch."""
        epoch = _day(departure)
        a, _ = self._state(origin, epoch)
        b, _ = self._state(destination, epoch)
        inner, outer = sorted((
            math.dist(a.position_km, (0, 0, 0)) / AU_KM,
            math.dist(b.position_km, (0, 0, 0)) / AU_KM,
        ))
        radial_dep = HALF_WINDOW_FACTOR * MIN_USEFUL_LAUNCH_WINDOW_DAYS * (
            inner / MERCURY_REFERENCE_AU_2026_01_01) ** 1.5
        # Do not chase sub-half-day launch edges of a hard speed threshold.
        departure_step = min(DEFAULT_DEPARTURE_STEP_DAYS, max(
            HALF_WINDOW_FACTOR * MIN_USEFUL_LAUNCH_WINDOW_DAYS, radial_dep))
        flight_step = DENSE_FLIGHT_STEP_DAYS * (
            outer / EARTH_REFERENCE_AU_2026_01_01) ** 1.5
        return {"departure_step_days": round(departure_step, 8),
                "flight_step_days": round(flight_step, 8),
                "inner_au": round(inner, 9), "outer_au": round(outer, 9)}

    def _key(self, origin, destination, departure, times, step, flight_range_days=None):
        first = _iso(departure + timedelta(days=times[0]))
        last = _iso(departure + timedelta(days=times[-1]))
        src_o, _ = self.adapter.registry.source_for(origin, _iso(departure))
        src_d, coverage = self.adapter.registry.source_for(destination, first)
        src_end, end_cov = self.adapter.registry.source_for(destination, last)
        if (not src_o.navigation_grade or not src_d.navigation_grade
                or not src_end.navigation_grade or src_d.sha256 != src_end.sha256
                or coverage != end_cov):
            raise ValueError("UNQUALIFIED_SOURCE_OR_COVERAGE_SEAM")
        return {
            "route": [origin, destination],
            "departure_epoch": _iso(departure),
            "flight_time_grid_sha256": sha256(json.dumps(times, separators=(",", ":")).encode()).hexdigest(),
            "flight_time_step_days": round(step, 8),
            "flight_duration_brackets_days": ([list(map(float,flight_range_days))]
                 if flight_range_days is not None else [list(b) for b in TOF_BRACKETS]),
            "flight_sample_count": len(times),
            "transfer_family": TRANSFER_FAMILY,
            "source_origin_sha256": src_o.sha256,
            "source_destination_sha256": src_d.sha256,
            "source_origin_id": src_o.ephemeris_source_id,
            "source_destination_id": src_d.ephemeris_source_id,
            "solver": "lamberthub.izzo2015",
            "solver_version": version("lamberthub"),
        }

    def geometry(self, origin, destination, departure, *, strategy="daily",
                 flight_range_days=None):
        if (origin, destination) not in ROUTES:
            raise ValueError("ROUTE_NOT_IN_NARROW_PILOT")
        if strategy not in ("daily", "distance_research"):
            raise ValueError("UNKNOWN_SAMPLING_STRATEGY")
        epoch = _day(departure)
        step = (DENSE_FLIGHT_STEP_DAYS if strategy == "daily"
                else self.steps_at(origin, destination, epoch)["flight_step_days"])
        times = self._times(step, flight_range_days)
        key = self._key(origin, destination, epoch, times, step, flight_range_days)
        raw_key = json.dumps(key, sort_keys=True, separators=(",", ":")).encode()
        fingerprint = sha256(raw_key).hexdigest()
        if fingerprint in self._geometry:
            return self._geometry[fingerprint]
        path = self.cache_dir / (fingerprint + ".json") if self.cache_dir else None
        if path is not None and path.exists():
            data = json.loads(path.read_text())
            if data["key"] != key:
                raise ValueError("GEOMETRY_CACHE_KEY_MISMATCH")
            self._geometry[fingerprint] = data
            return data

        original, origin_class = self._state(origin, epoch)
        if origin_class != "DIRECT":
            raise ValueError("UNQUALIFIED_ORIGIN")
        dates = [epoch + timedelta(days=t) for t in times]
        dest_states, src, _ = self._batch_states(destination, dates)
        first_position = np.asarray(original.position_km, dtype=np.float64)
        r1 = np.repeat(first_position[None, :], len(times), axis=0)
        v1, v2 = batched_izzo(legacy.SUN_GM_KM3_S2,
                             r1, dest_states[:, :3],
                             np.asarray(times) * 86400.)
        self.solve_count += len(times)
        departure_speeds = np.linalg.norm(
            v1 - np.asarray(original.velocity_km_s), axis=1)
        arrival_speeds = np.linalg.norm(v2 - dest_states[:, 3:], axis=1)
        rows = []
        for t, vdep, varr in zip(times, departure_speeds, arrival_speeds):
            if math.isfinite(float(vdep)) and math.isfinite(float(varr)):
                rows.append({
                    "flight_days": round(float(t), 8),
                    "departure_vinf_km_s": round(float(vdep), 7),
                    "arrival_vinf_km_s": round(float(varr), 7),
                })
        retained = pareto_geometry(rows)
        data = {"key": key, "sampled_solutions": len(rows),
                "retained_solutions": len(retained), "trajectories": retained,
                "standing": "TEST_ONLY_GEOMETRY_NOT_MISSION_DESIGN"}
        self._geometry[fingerprint] = data
        if path is not None:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, sort_keys=True,
                                       separators=(",", ":")) + "\n")
        return data

    @staticmethod
    def admissible(geometry, *, departure_limit, arrival_limit):
        """A lookup filter, deliberately absent from geometry and its key."""
        if departure_limit < 0 or arrival_limit < 0:
            raise ValueError("NEGATIVE_SPEED_LIMIT")
        return [r for r in geometry["trajectories"]
                if r["departure_vinf_km_s"] <= departure_limit
                and r["arrival_vinf_km_s"] <= arrival_limit]

    def lookup(self, origin, destination, ready_date, *, wait_limit_days,
               departure_limit, arrival_limit, strategy="daily",
               flight_range_days=None):
        """Every calendar departure inside [ready, ready+wait), plus research subdays."""
        if not isinstance(wait_limit_days, int) or wait_limit_days < 1:
            raise ValueError("INVALID_WAIT_LIMIT_DAYS")
        start = _day(ready_date)
        found = []
        for i in range(wait_limit_days):
            day = start + timedelta(days=i)
            departures = [day]
            if strategy == "distance_research":
                step = self.steps_at(origin, destination, day)["departure_step_days"]
                departures.extend(day + timedelta(days=k * step)
                                  for k in range(1, math.ceil(1 / step))
                                  if k * step < 1)
            for epoch in departures:
                geometry_kw = ({"flight_range_days": flight_range_days}
                               if flight_range_days is not None else {})
                geometry = self.geometry(origin, destination, epoch, strategy=strategy,
                                         **geometry_kw)
                options = self.admissible(geometry, departure_limit=departure_limit,
                                          arrival_limit=arrival_limit)
                if options:
                    found.append({"departure": _iso(epoch), "options": options})
        return {"origin": origin, "destination": destination,
                "ready_date": _iso(start), "wait_limit_days": wait_limit_days,
                "sampling_strategy": strategy, "opportunities": found,
                "note": "Sample-bound impulsive geometry only; not mission qualification"}
