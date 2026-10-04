from __future__ import annotations
from decimal import Decimal as D

from .mvp_state import (
    BUILD5_SETTLEMENT_SUPPORT_REQUIRED_FACT_KEYS,
    SettlementSupportDecision,
    SettlementSupportDecisionOutcome,
    SettlementSupportReasonCode,
    SettlementSupportRequest,
)
from .policy import DecisionSnapshot, FactState

SETTLEMENT_SUPPORT_PROTOCOL_VERSION='BUILD5_SETTLEMENT_SUPPORT_PROTOCOL_0_1'

def build_settlement_support_request(request_id,year,node_id,support_account_id,
                                     requested_residents,support_cost,
                                     currency_unit='MODEL_CURRENCY',
                                     population_unit='PEOPLE_EQUIVALENT'):
    return SettlementSupportRequest(
        str(request_id),int(year),str(node_id),str(support_account_id),
        int(requested_residents),D(support_cost),BUILD5_SETTLEMENT_SUPPORT_REQUIRED_FACT_KEYS,
        str(currency_unit),str(population_unit),
        'SETTLEMENT_SUPPORT_REQUEST_V1').validate_protocol()

def required_unknown_settlement_inputs(request:SettlementSupportRequest,
                                       snapshot:DecisionSnapshot):
    request.validate_protocol()
    facts={f.key:f for f in snapshot.admitted_facts}
    unknown=[]
    for key in request.required_fact_keys:
        fact=facts.get(key)
        if fact is None or fact.state!=FactState.KNOWN or fact.value is None:
            unknown.append(key)
    return tuple(sorted(unknown))

def build_settlement_support_decision(
        decision_id,request,actor_id,outcome,reason_code,reason,
        snapshot,policy_version,authorized_residents=0,support_amount=D('0')):
    outcome=SettlementSupportDecisionOutcome(outcome)
    reason_code=SettlementSupportReasonCode(reason_code)
    unknowns=required_unknown_settlement_inputs(request,snapshot)
    if unknowns and outcome!=SettlementSupportDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('required unknown settlement inputs must produce BLOCKED_UNKNOWN')
    if not unknowns and outcome==SettlementSupportDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('BLOCKED_UNKNOWN not allowed when settlement inputs are known')
    snapshot_ref=f'decision-snapshot:{snapshot.period_key}:{snapshot.fingerprint()}'
    return SettlementSupportDecision(
        str(decision_id),request.id,str(actor_id),outcome,int(authorized_residents),
        D(support_amount),str(reason),reason_code,unknowns,snapshot_ref,
        str(policy_version),'SETTLEMENT_SUPPORT_DECISION_V1').validate_protocol(request)
