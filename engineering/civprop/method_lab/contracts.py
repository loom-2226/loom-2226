"""Typed contracts for the synthetic CIVPROP propagation Method Lab V1.

This module owns no propagation logic. It freezes one small cross-engine input
bundle and one common result shape so candidate engines can be compared without
moving the goalposts.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Optional, Protocol, runtime_checkable

from engineering.civprop.contracts.actor_state_v1 import (
    ActorStatePackage,
    load_actor_state_package,
)
from engineering.civprop.contracts.accessibility_v1 import (
    AccessibilityPackage,
    load_accessibility_package,
)
from engineering.civprop.contracts.demand_pressure_v1 import (
    DemandPressurePackage,
    load_demand_pressure_package,
)
from engineering.civprop.contracts.project_economics_v1 import (
    ProjectEconomicsPackage,
    load_project_economics_package,
)


ALLOWED_PLACEMENTS = {"SURFACE", "ORBITAL", "FREE_SPACE"}
ALLOWED_CAPABILITY_STATUS = {"USABLE", "CONDITIONAL", "UNUSABLE", "UNKNOWN"}
ALLOWED_ACCESSIBILITY_STATUS = {"FEASIBLE", "INFEASIBLE", "UNKNOWN"}


@dataclass(frozen=True)
class CapacityVector:
    power: float = 0.0
    resource: float = 0.0
    industrial: float = 0.0
    habitat: float = 0.0
    shipyard: float = 0.0
    transport: float = 0.0


@dataclass(frozen=True)
class ActorInput:
    actor_id: str
    actor_type: str
    starting_capital: Optional[float] = None
    annual_capital_inflow: Optional[float] = None


@dataclass(frozen=True)
class LocationInput:
    location_id: str
    parent_body_id: Optional[str]
    placement: str
    biological_population: float
    transient_population: float
    workforce: float
    capital: float
    capacities: CapacityVector


@dataclass(frozen=True)
class TechnologyFrontier:
    tech_id: str
    frontier_year: int


@dataclass(frozen=True)
class ActorCapability:
    actor_id: str
    tech_id: str
    status: str
    valid_from: int
    valid_to: Optional[int]
    conditions: tuple[str, ...] = ()


@dataclass(frozen=True)
class AccessibilityPoint:
    year: int
    status: str
    generalized_cost: Optional[float]


@dataclass(frozen=True)
class AccessibilityProfile:
    origin_location_id: str
    destination_location_id: str
    years: tuple[AccessibilityPoint, ...]


@dataclass(frozen=True)
class ResourceBelief:
    resource_id: str
    location_id: str
    evidence_status: str
    prior_probability: float
    observation_sensitivity: float
    false_positive_probability: float


@dataclass(frozen=True)
class AnnualValue:
    year: int
    value: float


@dataclass(frozen=True)
class DemandSignal:
    signal_id: str
    unit: str
    values: tuple[AnnualValue, ...]


@dataclass(frozen=True)
class ProjectArchetype:
    project_archetype_id: str
    project_kind: str
    allowed_placements: tuple[str, ...]
    required_tech: tuple[str, ...]
    capital_cost: float
    construction_lag_years: int
    output_capacities: CapacityVector
    minimum_input_capacities: CapacityVector


@dataclass(frozen=True)
class LabScenario:
    format: str
    fixture_id: str
    start_year: int
    end_year: int
    units: Mapping[str, str]
    actors: tuple[ActorInput, ...]
    actor_state_v1: Optional[ActorStatePackage]
    locations: tuple[LocationInput, ...]
    technology_frontier: tuple[TechnologyFrontier, ...]
    actor_capability: tuple[ActorCapability, ...]
    accessibility_v1: Optional[AccessibilityPackage]
    accessibility: tuple[AccessibilityProfile, ...]
    resource_beliefs: tuple[ResourceBelief, ...]
    demand_pressure_v1: Optional[DemandPressurePackage]
    demand_signals: tuple[DemandSignal, ...]
    project_economics_v1: Optional[ProjectEconomicsPackage]
    project_archetypes: tuple[ProjectArchetype, ...]


@dataclass(frozen=True)
class TruthResource:
    resource_id: str
    present: bool
    grade_index: float


@dataclass(frozen=True)
class LabTruth:
    format: str
    fixture_id: str
    resources: tuple[TruthResource, ...]


@dataclass(frozen=True)
class LabBundle:
    manifest: Mapping[str, Any]
    scenario: LabScenario
    truth: LabTruth
    bundle_sha256: str


@dataclass(frozen=True)
class RunMetadata:
    format: str
    run_id: str
    engine_id: str
    engine_version: str
    input_bundle_sha256: str
    seed: int
    start_year: int
    end_year: int


@dataclass(frozen=True)
class LocationState:
    year: int
    location_id: str
    biological_population: float
    transient_population: float
    workforce: float
    capital: float
    capacities: CapacityVector


@dataclass(frozen=True)
class FacilityRecord:
    facility_id: str
    project_archetype_id: str
    location_id: str
    owner_actor_id: str
    committed_year: int
    commissioned_year: int
    status: str
    capital: float
    capacities: CapacityVector


@dataclass(frozen=True)
class DecisionRecord:
    decision_id: str
    year: int
    actor_id: str
    action: str
    target_location_id: Optional[str]
    project_archetype_id: Optional[str]
    status: str
    rationale_codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class EventRecord:
    event_id: str
    year: int
    event_type: str
    actor_id: Optional[str]
    location_id: Optional[str]
    parent_event_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class FlowRecord:
    flow_id: str
    year: int
    flow_type: str
    origin_location_id: Optional[str]
    destination_location_id: Optional[str]
    amount: float
    unit: str
    actor_id: Optional[str] = None


@dataclass(frozen=True)
class LabResult:
    metadata: RunMetadata
    annual_states: tuple[LocationState, ...]
    facilities: tuple[FacilityRecord, ...]
    decisions: tuple[DecisionRecord, ...]
    events: tuple[EventRecord, ...]
    flows: tuple[FlowRecord, ...]


@runtime_checkable
class PropagationEngine(Protocol):
    engine_id: str
    engine_version: str

    def run(self, bundle: LabBundle, seed: int) -> LabResult:
        ...


def _plain(value: Any) -> Any:
    if is_dataclass(value):
        return {k: _plain(v) for k, v in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(v) for v in value]
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(_plain(value), sort_keys=True, separators=(",", ":"), allow_nan=False)


def _capacity(data: Mapping[str, Any] | None = None) -> CapacityVector:
    data = data or {}
    return CapacityVector(**{k: float(data.get(k, 0.0)) for k in CapacityVector.__dataclass_fields__})


def _unique(items, key, label: str) -> None:
    values = [key(x) for x in items]
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {label}")


def _nonnegative_capacity(capacity: CapacityVector) -> None:
    for name, value in asdict(capacity).items():
        if value < 0:
            raise ValueError(f"negative capacity {name}")


def _parse_scenario(data: Mapping[str, Any]) -> LabScenario:
    return LabScenario(
        format=data["format"],
        fixture_id=data["fixture_id"],
        start_year=int(data["horizon"]["start_year"]),
        end_year=int(data["horizon"]["end_year"]),
        units=dict(data["units"]),
        actors=tuple(
            ActorInput(
                actor_id=x["actor_id"],
                actor_type=x["actor_type"],
                starting_capital=(
                    None if x.get("starting_capital") is None
                    else float(x["starting_capital"])
                ),
                annual_capital_inflow=(
                    None if x.get("annual_capital_inflow") is None
                    else float(x["annual_capital_inflow"])
                ),
            )
            for x in data["actors"]
        ),
        actor_state_v1=(
            None
            if data.get("actor_state_v1") is None
            else load_actor_state_package(data["actor_state_v1"])
        ),
        locations=tuple(
            LocationInput(
                location_id=x["location_id"],
                parent_body_id=x.get("parent_body_id"),
                placement=x["placement"],
                biological_population=float(x["initial_state"]["biological_population"]),
                transient_population=float(x["initial_state"]["transient_population"]),
                workforce=float(x["initial_state"]["workforce"]),
                capital=float(x["initial_state"]["capital"]),
                capacities=_capacity(x["initial_state"]["capacities"]),
            )
            for x in data["locations"]
        ),
        technology_frontier=tuple(
            TechnologyFrontier(x["tech_id"], int(x["frontier_year"]))
            for x in data["technology_frontier"]
        ),
        actor_capability=tuple(
            ActorCapability(
                actor_id=x["actor_id"],
                tech_id=x["tech_id"],
                status=x["status"],
                valid_from=int(x["valid_from"]),
                valid_to=None if x.get("valid_to") is None else int(x["valid_to"]),
                conditions=tuple(x.get("conditions", ())),
            )
            for x in data["actor_capability"]
        ),
        accessibility_v1=(
            None
            if data.get("accessibility_v1") is None
            else load_accessibility_package(data["accessibility_v1"])
        ),
        accessibility=tuple(
            AccessibilityProfile(
                origin_location_id=x["origin_location_id"],
                destination_location_id=x["destination_location_id"],
                years=tuple(
                    AccessibilityPoint(
                        year=int(y["year"]),
                        status=y["status"],
                        generalized_cost=None if y.get("generalized_cost") is None else float(y["generalized_cost"]),
                    )
                    for y in x["years"]
                ),
            )
            for x in data.get("accessibility", ())
        ),
        resource_beliefs=tuple(
            ResourceBelief(
                resource_id=x["resource_id"],
                location_id=x["location_id"],
                evidence_status=x["evidence_status"],
                prior_probability=float(x["prior_probability"]),
                observation_sensitivity=float(x["observation_sensitivity"]),
                false_positive_probability=float(x["false_positive_probability"]),
            )
            for x in data["resource_beliefs"]
        ),
        demand_pressure_v1=(
            None
            if data.get("demand_pressure_v1") is None
            else load_demand_pressure_package(data["demand_pressure_v1"])
        ),
        demand_signals=tuple(
            DemandSignal(
                signal_id=x["signal_id"],
                unit=x["unit"],
                values=tuple(AnnualValue(int(y["year"]), float(y["value"])) for y in x["values"]),
            )
            for x in data.get("demand_signals", ())
        ),
        project_economics_v1=(
            None
            if data.get("project_economics_v1") is None
            else load_project_economics_package(data["project_economics_v1"])
        ),
        project_archetypes=tuple(
            ProjectArchetype(
                project_archetype_id=x["project_archetype_id"],
                project_kind=x["project_kind"],
                allowed_placements=tuple(x["allowed_placements"]),
                required_tech=tuple(x.get("required_tech", ())),
                capital_cost=float(x["capital_cost"]),
                construction_lag_years=int(x["construction_lag_years"]),
                output_capacities=_capacity(x.get("output_capacities")),
                minimum_input_capacities=_capacity(x.get("minimum_input_capacities")),
            )
            for x in data["project_archetypes"]
        ),
    )


def _parse_truth(data: Mapping[str, Any]) -> LabTruth:
    return LabTruth(
        format=data["format"],
        fixture_id=data["fixture_id"],
        resources=tuple(
            TruthResource(
                resource_id=x["resource_id"],
                present=bool(x["present"]),
                grade_index=float(x["grade_index"]),
            )
            for x in data["resources"]
        ),
    )


def _validate_scenario(s: LabScenario, truth: LabTruth) -> None:
    if s.format != "CIVPROP_METHOD_LAB_SCENARIO_V1":
        raise ValueError("unexpected scenario format")
    if truth.format != "CIVPROP_METHOD_LAB_TRUTH_V1":
        raise ValueError("unexpected truth format")
    if s.fixture_id != truth.fixture_id:
        raise ValueError("fixture identity mismatch")
    if s.start_year >= s.end_year:
        raise ValueError("invalid horizon")

    _unique(s.actors, lambda x: x.actor_id, "actor id")
    _unique(s.locations, lambda x: x.location_id, "location id")
    _unique(s.technology_frontier, lambda x: x.tech_id, "technology id")
    _unique(s.project_archetypes, lambda x: x.project_archetype_id, "project archetype id")
    _unique(s.resource_beliefs, lambda x: x.resource_id, "resource belief id")
    _unique(truth.resources, lambda x: x.resource_id, "truth resource id")

    actor_ids = {x.actor_id for x in s.actors}
    location_ids = {x.location_id for x in s.locations}
    tech_ids = {x.tech_id for x in s.technology_frontier}

    if s.actor_state_v1 is not None:
        state_actor_ids = {x.actor_id for x in s.actor_state_v1.actors}
        if state_actor_ids != actor_ids:
            raise ValueError("actor-state identities do not match scenario actors")
    for actor in s.actors:
        legacy_values = (actor.starting_capital, actor.annual_capital_inflow)
        if s.actor_state_v1 is None:
            if any(value is None for value in legacy_values):
                raise ValueError("legacy actor budget fields required without actor-state contract")
            if actor.starting_capital < 0 or actor.annual_capital_inflow < 0:
                raise ValueError("negative actor capital")
        elif any(value is not None for value in legacy_values):
            raise ValueError("actor-state scenario cannot also carry legacy budget fields")
    for location in s.locations:
        if location.placement not in ALLOWED_PLACEMENTS:
            raise ValueError("invalid placement")
        if location.placement != "FREE_SPACE" and location.parent_body_id is None:
            raise ValueError("body-bound location missing parent body")
        if min(location.biological_population, location.transient_population, location.workforce, location.capital) < 0:
            raise ValueError("negative initial state")
        _nonnegative_capacity(location.capacities)

    for cap in s.actor_capability:
        if cap.actor_id not in actor_ids or cap.tech_id not in tech_ids:
            raise ValueError("capability references unknown actor/technology")
        if cap.status not in ALLOWED_CAPABILITY_STATUS:
            raise ValueError("invalid capability status")
        if cap.valid_from < s.start_year or (cap.valid_to is not None and cap.valid_to < cap.valid_from):
            raise ValueError("invalid capability validity")

    if s.accessibility_v1 is not None:
        if s.accessibility:
            raise ValueError("accessibility-v1 scenario cannot also carry legacy accessibility profiles")
        bound_locations = {x.location_id for x in s.accessibility_v1.location_bindings}
        if bound_locations != location_ids:
            raise ValueError("accessibility-v1 location bindings do not match scenario locations")

    for profile in s.accessibility:
        if profile.origin_location_id not in location_ids or profile.destination_location_id not in location_ids:
            raise ValueError("accessibility references unknown location")
        seen_years = set()
        for point in profile.years:
            if point.year in seen_years:
                raise ValueError("duplicate accessibility year")
            seen_years.add(point.year)
            if not s.start_year <= point.year <= s.end_year:
                raise ValueError("accessibility year outside horizon")
            if point.status not in ALLOWED_ACCESSIBILITY_STATUS:
                raise ValueError("invalid accessibility status")
            if point.status == "UNKNOWN" and point.generalized_cost is not None:
                raise ValueError("unknown accessibility cannot carry invented cost")
            if point.generalized_cost is not None and point.generalized_cost < 0:
                raise ValueError("negative accessibility cost")

    for belief in s.resource_beliefs:
        if belief.location_id not in location_ids:
            raise ValueError("resource belief unknown location")
        for value in (belief.prior_probability, belief.observation_sensitivity, belief.false_positive_probability):
            if not 0 <= value <= 1:
                raise ValueError("invalid resource probability")

    visible_resources = {x.resource_id for x in s.resource_beliefs}
    for resource in truth.resources:
        if resource.resource_id not in visible_resources:
            raise ValueError("truth resource has no visible question")
        if not 0 <= resource.grade_index <= 1:
            raise ValueError("invalid truth grade")

    if s.demand_pressure_v1 is not None and s.demand_signals:
        raise ValueError("demand-pressure-v1 scenario cannot also carry legacy demand signals")
    if s.demand_pressure_v1 is None and not s.demand_signals:
        raise ValueError("legacy scenario requires demand signals")

    for signal in s.demand_signals:
        years = [x.year for x in signal.values]
        if len(years) != len(set(years)):
            raise ValueError("duplicate demand-signal year")
        if any(not s.start_year <= x.year <= s.end_year or x.value < 0 for x in signal.values):
            raise ValueError("invalid demand signal")

    if s.project_economics_v1 is not None:
        economics_ids = {
            x.project_archetype_id for x in s.project_economics_v1.projects
        }
        project_ids = {x.project_archetype_id for x in s.project_archetypes}
        if not project_ids <= economics_ids:
            raise ValueError("project economics missing runtime project")
        if s.units.get("project_capital") != s.project_economics_v1.capital_unit:
            raise ValueError("project economics capital unit mismatch")

    for project in s.project_archetypes:
        if project.capital_cost <= 0 or project.construction_lag_years < 1:
            raise ValueError("invalid project economics")
        if not project.allowed_placements or not set(project.allowed_placements) <= ALLOWED_PLACEMENTS:
            raise ValueError("invalid project placement")
        if not set(project.required_tech) <= tech_ids:
            raise ValueError("project requires unknown technology")
        _nonnegative_capacity(project.output_capacities)
        _nonnegative_capacity(project.minimum_input_capacities)


def load_bundle(directory: Path) -> LabBundle:
    directory = Path(directory)
    manifest = json.loads((directory / "manifest_v1.json").read_bytes())
    if manifest.get("format") != "CIVPROP_METHOD_LAB_BUNDLE_V1":
        raise ValueError("unexpected method-lab manifest")

    payloads: dict[str, bytes] = {}
    for name, expected in manifest["sha256"].items():
        payload = (directory / name).read_bytes()
        payloads[name] = payload
        if hashlib.sha256(payload).hexdigest() != expected:
            raise ValueError(f"hash mismatch: {name}")

    scenario = _parse_scenario(json.loads(payloads[manifest["scenario_file"]]))
    truth = _parse_truth(json.loads(payloads[manifest["truth_file"]]))
    _validate_scenario(scenario, truth)

    joined = payloads[manifest["scenario_file"]] + b"\n" + payloads[manifest["truth_file"]]
    bundle_sha = hashlib.sha256(joined).hexdigest()
    if bundle_sha != manifest["bundle_sha256"]:
        raise ValueError("bundle hash mismatch")
    return LabBundle(manifest=manifest, scenario=scenario, truth=truth, bundle_sha256=bundle_sha)


def validate_result(result: LabResult, bundle: LabBundle) -> None:
    s = bundle.scenario
    if result.metadata.format != "CIVPROP_METHOD_LAB_RESULT_V1":
        raise ValueError("unexpected result format")
    if result.metadata.input_bundle_sha256 != bundle.bundle_sha256:
        raise ValueError("result/input mismatch")
    if (result.metadata.start_year, result.metadata.end_year) != (s.start_year, s.end_year):
        raise ValueError("result horizon mismatch")

    actor_ids = {x.actor_id for x in s.actors}
    locations = {x.location_id: x for x in s.locations}
    location_ids = set(locations)
    projects = {x.project_archetype_id: x for x in s.project_archetypes}

    state_keys = [(x.year, x.location_id) for x in result.annual_states]
    if len(state_keys) != len(set(state_keys)):
        raise ValueError("duplicate annual location state")
    for state in result.annual_states:
        if state.location_id not in location_ids or not s.start_year <= state.year <= s.end_year:
            raise ValueError("invalid annual state reference")
        if min(state.biological_population, state.transient_population, state.workforce, state.capital) < 0:
            raise ValueError("negative annual state")
        _nonnegative_capacity(state.capacities)

    _unique(result.facilities, lambda x: x.facility_id, "facility id")
    for facility in result.facilities:
        if facility.project_archetype_id not in projects:
            raise ValueError("facility unknown project archetype")
        if facility.location_id not in location_ids or facility.owner_actor_id not in actor_ids:
            raise ValueError("facility unknown reference")
        if facility.capital < 0:
            raise ValueError("negative facility capital")
        _nonnegative_capacity(facility.capacities)
        archetype = projects[facility.project_archetype_id]
        if locations[facility.location_id].placement not in archetype.allowed_placements:
            raise ValueError("facility placement incompatible with project archetype")
        lag = archetype.construction_lag_years
        if facility.committed_year < s.start_year or facility.commissioned_year > s.end_year:
            raise ValueError("facility timing outside horizon")
        if facility.commissioned_year < facility.committed_year + lag:
            raise ValueError("facility commissioned before required construction lag")

    _unique(result.decisions, lambda x: x.decision_id, "decision id")
    for decision in result.decisions:
        if decision.actor_id not in actor_ids:
            raise ValueError("decision unknown actor")
        if decision.target_location_id is not None and decision.target_location_id not in location_ids:
            raise ValueError("decision unknown location")
        if decision.project_archetype_id is not None and decision.project_archetype_id not in projects:
            raise ValueError("decision unknown project")
        if not s.start_year <= decision.year <= s.end_year:
            raise ValueError("decision outside horizon")

    _unique(result.events, lambda x: x.event_id, "event id")
    event_ids = {x.event_id for x in result.events}
    for event in result.events:
        if event.actor_id is not None and event.actor_id not in actor_ids:
            raise ValueError("event unknown actor")
        if event.location_id is not None and event.location_id not in location_ids:
            raise ValueError("event unknown location")
        if event.event_id in event.parent_event_ids or not set(event.parent_event_ids) <= event_ids:
            raise ValueError("event parent invalid")
        if not s.start_year <= event.year <= s.end_year:
            raise ValueError("event outside horizon")

    _unique(result.flows, lambda x: x.flow_id, "flow id")
    for flow in result.flows:
        if flow.amount < 0:
            raise ValueError("negative flow")
        for ref in (flow.origin_location_id, flow.destination_location_id):
            if ref is not None and ref not in location_ids:
                raise ValueError("flow unknown location")
        if flow.actor_id is not None and flow.actor_id not in actor_ids:
            raise ValueError("flow unknown actor")
        if not s.start_year <= flow.year <= s.end_year:
            raise ValueError("flow outside horizon")
