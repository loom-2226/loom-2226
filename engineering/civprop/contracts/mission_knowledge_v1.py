"""CIVPROP Mission / Observation / Knowledge V1.

General mission/knowledge contracts with one admitted observation implementation:
binary resource-presence detection with a Bernoulli confusion matrix.

Actor decisions consume actor-visible knowledge only. Hidden physical realization is
accepted solely by BinaryObservationRuntime.observe().
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Optional


FORMAT = "CIVPROP_MISSION_KNOWLEDGE_V1"
CONTRACT_VERSION = "1.1.0"
PACKAGE_STATUS = "GENERAL_CONTRACT_BINARY_RESOURCE_IMPLEMENTATION_V1"
QUESTION_KIND = "BINARY_PRESENCE"
QUESTION_KINDS = {"BINARY_PRESENCE", "UNRESOLVED_CHARACTERIZATION"}
OBSERVATION_MODEL_KIND = "BERNOULLI_CONFUSION_MATRIX_V1"
DECISION_MODEL_KIND = "EXPECTED_VALUE_OF_SAMPLE_INFORMATION_V1"
CHARACTERIZATION_DECISION_MODEL_KIND = "AUTHORED_EXPLORATION_PRIORITY_V1"
DECISION_MODEL_KINDS = {DECISION_MODEL_KIND, CHARACTERIZATION_DECISION_MODEL_KIND}
VALUE_STATUS = {"UNKNOWN", "SCENARIO_ASSUMPTION", "QUALIFIED_REFERENCE"}
VISIBILITY = {"PRIVATE", "PUBLIC", "PARTNER"}
ACCESS_STATUS = {"FEASIBLE", "INFEASIBLE", "UNKNOWN"}
CAPABILITY_STATUS = {"USABLE", "CONDITIONAL", "UNUSABLE", "UNKNOWN"}
BUDGET_STATUS = {"KNOWN", "UNKNOWN"}


def _prob(value: Any, name: str) -> float:
    out = float(value)
    if not math.isfinite(out) or not 0 < out < 1:
        raise ValueError(f"{name} must be finite and strictly between zero and one")
    return out


def _nonnegative(value: Any, name: str) -> float:
    out = float(value)
    if not math.isfinite(out) or out < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return out


def _refs(data: Mapping[str, Any], name: str) -> tuple[str, ...]:
    refs = tuple(str(x) for x in data.get("provenance_refs", ()))
    if not refs:
        raise ValueError(f"{name} requires provenance")
    return refs


@dataclass(frozen=True)
class DecisionValue:
    status: str
    value: Optional[float]
    unit: str
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class KnowledgeQuestion:
    question_id: str
    question_kind: str
    subject_id: str
    location_id: str
    prior_probability: Optional[float]
    prior_status: str
    visibility: str
    provenance_refs: tuple[str, ...]
    evidence_disposition: Optional[str] = None


@dataclass(frozen=True)
class KnowledgeClaimV1:
    """Actor-owned claim derived from evidence/knowledge, not evaluator truth.

    A claim is deliberately distinct from a knowledge question and from a mission.
    Qualification/certification is a later institutional layer.
    """
    claim_id: str
    actor_id: str
    question_id: str
    subject_id: str
    location_id: str
    claim_kind: str
    claim_status: str
    evidence_disposition: Optional[str]
    source_ids: tuple[str, ...]
    year: int
    visibility: str = "PRIVATE"
    authority_class: str = "SIMULATED_CLAIM"


@dataclass(frozen=True)
class ObservationModel:
    observation_model_id: Optional[str]
    model_kind: str
    quantity: str
    unit: str
    sensitivity: float
    false_positive_probability: float
    parameter_status: str
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class MissionArchetype:
    mission_archetype_id: str
    action_kind: str
    mission_class: str
    project_economics_id: str
    target_question_id: str
    observation_model_id: Optional[str]
    origin_location_id: str
    destination_location_id: str
    service_class: str
    required_tech: tuple[str, ...]
    visibility: str
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class MissionDecisionModel:
    decision_model_id: str
    mission_archetype_id: str
    model_kind: str
    follow_on_project_id: str
    success_value: DecisionValue
    threshold: float
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class MissionKnowledgePackage:
    format: str
    contract_version: str
    package_id: str
    scope: str
    package_status: str
    capital_unit: str
    questions: tuple[KnowledgeQuestion, ...]
    observation_models: tuple[ObservationModel, ...]
    missions: tuple[MissionArchetype, ...]
    decision_models: tuple[MissionDecisionModel, ...]


@dataclass(frozen=True)
class KnowledgeStateV1:
    actor_id: str
    question_id: str
    subject_id: str
    location_id: str
    probability: float
    source_id: str
    year: int
    observation_ids: tuple[str, ...] = ()
    visibility: str = "PRIVATE"
    authority_class: str = "SIMULATED_BELIEF"


@dataclass(frozen=True)
class CharacterizationKnowledgeStateV1:
    actor_id: str
    question_id: str
    subject_id: str
    location_id: str
    characterization_status: str
    source_id: str
    year: int
    observation_ids: tuple[str, ...] = ()
    visibility: str = "PRIVATE"
    authority_class: str = "SIMULATED_CHARACTERIZATION_STATE"
    evidence_disposition: Optional[str] = None


@dataclass(frozen=True)
class CharacterizationObservationRecordV1:
    observation_id: str
    mission_id: str
    actor_id: str
    question_id: str
    subject_id: str
    location_id: str
    year: int
    characterization_status: str
    resource_result_status: str
    visibility: str
    authority_class: str = "SIMULATED_CHARACTERIZATION_OBSERVATION"


@dataclass(frozen=True)
class MissionRecordV1:
    mission_id: str
    mission_archetype_id: str
    actor_id: str
    question_id: str
    origin_location_id: str
    destination_location_id: str
    committed_year: int
    execution_year: int
    capital_cost: float
    capital_unit: str
    status: str
    authority_class: str = "SIMULATION_MISSION"


@dataclass(frozen=True)
class ObservationRecordV1:
    observation_id: str
    mission_id: str
    actor_id: str
    question_id: str
    subject_id: str
    location_id: str
    year: int
    detected: bool
    sensitivity: float
    false_positive_probability: float
    quantity: str
    unit: str
    error_model: str
    visibility: str
    authority_class: str = "SIMULATED_OBSERVATION"


@dataclass(frozen=True)
class MissionDecisionRecordV1:
    decision_id: str
    year: int
    actor_id: str
    mission_archetype_id: str
    question_id: str
    target_location_id: str
    action: str
    status: str
    expected_value_of_information: Optional[float]
    value_unit: str
    rationale_codes: tuple[str, ...]
    authority_class: str = "SIMULATION_MISSION_DECISION"


@dataclass(frozen=True)
class MissionDecisionInputs:
    year: int
    actor_id: str
    mission_archetype_id: str
    access_status: str
    capability_status: str
    budget_status: str
    budget_amount: Optional[float]
    budget_unit: Optional[str]
    mission_cost: float
    continuation_cost: float
    continuation_unit: str


def _value(data: Mapping[str, Any], capital_unit: str, name: str) -> DecisionValue:
    status = str(data["status"])
    if status not in VALUE_STATUS:
        raise ValueError(f"{name}: invalid value status")
    unit = str(data.get("unit") or "")
    if unit != capital_unit:
        raise ValueError(f"{name}: unit must match package capital unit")
    raw_value = data.get("value")
    if status == "UNKNOWN":
        if raw_value is not None:
            raise ValueError(f"{name}: UNKNOWN cannot carry a value")
        value = None
    else:
        if raw_value is None:
            raise ValueError(f"{name}: known value status requires value")
        value = _nonnegative(raw_value, f"{name}.value")
    return DecisionValue(
        status=status,
        value=value,
        unit=unit,
        provenance_refs=_refs(data, name),
    )


def load_mission_knowledge_package(data: Mapping[str, Any]) -> MissionKnowledgePackage:
    if data.get("format") != FORMAT or data.get("contract_version") not in {"1.0.0", CONTRACT_VERSION}:
        raise ValueError("unexpected mission/knowledge contract")
    if data.get("package_status") != PACKAGE_STATUS:
        raise ValueError("unexpected mission/knowledge package status")
    capital_unit = str(data.get("capital_unit") or "")
    if not capital_unit:
        raise ValueError("capital_unit required")

    questions = []
    for row in data.get("questions", ()):
        kind = str(row["question_kind"])
        if kind not in QUESTION_KINDS:
            raise ValueError("unsupported knowledge question kind")
        visibility = str(row["visibility"])
        if visibility not in VISIBILITY:
            raise ValueError("invalid knowledge visibility")
        evidence_disposition=row.get("evidence_disposition")
        if kind == "UNRESOLVED_CHARACTERIZATION" and evidence_disposition is not None and str(evidence_disposition) not in {"UNKNOWN_AFTER_SEARCH","SUPPORTED_PRESENT_UNQUANTIFIED","SUPPORTED_QUANTIFIED","SUPPORTED_INFERRED_OR_MODELLED"}:
            raise ValueError("invalid characterization evidence disposition")
        questions.append(
            KnowledgeQuestion(
                question_id=str(row["question_id"]),
                question_kind=kind,
                subject_id=str(row["subject_id"]),
                location_id=str(row["location_id"]),
                prior_probability=(
                    _prob(row["prior_probability"], "prior probability")
                    if kind == QUESTION_KIND
                    else None
                ),
                prior_status=str(row["prior_status"]),
                visibility=visibility,
                provenance_refs=_refs(row, "knowledge question"),
                evidence_disposition=(str(row['evidence_disposition']) if row.get('evidence_disposition') is not None else None),
            )
        )

    observation_models = []
    for row in data.get("observation_models", ()):
        kind = str(row["model_kind"])
        if kind != OBSERVATION_MODEL_KIND:
            raise ValueError("only Bernoulli confusion-matrix observations are admitted in V1")
        sensitivity = _prob(row["sensitivity"], "observation sensitivity")
        false_positive = _prob(
            row["false_positive_probability"],
            "false-positive probability",
        )
        if sensitivity <= false_positive:
            raise ValueError("observation model must be informative")
        observation_models.append(
            ObservationModel(
                observation_model_id=(None if row.get("observation_model_id") is None else str(row["observation_model_id"])) ,
                model_kind=kind,
                quantity=str(row["quantity"]),
                unit=str(row["unit"]),
                sensitivity=sensitivity,
                false_positive_probability=false_positive,
                parameter_status=str(row["parameter_status"]),
                provenance_refs=_refs(row, "observation model"),
            )
        )

    missions = []
    for row in data.get("missions", ()):
        if row.get("action_kind") != "MISSION":
            raise ValueError("mission archetype action_kind must be MISSION")
        visibility = str(row["visibility"])
        if visibility not in VISIBILITY:
            raise ValueError("invalid mission visibility")
        missions.append(
            MissionArchetype(
                mission_archetype_id=str(row["mission_archetype_id"]),
                action_kind="MISSION",
                mission_class=str(row["mission_class"]),
                project_economics_id=str(row["project_economics_id"]),
                target_question_id=str(row["target_question_id"]),
                observation_model_id=(None if row.get("observation_model_id") is None else str(row["observation_model_id"])) ,
                origin_location_id=str(row["origin_location_id"]),
                destination_location_id=str(row["destination_location_id"]),
                service_class=str(row["service_class"]),
                required_tech=tuple(str(x) for x in row.get("required_tech", ())),
                visibility=visibility,
                provenance_refs=_refs(row, "mission archetype"),
            )
        )

    decision_models = []
    for row in data.get("decision_models", ()):
        if row.get("model_kind") not in DECISION_MODEL_KINDS:
            raise ValueError("unsupported mission decision model")
        threshold = _nonnegative(row["threshold"], "mission decision threshold")
        decision_models.append(
            MissionDecisionModel(
                decision_model_id=str(row["decision_model_id"]),
                mission_archetype_id=str(row["mission_archetype_id"]),
                model_kind=str(row["model_kind"]),
                follow_on_project_id=str(row["follow_on_project_id"]),
                success_value=_value(
                    row["success_value"],
                    capital_unit,
                    "mission success value",
                ),
                threshold=threshold,
                provenance_refs=_refs(row, "mission decision model"),
            )
        )

    def unique(items, field: str) -> None:
        values = [getattr(x, field) for x in items]
        if not values or len(values) != len(set(values)):
            raise ValueError(f"{field} must be nonempty and unique")

    unique(questions, "question_id")
    unique(observation_models, "observation_model_id")
    unique(missions, "mission_archetype_id")
    unique(decision_models, "decision_model_id")

    question_ids = {x.question_id for x in questions}
    model_ids = {x.observation_model_id for x in observation_models}
    mission_ids = {x.mission_archetype_id for x in missions}
    question_by_id = {x.question_id: x for x in questions}
    for mission in missions:
        if mission.target_question_id not in question_ids:
            raise ValueError("mission references unknown knowledge question")
        question = question_by_id[mission.target_question_id]
        if question.question_kind == QUESTION_KIND:
            if mission.observation_model_id not in model_ids:
                raise ValueError("binary mission references unknown observation model")
        elif question.question_kind == "UNRESOLVED_CHARACTERIZATION":
            if mission.observation_model_id is not None:
                raise ValueError("characterization mission cannot claim binary observation model")
    for decision in decision_models:
        if decision.mission_archetype_id not in mission_ids:
            raise ValueError("decision model references unknown mission")
    if {x.mission_archetype_id for x in decision_models} != mission_ids:
        raise ValueError("each mission requires exactly one decision model")

    return MissionKnowledgePackage(
        format=FORMAT,
        contract_version=CONTRACT_VERSION,
        package_id=str(data["package_id"]),
        scope=str(data["scope"]),
        package_status=PACKAGE_STATUS,
        capital_unit=capital_unit,
        questions=tuple(questions),
        observation_models=tuple(observation_models),
        missions=tuple(missions),
        decision_models=tuple(decision_models),
    )


def load_mission_knowledge_path(path: Path) -> MissionKnowledgePackage:
    return load_mission_knowledge_package(json.loads(Path(path).read_text()))


class KnowledgeRuntime:
    @staticmethod
    def update(
        knowledge: KnowledgeStateV1,
        observation: ObservationRecordV1,
    ) -> KnowledgeStateV1:
        if observation.actor_id != knowledge.actor_id:
            raise ValueError("observation actor does not match knowledge owner")
        if observation.question_id != knowledge.question_id:
            raise ValueError("observation question does not match knowledge")
        if observation.subject_id != knowledge.subject_id:
            raise ValueError("observation subject does not match knowledge")
        if observation.location_id != knowledge.location_id:
            raise ValueError("observation location does not match knowledge")
        if observation.observation_id in knowledge.observation_ids:
            raise ValueError("duplicate observation")
        if observation.year < knowledge.year:
            raise ValueError("observation predates knowledge state")
        p = knowledge.probability
        if observation.detected:
            a = observation.sensitivity
            b = observation.false_positive_probability
        else:
            a = 1.0 - observation.sensitivity
            b = 1.0 - observation.false_positive_probability
        denominator = p * a + (1.0 - p) * b
        if denominator <= 0:
            raise ValueError("invalid Bayesian denominator")
        posterior = p * a / denominator
        return replace(
            knowledge,
            probability=posterior,
            source_id=observation.observation_id,
            year=observation.year,
            observation_ids=knowledge.observation_ids + (observation.observation_id,),
            visibility=observation.visibility,
        )


class MissionKnowledgeRuntime:
    """Actor-visible mission decision and knowledge mechanics.

    This class has no hidden-physical-realization argument. Hidden truth enters only
    BinaryObservationRuntime.
    """

    def __init__(self, package: MissionKnowledgePackage):
        self.package = package
        self._questions = {x.question_id: x for x in package.questions}
        self._models = {
            x.observation_model_id: x for x in package.observation_models
        }
        self._missions = {x.mission_archetype_id: x for x in package.missions}
        self._decisions = {
            x.mission_archetype_id: x for x in package.decision_models
        }

    def initial_knowledge(
        self,
        *,
        actor_id: str,
        question_id: str,
        year: int,
    ) -> KnowledgeStateV1:
        q = self._questions[question_id]
        if q.question_kind != QUESTION_KIND or q.prior_probability is None:
            raise ValueError(
                "unresolved-characterization questions require the characterization lane; "
                "no numeric prior may be inferred"
            )
        return KnowledgeStateV1(
            actor_id=actor_id,
            question_id=q.question_id,
            subject_id=q.subject_id,
            location_id=q.location_id,
            probability=q.prior_probability,
            source_id=f"prior:{q.question_id}",
            year=int(year),
            visibility=q.visibility,
        )

    def evaluate(
        self,
        knowledge: KnowledgeStateV1,
        inputs: MissionDecisionInputs,
    ) -> MissionDecisionRecordV1:
        mission = self._missions[inputs.mission_archetype_id]
        decision_model = self._decisions[inputs.mission_archetype_id]
        if knowledge.actor_id != inputs.actor_id:
            raise ValueError("knowledge owner does not match decision actor")
        if knowledge.question_id != mission.target_question_id:
            raise ValueError("knowledge question does not match mission")
        if inputs.access_status not in ACCESS_STATUS:
            raise ValueError("invalid access status")
        if inputs.capability_status not in CAPABILITY_STATUS:
            raise ValueError("invalid capability status")
        if inputs.budget_status not in BUDGET_STATUS:
            raise ValueError("invalid budget status")
        mission_cost = _nonnegative(inputs.mission_cost, "mission cost")
        continuation_cost = _nonnegative(
            inputs.continuation_cost,
            "continuation cost",
        )

        reasons: list[str] = []
        if inputs.access_status != "FEASIBLE":
            reasons.append(f"ACCESS_{inputs.access_status}")
        if inputs.capability_status != "USABLE":
            reasons.append(f"CAPABILITY_{inputs.capability_status}")
        if inputs.budget_status != "KNOWN" or inputs.budget_amount is None:
            reasons.append("BUDGET_UNKNOWN")
        elif inputs.budget_unit != self.package.capital_unit:
            reasons.append("BUDGET_UNIT_MISMATCH")
        elif inputs.budget_amount + 1e-12 < mission_cost:
            reasons.append("MISSION_UNAFFORDABLE")
        if inputs.continuation_unit != self.package.capital_unit:
            reasons.append("FOLLOW_ON_UNIT_MISMATCH")
        if decision_model.success_value.status == "UNKNOWN":
            reasons.append("FOLLOW_ON_VALUE_UNKNOWN")

        expected_value: Optional[float] = None
        action = "WAIT"
        status = "DECLINED"

        if not reasons:
            assert inputs.budget_amount is not None
            assert decision_model.success_value.value is not None
            model = self._models[mission.observation_model_id]
            p = knowledge.probability
            positive_probability = (
                p * model.sensitivity
                + (1.0 - p) * model.false_positive_probability
            )
            posterior_positive = p * model.sensitivity / positive_probability
            negative_probability = 1.0 - positive_probability
            posterior_negative = (
                p * (1.0 - model.sensitivity) / negative_probability
            )
            success_value = decision_model.success_value.value
            follow_on_affordable = (
                inputs.budget_amount + 1e-12
                >= mission_cost + continuation_cost
            )
            after = 0.0
            if follow_on_affordable:
                after = (
                    positive_probability
                    * max(
                        0.0,
                        posterior_positive * success_value - continuation_cost,
                    )
                    + negative_probability
                    * max(
                        0.0,
                        posterior_negative * success_value - continuation_cost,
                    )
                )
            before = (
                max(
                    0.0,
                    p * success_value - continuation_cost,
                )
                if inputs.budget_amount + 1e-12 >= continuation_cost
                else 0.0
            )
            expected_value = after - before - mission_cost
            if expected_value > decision_model.threshold:
                action = "COMMIT_MISSION"
                status = "COMMITTED"
                reasons.append("POSITIVE_EXPECTED_VALUE_OF_INFORMATION")
            else:
                reasons.append("NONPOSITIVE_EXPECTED_VALUE_OF_INFORMATION")

        raw = (
            f"{inputs.actor_id}|{inputs.mission_archetype_id}|"
            f"{inputs.year}|{knowledge.source_id}"
        ).encode()
        decision_id = "md-" + hashlib.sha256(raw).hexdigest()[:16]
        return MissionDecisionRecordV1(
            decision_id=decision_id,
            year=int(inputs.year),
            actor_id=inputs.actor_id,
            mission_archetype_id=inputs.mission_archetype_id,
            question_id=knowledge.question_id,
            target_location_id=mission.destination_location_id,
            action=action,
            status=status,
            expected_value_of_information=expected_value,
            value_unit=self.package.capital_unit,
            rationale_codes=tuple(reasons),
        )

    def mission_record(
        self,
        *,
        actor_id: str,
        mission_archetype_id: str,
        committed_year: int,
        execution_year: int,
        capital_cost: float,
        capital_unit: str,
    ) -> MissionRecordV1:
        mission = self._missions[mission_archetype_id]
        if capital_unit != self.package.capital_unit:
            raise ValueError("mission capital unit mismatch")
        raw = (
            f"{actor_id}|{mission_archetype_id}|{committed_year}|"
            f"{mission.target_question_id}"
        ).encode()
        return MissionRecordV1(
            mission_id="mission-" + hashlib.sha256(raw).hexdigest()[:16],
            mission_archetype_id=mission_archetype_id,
            actor_id=actor_id,
            question_id=mission.target_question_id,
            origin_location_id=mission.origin_location_id,
            destination_location_id=mission.destination_location_id,
            committed_year=int(committed_year),
            execution_year=int(execution_year),
            capital_cost=_nonnegative(capital_cost, "mission capital cost"),
            capital_unit=capital_unit,
            status="COMMITTED",
        )

    def synthetic_observation_for_test(
        self,
        *,
        actor_id: str,
        mission_id: str,
        question_id: str,
        year: int,
        detected: bool,
    ) -> ObservationRecordV1:
        q = self._questions[question_id]
        mission = next(
            x for x in self.package.missions if x.target_question_id == question_id
        )
        model = self._models[mission.observation_model_id]
        return ObservationRecordV1(
            observation_id=f"obs:{mission_id}:{question_id}:{year}",
            mission_id=mission_id,
            actor_id=actor_id,
            question_id=question_id,
            subject_id=q.subject_id,
            location_id=q.location_id,
            year=int(year),
            detected=bool(detected),
            sensitivity=model.sensitivity,
            false_positive_probability=model.false_positive_probability,
            quantity=model.quantity,
            unit=model.unit,
            error_model=model.model_kind,
            visibility=mission.visibility,
        )


class BinaryObservationRuntime:
    """The only V1 lane allowed to accept hidden physical realization."""

    def __init__(self, package: MissionKnowledgePackage, seed: int):
        if type(seed) is not int or seed < 0:
            raise ValueError("seed must be a nonnegative integer")
        self.package = package
        self.seed = seed
        self._questions = {x.question_id: x for x in package.questions}
        self._models = {
            x.observation_model_id: x for x in package.observation_models
        }
        self._missions = {x.mission_archetype_id: x for x in package.missions}

    def keyed_unit(self, *parts: object) -> float:
        payload = json.dumps(
            [self.seed, self.package.package_id, *parts],
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
        return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") / 2**64

    def observe(
        self,
        *,
        mission: MissionRecordV1,
        hidden_present: bool,
        year: int,
    ) -> ObservationRecordV1:
        if type(hidden_present) is not bool:
            raise ValueError("hidden binary realization must be bool")
        archetype = self._missions[mission.mission_archetype_id]
        if archetype.target_question_id != mission.question_id:
            raise ValueError("mission question mismatch")
        q = self._questions[mission.question_id]
        model = self._models[archetype.observation_model_id]
        probability = (
            model.sensitivity
            if hidden_present
            else model.false_positive_probability
        )
        draw = self.keyed_unit(
            "instrument",
            mission.mission_id,
            mission.question_id,
            archetype.observation_model_id,
            int(year),
        )
        detected = draw < probability
        observation_id = (
            "obs-"
            + hashlib.sha256(
                (
                    f"{mission.mission_id}|{mission.question_id}|{year}|"
                    f"{archetype.observation_model_id}"
                ).encode()
            ).hexdigest()[:16]
        )
        return ObservationRecordV1(
            observation_id=observation_id,
            mission_id=mission.mission_id,
            actor_id=mission.actor_id,
            question_id=mission.question_id,
            subject_id=q.subject_id,
            location_id=q.location_id,
            year=int(year),
            detected=detected,
            sensitivity=model.sensitivity,
            false_positive_probability=model.false_positive_probability,
            quantity=model.quantity,
            unit=model.unit,
            error_model=model.model_kind,
            visibility=archetype.visibility,
        )


__all__ = [
    "CONTRACT_VERSION",
    "FORMAT",
    "PACKAGE_STATUS",
    "BinaryObservationRuntime",
    "DecisionValue",
    "KnowledgeQuestion",
    "KnowledgeRuntime",
    "KnowledgeStateV1",
    "MissionArchetype",
    "MissionDecisionInputs",
    "MissionDecisionModel",
    "MissionDecisionRecordV1",
    "MissionKnowledgePackage",
    "MissionKnowledgeRuntime",
    "MissionRecordV1",
    "ObservationModel",
    "ObservationRecordV1",
    "load_mission_knowledge_package",
    "load_mission_knowledge_path",
]
