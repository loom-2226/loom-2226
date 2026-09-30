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

    def run(self, bundle, seed):
        causal_demand = bundle.scenario.demand_pressure_v1 is not None
        production_economics = bundle.scenario.project_economics_v1 is not None
        mission_knowledge = bundle.scenario.mission_knowledge_v1 is not None
        pressure_observability = (
            bundle.scenario.pressure_observability_v1 is not None
        )
        if pressure_observability:
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
        annual_states = []

        recorder.event(bundle.scenario.start_year, "RUN_STARTED")

        for year in range(bundle.scenario.start_year, bundle.scenario.end_year + 1):
            recorder.event(year, "YEAR_STARTED")

            apply_actor_budget_events(bundle, budgets, year, recorder)

            commission_due(year, pending, states, recorder)

            if mission_lane is not None:
                mission_lane.execute_due(
                    year=year,
                    recorder=recorder,
                )

            if causal_demand:
                opening_pressure = dict(pressure)
                demand_observations = demand_runtime.derive(
                    states,
                    year=year,
                    additional_requirements=pending_input_requirements(pending),
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
