from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

from src.wayfarer_dispatch_doctrine import DispatchPolicy, dispatch_assessment


def _route_id(result: Mapping[str, Any], index: int) -> str:
    value = result.get("route_id") or result.get("plan_id") or result.get("id")
    return str(value) if value is not None else f"route_{index:03d}"


def _remass_used(result: Mapping[str, Any]) -> float:
    mass = result.get("mass")
    if not isinstance(mass, Mapping):
        raise KeyError("mass")
    value = mass.get("planned_remass_used_t")
    if not isinstance(value, (int, float)):
        raise KeyError("planned_remass_used_t")
    value = float(value)
    if value < 0:
        raise ValueError("planned_remass_used_t must be non-negative")
    return value


def score_suite(
    results: Iterable[Mapping[str, Any]],
    candidate_dispatch_t: Sequence[float] = (100.0, 150.0, 200.0, 250.0),
    protected_floor_t: float = 50.0,
) -> dict:
    """Replay Navigator-derived remass demand against candidate dispatch inventories.

    Route physics remain owned by Navigator. This function asks only whether the
    remass demand already computed by Navigator fits inside candidate dispatch
    inventories while preserving a protected operational floor.
    """
    if protected_floor_t < 0:
        raise ValueError("protected_floor_t must be non-negative")
    rows = []
    for i, result in enumerate(results, 1):
        rows.append({"route_id": _route_id(result, i), "remass_used_t": _remass_used(result)})
    if not rows:
        raise ValueError("results must contain at least one Navigator result")
    max_row = max(rows, key=lambda r: r["remass_used_t"])
    candidates: dict[str, dict] = {}
    minimum = None
    for dispatch in sorted(float(v) for v in candidate_dispatch_t):
        if dispatch <= 0:
            raise ValueError("candidate dispatch values must be positive")
        route_scores = []
        for row in rows:
            arrival = dispatch - row["remass_used_t"]
            route_scores.append({
                "route_id": row["route_id"],
                "arrival_remass_t": arrival,
                "reserve_margin_t": arrival - protected_floor_t,
                "pass": arrival >= protected_floor_t,
            })
        all_pass = all(r["pass"] for r in route_scores)
        candidates[str(dispatch)] = {
            "dispatch_t": dispatch,
            "all_pass": all_pass,
            "minimum_arrival_remass_t": min(r["arrival_remass_t"] for r in route_scores),
            "minimum_reserve_margin_t": min(r["reserve_margin_t"] for r in route_scores),
            "routes": route_scores,
        }
        if all_pass and minimum is None:
            minimum = dispatch
    return {
        "route_count": len(rows),
        "protected_floor_t": float(protected_floor_t),
        "max_route_remass_used_t": max_row["remass_used_t"],
        "worst_case_route_id": max_row["route_id"],
        "minimum_candidate_dispatch_t": minimum,
        "candidates": candidates,
        "source": "Navigator planned_remass_used_t replay",
        "qualification_status": "DERIVED_NON_CANON",
    }


def score_suite_with_policy(
    results: Iterable[Mapping[str, Any]],
    policy: DispatchPolicy,
    candidate_dispatch_t: Sequence[float] = (100.0, 150.0, 200.0, 250.0),
    *,
    tank_isolated: bool = False,
    alternate_feed_only: bool = False,
    alternate_feed_usable_fraction: float = 1.0,
) -> dict:
    """Score Navigator mission outputs using the Q7 dispatch doctrine directly.

    This does not alter route physics. It applies minimum-dispatch, accessible-remass
    and protected-reserve policy to Navigator's planned remass usage.
    """
    policy.validate()
    rows = []
    for i, result in enumerate(results, 1):
        rows.append({"route_id": _route_id(result, i), "remass_used_t": _remass_used(result)})
    if not rows:
        raise ValueError("results must contain at least one Navigator result")

    candidates: dict[str, dict] = {}
    minimum = None
    for dispatch in sorted(float(v) for v in candidate_dispatch_t):
        route_scores = []
        for row in rows:
            assessment = dispatch_assessment(
                row["remass_used_t"],
                dispatch,
                policy,
                tank_isolated=tank_isolated,
                alternate_feed_only=alternate_feed_only,
                alternate_feed_usable_fraction=alternate_feed_usable_fraction,
            )
            route_scores.append({"route_id": row["route_id"], **assessment})
        all_pass = all(r["disposition"] == "PASS" for r in route_scores)
        candidates[str(dispatch)] = {
            "dispatch_t": dispatch,
            "all_pass": all_pass,
            "minimum_arrival_remass_t": min(r["arrival_remass_t"] for r in route_scores),
            "minimum_reserve_margin_t": min(r["reserve_margin_t"] for r in route_scores),
            "routes": route_scores,
        }
        if all_pass and minimum is None:
            minimum = dispatch

    worst = max(rows, key=lambda r: r["remass_used_t"])
    return {
        "route_count": len(rows),
        "policy": {
            "normal_dispatch_remass_t": policy.normal_dispatch_remass_t,
            "minimum_dispatch_remass_t": policy.minimum_dispatch_remass_t,
            "protected_optimizer_reserve_t": policy.protected_optimizer_reserve_t,
            "contingency_feed_reserve_t": policy.contingency_feed_reserve_t,
            "one_tank_isolation_fraction": policy.one_tank_isolation_fraction,
        },
        "degraded_case": {
            "tank_isolated": tank_isolated,
            "alternate_feed_only": alternate_feed_only,
            "alternate_feed_usable_fraction": alternate_feed_usable_fraction,
        },
        "max_route_remass_used_t": worst["remass_used_t"],
        "worst_case_route_id": worst["route_id"],
        "minimum_candidate_dispatch_t": minimum,
        "candidates": candidates,
        "source": "Navigator planned_remass_used_t + Q7 dispatch doctrine",
        "qualification_status": "DERIVED_NON_CANON",
    }
