"""Phase 7 generalized Solar causal vertical slice.

NON_CANON / MACHINERY TEST ONLY. Generalizes the Phase-4 Ceres plumbing to
any unresolved Solar characterization question without asserting transport,
resource truth, jurisdiction, market value, or certification authority.
"""
from dataclasses import dataclass
from .mission_claim_ontology_v0_3 import characterization_claim_from_knowledge
from .mission_knowledge_v1 import CharacterizationKnowledgeStateV1, KnowledgeQuestion
from .ceres_causal_vertical_slice_v0_3 import (
    ActionableDecisionV03, QualificationDecisionV03, financing_gate, qualify_claim
)
from .certification_institutions_v0_3 import CertificationAuthorityV03, may_qualify

@dataclass(frozen=True)
class SolarSliceResultV03:
    location_id: str
    before: ActionableDecisionV03
    knowledge: CharacterizationKnowledgeStateV1
    claim: object
    qualification: QualificationDecisionV03 | None
    after: ActionableDecisionV03
    qualification_gate: str

def run_solar_machinery_slice(*, question: KnowledgeQuestion, actor_id: str,
        certifier_id: str, financier_id: str, observation_id: str, year: int,
        authority: CertificationAuthorityV03 | None, standard_id: str,
        qualified_person: bool, chain_of_custody: bool, auditable_data: bool,
        sampling_sufficient: bool) -> SolarSliceResultV03:
    if question.question_kind != "UNRESOLVED_CHARACTERIZATION":
        raise ValueError("Phase-7 Solar slice requires unresolved characterization")
    before=ActionableDecisionV03(
        f"decision:{financier_id}:pre:{question.question_id}:{year}", financier_id,
        "NONE", "WAIT", ("NO_QUALIFIED_CLAIM",), year)
    knowledge=CharacterizationKnowledgeStateV1(
        actor_id, question.question_id, question.subject_id, question.location_id,
        "CHARACTERIZATION_COMPLETED", observation_id, year,
        observation_ids=(observation_id,),
        evidence_disposition=question.evidence_disposition)
    claim=characterization_claim_from_knowledge(
        knowledge=knowledge, question=question, year=year)
    if authority is None or authority.actor_id != certifier_id or not may_qualify(authority):
        after=financing_gate(actor_id=financier_id,claim=claim,qualification=None,year=year)
        return SolarSliceResultV03(question.location_id,before,knowledge,claim,None,after,
            "NO_AUTHORIZED_CERTIFIER")
    qualification=qualify_claim(
        claim=claim, certifier_id=certifier_id, standard_id=standard_id,
        qualified_person=qualified_person, chain_of_custody=chain_of_custody,
        auditable_data=auditable_data, sampling_sufficient=sampling_sufficient,
        year=year)
    after=financing_gate(
        actor_id=financier_id, claim=claim, qualification=qualification, year=year)
    return SolarSliceResultV03(question.location_id,before,knowledge,claim,qualification,
        after,"AUTHORIZED_CERTIFIER")
