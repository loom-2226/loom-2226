"""Candidate A: annual dynamic-recursive stock/flow + events + discrete choice."""
from __future__ import annotations

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
    softmax_pick,
)


class DynamicRecursiveEngine:
    engine_id = "DYNAMIC_RECURSIVE"
    engine_version = "prototype-v1"

    def run(self, bundle, seed):
        states = initial_state(bundle)
        budgets = actor_budget(bundle)
        pending = []
        recorder = Recorder()
        annual_states = []
        recorder.event(bundle.scenario.start_year, "RUN_STARTED")

        for year in range(bundle.scenario.start_year, bundle.scenario.end_year + 1):
            if year > bundle.scenario.start_year:
                for actor_id in budgets:
                    budgets[actor_id] += actor_inflow(bundle, actor_id)

            commission_due(year, pending, states, recorder)

            for actor_id in sorted(budgets):
                choices = []
                for opportunity in opportunities(bundle, states, actor_id, year):
                    project_id = opportunity.project.project_archetype_id
                    if already_pending(pending, opportunity.location_id, project_id):
                        continue
                    if budgets[actor_id] + 1e-9 < opportunity.project.capital_cost:
                        continue
                    score = base_utility(opportunity)
                    if score > -3.0:
                        choices.append((opportunity, score))

                choice = softmax_pick(
                    choices,
                    seed,
                    self.engine_id,
                    actor_id,
                    year,
                    temperature=2.5,
                )
                if choice is None:
                    recorder.decision(
                        year,
                        actor_id,
                        "WAIT",
                        "DECLINED",
                        rationale=("NO_ADMITTED_OPPORTUNITY",),
                    )
                    continue

                budgets[actor_id] -= choice.project.capital_cost
                schedule(pending, recorder, self.engine_id, actor_id, choice, year)
                recorder.decision(
                    year,
                    actor_id,
                    "COMMIT_PROJECT",
                    "COMMITTED",
                    choice.location_id,
                    choice.project.project_archetype_id,
                    rationale=("SOFTMAX_DISCRETE_CHOICE",),
                )

            migration_step(bundle, states, year, recorder, adjustment=0.35)
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
