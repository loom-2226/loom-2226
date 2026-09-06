"""Shared gravity-field primitives for LOOM Navigation Physics v2.

This module deliberately does *not* own ephemeris generation or trajectory
integration. It consumes explicit celestial states at a resolved epoch and
computes deterministic Newtonian point-mass acceleration in one declared frame.

That separation is intentional:
- Ephemeris/state services own where bodies are and the provenance/uncertainty
  of those states.
- This module owns the force contribution from accepted gravity sources.
- Navigator will later own numerical integration and propulsion coupling.

No body is silently promoted to navigation grade here. Consumers can include a
propagated moon state in a force evaluation while preserving its provenance and
qualification separately from a direct JPL state.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Iterable, Mapping, Sequence

from loom.application.contracts import SpatialState

CANONICAL_GRAVITY_FRAME = "J2000/ECLIPTIC"


class GravityModelError(ValueError):
    """Raised when a gravity-field request is physically or structurally invalid."""


def _vec3(value: Sequence[float], name: str) -> tuple[float, float, float]:
    try:
        out = tuple(float(v) for v in value)
    except (TypeError, ValueError) as exc:
        raise GravityModelError(f"{name} must contain three numeric values") from exc
    if len(out) != 3 or not all(math.isfinite(v) for v in out):
        raise GravityModelError(f"{name} must contain exactly three finite values")
    return out  # type: ignore[return-value]


@dataclass(frozen=True)
class GravitySource:
    """One accepted gravitating body at one epoch.

    ``mu_km3_s2`` is the standard gravitational parameter GM. It is supplied by
    an authoritative constants/catalog layer; this module never infers GM from
    display size, entity class, or identifier.
    """

    entity_id: str
    state: SpatialState
    mu_km3_s2: float
    provenance: Mapping[str, Any] = field(default_factory=dict)
    uncertainty: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        entity_id = str(self.entity_id).strip()
        if not entity_id:
            raise GravityModelError("entity_id is required")
        mu = float(self.mu_km3_s2)
        if not math.isfinite(mu) or mu <= 0.0:
            raise GravityModelError("mu_km3_s2 must be finite and greater than zero")
        if self.state.entity_id != entity_id:
            raise GravityModelError("GravitySource entity_id must match SpatialState.entity_id")
        if self.state.reference_frame != CANONICAL_GRAVITY_FRAME:
            raise GravityModelError(
                f"gravity source {entity_id} must use {CANONICAL_GRAVITY_FRAME}; "
                f"got {self.state.reference_frame}"
            )
        object.__setattr__(self, "entity_id", entity_id)
        object.__setattr__(self, "mu_km3_s2", mu)
        object.__setattr__(self, "provenance", dict(self.provenance))
        object.__setattr__(self, "uncertainty", dict(self.uncertainty))


@dataclass(frozen=True)
class GravityContribution:
    entity_id: str
    acceleration_km_s2: tuple[float, float, float]
    magnitude_km_s2: float
    separation_km: float
    mu_km3_s2: float
    navigation_grade_state: bool | None
    provenance: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GravityEvaluation:
    epoch_utc: str
    reference_frame: str
    position_km: tuple[float, float, float]
    total_acceleration_km_s2: tuple[float, float, float]
    total_magnitude_km_s2: float
    contributions: tuple[GravityContribution, ...]
    excluded_below_threshold: tuple[str, ...] = ()


def acceleration_from_source(
    position_km: Sequence[float],
    source: GravitySource,
    *,
    minimum_separation_km: float = 1e-6,
) -> GravityContribution:
    """Return Newtonian point-mass acceleration toward ``source``.

    The singularity guard is deliberately tiny and is not a collision model.
    Trajectory integration must use body radii/collision geometry separately.
    """
    p = _vec3(position_km, "position_km")
    sp = _vec3(source.state.position_km, "source.state.position_km")
    dx = sp[0] - p[0]
    dy = sp[1] - p[1]
    dz = sp[2] - p[2]
    r2 = dx * dx + dy * dy + dz * dz
    r = math.sqrt(r2)
    if r <= float(minimum_separation_km):
        raise GravityModelError(
            f"gravity evaluation for {source.entity_id} is inside singularity guard: {r} km"
        )
    scale = source.mu_km3_s2 / (r2 * r)
    acc = (dx * scale, dy * scale, dz * scale)
    mag = source.mu_km3_s2 / r2
    return GravityContribution(
        entity_id=source.entity_id,
        acceleration_km_s2=acc,
        magnitude_km_s2=mag,
        separation_km=r,
        mu_km3_s2=source.mu_km3_s2,
        navigation_grade_state=source.state.navigation_grade,
        provenance={
            "state": dict(source.state.provenance),
            "gravity_parameter": dict(source.provenance),
        },
    )


def evaluate_gravity(
    position_km: Sequence[float],
    sources: Iterable[GravitySource],
    *,
    epoch_utc: str,
    minimum_acceleration_km_s2: float = 0.0,
) -> GravityEvaluation:
    """Evaluate the summed point-mass gravitational field.

    ``minimum_acceleration_km_s2`` is an influence threshold for performance,
    not an authority threshold. A caller may use zero for full supplied-source
    summation or a documented tolerance for adaptive integration. Contributions
    are sorted deterministically by descending magnitude then entity id.
    """
    p = _vec3(position_km, "position_km")
    threshold = float(minimum_acceleration_km_s2)
    if not math.isfinite(threshold) or threshold < 0.0:
        raise GravityModelError("minimum_acceleration_km_s2 must be finite and non-negative")

    accepted: list[GravityContribution] = []
    excluded: list[str] = []
    seen: set[str] = set()
    source_epoch: str | None = None
    for source in sources:
        if source.entity_id in seen:
            raise GravityModelError(f"duplicate gravity source: {source.entity_id}")
        seen.add(source.entity_id)
        if source_epoch is None:
            source_epoch = source.state.epoch_utc
        elif source.state.epoch_utc != source_epoch:
            raise GravityModelError("all gravity source states must share one epoch")
        if source.state.epoch_utc != epoch_utc:
            raise GravityModelError(
                f"gravity source epoch {source.state.epoch_utc} does not match requested {epoch_utc}"
            )
        c = acceleration_from_source(p, source)
        if c.magnitude_km_s2 < threshold:
            excluded.append(source.entity_id)
        else:
            accepted.append(c)

    accepted.sort(key=lambda c: (-c.magnitude_km_s2, c.entity_id))
    ax = sum(c.acceleration_km_s2[0] for c in accepted)
    ay = sum(c.acceleration_km_s2[1] for c in accepted)
    az = sum(c.acceleration_km_s2[2] for c in accepted)
    total = (ax, ay, az)
    return GravityEvaluation(
        epoch_utc=epoch_utc,
        reference_frame=CANONICAL_GRAVITY_FRAME,
        position_km=p,
        total_acceleration_km_s2=total,
        total_magnitude_km_s2=math.sqrt(ax * ax + ay * ay + az * az),
        contributions=tuple(accepted),
        excluded_below_threshold=tuple(sorted(excluded)),
    )
