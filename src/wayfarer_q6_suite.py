from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence


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
