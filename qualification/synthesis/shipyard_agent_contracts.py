from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Mapping, Sequence, Tuple


CONTRACT_VERSION = "LOOM_COMPUTATIONAL_SHIPYARD_AGENT_CONTRACTS_v0.1"


class AgentContractError(ValueError):
    """Fail-closed error for malformed designer/critic exchanges."""


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AgentContractError(f"{label} must be a non-empty string")
    return value.strip()


def _unique_text(values: Sequence[str], label: str) -> Tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise AgentContractError(f"{label} must be a sequence, not a string")
    cleaned = tuple(_text(v, label) for v in values)
    if len(set(cleaned)) != len(cleaned):
        raise AgentContractError(f"{label} must contain unique values")
    return cleaned


@dataclass(frozen=True)
class DesignMutation:
    mutation_id: str
    operation: str
    target: str
    value_json: str
    rationale: str
    evidence_refs: Tuple[str, ...] = ()


@dataclass(frozen=True)
class DesignProposal:
    proposal_id: str
    parent_candidate_id: str
    requirements_hash: str
    institution_context_hash: str
    architecture_family: str
    mutations: Tuple[DesignMutation, ...]
    experiment_question: str
    proposer_id: str
    proposer_model: str
    authority_claim: str = "PROPOSAL_ONLY"


@dataclass(frozen=True)
class CritiqueIssue:
    issue_id: str
    category: str
    severity: str
    claim: str
    evidence_refs: Tuple[str, ...]
    proposed_experiment: str
    authority_claim: str = "CRITIQUE_ONLY"


@dataclass(frozen=True)
class DesignCritique:
    critique_id: str
    candidate_id: str
    evaluation_hash: str
    institution_context_hash: str
    issues: Tuple[CritiqueIssue, ...]
    critic_id: str
    critic_model: str
    overall_recommendation: str
    authority_claim: str = "CRITIQUE_ONLY"


@dataclass(frozen=True)
class ShipyardInstitutionContext:
    institution_id: str
    context_date: str
    progenitor_cultures: Tuple[str, ...]
    engineering_lineage: Tuple[str, ...]
    design_doctrine: Tuple[str, ...]
    aesthetic_principles: Tuple[str, ...]
    manufacturing_capabilities: Tuple[str, ...]
    material_constraints: Tuple[str, ...]
    economic_constraints: Tuple[str, ...]
    historical_design_refs: Tuple[str, ...]
    provenance_refs: Tuple[str, ...]
    authority_status: str


def validate_institution_context(ctx: ShipyardInstitutionContext) -> None:
    _text(ctx.institution_id, "institution_id")
    _text(ctx.context_date, "context_date")
    _text(ctx.authority_status, "authority_status")
    for field in (
        "progenitor_cultures", "engineering_lineage", "design_doctrine",
        "aesthetic_principles", "manufacturing_capabilities", "material_constraints",
        "economic_constraints", "historical_design_refs", "provenance_refs",
    ):
        _unique_text(getattr(ctx, field), field)


def validate_proposal(row: DesignProposal) -> None:
    for value, label in (
        (row.proposal_id, "proposal_id"), (row.parent_candidate_id, "parent_candidate_id"),
        (row.requirements_hash, "requirements_hash"),
        (row.institution_context_hash, "institution_context_hash"),
        (row.architecture_family, "architecture_family"),
        (row.experiment_question, "experiment_question"), (row.proposer_id, "proposer_id"),
        (row.proposer_model, "proposer_model"), (row.authority_claim, "authority_claim"),
    ):
        _text(value, label)
    if row.authority_claim != "PROPOSAL_ONLY":
        raise AgentContractError("Designer output may not claim engineering authority")
    if not row.mutations:
        raise AgentContractError("DesignProposal requires at least one mutation")
    mutation_ids = set()
    for m in row.mutations:
        for value, label in ((m.mutation_id,"mutation_id"),(m.operation,"operation"),(m.target,"target"),
                             (m.value_json,"value_json"),(m.rationale,"rationale")):
            _text(value, label)
        try:
            json.loads(m.value_json)
        except json.JSONDecodeError as exc:
            raise AgentContractError(f"mutation {m.mutation_id} value_json is invalid JSON") from exc
        _unique_text(m.evidence_refs, "mutation evidence_refs")
        if m.mutation_id in mutation_ids:
            raise AgentContractError(f"duplicate mutation_id {m.mutation_id}")
        mutation_ids.add(m.mutation_id)


def validate_critique(row: DesignCritique) -> None:
    for value, label in (
        (row.critique_id,"critique_id"),(row.candidate_id,"candidate_id"),
        (row.evaluation_hash,"evaluation_hash"),(row.institution_context_hash,"institution_context_hash"),
        (row.critic_id,"critic_id"),(row.critic_model,"critic_model"),
        (row.overall_recommendation,"overall_recommendation"),(row.authority_claim,"authority_claim"),
    ):
        _text(value, label)
    if row.authority_claim != "CRITIQUE_ONLY":
        raise AgentContractError("Critic output may not claim engineering authority")
    issue_ids = set()
    for issue in row.issues:
        for value, label in ((issue.issue_id,"issue_id"),(issue.category,"category"),(issue.severity,"severity"),
                             (issue.claim,"claim"),(issue.proposed_experiment,"proposed_experiment"),
                             (issue.authority_claim,"issue authority_claim")):
            _text(value, label)
        if issue.authority_claim != "CRITIQUE_ONLY":
            raise AgentContractError("Critique issue may not claim engineering authority")
        _unique_text(issue.evidence_refs, "critique evidence_refs")
        if issue.issue_id in issue_ids:
            raise AgentContractError(f"duplicate issue_id {issue.issue_id}")
        issue_ids.add(issue.issue_id)


def canonical_json(row: object) -> str:
    return json.dumps(asdict(row), sort_keys=True, separators=(",", ":"), allow_nan=False)


def content_hash(row: object) -> str:
    return hashlib.sha256(canonical_json(row).encode("utf-8")).hexdigest()
