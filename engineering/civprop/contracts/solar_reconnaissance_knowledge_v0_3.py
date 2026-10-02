"""Pre-GAP14 Solar reconnaissance eligibility from unresolved qualified evidence.

This deliberately does NOT invent Bayesian priors, hidden resource truth, abundance,
or economic value. It only answers whether an unresolved evidence question may enter
an actor-visible reconnaissance opportunity set.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

ADMITTED={"UNKNOWN_AFTER_SEARCH","SUPPORTED_PRESENT_UNQUANTIFIED","SUPPORTED_QUANTIFIED","SUPPORTED_INFERRED_OR_MODELLED"}

@dataclass(frozen=True)
class ReconnaissanceKnowledgeStateV03:
    question_id: str
    body_id: str
    resource_family: str
    evidence_disposition: str
    prior_probability: Optional[float]
    characterization_status: str
    provenance_refs: tuple[str,...]

@dataclass(frozen=True)
class ReconnaissanceEligibilityV03:
    eligible: bool
    rationale_codes: tuple[str,...]


def state_from_coverage_row(row: dict[str,str]) -> ReconnaissanceKnowledgeStateV03:
    disposition=row["coverage_disposition"]
    if disposition not in ADMITTED:
        raise ValueError(f"unsupported evidence disposition: {disposition}")
    return ReconnaissanceKnowledgeStateV03(
        question_id=f"SOLAR_RESOURCE::{row['body_id']}::{row['resource_family']}",
        body_id=row["body_id"], resource_family=row["resource_family"],
        evidence_disposition=disposition, prior_probability=None,
        characterization_status="UNRESOLVED",
        provenance_refs=("dev/solar_civprop_m4b/reports/M4B_COVERAGE_MATRIX.csv",),
    )


def reconnaissance_eligibility(state: ReconnaissanceKnowledgeStateV03, *, nav1_candidate: bool) -> ReconnaissanceEligibilityV03:
    reasons=[]
    if not nav1_candidate: reasons.append("NAV1_NOT_AVAILABLE")
    if state.characterization_status != "UNRESOLVED": reasons.append("ALREADY_CHARACTERIZED")
    if state.prior_probability is not None: reasons.append("UNAUTHORIZED_NUMERIC_PRIOR")
    if reasons: return ReconnaissanceEligibilityV03(False,tuple(reasons))
    return ReconnaissanceEligibilityV03(True,("UNRESOLVED_QUALIFIED_EVIDENCE_QUESTION","NO_NUMERIC_PRIOR_INFERRED"))

@dataclass(frozen=True)
class CharacterizationDecisionV03:
    action: str
    rationale_codes: tuple[str,...]

@dataclass(frozen=True)
class CharacterizationObservationV03:
    question_id: str
    characterization_status: str
    resource_result_status: str
    provenance_refs: tuple[str,...]


def characterization_gate_reasons(*, characterization_status: str, prior_probability, nav1_candidate: bool, capability_usable: bool, budget_known: bool, affordable: bool, exploration_weight) -> tuple[str,...]:
    """Single governed Phase-2 characterization gate used by contract and runtime."""
    reasons=[]
    if not nav1_candidate: reasons.append("NAV1_NOT_AVAILABLE")
    if characterization_status != "UNRESOLVED": reasons.append("ALREADY_CHARACTERIZED")
    if prior_probability is not None: reasons.append("UNAUTHORIZED_NUMERIC_PRIOR")
    if not capability_usable: reasons.append("CAPABILITY_NOT_USABLE")
    if not budget_known: reasons.append("BUDGET_UNKNOWN")
    elif not affordable: reasons.append("MISSION_UNAFFORDABLE")
    if exploration_weight not in {0.25,0.5,0.75}: reasons.append("UNAUTHORIZED_EXPLORATION_WEIGHT")
    return tuple(reasons)

def evaluate_characterization(state: ReconnaissanceKnowledgeStateV03, *, nav1_candidate: bool,
                              capability_usable: bool, budget_known: bool,
                              affordable: bool, exploration_weight: float) -> CharacterizationDecisionV03:
    reasons=characterization_gate_reasons(characterization_status=state.characterization_status,
        prior_probability=state.prior_probability,nav1_candidate=nav1_candidate,
        capability_usable=capability_usable,budget_known=budget_known,affordable=affordable,
        exploration_weight=exploration_weight)
    if reasons: return CharacterizationDecisionV03("WAIT",reasons)
    return CharacterizationDecisionV03("COMMIT_MISSION",("UNRESOLVED_QUALIFIED_EVIDENCE_QUESTION","NO_NUMERIC_PRIOR_INFERRED","AUTHORED_EXPLORATION_PRIORITY"))


def complete_characterization(state: ReconnaissanceKnowledgeStateV03) -> CharacterizationObservationV03:
    # Completion says an observation campaign happened. It does not manufacture a
    # physical resource result where the evidence stack supplies none.
    return CharacterizationObservationV03(
        question_id=state.question_id,
        characterization_status="CHARACTERIZATION_COMPLETED",
        resource_result_status="UNRESOLVED_WITHOUT_AUTHORIZED_OBSERVATION_RESULT",
        provenance_refs=state.provenance_refs+("CIVPROP_MISSION_KNOWLEDGE_V1_1_CHARACTERIZATION",),
    )
