"""Hydrate metric-domain centers from shared celestial-state authority.

Bounded E1 seam: convert authoritative body states at route-sample epochs into
moving spherical domains consumed by the deterministic metric-domain checker.
This module does not choose domain radii, generate routes, interpolate ephemeris,
mutate campaign state, or grant Mara numerical authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol, Sequence

from src.loom_metric_domain_intersection import (
    ExclusionClass,
    MovingDomainSegment,
    TimedPosition,
)
from src.loom_spatial_state_authority import CANONICAL_FRAME, CelestialStateError, SpatialState


class CelestialResolver(Protocol):
    def resolve(self, entity_id: str, epoch_utc: str) -> SpatialState: ...


@dataclass(frozen=True)
class MetricRouteSample:
    epoch_utc: str
    position_km: tuple[float, float, float]


@dataclass(frozen=True)
class MetricDomainPolicy:
    domain_id: str
    center_entity_id: str
    exclusion_class: ExclusionClass
    radius_km: float

    def __post_init__(self) -> None:
        if not self.domain_id or not self.center_entity_id:
            raise ValueError("domain_id and center_entity_id are required")
        if self.radius_km < 0.0:
            raise ValueError("radius_km must be non-negative")


@dataclass(frozen=True)
class HydratedMetricRoute:
    trajectory: tuple[TimedPosition, ...]
    domains: tuple[MovingDomainSegment, ...]


def _epoch_seconds(epoch_utc: str) -> float:
    text = str(epoch_utc).strip()
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    dt = datetime.fromisoformat(probe)
    if dt.tzinfo is None:
        raise ValueError("route sample epoch must include timezone")
    return dt.astimezone(timezone.utc).timestamp()


def _checked_center(resolver: CelestialResolver, entity_id: str, epoch_utc: str) -> SpatialState:
    state = resolver.resolve(entity_id, epoch_utc)
    if state.reference_frame != CANONICAL_FRAME:
        raise CelestialStateError("metric-domain center is not in canonical celestial frame")
    if state.navigation_grade is not True:
        raise CelestialStateError("metric-domain routing requires navigation-grade center state")
    return state


def hydrate_metric_route(
    samples: Sequence[MetricRouteSample],
    policies: Sequence[MetricDomainPolicy],
    resolver: CelestialResolver,
) -> HydratedMetricRoute:
    """Resolve moving domains at each route leg endpoint.

    The route itself is supplied by Navigator. Radius/class policy is supplied by
    the metric-domain policy layer. Celestial position comes only from the shared
    state resolver.
    """
    if len(samples) < 2:
        raise ValueError("metric route requires at least two samples")
    ids = [p.domain_id for p in policies]
    if len(ids) != len(set(ids)):
        raise ValueError("metric domain ids must be unique")

    trajectory = tuple(TimedPosition(_epoch_seconds(s.epoch_utc), tuple(float(v) for v in s.position_km)) for s in samples)
    if any(b.epoch <= a.epoch for a, b in zip(trajectory, trajectory[1:])):
        raise ValueError("metric route sample epochs must strictly increase")

    domains = []
    for policy in policies:
        resolved = [_checked_center(resolver, policy.center_entity_id, s.epoch_utc) for s in samples]
        for i in range(len(samples) - 1):
            domains.append(
                MovingDomainSegment(
                    domain_id=policy.domain_id,
                    exclusion_class=policy.exclusion_class,
                    radius=float(policy.radius_km),
                    start=TimedPosition(trajectory[i].epoch, tuple(resolved[i].position_km)),
                    end=TimedPosition(trajectory[i + 1].epoch, tuple(resolved[i + 1].position_km)),
                )
            )
    return HydratedMetricRoute(trajectory=trajectory, domains=tuple(domains))
