from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from typing import Iterable, Tuple

from physical_design_core import (
    CandidateDesign,
    PhysicalComponentInstance,
    PhysicalDesignError,
    Transform,
    validate_transform,
)
from shipyard_agent_contracts import DesignMutation, DesignProposal, canonical_json, validate_proposal


EXECUTOR_VERSION = "LOOM_PROPOSAL_MUTATION_EXECUTOR_v0.1"
EXECUTION_AUTHORITY = "CANDIDATE_DERIVATION_ONLY"

ALLOWED_OPERATIONS = (
    "SET_INSTANCE_TRANSLATION",
    "SET_INSTANCE_ACTIVE",
)


class MutationExecutionError(PhysicalDesignError):
    """Fail-closed error for unsupported or unsafe proposal execution."""


@dataclass(frozen=True)
class AppliedMutation:
    mutation_id: str
    operation: str
    target: str
    before_json: str
    after_json: str
    rationale: str
    evidence_refs: Tuple[str, ...]


@dataclass(frozen=True)
class MutationExecutionRecord:
    executor_version: str
    proposal_id: str
    proposal_hash: str
    parent_candidate_id: str
    child_candidate_id: str
    applied_mutations: Tuple[AppliedMutation, ...]
    authority_status: str = EXECUTION_AUTHORITY
    flight_dynamics_authority: bool = False
    canon_changed: bool = False
    production_shipclasses_changed: bool = False


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _child_candidate_id(parent_candidate_id: str, proposal_hash: str, applied: Iterable[AppliedMutation]) -> str:
    payload = {
        "executor_version": EXECUTOR_VERSION,
        "parent_candidate_id": parent_candidate_id,
        "proposal_hash": proposal_hash,
        "applied_mutations": [
            {
                "mutation_id": row.mutation_id,
                "operation": row.operation,
                "target": row.target,
                "before_json": row.before_json,
                "after_json": row.after_json,
                "evidence_refs": list(row.evidence_refs),
            }
            for row in applied
        ],
    }
    digest = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()[:20].upper()
    return f"CAND-MUT-{digest}"


def _instance_index(candidate: CandidateDesign, target: str) -> int:
    matches = [i for i, row in enumerate(candidate.component_instances) if row.instance_id == target]
    if len(matches) != 1:
        if not matches:
            raise MutationExecutionError(f"unknown component instance target {target}")
        raise MutationExecutionError(f"ambiguous component instance target {target}")
    return matches[0]


def _apply_one(candidate: CandidateDesign, mutation: DesignMutation) -> tuple[CandidateDesign, AppliedMutation]:
    if mutation.operation not in ALLOWED_OPERATIONS:
        raise MutationExecutionError(f"unsupported mutation operation {mutation.operation}")

    index = _instance_index(candidate, mutation.target)
    instances = list(candidate.component_instances)
    original = instances[index]
    value = json.loads(mutation.value_json)

    if mutation.operation == "SET_INSTANCE_TRANSLATION":
        if not isinstance(value, dict) or set(value) != {"translation_m"}:
            raise MutationExecutionError("SET_INSTANCE_TRANSLATION requires exactly {'translation_m': [x,y,z]}")
        vector = value["translation_m"]
        if not isinstance(vector, list) or len(vector) != 3:
            raise MutationExecutionError("translation_m must be a three-element JSON array")
        try:
            translated = tuple(float(v) for v in vector)
        except (TypeError, ValueError) as exc:
            raise MutationExecutionError("translation_m values must be numeric") from exc
        transform = Transform(
            translation_m=translated,  # type: ignore[arg-type]
            quaternion_wxyz=original.transform.quaternion_wxyz,
        )
        validate_transform(transform)
        replacement = replace(original, transform=transform)
        before = {"translation_m": list(original.transform.translation_m)}
        after = {"translation_m": list(replacement.transform.translation_m)}
    else:
        if type(value) is not bool:
            raise MutationExecutionError("SET_INSTANCE_ACTIVE requires a JSON boolean")
        replacement = replace(original, active=value)
        before = {"active": bool(original.active)}
        after = {"active": bool(replacement.active)}

    instances[index] = replacement
    next_candidate = replace(candidate, component_instances=tuple(instances))
    applied = AppliedMutation(
        mutation_id=mutation.mutation_id,
        operation=mutation.operation,
        target=mutation.target,
        before_json=_canonical(before),
        after_json=_canonical(after),
        rationale=mutation.rationale,
        evidence_refs=tuple(sorted(mutation.evidence_refs)),
    )
    return next_candidate, applied


def execute_proposal(parent: CandidateDesign, proposal: DesignProposal) -> tuple[CandidateDesign, MutationExecutionRecord]:
    """Apply admitted proposal mutations to the existing deterministic CandidateDesign type.

    This function deliberately does not evaluate physics. The returned candidate must be passed
    through the existing deterministic engineering evaluator/search machinery after mutation.
    """
    validate_proposal(proposal)
    if proposal.parent_candidate_id != parent.candidate_id:
        raise MutationExecutionError("proposal parent_candidate_id does not match supplied candidate")

    working = parent
    applied_rows = []
    for mutation in proposal.mutations:
        working, applied = _apply_one(working, mutation)
        applied_rows.append(applied)

    proposal_hash = hashlib.sha256(canonical_json(proposal).encode("utf-8")).hexdigest()
    child_id = _child_candidate_id(parent.candidate_id, proposal_hash, applied_rows)
    provenance = dict(working.provenance_map)
    provenance[f"proposal:{proposal.proposal_id}"] = proposal_hash
    for row in applied_rows:
        provenance[f"mutation:{row.mutation_id}"] = row.rationale

    child = replace(
        working,
        candidate_id=child_id,
        provenance_map=provenance,
    )
    record = MutationExecutionRecord(
        executor_version=EXECUTOR_VERSION,
        proposal_id=proposal.proposal_id,
        proposal_hash=proposal_hash,
        parent_candidate_id=parent.candidate_id,
        child_candidate_id=child_id,
        applied_mutations=tuple(applied_rows),
    )
    return child, record
