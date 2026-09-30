"""Shared physical/accounting helpers for Method Lab prototypes.

These helpers deliberately standardize feasibility, accounting, migration and
serialization so the prototype comparison is about orchestration/decision method,
not three incompatible definitions of physics.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from typing import Iterable, Optional

from engineering.civprop.contracts.actor_state_v1 import ActorStateRuntime

from ..contracts import (
    CapacityVector,
    DecisionRecord,
    EventRecord,
    FacilityRecord,
    FlowRecord,
    LabBundle,
    LabResult,
    LocationState,
    ProjectArchetype,
    RunMetadata,
)


@dataclass
class MutableActorBudget:
    status: str
    amount: Optional[float]
    unit: Optional[str]
    scope: str

    def can_afford(self, cost: float, unit: str) -> bool:
        return (
            self.status == "KNOWN"
            and self.amount is not None
            and self.unit == unit
            and self.amount + 1e-9 >= cost
        )


@dataclass
class MutableLocation:
    biological_population: float
    transient_population: float
    workforce: float
    capital: float
    power: float
    resource: float
    industrial: float
    habitat: float
    shipyard: float
    transport: float

    @classmethod
    def from_input(cls, location):
        c = location.capacities
        return cls(
            biological_population=location.biological_population,
            transient_population=location.transient_population,
            workforce=location.workforce,
            capital=location.capital,
            power=c.power,
            resource=c.resource,
            industrial=c.industrial,
            habitat=c.habitat,
            shipyard=c.shipyard,
            transport=c.transport,
        )

    def capacities(self) -> CapacityVector:
        return CapacityVector(
            power=self.power,
            resource=self.resource,
            industrial=self.industrial,
            habitat=self.habitat,
            shipyard=self.shipyard,
            transport=self.transport,
        )

    def add_capacities(self, c: CapacityVector) -> None:
        self.power += c.power
        self.resource += c.resource
        self.industrial += c.industrial
        self.habitat += c.habitat
        self.shipyard += c.shipyard
        self.transport += c.transport


@dataclass(frozen=True)
class Opportunity:
    actor_id: str
    location_id: str
    project: ProjectArchetype
    access_cost: float
    demand: float
    resource_probability: float
    complementarity: float


@dataclass(frozen=True)
class PendingProject:
    facility_id: str
    actor_id: str
    location_id: str
    project: ProjectArchetype
    committed_year: int
    commissioned_year: int


class Recorder:
    def __init__(self):
        self.events: list[EventRecord] = []
        self.decisions: list[DecisionRecord] = []
        self.flows: list[FlowRecord] = []
        self.facilities: list[FacilityRecord] = []
        self._event_counter = 0
        self._decision_counter = 0
        self._flow_counter = 0

    def event(self, year: int, event_type: str, actor_id=None, location_id=None) -> str:
        self._event_counter += 1
        event_id = f"e{self._event_counter:05d}"
        parents = (self.events[-1].event_id,) if self.events else ()
        self.events.append(
            EventRecord(
                event_id=event_id,
                year=year,
                event_type=event_type,
                actor_id=actor_id,
                location_id=location_id,
                parent_event_ids=parents,
            )
        )
        return event_id

    def decision(
        self,
        year: int,
        actor_id: str,
        action: str,
        status: str,
        location_id=None,
        project_id=None,
        rationale=(),
    ) -> str:
        self._decision_counter += 1
        decision_id = f"d{self._decision_counter:05d}"
        self.decisions.append(
            DecisionRecord(
                decision_id=decision_id,
                year=year,
                actor_id=actor_id,
                action=action,
                target_location_id=location_id,
                project_archetype_id=project_id,
                status=status,
                rationale_codes=tuple(rationale),
            )
        )
        self.event(year, "DECISION_MADE", actor_id, location_id)
        return decision_id

    def migration(self, year: int, origin: str, destination: str, amount: float) -> None:
        if amount <= 0:
            return
        self._flow_counter += 1
        self.flows.append(
            FlowRecord(
                flow_id=f"f{self._flow_counter:05d}",
                year=year,
                flow_type="MIGRATION",
                origin_location_id=origin,
                destination_location_id=destination,
                amount=amount,
                unit="person",
            )
        )
        self.event(year, "MIGRATION_APPLIED", None, destination)


def stable_unit(seed: int, *parts: object) -> float:
    payload = "|".join([str(seed), *(str(x) for x in parts)]).encode()
    raw = hashlib.sha256(payload).digest()[:8]
    return int.from_bytes(raw, "big") / 2**64


def run_id(engine_id: str, engine_version: str, bundle_sha: str, seed: int) -> str:
    payload = f"{engine_id}|{engine_version}|{bundle_sha}|{seed}".encode()
    return hashlib.sha256(payload).hexdigest()[:24]


def initial_state(bundle: LabBundle) -> dict[str, MutableLocation]:
    return {
        x.location_id: MutableLocation.from_input(x)
        for x in bundle.scenario.locations
    }


def project_map(bundle: LabBundle):
    return {x.project_archetype_id: x for x in bundle.scenario.project_archetypes}


def actor_budget(bundle: LabBundle):
    """Return legacy numeric budgets unchanged, or ActorState budgets for V1 inputs."""
    if bundle.scenario.actor_state_v1 is not None:
        runtime = ActorStateRuntime(bundle.scenario.actor_state_v1)
        result = {}
        for actor in bundle.scenario.actors:
            view = runtime.budget(actor.actor_id, bundle.scenario.start_year)
            result[actor.actor_id] = MutableActorBudget(
                status=view.status,
                amount=view.amount,
                unit=view.unit,
                scope=view.scope,
            )
        return result
    return {x.actor_id: x.starting_capital for x in bundle.scenario.actors}


def apply_actor_budget_events(
    bundle: LabBundle,
    budgets: dict[str, MutableActorBudget],
    year: int,
    recorder: Recorder,
) -> None:
    if bundle.scenario.actor_state_v1 is None:
        if year > bundle.scenario.start_year:
            for actor in bundle.scenario.actors:
                budgets[actor.actor_id] += actor.annual_capital_inflow
        return
    for event in bundle.scenario.actor_state_v1.events:
        if event.year != year or event.event_type != "BUDGET_ALLOCATION_SET":
            continue
        payload = event.payload
        budgets[event.actor_id] = MutableActorBudget(
            status="KNOWN",
            amount=float(payload["amount"]),
            unit=str(payload["unit"]),
            scope=str(payload["scope"]),
        )


def budget_can_afford(bundle: LabBundle, budget, cost: float) -> bool:
    if isinstance(budget, MutableActorBudget):
        return budget.can_afford(cost, bundle.scenario.units["capital"])
    return budget + 1e-9 >= cost


def budget_debit(bundle: LabBundle, budget, cost: float):
    if isinstance(budget, MutableActorBudget):
        if not budget.can_afford(cost, bundle.scenario.units["capital"]):
            raise ValueError("cannot debit unknown, mismatched, or insufficient actor budget")
        budget.amount -= cost
        return budget
    if budget + 1e-9 < cost:
        raise ValueError("insufficient actor budget")
    return budget - cost


def budget_rationale(bundle: LabBundle, budget) -> tuple[str, ...]:
    if not isinstance(budget, MutableActorBudget):
        return ()
    if budget.status == "UNKNOWN":
        return ("SPENDABLE_ALLOCATION_UNKNOWN",)
    if budget.unit != bundle.scenario.units["capital"]:
        return ("BUDGET_UNIT_MISMATCH",)
    return ()


def demand_value(bundle: LabBundle, signal_id: str, year: int) -> float:
    for signal in bundle.scenario.demand_signals:
        if signal.signal_id == signal_id:
            for value in signal.values:
                if value.year == year:
                    return value.value
    return 0.0


def project_demand(bundle: LabBundle, project: ProjectArchetype, year: int) -> float:
    c = project.output_capacities
    values = []
    if c.transport > 0:
        values.append(demand_value(bundle, "OFFWORLD_TRANSPORT_DEMAND", year))
    if c.industrial > 0:
        values.append(demand_value(bundle, "OFFWORLD_INDUSTRIAL_DEMAND", year))
    if c.habitat > 0:
        values.append(demand_value(bundle, "OFFWORLD_HABITAT_INTEREST", year) / 5.0)
    if c.resource > 0:
        values.append(demand_value(bundle, "WATER_RESOURCE_DEMAND", year))
    if c.power > 0:
        values.extend(
            [
                demand_value(bundle, "OFFWORLD_TRANSPORT_DEMAND", year) * 0.25,
                demand_value(bundle, "OFFWORLD_INDUSTRIAL_DEMAND", year) * 0.5,
                demand_value(bundle, "OFFWORLD_HABITAT_INTEREST", year) / 20.0,
            ]
        )
    if project.project_kind == "MISSION":
        values.append(demand_value(bundle, "WATER_RESOURCE_DEMAND", year) + 2.0)
    return max(values) if values else 0.0


def actor_tech_status(bundle: LabBundle, actor_id: str, tech_id: str, year: int) -> str:
    frontier = next(x for x in bundle.scenario.technology_frontier if x.tech_id == tech_id)
    if year < frontier.frontier_year:
        return "UNUSABLE"
    if bundle.scenario.actor_state_v1 is not None:
        return ActorStateRuntime(bundle.scenario.actor_state_v1).capability_status(
            actor_id, tech_id, year
        )
    for cap in bundle.scenario.actor_capability:
        if cap.actor_id == actor_id and cap.tech_id == tech_id:
            if year < cap.valid_from:
                return "UNUSABLE"
            if cap.valid_to is not None and year > cap.valid_to:
                return "UNUSABLE"
            return cap.status
    return "UNKNOWN"


def required_techs(project: ProjectArchetype, location_id: str) -> tuple[str, ...]:
    techs = list(project.required_tech)
    if location_id == "LUNA_SURFACE" and "LUNAR_SURFACE_OPERATIONS" not in techs:
        techs.append("LUNAR_SURFACE_OPERATIONS")
    return tuple(techs)


def best_access_cost(
    bundle: LabBundle,
    states: dict[str, MutableLocation],
    destination: str,
    year: int,
) -> Optional[float]:
    if destination == "EARTH_SURFACE":
        return 0.0
    candidates = []
    for profile in bundle.scenario.accessibility:
        if profile.destination_location_id != destination:
            continue
        origin = profile.origin_location_id
        if origin not in states:
            continue
        if origin != "EARTH_SURFACE" and states[origin].transport <= 0:
            continue
        point = next((x for x in profile.years if x.year == year), None)
        if point is not None and point.status == "FEASIBLE" and point.generalized_cost is not None:
            candidates.append(point.generalized_cost)
    return min(candidates) if candidates else None


def resource_probability(bundle: LabBundle, location_id: str) -> float:
    probs = [
        x.prior_probability
        for x in bundle.scenario.resource_beliefs
        if x.location_id == location_id
    ]
    return max(probs) if probs else 0.0


def transport_support(access_cost: Optional[float]) -> float:
    if access_cost is None:
        return 0.0
    return max(0.0, 15.0 - access_cost)


def local_minimums_met(
    state: MutableLocation,
    project: ProjectArchetype,
    access_cost: Optional[float],
) -> bool:
    need = project.minimum_input_capacities
    if state.power + 1e-9 < need.power:
        return False
    if state.resource + 1e-9 < need.resource:
        return False
    if state.industrial + 1e-9 < need.industrial:
        return False
    if state.habitat + 1e-9 < need.habitat:
        return False
    if state.shipyard + 1e-9 < need.shipyard:
        return False
    if transport_support(access_cost) + state.transport + 1e-9 < need.transport:
        return False
    return True


def complementarity(
    state: MutableLocation,
    project: ProjectArchetype,
    demand: float,
) -> float:
    c = project.output_capacities
    score = 0.0
    if c.power:
        score += 0.08 * (state.industrial + state.resource + state.habitat / 20.0)
        score -= 0.10 * max(0.0, state.power - 2.0 * demand)
    if c.transport:
        score += 0.05 * (state.capital + state.industrial * 2.0)
        score -= 0.35 * max(0.0, state.transport - demand)
    if c.habitat:
        score += 0.12 * (state.power + state.industrial + state.resource)
        score -= 0.05 * max(0.0, state.habitat - 5.0 * demand)
    if c.industrial:
        score += 0.12 * state.power + 0.08 * state.transport + 0.04 * state.resource
        score -= 0.45 * max(0.0, state.industrial - demand)
    if c.resource:
        score += 0.15 * state.power + 0.08 * state.transport
        score -= 0.50 * max(0.0, state.resource - demand)
    return score


def opportunities(
    bundle: LabBundle,
    states: dict[str, MutableLocation],
    actor_id: str,
    year: int,
    *,
    include_missions: bool = False,
) -> list[Opportunity]:
    result = []
    placements = {x.location_id: x.placement for x in bundle.scenario.locations}
    for project in bundle.scenario.project_archetypes:
        if project.project_kind == "MISSION" and not include_missions:
            continue
        for location_id, state in states.items():
            if location_id == "EARTH_SURFACE":
                continue
            if placements[location_id] not in project.allowed_placements:
                continue
            techs = required_techs(project, location_id)
            if any(actor_tech_status(bundle, actor_id, tech, year) != "USABLE" for tech in techs):
                continue
            access_cost = best_access_cost(bundle, states, location_id, year)
            if access_cost is None:
                continue
            if not local_minimums_met(state, project, access_cost):
                continue
            probability = resource_probability(bundle, location_id)
            if project.output_capacities.resource > 0 and probability <= 0:
                continue
            demand = project_demand(bundle, project, year)
            result.append(
                Opportunity(
                    actor_id=actor_id,
                    location_id=location_id,
                    project=project,
                    access_cost=access_cost,
                    demand=demand,
                    resource_probability=probability,
                    complementarity=complementarity(state, project, demand),
                )
            )
    return result


def base_utility(opportunity: Opportunity) -> float:
    project = opportunity.project
    resource_term = (
        14.0 * opportunity.resource_probability
        if project.output_capacities.resource > 0
        else 0.0
    )
    return (
        1.20 * opportunity.demand
        + opportunity.complementarity
        + resource_term
        - 0.45 * opportunity.access_cost
        - 0.35 * project.capital_cost
    )


def softmax_pick(
    choices: list[tuple[Opportunity, float]],
    seed: int,
    *key: object,
    temperature: float = 3.0,
) -> Optional[Opportunity]:
    if not choices:
        return None
    maximum = max(score for _, score in choices)
    weights = [math.exp((score - maximum) / temperature) for _, score in choices]
    total = sum(weights)
    draw = stable_unit(seed, *key) * total
    cumulative = 0.0
    for (choice, _), weight in zip(choices, weights):
        cumulative += weight
        if draw <= cumulative:
            return choice
    return choices[-1][0]


def pending_id(engine_id: str, actor_id: str, location_id: str, project_id: str, year: int, n: int) -> str:
    raw = f"{engine_id}|{actor_id}|{location_id}|{project_id}|{year}|{n}".encode()
    return "fac-" + hashlib.sha256(raw).hexdigest()[:14]


def commission_due(
    year: int,
    pending: list[PendingProject],
    states: dict[str, MutableLocation],
    recorder: Recorder,
) -> None:
    remaining = []
    for item in pending:
        if item.commissioned_year != year:
            remaining.append(item)
            continue
        state = states[item.location_id]
        state.capital += item.project.capital_cost
        state.add_capacities(item.project.output_capacities)
        recorder.facilities.append(
            FacilityRecord(
                facility_id=item.facility_id,
                project_archetype_id=item.project.project_archetype_id,
                location_id=item.location_id,
                owner_actor_id=item.actor_id,
                committed_year=item.committed_year,
                commissioned_year=item.commissioned_year,
                status="ACTIVE",
                capital=item.project.capital_cost,
                capacities=item.project.output_capacities,
            )
        )
        recorder.event(year, "FACILITY_COMMISSIONED", item.actor_id, item.location_id)
    pending[:] = remaining


def schedule(
    pending: list[PendingProject],
    recorder: Recorder,
    engine_id: str,
    actor_id: str,
    opportunity: Opportunity,
    year: int,
) -> PendingProject:
    item = PendingProject(
        facility_id=pending_id(
            engine_id,
            actor_id,
            opportunity.location_id,
            opportunity.project.project_archetype_id,
            year,
            len(pending) + len(recorder.facilities),
        ),
        actor_id=actor_id,
        location_id=opportunity.location_id,
        project=opportunity.project,
        committed_year=year,
        commissioned_year=year + opportunity.project.construction_lag_years,
    )
    pending.append(item)
    recorder.event(year, "PROJECT_COMMITTED", actor_id, opportunity.location_id)
    return item


def job_capacity(state: MutableLocation) -> float:
    return (
        state.transport * 1.5
        + state.industrial * 3.0
        + state.resource * 2.5
        + state.power * 0.20
        + state.shipyard * 2.0
    )


def migration_step(
    bundle: LabBundle,
    states: dict[str, MutableLocation],
    year: int,
    recorder: Recorder,
    *,
    adjustment: float,
) -> None:
    earth = states["EARTH_SURFACE"]
    interest = demand_value(bundle, "OFFWORLD_HABITAT_INTEREST", year)
    if interest <= 0 or earth.biological_population <= 0:
        return

    candidates = []
    for location_id, state in states.items():
        if location_id == "EARTH_SURFACE":
            continue
        if best_access_cost(bundle, states, location_id, year) is None:
            continue
        room = max(0.0, state.habitat - state.biological_population)
        jobs = max(0.0, job_capacity(state) - state.biological_population)
        capacity = min(room, jobs, interest)
        if capacity > 0:
            candidates.append((location_id, capacity))

    total_capacity = sum(x[1] for x in candidates)
    if total_capacity <= 0:
        return
    total_move = min(earth.biological_population, interest, total_capacity) * adjustment
    for location_id, capacity in candidates:
        amount = total_move * capacity / total_capacity
        amount = min(amount, states[location_id].habitat - states[location_id].biological_population)
        if amount <= 0:
            continue
        earth.biological_population -= amount
        states[location_id].biological_population += amount
        states[location_id].workforce = max(
            states[location_id].workforce,
            states[location_id].biological_population * 0.5,
        )
        earth.workforce = min(earth.workforce, earth.biological_population * 0.5)
        recorder.migration(year, "EARTH_SURFACE", location_id, amount)


def snapshot(year: int, states: dict[str, MutableLocation]) -> list[LocationState]:
    return [
        LocationState(
            year=year,
            location_id=location_id,
            biological_population=state.biological_population,
            transient_population=state.transient_population,
            workforce=state.workforce,
            capital=state.capital,
            capacities=state.capacities(),
        )
        for location_id, state in sorted(states.items())
    ]


def finalize(
    bundle: LabBundle,
    engine_id: str,
    engine_version: str,
    seed: int,
    annual_states: list[LocationState],
    recorder: Recorder,
) -> LabResult:
    return LabResult(
        metadata=RunMetadata(
            format="CIVPROP_METHOD_LAB_RESULT_V1",
            run_id=run_id(engine_id, engine_version, bundle.bundle_sha256, seed),
            engine_id=engine_id,
            engine_version=engine_version,
            input_bundle_sha256=bundle.bundle_sha256,
            seed=seed,
            start_year=bundle.scenario.start_year,
            end_year=bundle.scenario.end_year,
        ),
        annual_states=tuple(annual_states),
        facilities=tuple(recorder.facilities),
        decisions=tuple(recorder.decisions),
        events=tuple(recorder.events),
        flows=tuple(recorder.flows),
    )


def actor_inflow(bundle: LabBundle, actor_id: str) -> float:
    actor = next(x for x in bundle.scenario.actors if x.actor_id == actor_id)
    return 0.0 if actor.annual_capital_inflow is None else actor.annual_capital_inflow


def active_facility_count(recorder: Recorder, location_id: str, project_id: str) -> int:
    return sum(
        1
        for f in recorder.facilities
        if f.location_id == location_id and f.project_archetype_id == project_id
    )


def already_pending(pending: Iterable[PendingProject], location_id: str, project_id: str) -> bool:
    return any(
        x.location_id == location_id and x.project.project_archetype_id == project_id
        for x in pending
    )
