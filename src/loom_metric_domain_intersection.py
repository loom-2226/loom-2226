"""Deterministic metric-trajectory intersection check for moving spherical domains.

This module consumes already-resolved trajectory and domain geometry. It does not
own ephemeris, select domain radii, calculate routes, mutate campaign state, or
expose authority to Mara. Domain centers must be supplied for the same segment
epochs as the trajectory by the authoritative navigation/ephemeris layer.
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
class MetricTrajectoryCheck:
    admissible: bool
    blocking_domains: Tuple[str, ...]


def _sub(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _scale(a: Vector3, s: float) -> Vector3:
    return (a[0] * s, a[1] * s, a[2] * s)


def _dot(a: Vector3, b: Vector3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _relative_segment_min_distance(
    ship_start: Vector3,
    ship_end: Vector3,
    domain_start: Vector3,
    domain_end: Vector3,
) -> float:
    """Exact minimum separation for linear ship/domain motion over one segment."""
    r0 = _sub(ship_start, domain_start)
    ship_delta = _sub(ship_end, ship_start)
    domain_delta = _sub(domain_end, domain_start)
    relative_delta = _sub(ship_delta, domain_delta)
    denom = _dot(relative_delta, relative_delta)
    if denom == 0.0:
        return sqrt(_dot(r0, r0))
    u = -_dot(r0, relative_delta) / denom
    u = min(1.0, max(0.0, u))
    closest = _add(r0, _scale(relative_delta, u))
    return sqrt(_dot(closest, closest))


def segment_intersects_moving_domain(
    ship_start: TimedPosition,
    ship_end: TimedPosition,
    domain: MovingDomainSegment,
) -> bool:
    if ship_end.epoch <= ship_start.epoch:
        raise ValueError("trajectory segment epochs must increase")
    if ship_start.epoch != domain.start.epoch or ship_end.epoch != domain.end.epoch:
        raise ValueError("trajectory/domain epochs must match; interpolate from ephemeris first")
    distance = _relative_segment_min_distance(
        ship_start.position,
        ship_end.position,
        domain.start.position,
        domain.end.position,
    )
    return distance <= domain.radius


def check_metric_trajectory(
    trajectory: Sequence[TimedPosition],
    domains: Iterable[MovingDomainSegment],
    preferences: NavigationPreferences,
) -> MetricTrajectoryCheck:
    """Check one metric segment against moving exclusion domains.

    The first seam intentionally accepts exactly two trajectory states. Navigator
    can later call this per segment for a piecewise trajectory/ephemeris solution.
    """
    if len(trajectory) != 2:
        raise ValueError("first metric-domain seam requires exactly one trajectory segment")
    start, end = trajectory
    blockers = []
    for domain in domains:
        if (
            domain.exclusion_class is ExclusionClass.REGULATORY
            and not preferences.obey_regulatory_exclusions
        ):
            continue
        if segment_intersects_moving_domain(start, end, domain):
            blockers.append(domain.domain_id)
    unique = tuple(dict.fromkeys(blockers))
    return MetricTrajectoryCheck(admissible=not unique, blocking_domains=unique)
