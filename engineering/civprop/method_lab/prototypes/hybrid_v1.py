"""Selected CIVPROP Engine V1 method: dynamic recursion + pressures + actor events.

This is the executable Method Lab reference for the selected architecture, not yet
the production 2026-2226 engine. It deliberately combines:

1. an annual dynamic-recursive state skeleton;
2. decaying system-pressure reservoirs that qualify opportunities;
3. bounded actor decisions that turn qualified opportunities into discrete projects.
"""
from __future__ import annotations

from collections import defaultdict

from engineering.civprop.contracts.demand_pressure_v1 import DemandPressureRuntime
from ..mission_lane_v1 import MissionLaneV1
from ..pressure_lane_v1 import PressureLaneV1
from ..resource_lane_v1 import ResourceLaneV1
from ..production_lane_v1 import ProductionLaneV1
from ..power_lane_v1 import PowerLaneV1
from ..traffic_lane_v1 import TrafficLaneV1
from ..demographic_lane_v1 import DemographicRuntimeV1

from .common import (
    Recorder,
    actor_budget,
    already_pending,
    apply_actor_budget_events,
    base_utility,
    budget_can_afford,
    budget_debit,
    budget_rationale,
    commission_due,
    finalize,
    initial_state,
    migration_step,
    opportunities,
    opportunity_context,
    pending_input_requirements,
    schedule,
    snapshot,
    stable_unit,
)


class HybridEngineV1:
    engine_id = "HYBRID_V1"
    engine_version = "method-reference-v1"

    # Pressure must retain history without becoming an immortal bucket.
    pressure_decay = 0.60
    pressure_gain = 0.24
    qualification_ratio = 0.55
    pressure_discharge = 0.85

    def _actor_weight(self, actor_type, opportunity):
        c = opportunity.project.output_capacities
        if actor_type in {"PUBLIC_FINANCER", "STATE"}:
            return (
                0.08 * c.habitat
                + 0.18 * c.power
                + 0.12 * c.transport
                + 0.08 * c.resource
            )
        return (
            0.22 * c.industrial
            + 0.18 * c.transport
            + 0.12 * c.resource
            + 0.04 * c.power
        )

    def _project_pressure_ratio(self, scenario, pressure, opportunity):
        ratios = []
        for channel in scenario.demand_pressure_v1.channels:
            output = float(
                getattr(opportunity.project.output_capacities, channel.available_field)
            )
            if output <= 0:
                continue
            value = pressure.get(
                (opportunity.location_id, channel.channel_id),
                0.0,
            )
            ratios.append(value / output)
        return max(ratios) if ratios else 0.0

    def run(self, bundle, seed, *, trace_decisions=False):
        causal_demand = bundle.scenario.demand_pressure_v1 is not None
        production_economics = bundle.scenario.project_economics_v1 is not None
        mission_knowledge = bundle.scenario.mission_knowledge_v1 is not None
        pressure_observability = (
            bundle.scenario.pressure_observability_v1 is not None
        )
        resource_mass_balance = (
            bundle.scenario.resource_mass_balance_v1 is not None
        )
        production_accounting = (
            bundle.scenario.production_accounting_v1 is not None
        )
        power_balance = bundle.scenario.power_balance_v1 is not None
        traffic_fleet = bundle.scenario.traffic_fleet_v1 is not None
        demographic_authority = bundle.scenario.demographic_authority_v1 is not None
        if traffic_fleet:
            self.engine_version = "method-reference-v9"
        elif power_balance:
            self.engine_version = "method-reference-v8"
        elif production_accounting:
            self.engine_version = "method-reference-v7"
        elif resource_mass_balance:
            self.engine_version = "method-reference-v6"
        elif pressure_observability:
            self.engine_version = "method-reference-v5"
        elif mission_knowledge:
            self.engine_version = "method-reference-v4"
        elif production_economics:
            self.engine_version = "method-reference-v3"
        elif causal_demand:
            self.engine_version = "method-reference-v2"
        else:
            self.engine_version = "method-reference-v1"
        demand_runtime = (
            DemandPressureRuntime(bundle.scenario.demand_pressure_v1)
            if causal_demand
            else None
        )

        states = initial_state(bundle)
        budgets = actor_budget(bundle)
        actor_types = {x.actor_id: x.actor_type for x in bundle.scenario.actors}
        actor_ids = tuple(sorted(budgets))
        pending = []
        pressure = defaultdict(float)
        recorder = Recorder()
        mission_lane = (
            MissionLaneV1(bundle, seed, recorder)
            if mission_knowledge
            else None
        )
        pressure_lane = (
            PressureLaneV1(bundle.scenario, recorder)
            if pressure_observability
            else None
        )
        resource_lane = (
            ResourceLaneV1(bundle, recorder)
            if resource_mass_balance
            else None
        )
        power_lane = (
            PowerLaneV1(bundle, recorder)
            if power_balance
            else None
        )
        traffic_lane = (
            TrafficLaneV1(bundle, recorder)
            if traffic_fleet
            else None
        )
        production_lane = (
            ProductionLaneV1(bundle, recorder)
            if production_accounting
            else None
        )
        demographic_lane = (
            DemographicRuntimeV1(
                bundle.scenario.demographic_authority_v1,
                bundle.scenario.migration_demand_v1,
            )
            if demographic_authority else None
        )
        annual_states = []

        recorder.event(bundle.scenario.start_year, "RUN_STARTED")

        for year in range(bundle.scenario.start_year, bundle.scenario.end_year + 1):
            recorder.event(year, "YEAR_STARTED")
            trace_decision_start = len(recorder.decisions)
            trace_mission_start = len(recorder.mission_decisions)
            trace_observation_start = len(recorder.observations)

            apply_actor_budget_events(bundle, budgets, year, recorder)

            if demographic_lane is not None:
                demographic_lane.apply_earth_baseline(year=year, states=states)

            commission_due(year, pending, states, recorder)

            if mission_lane is not None:
                mission_lane.execute_due(
                    year=year,
                    recorder=recorder,
                )

            if resource_lane is not None:
                resource_lane.step(year=year)

            if power_lane is not None:
                power_lane.step(year=year, states=states)

            if traffic_lane is not None:
                traffic_lane.step(
                    year=year,
                    states=states,
                    additional_requirements=pending_input_requirements(
                        pending
                    ),
                )

            if production_lane is not None:
                production_lane.step(year=year)

            if causal_demand:
                opening_pressure = dict(pressure)
                demand_observations = demand_runtime.derive(
                    states,
                    year=year,
                    additional_requirements=pending_input_requirements(pending),
                )
                if traffic_lane is not None:
                    demand_observations = (
                        traffic_lane.apply_pressure_overrides(
                            year=year,
                            observations=demand_observations,
                        )
                    )
                pressure = demand_runtime.advance_pressure(
                    pressure,
                    demand_observations,
                )
                if pressure_lane is not None:
                    pressure_lane.causal_update(
                        year=year,
                        previous_pressure=opening_pressure,
                        observations=demand_observations,
                        resulting_pressure=pressure,
                    )
                shared_context = opportunity_context(
                    bundle, states, year, demand_observations=demand_observations
                )
                actor_opportunities = {
                    actor_id: opportunities(
                        bundle,
                        states,
                        actor_id,
                        year,
                        demand_observations=demand_observations,
                        knowledge=(
                            mission_lane.knowledge
                            if mission_lane is not None
                            else None
                        ),
                        shared_context=shared_context,
                    )
                    for actor_id in actor_ids
                }
            else:
                opening_pressure = dict(pressure)
                # Historical Method Lab semantics are retained byte-for-byte:
                # decay project pressure and replenish it from the old exogenous
                # demand/utility fixture.
                for key in tuple(pressure):
                    pressure[key] *= self.pressure_decay
                    if pressure[key] < 1e-12:
                        pressure.pop(key, None)

                shared_context = opportunity_context(bundle, states, year)
                actor_opportunities = {
                    actor_id: opportunities(
                        bundle,
                        states,
                        actor_id,
                        year,
                        knowledge=(
                            mission_lane.knowledge
                            if mission_lane is not None
                            else None
                        ),
                        shared_context=shared_context,
                    )
                    for actor_id in actor_ids
                }
                structural = {}
                for actor_id, rows in actor_opportunities.items():
                    for opportunity in rows:
                        key = (
                            opportunity.location_id,
                            opportunity.project.project_archetype_id,
                        )
                        signal = max(0.0, base_utility(opportunity) + 5.0)
                        if key not in structural or signal > structural[key]:
                            structural[key] = signal

                for key, signal in structural.items():
                    pressure[key] += signal * self.pressure_gain
                if pressure_lane is not None:
                    pressure_lane.legacy_update(
                        year=year,
                        opening_pressure=opening_pressure,
                        structural_signals=structural,
                        resulting_pressure=pressure,
                        decay=self.pressure_decay,
                        gain=self.pressure_gain,
                    )

            if mission_lane is not None:
                mission_lane.evaluate_and_commit(
                    year=year,
                    budgets=budgets,
                    recorder=recorder,
                )

            committed_keys = set()
            for actor_id in actor_ids:
                choices = []
                for opportunity in actor_opportunities[actor_id]:
                    key = (
                        opportunity.location_id,
                        opportunity.project.project_archetype_id,
                    )
                    if key in committed_keys:
                        continue
                    if already_pending(pending, *key):
                        continue

                    audit_qualification = None
                    if pressure_lane is not None:
                        audit_qualification = (
                            pressure_lane.causal_qualification(
                                year=year,
                                actor_id=actor_id,
                                opportunity=opportunity,
                                threshold=self.qualification_ratio,
                            )
                            if causal_demand
                            else pressure_lane.legacy_qualification(
                                year=year,
                                actor_id=actor_id,
                                opportunity=opportunity,
                                threshold=self.qualification_ratio,
                            )
                        )

                    if not budget_can_afford(
                        bundle, budgets[actor_id], opportunity.project.capital_cost
                    ):
                        continue

                    ratio = (
                        self._project_pressure_ratio(
                            bundle.scenario,
                            pressure,
                            opportunity,
                        )
                        if causal_demand
                        else pressure[key] / opportunity.project.capital_cost
                    )
                    if (
                        audit_qualification is not None
                        and abs(
                            audit_qualification.controlling_ratio - ratio
                        )
                        > 1e-12
                    ):
                        raise ValueError(
                            "pressure qualification ledger diverges from engine ratio"
                        )
                    if ratio < self.qualification_ratio:
                        continue

                    recorder.event(
                        year,
                        "OPPORTUNITY_PRESSURE_QUALIFIED",
                        actor_id,
                        opportunity.location_id,
                    )
                    jitter = 1.5 * stable_unit(
                        seed,
                        self.engine_id,
                        actor_id,
                        year,
                        opportunity.location_id,
                        opportunity.project.project_archetype_id,
                    )
                    score = (
                        base_utility(opportunity)
                        + self._actor_weight(actor_types[actor_id], opportunity)
                        + 2.0 * ratio
                        + jitter
                    )
                    choices.append((score, opportunity, key))

                if not choices:
                    recorder.decision(
                        year,
                        actor_id,
                        "WAIT",
                        "DECLINED",
                        rationale=(
                            "NO_PRESSURE_QUALIFIED_OPPORTUNITY",
                            *budget_rationale(bundle, budgets[actor_id]),
                        ),
                    )
                    continue

                choices.sort(
                    key=lambda row: (
                        row[0],
                        row[1].location_id,
                        row[1].project.project_archetype_id,
                    ),
                    reverse=True,
                )
                _, choice, key = choices[0]
                budgets[actor_id] = budget_debit(
                    bundle, budgets[actor_id], choice.project.capital_cost
                )
                schedule(
                    pending, recorder, self.engine_id, actor_id, choice, year
                )
                decision_id = recorder.decision(
                    year,
                    actor_id,
                    "COMMIT_PROJECT",
                    "COMMITTED",
                    choice.location_id,
                    choice.project.project_archetype_id,
                    rationale=("PRESSURE_QUALIFIED", "ACTOR_SELECTED"),
                )
                if pressure_lane is not None:
                    pressure_lane.link_selected_decision(
                        year=year,
                        actor_id=actor_id,
                        location_id=choice.location_id,
                        project_archetype_id=choice.project.project_archetype_id,
                        decision_id=decision_id,
                    )
                committed_keys.add(key)

                if not causal_demand:
                    pressure[key] = max(
                        0.0,
                        pressure[key]
                        - choice.project.capital_cost * self.pressure_discharge,
                    )

            if pressure_lane is not None and not causal_demand:
                pressure_lane.close_legacy_year(
                    resulting_pressure=pressure,
                )

            if trace_decisions:
                # Presentation-only trace. Read recorder state after all decisions;
                # never feeds back into simulation state, ordering, or scoring.
                for row in recorder.mission_decisions[trace_mission_start:]:
                    if row.action != "WAIT":
                        print(
                            f"{year}  {row.actor_id:<20} {row.action:<15} "
                            f"{row.mission_archetype_id} @ {row.target_location_id} "
                            f"voi={row.expected_value_of_information}",
                            flush=True,
                        )
                for row in recorder.decisions[trace_decision_start:]:
                    if row.action != "WAIT":
                        print(
                            f"{year}  {row.actor_id:<20} {row.action:<15} "
                            f"{row.project_archetype_id} @ {row.target_location_id}",
                            flush=True,
                        )
                for row in recorder.observations[trace_observation_start:]:
                    if hasattr(row, "detected"):
                        detail = f"detected={row.detected}"
                    else:
                        detail = (
                            f"status={row.characterization_status} "
                            f"resource_result={row.resource_result_status}"
                        )
                    print(
                        f"{year}  {row.actor_id:<20} OBSERVE         "
                        f"{row.subject_id} @ {row.location_id} {detail}",
                        flush=True,
                    )
                if (year - bundle.scenario.start_year) % 10 == 0:
                    active = sum(1 for rows in actor_opportunities.values() if rows)
                    candidates = sum(len(rows) for rows in actor_opportunities.values())
                    year_qualifications = [
                        q for q in recorder.pressure_qualifications if q.year == year
                    ]
                    pressure_pass = sum(q.pressure_qualified for q in year_qualifications)
                    selected = sum(q.selected for q in year_qualifications)
                    pressure_wait = len(year_qualifications) - pressure_pass
                    # Opportunities absent from the qualification ledger were rejected
                    # earlier (for example budget/pending/duplicate guards). Keep that
                    # bucket descriptive rather than inventing a more specific cause.
                    prequalification_reject = max(
                        0, candidates - len(year_qualifications)
                    )
                    print(
                        f"{year}  YEAR  candidates={candidates} actors_with_options={active} "
                        f"qualified={pressure_pass} pressure_wait={pressure_wait} "
                        f"prequal_reject={prequalification_reject} selected={selected} "
                        f"facilities={len(recorder.facilities)} missions={len(recorder.missions)}",
                        flush=True,
                    )

            if demographic_lane is not None:
                demographic_lane.migrate(
                    year=year,
                    states=states,
                    route_traffic_states=recorder.route_traffic_states,
                    recorder=recorder,
                )
            else:
                migration_step(bundle, states, year, recorder, adjustment=0.30)
            annual_states.extend(snapshot(year, states))
            recorder.event(year, "YEAR_COMPLETED")

        recorder.event(bundle.scenario.end_year, "RUN_COMPLETED")
        return finalize(
            bundle,
            self.engine_id,
            self.engine_version,
            seed,
            annual_states,
            recorder,
        )
