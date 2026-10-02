"""Hybrid adapter for CIVPROP Mission / Observation / Knowledge V1.

The actor-visible lane evaluates missions from knowledge, access, capability, budget
and typed economics. Hidden evaluator truth is read only in execute_due(), where it
is passed to BinaryObservationRuntime to produce a noisy observation.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Optional

from engineering.civprop.contracts.accessibility_v1 import (
    AccessibilityRequest,
    AccessibilityRuntime,
    accessibility_runtime,
)
from engineering.civprop.contracts.project_economics_v1 import (
    ProjectEconomicsRuntime,
)
from engineering.civprop.contracts.mission_knowledge_v1 import (
    BinaryObservationRuntime,
    KnowledgeRuntime,
    MissionDecisionInputs,
    MissionKnowledgeRuntime,
)

from .prototypes.common import (
    MutableActorBudget,
    actor_tech_status,
    budget_debit,
)


_CAPABILITY_PRIORITY = {
    "UNUSABLE": 3,
    "UNKNOWN": 2,
    "CONDITIONAL": 1,
    "USABLE": 0,
}


class MissionLaneV1:
    def __init__(self, bundle, seed: int, recorder):
        package = bundle.scenario.mission_knowledge_v1
        if package is None:
            raise ValueError("MissionLaneV1 requires Mission/Knowledge V1")
        self.bundle = bundle
        self.package = package
        self.runtime = MissionKnowledgeRuntime(package)
        self.observer = BinaryObservationRuntime(package, seed)
        self.knowledge = {}
        self._mission_by_id = {
            x.mission_archetype_id: x for x in package.missions
        }
        self._decision_by_mission = {
            x.mission_archetype_id: x for x in package.decision_models
        }
        self._question_by_id = {x.question_id: x for x in package.questions}
        self._actor_state_by_id = (
            {x.actor_id: x for x in bundle.scenario.actor_state_v1.actors}
            if bundle.scenario.actor_state_v1 is not None else {}
        )
        self._completed_mission_keys = set()
        self._economics_runtime = (
            ProjectEconomicsRuntime(bundle.scenario.project_economics_v1)
            if bundle.scenario.project_economics_v1 is not None else None
        )
        self._initialize_knowledge(recorder)

    def _initialize_knowledge(self, recorder) -> None:
        year = self.bundle.scenario.start_year
        for actor in sorted(self.bundle.scenario.actors, key=lambda x: x.actor_id):
            for question in sorted(
                self.package.questions,
                key=lambda x: x.question_id,
            ):
                state = self.runtime.initial_knowledge(
                    actor_id=actor.actor_id,
                    question_id=question.question_id,
                    year=year,
                )
                key = (
                    state.actor_id,
                    state.subject_id,
                    state.location_id,
                )
                self.knowledge[key] = state
                recorder.knowledge_states.append(state)

    def _economics(self, mission_archetype_id: str, year: int):
        mission = self._mission_by_id[mission_archetype_id]
        decision = self._decision_by_mission[mission_archetype_id]
        if self._economics_runtime is not None:
            economics = self._economics_runtime
            mission_economics = economics.resolve(
                mission.project_economics_id,
                year=year,
            )
            continuation = economics.resolve(
                decision.follow_on_project_id,
                year=year,
            )
            return (
                mission_economics.capital_cost,
                mission_economics.construction_lag_years,
                continuation.capital_cost,
                mission_economics.capital_unit,
            )

        projects = {
            x.project_archetype_id: x
            for x in self.bundle.scenario.project_archetypes
        }
        mission_project = projects[mission.project_economics_id]
        follow_on = projects[decision.follow_on_project_id]
        return (
            mission_project.capital_cost,
            mission_project.construction_lag_years,
            follow_on.capital_cost,
            self.bundle.scenario.units["capital"],
        )

    def _access_status(
        self,
        *,
        actor_id: str,
        mission_archetype_id: str,
        year: int,
    ) -> str:
        mission = self._mission_by_id[mission_archetype_id]
        if mission.destination_location_id == mission.origin_location_id:
            return "FEASIBLE"

        if self.bundle.scenario.accessibility_v1 is not None:
            if self.bundle.scenario.actor_state_v1 is None:
                return "UNKNOWN"
            actor_state = self._actor_state_by_id.get(actor_id)
            if actor_state is None:
                return "UNKNOWN"
            assessment = accessibility_runtime(
                self.bundle.scenario.accessibility_v1
            ).assess(
                AccessibilityRequest(
                    actor_id=actor_id,
                    origin_location_id=mission.origin_location_id,
                    destination_location_id=mission.destination_location_id,
                    epoch_utc=f"{year:04d}-07-01T00:00:00Z",
                    mission_class=mission.mission_class,
                    service_class=mission.service_class,
                    subject_id=mission.mission_archetype_id,
                ),
                actor_state=actor_state,
                technology_state={},
            )
            return assessment.status

        profile = next(
            (
                x
                for x in self.bundle.scenario.accessibility
                if x.origin_location_id == mission.origin_location_id
                and x.destination_location_id == mission.destination_location_id
            ),
            None,
        )
        if profile is None:
            return "UNKNOWN"
        point = next((x for x in profile.years if x.year == year), None)
        return "UNKNOWN" if point is None else point.status

    def _capability_status(
        self,
        *,
        actor_id: str,
        mission_archetype_id: str,
        year: int,
    ) -> str:
        mission = self._mission_by_id[mission_archetype_id]
        statuses = [
            actor_tech_status(
                self.bundle,
                actor_id,
                tech_id,
                year,
            )
            for tech_id in mission.required_tech
        ]
        if not statuses:
            return "USABLE"
        return max(statuses, key=lambda x: _CAPABILITY_PRIORITY[x])

    @staticmethod
    def _budget_fields(budget, unit: str):
        if isinstance(budget, MutableActorBudget):
            return (
                budget.status,
                budget.amount,
                budget.unit,
            )
        return ("KNOWN", float(budget), unit)

    def evaluate_and_commit(
        self,
        *,
        year: int,
        budgets,
        recorder,
    ) -> None:
        for actor in sorted(self.bundle.scenario.actors, key=lambda x: x.actor_id):
            actor_id = actor.actor_id
            for mission in sorted(
                self.package.missions,
                key=lambda x: x.mission_archetype_id,
            ):
                if (actor_id, mission.mission_archetype_id) in self._completed_mission_keys:
                    continue

                key = (
                    actor_id,
                    self._question_by_id[mission.target_question_id].subject_id,
                    mission.destination_location_id,
                )
                knowledge = self.knowledge[key]
                mission_cost, lag, continuation_cost, capital_unit = self._economics(
                    mission.mission_archetype_id,
                    year,
                )
                budget_status, budget_amount, budget_unit = self._budget_fields(
                    budgets[actor_id],
                    capital_unit,
                )
                decision = self.runtime.evaluate(
                    knowledge,
                    MissionDecisionInputs(
                        year=year,
                        actor_id=actor_id,
                        mission_archetype_id=mission.mission_archetype_id,
                        access_status=self._access_status(
                            actor_id=actor_id,
                            mission_archetype_id=mission.mission_archetype_id,
                            year=year,
                        ),
                        capability_status=self._capability_status(
                            actor_id=actor_id,
                            mission_archetype_id=mission.mission_archetype_id,
                            year=year,
                        ),
                        budget_status=budget_status,
                        budget_amount=budget_amount,
                        budget_unit=budget_unit,
                        mission_cost=mission_cost,
                        continuation_cost=continuation_cost,
                        continuation_unit=capital_unit,
                    ),
                )
                execution_year = year + lag
                if (
                    decision.action == "COMMIT_MISSION"
                    and execution_year > self.bundle.scenario.end_year
                ):
                    decision = replace(
                        decision,
                        action="WAIT",
                        status="DECLINED",
                        rationale_codes=decision.rationale_codes
                        + ("EXECUTION_OUTSIDE_HORIZON",),
                    )

                recorder.mission_decisions.append(decision)
                recorder.event(
                    year,
                    "MISSION_DECISION_MADE",
                    actor_id,
                    mission.destination_location_id,
                )

                if decision.action != "COMMIT_MISSION":
                    continue

                budgets[actor_id] = budget_debit(
                    self.bundle,
                    budgets[actor_id],
                    mission_cost,
                )
                record = self.runtime.mission_record(
                    actor_id=actor_id,
                    mission_archetype_id=mission.mission_archetype_id,
                    committed_year=year,
                    execution_year=execution_year,
                    capital_cost=mission_cost,
                    capital_unit=capital_unit,
                )
                recorder.missions.append(record)
                self._completed_mission_keys.add((actor_id, mission.mission_archetype_id))
                recorder.event(
                    year,
                    "MISSION_COMMITTED",
                    actor_id,
                    mission.destination_location_id,
                )

    def execute_due(
        self,
        *,
        year: int,
        recorder,
    ) -> None:
        for index, mission in list(enumerate(recorder.missions)):
            if mission.status != "COMMITTED" or mission.execution_year != year:
                continue

            question = self._question_by_id[mission.question_id]

            # Epistemic firewall: this is the sole Hybrid integration point that
            # reads evaluator-only physical realization.
            truth = next(
                (
                    x
                    for x in self.bundle.truth.resources
                    if x.resource_id == question.subject_id
                ),
                None,
            )
            if truth is None:
                raise ValueError("mission observation has no hidden physical realization")

            executed = replace(mission, status="EXECUTED")
            recorder.missions[index] = executed
            recorder.event(
                year,
                "MISSION_EXECUTED",
                mission.actor_id,
                mission.destination_location_id,
            )
            observation = self.observer.observe(
                mission=executed,
                hidden_present=truth.present,
                year=year,
            )
            recorder.observations.append(observation)
            recorder.event(
                year,
                "OBSERVATION_PRODUCED",
                mission.actor_id,
                mission.destination_location_id,
            )
            recorder.event(
                year,
                "OBSERVATION_RECEIVED",
                mission.actor_id,
                mission.destination_location_id,
            )

            key = (
                mission.actor_id,
                question.subject_id,
                question.location_id,
            )
            current = self.knowledge[key]
            updated = KnowledgeRuntime.update(current, observation)
            self.knowledge[key] = updated
            recorder.knowledge_states.append(updated)
            recorder.event(
                year,
                "KNOWLEDGE_UPDATED",
                mission.actor_id,
                mission.destination_location_id,
            )


__all__ = ["MissionLaneV1"]
