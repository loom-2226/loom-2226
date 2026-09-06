"""Hybrid celestial-state service for LOOM Navigation Physics v2.

The service resolves one body's physical state at an arbitrary UTC epoch in
J2000/ECLIPTIC. Direct authoritative state is preferred when available. When a
natural satellite lacks direct coverage, a declared parent-centric osculating
model may be propagated with two-body Kepler dynamics and added to the resolved
parent heliocentric state.

This module does not silently promote propagated states to navigation grade.
Every fallback carries explicit provenance and uncertainty. Higher-fidelity
perturbation models can replace the propagator behind the same resolver contract
without changing GIS/Navigator consumers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import math
from typing import Any, Callable, Mapping

from loom.application.contracts import SpatialState

CANONICAL_FRAME = "J2000/ECLIPTIC"


class CelestialStateError(RuntimeError):
    """Raised when a celestial state cannot be resolved safely."""


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


def _finite_positive(value: float, name: str) -> float:
    out = float(value)
    if not math.isfinite(out) or out <= 0.0:
        raise CelestialStateError(f"{name} must be finite and greater than zero")
    return out


@dataclass(frozen=True)
class ParentCentricOrbitModel:
    """Osculating Keplerian model for one child relative to one parent."""

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
        eid = str(self.entity_id).strip()
        pid = str(self.parent_entity_id).strip()
        mid = str(self.model_id).strip()
        if not eid or not pid or not mid:
            raise CelestialStateError("entity_id, parent_entity_id and model_id are required")
        _epoch(self.element_epoch_utc)
        a = _finite_positive(self.semi_major_axis_km, "semi_major_axis_km")
        mu = _finite_positive(self.parent_mu_km3_s2, "parent_mu_km3_s2")
        e = float(self.eccentricity)
        if not math.isfinite(e) or not 0.0 <= e < 1.0:
            raise CelestialStateError("eccentricity must be finite and in [0,1)")
        for name in ("inclination_deg", "raan_deg", "arg_periapsis_deg", "mean_anomaly_deg"):
            if not math.isfinite(float(getattr(self, name))):
                raise CelestialStateError(f"{name} must be finite")
        object.__setattr__(self, "entity_id", eid)
        object.__setattr__(self, "parent_entity_id", pid)
        object.__setattr__(self, "model_id", mid)
        object.__setattr__(self, "semi_major_axis_km", a)
        object.__setattr__(self, "parent_mu_km3_s2", mu)
        object.__setattr__(self, "eccentricity", e)
        object.__setattr__(self, "provenance", dict(self.provenance))
        object.__setattr__(self, "uncertainty", dict(self.uncertainty))


def _solve_kepler(mean_anomaly_rad: float, eccentricity: float) -> float:
    """Deterministic Newton solve for elliptic eccentric anomaly."""
    m = math.fmod(mean_anomaly_rad, 2.0 * math.pi)
    if m < -math.pi:
        m += 2.0 * math.pi
    elif m > math.pi:
        m -= 2.0 * math.pi
    e_anom = m if eccentricity < 0.8 else math.pi
    for _ in range(32):
        f = e_anom - eccentricity * math.sin(e_anom) - m
        fp = 1.0 - eccentricity * math.cos(e_anom)
        delta = f / fp
        e_anom -= delta
        if abs(delta) < 1e-13:
            return e_anom
    raise CelestialStateError("Kepler solver failed to converge")


def _rotate_perifocal(
    vector: tuple[float, float, float],
    *,
    inclination_rad: float,
    raan_rad: float,
    arg_periapsis_rad: float,
) -> tuple[float, float, float]:
    """Rotate perifocal vector into the declared inertial J2000/ecliptic frame."""
    x, y, z = vector
    co, so = math.cos(raan_rad), math.sin(raan_rad)
    ci, si = math.cos(inclination_rad), math.sin(inclination_rad)
    cw, sw = math.cos(arg_periapsis_rad), math.sin(arg_periapsis_rad)
    r11 = co * cw - so * sw * ci
    r12 = -co * sw - so * cw * ci
    r13 = so * si
    r21 = so * cw + co * sw * ci
    r22 = -so * sw + co * cw * ci
    r23 = -co * si
    r31 = sw * si
    r32 = cw * si
    r33 = ci
    return (
        r11 * x + r12 * y + r13 * z,
        r21 * x + r22 * y + r23 * z,
        r31 * x + r32 * y + r33 * z,
    )


def propagate_parent_centric(
    model: ParentCentricOrbitModel,
    epoch_utc: str,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Propagate a child relative to its parent using elliptic two-body motion."""
    target = _epoch(epoch_utc)
    base = _epoch(model.element_epoch_utc)
    dt_s = (target - base).total_seconds()
    a = model.semi_major_axis_km
    e = model.eccentricity
    mu = model.parent_mu_km3_s2
    n = math.sqrt(mu / (a * a * a))
    mean = math.radians(model.mean_anomaly_deg) + n * dt_s
    ea = _solve_kepler(mean, e)

    cos_e, sin_e = math.cos(ea), math.sin(ea)
    root = math.sqrt(1.0 - e * e)
    r = a * (1.0 - e * cos_e)
    pos_pf = (a * (cos_e - e), a * root * sin_e, 0.0)
    factor = math.sqrt(mu * a) / r
    vel_pf = (-factor * sin_e, factor * root * cos_e, 0.0)

    kwargs = {
        "inclination_rad": math.radians(model.inclination_deg),
        "raan_rad": math.radians(model.raan_deg),
        "arg_periapsis_rad": math.radians(model.arg_periapsis_deg),
    }
    return _rotate_perifocal(pos_pf, **kwargs), _rotate_perifocal(vel_pf, **kwargs)


DirectStateLookup = Callable[[str, str], SpatialState | None]


class HybridCelestialStateService:
    """Resolve direct or propagated celestial states behind one typed boundary."""

    def __init__(
        self,
        direct_lookup: DirectStateLookup,
        orbit_models: Mapping[str, ParentCentricOrbitModel],
    ) -> None:
        self._direct_lookup = direct_lookup
        self._models = dict(orbit_models)

    def resolve(self, entity_id: str, epoch_utc: str) -> SpatialState:
        return self._resolve(str(entity_id).strip(), epoch_utc, stack=())

    def _resolve(self, entity_id: str, epoch_utc: str, *, stack: tuple[str, ...]) -> SpatialState:
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
        parent = self._resolve(model.parent_entity_id, requested, stack=stack + (entity_id,))
        rel_p, rel_v = propagate_parent_centric(model, requested)
        pos = tuple(parent.position_km[i] + rel_p[i] for i in range(3))
        vel = tuple(parent.velocity_km_s[i] + rel_v[i] for i in range(3))
        return SpatialState(
            entity_id=entity_id,
            epoch_utc=requested,
            reference_frame=CANONICAL_FRAME,
            position_km=pos,
            velocity_km_s=vel,
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
            payload={
                "state_class": "CELESTIAL",
                "propagation_model": "TWO_BODY_OSCULATING_KEPLER",
                "parent_entity_id": model.parent_entity_id,
            },
        )
