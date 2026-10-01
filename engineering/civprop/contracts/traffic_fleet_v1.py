"""CIVPROP Traffic/Fleet V1.

Annual discrete route/service/fleet accounting. Installed local transport handling
capacity is not itself realized OD movement. Technology timeline dates are context
only and never auto-spawn fleet assets.
"""
from __future__ import annotations

from dataclasses import dataclass
import calendar
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from .accessibility_v1 import AccessibilityPackage
from .demand_pressure_v1 import DemandPressurePackage, DemandPressureRuntime


FORMAT = "CIVPROP_TRAFFIC_FLEET_V1"
CONTRACT_VERSION = "1.0.0"
VALUE_STATUS = {"KNOWN", "UNKNOWN"}
TRAFFIC_STATUS = {"KNOWN", "UNKNOWN", "INFEASIBLE", "NO_FLEET"}


def _sid(prefix: str, *parts: object) -> str:
    payload = json.dumps(parts, separators=(",", ":"), allow_nan=False).encode()
    return f"{prefix}-" + hashlib.sha256(payload).hexdigest()[:20]


def _nn(v: Any, name: str) -> float:
    x = float(v)
    if not math.isfinite(x) or x < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return x


def _frac(v: Any, name: str) -> float:
    x = float(v)
    if not math.isfinite(x) or not 0 <= x <= 1:
        raise ValueError(f"{name} must be in [0,1]")
    return x


def _refs(raw: Mapping[str, Any], name: str) -> tuple[str, ...]:
    refs = tuple(str(x) for x in raw.get("provenance_refs", ()))
    if not refs:
        raise ValueError(f"{name} requires provenance")
    return refs


@dataclass(frozen=True)
class ValueParameter:
    status: str
    value: Optional[float]
    unit: str
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class TimelineContext:
    heavy_service_milestone_id: str
    heavy_service_threshold_year: int
    nep_milestone_id: str
    nep_threshold_year: int
    auto_spawn_fleet: bool
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class ServiceBinding:
    service_id: str
    generic_demand_eligible: bool
    traffic_role: str
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class VehicleClass:
    vehicle_class_id: str
    compatible_service_ids: tuple[str, ...]
    cargo_capacity_tonnes: ValueParameter
    passenger_capacity_persons: ValueParameter
    mission_duration_days: ValueParameter
    turnaround_days: ValueParameter
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class FleetAsset:
    vehicle_id: str
    vehicle_class_id: str
    owner_actor_id: str
    service_id: str
    commissioned_year: int
    retired_year: Optional[int]
    availability_fraction: ValueParameter
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class DemandAllocation:
    allocation_id: str
    actor_id: str
    origin_location_id: str
    destination_location_id: str
    service_id: str
    cargo_fraction_of_transport_requirement: float
    passenger_demand_persons_year: ValueParameter
    valid_from_year: int
    valid_to_year: Optional[int]
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class TrafficFleetPackage:
    format: str
    contract_version: str
    package_id: str
    demand_assignment_policy: str
    excluded_demand_location_ids: tuple[str, ...]
    timeline_context: TimelineContext
    service_bindings: tuple[ServiceBinding, ...]
    vehicle_classes: tuple[VehicleClass, ...]
    fleet_assets: tuple[FleetAsset, ...]
    demand_allocations: tuple[DemandAllocation, ...]


@dataclass(frozen=True)
class TrafficDemandStateV1:
    traffic_demand_state_id: str
    year: int
    location_id: str
    local_transport_requirement_tonnes_year: float
    assigned_cargo_demand_tonnes_year: float
    unassigned_cargo_demand_tonnes_year: float
    allocation_coverage_fraction: float
    passenger_demand_status: str
    assigned_passenger_demand_persons_year: Optional[float]
    assignment_status: str


@dataclass(frozen=True)
class TrafficServiceStateV1:
    traffic_service_state_id: str
    year: int
    service_id: str
    actor_id: str
    origin_location_id: str
    destination_location_id: str
    accessibility_status: str
    generic_demand_eligible: bool
    active_fleet_count: int
    available_trip_status: str
    available_trips: Optional[int]
    cargo_capacity_status: str
    cargo_capacity_tonnes_year: Optional[float]
    passenger_capacity_status: str
    passenger_capacity_persons_year: Optional[float]


@dataclass(frozen=True)
class FleetStateV1:
    fleet_state_id: str
    year: int
    vehicle_id: str
    vehicle_class_id: str
    service_id: str
    owner_actor_id: str
    status: str
    available_trip_status: str
    available_trips: Optional[int]
    realized_trips: int
    utilization_ratio: Optional[float]


@dataclass(frozen=True)
class VoyageStateV1:
    voyage_id: str
    year: int
    service_id: str
    vehicle_id: str
    voyage_ordinal: int
    origin_location_id: str
    destination_location_id: str
    cargo_tonnes: float
    passenger_movements: float
    departure_calls: int
    arrival_calls: int


@dataclass(frozen=True)
class RouteTrafficStateV1:
    route_traffic_state_id: str
    year: int
    allocation_id: str
    service_id: str
    actor_id: str
    origin_location_id: str
    destination_location_id: str
    accessibility_status: str
    traffic_status: str
    opening_cargo_backlog_tonnes: float
    new_cargo_demand_tonnes: float
    total_cargo_demand_tonnes: float
    cargo_service_capacity_status: str
    cargo_service_capacity_tonnes_year: Optional[float]
    realized_cargo_tonnes: Optional[float]
    closing_cargo_backlog_tonnes: Optional[float]
    opening_passenger_backlog_persons: float
    new_passenger_demand_status: str
    new_passenger_demand_persons: Optional[float]
    total_passenger_demand_persons: Optional[float]
    passenger_service_capacity_status: str
    passenger_service_capacity_persons_year: Optional[float]
    realized_passenger_movements: Optional[float]
    closing_passenger_backlog_persons: Optional[float]
    departure_calls: Optional[int]
    arrival_calls: Optional[int]
    realized_trips: Optional[int]
    available_trips: Optional[int]
    route_utilization_ratio: Optional[float]
    transport_service_ratio: Optional[float]


@dataclass(frozen=True)
class LocationTrafficStateV1:
    location_traffic_state_id: str
    year: int
    location_id: str
    cargo_inbound_tonnes: float
    cargo_outbound_tonnes: float
    cargo_throughput_tonnes_year: float
    passenger_inbound_movements: float
    passenger_outbound_movements: float
    passenger_movements_year: float
    arrival_calls: int
    departure_calls: int
    ship_calls_year: int
    transport_service_ratio: Optional[float]
    metric_scope: str


@dataclass(frozen=True)
class TrafficPressureOverrideV1:
    year: int
    location_id: str
    required_transport_tonnes_year: float
    available_transport_tonnes_year: float
    opening_backlog_clearance_tonnes_year: float
    allocation_coverage_fraction: float


def _param(raw: Mapping[str, Any], name: str, unit: str, fraction=False) -> ValueParameter:
    status = str(raw.get("status"))
    if status not in VALUE_STATUS:
        raise ValueError(f"{name}: invalid status")
    if raw.get("unit") != unit:
        raise ValueError(f"{name}: expected {unit}")
    rv = raw.get("value")
    if status == "UNKNOWN":
        if rv is not None:
            raise ValueError(f"{name}: UNKNOWN cannot carry value")
        value = None
    else:
        if rv is None:
            raise ValueError(f"{name}: KNOWN requires value")
        value = _frac(rv, name) if fraction else _nn(rv, name)
    return ValueParameter(status, value, unit, _refs(raw, name))


def load_traffic_fleet_package(data: Mapping[str, Any]) -> TrafficFleetPackage:
    if data.get("format") != FORMAT or data.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("unexpected Traffic/Fleet V1 contract")
    if data.get("demand_assignment_policy") != "EXPLICIT_OD_ONLY":
        raise ValueError("Traffic/Fleet V1 requires explicit OD allocation")
    t = data["timeline_context"]
    if bool(t.get("auto_spawn_fleet")):
        raise ValueError("timeline may not auto-spawn fleet")

    bindings = tuple(
        ServiceBinding(
            service_id=str(x["service_id"]),
            generic_demand_eligible=bool(x["generic_demand_eligible"]),
            traffic_role=str(x["traffic_role"]),
            provenance_refs=_refs(x, "service binding"),
        )
        for x in data.get("service_bindings", ())
    )
    if len({x.service_id for x in bindings}) != len(bindings):
        raise ValueError("duplicate service binding")

    classes = []
    for x in data.get("vehicle_classes", ()):
        classes.append(
            VehicleClass(
                vehicle_class_id=str(x["vehicle_class_id"]),
                compatible_service_ids=tuple(str(v) for v in x["compatible_service_ids"]),
                cargo_capacity_tonnes=_param(x["cargo_capacity_tonnes"], "cargo capacity", "tonne"),
                passenger_capacity_persons=_param(x["passenger_capacity_persons"], "passenger capacity", "person"),
                mission_duration_days=_param(x["mission_duration_days"], "mission duration", "day"),
                turnaround_days=_param(x["turnaround_days"], "turnaround", "day"),
                provenance_refs=_refs(x, "vehicle class"),
            )
        )
    if len({x.vehicle_class_id for x in classes}) != len(classes):
        raise ValueError("duplicate vehicle class")
    class_map = {x.vehicle_class_id: x for x in classes}
    binding_map = {x.service_id: x for x in bindings}

    assets = []
    for x in data.get("fleet_assets", ()):
        vc = str(x["vehicle_class_id"])
        sid = str(x["service_id"])
        if vc not in class_map:
            raise ValueError("fleet asset references unknown vehicle class")
        if sid not in binding_map or sid not in class_map[vc].compatible_service_ids:
            raise ValueError("fleet asset service incompatible with vehicle class")
        commissioned = int(x["commissioned_year"])
        retired = None if x.get("retired_year") is None else int(x["retired_year"])
        if retired is not None and retired < commissioned:
            raise ValueError("fleet asset retires before commissioning")
        assets.append(
            FleetAsset(
                vehicle_id=str(x["vehicle_id"]),
                vehicle_class_id=vc,
                owner_actor_id=str(x["owner_actor_id"]),
                service_id=sid,
                commissioned_year=commissioned,
                retired_year=retired,
                availability_fraction=_param(
                    x["availability_fraction"],
                    "fleet availability",
                    "fraction",
                    fraction=True,
                ),
                provenance_refs=_refs(x, "fleet asset"),
            )
        )
    if len({x.vehicle_id for x in assets}) != len(assets):
        raise ValueError("duplicate fleet asset")

    allocs = []
    seen_services = set()
    for x in data.get("demand_allocations", ()):
        sid = str(x["service_id"])
        if sid not in binding_map:
            raise ValueError("demand allocation references unknown service")
        if not binding_map[sid].generic_demand_eligible:
            raise ValueError("generic demand cannot bind to non-generic service")
        if sid in seen_services:
            raise ValueError("Traffic/Fleet V1 permits one demand allocation per service")
        seen_services.add(sid)
        vf = int(x["valid_from_year"])
        vt = None if x.get("valid_to_year") is None else int(x["valid_to_year"])
        if vt is not None and vt < vf:
            raise ValueError("invalid demand-allocation validity")
        allocs.append(
            DemandAllocation(
                allocation_id=str(x["allocation_id"]),
                actor_id=str(x["actor_id"]),
                origin_location_id=str(x["origin_location_id"]),
                destination_location_id=str(x["destination_location_id"]),
                service_id=sid,
                cargo_fraction_of_transport_requirement=_frac(
                    x["cargo_fraction_of_transport_requirement"],
                    "cargo allocation fraction",
                ),
                passenger_demand_persons_year=_param(
                    x["passenger_demand_persons_year"],
                    "passenger demand",
                    "person/year",
                ),
                valid_from_year=vf,
                valid_to_year=vt,
                provenance_refs=_refs(x, "demand allocation"),
            )
        )
    if len({x.allocation_id for x in allocs}) != len(allocs):
        raise ValueError("duplicate demand allocation")

    return TrafficFleetPackage(
        format=FORMAT,
        contract_version=CONTRACT_VERSION,
        package_id=str(data["package_id"]),
        demand_assignment_policy="EXPLICIT_OD_ONLY",
        excluded_demand_location_ids=tuple(str(x) for x in data.get("excluded_demand_location_ids", ())),
        timeline_context=TimelineContext(
            heavy_service_milestone_id=str(t["heavy_service_milestone_id"]),
            heavy_service_threshold_year=int(t["heavy_service_threshold_year"]),
            nep_milestone_id=str(t["nep_milestone_id"]),
            nep_threshold_year=int(t["nep_threshold_year"]),
            auto_spawn_fleet=False,
            provenance_refs=_refs(t, "traffic timeline context"),
        ),
        service_bindings=bindings,
        vehicle_classes=tuple(classes),
        fleet_assets=tuple(assets),
        demand_allocations=tuple(allocs),
    )


def load_traffic_fleet_path(path: Path) -> TrafficFleetPackage:
    return load_traffic_fleet_package(json.loads(Path(path).read_text()))


class TrafficFleetRuntime:
    def __init__(
        self,
        package: TrafficFleetPackage,
        accessibility: AccessibilityPackage,
        demand_pressure: DemandPressurePackage,
    ):
        self.package = package
        self.accessibility = {x.service_id: x for x in accessibility.service_paths}
        self.demand_runtime = DemandPressureRuntime(demand_pressure)
        self.transport_channel = next(
            (x for x in demand_pressure.channels if x.channel_id == "TRANSPORT"),
            None,
        )
        if self.transport_channel is None or self.transport_channel.unit != "tonnes/year":
            raise ValueError("Traffic/Fleet V1 requires TRANSPORT tonnes/year channel")
        if set(package.excluded_demand_location_ids) != set(demand_pressure.excluded_location_ids):
            raise ValueError("traffic demand scope must match demand-pressure exclusions")
        self.bindings = {x.service_id: x for x in package.service_bindings}
        for sid in self.bindings:
            if sid not in self.accessibility:
                raise ValueError("traffic service binding lacks Accessibility V1 path")
        self.classes = {x.vehicle_class_id: x for x in package.vehicle_classes}
        self.assets = {x.vehicle_id: x for x in package.fleet_assets}
        self.backlog: dict[str, tuple[float, float]] = {}

    @staticmethod
    def _days(year: int) -> int:
        return 366 if calendar.isleap(year) else 365

    def _active_allocations(self, year: int) -> tuple[DemandAllocation, ...]:
        return tuple(
            x for x in self.package.demand_allocations
            if year >= x.valid_from_year and (x.valid_to_year is None or year <= x.valid_to_year)
        )

    def _active_assets(self, year: int, service_id: str) -> tuple[FleetAsset, ...]:
        return tuple(
            x for x in self.package.fleet_assets
            if x.service_id == service_id
            and year >= x.commissioned_year
            and (x.retired_year is None or year <= x.retired_year)
        )

    def _asset_trip_capacity(self, asset: FleetAsset, year: int) -> Optional[int]:
        cls = self.classes[asset.vehicle_class_id]
        vals = (
            cls.mission_duration_days.value,
            cls.turnaround_days.value,
            asset.availability_fraction.value,
        )
        if any(x is None for x in vals):
            return None
        cycle = float(vals[0]) + float(vals[1])
        if cycle <= 0:
            raise ValueError("vehicle mission+turnaround cycle must be positive")
        return int(math.floor(self._days(year) * float(vals[2]) / cycle))

    def step_year(
        self,
        *,
        year: int,
        states: Mapping[str, Any],
        additional_requirements: Mapping[tuple[str, str], float] | None = None,
    ) -> tuple[
        tuple[TrafficDemandStateV1, ...],
        tuple[TrafficServiceStateV1, ...],
        tuple[FleetStateV1, ...],
        tuple[VoyageStateV1, ...],
        tuple[RouteTrafficStateV1, ...],
        tuple[LocationTrafficStateV1, ...],
        tuple[TrafficPressureOverrideV1, ...],
    ]:
        obs = self.demand_runtime.derive(
            states,
            year=year,
            additional_requirements=additional_requirements,
        )
        transport_req = {
            x.location_id: x.required for x in obs if x.channel_id == "TRANSPORT"
        }
        active_allocs = self._active_allocations(year)
        by_dest: dict[str, list[DemandAllocation]] = {}
        for a in active_allocs:
            if a.origin_location_id not in states or a.destination_location_id not in states:
                raise ValueError("traffic allocation references unknown runtime location")
            service = self.accessibility[a.service_id]
            if (
                service.actor_id != a.actor_id
                or service.origin_location_id != a.origin_location_id
                or service.destination_location_id != a.destination_location_id
            ):
                raise ValueError("traffic allocation does not match Accessibility V1 service scope")
            by_dest.setdefault(a.destination_location_id, []).append(a)

        demand_states = []
        for location_id in sorted(transport_req):
            rows = by_dest.get(location_id, [])
            coverage = sum(x.cargo_fraction_of_transport_requirement for x in rows)
            if coverage > 1 + 1e-12:
                raise ValueError("cargo OD allocation exceeds local transport requirement")
            required = transport_req[location_id]
            passenger_values = [x.passenger_demand_persons_year.value for x in rows]
            passenger_status = "KNOWN" if rows and all(x is not None for x in passenger_values) else "UNKNOWN"
            passenger_total = (
                sum(float(x) for x in passenger_values)
                if passenger_status == "KNOWN"
                else None
            )
            demand_states.append(
                TrafficDemandStateV1(
                    traffic_demand_state_id=_sid("td", year, location_id),
                    year=year,
                    location_id=location_id,
                    local_transport_requirement_tonnes_year=required,
                    assigned_cargo_demand_tonnes_year=required * coverage,
                    unassigned_cargo_demand_tonnes_year=required * (1 - coverage),
                    allocation_coverage_fraction=coverage,
                    passenger_demand_status=passenger_status,
                    assigned_passenger_demand_persons_year=passenger_total,
                    assignment_status=(
                        "FULLY_ASSIGNED" if math.isclose(coverage, 1.0, abs_tol=1e-12)
                        else "PARTIALLY_ASSIGNED" if coverage > 0 else "UNASSIGNED_OD"
                    ),
                )
            )

        service_states = []
        fleet_states: list[FleetStateV1] = []
        service_asset_caps: dict[str, list[tuple[FleetAsset, Optional[int], Optional[float], Optional[float]]]] = {}
        for binding in sorted(self.package.service_bindings, key=lambda x: x.service_id):
            service = self.accessibility[binding.service_id]
            active_assets = self._active_assets(year, binding.service_id)
            entries = []
            trip_values = []
            cargo_values = []
            pax_values = []
            for asset in sorted(active_assets, key=lambda x: x.vehicle_id):
                trips = self._asset_trip_capacity(asset, year)
                cls = self.classes[asset.vehicle_class_id]
                cargo = None if trips is None or cls.cargo_capacity_tonnes.value is None else trips * cls.cargo_capacity_tonnes.value
                pax = None if trips is None or cls.passenger_capacity_persons.value is None else trips * cls.passenger_capacity_persons.value
                entries.append((asset, trips, cargo, pax))
                trip_values.append(trips)
                cargo_values.append(cargo)
                pax_values.append(pax)
            service_asset_caps[binding.service_id] = entries
            if not active_assets:
                trips_status = cargo_status = pax_status = "KNOWN"
                total_trips = 0
                cargo_cap = pax_cap = 0.0
            else:
                trips_status = "KNOWN" if all(x is not None for x in trip_values) else "UNKNOWN"
                cargo_status = "KNOWN" if all(x is not None for x in cargo_values) else "UNKNOWN"
                pax_status = "KNOWN" if all(x is not None for x in pax_values) else "UNKNOWN"
                total_trips = sum(int(x) for x in trip_values) if trips_status == "KNOWN" else None
                cargo_cap = sum(float(x) for x in cargo_values) if cargo_status == "KNOWN" else None
                pax_cap = sum(float(x) for x in pax_values) if pax_status == "KNOWN" else None
            service_states.append(
                TrafficServiceStateV1(
                    traffic_service_state_id=_sid("ts", year, binding.service_id),
                    year=year,
                    service_id=binding.service_id,
                    actor_id=service.actor_id,
                    origin_location_id=service.origin_location_id,
                    destination_location_id=service.destination_location_id,
                    accessibility_status=service.status,
                    generic_demand_eligible=binding.generic_demand_eligible,
                    active_fleet_count=len(active_assets),
                    available_trip_status=trips_status,
                    available_trips=total_trips,
                    cargo_capacity_status=cargo_status,
                    cargo_capacity_tonnes_year=cargo_cap,
                    passenger_capacity_status=pax_status,
                    passenger_capacity_persons_year=pax_cap,
                )
            )

        voyages: list[VoyageStateV1] = []
        route_states: list[RouteTrafficStateV1] = []
        realized_trip_count: dict[str, int] = {x.vehicle_id: 0 for x in self.package.fleet_assets}
        for a in sorted(active_allocs, key=lambda x: x.allocation_id):
            service = self.accessibility[a.service_id]
            entries = service_asset_caps[a.service_id]
            required = transport_req[a.destination_location_id] * a.cargo_fraction_of_transport_requirement
            opening_cargo, opening_pax = self.backlog.get(a.allocation_id, (0.0, 0.0))
            new_pax = a.passenger_demand_persons_year.value
            total_cargo = opening_cargo + required
            total_pax = None if new_pax is None else opening_pax + new_pax

            if not entries:
                traffic_status = "NO_FLEET"
                cargo_capacity = 0.0
                pax_capacity = 0.0
                realized_cargo = 0.0
                realized_pax = None if total_pax is None else 0.0
                realized_trips = 0
                available_trips = 0
            elif service.status == "INFEASIBLE":
                traffic_status = "INFEASIBLE"
                cargo_capacity = 0.0
                pax_capacity = 0.0
                realized_cargo = 0.0
                realized_pax = None if total_pax is None else 0.0
                realized_trips = 0
                available_trips = sum(x[1] or 0 for x in entries) if all(x[1] is not None for x in entries) else None
            elif service.status != "FEASIBLE" or any(x[1] is None or x[2] is None or x[3] is None for x in entries) or total_pax is None:
                traffic_status = "UNKNOWN"
                cargo_capacity = None
                pax_capacity = None
                realized_cargo = None
                realized_pax = None
                realized_trips = None
                available_trips = None
            else:
                traffic_status = "KNOWN"
                available_trips = sum(int(x[1]) for x in entries)
                cargo_capacity = sum(float(x[2]) for x in entries)
                pax_capacity = sum(float(x[3]) for x in entries)
                origin_handling = _nn(getattr(states[a.origin_location_id], "transport"), "origin transport handling")
                dest_handling = _nn(getattr(states[a.destination_location_id], "transport"), "destination transport handling")
                cargo_capacity = min(cargo_capacity, origin_handling, dest_handling)
                rem_cargo = min(total_cargo, cargo_capacity)
                rem_pax = min(total_pax, pax_capacity)
                realized_cargo = 0.0
                realized_pax = 0.0
                ordinal = 0
                for asset, trip_cap, _, _ in entries:
                    cls = self.classes[asset.vehicle_class_id]
                    ccap = float(cls.cargo_capacity_tonnes.value or 0)
                    pcap = float(cls.passenger_capacity_persons.value or 0)
                    for _ in range(int(trip_cap)):
                        if rem_cargo <= 1e-12 and rem_pax <= 1e-12:
                            break
                        c = min(ccap, rem_cargo)
                        p = min(pcap, rem_pax)
                        if c <= 0 and p <= 0:
                            break
                        ordinal += 1
                        rem_cargo -= c
                        rem_pax -= p
                        realized_cargo += c
                        realized_pax += p
                        realized_trip_count[asset.vehicle_id] += 1
                        voyages.append(
                            VoyageStateV1(
                                voyage_id=_sid("voy", year, a.service_id, asset.vehicle_id, ordinal),
                                year=year,
                                service_id=a.service_id,
                                vehicle_id=asset.vehicle_id,
                                voyage_ordinal=ordinal,
                                origin_location_id=a.origin_location_id,
                                destination_location_id=a.destination_location_id,
                                cargo_tonnes=c,
                                passenger_movements=p,
                                departure_calls=1,
                                arrival_calls=1,
                            )
                        )
                realized_trips = sum(realized_trip_count[x[0].vehicle_id] for x in entries)

            closing_cargo = None if realized_cargo is None else total_cargo - realized_cargo
            closing_pax = None if realized_pax is None or total_pax is None else total_pax - realized_pax
            if closing_cargo is not None and closing_pax is not None:
                self.backlog[a.allocation_id] = (closing_cargo, closing_pax)
            if realized_trips is None or available_trips in (None, 0):
                util = None if realized_trips is None else (0.0 if available_trips == 0 else None)
            else:
                util = realized_trips / available_trips
            ratios = []
            if total_cargo > 0 and realized_cargo is not None:
                ratios.append(realized_cargo / total_cargo)
            if total_pax is not None and total_pax > 0 and realized_pax is not None:
                ratios.append(realized_pax / total_pax)
            service_ratio = min(ratios) if ratios else (1.0 if realized_cargo is not None and total_cargo == 0 and total_pax == 0 else None)
            route_states.append(
                RouteTrafficStateV1(
                    route_traffic_state_id=_sid("rt", year, a.allocation_id),
                    year=year,
                    allocation_id=a.allocation_id,
                    service_id=a.service_id,
                    actor_id=a.actor_id,
                    origin_location_id=a.origin_location_id,
                    destination_location_id=a.destination_location_id,
                    accessibility_status=service.status,
                    traffic_status=traffic_status,
                    opening_cargo_backlog_tonnes=opening_cargo,
                    new_cargo_demand_tonnes=required,
                    total_cargo_demand_tonnes=total_cargo,
                    cargo_service_capacity_status="KNOWN" if cargo_capacity is not None else "UNKNOWN",
                    cargo_service_capacity_tonnes_year=cargo_capacity,
                    realized_cargo_tonnes=realized_cargo,
                    closing_cargo_backlog_tonnes=closing_cargo,
                    opening_passenger_backlog_persons=opening_pax,
                    new_passenger_demand_status=a.passenger_demand_persons_year.status,
                    new_passenger_demand_persons=new_pax,
                    total_passenger_demand_persons=total_pax,
                    passenger_service_capacity_status="KNOWN" if pax_capacity is not None else "UNKNOWN",
                    passenger_service_capacity_persons_year=pax_capacity,
                    realized_passenger_movements=realized_pax,
                    closing_passenger_backlog_persons=closing_pax,
                    departure_calls=realized_trips,
                    arrival_calls=realized_trips,
                    realized_trips=realized_trips,
                    available_trips=available_trips,
                    route_utilization_ratio=util,
                    transport_service_ratio=service_ratio,
                )
            )

        for asset in sorted(self.package.fleet_assets, key=lambda x: x.vehicle_id):
            active = asset in self._active_assets(year, asset.service_id)
            trips = self._asset_trip_capacity(asset, year) if active else 0
            realized = realized_trip_count.get(asset.vehicle_id, 0)
            fleet_states.append(
                FleetStateV1(
                    fleet_state_id=_sid("fs", year, asset.vehicle_id),
                    year=year,
                    vehicle_id=asset.vehicle_id,
                    vehicle_class_id=asset.vehicle_class_id,
                    service_id=asset.service_id,
                    owner_actor_id=asset.owner_actor_id,
                    status="ACTIVE" if active else "INACTIVE",
                    available_trip_status="KNOWN" if trips is not None else "UNKNOWN",
                    available_trips=trips,
                    realized_trips=realized,
                    utilization_ratio=None if trips is None else (0.0 if trips == 0 else realized / trips),
                )
            )

        loc_metrics = []
        metric_locations = set(transport_req)
        metric_locations.update(x.origin_location_id for x in route_states)
        metric_locations.update(x.destination_location_id for x in route_states)
        for location_id in sorted(metric_locations):
            inbound = sum(x.cargo_tonnes for x in voyages if x.destination_location_id == location_id)
            outbound = sum(x.cargo_tonnes for x in voyages if x.origin_location_id == location_id)
            pin = sum(x.passenger_movements for x in voyages if x.destination_location_id == location_id)
            pout = sum(x.passenger_movements for x in voyages if x.origin_location_id == location_id)
            arrivals = sum(x.arrival_calls for x in voyages if x.destination_location_id == location_id)
            departures = sum(x.departure_calls for x in voyages if x.origin_location_id == location_id)
            dstate = next(
                (x for x in demand_states if x.location_id == location_id),
                None,
            )
            route_rows = [x for x in route_states if x.destination_location_id == location_id]
            ratio = None
            if (
                dstate is not None
                and math.isclose(
                    dstate.allocation_coverage_fraction,
                    1.0,
                    abs_tol=1e-12,
                )
                and route_rows
                and all(
                    x.transport_service_ratio is not None
                    for x in route_rows
                )
            ):
                total_demand = sum(x.total_cargo_demand_tonnes for x in route_rows)
                total_realized = sum(float(x.realized_cargo_tonnes) for x in route_rows)
                ratio = 1.0 if total_demand == 0 else min(1.0, total_realized / total_demand)
            loc_metrics.append(
                LocationTrafficStateV1(
                    location_traffic_state_id=_sid("lt", year, location_id),
                    year=year,
                    location_id=location_id,
                    cargo_inbound_tonnes=inbound,
                    cargo_outbound_tonnes=outbound,
                    cargo_throughput_tonnes_year=inbound + outbound,
                    passenger_inbound_movements=pin,
                    passenger_outbound_movements=pout,
                    passenger_movements_year=pin + pout,
                    arrival_calls=arrivals,
                    departure_calls=departures,
                    ship_calls_year=arrivals + departures,
                    transport_service_ratio=ratio,
                    metric_scope="MODELED_GENERIC_TRAFFIC_ONLY",
                )
            )

        overrides = []
        for d in demand_states:
            if not math.isclose(d.allocation_coverage_fraction, 1.0, abs_tol=1e-12):
                continue
            rows = [x for x in route_states if x.destination_location_id == d.location_id]
            if not rows or any(x.cargo_service_capacity_tonnes_year is None for x in rows):
                continue
            opening_backlog = sum(x.opening_cargo_backlog_tonnes for x in rows)
            service_capacity = sum(float(x.cargo_service_capacity_tonnes_year) for x in rows)
            local_handling = _nn(getattr(states[d.location_id], "transport"), "local transport handling")
            overrides.append(
                TrafficPressureOverrideV1(
                    year=year,
                    location_id=d.location_id,
                    required_transport_tonnes_year=d.local_transport_requirement_tonnes_year + opening_backlog,
                    available_transport_tonnes_year=min(local_handling, service_capacity),
                    opening_backlog_clearance_tonnes_year=opening_backlog,
                    allocation_coverage_fraction=1.0,
                )
            )

        return (
            tuple(demand_states),
            tuple(service_states),
            tuple(fleet_states),
            tuple(voyages),
            tuple(route_states),
            tuple(loc_metrics),
            tuple(overrides),
        )


__all__ = [
    "CONTRACT_VERSION",
    "FORMAT",
    "DemandAllocation",
    "FleetAsset",
    "FleetStateV1",
    "LocationTrafficStateV1",
    "RouteTrafficStateV1",
    "ServiceBinding",
    "TrafficDemandStateV1",
    "TrafficFleetPackage",
    "TrafficFleetRuntime",
    "TrafficPressureOverrideV1",
    "TrafficServiceStateV1",
    "ValueParameter",
    "VehicleClass",
    "VoyageStateV1",
    "load_traffic_fleet_package",
    "load_traffic_fleet_path",
]
