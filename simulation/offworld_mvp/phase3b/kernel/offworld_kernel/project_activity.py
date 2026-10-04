from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Tuple

from .kernel import InvariantError
from .policy import DecisionSnapshot, FactState

D=Decimal


class ProjectActivityStatus(str,Enum):
    PROPOSED='PROPOSED'
    AUTHORIZED='AUTHORIZED'
    WAITING_PREREQUISITES='WAITING_PREREQUISITES'
    WAITING_WINDOW='WAITING_WINDOW'
    ACTIVE='ACTIVE'
    COMPLETED='COMPLETED'
    CANCELED='CANCELED'
    FAILED='FAILED'


class SponsorPortfolioDecisionOutcome(str,Enum):
    AUTHORIZE='AUTHORIZE'
    DEFER='DEFER'
    BLOCKED_UNKNOWN='BLOCKED_UNKNOWN'


class SponsorPortfolioReasonCode(str,Enum):
    SELECTED_PRIORITY_AFFORDABLE='SELECTED_PRIORITY_AFFORDABLE'
    INSUFFICIENT_AVAILABLE_CAPITAL='INSUFFICIENT_AVAILABLE_CAPITAL'
    NO_ELIGIBLE_ACTIVITY='NO_ELIGIBLE_ACTIVITY'
    CAPABILITY_OR_OBJECTIVE_BLOCK='CAPABILITY_OR_OBJECTIVE_BLOCK'
    BLOCKED_REQUIRED_INPUT_UNKNOWN='BLOCKED_REQUIRED_INPUT_UNKNOWN'


@dataclass
class ProjectActivity:
    id: str
    project_id: str
    activity_type: str
    actor_id: str
    priority: int
    earliest_start: D
    planned_duration: D
    capital_commitment: D
    result_type: str
    opportunity_window_id: str=''
    window_open: D|None=None
    window_close: D|None=None
    status: ProjectActivityStatus=ProjectActivityStatus.PROPOSED
    authorized_at: D|None=None
    actual_start: D|None=None
    planned_completion: D|None=None
    actual_completion: D|None=None
    result_ref: str=''
    authorization_decision_id: str=''
    activity_version: str='BUILD6A_PROJECT_ACTIVITY_V0_1'

    @property
    def reserves_capital(self):
        return self.status in {
            ProjectActivityStatus.AUTHORIZED,
            ProjectActivityStatus.WAITING_PREREQUISITES,
            ProjectActivityStatus.WAITING_WINDOW,
            ProjectActivityStatus.ACTIVE,
        }

    def validate(self):
        if not self.id or not self.project_id or not self.activity_type or not self.actor_id:
            raise ValueError('project activity identity incomplete')
        if self.priority<0:
            raise ValueError('project activity priority invalid')
        if D(self.earliest_start)<0 or D(self.planned_duration)<=0 or D(self.capital_commitment)<0:
            raise ValueError('project activity time/capital invalid')
        if not self.result_type:
            raise ValueError('project activity result type required')
        has_window=bool(self.opportunity_window_id)
        if has_window!=(self.window_open is not None and self.window_close is not None):
            raise ValueError('project activity opportunity-window metadata incomplete')
        if has_window:
            if D(self.window_open)<0 or D(self.window_close)<D(self.window_open):
                raise ValueError('project activity opportunity window invalid')
        if self.status==ProjectActivityStatus.PROPOSED:
            if any(x is not None for x in (self.authorized_at,self.actual_start,self.planned_completion,self.actual_completion)):
                raise ValueError('proposed activity carries execution timestamps')
            if self.result_ref or self.authorization_decision_id:
                raise ValueError('proposed activity carries execution lineage')
        else:
            if self.authorized_at is None or not self.authorization_decision_id:
                raise ValueError('authorized activity missing authorization lineage')
        if self.status==ProjectActivityStatus.ACTIVE:
            if self.actual_start is None or self.planned_completion is None or self.actual_completion is not None:
                raise ValueError('active project activity timing invalid')
        if self.status==ProjectActivityStatus.COMPLETED:
            if self.actual_start is None or self.planned_completion is None or self.actual_completion is None or not self.result_ref:
                raise ValueError('completed project activity state incomplete')
            if D(self.actual_completion)<D(self.actual_start):
                raise ValueError('project activity completion precedes start')
        if self.status in {ProjectActivityStatus.AUTHORIZED,ProjectActivityStatus.WAITING_PREREQUISITES,ProjectActivityStatus.WAITING_WINDOW}:
            if self.actual_start is not None or self.planned_completion is not None or self.actual_completion is not None or self.result_ref:
                raise ValueError('not-started project activity carries execution result')
        return self


@dataclass(frozen=True)
class ProjectActivityTransitionRecord:
    activity_id: str
    project_id: str
    actor_id: str
    effective_time: D
    prior_status: ProjectActivityStatus
    new_status: ProjectActivityStatus
    event_id: str
    decision_id: str=''
    result_ref: str=''
    record_version: str='BUILD6A_PROJECT_ACTIVITY_TRANSITION_V0_1'


@dataclass(frozen=True)
class ProjectActivityInformationRecord:
    activity_id: str
    project_id: str
    agent_id: str
    result_ref: str
    admitted_at: D
    event_id: str
    record_version: str='BUILD6A_PROJECT_ACTIVITY_INFORMATION_V0_1'


@dataclass(frozen=True)
class SponsorPortfolioDecisionRequest:
    id: str
    effective_time: D
    candidate_activity_ids: Tuple[str,...]
    required_fact_keys: Tuple[str,...]
    currency_unit: str='MODEL_CURRENCY'
    request_version: str='BUILD6A_SPONSOR_PORTFOLIO_REQUEST_V0_1'

    def validate_protocol(self):
        if not self.id or D(self.effective_time)<0 or not self.candidate_activity_ids:
            raise ValueError('portfolio request identity/time/candidates invalid')
        if len(set(self.candidate_activity_ids))!=len(self.candidate_activity_ids):
            raise ValueError('duplicate portfolio candidate')
        expected=portfolio_required_fact_keys(self.candidate_activity_ids)
        if tuple(self.required_fact_keys)!=expected:
            raise ValueError('portfolio request required fact contract drift')
        if not self.currency_unit:
            raise ValueError('portfolio request currency unit missing')
        return self


@dataclass(frozen=True)
class SponsorPortfolioDecision:
    id: str
    request_id: str
    actor_id: str
    outcome: SponsorPortfolioDecisionOutcome
    selected_activity_id: str
    reserved_capital: D
    reason: str
    reason_code: SponsorPortfolioReasonCode
    unknown_input_keys: Tuple[str,...]
    input_snapshot_ref: str
    policy_version: str
    decision_version: str='BUILD6A_SPONSOR_PORTFOLIO_DECISION_V0_1'

    def validate_protocol(self,request:SponsorPortfolioDecisionRequest|None=None):
        if not self.id or not self.request_id or not self.actor_id or not self.input_snapshot_ref or not self.policy_version:
            raise ValueError('portfolio decision identity/lineage incomplete')
        amount=D(self.reserved_capital)
        if self.outcome==SponsorPortfolioDecisionOutcome.AUTHORIZE:
            if not self.selected_activity_id or amount<0:
                raise ValueError('AUTHORIZE requires selected activity and nonnegative reservation')
            if request is not None and self.selected_activity_id not in request.candidate_activity_ids:
                raise ValueError('portfolio selected activity not in request')
        else:
            if self.selected_activity_id or amount!=0:
                raise ValueError('non-authorization portfolio outcome cannot reserve activity capital')
        if self.outcome==SponsorPortfolioDecisionOutcome.BLOCKED_UNKNOWN:
            if not self.unknown_input_keys or self.reason_code!=SponsorPortfolioReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN:
                raise ValueError('BLOCKED_UNKNOWN portfolio decision invalid')
        elif self.unknown_input_keys:
            raise ValueError('known portfolio decision carries unknown inputs')
        if request is not None and request.id!=self.request_id:
            raise ValueError('portfolio decision/request lineage mismatch')
        return self


def portfolio_required_fact_keys(activity_ids):
    keys=['portfolio.AVAILABLE_CAPITAL']
    for aid in sorted(str(x) for x in activity_ids):
        prefix=f'activity.{aid}.'
        keys.extend((
            prefix+'PROJECT_ID',
            prefix+'PROJECT_STATUS',
            prefix+'STATUS',
            prefix+'COMMITMENT',
            prefix+'PRIORITY',
            prefix+'WINDOW_VALID',
        ))
    return tuple(keys)


def build_sponsor_portfolio_request(request_id,effective_time,candidate_activity_ids,currency_unit='MODEL_CURRENCY'):
    candidates=tuple(str(x) for x in candidate_activity_ids)
    return SponsorPortfolioDecisionRequest(
        str(request_id),D(str(effective_time)),candidates,
        portfolio_required_fact_keys(candidates),str(currency_unit)
    ).validate_protocol()


def required_unknown_portfolio_inputs(request:SponsorPortfolioDecisionRequest,snapshot:DecisionSnapshot):
    request.validate_protocol()
    facts={f.key:f for f in snapshot.admitted_facts}
    unknown=[]
    for key in request.required_fact_keys:
        f=facts.get(key)
        if f is None or f.state!=FactState.KNOWN or f.value is None:
            unknown.append(key)
    return tuple(sorted(unknown))


def build_sponsor_portfolio_decision(
    decision_id,request:SponsorPortfolioDecisionRequest,actor_id,outcome,reason_code,reason,
    snapshot:DecisionSnapshot,policy_version,selected_activity_id='',reserved_capital=D('0')
):
    outcome=SponsorPortfolioDecisionOutcome(outcome)
    reason_code=SponsorPortfolioReasonCode(reason_code)
    unknowns=required_unknown_portfolio_inputs(request,snapshot)
    if unknowns and outcome!=SponsorPortfolioDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('required unknown portfolio inputs must produce BLOCKED_UNKNOWN')
    if not unknowns and outcome==SponsorPortfolioDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('BLOCKED_UNKNOWN not allowed when portfolio inputs known')
    decision=SponsorPortfolioDecision(
        str(decision_id),request.id,str(actor_id),outcome,str(selected_activity_id),D(reserved_capital),
        str(reason),reason_code,unknowns,
        f'decision-snapshot:{snapshot.period_key}:{snapshot.fingerprint()}',
        str(policy_version)
    )
    return decision.validate_protocol(request)
