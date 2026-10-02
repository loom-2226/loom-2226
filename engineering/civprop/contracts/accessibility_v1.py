"""Versioned physics + service accessibility boundary for CIVPROP Engine V1.

The contract keeps three things separate:
1. qualified body geometry;
2. scoped provider/service access;
3. generalized transport cost.

A body-center straight-line separation is context. It is never route length,
delta-v, transfer duration, or proof that an actor can use a service.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import math
from typing import Any, Mapping, Optional

from .actor_state_v1 import ActorState


FORMAT = "CIVPROP_ACCESSIBILITY_V1"
CONTRACT_VERSION = "1.0.0"
ACCESS_STATUS = {"FEASIBLE", "INFEASIBLE", "UNKNOWN"}
QUANTITY_STATUS = {"KNOWN", "UNKNOWN"}
DISTANCE_SEMANTICS = "BODY_CENTER_STRAIGHT_LINE_CONTEXT_NOT_ROUTE_LENGTH"


def _year(epoch_utc: str) -> int:
    text = str(epoch_utc)
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    value = datetime.fromisoformat(probe)
    if value.tzinfo is None:
        raise ValueError("accessibility epoch must include timezone")
    return value.year


def _finite_nonnegative(value: float, name: str) -> float:
    out = float(value)
    if not math.isfinite(out) or out < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return out


@dataclass(frozen=True)
class CostComponent:
    component_id: str
    status: str
    value: Optional[float]
    unit: str
    uncertainty: Optional[float]


@dataclass(frozen=True)
class GeneralizedCost:
    status: str
    value: Optional[float]
    unit: Optional[str]
    uncertainty: Optional[float]
    components: tuple[CostComponent, ...] = ()


@dataclass(frozen=True)
class GeometryContext:
    origin_body_id: str
    destination_body_id: str
    epoch_utc: str
    straight_line_separation_km: float
    relative_speed_km_s: float
    uncertainty_km: Optional[float]
    reference_frame: str
    distance_semantics: str
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class LocationBinding:
    location_id: str
    body_id: Optional[str]


@dataclass(frozen=True)
class ServicePath:
    service_id: str
    actor_id: str
    provider_id: str
    subject_id: Optional[str]
    origin_location_id: str
    destination_location_id: str
    mission_class: str
    service_class: str
    valid_from_year: int
    valid_to_year: Optional[int]
    target_year: Optional[int]
    status: str
    limiting_constraints: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    cost_components: tuple[CostComponent, ...]
    generalized_cost: GeneralizedCost
    required_technology_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class AccessibilityPackage:
    format: str
    contract_version: str
    epoch_policy: str
    location_bindings: tuple[LocationBinding, ...]
    geometry_samples: tuple[GeometryContext, ...]
    service_paths: tuple[ServicePath, ...]


@dataclass(frozen=True)
class AccessibilityRequest:
    actor_id: str
    origin_location_id: str
    destination_location_id: str
    epoch_utc: str
    mission_class: str
    service_class: str
    subject_id: Optional[str] = None
    requested_service_id: Optional[str] = None


@dataclass(frozen=True)
class AccessibilityAssessment:
    status: str
    request: AccessibilityRequest
    matched_service_id: Optional[str]
    geometry: Optional[GeometryContext]
    generalized_cost: GeneralizedCost
    limiting_constraints: tuple[str, ...]
    provenance_refs: tuple[str, ...]


def _component(data: Mapping[str, Any]) -> CostComponent:
    status = str(data["status"])
    if status not in QUANTITY_STATUS:
        raise ValueError("invalid accessibility quantity status")
    value = None if data.get("value") is None else _finite_nonnegative(
        data["value"], "accessibility quantity"
    )
    unit = str(data.get("unit") or "")
    uncertainty = (
        None if data.get("uncertainty") is None
        else _finite_nonnegative(data["uncertainty"], "accessibility uncertainty")
    )
    if not unit:
        raise ValueError("accessibility quantity requires unit")
    if status == "UNKNOWN" and value is not None:
        raise ValueError("UNKNOWN accessibility quantity cannot invent value")
    if status == "KNOWN" and value is None:
        raise ValueError("KNOWN accessibility quantity requires value")
    return CostComponent(
        component_id=str(data["component_id"]),
        status=status,
        value=value,
        unit=unit,
        uncertainty=uncertainty,
    )


def _generalized_cost(data: Mapping[str, Any]) -> GeneralizedCost:
    status = str(data["status"])
    if status not in QUANTITY_STATUS:
        raise ValueError("invalid generalized-cost status")
    value = None if data.get("value") is None else _finite_nonnegative(
        data["value"], "generalized cost"
    )
    unit = data.get("unit")
    uncertainty = (
        None if data.get("uncertainty") is None
        else _finite_nonnegative(data["uncertainty"], "generalized-cost uncertainty")
    )
    if status == "UNKNOWN" and value is not None:
        raise ValueError("UNKNOWN generalized cost cannot invent scalar")
    if status == "KNOWN" and (value is None or not unit):
        raise ValueError("KNOWN generalized cost requires value and unit")
    return GeneralizedCost(status, value, unit, uncertainty)


def _geometry(data: Mapping[str, Any]) -> GeometryContext:
    if data.get("source_status") != "QUALIFIED" or data.get("navigation_grade") is not True:
        raise ValueError("geometry sample is not qualified/navigation-grade")
    return GeometryContext(
        origin_body_id=str(data["origin_body_id"]),
        destination_body_id=str(data["destination_body_id"]),
        epoch_utc=str(data["epoch_utc"]),
        straight_line_separation_km=_finite_nonnegative(
            data["straight_line_separation_km"], "straight-line separation"
        ),
        relative_speed_km_s=_finite_nonnegative(
            data["relative_speed_km_s"], "relative body speed"
        ),
        uncertainty_km=(
            None if data.get("uncertainty_km") is None
            else _finite_nonnegative(data["uncertainty_km"], "geometry uncertainty")
        ),
        reference_frame=str(data["reference_frame"]),
        distance_semantics=DISTANCE_SEMANTICS,
        provenance_refs=tuple(data.get("provenance_refs", ())),
    )


def _service_path(data: Mapping[str, Any]) -> ServicePath:
    status = str(data["status"])
    if status not in ACCESS_STATUS:
        raise ValueError("invalid service-path accessibility status")
    components = tuple(_component(x) for x in data.get("cost_components", ()))
    ids = [x.component_id for x in components]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate accessibility cost component")
    cost = _generalized_cost(data["generalized_cost"])
    if status == "FEASIBLE" and (cost.status != "KNOWN" or not components):
        raise ValueError("FEASIBLE service path requires decomposed known generalized cost")
    valid_from = int(data["valid_from_year"])
    valid_to = None if data.get("valid_to_year") is None else int(data["valid_to_year"])
    if valid_to is not None and valid_to < valid_from:
        raise ValueError("invalid service-path validity")
    return ServicePath(
        service_id=str(data["service_id"]),
        actor_id=str(data["actor_id"]),
        provider_id=str(data["provider_id"]),
        subject_id=data.get("subject_id"),
        origin_location_id=str(data["origin_location_id"]),
        destination_location_id=str(data["destination_location_id"]),
        mission_class=str(data["mission_class"]),
        service_class=str(data["service_class"]),
        valid_from_year=valid_from,
        valid_to_year=valid_to,
        target_year=None if data.get("target_year") is None else int(data["target_year"]),
        status=status,
        limiting_constraints=tuple(data.get("limiting_constraints", ())),
        provenance_refs=tuple(data.get("provenance_refs", ())),
        cost_components=components,
        generalized_cost=cost,
        required_technology_ids=tuple(data.get("required_technology_ids", ())),
    )


def load_accessibility_package(data: Mapping[str, Any]) -> AccessibilityPackage:
    if data.get("format") != FORMAT or data.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("unexpected accessibility contract")
    bindings = tuple(
        LocationBinding(str(x["location_id"]), x.get("body_id"))
        for x in data.get("location_bindings", ())
    )
    binding_ids = [x.location_id for x in bindings]
    if not binding_ids or len(binding_ids) != len(set(binding_ids)):
        raise ValueError("accessibility location bindings must be nonempty and unique")
    geometry = tuple(_geometry(x) for x in data.get("geometry_samples", ()))
    services = tuple(_service_path(x) for x in data.get("service_paths", ()))
    service_ids = [x.service_id for x in services]
    if len(service_ids) != len(set(service_ids)):
        raise ValueError("duplicate accessibility service id")
    known_locations = set(binding_ids)
    for service in services:
        if service.origin_location_id not in known_locations or service.destination_location_id not in known_locations:
            raise ValueError("service path references unknown location")
    return AccessibilityPackage(
        format=FORMAT,
        contract_version=CONTRACT_VERSION,
        epoch_policy=str(data["epoch_policy"]),
        location_bindings=bindings,
        geometry_samples=geometry,
        service_paths=services,
    )


class AccessibilityRuntime:
    """Pure deterministic query layer over a frozen accessibility package."""

    def __init__(self, package: AccessibilityPackage):
        self.package = package
        self._bodies = {x.location_id: x.body_id for x in package.location_bindings}
        self._services = {x.service_id: x for x in package.service_paths}
        idx = {}
        for service in package.service_paths:
            key=(service.actor_id,service.origin_location_id,service.destination_location_id,
                 service.mission_class,service.service_class)
            idx.setdefault(key,[]).append(service)
        self._service_index={k:tuple(sorted(v,key=lambda x:x.service_id)) for k,v in idx.items()}
        self._geometry_index={}
        for row in package.geometry_samples:
            self._geometry_index[(row.origin_body_id,row.destination_body_id,row.epoch_utc)]=row
            self._geometry_index[(row.destination_body_id,row.origin_body_id,row.epoch_utc)]=row

    def has_scoped_service(self, actor_id: str, origin_location_id: str, destination_location_id: str, mission_class: str, service_class: str) -> bool:
        return (actor_id,origin_location_id,destination_location_id,mission_class,service_class) in self._service_index

    def _geometry_for(self, request: AccessibilityRequest) -> Optional[GeometryContext]:
        origin = self._bodies.get(request.origin_location_id)
        destination = self._bodies.get(request.destination_location_id)
        if not origin or not destination or origin == destination:
            return None
        return self._geometry_index.get((origin,destination,request.epoch_utc))

    @staticmethod
    def _actor_has_service(actor_state: ActorState, service: ServicePath, year: int) -> bool:
        if actor_state.actor_id != service.actor_id:
            return False
        if actor_state.provider_service_access.status != "KNOWN_RECORDS":
            return False
        for fact in actor_state.provider_service_access.records:
            if fact.provider_id != service.provider_id:
                continue
            if service.subject_id is not None and fact.subject_id != service.subject_id:
                continue
            if fact.valid_from is not None and year < fact.valid_from:
                continue
            if fact.valid_to is not None and year > fact.valid_to:
                continue
            return True
        return False

    @staticmethod
    def _physical_components(geometry: Optional[GeometryContext]) -> tuple[CostComponent, ...]:
        if geometry is None:
            return ()
        return (
            CostComponent(
                "STRAIGHT_LINE_BODY_CENTER_SEPARATION", "KNOWN",
                geometry.straight_line_separation_km, "km", geometry.uncertainty_km,
            ),
            CostComponent(
                "RELATIVE_BODY_SPEED", "KNOWN",
                geometry.relative_speed_km_s, "km/s", None,
            ),
        )

    def _unknown(
        self,
        request: AccessibilityRequest,
        geometry: Optional[GeometryContext],
        constraints: tuple[str, ...],
        provenance: tuple[str, ...] = (),
    ) -> AccessibilityAssessment:
        components = self._physical_components(geometry) + (
            CostComponent("ROUTE_LENGTH", "UNKNOWN", None, "km", None),
            CostComponent("TRANSFER_DURATION", "UNKNOWN", None, "s", None),
            CostComponent("DELTA_V", "UNKNOWN", None, "km/s", None),
            CostComponent("SERVICE_PRICE", "UNKNOWN", None, "currency/service-unit", None),
        )
        return AccessibilityAssessment(
            status="UNKNOWN",
            request=request,
            matched_service_id=None,
            geometry=geometry,
            generalized_cost=GeneralizedCost("UNKNOWN", None, None, None, components),
            limiting_constraints=constraints,
            provenance_refs=provenance,
        )

    def assess(
        self,
        request: AccessibilityRequest,
        *,
        actor_state: ActorState,
        technology_state: Mapping[str, str],
    ) -> AccessibilityAssessment:
        year = _year(request.epoch_utc)
        geometry = self._geometry_for(request)

        if request.requested_service_id is not None:
            service = self._services.get(request.requested_service_id)
            if service is None:
                return self._unknown(
                    request, geometry, ("REQUESTED_SERVICE_NOT_FOUND",)
                )
            scope_match = (
                service.actor_id == request.actor_id
                and service.origin_location_id == request.origin_location_id
                and service.destination_location_id == request.destination_location_id
                and service.mission_class == request.mission_class
                and service.service_class == request.service_class
                and (service.subject_id is None or service.subject_id == request.subject_id)
            )
            if not scope_match:
                return AccessibilityAssessment(
                    status="INFEASIBLE",
                    request=request,
                    matched_service_id=service.service_id,
                    geometry=geometry,
                    generalized_cost=GeneralizedCost(
                        "UNKNOWN", None, None, None, self._physical_components(geometry)
                    ),
                    limiting_constraints=("REQUEST_OUTSIDE_NAMED_SERVICE_SCOPE",),
                    provenance_refs=service.provenance_refs,
                )
            candidates = (service,)
        else:
            scoped=self._service_index.get((
                request.actor_id,request.origin_location_id,request.destination_location_id,
                request.mission_class,request.service_class),())
            candidates=tuple(service for service in scoped
                if (service.subject_id is None or service.subject_id == request.subject_id)
                and service.valid_from_year <= year
                and (service.valid_to_year is None or year <= service.valid_to_year))

        if not candidates:
            constraints = ["NO_MATCHING_SCOPED_SERVICE_PATH"]
            if geometry is None:
                constraints.append("QUALIFIED_GEOMETRY_SAMPLE_UNAVAILABLE_AT_REQUEST_EPOCH")
            return self._unknown(request, geometry, tuple(constraints))

        service = sorted(candidates, key=lambda x: x.service_id)[0]
        constraints = list(service.limiting_constraints)
        if not self._actor_has_service(actor_state, service, year):
            constraints.append("ACTOR_SERVICE_ACCESS_UNQUALIFIED")
            return self._unknown(
                request, geometry, tuple(constraints), service.provenance_refs
            )

        tech_values = [
            technology_state.get(tech_id, "UNKNOWN")
            for tech_id in service.required_technology_ids
        ]
        if any(value == "UNUSABLE" for value in tech_values):
            return AccessibilityAssessment(
                status="INFEASIBLE",
                request=request,
                matched_service_id=service.service_id,
                geometry=geometry,
                generalized_cost=GeneralizedCost(
                    "UNKNOWN", None, None, None,
                    self._physical_components(geometry) + service.cost_components,
                ),
                limiting_constraints=tuple(constraints + ["REQUIRED_TRANSPORT_TECHNOLOGY_UNUSABLE"]),
                provenance_refs=service.provenance_refs,
            )
        if any(value != "USABLE" for value in tech_values):
            constraints.append("REQUIRED_TRANSPORT_TECHNOLOGY_UNKNOWN")
        if service.target_year is not None and year != service.target_year:
            constraints.append("REQUEST_EPOCH_OUTSIDE_DOCUMENTED_TARGET_YEAR")

        status = service.status
        if constraints and status == "FEASIBLE" and (
            "REQUIRED_TRANSPORT_TECHNOLOGY_UNKNOWN" in constraints
            or "REQUEST_EPOCH_OUTSIDE_DOCUMENTED_TARGET_YEAR" in constraints
        ):
            status = "UNKNOWN"

        components = self._physical_components(geometry) + service.cost_components
        cost = GeneralizedCost(
            service.generalized_cost.status,
            service.generalized_cost.value,
            service.generalized_cost.unit,
            service.generalized_cost.uncertainty,
            components,
        )
        if status != "FEASIBLE":
            cost = GeneralizedCost("UNKNOWN", None, None, None, components)

        return AccessibilityAssessment(
            status=status,
            request=request,
            matched_service_id=service.service_id,
            geometry=geometry,
            generalized_cost=cost,
            limiting_constraints=tuple(constraints),
            provenance_refs=tuple(dict.fromkeys(
                (*service.provenance_refs, *(geometry.provenance_refs if geometry else ()))
            )),
        )


_RUNTIME_CACHE={}
def accessibility_runtime(package: AccessibilityPackage) -> AccessibilityRuntime:
    key=id(package); cached=_RUNTIME_CACHE.get(key)
    if cached is not None and cached[0] is package: return cached[1]
    runtime=AccessibilityRuntime(package)
    if len(_RUNTIME_CACHE)>=16: _RUNTIME_CACHE.pop(next(iter(_RUNTIME_CACHE)))
    _RUNTIME_CACHE[key]=(package,runtime); return runtime


__all__ = [
    "ACCESS_STATUS", "CONTRACT_VERSION", "DISTANCE_SEMANTICS", "FORMAT",
    "AccessibilityAssessment", "AccessibilityPackage", "AccessibilityRequest",
    "AccessibilityRuntime", "accessibility_runtime", "CostComponent", "GeneralizedCost", "GeometryContext",
    "LocationBinding", "ServicePath", "load_accessibility_package",
]
