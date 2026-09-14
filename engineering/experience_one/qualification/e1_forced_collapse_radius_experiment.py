#!/usr/bin/env python3
from __future__ import annotations

"""E1 diagnostic: force candidate destination collapse radii through NAV-V1-A's seam.

This does NOT change runtime Navigator physics. It reuses Navigator SOURCE-010,
`_state_primary`, `_metric_time_s`, `_torch_burn`, `_burn_displacement`, and the
same velocity-memory assumption as NAV-V1-A to ask a bounded question:

If metric collapse had to occur at a much larger Neptune-centered radius, can the
current local model (coast at carried ordinary velocity, then the existing terminal
burn) still close within the authoritative SOURCE-010 axis, and at what cost?

Candidate Hill/SOI values are diagnostic comparators only. They are not adopted
metric policy or canon.
"""

import json
import math
import sys
import tempfile
import time
from datetime import timedelta
from pathlib import Path
from typing import Any, Callable

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src import loom_navigator_core as campaign

DEPARTURE = "2226-08-22T01:32:00Z"
EARNED_ARRIVAL = "2226-08-22T09:45:17.864616Z"

# Diagnostic-only reference constants used solely to reproduce the already-researched
# Neptune candidate ordering. They are deliberately isolated from runtime authority.
AU_KM = 149_597_870.7
NEPTUNE_A_AU_DIAGNOSTIC = 30.07
NEPTUNE_E_DIAGNOSTIC = 0.008678
NEPTUNE_TO_SUN_MASS_RATIO_DIAGNOSTIC = 5.15034172e-5


def candidate_neptune_radii_km() -> list[dict[str, float | str]]:
    a_km = NEPTUNE_A_AU_DIAGNOSTIC * AU_KM
    q_km = a_km * (1.0 - NEPTUNE_E_DIAGNOSTIC)
    hill_peri = q_km * (NEPTUNE_TO_SUN_MASS_RATIO_DIAGNOSTIC / 3.0) ** (1.0 / 3.0)
    soi = a_km * NEPTUNE_TO_SUN_MASS_RATIO_DIAGNOSTIC ** (2.0 / 5.0)
    return [
        {"id": "HALF_HILL_PERIAPSIS", "radius_km": 0.5 * hill_peri},
        {"id": "LAPLACE_SOI", "radius_km": soi},
        {"id": "HILL_PERIAPSIS", "radius_km": hill_peri},
    ]


def bracketed_bisect(fn: Callable[[float], float], lo: float, hi: float, *, tol: float = 1e-7, max_iter: int = 100) -> float:
    flo = fn(lo)
    fhi = fn(hi)
    if flo == 0:
        return lo
    if fhi == 0:
        return hi
    if flo * fhi > 0:
        raise ValueError("root is not bracketed")
    for _ in range(max_iter):
        mid = (lo + hi) / 2.0
        fm = fn(mid)
        if abs(fm) <= tol or (hi - lo) <= tol:
            return mid
        if flo * fm <= 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
    return (lo + hi) / 2.0


def _route_scoped_acquisition(nav: Any, normalized: dict[str, Any], cache: Path) -> tuple[dict[str, Any], set[str]]:
    _, _, trace = nav.acquisition_window(normalized)
    full_plan = nav.build_acquisition_plan(normalized)
    required_ids = {nav.ROUTE_OBJECTS[token]["base_id"] for token in normalized["route"]}
    if required_ids != {"CE", "NE"}:
        raise RuntimeError(f"unexpected E1 dependencies: {sorted(required_ids)}")
    route_plan = [i for i in full_plan if i["scope"] == "BASE" and i["id"] in required_ids]
    session = nav.build_session()
    entries = []
    hits = fetched = 0
    t0 = time.perf_counter()
    for item in route_plan:
        req = item["request"]
        r = nav.fetch_or_cache(req, cache, session, offline=False, refresh=False)
        hits += int(r["status"] == "CACHE_HIT")
        fetched += int(r["status"] == "FETCHED")
        entries.append({**{k: v for k, v in item.items() if k != "request"}, "request": req.canonical(), **r})
    return {
        "schema": "LOOM_NAV_EPHEMERIS_ACQUISITION_INDEX_v1",
        "workflow_version": nav.WORKFLOW_VERSION,
        "test_id": normalized["test_id"],
        "epoch_utc": normalized["epoch_utc"],
        "policy": nav.EPHEMERIS_POLICY,
        "window_trace": trace,
        "request_count": len(route_plan),
        "cache_hits": hits,
        "fetched": fetched,
        "direct_unavailable": 0,
        "cache_bytes_touched": sum(int(e.get("cache_bytes", 0)) for e in entries),
        "raw_archive_bytes_written": sum(int(e.get("raw_archive_bytes", 0)) for e in entries),
        "elapsed_seconds": round(time.perf_counter() - t0, 6),
        "entries": entries,
        "authority": {"source": "SOURCE-010", "derived_scientific_values_in_cache": False, "llm_calculation_authority": "ZERO"},
    }, required_ids


def _axis_limit_seconds(nav: Any, axis: dict[str, Any], rows: list[tuple[float, ...]], departure: Any) -> float:
    start = nav._dt(axis["start_utc"])
    step = float(axis["step_seconds"])
    end = start + timedelta(seconds=step * (len(rows) - 1))
    return (end - departure).total_seconds()


def _find_sign_bracket(fn: Callable[[float], float], lo: float, hi: float, *, samples: int = 160) -> tuple[float, float] | None:
    last_x = None
    last_f = None
    for i in range(samples + 1):
        x = lo + (hi - lo) * (i / samples)
        try:
            fx = fn(x)
        except Exception:
            continue
        if fx == 0:
            return x, x
        if last_x is not None and last_f is not None and last_f * fx < 0:
            return last_x, x
        last_x, last_f = x, fx
    return None


def _solve_with_coast(nav: Any, departure: Any, origin_rows: list[tuple[float, ...]], dest_rows: list[tuple[float, ...]], axis: dict[str, Any], metric_mode: str, torch_mode: str, wet_mass_t: float, coast_s: float) -> dict[str, Any]:
    origin = nav._state_primary(origin_rows, departure, axis)
    p0 = nav._pos_km(origin)
    v0 = nav._vel_km_s(origin)
    axis_limit_s = _axis_limit_seconds(nav, axis, dest_rows, departure)

    def evaluate(total_s: float) -> tuple[float, dict[str, Any]]:
        arrival = departure + timedelta(seconds=total_s)
        target = nav._state_primary(dest_rows, arrival, axis)
        burn = nav._torch_burn(nav._vsub(nav._vel_km_s(target), v0), torch_mode, wet_mass_t)
        coast_disp = nav._vscale(v0, coast_s)
        burn_disp = nav._burn_displacement(v0, burn)
        ordinary_disp = nav._vadd(coast_disp, burn_disp)
        collapse_p = nav._vsub(nav._pos_km(target), ordinary_disp)
        distance_km = nav._vnorm(nav._vsub(collapse_p, p0))
        metric_s = nav._metric_time_s(distance_km, metric_mode)
        residual_s = metric_s + coast_s + burn["burn_s"] - total_s
        collapse_epoch = departure + timedelta(seconds=metric_s)
        center_at_collapse = nav._pos_km(nav._state_primary(dest_rows, collapse_epoch, axis))
        radius_km = nav._vnorm(nav._vsub(collapse_p, center_at_collapse))
        return residual_s, {
            "arrival": arrival,
            "collapse_epoch": collapse_epoch,
            "collapse_position_km": collapse_p,
            "collapse_radius_km": radius_km,
            "metric_distance_km": distance_km,
            "metric_duration_s": metric_s,
            "coast_s": coast_s,
            "burn": burn,
        }

    low = max(0.0, coast_s)
    high = max(low + 1.0, axis_limit_s - 1e-6)
    bracket = _find_sign_bracket(lambda t: evaluate(t)[0], low, high)
    if bracket is None:
        raise RuntimeError("no NAV-V1-A timing closure within current SOURCE-010 axis for requested coast")
    if bracket[0] == bracket[1]:
        total = bracket[0]
    else:
        total = bracketed_bisect(lambda t: evaluate(t)[0], bracket[0], bracket[1], tol=1e-6)
    residual, meta = evaluate(total)
    meta["total_duration_s"] = total
    meta["timing_residual_s"] = residual
    meta["ordinary_local_duration_s"] = coast_s + meta["burn"]["burn_s"]
    return meta


def forced_radius_case(nav: Any, departure: Any, origin_rows: list[tuple[float, ...]], dest_rows: list[tuple[float, ...]], axis: dict[str, Any], metric_mode: str, torch_mode: str, wet_mass_t: float, target_radius_km: float) -> dict[str, Any]:
    axis_limit_s = _axis_limit_seconds(nav, axis, dest_rows, departure)
    feasible: list[tuple[float, dict[str, Any]]] = []
    max_coast = max(0.0, axis_limit_s - 1.0)
    for i in range(81):
        coast = max_coast * (i / 80.0)
        try:
            meta = _solve_with_coast(nav, departure, origin_rows, dest_rows, axis, metric_mode, torch_mode, wet_mass_t, coast)
        except Exception:
            continue
        feasible.append((coast, meta))
    if not feasible:
        return {"status": "NO_TIMING_SOLUTION_WITHIN_SOURCE010_AXIS", "target_radius_km": target_radius_km}

    feasible.sort(key=lambda x: x[0])
    min_r = min(m["collapse_radius_km"] for _, m in feasible)
    max_r = max(m["collapse_radius_km"] for _, m in feasible)
    if not (min_r <= target_radius_km <= max_r):
        best = max(feasible, key=lambda x: x[1]["collapse_radius_km"])
        return {
            "status": "TARGET_RADIUS_OUTSIDE_CURRENT_SOURCE010_AXIS",
            "target_radius_km": target_radius_km,
            "reachable_radius_min_km": min_r,
            "reachable_radius_max_km": max_r,
            "max_reachable_case": {
                "coast_s": best[0],
                "ordinary_local_duration_s": best[1]["ordinary_local_duration_s"],
                "total_duration_s": best[1]["total_duration_s"],
                "collapse_radius_km": best[1]["collapse_radius_km"],
            },
        }

    bracket = None
    prev = feasible[0]
    for cur in feasible[1:]:
        f0 = prev[1]["collapse_radius_km"] - target_radius_km
        f1 = cur[1]["collapse_radius_km"] - target_radius_km
        if f0 == 0:
            bracket = (prev[0], prev[0])
            break
        if f0 * f1 <= 0:
            bracket = (prev[0], cur[0])
            break
        prev = cur
    if bracket is None:
        return {"status": "RADIUS_NOT_BRACKETED_DESPITE_RANGE", "target_radius_km": target_radius_km}

    def radius_residual(coast: float) -> float:
        return _solve_with_coast(nav, departure, origin_rows, dest_rows, axis, metric_mode, torch_mode, wet_mass_t, coast)["collapse_radius_km"] - target_radius_km

    coast = bracket[0] if bracket[0] == bracket[1] else bracketed_bisect(radius_residual, bracket[0], bracket[1], tol=1e-3)
    meta = _solve_with_coast(nav, departure, origin_rows, dest_rows, axis, metric_mode, torch_mode, wet_mass_t, coast)
    burn = meta["burn"]
    return {
        "status": "SOLVED_WITHIN_CURRENT_SOURCE010_AXIS",
        "target_radius_km": target_radius_km,
        "collapse_radius_km": meta["collapse_radius_km"],
        "collapse_epoch_utc": nav._iso_precise(meta["collapse_epoch"]),
        "arrival_epoch_utc": nav._iso_precise(meta["arrival"]),
        "metric_duration_s": meta["metric_duration_s"],
        "coast_s": coast,
        "terminal_burn_s": burn["burn_s"],
        "ordinary_local_duration_s": meta["ordinary_local_duration_s"],
        "total_duration_s": meta["total_duration_s"],
        "delta_v_km_s": burn["delta_v_km_s"],
        "remass_used_t": burn["remass_used_t"],
        "timing_residual_s": meta["timing_residual_s"],
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="loom-e1-forced-radius-") as td:
        root = Path(td)
        nav = campaign._load_core(root / "core")
        mission = {
            "schema": nav.MISSION_SCHEMA,
            "test_id": "E1_FORCED_COLLAPSE_RADIUS_EXPERIMENT",
            "epoch": {"local": "2226-08-22T01:32:00", "timezone": "UTC", "fold": 0},
            "route": ["CERES", "NEPTUNE_SYSTEM"],
            "ship": "WAYFARER_BASELINE",
            "requested_modes": {"metric": "HARD", "torch": "CRUISE"},
        }
        normalized = nav.validate_and_normalize_mission(mission)
        cache = root / "cache"
        acquisition, required_ids = _route_scoped_acquisition(nav, normalized, cache)
        canonical, axis_validation = nav.build_canonical_dependency_index(acquisition, cache)
        if axis_validation.get("status") != "PASS":
            raise RuntimeError(f"canonical axis qualification failed: {axis_validation}")
        origin, dest = normalized["route"]
        rr0 = {"request": origin, **nav.ROUTE_OBJECTS[origin]}
        rr1 = {"request": dest, **nav.ROUTE_OBJECTS[dest]}
        rows0, _ = nav._route_rows_from_canonical(rr0, canonical, cache)
        rows1, _ = nav._route_rows_from_canonical(rr1, canonical, cache)
        departure = nav._dt(normalized["epoch_utc"])
        state = campaign._new_state("E1-FORCED-RADIUS", "WAYFARER-E1")
        wet = float(state["ship"]["wet_mass_t"])

        baseline = nav._solve_leg(origin, dest, departure, rows0, rows1, canonical["time_axis"], "HARD", "CRUISE", wet)
        collapse_epoch = nav._dt(baseline["metric_segment"]["collapse_epoch_utc"])
        center = nav._pos_km(nav._state_primary(rows1, collapse_epoch, canonical["time_axis"]))
        baseline_radius = nav._vnorm(nav._vsub(baseline["metric_segment"]["collapse_position_km_j2000_ecliptic"], center))
        axis_limit_s = _axis_limit_seconds(nav, canonical["time_axis"], rows1, departure)

        cases = []
        for candidate in candidate_neptune_radii_km():
            case = forced_radius_case(nav, departure, rows0, rows1, canonical["time_axis"], "HARD", "CRUISE", wet, float(candidate["radius_km"]))
            cases.append({**candidate, **case})

        result = {
            "schema": "LOOM_E1_FORCED_COLLAPSE_RADIUS_EXPERIMENT_V1",
            "status": "PASS",
            "route": normalized["route"],
            "source_authority": acquisition["authority"]["source"],
            "axis_qualification": axis_validation["status"],
            "acquisition_dependency_ids": sorted(required_ids),
            "model": "NAV-V1-A_DIAGNOSTIC_EXTENSION_COAST_THEN_EXISTING_TERMINAL_BURN",
            "model_note": "No runtime physics mutation. Coast extension preserves NAV-V1-A ordinary velocity memory and existing terminal burn; candidate radii are diagnostic only.",
            "source010_axis_seconds_after_departure": axis_limit_s,
            "baseline": {
                "collapse_radius_km": baseline_radius,
                "collapse_epoch_utc": baseline["metric_segment"]["collapse_epoch_utc"],
                "arrival_epoch_utc": baseline["arrival"]["epoch_utc"],
                "arrival_matches_earned_e1": baseline["arrival"]["epoch_utc"] == EARNED_ARRIVAL,
                "ordinary_local_duration_s": baseline["terminal_burn"]["burn_s"],
                "delta_v_km_s": baseline["terminal_burn"]["delta_v_km_s"],
                "remass_used_t": baseline["terminal_burn"]["remass_used_t"],
            },
            "candidate_radii_provenance": "DIAGNOSTIC_STANDARD_HILL_LAPLACE_FORMULAE_NOT_RUNTIME_AUTHORITY_NOT_ADOPTED_POLICY",
            "cases": cases,
            "authority_note": "READ_ONLY_DIAGNOSTIC_NO_CAMPAIGN_MUTATION_NO_RUNTIME_POLICY_CHANGE_LLM_AUTHORITY_ZERO",
            "next_action": "INTERPRET_RADIUS_FEASIBILITY_BEFORE_ANY_METRIC_DOMAIN_POLICY_ADOPTION",
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
