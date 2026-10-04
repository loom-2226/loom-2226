from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal as D
from enum import Enum

from .policy import DecisionSnapshot, FactState

BUILD5_ENTERPRISE_REVIEW_REQUIRED_FACT_KEYS=(
    'project.STATUS',
    'cycle.PLANNED_QUANTITY',
    'cycle.ACTUAL_OUTPUT',
)

class EnterpriseReviewDecisionOutcome(str,Enum):
    CONTINUE='CONTINUE'
    CLOSE='CLOSE'
    DEFER='DEFER'
    BLOCKED_UNKNOWN='BLOCKED_UNKNOWN'

class EnterpriseReviewReasonCode(str,Enum):
    POSITIVE_OUTPUT_CONTINUE='POSITIVE_OUTPUT_CONTINUE'
    ZERO_OUTPUT_CLOSE='ZERO_OUTPUT_CLOSE'
    CAPABILITY_OR_OBJECTIVE_BLOCK='CAPABILITY_OR_OBJECTIVE_BLOCK'
    PROJECT_STATE_BLOCK='PROJECT_STATE_BLOCK'
    OUTPUT_RECORD_INVALID='OUTPUT_RECORD_INVALID'
    BLOCKED_REQUIRED_INPUT_UNKNOWN='BLOCKED_REQUIRED_INPUT_UNKNOWN'

@dataclass(frozen=True)
class EnterpriseReviewRequest:
    id: str
    year: int
    project_id: str
    extraction_event_id: str
    required_fact_keys: tuple[str,...]=()
    quantity_unit: str='MODEL_RESOURCE_UNIT_BY_FAMILY'
    request_version: str='ENTERPRISE_REVIEW_REQUEST_V1'
    def validate_protocol(self):
        if not self.id or not self.project_id or not self.extraction_event_id:
            raise ValueError('enterprise-review request identity incomplete')
        if self.year<0:
            raise ValueError('enterprise-review year invalid')
        if tuple(self.required_fact_keys)!=BUILD5_ENTERPRISE_REVIEW_REQUIRED_FACT_KEYS:
            raise ValueError('enterprise-review request must declare exact Test 014A fact contract')
        if not self.quantity_unit:
            raise ValueError('enterprise-review quantity unit missing')
        return self

@dataclass(frozen=True)
class EnterpriseReviewDecision:
    id: str
    request_id: str
    actor_id: str
    outcome: EnterpriseReviewDecisionOutcome
    reason: str
    reason_code: EnterpriseReviewReasonCode
    unknown_input_keys: tuple[str,...]=()
    input_snapshot_ref: str=''
    policy_version: str=''
    decision_version: str='ENTERPRISE_REVIEW_DECISION_V1'
    def validate_protocol(self,request:EnterpriseReviewRequest|None=None):
        if not self.id or not self.request_id or not self.actor_id:
            raise ValueError('enterprise-review decision identity incomplete')
        if not self.input_snapshot_ref or not self.policy_version:
            raise ValueError('enterprise-review decision requires snapshot and policy version')
        if self.unknown_input_keys and self.outcome!=EnterpriseReviewDecisionOutcome.BLOCKED_UNKNOWN:
            raise ValueError('required unknown enterprise-review inputs must produce BLOCKED_UNKNOWN')
        if self.outcome==EnterpriseReviewDecisionOutcome.BLOCKED_UNKNOWN:
            if not self.unknown_input_keys or self.reason_code!=EnterpriseReviewReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN:
                raise ValueError('invalid blocked enterprise-review decision')
        if request is not None:
            request.validate_protocol()
            if request.id!=self.request_id:
                raise ValueError('enterprise-review decision/request lineage mismatch')
        return self

@dataclass(frozen=True)
class EnterpriseReviewRecord:
    year: int
    actor_id: str
    decision_id: str
    request_id: str
    project_id: str
    extraction_event_id: str
    planned_quantity: D
    actual_output: D
    outcome: EnterpriseReviewDecisionOutcome
    status_before: str
    status_after: str
    event_id: str
    record_version: str='ENTERPRISE_REVIEW_RECORD_V1'
    def validate(self):
        planned=D(self.planned_quantity); actual=D(self.actual_output)
        if planned<=0 or actual<0 or actual>planned:
            raise ValueError('enterprise-review record output invalid')
        if self.outcome==EnterpriseReviewDecisionOutcome.CONTINUE:
            if actual<=0 or self.status_before!='OPERATING' or self.status_after!='OPERATING':
                raise ValueError('enterprise-review CONTINUE record invalid')
        elif self.outcome==EnterpriseReviewDecisionOutcome.CLOSE:
            if actual!=0 or self.status_before!='OPERATING' or self.status_after!='CLOSED':
                raise ValueError('enterprise-review CLOSE record invalid')
        else:
            raise ValueError('enterprise-review execution record requires CONTINUE/CLOSE')
        if not self.event_id:
            raise ValueError('enterprise-review record event missing')
        return self

def build_enterprise_review_request(request_id,year,project_id,extraction_event_id,
                                    quantity_unit='MODEL_RESOURCE_UNIT_BY_FAMILY'):
    return EnterpriseReviewRequest(
        str(request_id),int(year),str(project_id),str(extraction_event_id),
        BUILD5_ENTERPRISE_REVIEW_REQUIRED_FACT_KEYS,str(quantity_unit),
        'ENTERPRISE_REVIEW_REQUEST_V1').validate_protocol()

def required_unknown_enterprise_review_inputs(request:EnterpriseReviewRequest,
                                              snapshot:DecisionSnapshot):
    request.validate_protocol()
    facts={f.key:f for f in snapshot.admitted_facts}
    unknown=[]
    for key in request.required_fact_keys:
        fact=facts.get(key)
        if fact is None or fact.state!=FactState.KNOWN or fact.value is None:
            unknown.append(key)
    return tuple(sorted(unknown))

def build_enterprise_review_decision(decision_id,request,actor_id,outcome,reason_code,
                                     reason,snapshot,policy_version):
    outcome=EnterpriseReviewDecisionOutcome(outcome)
    reason_code=EnterpriseReviewReasonCode(reason_code)
    unknowns=required_unknown_enterprise_review_inputs(request,snapshot)
    if unknowns and outcome!=EnterpriseReviewDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('required unknown enterprise-review inputs must produce BLOCKED_UNKNOWN')
    if not unknowns and outcome==EnterpriseReviewDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('BLOCKED_UNKNOWN not allowed when enterprise-review inputs are known')
    snapshot_ref=f'decision-snapshot:{snapshot.period_key}:{snapshot.fingerprint()}'
    return EnterpriseReviewDecision(
        str(decision_id),request.id,str(actor_id),outcome,str(reason),reason_code,
        unknowns,snapshot_ref,str(policy_version),'ENTERPRISE_REVIEW_DECISION_V1'
    ).validate_protocol(request)
