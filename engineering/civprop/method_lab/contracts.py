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
from engineering.civprop.contracts.mission_knowledge_v1 import (
    KnowledgeStateV1,
    MissionDecisionRecordV1,
    MissionKnowledgePackage,
    MissionRecordV1,
    ObservationRecordV1,
    load_mission_knowledge_package,
)
from engineering.civprop.contracts.pressure_observability_v1 import (
    CAUSAL_SEMANTICS,
    LEGACY_SEMANTICS,
    PressureContributionV1,
    PressureObservabilityPackage,
    PressureObservabilityRuntime,
    PressureQualificationV1,
    PressureStateV1,
    load_pressure_observability_package,
)
from engineering.civprop.contracts.resource_mass_balance_v1 import (
    ResourceFlowV1,
    ResourceMassBalancePackage,
    ResourceMassBalanceRuntime,
    ResourcePhysicalRealizationPackage,
    ResourceStateV1,
    load_resource_mass_balance_package,
    load_resource_physical_realization,
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
    mission_knowledge_v1: Optional[MissionKnowledgePackage] = None
    pressure_observability_v1: Optional[PressureObservabilityPackage] = None
    resource_mass_balance_v1: Optional[ResourceMassBalancePackage] = None


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
    resource_physical_realization_v1: Optional[
        ResourcePhysicalRealizationPackage
    ] = None


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
    missions: tuple[MissionRecordV1, ...] = ()
    observations: tuple[ObservationRecordV1, ...] = ()
    knowledge_states: tuple[KnowledgeStateV1, ...] = ()
    mission_decisions: tuple[MissionDecisionRecordV1, ...] = ()
    pressure_states: tuple[PressureStateV1, ...] = ()
    pressure_contributions: tuple[PressureContributionV1, ...] = ()
    pressure_qualifications: tuple[PressureQualificationV1, ...] = ()
    resource_states: tuple[ResourceStateV1, ...] = ()
    resource_flows: tuple[ResourceFlowV1, ...] = ()


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
    plain = _plain(value)
    if isinstance(value, LabResult) and not (
        value.missions
        or value.observations
        or value.knowledge_states
        or value.mission_decisions
    ):
        # Historical Method Lab result hashes remain byte-stable when the
        # Mission/Knowledge V1 lane is absent.
        for key in (
            "missions",
            "observations",
            "knowledge_states",
            "mission_decisions",
        ):
            plain.pop(key, None)
    if isinstance(value, LabResult) and not (
        value.pressure_states
        or value.pressure_contributions
        or value.pressure_qualifications
    ):
        # Historical runs without Pressure Observability V1 keep their exact
        # canonical result hash.
        for key in (
            "pressure_states",
            "pressure_contributions",
            "pressure_qualifications",
        ):
            plain.pop(key, None)
    if isinstance(value, LabResult) and not (
        value.resource_states or value.resource_flows
    ):
        # Historical runs without Resource Mass Balance V1 keep their exact
        # canonical result hash.
        plain.pop("resource_states", None)
        plain.pop("resource_flows", None)
    return json.dumps(
        plain,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


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
        mission_knowledge_v1=(
            None
            if data.get("mission_knowledge_v1") is None
            else load_mission_knowledge_package(data["mission_knowledge_v1"])
        ),
        pressure_observability_v1=(
            None
            if data.get("pressure_observability_v1") is None
            else load_pressure_observability_package(
                data["pressure_observability_v1"]
            )
        ),
        resource_mass_balance_v1=(
            None
            if data.get("resource_mass_balance_v1") is None
            else load_resource_mass_balance_package(
                data["resource_mass_balance_v1"]
            )
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
        resource_physical_realization_v1=(
            None
            if data.get("resource_physical_realization_v1") is None
            else load_resource_physical_realization(
                data["resource_physical_realization_v1"]
            )
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

    if s.mission_knowledge_v1 is not None:
        mission_package = s.mission_knowledge_v1
        if s.project_economics_v1 is not None:
            if mission_package.capital_unit != s.project_economics_v1.capital_unit:
                raise ValueError("mission/project economics capital unit mismatch")
            if any(x.project_kind == "MISSION" for x in s.project_archetypes):
                raise ValueError(
                    "production mission archetypes must not remain in project_archetypes"
                )
            economics_ids = {
                x.project_archetype_id for x in s.project_economics_v1.projects
            }
        else:
            if mission_package.capital_unit != s.units.get("capital"):
                raise ValueError("legacy mission capital unit mismatch")
            economics_ids = {x.project_archetype_id for x in s.project_archetypes}

        beliefs = {
            (x.resource_id, x.location_id): x for x in s.resource_beliefs
        }
        observation_models = {
            x.observation_model_id: x
            for x in mission_package.observation_models
        }
        mission_by_question = {}
        for mission in mission_package.missions:
            if mission.origin_location_id not in location_ids:
                raise ValueError("mission origin references unknown location")
            if mission.destination_location_id not in location_ids:
                raise ValueError("mission destination references unknown location")
            if not set(mission.required_tech) <= tech_ids:
                raise ValueError("mission requires unknown technology")
            if mission.project_economics_id not in economics_ids:
                raise ValueError("mission missing economics parameterization")
            mission_by_question.setdefault(
                mission.target_question_id,
                mission,
            )
        for decision in mission_package.decision_models:
            if decision.follow_on_project_id not in economics_ids:
                raise ValueError("mission decision references unknown follow-on economics")

        for question in mission_package.questions:
            key = (question.subject_id, question.location_id)
            if key not in beliefs:
                raise ValueError("mission knowledge question has no resource belief")
            belief = beliefs[key]
            if abs(question.prior_probability - belief.prior_probability) > 1e-12:
                raise ValueError("mission prior diverges from resource belief")
            mission = mission_by_question.get(question.question_id)
            if mission is None:
                raise ValueError("knowledge question has no mission")
            model = observation_models[mission.observation_model_id]
            if (
                abs(model.sensitivity - belief.observation_sensitivity) > 1e-12
                or abs(
                    model.false_positive_probability
                    - belief.false_positive_probability
                )
                > 1e-12
            ):
                raise ValueError(
                    "mission observation model diverges from resource belief"
                )

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

    if s.pressure_observability_v1 is None:
        if (
            result.pressure_states
            or result.pressure_contributions
            or result.pressure_qualifications
        ):
            raise ValueError(
                "pressure outputs require Pressure Observability V1"
            )
    else:
        pressure_runtime = PressureObservabilityRuntime(
            s.pressure_observability_v1
        )
        _unique(
            result.pressure_states,
            lambda x: x.pressure_state_id,
            "pressure state id",
        )
        state_by_id = {
            x.pressure_state_id: x for x in result.pressure_states
        }
        channel_by_id = (
            {}
            if s.demand_pressure_v1 is None
            else {
                x.channel_id: x
                for x in s.demand_pressure_v1.channels
            }
        )
        project_ids = {
            x.project_archetype_id for x in s.project_archetypes
        }

        for state in result.pressure_states:
            pressure_runtime.validate_state(state)
            if not s.start_year <= state.year <= s.end_year:
                raise ValueError("pressure state outside horizon")
            if state.location_id not in location_ids:
                raise ValueError("pressure state unknown location")
            if state.semantics == CAUSAL_SEMANTICS:
                if state.channel_id not in channel_by_id:
                    raise ValueError("pressure state unknown demand channel")
                if state.unit != channel_by_id[state.channel_id].unit:
                    raise ValueError("pressure state channel unit mismatch")
            elif state.semantics == LEGACY_SEMANTICS:
                if state.project_archetype_id not in project_ids:
                    raise ValueError("legacy pressure state unknown project")
            else:
                raise ValueError("unknown pressure-state semantics")

        _unique(
            result.pressure_contributions,
            lambda x: x.contribution_id,
            "pressure contribution id",
        )
        for contribution in result.pressure_contributions:
            if contribution.pressure_state_id not in state_by_id:
                raise ValueError(
                    "pressure contribution references unknown state"
                )
            state = state_by_id[contribution.pressure_state_id]
            if (
                contribution.year != state.year
                or contribution.location_id != state.location_id
                or contribution.semantics != state.semantics
            ):
                raise ValueError("pressure contribution/state scope mismatch")
            if contribution.sign not in {-1, 1}:
                raise ValueError("invalid pressure contribution sign")
            if contribution.quantity < 0:
                raise ValueError("negative pressure contribution quantity")
            if state.semantics == CAUSAL_SEMANTICS:
                if contribution.channel_id != state.channel_id:
                    raise ValueError(
                        "causal pressure contribution channel mismatch"
                    )
                if contribution.unit != state.unit:
                    raise ValueError(
                        "causal pressure contribution unit mismatch"
                    )
            else:
                if (
                    contribution.project_archetype_id
                    != state.project_archetype_id
                ):
                    raise ValueError(
                        "legacy pressure contribution project mismatch"
                    )

        _unique(
            result.pressure_qualifications,
            lambda x: x.qualification_id,
            "pressure qualification id",
        )
        decision_by_id = {
            x.decision_id: x for x in result.decisions
        }
        selected_by_decision = {}
        for qualification in result.pressure_qualifications:
            if qualification.actor_id not in actor_ids:
                raise ValueError("pressure qualification unknown actor")
            if qualification.location_id not in location_ids:
                raise ValueError(
                    "pressure qualification unknown location"
                )
            if qualification.project_archetype_id not in project_ids:
                raise ValueError(
                    "pressure qualification unknown project"
                )
            if not s.start_year <= qualification.year <= s.end_year:
                raise ValueError(
                    "pressure qualification outside horizon"
                )
            ratios = [
                x.ratio for x in qualification.channel_ratios
            ]
            if ratios:
                expected = max(ratios)
                if abs(
                    qualification.controlling_ratio - expected
                ) > 1e-12:
                    raise ValueError(
                        "pressure controlling ratio mismatch"
                    )
                controls = [
                    x
                    for x in qualification.channel_ratios
                    if abs(x.ratio - expected) <= 1e-12
                ]
                if qualification.controlling_channel_id not in {
                    x.channel_id for x in controls
                }:
                    raise ValueError(
                        "pressure controlling channel mismatch"
                    )
            elif qualification.semantics == CAUSAL_SEMANTICS:
                if qualification.controlling_channel_id is not None:
                    raise ValueError(
                        "empty causal ratio set has controlling channel"
                    )

            for ratio in qualification.channel_ratios:
                if ratio.pressure_state_id is None:
                    continue
                if ratio.pressure_state_id not in state_by_id:
                    raise ValueError(
                        "qualification references unknown pressure state"
                    )
                state = state_by_id[ratio.pressure_state_id]
                if (
                    state.year != qualification.year
                    or state.location_id
                    != qualification.location_id
                    or state.channel_id != ratio.channel_id
                ):
                    raise ValueError(
                        "qualification pressure-state scope mismatch"
                    )
                if ratio.unit != state.unit:
                    raise ValueError(
                        "qualification pressure-state unit mismatch"
                    )
                if abs(
                    ratio.pressure
                    - state.prequalification_pressure
                ) > 1e-12:
                    raise ValueError(
                        "qualification pressure value mismatch"
                    )

            expected_qualified = (
                qualification.controlling_ratio
                >= qualification.threshold
            )
            if qualification.pressure_qualified != expected_qualified:
                raise ValueError(
                    "pressure qualification threshold mismatch"
                )
            if qualification.selected:
                if not qualification.pressure_qualified:
                    raise ValueError(
                        "selected qualification is below threshold"
                    )
                if qualification.decision_id not in decision_by_id:
                    raise ValueError(
                        "selected qualification missing decision"
                    )
                decision = decision_by_id[
                    qualification.decision_id
                ]
                if (
                    decision.action != "COMMIT_PROJECT"
                    or decision.status != "COMMITTED"
                    or decision.year != qualification.year
                    or decision.actor_id != qualification.actor_id
                    or decision.target_location_id
                    != qualification.location_id
                    or decision.project_archetype_id
                    != qualification.project_archetype_id
                ):
                    raise ValueError(
                        "qualification/decision provenance mismatch"
                    )
                if decision.decision_id in selected_by_decision:
                    raise ValueError(
                        "decision has duplicate pressure provenance"
                    )
                selected_by_decision[decision.decision_id] = (
                    qualification.qualification_id
                )
            elif qualification.decision_id is not None:
                raise ValueError(
                    "unselected qualification cannot link decision"
                )

        for decision in result.decisions:
            if (
                decision.action == "COMMIT_PROJECT"
                and decision.status == "COMMITTED"
                and decision.decision_id not in selected_by_decision
            ):
                raise ValueError(
                    "committed project lacks pressure qualification trace"
                )

    if s.mission_knowledge_v1 is None:
        if (
            result.missions
            or result.observations
            or result.knowledge_states
            or result.mission_decisions
        ):
            raise ValueError("mission outputs require Mission/Knowledge V1")
        return

    package = s.mission_knowledge_v1
    mission_archetypes = {
        x.mission_archetype_id: x for x in package.missions
    }
    question_ids = {x.question_id for x in package.questions}

    _unique(result.missions, lambda x: x.mission_id, "mission id")
    mission_by_id = {x.mission_id: x for x in result.missions}
    for mission in result.missions:
        if mission.mission_archetype_id not in mission_archetypes:
            raise ValueError("mission unknown archetype")
        if mission.actor_id not in actor_ids:
            raise ValueError("mission unknown actor")
        if mission.question_id not in question_ids:
            raise ValueError("mission unknown question")
        if mission.origin_location_id not in location_ids:
            raise ValueError("mission unknown origin")
        if mission.destination_location_id not in location_ids:
            raise ValueError("mission unknown destination")
        if not s.start_year <= mission.committed_year <= s.end_year:
            raise ValueError("mission commitment outside horizon")
        if not mission.committed_year <= mission.execution_year <= s.end_year:
            raise ValueError("mission execution outside horizon")
        if mission.capital_cost < 0:
            raise ValueError("negative mission cost")
        if mission.capital_unit != package.capital_unit:
            raise ValueError("mission capital unit mismatch")
        if mission.status not in {"COMMITTED", "EXECUTED"}:
            raise ValueError("invalid mission status")

    _unique(result.observations, lambda x: x.observation_id, "observation id")
    observation_ids = {x.observation_id for x in result.observations}
    for observation in result.observations:
        if observation.mission_id not in mission_by_id:
            raise ValueError("observation references unknown mission")
        mission = mission_by_id[observation.mission_id]
        if mission.status != "EXECUTED":
            raise ValueError("observation requires executed mission")
        if observation.actor_id != mission.actor_id:
            raise ValueError("observation actor mismatch")
        if observation.question_id != mission.question_id:
            raise ValueError("observation question mismatch")
        if observation.location_id != mission.destination_location_id:
            raise ValueError("observation location mismatch")
        if observation.year != mission.execution_year:
            raise ValueError("observation timing mismatch")
        if observation.authority_class != "SIMULATED_OBSERVATION":
            raise ValueError("invalid observation authority")

    knowledge_keys = [
        (
            x.actor_id,
            x.question_id,
            x.year,
            x.source_id,
        )
        for x in result.knowledge_states
    ]
    if len(knowledge_keys) != len(set(knowledge_keys)):
        raise ValueError("duplicate knowledge state")
    for knowledge in result.knowledge_states:
        if knowledge.actor_id not in actor_ids:
            raise ValueError("knowledge unknown actor")
        if knowledge.question_id not in question_ids:
            raise ValueError("knowledge unknown question")
        if knowledge.location_id not in location_ids:
            raise ValueError("knowledge unknown location")
        if not s.start_year <= knowledge.year <= s.end_year:
            raise ValueError("knowledge outside horizon")
        if not 0 < knowledge.probability < 1:
            raise ValueError("invalid knowledge probability")
        if not set(knowledge.observation_ids) <= observation_ids:
            raise ValueError("knowledge references unknown observation")
        if knowledge.authority_class != "SIMULATED_BELIEF":
            raise ValueError("invalid knowledge authority")

    _unique(
        result.mission_decisions,
        lambda x: x.decision_id,
        "mission decision id",
    )
    for decision in result.mission_decisions:
        if decision.actor_id not in actor_ids:
            raise ValueError("mission decision unknown actor")
        if decision.mission_archetype_id not in mission_archetypes:
            raise ValueError("mission decision unknown archetype")
        if decision.question_id not in question_ids:
            raise ValueError("mission decision unknown question")
        if decision.target_location_id not in location_ids:
            raise ValueError("mission decision unknown target")
        if not s.start_year <= decision.year <= s.end_year:
            raise ValueError("mission decision outside horizon")
        if decision.action not in {"WAIT", "COMMIT_MISSION", "CONTINUE", "REJECT"}:
            raise ValueError("invalid mission decision action")
        if decision.value_unit != package.capital_unit:
            raise ValueError("mission decision value unit mismatch")
