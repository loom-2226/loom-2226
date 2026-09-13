"""Small deterministic contract for metric-entry versus local navigation domains.

This module owns no ephemeris, trajectory calculation, campaign state, or UI.
It only resolves a semantic target to the enclosing domain at which metric
flight may terminate. Moving boundary geometry remains an ephemeris/navigation
service concern.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Optional


class DomainKind(str, Enum):
    METRIC_ENTRY = "METRIC_ENTRY"
    LOCAL_ONLY = "LOCAL_ONLY"


@dataclass(frozen=True)
class DomainRule:
    target_id: str
    parent_id: Optional[str]
    kind: DomainKind


@dataclass(frozen=True)
class NavigationPreferences:
    regulatory_override_requested: bool = False

    @property
    def obey_regulatory_exclusions(self) -> bool:
        return not self.regulatory_override_requested

    @property
    def obey_physical_exclusions(self) -> bool:
        # Physical exclusion is never a semantic/player override.
        return True


@dataclass(frozen=True)
class ResolvedMetricRoute:
    requested_target: str
    metric_entry_domain: str
    local_target: str
    obey_regulatory_exclusions: bool
    obey_physical_exclusions: bool


def resolve_metric_route(
    target_id: str,
    rules: Mapping[str, DomainRule],
    preferences: NavigationPreferences,
) -> ResolvedMetricRoute:
    """Resolve target hierarchy only; do not calculate flight geometry.

    LOCAL_ONLY targets walk outward until the first METRIC_ENTRY ancestor.
    Missing, cyclic, or unterminated hierarchies fail closed.
    """
    if target_id not in rules:
        raise KeyError(f"unknown navigation target: {target_id}")

    current = target_id
    seen: set[str] = set()
    while True:
        if current in seen:
            raise ValueError(f"cyclic navigation-domain hierarchy at {current}")
        seen.add(current)
        rule = rules.get(current)
        if rule is None:
            raise KeyError(f"missing navigation-domain rule: {current}")
        if rule.kind is DomainKind.METRIC_ENTRY:
            return ResolvedMetricRoute(
                requested_target=target_id,
                metric_entry_domain=current,
                local_target=target_id,
                obey_regulatory_exclusions=preferences.obey_regulatory_exclusions,
                obey_physical_exclusions=preferences.obey_physical_exclusions,
            )
        if not rule.parent_id:
            raise ValueError(f"LOCAL_ONLY target has no metric-entry ancestor: {current}")
        current = rule.parent_id
