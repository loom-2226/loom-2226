from __future__ import annotations

import dataclasses
import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence, Tuple

from architectural_review import (
    ARCHITECTURAL_REVIEW_AUTHORITY,
    DesignReviewFinding,
    DesignReviewReport,
    content_hash as architectural_hash,
    functional_expressionism_doctrine,
    validate_report,
)
from critic_evidence_interface import architectural_review_to_design_critique
from proposal_mutation_executor import ALLOWED_OPERATIONS, execute_proposal
from shipyard_agent_contracts import (
    DesignMutation,
    DesignProposal,
    content_hash as agent_hash,
    validate_proposal,
)
from wayfarer_s1_adapter import evaluate_candidate
from wayfarer_s1_solver import DEFAULT_SEED, solve
from wayfarer_shipyard_vertical_slice import (
    INSTITUTION_CONTEXT_HASH,
    REQUIREMENTS_HASH,
    _evidence_for,
    _evaluation_hash,
)

EXPERIMENT_VERSION = "LOOM_MODEL_PERMUTATION_EXPERIMENT_v0.1"
STATUS = ("ENGINEERING_RESEARCH", "NON_CANON", "NON_PRODUCTION")
DESIGNER_PACKET_AUTHORITY = "MODEL_INPUT_ONLY"
CRITIC_PACKET_AUTHORITY = "MODEL_INPUT_ONLY"
TRACE_AUTHORITY = "MODEL_EXPERIMENT_TRACE_ONLY"


class ModelPermutationError(ValueError):
    """Fail-closed error for model packets, raw responses, or trace records."""


def _canonical(value: object) -> str:
    if dataclasses.is_dataclass(value):
        value = asdict(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ModelPermutationError(f"{label} must be a non-empty string")
    return value.strip()


def _mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ModelPermutationError(f"{label} must be a JSON object")
    return value


def _exact_keys(row: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(row)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ModelPermutationError(f"{label} keys mismatch; missing={missing}; extra={extra}")


def _strict_json(raw: str, label: str) -> Mapping[str, Any]:
    _text(raw, label)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ModelPermutationError(f"{label} is not valid JSON") from exc
    return _mapping(parsed, label)


@dataclass(frozen=True)
class ModelIdentity:
    model_id: str
    provider: str
    configuration: str


@dataclass(frozen=True)
class CandidateInstanceFact:
    instance_id: str
    component_type_id: str
    active: bool
    translation_m: Tuple[float, float, float]


@dataclass(frozen=True)
class DesignerInputPacket:
    experiment_version: str
    parent_candidate_id: str
    seed: int
    requirements_hash: str
    institution_context_hash: str
    architecture_family: str
    allowed_operations: Tuple[str, ...]
    candidate_instances: Tuple[CandidateInstanceFact, ...]
    hard_rule: str
    response_schema: str
    authority_status: str
    packet_hash: str


@dataclass(frozen=True)
class CriticInputPacket:
    experiment_version: str
    candidate_id: str
    evaluation_hash: str
    evidence_package_hash: str
    doctrine_hash: str
    criterion_ids: Tuple[str, ...]
    evidence_json: str
    doctrine_json: str
    hard_rule: str
    response_schema: str
    authority_status: str
    packet_hash: str


@dataclass(frozen=True)
class ModelRunTrace:
    experiment_version: str
    role: str
    model_identity: ModelIdentity
    prompt_hash: str
    input_packet_hash: str
    raw_response_hash: str
    parsed_output_hash: str
    parent_candidate_id: str
    child_candidate_id: str
    evaluation_hash: str
    evidence_package_hash: str
    authority_status: str = TRACE_AUTHORITY
    flight_dynamics_authority: bool = False
    canon_changed: bool = False
    production_shipclasses_changed: bool = False


def _packet_hash(payload: Mapping[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("packet_hash", None)
    return _sha(_canonical(clean))


def build_designer_packet(seed: int = DEFAULT_SEED) -> DesignerInputPacket:
    solved = solve(seed)
    candidate = solved.candidate
    instances = tuple(
        CandidateInstanceFact(
            instance_id=row.instance_id,
            component_type_id=row.component_type_id,
            active=bool(row.active),
            translation_m=tuple(float(v) for v in row.transform.translation_m),
        )
        for row in sorted(candidate.component_instances, key=lambda row: row.instance_id)
    )
    payload = {
        "experiment_version": EXPERIMENT_VERSION,
        "parent_candidate_id": candidate.candidate_id,
        "seed": int(seed),
        "requirements_hash": REQUIREMENTS_HASH,
        "institution_context_hash": INSTITUTION_CONTEXT_HASH,
        "architecture_family": "WAYFARER_COURIER_BASELINE",
        "allowed_operations": tuple(sorted(ALLOWED_OPERATIONS)),
        "candidate_instances": tuple(asdict(row) for row in instances),
        "hard_rule": (
            "Propose only. Do not claim engineering PASS/FAIL, flight-dynamics authority, canon change, "
            "production approval, or closure of OPEN items. Use only the admitted operations and exact instance IDs."
        ),
        "response_schema": (
            "Strict JSON DesignProposal: proposal_id,parent_candidate_id,requirements_hash,institution_context_hash,"
            "architecture_family,mutations[],experiment_question,proposer_id,proposer_model,authority_claim. "
            "Each mutation requires mutation_id,operation,target,value_json,rationale,evidence_refs[]."
        ),
        "authority_status": DESIGNER_PACKET_AUTHORITY,
    }
    return DesignerInputPacket(
        experiment_version=payload["experiment_version"],
        parent_candidate_id=payload["parent_candidate_id"],
        seed=payload["seed"],
        requirements_hash=payload["requirements_hash"],
        institution_context_hash=payload["institution_context_hash"],
        architecture_family=payload["architecture_family"],
        allowed_operations=payload["allowed_operations"],
        candidate_instances=instances,
        hard_rule=payload["hard_rule"],
        response_schema=payload["response_schema"],
        authority_status=payload["authority_status"],
        packet_hash=_packet_hash(payload),
    )


def designer_prompt(packet: DesignerInputPacket) -> str:
    if packet.authority_status != DESIGNER_PACKET_AUTHORITY:
        raise ModelPermutationError("designer packet may not claim engineering authority")
    return (
        "ROLE: LOOM Computational Shipyard Designer.\n"
        "Return exactly one JSON object and no prose.\n"
        f"PACKET_SHA256: {packet.packet_hash}\n"
        f"PACKET: {_canonical(packet)}\n"
        "Choose a modest, evidence-seeking experiment. Do not optimize by assertion."
    )


def parse_designer_response(raw: str, packet: DesignerInputPacket) -> DesignProposal:
    row = _strict_json(raw, "designer response")
    _exact_keys(row, {
        "proposal_id", "parent_candidate_id", "requirements_hash", "institution_context_hash",
        "architecture_family", "mutations", "experiment_question", "proposer_id", "proposer_model",
        "authority_claim",
    }, "designer response")
    if row["parent_candidate_id"] != packet.parent_candidate_id:
        raise ModelPermutationError("designer response parent_candidate_id mismatch")
    if row["requirements_hash"] != packet.requirements_hash:
        raise ModelPermutationError("designer response requirements_hash mismatch")
    if row["institution_context_hash"] != packet.institution_context_hash:
        raise ModelPermutationError("designer response institution_context_hash mismatch")
    if row["architecture_family"] != packet.architecture_family:
        raise ModelPermutationError("designer response architecture_family mismatch")
    mutations_raw = row["mutations"]
    if not isinstance(mutations_raw, list) or not mutations_raw:
        raise ModelPermutationError("designer response mutations must be a non-empty JSON array")
    known_targets = {item.instance_id for item in packet.candidate_instances}
    mutations = []
    for i, item in enumerate(mutations_raw, start=1):
        m = _mapping(item, f"designer mutation {i}")
        _exact_keys(m, {"mutation_id", "operation", "target", "value_json", "rationale", "evidence_refs"}, f"designer mutation {i}")
        if m["operation"] not in packet.allowed_operations:
            raise ModelPermutationError(f"designer mutation {i} uses unadmitted operation {m['operation']}")
        if m["target"] not in known_targets:
            raise ModelPermutationError(f"designer mutation {i} references unknown target {m['target']}")
        refs = m["evidence_refs"]
        if not isinstance(refs, list):
            raise ModelPermutationError(f"designer mutation {i} evidence_refs must be an array")
        mutations.append(DesignMutation(
            mutation_id=_text(m["mutation_id"], "mutation_id"),
            operation=_text(m["operation"], "operation"),
            target=_text(m["target"], "target"),
            value_json=_text(m["value_json"], "value_json"),
            rationale=_text(m["rationale"], "rationale"),
            evidence_refs=tuple(_text(v, "evidence_ref") for v in refs),
        ))
    proposal = DesignProposal(
        proposal_id=_text(row["proposal_id"], "proposal_id"),
        parent_candidate_id=row["parent_candidate_id"],
        requirements_hash=row["requirements_hash"],
        institution_context_hash=row["institution_context_hash"],
        architecture_family=row["architecture_family"],
        mutations=tuple(mutations),
        experiment_question=_text(row["experiment_question"], "experiment_question"),
        proposer_id=_text(row["proposer_id"], "proposer_id"),
        proposer_model=_text(row["proposer_model"], "proposer_model"),
        authority_claim=_text(row["authority_claim"], "authority_claim"),
    )
    validate_proposal(proposal)
    return proposal


def execute_designer_response(raw: str, *, seed: int = DEFAULT_SEED):
    packet = build_designer_packet(seed)
    parent = solve(seed).candidate
    proposal = parse_designer_response(raw, packet)
    child, execution = execute_proposal(parent, proposal)
    child_eval = evaluate_candidate(child)
    evidence = _evidence_for(child, child_eval)
    return packet, proposal, child, execution, child_eval, evidence


def build_critic_packet(*, child, child_eval, evidence) -> CriticInputPacket:
    doctrine = functional_expressionism_doctrine()
    payload = {
        "experiment_version": EXPERIMENT_VERSION,
        "candidate_id": child.candidate_id,
        "evaluation_hash": _evaluation_hash(child_eval),
        "evidence_package_hash": evidence.package_hash,
        "doctrine_hash": architectural_hash(doctrine),
        "criterion_ids": tuple(row.criterion_id for row in doctrine.criteria),
        "evidence_json": _canonical(evidence),
        "doctrine_json": _canonical(doctrine),
        "hard_rule": (
            "Critique only what supplied evidence supports. Numerical evidence is not visual evidence. Do not claim "
            "physical PASS/FAIL authority, flight-dynamics authority, canon change, production approval, or closure of OPEN items."
        ),
        "response_schema": (
            "Strict JSON DesignReviewReport: report_id,candidate_id,evidence_package_hash,doctrine_hash,reviewer_id,"
            "reviewer_model,findings[],overall_recommendation,architectural_summary,physical_feasibility_claimed,"
            "flight_dynamics_authority_claimed,canon_change_claimed,production_shipclass_change_claimed,authority_status. "
            "Each finding requires finding_id,criterion_id,severity,claim,evidence_refs[],experiment_request,authority_status."
        ),
        "authority_status": CRITIC_PACKET_AUTHORITY,
    }
    return CriticInputPacket(
        experiment_version=payload["experiment_version"],
        candidate_id=payload["candidate_id"],
        evaluation_hash=payload["evaluation_hash"],
        evidence_package_hash=payload["evidence_package_hash"],
        doctrine_hash=payload["doctrine_hash"],
        criterion_ids=payload["criterion_ids"],
        evidence_json=payload["evidence_json"],
        doctrine_json=payload["doctrine_json"],
        hard_rule=payload["hard_rule"],
        response_schema=payload["response_schema"],
        authority_status=payload["authority_status"],
        packet_hash=_packet_hash(payload),
    )


def critic_prompt(packet: CriticInputPacket) -> str:
    if packet.authority_status != CRITIC_PACKET_AUTHORITY:
        raise ModelPermutationError("critic packet may not claim engineering authority")
    return (
        "ROLE: SOL, LOOM architectural critic.\n"
        "Return exactly one JSON object and no prose.\n"
        f"PACKET_SHA256: {packet.packet_hash}\n"
        f"PACKET: {_canonical(packet)}\n"
        "If evidence needed for a criterion is absent, say so and request the smallest useful experiment."
    )


def parse_critic_response(raw: str, packet: CriticInputPacket) -> DesignReviewReport:
    row = _strict_json(raw, "critic response")
    _exact_keys(row, {
        "report_id", "candidate_id", "evidence_package_hash", "doctrine_hash", "reviewer_id", "reviewer_model",
        "findings", "overall_recommendation", "architectural_summary", "physical_feasibility_claimed",
        "flight_dynamics_authority_claimed", "canon_change_claimed", "production_shipclass_change_claimed",
        "authority_status",
    }, "critic response")
    if row["candidate_id"] != packet.candidate_id:
        raise ModelPermutationError("critic response candidate_id mismatch")
    if row["evidence_package_hash"] != packet.evidence_package_hash:
        raise ModelPermutationError("critic response evidence_package_hash mismatch")
    if row["doctrine_hash"] != packet.doctrine_hash:
        raise ModelPermutationError("critic response doctrine_hash mismatch")
    findings_raw = row["findings"]
    if not isinstance(findings_raw, list):
        raise ModelPermutationError("critic findings must be a JSON array")
    findings = []
    for i, item in enumerate(findings_raw, start=1):
        f = _mapping(item, f"critic finding {i}")
        _exact_keys(f, {"finding_id", "criterion_id", "severity", "claim", "evidence_refs", "experiment_request", "authority_status"}, f"critic finding {i}")
        if f["criterion_id"] not in packet.criterion_ids:
            raise ModelPermutationError(f"critic finding {i} references unknown criterion {f['criterion_id']}")
        refs = f["evidence_refs"]
        if not isinstance(refs, list):
            raise ModelPermutationError(f"critic finding {i} evidence_refs must be an array")
        findings.append(DesignReviewFinding(
            finding_id=_text(f["finding_id"], "finding_id"),
            criterion_id=_text(f["criterion_id"], "criterion_id"),
            severity=_text(f["severity"], "severity"),
            claim=_text(f["claim"], "claim"),
            evidence_refs=tuple(_text(v, "evidence_ref") for v in refs),
            experiment_request=_text(f["experiment_request"], "experiment_request"),
            authority_status=_text(f["authority_status"], "finding authority_status"),
        ))
    report = DesignReviewReport(
        report_id=_text(row["report_id"], "report_id"),
        candidate_id=row["candidate_id"],
        evidence_package_hash=row["evidence_package_hash"],
        doctrine_hash=row["doctrine_hash"],
        reviewer_id=_text(row["reviewer_id"], "reviewer_id"),
        reviewer_model=_text(row["reviewer_model"], "reviewer_model"),
        findings=tuple(findings),
        overall_recommendation=_text(row["overall_recommendation"], "overall_recommendation"),
        architectural_summary=_text(row["architectural_summary"], "architectural_summary"),
        physical_feasibility_claimed=row["physical_feasibility_claimed"],
        flight_dynamics_authority_claimed=row["flight_dynamics_authority_claimed"],
        canon_change_claimed=row["canon_change_claimed"],
        production_shipclass_change_claimed=row["production_shipclass_change_claimed"],
        authority_status=_text(row["authority_status"], "authority_status"),
    )
    for label in (
        "physical_feasibility_claimed", "flight_dynamics_authority_claimed",
        "canon_change_claimed", "production_shipclass_change_claimed",
    ):
        if not isinstance(getattr(report, label), bool):
            raise ModelPermutationError(f"{label} must be a JSON boolean")
    doctrine = functional_expressionism_doctrine()
    validate_report(report, doctrine)
    return report


def execute_critic_response(raw: str, *, child, child_eval, evidence):
    packet = build_critic_packet(child=child, child_eval=child_eval, evidence=evidence)
    report = parse_critic_response(raw, packet)
    doctrine = functional_expressionism_doctrine()
    critique = architectural_review_to_design_critique(evidence=evidence, report=report, doctrine=doctrine)
    return packet, report, critique


def build_trace(
    *,
    role: str,
    identity: ModelIdentity,
    prompt: str,
    input_packet_hash: str,
    raw_response: str,
    parsed_output: object,
    parent_candidate_id: str,
    child_candidate_id: str,
    evaluation_hash: str,
    evidence_package_hash: str,
) -> ModelRunTrace:
    role = _text(role, "role")
    if role not in {"DESIGNER", "CRITIC"}:
        raise ModelPermutationError("role must be DESIGNER or CRITIC")
    for value, label in ((identity.model_id, "model_id"), (identity.provider, "provider"), (identity.configuration, "configuration")):
        _text(value, label)
    return ModelRunTrace(
        experiment_version=EXPERIMENT_VERSION,
        role=role,
        model_identity=identity,
        prompt_hash=_sha(prompt),
        input_packet_hash=_text(input_packet_hash, "input_packet_hash"),
        raw_response_hash=_sha(raw_response),
        parsed_output_hash=(agent_hash(parsed_output) if isinstance(parsed_output, DesignProposal) else architectural_hash(parsed_output)),
        parent_candidate_id=_text(parent_candidate_id, "parent_candidate_id"),
        child_candidate_id=_text(child_candidate_id, "child_candidate_id"),
        evaluation_hash=_text(evaluation_hash, "evaluation_hash"),
        evidence_package_hash=_text(evidence_package_hash, "evidence_package_hash"),
    )
