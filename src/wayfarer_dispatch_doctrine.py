from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


MODE_POLICY = {
    "ECON": "ROUTINE_BULK_DV",
    "CRUISE": "ROUTINE_BULK_DV",
    "EXPEDITE": "TIME_CRITICAL_COSTED",
    "FAST": "EXCEPTIONAL_AUTHORIZED",
    "HARD": "EMERGENCY_OR_TACTICAL",
    "LIMIT": "CONTINGENCY_ONLY",
}


@dataclass(frozen=True)
class DispatchPolicy:
    normal_dispatch_remass_t: float
    minimum_dispatch_remass_t: float
    protected_optimizer_reserve_t: float
    contingency_feed_reserve_t: float = 0.0
    one_tank_isolation_fraction: float = 0.25

    def validate(self) -> None:
        vals = (
            self.normal_dispatch_remass_t,
            self.minimum_dispatch_remass_t,
            self.protected_optimizer_reserve_t,
            self.contingency_feed_reserve_t,
        )
        if any(v < 0 for v in vals):
            raise ValueError("dispatch values must be non-negative")
        if self.minimum_dispatch_remass_t > self.normal_dispatch_remass_t:
            raise ValueError("minimum dispatch cannot exceed normal dispatch")
        if self.protected_optimizer_reserve_t > self.minimum_dispatch_remass_t:
            raise ValueError("optimizer reserve cannot exceed minimum dispatch")
        if not 0.0 <= self.one_tank_isolation_fraction < 1.0:
            raise ValueError("one_tank_isolation_fraction must be in [0,1)")


def mode_authorized(mode: str, urgency_class: str) -> bool:
    """Return whether a torch mode is permitted for the requested urgency class.

    Urgency classes are ROUTINE, TIME_CRITICAL, EXCEPTIONAL, EMERGENCY, CONTINGENCY.
    Higher classes may use all lower-class modes.
    """
    rank = {"ROUTINE": 0, "TIME_CRITICAL": 1, "EXCEPTIONAL": 2, "EMERGENCY": 3, "CONTINGENCY": 4}
    minimum = {
        "ECON": 0,
        "CRUISE": 0,
        "EXPEDITE": 1,
        "FAST": 2,
        "HARD": 3,
        "LIMIT": 4,
    }
    m = mode.upper()
    u = urgency_class.upper()
    if m not in minimum:
        raise KeyError(m)
    if u not in rank:
        raise KeyError(u)
    return rank[u] >= minimum[m]


def dispatch_assessment(
    planned_remass_used_t: float,
    dispatch_remass_t: float,
    policy: DispatchPolicy,
    *,
    tank_isolated: bool = False,
    alternate_feed_only: bool = False,
    alternate_feed_usable_fraction: float = 1.0,
) -> dict:
    policy.validate()
    if planned_remass_used_t < 0 or dispatch_remass_t < 0:
        raise ValueError("remass values must be non-negative")
    if not 0.0 <= alternate_feed_usable_fraction <= 1.0:
        raise ValueError("alternate_feed_usable_fraction must be in [0,1]")

    accessible = dispatch_remass_t
    if tank_isolated:
        accessible *= 1.0 - policy.one_tank_isolation_fraction
    if alternate_feed_only:
        accessible *= alternate_feed_usable_fraction

    arrival = accessible - planned_remass_used_t
    reserve_margin = arrival - policy.protected_optimizer_reserve_t
    minimum_dispatch_pass = dispatch_remass_t >= policy.minimum_dispatch_remass_t
    mission_pass = arrival >= policy.protected_optimizer_reserve_t

    if not minimum_dispatch_pass:
        disposition = "NO_DISPATCH"
    elif mission_pass:
        disposition = "PASS"
    elif arrival >= 0:
        disposition = "DIVERT_OR_REPLAN"
    else:
        disposition = "MISSION_INFEASIBLE"

    return {
        "dispatch_remass_t": dispatch_remass_t,
        "accessible_remass_t": accessible,
        "planned_remass_used_t": planned_remass_used_t,
        "arrival_remass_t": arrival,
        "protected_optimizer_reserve_t": policy.protected_optimizer_reserve_t,
        "reserve_margin_t": reserve_margin,
        "minimum_dispatch_pass": minimum_dispatch_pass,
        "mission_pass": mission_pass,
        "tank_isolated": tank_isolated,
        "alternate_feed_only": alternate_feed_only,
        "alternate_feed_usable_fraction": alternate_feed_usable_fraction,
        "disposition": disposition,
    }


def degraded_system_actions(state: Mapping[str, bool]) -> tuple[str, ...]:
    """Deterministic minimum actions for key Q7 degraded states.

    This is policy logic only; it does not model trajectories or repair success.
    """
    actions: list[str] = []
    if state.get("metric_unavailable", False):
        actions += ["REPLAN_ORDINARY_SPACE", "PRESERVE_BULK_DV_MODES", "CHECK_DIVERSION"]
    if state.get("torch_unavailable", False):
        actions += ["CANCEL_HIGH_DV_DEPARTURE", "USE_RCS_FOR_SAFETY_ONLY", "SEEK_TUG_OR_SAFE_HAVEN"]
    if state.get("radiator_degraded", False):
        actions += ["DERATE_DUTY_CYCLE", "BLOCK_THERMALLY_UNCLOSED_MODE"]
    if state.get("reactor_or_bus_degraded", False):
        actions += ["DERATE_RCS", "BLOCK_POWER_UNCLOSED_MODE"]
    if state.get("tank_isolated", False):
        actions += ["RECOMPUTE_ACCESSIBLE_REMASS", "REBALANCE_MASS_PROPERTIES"]
    if state.get("primary_feed_unavailable", False):
        actions += ["LOAD_CERTIFIED_ALTERNATE_ONLY", "APPLY_ALTERNATE_DERATING"]
    if state.get("rcs_cluster_lost", False):
        actions += ["RECOMPUTE_CONTROL_AUTHORITY", "BLOCK_GEOMETRICALLY_UNCLOSED_DOCKING"]
    if state.get("attitude_system_degraded", False):
        actions += ["REDUCE_SLEW_ENVELOPE", "INCREASE_SETTLE_MARGIN"]
    return tuple(dict.fromkeys(actions))
