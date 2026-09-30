"""Candidate C: actor-sequential discrete-event project scheduling."""
from __future__ import annotations

import heapq

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
    stable_unit,
)


class ActorEventEngine:
    engine_id = "ACTOR_DISCRETE_EVENT"
    engine_version = "prototype-v1"

    def _actor_weight(self, actor_type, opportunity):
        c = opportunity.project.output_capacities
        if actor_type == "PUBLIC_FINANCER":
            return 0.10 * c.habitat + 0.20 * c.power + 0.15 * c.transport + 0.10 * c.resource
        return 0.25 * c.industrial + 0.20 * c.transport + 0.15 * c.resource + 0.05 * c.power

    def run(self, bundle, seed):
        states = initial_state(bundle)
        budgets = actor_budget(bundle)
        actor_types = {x.actor_id: x.actor_type for x in bundle.scenario.actors}
        pending = []
        recorder = Recorder()
        annual_states = []
        queue = []
        serial = 0

        def push(year, phase, kind, actor_id=None):
            nonlocal serial
            serial += 1
            heapq.heappush(queue, (year, phase, serial, kind, actor_id))

        recorder.event(bundle.scenario.start_year, "RUN_STARTED")
        for year in range(bundle.scenario.start_year, bundle.scenario.end_year + 1):
            for actor_id in sorted(budgets):
                push(year, 20, "ACTOR_DECISION", actor_id)
            push(year, 30, "MIGRATION")
            push(year, 40, "SNAPSHOT")

        current_year = bundle.scenario.start_year
        credited_years = set()
        while queue:
            year, phase, _, kind, actor_id = heapq.heappop(queue)
            current_year = year
            if year not in credited_years:
                if year > bundle.scenario.start_year:
                    for aid in budgets:
                        budgets[aid] += actor_inflow(bundle, aid)
                commission_due(year, pending, states, recorder)
                credited_years.add(year)

            if kind == "ACTOR_DECISION":
                choices = []
                for opportunity in opportunities(bundle, states, actor_id, year):
                    project_id = opportunity.project.project_archetype_id
                    if already_pending(pending, opportunity.location_id, project_id):
                        continue
                    if budgets[actor_id] + 1e-9 < opportunity.project.capital_cost:
                        continue
                    jitter = 2.0 * stable_unit(
                        seed,
                        self.engine_id,
                        actor_id,
                        year,
                        opportunity.location_id,
                        project_id,
                    )
                    score = (
                        base_utility(opportunity)
                        + self._actor_weight(actor_types[actor_id], opportunity)
                        + jitter
                    )
                    choices.append((score, opportunity))

                choices.sort(
                    key=lambda item: (
                        item[0],
                        item[1].location_id,
                        item[1].project.project_archetype_id,
                    ),
                    reverse=True,
                )
                if not choices or choices[0][0] <= -2.0:
                    recorder.decision(
                        year,
                        actor_id,
                        "WAIT",
                        "DECLINED",
                        rationale=("ACTOR_NO_ACCEPTABLE_EVENT",),
                    )
                    continue

                _, choice = choices[0]
                budgets[actor_id] -= choice.project.capital_cost
                schedule(pending, recorder, self.engine_id, actor_id, choice, year)
                recorder.decision(
                    year,
                    actor_id,
                    "COMMIT_PROJECT",
                    "COMMITTED",
                    choice.location_id,
                    choice.project.project_archetype_id,
                    rationale=("ACTOR_EVENT_RANKING",),
                )

            elif kind == "MIGRATION":
                migration_step(bundle, states, year, recorder, adjustment=0.50)

            elif kind == "SNAPSHOT":
                annual_states.extend(snapshot(year, states))

        recorder.event(current_year, "RUN_COMPLETED")
        return finalize(
            bundle,
            self.engine_id,
            self.engine_version,
            seed,
            annual_states,
            recorder,
        )
