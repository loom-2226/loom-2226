from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Tuple
from hashlib import sha256

from .policy import DecisionSnapshot, FactState

D=Decimal


def region_study_activity_id(project_id: str) -> str:
    """Stable per-project identity for Build 7's existing REGION study."""
    return 'BUILD7_REGION_STUDY:'+sha256(str(project_id).encode()).hexdigest()[:20]


def region_study_plan_id(project_id: str) -> str:
    """Stable per-project identity for its existing REGION study plan."""
    return 'BUILD7_REGION_STUDY_PLAN:'+sha256(str(project_id).encode()).hexdigest()[:20]


class ProjectStudyMaturity(str,Enum):
    SCREENED='SCREENED'
    REMOTE_CHARACTERIZED='REMOTE_CHARACTERIZED'
    SURFACE_OR_SAMPLE_CHARACTERIZED='SURFACE_OR_SAMPLE_CHARACTERIZED'
    RESOURCE_ASSESSMENT='RESOURCE_ASSESSMENT'
    CONCEPT_SCOPING='CONCEPT_SCOPING'
    PREFEASIBILITY='PREFEASIBILITY'
    FEASIBILITY='FEASIBILITY'
    DEVELOPMENT_READY='DEVELOPMENT_READY'


MATURITY_ORDER=(
    ProjectStudyMaturity.SCREENED,
    ProjectStudyMaturity.REMOTE_CHARACTERIZED,
    ProjectStudyMaturity.SURFACE_OR_SAMPLE_CHARACTERIZED,
    ProjectStudyMaturity.RESOURCE_ASSESSMENT,
    ProjectStudyMaturity.CONCEPT_SCOPING,
    ProjectStudyMaturity.PREFEASIBILITY,
    ProjectStudyMaturity.FEASIBILITY,
    ProjectStudyMaturity.DEVELOPMENT_READY,
)
MATURITY_INDEX={x:i for i,x in enumerate(MATURITY_ORDER)}


class ProjectStudyResultStanding(str,Enum):
    SUPPORTS_ADVANCE='SUPPORTS_ADVANCE'
    INSUFFICIENT='INSUFFICIENT'
    NEGATIVE='NEGATIVE'


class ProjectStudyReviewOutcome(str,Enum):
    ADVANCE='ADVANCE'
    DEFER='DEFER'
    ABANDON='ABANDON'
    BLOCKED_UNKNOWN='BLOCKED_UNKNOWN'


class ProjectStudyReviewReasonCode(str,Enum):
    SUPPORTS_DECLARED_ADVANCE='SUPPORTS_DECLARED_ADVANCE'
    INSUFFICIENT_EVIDENCE='INSUFFICIENT_EVIDENCE'
    NEGATIVE_EVIDENCE='NEGATIVE_EVIDENCE'
    PROJECT_OR_CAPABILITY_BLOCK='PROJECT_OR_CAPABILITY_BLOCK'
    BLOCKED_REQUIRED_INPUT_UNKNOWN='BLOCKED_REQUIRED_INPUT_UNKNOWN'


@dataclass
class ProjectStudyState:
    project_id: str
    maturity: ProjectStudyMaturity=ProjectStudyMaturity.SCREENED
    last_review_decision_id: str=''
    state_version: str='BUILD6B_PROJECT_STUDY_STATE_V0_1'

    def validate(self):
        if not self.project_id:
            raise ValueError('project study state project missing')
        ProjectStudyMaturity(self.maturity)
        return self


@dataclass(frozen=True)
class ProjectStudyPlan:
    id: str
    activity_id: str
    project_id: str
    required_maturity: ProjectStudyMaturity
    next_maturity: ProjectStudyMaturity
    supplier_account_id: str
    result_type: str
    plan_version: str='BUILD6B_PROJECT_STUDY_PLAN_V0_1'

    def validate(self):
        if not self.id or not self.activity_id or not self.project_id or not self.supplier_account_id or not self.result_type:
            raise ValueError('project study plan identity incomplete')
        required=ProjectStudyMaturity(self.required_maturity)
        nxt=ProjectStudyMaturity(self.next_maturity)
        if MATURITY_INDEX[nxt]!=MATURITY_INDEX[required]+1:
            raise ValueError('project study plan must advance exactly one maturity edge')
        return self


@dataclass(frozen=True)
class ProjectActivityExpenseRecord:
    activity_id: str
    project_id: str
    actor_id: str
    amount: D
    spent_at: D
    investment_transaction_id: str
    exploration_transaction_id: str
    wip_asset_id: str
    record_version: str='BUILD6B_PROJECT_ACTIVITY_EXPENSE_V0_1'

    def validate(self):
        if not self.activity_id or not self.project_id or not self.actor_id:
            raise ValueError('project activity expense identity incomplete')
        if D(self.amount)<0 or D(self.spent_at)<0:
            raise ValueError('project activity expense amount/time invalid')
        if not self.investment_transaction_id or not self.exploration_transaction_id or not self.wip_asset_id:
            raise ValueError('project activity expense lineage incomplete')
        return self


@dataclass(frozen=True)
class ProjectStudyResultRecord:
    activity_id: str
    plan_id: str
    project_id: str
    result_ref: str
    standing: ProjectStudyResultStanding
    completed_at: D
    knowledge_asset_id: str
    record_version: str='BUILD6B_PROJECT_STUDY_RESULT_V0_1'

    def validate(self):
        if not self.activity_id or not self.plan_id or not self.project_id or not self.result_ref or not self.knowledge_asset_id:
            raise ValueError('project study result identity incomplete')
        ProjectStudyResultStanding(self.standing)
        if D(self.completed_at)<0:
            raise ValueError('project study result time invalid')
        return self


@dataclass(frozen=True)
class ProjectStudyReviewRequest:
    id: str
    project_id: str
    activity_id: str
    result_ref: str
    required_fact_keys: Tuple[str,...]
    request_version: str='BUILD6B_PROJECT_STUDY_REVIEW_REQUEST_V0_1'

    def validate_protocol(self):
        if not self.id or not self.project_id or not self.activity_id or not self.result_ref:
            raise ValueError('study review request identity incomplete')
        expected=study_review_required_fact_keys()
        if tuple(self.required_fact_keys)!=expected:
            raise ValueError('study review required fact contract drift')
        return self


@dataclass(frozen=True)
class ProjectStudyReviewDecision:
    id: str
    request_id: str
    actor_id: str
    outcome: ProjectStudyReviewOutcome
    reason_code: ProjectStudyReviewReasonCode
    reason: str
    unknown_input_keys: Tuple[str,...]
    input_snapshot_ref: str
    policy_version: str
    decision_version: str='BUILD6B_PROJECT_STUDY_REVIEW_DECISION_V0_1'

    def validate_protocol(self,request:ProjectStudyReviewRequest|None=None):
        if not self.id or not self.request_id or not self.actor_id or not self.input_snapshot_ref or not self.policy_version:
            raise ValueError('study review decision identity/lineage incomplete')
        ProjectStudyReviewOutcome(self.outcome)
        ProjectStudyReviewReasonCode(self.reason_code)
        if self.outcome==ProjectStudyReviewOutcome.BLOCKED_UNKNOWN:
            if not self.unknown_input_keys or self.reason_code!=ProjectStudyReviewReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN:
                raise ValueError('BLOCKED_UNKNOWN study review invalid')
        elif self.unknown_input_keys:
            raise ValueError('known study review carries unknown inputs')
        if request is not None and request.id!=self.request_id:
            raise ValueError('study review decision/request lineage mismatch')
        return self


@dataclass(frozen=True)
class ProjectStudyReviewExecutionRecord:
    decision_id: str
    request_id: str
    project_id: str
    activity_id: str
    result_ref: str
    prior_maturity: ProjectStudyMaturity
    resulting_maturity: ProjectStudyMaturity
    project_status_before: str
    project_status_after: str
    outcome: ProjectStudyReviewOutcome
    effective_time: D
    event_id: str
    record_version: str='BUILD6B_PROJECT_STUDY_REVIEW_EXECUTION_V0_1'


def study_review_required_fact_keys():
    return (
        'project.STATUS',
        'study.CURRENT_MATURITY',
        'study.ACTIVITY_ID',
        'study.RESULT_REF',
        'study.RESULT_STANDING',
        'study.NEXT_MATURITY',
    )


def build_project_study_review_request(request_id,project_id,activity_id,result_ref):
    return ProjectStudyReviewRequest(
        str(request_id),str(project_id),str(activity_id),str(result_ref),
        study_review_required_fact_keys()
    ).validate_protocol()


def required_unknown_study_review_inputs(request:ProjectStudyReviewRequest,snapshot:DecisionSnapshot):
    request.validate_protocol()
    facts={f.key:f for f in snapshot.admitted_facts}
    unknown=[]
    for key in request.required_fact_keys:
        f=facts.get(key)
        if f is None or f.state!=FactState.KNOWN or f.value is None:
            unknown.append(key)
    return tuple(sorted(unknown))


def build_project_study_review_decision(
    decision_id,request:ProjectStudyReviewRequest,actor_id,outcome,reason_code,reason,
    snapshot:DecisionSnapshot,policy_version
):
    outcome=ProjectStudyReviewOutcome(outcome)
    reason_code=ProjectStudyReviewReasonCode(reason_code)
    unknowns=required_unknown_study_review_inputs(request,snapshot)
    if unknowns and outcome!=ProjectStudyReviewOutcome.BLOCKED_UNKNOWN:
        raise ValueError('unknown study review inputs must BLOCK')
    if not unknowns and outcome==ProjectStudyReviewOutcome.BLOCKED_UNKNOWN:
        raise ValueError('BLOCKED_UNKNOWN not allowed when study review inputs known')
    d=ProjectStudyReviewDecision(
        str(decision_id),request.id,str(actor_id),outcome,reason_code,str(reason),
        unknowns,f'decision-snapshot:{snapshot.period_key}:{snapshot.fingerprint()}',
        str(policy_version)
    )
    return d.validate_protocol(request)
