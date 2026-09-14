"""Minimal shared celestial-state authority promoted from the qualified spatial lineage.

Resolves a body's position and velocity at an explicit UTC epoch in one canonical
inertial frame. Direct authoritative state is preferred. Declared parent-centric
Kepler propagation is an explicit fallback and is never silently navigation-grade.

This module owns no UI, target registry, metric-domain radius, route planning,
execution, or campaign mutation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import math
from typing import Any, Callable, Mapping, Sequence

CANONICAL_FRAME = "J2000/ECLIPTIC"


class CelestialStateError(RuntimeError):
    pass


def _epoch(value: str) -> datetime:
    text = str(value).strip()
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        dt = datetime.fromisoformat(probe)
    except ValueError as exc:
        raise CelestialStateError(f"invalid epoch_utc: {value!r}") from exc
    if dt.tzinfo is None:
        raise CelestialStateError("epoch_utc must include timezone")
    return dt.astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _vec3(value: Sequence[float], name: str) -> tuple[float, float, float]:
    try:
        out = tuple(float(v) for v in value)
    except (TypeError, ValueError) as exc:
        raise CelestialStateError(f"{name} must contain numeric values") from exc
    if len(out) != 3 or not all(math.isfinite(v) for v in out):
        raise CelestialStateError(f"{name} must contain exactly three finite values")
    return out  # type: ignore[return-value]


@dataclass(frozen=True)
class SpatialState:
    entity_id: str
    epoch_utc: str
    reference_frame: str
    position_km: Sequence[float]
    velocity_km_s: Sequence[float]
    provenance: Mapping[str, Any] = field(default_factory=dict)
    navigation_grade: bool | None = None
    uncertainty: Mapping[str, Any] = field(default_factory=dict)
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        entity = str(self.entity_id).strip()
        frame = str(self.reference_frame).strip()
        if not entity or not frame:
            raise CelestialStateError("entity_id and reference_frame are required")
        object.__setattr__(self, "entity_id", entity)
        object.__setattr__(self, "epoch_utc", _iso(_epoch(self.epoch_utc)))
        object.__setattr__(self, "reference_frame", frame)
        object.__setattr__(self, "position_km", _vec3(self.position_km, "position_km"))
        object.__setattr__(self, "velocity_km_s", _vec3(self.velocity_km_s, "velocity_km_s"))
        object.__setattr__(self, "provenance", dict(self.provenance))
        object.__setattr__(self, "uncertainty", dict(self.uncertainty))
        object.__setattr__(self, "payload", dict(self.payload))


@dataclass(frozen=True)
class ParentCentricOrbitModel:
    entity_id: str
    parent_entity_id: str
    element_epoch_utc: str
    semi_major_axis_km: float
    eccentricity: float
    inclination_deg: float
    raan_deg: float
    arg_periapsis_deg: float
    mean_anomaly_deg: float
    parent_mu_km3_s2: float
    model_id: str
    provenance: Mapping[str, Any] = field(default_factory=dict)
    uncertainty: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not str(self.entity_id).strip() or not str(self.parent_entity_id).strip() or not str(self.model_id).strip():
            raise CelestialStateError("entity_id, parent_entity_id and model_id are required")
        _epoch(self.element_epoch_utc)
        if not math.isfinite(float(self.semi_major_axis_km)) or float(self.semi_major_axis_km) <= 0:
            raise CelestialStateError("semi_major_axis_km must be finite and positive")
        if not math.isfinite(float(self.parent_mu_km3_s2)) or float(self.parent_mu_km3_s2) <= 0:
            raise CelestialStateError("parent_mu_km3_s2 must be finite and positive")
        e = float(self.eccentricity)
        if not math.isfinite(e) or not 0 <= e < 1:
            raise CelestialStateError("eccentricity must be finite and in [0,1)")


def _solve_kepler(mean: float, eccentricity: float) -> float:
    m = math.fmod(mean, 2 * math.pi)
    e_anom = m if eccentricity < 0.8 else math.pi
    for _ in range(32):
        delta = (e_anom - eccentricity * math.sin(e_anom) - m) / (1 - eccentricity * math.cos(e_anom))
        e_anom -= delta
        if abs(delta) < 1e-13:
            return e_anom
    raise CelestialStateError("Kepler solver failed to converge")


def _rotate(v: tuple[float, float, float], model: ParentCentricOrbitModel) -> tuple[float, float, float]:
    x, y, z = v
    O, i, w = map(math.radians, (model.raan_deg, model.inclination_deg, model.arg_periapsis_deg))
    co, so, ci, si, cw, sw = math.cos(O), math.sin(O), math.cos(i), math.sin(i), math.cos(w), math.sin(w)
    return (
        (co*cw-so*sw*ci)*x + (-co*sw-so*cw*ci)*y + so*si*z,
        (so*cw+co*sw*ci)*x + (-so*sw+co*cw*ci)*y - co*si*z,
        sw*si*x + cw*si*y + ci*z,
    )


def propagate_parent_centric(model: ParentCentricOrbitModel, epoch_utc: str):
    dt = (_epoch(epoch_utc) - _epoch(model.element_epoch_utc)).total_seconds()
    a, e, mu = float(model.semi_major_axis_km), float(model.eccentricity), float(model.parent_mu_km3_s2)
    n = math.sqrt(mu / a**3)
    ea = _solve_kepler(math.radians(model.mean_anomaly_deg) + n * dt, e)
    ce, se, root = math.cos(ea), math.sin(ea), math.sqrt(1-e*e)
    r = a * (1-e*ce)
    pos = (a*(ce-e), a*root*se, 0.0)
    factor = math.sqrt(mu*a)/r
    vel = (-factor*se, factor*root*ce, 0.0)
    return _rotate(pos, model), _rotate(vel, model)


DirectStateLookup = Callable[[str, str], SpatialState | None]


class HybridCelestialStateService:
    def __init__(self, direct_lookup: DirectStateLookup, orbit_models: Mapping[str, ParentCentricOrbitModel]):
        self._direct_lookup = direct_lookup
        self._models = dict(orbit_models)

    def resolve(self, entity_id: str, epoch_utc: str) -> SpatialState:
        return self._resolve(str(entity_id).strip(), epoch_utc, ())

    def _resolve(self, entity_id: str, epoch_utc: str, stack: tuple[str, ...]) -> SpatialState:
        if not entity_id:
            raise CelestialStateError("entity_id is required")
        if entity_id in stack:
            raise CelestialStateError("celestial parent graph contains a cycle")
        requested_dt = _epoch(epoch_utc)
        requested = _iso(requested_dt)
        direct = self._direct_lookup(entity_id, requested)
        if direct is not None:
            if direct.entity_id != entity_id:
                raise CelestialStateError("direct provider returned wrong entity_id")
            if direct.reference_frame != CANONICAL_FRAME:
                raise CelestialStateError("direct provider returned non-canonical frame")
            if _epoch(direct.epoch_utc) != requested_dt:
                raise CelestialStateError("direct provider returned wrong epoch")
            return direct
        model = self._models.get(entity_id)
        if model is None:
            raise CelestialStateError(f"no direct state or propagation model for {entity_id}")
        parent = self._resolve(model.parent_entity_id, requested, stack + (entity_id,))
        rel_p, rel_v = propagate_parent_centric(model, requested)
        return SpatialState(
            entity_id=entity_id,
            epoch_utc=requested,
            reference_frame=CANONICAL_FRAME,
            position_km=tuple(parent.position_km[i] + rel_p[i] for i in range(3)),
            velocity_km_s=tuple(parent.velocity_km_s[i] + rel_v[i] for i in range(3)),
            provenance={
                "state_source": "PROPAGATED_PARENT_CENTRIC_KEPLER",
                "model_id": model.model_id,
                "element_epoch_utc": model.element_epoch_utc,
                "parent_entity_id": model.parent_entity_id,
                "parent_state_source": parent.provenance.get("state_source"),
                "model_provenance": dict(model.provenance),
            },
            navigation_grade=False,
            uncertainty=dict(model.uncertainty),
            payload={"state_class": "CELESTIAL", "propagation_model": "TWO_BODY_OSCULATING_KEPLER", "parent_entity_id": model.parent_entity_id},
        )
