"""Shared named-target contract and deterministic resolver for LOOM spatial consumers.

This module deliberately sits above the existing celestial-state and orbital
propagation services. It does not introduce a second ephemeris, gravity model,
or orbital propagator.

V0.1 supports:
- standard two-body orbit references;
- orbital stations attached to those references with an explicit phase offset;
- fail-closed surface targets until an authoritative body-fixed resolver exists.

HUD, Navigator, LLM/Mara, NPC and scripted consumers should all resolve a target
through this same boundary. Caller identity is intentionally absent from the
state calculation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import math
from typing import Any, Callable, Mapping

from loom.application.contracts import SpatialState
from .celestial_state import CANONICAL_FRAME, ParentCentricOrbitModel, propagate_parent_centric


TARGET_TYPES = {
    "CELESTIAL_BODY",
    "STANDARD_ORBIT",
    "ORBITAL_STATION",
    "GROUND_PORT",
    "SURFACE_PORT",
    "SPACECRAFT",
    "WAYPOINT",
}
STATUS_VALUES = {
    "REFERENCE",
    "DERIVED",
    "CANON",
    "ENGINEERING_CANDIDATE",
    "NON_CANON",
    "UNAVAILABLE",
}


class SpatialTargetError(RuntimeError):
    """Raised when a target catalog or target resolution request is invalid."""


class TargetStateUnavailable(SpatialTargetError):
    """Raised when a valid target cannot honestly produce physical state yet."""


def _required_text(value: Any, name: str) -> str:
    text = str(value).strip() if value is not None else ""
    if not text:
        raise SpatialTargetError(f"{name} is required")
    return text


def _optional_float(value: Any, name: str) -> float | None:
    if value is None:
        return None
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise SpatialTargetError(f"{name} must be numeric or null") from exc
    if not math.isfinite(out):
        raise SpatialTargetError(f"{name} must be finite")
    return out


@dataclass(frozen=True)
class OrbitDefinition:
    orbit_class: str
    representation: str
    element_epoch_utc: str
    phase_rule: str
    altitude_km: float | None = None
    periapsis_altitude_km: float | None = None
    apoapsis_altitude_km: float | None = None
    inclination_deg: float = 0.0
    raan_deg: float = 0.0
    arg_periapsis_deg: float = 0.0
    mean_anomaly_deg: float = 0.0

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "OrbitDefinition":
        return cls(
            orbit_class=_required_text(value.get("orbit_class"), "orbit.orbit_class"),
            representation=_required_text(value.get("representation"), "orbit.representation"),
            element_epoch_utc=_required_text(value.get("element_epoch_utc"), "orbit.element_epoch_utc"),
            phase_rule=_required_text(value.get("phase_rule"), "orbit.phase_rule"),
            altitude_km=_optional_float(value.get("altitude_km"), "orbit.altitude_km"),
            periapsis_altitude_km=_optional_float(value.get("periapsis_altitude_km"), "orbit.periapsis_altitude_km"),
            apoapsis_altitude_km=_optional_float(value.get("apoapsis_altitude_km"), "orbit.apoapsis_altitude_km"),
            inclination_deg=float(value.get("inclination_deg", 0.0)),
            raan_deg=float(value.get("raan_deg", 0.0)),
            arg_periapsis_deg=float(value.get("arg_periapsis_deg", 0.0)),
            mean_anomaly_deg=float(value.get("mean_anomaly_deg", 0.0)),
        )

    def elements(self, *, body_radius_km: float) -> tuple[float, float]:
        """Return semi-major axis and eccentricity from declared altitude geometry."""
        radius = float(body_radius_km)
        if not math.isfinite(radius) or radius <= 0.0:
            raise SpatialTargetError("central-body radius must be finite and positive")
        if self.representation != "KEPLERIAN_ELEMENTS":
            raise TargetStateUnavailable(f"unsupported orbit representation: {self.representation}")
        if self.altitude_km is not None:
            if self.altitude_km < 0.0:
                raise SpatialTargetError("orbit altitude cannot be negative")
            if self.periapsis_altitude_km is not None or self.apoapsis_altitude_km is not None:
                raise SpatialTargetError("circular altitude cannot be combined with periapsis/apoapsis")
            return radius + self.altitude_km, 0.0
        if self.periapsis_altitude_km is None or self.apoapsis_altitude_km is None:
            raise TargetStateUnavailable("orbit geometry is incomplete")
        rp = radius + self.periapsis_altitude_km
        ra = radius + self.apoapsis_altitude_km
        if rp <= 0.0 or ra <= 0.0 or ra < rp:
            raise SpatialTargetError("invalid periapsis/apoapsis geometry")
        semi_major = (rp + ra) / 2.0
        eccentricity = (ra - rp) / (ra + rp)
        return semi_major, eccentricity


@dataclass(frozen=True)
class SurfaceLocation:
    latitude_deg: float
    longitude_deg: float
    elevation_m: float | None
    reference_datum: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "SurfaceLocation":
        latitude = float(value["latitude_deg"])
        longitude = float(value["longitude_deg"])
        if not -90.0 <= latitude <= 90.0:
            raise SpatialTargetError("surface latitude must be in [-90,90]")
        if not -180.0 <= longitude <= 180.0:
            raise SpatialTargetError("surface longitude must be in [-180,180]")
        return cls(
            latitude_deg=latitude,
            longitude_deg=longitude,
            elevation_m=_optional_float(value.get("elevation_m"), "surface_location.elevation_m"),
            reference_datum=_required_text(value.get("reference_datum"), "surface_location.reference_datum"),
        )


@dataclass(frozen=True)
class SpatialTarget:
    """Metadata contract corresponding to LOOM_SPATIAL_TARGET_V1.

    Position/velocity are intentionally not stored here. They are epoch-dependent
    outputs of :class:`SpatialTargetResolver`.
    """

    target_id: str
    target_type: str
    display_name: str
    parent_body: str | None
    reference_frame: str
    status: str
    state_availability: str
    state_method: str
    navigation_grade: bool | None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    operational_metadata: Mapping[str, Any] = field(default_factory=dict)
    orbit: OrbitDefinition | None = None
    orbit_id: str | None = None
    phase_offset_deg: float = 0.0
    surface_location: SurfaceLocation | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "SpatialTarget":
        target_type = _required_text(value.get("target_type"), "target_type")
        if target_type not in TARGET_TYPES:
            raise SpatialTargetError(f"unsupported target_type: {target_type}")
        status = _required_text(value.get("status"), "status")
        if status not in STATUS_VALUES:
            raise SpatialTargetError(f"unsupported status: {status}")
        parent = value.get("parent_body")
        target = cls(
            target_id=_required_text(value.get("target_id"), "target_id"),
            target_type=target_type,
            display_name=_required_text(value.get("display_name"), "display_name"),
            parent_body=str(parent).strip() if parent is not None else None,
            reference_frame=_required_text(value.get("reference_frame"), "reference_frame"),
            status=status,
            state_availability=_required_text(value.get("state_availability"), "state_availability"),
            state_method=_required_text(value.get("state_method"), "state_method"),
            navigation_grade=value.get("navigation_grade"),
            provenance=dict(value.get("provenance") or {}),
            operational_metadata=dict(value.get("operational_metadata") or {}),
            orbit=OrbitDefinition.from_mapping(value["orbit"]) if value.get("orbit") is not None else None,
            orbit_id=str(value["orbit_id"]).strip() if value.get("orbit_id") is not None else None,
            phase_offset_deg=float(value.get("phase_offset_deg", 0.0)),
            surface_location=SurfaceLocation.from_mapping(value["surface_location"])
            if value.get("surface_location") is not None else None,
        )
        if target.target_type in {"STANDARD_ORBIT", "ORBITAL_STATION", "GROUND_PORT", "SURFACE_PORT"} and not target.parent_body:
            raise SpatialTargetError(f"{target.target_type} requires parent_body")
        if target.target_type == "ORBITAL_STATION" and not target.orbit_id:
            raise SpatialTargetError("ORBITAL_STATION requires orbit_id")
        if target.state_availability == "RESOLVABLE" and target.target_type == "STANDARD_ORBIT" and target.orbit is None:
            raise SpatialTargetError("resolvable STANDARD_ORBIT requires orbit definition")
        return target

    def describe(self) -> dict[str, Any]:
        return {
            "contract": "LOOM_SPATIAL_TARGET_V1",
            "target_id": self.target_id,
            "target_type": self.target_type,
            "display_name": self.display_name,
            "parent_body": self.parent_body,
            "reference_frame": self.reference_frame,
            "state_availability": self.state_availability,
            "state_method": self.state_method,
            "navigation_grade": self.navigation_grade,
            "status": self.status,
            "provenance": dict(self.provenance),
            "operational_metadata": dict(self.operational_metadata),
        }


@dataclass(frozen=True)
class SpatialTargetCatalog:
    catalog_id: str
    version: str
    targets: Mapping[str, SpatialTarget]
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        catalog_id = _required_text(self.catalog_id, "catalog_id")
        version = _required_text(self.version, "version")
        targets = dict(self.targets)
        for target_id, target in targets.items():
            if target_id != target.target_id:
                raise SpatialTargetError("target registry key differs from target_id")
        object.__setattr__(self, "catalog_id", catalog_id)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "targets", targets)
        object.__setattr__(self, "provenance", dict(self.provenance))

    def get(self, target_id: str) -> SpatialTarget:
        key = str(target_id).strip()
        try:
            return self.targets[key]
        except KeyError as exc:
            raise SpatialTargetError(f"unknown spatial target: {key}") from exc

    def list_targets(self, *, target_type: str | None = None, resolvable_only: bool = False) -> tuple[SpatialTarget, ...]:
        values = self.targets.values()
        if target_type is not None:
            values = (t for t in values if t.target_type == target_type)
        if resolvable_only:
            values = (t for t in values if t.state_availability == "RESOLVABLE")
        return tuple(sorted(values, key=lambda item: item.target_id))


BodyStateResolver = Callable[[str, str], SpatialState]
BodyPropertyResolver = Callable[[str], Mapping[str, Any]]
BodyFixedResolver = Callable[[SpatialTarget, str], SpatialState]


@dataclass
class SpatialTargetResolver:
    catalog: SpatialTargetCatalog
    body_state_resolver: BodyStateResolver
    body_property_resolver: BodyPropertyResolver
    body_fixed_resolver: BodyFixedResolver | None = None

    def describe_target(self, target_id: str) -> dict[str, Any]:
        return self.catalog.get(target_id).describe()

    def resolve_target_state(self, target_id: str, epoch_utc: str) -> SpatialState:
        target = self.catalog.get(target_id)
        if target.state_availability != "RESOLVABLE":
            raise TargetStateUnavailable(
                f"{target.target_id} state unavailable: {target.state_availability}"
            )
        if target.target_type == "STANDARD_ORBIT":
            return self._resolve_orbit_target(target, epoch_utc)
        if target.target_type == "ORBITAL_STATION":
            return self._resolve_station(target, epoch_utc)
        if target.target_type in {"GROUND_PORT", "SURFACE_PORT"}:
            return self._resolve_surface(target, epoch_utc)
        if target.target_type == "CELESTIAL_BODY":
            return self.body_state_resolver(target.target_id, epoch_utc)
        raise TargetStateUnavailable(f"no V0.1 state method for target_type {target.target_type}")

    def _body_properties(self, body_id: str) -> tuple[float, float, str]:
        data = dict(self.body_property_resolver(body_id))
        try:
            radius = float(data["radius_km"])
            mu = float(data["mu_km3_s2"])
        except (KeyError, TypeError, ValueError) as exc:
            raise TargetStateUnavailable(f"authoritative body properties incomplete for {body_id}") from exc
        if not math.isfinite(radius) or radius <= 0.0 or not math.isfinite(mu) or mu <= 0.0:
            raise TargetStateUnavailable(f"invalid authoritative body properties for {body_id}")
        source = str(data.get("source") or "UNSPECIFIED_PROPERTY_SOURCE")
        return radius, mu, source

    def _orbit_model(
        self,
        target: SpatialTarget,
        *,
        phase_offset_deg: float = 0.0,
    ) -> tuple[ParentCentricOrbitModel, float, str]:
        if target.parent_body is None or target.orbit is None:
            raise TargetStateUnavailable(f"{target.target_id} lacks resolvable orbit geometry")
        if target.reference_frame != CANONICAL_FRAME:
            raise TargetStateUnavailable(
                f"{target.target_id} requires unsupported orbit frame {target.reference_frame}"
            )
        radius, mu, property_source = self._body_properties(target.parent_body)
        semi_major, eccentricity = target.orbit.elements(body_radius_km=radius)
        model = ParentCentricOrbitModel(
            entity_id=target.target_id,
            parent_entity_id=target.parent_body,
            element_epoch_utc=target.orbit.element_epoch_utc,
            semi_major_axis_km=semi_major,
            eccentricity=eccentricity,
            inclination_deg=target.orbit.inclination_deg,
            raan_deg=target.orbit.raan_deg,
            arg_periapsis_deg=target.orbit.arg_periapsis_deg,
            mean_anomaly_deg=target.orbit.mean_anomaly_deg + float(phase_offset_deg),
            parent_mu_km3_s2=mu,
            model_id=f"LOOM_SPATIAL_TARGET:{target.target_id}:{target.orbit.phase_rule}",
            provenance={
                "target_catalog": self.catalog.catalog_id,
                "target_status": target.status,
                "target_provenance": dict(target.provenance),
                "central_body_property_source": property_source,
            },
            uncertainty={
                "model_class": "TWO_BODY_ENGINEERING_REFERENCE",
                "navigation_qualification": "REFERENCE_NOT_DIRECT_NAVIGATION_GRADE",
                "unmodeled_perturbations": True,
            },
        )
        return model, mu, property_source

    def _compose_orbit_state(
        self,
        target: SpatialTarget,
        epoch_utc: str,
        *,
        model_target: SpatialTarget,
        phase_offset_deg: float = 0.0,
        orbit_id: str | None = None,
    ) -> SpatialState:
        model, mu, property_source = self._orbit_model(model_target, phase_offset_deg=phase_offset_deg)
        if model_target.parent_body is None:
            raise TargetStateUnavailable("orbit target has no central body")
        body = self.body_state_resolver(model_target.parent_body, epoch_utc)
        if body.reference_frame != CANONICAL_FRAME:
            raise TargetStateUnavailable("central-body state is not in canonical J2000/ECLIPTIC frame")
        if body.epoch_utc != epoch_utc:
            raise TargetStateUnavailable("central-body state epoch differs from requested target epoch")
        rel_position, rel_velocity = propagate_parent_centric(model, epoch_utc)
        position = tuple(body.position_km[i] + rel_position[i] for i in range(3))
        velocity = tuple(body.velocity_km_s[i] + rel_velocity[i] for i in range(3))
        period_s = 2.0 * math.pi * math.sqrt(model.semi_major_axis_km ** 3 / mu)
        return SpatialState(
            entity_id=target.target_id,
            epoch_utc=epoch_utc,
            reference_frame=CANONICAL_FRAME,
            position_km=position,
            velocity_km_s=velocity,
            provenance={
                "state_source": "LOOM_SPATIAL_TARGET_RESOLVER_V1",
                "state_method": target.state_method,
                "target_catalog": self.catalog.catalog_id,
                "target_catalog_version": self.catalog.version,
                "target_status": target.status,
                "target_provenance": dict(target.provenance),
                "central_body_state_source": body.provenance.get("state_source"),
                "central_body_property_source": property_source,
                "orbit_model_id": model.model_id,
            },
            navigation_grade=bool(target.navigation_grade),
            uncertainty=dict(model.uncertainty),
            payload={
                "contract": "LOOM_SPATIAL_TARGET_V1",
                "target_type": target.target_type,
                "display_name": target.display_name,
                "parent_body": model_target.parent_body,
                "orbit_id": orbit_id or model_target.target_id,
                "orbit_class": model_target.orbit.orbit_class if model_target.orbit else None,
                "representation": model_target.orbit.representation if model_target.orbit else None,
                "semi_major_axis_km": model.semi_major_axis_km,
                "eccentricity": model.eccentricity,
                "inclination_deg": model.inclination_deg,
                "period_s": period_s,
                "operational_metadata": dict(target.operational_metadata),
            },
        )

    def _resolve_orbit_target(self, target: SpatialTarget, epoch_utc: str) -> SpatialState:
        return self._compose_orbit_state(target, epoch_utc, model_target=target)

    def _resolve_station(self, target: SpatialTarget, epoch_utc: str) -> SpatialState:
        if not target.orbit_id:
            raise TargetStateUnavailable(f"station {target.target_id} has no orbit_id")
        orbit = self.catalog.get(target.orbit_id)
        if orbit.target_type != "STANDARD_ORBIT":
            raise SpatialTargetError(f"station orbit_id is not STANDARD_ORBIT: {target.orbit_id}")
        if orbit.state_availability != "RESOLVABLE":
            raise TargetStateUnavailable(f"station orbit unavailable: {orbit.state_availability}")
        if orbit.parent_body != target.parent_body:
            raise SpatialTargetError("station parent_body differs from referenced orbit")
        return self._compose_orbit_state(
            target,
            epoch_utc,
            model_target=orbit,
            phase_offset_deg=target.phase_offset_deg,
            orbit_id=orbit.target_id,
        )

    def _resolve_surface(self, target: SpatialTarget, epoch_utc: str) -> SpatialState:
        if target.surface_location is None:
            raise TargetStateUnavailable(f"surface target {target.target_id} has no governed geodetic location")
        if self.body_fixed_resolver is None:
            raise TargetStateUnavailable(
                f"surface target {target.target_id} requires authoritative body-fixed → inertial transform"
            )
        state = self.body_fixed_resolver(target, epoch_utc)
        if state.entity_id != target.target_id:
            raise SpatialTargetError("body-fixed resolver returned wrong entity_id")
        if state.epoch_utc != epoch_utc:
            raise SpatialTargetError("body-fixed resolver returned wrong epoch")
        return state


def load_target_catalog(path: Path | str) -> SpatialTargetCatalog:
    file_path = Path(path)
    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SpatialTargetError(f"cannot load target catalog: {file_path}") from exc
    if payload.get("contract") != "LOOM_SPATIAL_TARGET_CATALOG_V1":
        raise SpatialTargetError("unsupported spatial target catalog contract")
    targets: dict[str, SpatialTarget] = {}
    for section in ("standard_orbits", "orbital_stations", "earth_ground_ports", "lunar_surface_ports"):
        rows = payload.get(section)
        if not isinstance(rows, list):
            raise SpatialTargetError(f"catalog section {section} must be a list")
        for row in rows:
            target = SpatialTarget.from_mapping(row)
            if target.target_id in targets:
                raise SpatialTargetError(f"duplicate target_id: {target.target_id}")
            targets[target.target_id] = target
    return SpatialTargetCatalog(
        catalog_id=_required_text(payload.get("catalog_id"), "catalog_id"),
        version=_required_text(payload.get("version"), "version"),
        targets=targets,
        provenance=dict(payload.get("provenance") or {}),
    )
