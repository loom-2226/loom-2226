"""Phase 4 non-lunar Ceres causal vertical slice.

NON_CANON / MACHINERY TEST ONLY.  This proves causal plumbing, not Ceres
resource truth, transport feasibility, market value, or a 2026 certification
standard for space resources.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .mission_claim_ontology_v0_3 import characterization_claim_from_knowledge
from .mission_knowledge_v1 import CharacterizationKnowledgeStateV1, KnowledgeQuestion

QUALIFICATION_STATUSES=frozenset({"QUALIFIED","DECLINED"})

@dataclass(frozen=True)
class QualificationDecisionV03:
    qualification_id: str
    certifier_id: str
    claim_id: str
    standard_id: str
    status: str
    rationale_codes: tuple[str,...]
    year: int
    authority_class: str="SIMULATED_QUALIFICATION_DECISION"

@dataclass(frozen=True)
class ActionableDecisionV03:
    decision_id: str
    actor_id: str
    claim_id: str
    action: str
    rationale_codes: tuple[str,...]
    year: int
    authority_class: str="SIMULATED_ACTIONABLE_DECISION"


def qualify_claim(*, claim, certifier_id: str, standard_id: str, qualified_person: bool,
                  chain_of_custody: bool, auditable_data: bool, sampling_sufficient: bool,
                  year: int) -> QualificationDecisionV03:
    reasons=[]
    if claim.claim_status != "EVIDENCE_AVAILABLE": reasons.append("INSUFFICIENT_EVIDENCE")
    if not sampling_sufficient: reasons.append("INSUFFICIENT_SAMPLING")
    if not qualified_person: reasons.append("UNQUALIFIED_PERSON")
    if not chain_of_custody: reasons.append("NO_CHAIN_OF_CUSTODY")
    if not auditable_data: reasons.append("DATA_NOT_AUDITABLE")
    status="DECLINED" if reasons else "QUALIFIED"
    return QualificationDecisionV03(
        qualification_id=f"qual:{certifier_id}:{claim.claim_id}:{year}",certifier_id=certifier_id,
        claim_id=claim.claim_id,standard_id=standard_id,status=status,
        rationale_codes=tuple(reasons) if reasons else ("CLAIM_QUALIFIED_FOR_MACHINERY_TEST",),year=year)


def financing_gate(*, actor_id: str, claim, qualification: Optional[QualificationDecisionV03],
                   year: int) -> ActionableDecisionV03:
    # This is a deliberately binary machinery-test gate, not an NPV model.
    if qualification is None:
        action="WAIT"; reasons=("NO_QUALIFICATION_DECISION",)
    elif qualification.claim_id != claim.claim_id:
        action="WAIT"; reasons=("QUALIFICATION_CLAIM_MISMATCH",)
    elif qualification.status != "QUALIFIED":
        action="WAIT"; reasons=("CLAIM_NOT_QUALIFIED",)+qualification.rationale_codes
    else:
        action="ADVANCE_DUE_DILIGENCE"; reasons=("QUALIFIED_CLAIM_AVAILABLE",)
    return ActionableDecisionV03(f"decision:{actor_id}:{claim.claim_id}:{year}",actor_id,
        claim.claim_id,action,reasons,year)


def run_ceres_machinery_slice(*, question: KnowledgeQuestion, actor_id: str,
                              certifier_id: str, financier_id: str, observation_id: str,
                              year: int, qualified_person: bool, chain_of_custody: bool,
                              auditable_data: bool, sampling_sufficient: bool):
    if question.location_id != "CERES": raise ValueError("Phase-4 slice is Ceres-only")
    before=ActionableDecisionV03(f"decision:{financier_id}:pre:{year}",financier_id,
        "NONE","WAIT",("NO_QUALIFIED_CLAIM",),year)
    knowledge=CharacterizationKnowledgeStateV1(actor_id,question.question_id,question.subject_id,
        question.location_id,"CHARACTERIZATION_COMPLETED",observation_id,year,
        observation_ids=(observation_id,),evidence_disposition=question.evidence_disposition)
    claim=characterization_claim_from_knowledge(knowledge=knowledge,question=question,year=year)
    qualification=qualify_claim(claim=claim,certifier_id=certifier_id,
        standard_id="AUTHORED_PHASE4_SPACE_RESOURCE_TEST_STANDARD",qualified_person=qualified_person,
        chain_of_custody=chain_of_custody,auditable_data=auditable_data,
        sampling_sufficient=sampling_sufficient,year=year)
    after=financing_gate(actor_id=financier_id,claim=claim,qualification=qualification,year=year)
    return before,knowledge,claim,qualification,after
