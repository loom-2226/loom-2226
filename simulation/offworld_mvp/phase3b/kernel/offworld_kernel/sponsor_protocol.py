from __future__ import annotations
from decimal import Decimal as D

from .mvp_state import (
    BUILD5_SPONSOR_REQUIRED_BELIEF_KEYS,
    BUILD5_SPONSOR_REQUIRED_FACT_KEYS,
    BUILD5_SPONSOR_REQUIRED_PRIOR_KEYS,
    SponsorProjectDecision,
    SponsorProjectDecisionOutcome,
    SponsorProjectDecisionRequest,
    SponsorProjectReasonCode,
)
from .policy import DecisionSnapshot, FactState

SPONSOR_PROTOCOL_VERSION='BUILD5_SPONSOR_PROJECT_PROTOCOL_0_1'

def build_sponsor_project_request(request_id,year,project_id,resource_id,observation_id,
                                  currency_unit='MODEL_CURRENCY'):
    return SponsorProjectDecisionRequest(
        str(request_id),int(year),str(project_id),str(resource_id),str(observation_id),
        BUILD5_SPONSOR_REQUIRED_FACT_KEYS,
        BUILD5_SPONSOR_REQUIRED_BELIEF_KEYS,
        BUILD5_SPONSOR_REQUIRED_PRIOR_KEYS,
        str(currency_unit),
        'SPONSOR_PROJECT_DECISION_REQUEST_V1').validate_protocol()

def required_unknown_sponsor_inputs(request:SponsorProjectDecisionRequest,
                                    snapshot:DecisionSnapshot):
    request.validate_protocol()
    facts={f.key:f for f in snapshot.admitted_facts}
    unknown=[]
    for key in request.required_fact_keys:
        fact=facts.get(key)
        if fact is None or fact.state!=FactState.KNOWN or fact.value is None:
            unknown.append(key)
    beliefs=dict(snapshot.beliefs)
    for key in request.required_belief_keys:
        if key not in beliefs:
            unknown.append(f'belief.{key}')
    priors=dict(snapshot.priors)
    for key in request.required_prior_keys:
        if key not in priors:
            unknown.append(f'prior.{key}')
    return tuple(sorted(unknown))

def build_sponsor_project_decision(decision_id,request:SponsorProjectDecisionRequest,
                                   actor_id,outcome,reason_code,reason,
                                   snapshot:DecisionSnapshot,policy_version,
                                   requested_financing=D('0')):
    outcome=SponsorProjectDecisionOutcome(outcome)
    reason_code=SponsorProjectReasonCode(reason_code)
    unknowns=required_unknown_sponsor_inputs(request,snapshot)
    if unknowns and outcome!=SponsorProjectDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('required unknown sponsor inputs must produce BLOCKED_UNKNOWN')
    if not unknowns and outcome==SponsorProjectDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('BLOCKED_UNKNOWN not allowed when sponsor inputs are known')
    snapshot_ref=f'decision-snapshot:{snapshot.period_key}:{snapshot.fingerprint()}'
    decision=SponsorProjectDecision(
        str(decision_id),request.id,str(actor_id),outcome,D(requested_financing),
        str(reason),reason_code,unknowns,snapshot_ref,str(policy_version),
        'SPONSOR_PROJECT_DECISION_V1')
    return decision.validate_protocol(request)
