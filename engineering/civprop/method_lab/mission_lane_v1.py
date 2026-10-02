"""Hybrid adapter for CIVPROP Mission / Observation / Knowledge V1.

The actor-visible lane evaluates missions from knowledge, access, capability, budget
and typed economics. Hidden evaluator truth is read only in execute_due(), where it
is passed to BinaryObservationRuntime to produce a noisy observation.
"""
from __future__ import annotations

from dataclasses import replace
import hashlib
from typing import Optional

from engineering.civprop.contracts.accessibility_v1 import (
    AccessibilityRequest,
    AccessibilityRuntime,
    accessibility_runtime,
)
from engineering.civprop.contracts.solar_reconnaissance_knowledge_v0_3 import characterization_gate_reasons
from engineering.civprop.contracts.project_economics_v1 import (
    ProjectEconomicsRuntime,
)
from engineering.civprop.contracts.mission_knowledge_v1 import (
    BinaryObservationRuntime,
    CharacterizationKnowledgeStateV1,
    CharacterizationObservationRecordV1,
    KnowledgeRuntime,
    MissionDecisionInputs,
    MissionDecisionRecordV1,
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
                if question.question_kind == "UNRESOLVED_CHARACTERIZATION":
                    state = CharacterizationKnowledgeStateV1(
                        actor_id=actor.actor_id, question_id=question.question_id,
                        subject_id=question.subject_id, location_id=question.location_id,
                        characterization_status="UNRESOLVED", source_id=f"unresolved:{question.question_id}",
                        year=year, visibility=question.visibility, evidence_disposition=question.evidence_disposition,
                    )
                else:
                    state = self.runtime.initial_knowledge(
                        actor_id=actor.actor_id, question_id=question.question_id, year=year,
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

    def _access_assessment(
        self, *, actor_id: str, mission_archetype_id: str, year: int
    ):
        mission = self._mission_by_id[mission_archetype_id]
        if mission.destination_location_id == mission.origin_location_id:
            return None
        if self.bundle.scenario.accessibility_v1 is None or self.bundle.scenario.actor_state_v1 is None:
            return None
        actor_state = self._actor_state_by_id.get(actor_id)
        if actor_state is None: return None
        return accessibility_runtime(self.bundle.scenario.accessibility_v1).assess(
            AccessibilityRequest(actor_id=actor_id, origin_location_id=mission.origin_location_id,
                destination_location_id=mission.destination_location_id, epoch_utc=f"{year:04d}-07-01T00:00:00Z",
                mission_class=mission.mission_class, service_class=mission.service_class, subject_id=mission.mission_archetype_id),
            actor_state=actor_state, technology_state={
                tech_id: actor_tech_status(self.bundle, actor_id, tech_id, year)
                for service in self.bundle.scenario.accessibility_v1.service_paths
                if service.actor_id == actor_id
                and service.origin_location_id == mission.origin_location_id
                and service.destination_location_id == mission.destination_location_id
                and service.mission_class == mission.mission_class
                and service.service_class == mission.service_class
                for tech_id in service.required_technology_ids
            })

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
            assessment=self._access_assessment(actor_id=actor_id,mission_archetype_id=mission_archetype_id,year=year)
            return "UNKNOWN" if assessment is None else assessment.status

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
            question=self._question_by_id[mission.target_question_id]
            return "UNKNOWN" if question.question_kind == "UNRESOLVED_CHARACTERIZATION" else "USABLE"
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

    def _exploration_weight(self, actor_id: str, year: int) -> Optional[float]:
        state=self._actor_state_by_id.get(actor_id)
        if state is None or state.experience.status != "KNOWN_RECORDS": return None
        for record in state.experience.records:
            if record.scope != "SOLAR_CHARACTERIZATION_PRIORITY_V0_3": continue
            if record.valid_from is not None and year < record.valid_from: continue
            if record.valid_to is not None and year > record.valid_to: continue
            value=record.details.get("exploration_weight")
            return None if value is None else float(value)
        return None

    def _characterization_annual_cap(self, actor_id: str, year: int) -> int:
        weight=self._exploration_weight(actor_id,year)
        caps={0.25:1,0.5:2,0.75:3}
        if weight not in caps:
            raise ValueError(f"UNKNOWN_OR_UNAUTHORIZED_EXPLORATION_WEIGHT:{actor_id}:{year}:{weight}")
        return caps[weight]

    def _characterization_rank(self, actor_id: str, mission, year: int, mission_cost: float, assessment=None):
        if assessment is None:
            assessment=self._access_assessment(actor_id=actor_id,mission_archetype_id=mission.mission_archetype_id,year=year)
        friction=None
        if assessment is not None:
            for component in assessment.generalized_cost.components:
                if component.component_id == "SOLAR_V03_GAP016_FRICTION_PROXY":
                    friction=component.value
                    break
        if friction is None: friction=float("inf")
        # Lower authored GAP-016 friction and lower mission cost are preferred.
        # No resource abundance, attractiveness, or economic value is inferred.
        return (float(friction),float(mission_cost),mission.destination_location_id,mission.mission_archetype_id)

    def _evaluate_characterization(self, *, knowledge, mission, year, actor_id,
                                   access_status, capability_status, budget_status,
                                   budget_amount, budget_unit, mission_cost):
        weight=self._exploration_weight(actor_id,year)
        budget_known=budget_status == "KNOWN" and budget_amount is not None and budget_unit == self.package.capital_unit
        affordable=budget_known and budget_amount + 1e-12 >= mission_cost
        reasons=list(characterization_gate_reasons(characterization_status=knowledge.characterization_status,
            prior_probability=None,nav1_candidate=(access_status == "FEASIBLE"),
            capability_usable=(capability_status == "USABLE"),budget_known=budget_known,
            affordable=affordable,exploration_weight=weight))
        if budget_status == "KNOWN" and budget_amount is not None and budget_unit != self.package.capital_unit:
            reasons=[x for x in reasons if x != "BUDGET_UNKNOWN"]+["BUDGET_UNIT_MISMATCH"]
        action="WAIT" if reasons else "COMMIT_MISSION"; status="DECLINED" if reasons else "COMMITTED"
        if not reasons: reasons=["AUTHORED_EXPLORATION_PRIORITY"]
        raw=f"{actor_id}|{mission.mission_archetype_id}|{year}|{knowledge.source_id}".encode()
        return MissionDecisionRecordV1(decision_id="md-"+hashlib.sha256(raw).hexdigest()[:16], year=year, actor_id=actor_id,
            mission_archetype_id=mission.mission_archetype_id, question_id=knowledge.question_id,
            target_location_id=mission.destination_location_id, action=action, status=status,
            expected_value_of_information=None, value_unit=self.package.capital_unit, rationale_codes=tuple(reasons))

    def evaluate_and_commit(self, *, year: int, budgets, recorder) -> None:
        for actor in sorted(self.bundle.scenario.actors, key=lambda x: x.actor_id):
            actor_id=actor.actor_id
            binary=[]; characterization=[]
            for mission in sorted(self.package.missions,key=lambda x:x.mission_archetype_id):
                if (actor_id,mission.mission_archetype_id) in self._completed_mission_keys: continue
                question=self._question_by_id[mission.target_question_id]
                (characterization if question.question_kind=="UNRESOLVED_CHARACTERIZATION" else binary).append(mission)

            # Preserve legacy binary/Bayesian mission behavior exactly.
            ordered=[(m,False) for m in binary]
            # Characterization is a portfolio choice, not 344 independent yes/no decisions.
            ranked=[]
            characterization_eval={}
            weight=self._exploration_weight(actor_id,year)
            for mission in characterization:
                question=self._question_by_id[mission.target_question_id]
                key=(actor_id,question.subject_id,mission.destination_location_id); knowledge=self.knowledge[key]
                cost,lag,continuation_cost,unit=self._economics(mission.mission_archetype_id,year)
                budget_status,budget_amount,budget_unit=self._budget_fields(budgets[actor_id],unit)
                assessment=self._access_assessment(actor_id=actor_id,mission_archetype_id=mission.mission_archetype_id,year=year)
                access_status="FEASIBLE" if mission.destination_location_id == mission.origin_location_id else ("UNKNOWN" if assessment is None else assessment.status)
                capability_status=self._capability_status(actor_id=actor_id,mission_archetype_id=mission.mission_archetype_id,year=year)
                snapshot=(knowledge,cost,lag,continuation_cost,unit,budget_status,budget_amount,budget_unit,access_status,capability_status,assessment,weight)
                characterization_eval[mission.mission_archetype_id]=snapshot
                eligible=(knowledge.characterization_status == "UNRESOLVED" and access_status == "FEASIBLE" and capability_status == "USABLE" and budget_status == "KNOWN" and budget_amount is not None and budget_unit == self.package.capital_unit and budget_amount + 1e-12 >= cost and weight in {0.25,0.5,0.75})
                if eligible:
                    ranked.append((self._characterization_rank(actor_id,mission,year,cost,assessment=assessment),mission))
            # Unknown/unauthorized behavior authority blocks selection but remains
            # observable in dispositions; it must not crash the production world.
            cap=(self._characterization_annual_cap(actor_id,year)
                 if characterization and weight in {0.25,0.5,0.75} else 0)
            # Availability is not a decision. Only the bounded annual shortlist is
            # promoted into actor decision records; the rest remain opportunity-set
            # members and therefore do not create millions of synthetic WAIT rows.
            selected_ranked=sorted(ranked)[:cap]
            selected={m.mission_archetype_id for _,m in selected_ranked}
            ordered.extend((m,True) for _,m in selected_ranked)
            # Gate-B observability: every characterization candidate receives an
            # explicit annual disposition. Non-shortlisted opportunities are not
            # actor decisions, but they may no longer vanish silently.
            if hasattr(recorder, "mission_opportunity_dispositions"):
                ranked_ids={m.mission_archetype_id for _,m in ranked}
                for mission in characterization:
                    question=self._question_by_id[mission.target_question_id]
                    knowledge,cost,_,_,unit,budget_status,budget_amount,budget_unit,access_status,capability_status,_,weight=characterization_eval[mission.mission_archetype_id]
                    reasons=[]
                    if knowledge.characterization_status != "UNRESOLVED": reasons.append("CHARACTERIZATION_ALREADY_RESOLVED")
                    if access_status != "FEASIBLE": reasons.append(f"ACCESS_{access_status}")
                    if capability_status != "USABLE": reasons.append(f"CAPABILITY_{capability_status}")
                    if budget_status != "KNOWN" or budget_amount is None: reasons.append("BUDGET_UNKNOWN")
                    elif budget_unit != self.package.capital_unit: reasons.append("BUDGET_UNIT_MISMATCH")
                    elif budget_amount + 1e-12 < cost: reasons.append("BUDGET_INSUFFICIENT")
                    if weight not in {0.25,0.5,0.75}: reasons.append("EXPLORATION_WEIGHT_UNAUTHORIZED")
                    if mission.mission_archetype_id in selected:
                        disposition="DECISION_EMITTED"
                    elif mission.mission_archetype_id in ranked_ids:
                        disposition="EXCLUDED_ANNUAL_PORTFOLIO_CAP"; reasons.append("ANNUAL_PORTFOLIO_CAP")
                    else:
                        disposition="EXCLUDED_GATE"
                    row={"year":year,"actor_id":actor_id,"mission_archetype_id":mission.mission_archetype_id,
                        "question_id":question.question_id,"target_location_id":mission.destination_location_id,
                        "disposition":disposition,"reason_codes":sorted(set(reasons))}
                    if (getattr(recorder,"compact_mission_opportunity_dispositions",False)
                            and disposition != "DECISION_EMITTED"):
                        # Exact accounting without one near-duplicate row per question.
                        # The member digest preserves the deterministic identity of the
                        # omitted opportunity set; count + reasons preserve auditability.
                        key=(year,actor_id,disposition,tuple(row["reason_codes"]))
                        groups=getattr(recorder,"_mission_disposition_groups",None)
                        if groups is None:
                            groups={}; recorder._mission_disposition_groups=groups
                        g=groups.get(key)
                        member=f'{mission.mission_archetype_id}|{question.question_id}|{mission.destination_location_id}'
                        if g is None:
                            import hashlib as _hashlib
                            g={"count":0,"hasher":_hashlib.sha256()}; groups[key]=g
                        g["count"]+=1; g["hasher"].update((member+"\n").encode())
                    else:
                        recorder.mission_opportunity_dispositions.append(row)

            if getattr(recorder,"compact_mission_opportunity_dispositions",False):
                groups=getattr(recorder,"_mission_disposition_groups",{})
                for key in sorted([k for k in groups if k[0]==year and k[1]==actor_id]):
                    y,a,d,reasons=key; g=groups.pop(key)
                    recorder.mission_opportunity_disposition_summaries.append({
                        "year":y,"actor_id":a,"disposition":d,"reason_codes":list(reasons),
                        "opportunity_count":g["count"],"member_sha256":g["hasher"].hexdigest(),
                        "aggregation":"CHARACTERIZATION_OPPORTUNITY_SET_V1"})

            for mission,is_characterization in ordered:
                question=self._question_by_id[mission.target_question_id]
                key=(actor_id,question.subject_id,mission.destination_location_id); knowledge=self.knowledge[key]
                if is_characterization:
                    knowledge,mission_cost,lag,continuation_cost,capital_unit,_,_,_,access_status,capability_status,_,_=characterization_eval[mission.mission_archetype_id]
                    # Budget is mutable within the actor's annual shortlist: preserve
                    # sequential debit semantics while reusing expensive assessments.
                    budget_status,budget_amount,budget_unit=self._budget_fields(budgets[actor_id],capital_unit)
                else:
                    mission_cost,lag,continuation_cost,capital_unit=self._economics(mission.mission_archetype_id,year)
                    budget_status,budget_amount,budget_unit=self._budget_fields(budgets[actor_id],capital_unit)
                    access_status=self._access_status(actor_id=actor_id,mission_archetype_id=mission.mission_archetype_id,year=year)
                    capability_status=self._capability_status(actor_id=actor_id,mission_archetype_id=mission.mission_archetype_id,year=year)
                if is_characterization:
                    decision=self._evaluate_characterization(knowledge=knowledge,mission=mission,year=year,actor_id=actor_id,
                        access_status=access_status,capability_status=capability_status,budget_status=budget_status,
                        budget_amount=budget_amount,budget_unit=budget_unit,mission_cost=mission_cost)
                else:
                    decision=self.runtime.evaluate(knowledge,MissionDecisionInputs(year=year,actor_id=actor_id,
                        mission_archetype_id=mission.mission_archetype_id,access_status=access_status,
                        capability_status=capability_status,budget_status=budget_status,budget_amount=budget_amount,
                        budget_unit=budget_unit,mission_cost=mission_cost,continuation_cost=continuation_cost,continuation_unit=capital_unit))
                execution_year=year+lag
                if decision.action=="COMMIT_MISSION" and execution_year>self.bundle.scenario.end_year:
                    decision=replace(decision,action="WAIT",status="DECLINED",rationale_codes=decision.rationale_codes+("EXECUTION_OUTSIDE_HORIZON",))
                recorder.mission_decisions.append(decision); recorder.event(year,"MISSION_DECISION_MADE",actor_id,mission.destination_location_id)
                if decision.action!="COMMIT_MISSION": continue
                budgets[actor_id]=budget_debit(self.bundle,budgets[actor_id],mission_cost)
                record=self.runtime.mission_record(actor_id=actor_id,mission_archetype_id=mission.mission_archetype_id,
                    committed_year=year,execution_year=execution_year,capital_cost=mission_cost,capital_unit=capital_unit)
                recorder.missions.append(record); self._completed_mission_keys.add((actor_id,mission.mission_archetype_id))
                recorder.event(year,"MISSION_COMMITTED",actor_id,mission.destination_location_id)

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

            if question.question_kind == "UNRESOLVED_CHARACTERIZATION":
                executed=replace(mission,status="EXECUTED"); recorder.missions[index]=executed
                recorder.event(year,"MISSION_EXECUTED",mission.actor_id,mission.destination_location_id)
                raw=f"{mission.mission_id}|{year}|characterization".encode()
                observation=CharacterizationObservationRecordV1(
                    observation_id="obs-"+hashlib.sha256(raw).hexdigest()[:16], mission_id=mission.mission_id,
                    actor_id=mission.actor_id, question_id=question.question_id, subject_id=question.subject_id,
                    location_id=question.location_id, year=year, characterization_status="CHARACTERIZATION_COMPLETED",
                    resource_result_status="UNRESOLVED_WITHOUT_AUTHORIZED_OBSERVATION_RESULT", visibility=question.visibility)
                recorder.observations.append(observation)
                recorder.event(year,"OBSERVATION_PRODUCED",mission.actor_id,mission.destination_location_id)
                recorder.event(year,"OBSERVATION_RECEIVED",mission.actor_id,mission.destination_location_id)
                key=(mission.actor_id,question.subject_id,question.location_id); current=self.knowledge[key]
                updated=replace(current,characterization_status="CHARACTERIZATION_COMPLETED",source_id=observation.observation_id,
                    year=year,observation_ids=current.observation_ids+(observation.observation_id,),visibility=observation.visibility)
                self.knowledge[key]=updated; recorder.knowledge_states.append(updated)
                recorder.event(year,"KNOWLEDGE_UPDATED",mission.actor_id,mission.destination_location_id)
                continue

            # Epistemic firewall: this is the sole binary-presence integration point that
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
