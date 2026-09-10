from __future__ import annotations

from typing import Any, Mapping


REQUIRED_MASS_FIELDS = (
    "departure_remass_t",
    "planned_remass_used_t",
    "planned_arrival_remass_t",
)


def _require_number(mapping: Mapping[str, Any], key: str) -> float:
    if key not in mapping:
        raise KeyError(key)
    value = mapping[key]
    if not isinstance(value, (int, float)):
        raise TypeError(f"{key} must be numeric")
    return float(value)


def score_navigator_result(result: Mapping[str, Any], protected_dispatch_floor_t: float) -> dict:
    """Score a Navigator preview/plan result against a remass floor.

    The adapter consumes Navigator's existing output contract rather than duplicating
    route physics. It is intentionally agnostic to route geometry and strategy.
    """
    if protected_dispatch_floor_t < 0:
        raise ValueError("protected_dispatch_floor_t must be non-negative")
    mass = result.get("mass")
    if not isinstance(mass, Mapping):
        raise KeyError("mass")
    departure = _require_number(mass, "departure_remass_t")
    used = _require_number(mass, "planned_remass_used_t")
    arrival = _require_number(mass, "planned_arrival_remass_t")
    if departure <= 0:
        raise ValueError("departure_remass_t must be positive")
    if used < 0 or arrival < 0:
        raise ValueError("remass values must be non-negative")
    # Navigator owns the authoritative burn integration. We only sanity-check
    # arithmetic and score reserve posture here.
    arithmetic_error_t = arrival - (departure - used)
    speeds = result.get("speeds") if isinstance(result.get("speeds"), Mapping) else {}
    torch = result.get("torch") if isinstance(result.get("torch"), Mapping) else {}
    return {
        "departure_remass_t": departure,
        "remass_used_t": used,
        "arrival_remass_t": arrival,
        "fraction_of_departure_remass_used": used / departure,
        "protected_dispatch_floor_t": float(protected_dispatch_floor_t),
        "reserve_margin_t": arrival - float(protected_dispatch_floor_t),
        "dispatch_floor_pass": arrival >= float(protected_dispatch_floor_t),
        "navigator_mass_arithmetic_error_t": arithmetic_error_t,
        "terminal_delta_v_km_s": speeds.get("terminal_delta_v_km_s"),
        "exhaust_velocity_km_s": speeds.get("exhaust_velocity_km_s"),
        "torch_burn_s": torch.get("burn_s"),
        "source_contract": "Navigator.mass/speeds/torch",
        "qualification_status": "DERIVED_FROM_NAVIGATOR_RESULT",
    }
