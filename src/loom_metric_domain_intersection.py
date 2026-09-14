"""Deterministic checks for metric trajectories against moving spherical domains.

This module consumes aligned trajectory/domain geometry supplied by navigation and
ephemeris authority. It owns no ephemeris, radius policy, route generation, campaign
state, or Mara numerical authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import sqrt
from typing import Iterable, Sequence, Tuple

from src.loom_metric_domain_routing import NavigationPreferences

Vector3 = Tuple[float, float, float]


class ExclusionClass(str, Enum):
    PHYSICAL = "PHYSICAL"
    REGULATORY = "REGULATORY"


@dataclass(frozen=True)
class TimedPosition:
    epoch: float
    position: Vector3


@dataclass(frozen=True)
class MovingDomainSegment:
    domain_id: str
    exclusion_class: ExclusionClass
    radius: float
    start: TimedPosition
    end: TimedPosition

    def __post_init__(self) -> None:
        if self.radius < 0.0:
            raise ValueError("domain radius must be non-negative")
        if self.end.epoch <= self.start.epoch:
            raise ValueError("domain segment epochs must increase")


@dataclass(frozen=True)
class DomainEncounter:
    domain_id: str
    exclusion_class: ExclusionClass
    segment_index: int
    closest_fraction: float
    closest_epoch: float
    minimum_distance: float
    minimum_clearance: float


@dataclass(frozen=True)
class MetricTrajectoryCheck:
    admissible: bool
    blocking_domains: Tuple[str, ...]
    blocking_segment_indexes: Tuple[int, ...] = ()
    encounters: Tuple[DomainEncounter, ...] = ()


def _sub(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _scale(a: Vector3, s: float) -> Vector3:
    return (a[0] * s, a[1] * s, a[2] * s)


def _dot(a: Vector3, b: Vector3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _relative_segment_closest(ship_start: Vector3, ship_end: Vector3, domain_start: Vector3, domain_end: Vector3) -> Tuple[float, float]:
    r0 = _sub(ship_start, domain_start)
    relative_delta = _sub(_sub(ship_end, ship_start), _sub(domain_end, domain_start))
    denom = _dot(relative_delta, relative_delta)
    if denom == 0.0:
        return sqrt(_dot(r0, r0)), 0.0
    u = min(1.0, max(0.0, -_dot(r0, relative_delta) / denom))
    closest = _add(r0, _scale(relative_delta, u))
    return sqrt(_dot(closest, closest)), u


def _validate_aligned(ship_start: TimedPosition, ship_end: TimedPosition, domain: MovingDomainSegment) -> None:
    if ship_end.epoch <= ship_start.epoch:
        raise ValueError("trajectory segment epochs must increase")
    if ship_start.epoch != domain.start.epoch or ship_end.epoch != domain.end.epoch:
        raise ValueError("trajectory/domain epochs must match; interpolate from ephemeris first")


def segment_intersects_moving_domain(ship_start: TimedPosition, ship_end: TimedPosition, domain: MovingDomainSegment) -> bool:
    _validate_aligned(ship_start, ship_end, domain)
    distance, _ = _relative_segment_closest(ship_start.position, ship_end.position, domain.start.position, domain.end.position)
    return distance <= domain.radius


def _encounter(ship_start: TimedPosition, ship_end: TimedPosition, domain: MovingDomainSegment, segment_index: int) -> DomainEncounter:
    _validate_aligned(ship_start, ship_end, domain)
    distance, u = _relative_segment_closest(ship_start.position, ship_end.position, domain.start.position, domain.end.position)
    return DomainEncounter(
        domain_id=domain.domain_id,
        exclusion_class=domain.exclusion_class,
        segment_index=segment_index,
        closest_fraction=u,
        closest_epoch=ship_start.epoch + u * (ship_end.epoch - ship_start.epoch),
        minimum_distance=distance,
        minimum_clearance=distance - domain.radius,
    )


def check_metric_trajectory(trajectory: Sequence[TimedPosition], domains: Iterable[MovingDomainSegment], preferences: NavigationPreferences) -> MetricTrajectoryCheck:
    """Backward-compatible one-segment check."""
    if len(trajectory) != 2:
        raise ValueError("single metric-trajectory check requires exactly one segment")
    return check_metric_route(trajectory, domains, preferences)


def check_metric_route(
    trajectory: Sequence[TimedPosition],
    domains: Iterable[MovingDomainSegment],
    preferences: NavigationPreferences,
    *,
    origin_domain_id: str | None = None,
    destination_domain_id: str | None = None,
) -> MetricTrajectoryCheck:
    """Check every metric leg against its exactly aligned moving-domain segments.

    The authorized origin domain is exempt on the first leg only. The authorized
    destination domain is exempt on the final leg only. These are transition
    exemptions, not general permission to cross the same domain elsewhere.
    """
    if len(trajectory) < 2:
        raise ValueError("metric route requires at least two timed positions")
    for a, b in zip(trajectory, trajectory[1:]):
        if b.epoch <= a.epoch:
            raise ValueError("trajectory epochs must strictly increase")

    supplied = tuple(domains)
    expected_legs = {(trajectory[i].epoch, trajectory[i + 1].epoch) for i in range(len(trajectory) - 1)}
    for domain in supplied:
        key = (domain.start.epoch, domain.end.epoch)
        if key not in expected_legs:
            raise ValueError("domain segment must align exactly to one trajectory leg")

    encounters = []
    last_leg = len(trajectory) - 2
    for i, (start, end) in enumerate(zip(trajectory, trajectory[1:])):
        leg_domains = [d for d in supplied if d.start.epoch == start.epoch and d.end.epoch == end.epoch]
        for domain in leg_domains:
            if domain.exclusion_class is ExclusionClass.REGULATORY and not preferences.obey_regulatory_exclusions:
                continue
            hit = _encounter(start, end, domain, i)
            if hit.minimum_clearance > 0.0:
                continue
            if i == 0 and origin_domain_id and domain.domain_id == origin_domain_id:
                continue
            if i == last_leg and destination_domain_id and domain.domain_id == destination_domain_id:
                continue
            encounters.append(hit)

    blockers = tuple(dict.fromkeys(hit.domain_id for hit in encounters))
    segments = tuple(dict.fromkeys(hit.segment_index for hit in encounters))
    return MetricTrajectoryCheck(
        admissible=not encounters,
        blocking_domains=blockers,
        blocking_segment_indexes=segments,
        encounters=tuple(encounters),
    )
