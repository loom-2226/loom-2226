"""Phase 3 Solar mission + claim ontology.

NON_CANON / UNPROMOTED / NOT A BASELINE.

This contract prevents BODY x RESOURCE_FAMILY questions from being treated as
missions. Questions describe uncertainty; claims describe actor assertions;
mission opportunities describe possible evidence-gathering actions; missions
remain committed/executed actions in the runtime ledger.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .mission_knowledge_v1 import (
    CharacterizationKnowledgeStateV1,
    KnowledgeClaimV1,
    KnowledgeQuestion,
)

CLAIM_KINDS = frozenset({"CHARACTERIZATION_RESULT"})
CLAIM_STATUSES = frozenset({"EVIDENCE_AVAILABLE", "INSUFFICIENT_EVIDENCE", "WITHDRAWN"})


@dataclass(frozen=True)
class MissionOpportunityV03:
    opportunity_id: str
    question_id: str
    origin_location_id: str
    destination_location_id: str
    mission_class: str
    service_class: str
    required_tech: tuple[str, ...]
    status: str = "CANDIDATE"
    authority_class: str = "NON_CANON_MISSION_OPPORTUNITY"


def characterization_claim_from_knowledge(
    *,
    knowledge: CharacterizationKnowledgeStateV1,
    question: KnowledgeQuestion,
    year: int,
) -> KnowledgeClaimV1:
    if question.question_kind != "UNRESOLVED_CHARACTERIZATION":
        raise ValueError("characterization claim requires characterization question")
    if knowledge.question_id != question.question_id:
        raise ValueError("knowledge/question mismatch")
    if knowledge.characterization_status != "CHARACTERIZATION_COMPLETED":
        raise ValueError("uncompleted characterization cannot support claim")
    if not knowledge.observation_ids:
        raise ValueError("claim requires observation provenance")
    # Completion does not manufacture a resource result.  The inherited M4-B
    # disposition is evidence context only and never abundance/recoverability/value.
    status = "EVIDENCE_AVAILABLE" if knowledge.evidence_disposition else "INSUFFICIENT_EVIDENCE"
    return KnowledgeClaimV1(
        claim_id=f"claim:{knowledge.actor_id}:{question.question_id}:{year}",
        actor_id=knowledge.actor_id,
        question_id=question.question_id,
        subject_id=question.subject_id,
        location_id=question.location_id,
        claim_kind="CHARACTERIZATION_RESULT",
        claim_status=status,
        evidence_disposition=knowledge.evidence_disposition,
        source_ids=tuple(knowledge.observation_ids),
        year=int(year),
        visibility=knowledge.visibility,
    )
