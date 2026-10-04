from __future__ import annotations

from decimal import Decimal as D

from .policy import DecisionSnapshot, FactState
from .transport import (
    TRANSPORT_SETTLEMENT_REQUIRED_FACT_KEYS,
    TransportSettlementDecision,
    TransportSettlementDecisionOutcome,
    TransportSettlementReasonCode,
    TransportSettlementRequest,
)

TRANSPORT_SETTLEMENT_PROTOCOL_VERSION='BUILD5_TRANSPORT_SETTLEMENT_PROTOCOL_0_1'


def build_transport_settlement_request(
        request_id,departure_time,origin_node_id,destination_node_id,
        support_account_id,transport_account_id,requested_residents,support_cost,
        transport_relationship_id,technology_state_id,
        currency_unit='MODEL_CURRENCY',population_unit='PEOPLE_EQUIVALENT',
        time_unit='SIM_TIME'):
    return TransportSettlementRequest(
        str(request_id),D(departure_time),str(origin_node_id),str(destination_node_id),
        str(support_account_id),str(transport_account_id),int(requested_residents),
        D(support_cost),str(transport_relationship_id),str(technology_state_id),
        TRANSPORT_SETTLEMENT_REQUIRED_FACT_KEYS,str(currency_unit),
        str(population_unit),str(time_unit),
        'TRANSPORT_SETTLEMENT_REQUEST_V1').validate_protocol()


def required_unknown_transport_settlement_inputs(
        request:TransportSettlementRequest,snapshot:DecisionSnapshot):
    request.validate_protocol()
    facts={f.key:f for f in snapshot.admitted_facts}
    unknown=[]
    for key in request.required_fact_keys:
        fact=facts.get(key)
        if fact is None or fact.state!=FactState.KNOWN or fact.value is None:
            unknown.append(key)
    return tuple(sorted(unknown))


def build_transport_settlement_decision(
        decision_id,request,actor_id,outcome,reason_code,reason,
        snapshot,policy_version,authorized_residents=0,
        support_amount=D('0'),transport_amount=D('0'),
        relationship_id='',technology_state_id='',
        departure_time=D('0'),arrival_time=D('0')):
    outcome=TransportSettlementDecisionOutcome(outcome)
    reason_code=TransportSettlementReasonCode(reason_code)
    unknowns=required_unknown_transport_settlement_inputs(request,snapshot)
    if unknowns and outcome!=TransportSettlementDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('required unknown transport settlement inputs must produce BLOCKED_UNKNOWN')
    if not unknowns and outcome==TransportSettlementDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('BLOCKED_UNKNOWN not allowed when transport settlement inputs are known')
    snapshot_ref=f'decision-snapshot:{snapshot.period_key}:{snapshot.fingerprint()}'
    return TransportSettlementDecision(
        str(decision_id),request.id,str(actor_id),outcome,int(authorized_residents),
        D(support_amount),D(transport_amount),str(relationship_id),
        str(technology_state_id),D(departure_time),D(arrival_time),
        str(reason),reason_code,unknowns,snapshot_ref,str(policy_version),
        'TRANSPORT_SETTLEMENT_DECISION_V1').validate_protocol(request)
