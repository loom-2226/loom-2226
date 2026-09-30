"""Candidate B: aggregate development-pressure reservoirs with stock/flow thresholds."""
from __future__ import annotations

from collections import defaultdict

from .common import (
    Recorder,
    actor_budget,
    actor_inflow,
    already_pending,
    base_utility,
    commission_due,
    finalize,
    initial_state,
    migration_step,
    opportunities,
    schedule,
    snapshot,
)


class SystemDynamicsEngine:
    engine_id = "SYSTEM_DYNAMICS_HEAVY"
    engine_version = "prototype-v1"

    def run(self, bundle, seed):
        states = initial_state(bundle)
        budgets = actor_budget(bundle)
        pending = []
        recorder = Recorder()
        annual_states = []
        pressure = defaultdict(float)
        recorder.event(bundle.scenario.start_year, "RUN_STARTED")

        actor_order = tuple(sorted(budgets))
        for year in range(bundle.scenario.start_year, bundle.scenario.end_year + 1):
            if year > bundle.scenario.start_year:
                for actor_id in actor_order:
                    budgets[actor_id] += actor_inflow(bundle, actor_id)

            commission_due(year, pending, states, recorder)

            pooled = {}
            for actor_id in actor_order:
                for opportunity in opportunities(bundle, states, actor_id, year):
                    key = (opportunity.location_id, opportunity.project.project_archetype_id)
                    score = max(0.0, base_utility(opportunity) + 6.0)
                    if key not in pooled or score > pooled[key][1]:
                        pooled[key] = (opportunity, score)

            for key in sorted(pooled):
                opportunity, score = pooled[key]
                pressure[key] += score * 0.22

            committed_any = {actor_id: False for actor_id in actor_order}
            ranked = sorted(
                (
                    (pressure[key] / max(1.0, opportunity.project.capital_cost), key, opportunity)
                    for key, (opportunity, _) in pooled.items()
                    if not already_pending(pending, key[0], key[1])
                ),
                reverse=True,
            )
            for ratio, key, opportunity in ranked:
                if ratio < 0.55:
                    continue
                eligible = [
                    actor_id
                    for actor_id in actor_order
                    if budgets[actor_id] + 1e-9 >= opportunity.project.capital_cost
                    and not committed_any[actor_id]
                    and any(
                        o.location_id == opportunity.location_id
                        and o.project.project_archetype_id == opportunity.project.project_archetype_id
                        for o in opportunities(bundle, states, actor_id, year)
                    )
                ]
                if not eligible:
                    continue
                actor_id = max(eligible, key=lambda a: budgets[a])
                actual = next(
                    o for o in opportunities(bundle, states, actor_id, year)
                    if o.location_id == opportunity.location_id
                    and o.project.project_archetype_id == opportunity.project.project_archetype_id
                )
                budgets[actor_id] -= actual.project.capital_cost
                schedule(pending, recorder, self.engine_id, actor_id, actual, year)
                recorder.decision(
                    year,
                    actor_id,
                    "COMMIT_PROJECT",
                    "COMMITTED",
                    actual.location_id,
                    actual.project.project_archetype_id,
                    rationale=("AGGREGATE_PRESSURE_THRESHOLD",),
                )
                committed_any[actor_id] = True
                pressure[key] = max(0.0, pressure[key] - actual.project.capital_cost)

            for actor_id in actor_order:
                if not committed_any[actor_id]:
                    recorder.decision(
                        year,
                        actor_id,
                        "WAIT",
                        "DECLINED",
                        rationale=("PRESSURE_BELOW_THRESHOLD",),
                    )

            migration_step(bundle, states, year, recorder, adjustment=0.22)
            annual_states.extend(snapshot(year, states))

        recorder.event(bundle.scenario.end_year, "RUN_COMPLETED")
        return finalize(
            bundle,
            self.engine_id,
            self.engine_version,
            seed,
            annual_states,
            recorder,
        )
