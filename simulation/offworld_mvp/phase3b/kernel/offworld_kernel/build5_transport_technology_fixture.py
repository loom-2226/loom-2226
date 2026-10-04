from __future__ import annotations

from decimal import Decimal as D

from .build5_settlement_fixture import (
    RESEARCH_POPULATION_REF,
    RESEARCH_SETTLEMENT_REF,
    settlement_kernel,
)
from .model import AccountKind
from .mvp_state import RuntimeObjectClass, SystemState
from .policy import FactState, SnapshotFact, build_decision_snapshot
from .transport import TechnologyCapabilityState, TransportRelationship
from .transport_protocol import build_transport_settlement_request


RESEARCH_TRANSPORT_REF=(
    'loom-2226/loom-research-lab@572f174f8b329ca749fddaf3a3ce492ae97304bc:'
    'projects/offworld_transport_energy_logistics/RESEARCH_BRIEF_v0.1.md'
)
RESEARCH_TECHNOLOGY_REF=(
    'loom-2226/loom-research-lab@572f174f8b329ca749fddaf3a3ce492ae97304bc:'
    'projects/offworld_technology_research_innovation/RESEARCH_BRIEF_v0.1.md'
)

BASELINE_CAPABILITY='PASSENGER_TRANSFER_BASELINE_TEST012A'
IMPROVED_CAPABILITY='PASSENGER_TRANSFER_IMPROVED_TEST012A'


def transport_technology_kernel(
        universe_id='RICH_PUBLIC_3',stock='20',
        public_balance=None,earth_population=1000,
        requested_residents=10,public_support_cost='10',
        technology_qualified=True,register_relationship=True,
        relationship_id='TR-EARTH-T1-BASELINE',
        technology_state_id='TECH-STATE-012A-BASELINE',
        required_capability_id=BASELINE_CAPABILITY,
        transport_capacity=10,cost_per_passenger='2',
        travel_time='1',energy_per_passenger='3',loss_risk='0',
        effective_from='12',effective_to='20'):
    k,h=settlement_kernel(
        universe_id,stock,
        public_balance=public_balance,
        earth_population=earth_population,
        requested_residents=requested_residents,
        public_support_cost=public_support_cost)

    k.add_account(
        'transport_provider','TRANSPORT_PROVIDER','EARTH:X',
        AccountKind.SUPPLIER,D('0'))

    for system in (
        SystemState(
            'TRANSPORT_SETTLEMENT_DECISION_ORCHESTRATOR',
            'TRANSPORT_SETTLEMENT_DECISION_ORCHESTRATION',set()),
        SystemState(
            'PASSENGER_TRANSPORT_DEPARTURE_SYSTEM',
            'PASSENGER_TRANSPORT_DEPARTURE',
            {'accounts','transactions','colonies','population',
             'passenger_transport_departures','events'}),
        SystemState(
            'PASSENGER_TRANSPORT_ARRIVAL_SYSTEM',
            'PASSENGER_TRANSPORT_ARRIVAL',
            {'colonies','population','passenger_transport_arrivals',
             'settlement_stage_records','events'}),
    ):
        k.add_system(system)

    caps=(str(required_capability_id),) if technology_qualified else ()
    technology=TechnologyCapabilityState(
        str(technology_state_id),D(effective_from),D(effective_to),caps,
        'TEST_ONLY:BUILD5_TEST012A_EXOGENOUS_TECHNOLOGY_STATE'
        +'|ADVISORY_TECHNOLOGY:'+RESEARCH_TECHNOLOGY_REF,
        'TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE').validate()
    k.register_technology_capability_state(technology)

    relationship=TransportRelationship(
        str(relationship_id),'EARTH:X','OFF:T1',D(effective_from),D(effective_to),
        str(required_capability_id),D(cost_per_passenger),D(travel_time),
        D(energy_per_passenger),D(loss_risk),int(transport_capacity),
        'PASSENGER',
        'TEST_ONLY:BUILD5_TEST012A_TRANSPORT_RELATIONSHIP'
        +'|ADVISORY_TRANSPORT:'+RESEARCH_TRANSPORT_REF,
        'TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE').validate()
    if register_relationship:
        k.register_transport_relationship(relationship)

    h['transport_technology_state']=technology
    h['transport_relationship']=relationship
    h['transport_relationship_registered']=bool(register_relationship)
    h['transport_departure_time']=D('12')
    return k,h


def transport_settlement_facts(
        k,h,unknown_transport_key=None,
        stage_override=None,headroom_override=None,
        requested_override=None,earth_override=None,
        support_cost_override=None):
    c=k.colonies['OFF:T1']
    request_relationship=h['transport_relationship']
    technology=h['transport_technology_state']
    q=k.transport_qualification(
        technology.id,request_relationship.id,h['transport_departure_time'])

    stage=c.stage if stage_override is None else str(stage_override)
    headroom=k.settlement_habitat_headroom('OFF:T1')
    if headroom_override is not None:
        headroom=int(headroom_override)
    requested=h['requested_residents']
    if requested_override is not None:
        requested=int(requested_override)
    earth=k.population.earth
    if earth_override is not None:
        earth=int(earth_override)
    support=D(h['public_support_cost'])
    if support_cost_override is not None:
        support=D(support_cost_override)

    relationship=k.transport_relationships.get(request_relationship.id)

    def tfact(key,value,source):
        unknown=(unknown_transport_key==key)
        return SnapshotFact(
            key,FactState.UNKNOWN if unknown else FactState.KNOWN,
            None if unknown else str(value),source)

    facts=[
        SnapshotFact(
            'settlement.STAGE',FactState.KNOWN,stage,
            'SETTLEMENT_STAGE_RULE_TEST011A_V0_1'),
        SnapshotFact(
            'settlement.HABITAT_HEADROOM',FactState.KNOWN,str(headroom),
            f'COLONY:OFF:T1:HABITAT_CAPACITY={c.habitat_capacity}:POPULATION={c.population}'),
        SnapshotFact(
            'settlement.REQUESTED_RESIDENTS',FactState.KNOWN,str(requested),
            'TEST_ONLY:BUILD5_TEST012A_REQUESTED_RESIDENTS'),
        SnapshotFact(
            'population.EARTH_AVAILABLE',FactState.KNOWN,str(earth),
            'POPULATION_LEDGER:EARTH'),
        SnapshotFact(
            'settlement.PUBLIC_SUPPORT_COST',FactState.KNOWN,str(support),
            'TEST_ONLY:BUILD5_TEST012A_PUBLIC_SUPPORT_COST'),
        tfact('transport.AVAILABLE','TRUE' if q.available else 'FALSE',
              f'TRANSPORT_QUALIFICATION:{q.reason}'),
        tfact('transport.RELATIONSHIP_ID',request_relationship.id,
              'TRANSPORT_RELATIONSHIP_ID'),
        tfact('technology.STATE_ID',technology.id,'TECHNOLOGY_CAPABILITY_STATE_ID'),
    ]

    if relationship is None:
        for key in (
            'transport.CAPACITY','transport.COST_PER_PASSENGER',
            'transport.TRAVEL_TIME','transport.ENERGY_PER_PASSENGER',
            'transport.LOSS_RISK'):
            facts.append(SnapshotFact(
                key,FactState.UNKNOWN,None,
                'TRANSPORT_RELATIONSHIP_MISSING'))
    else:
        facts.extend((
            tfact('transport.CAPACITY',relationship.capacity,
                  relationship.id+':Capacity'),
            tfact('transport.COST_PER_PASSENGER',relationship.cost_per_passenger,
                  relationship.id+':Cost'),
            tfact('transport.TRAVEL_TIME',relationship.travel_time,
                  relationship.id+':TravelTime'),
            tfact('transport.ENERGY_PER_PASSENGER',relationship.energy_per_passenger,
                  relationship.id+':Energy'),
            tfact('transport.LOSS_RISK',relationship.loss_risk,
                  relationship.id+':LossRisk'),
        ))
    return tuple(facts)


def transport_settlement_snapshot(
        k,h,period_key='TRANSPORT-SETTLEMENT-12',
        effective_time='12',**kw):
    return build_decision_snapshot(
        k,'PUB',period_key,D(str(effective_time)),
        transport_settlement_facts(k,h,**kw))


def transport_settlement_request(
        h,requested_residents=None,request_id='TRSETREQ-012A-1'):
    requested=h['requested_residents'] if requested_residents is None else int(requested_residents)
    rel=h['transport_relationship']
    tech=h['transport_technology_state']
    return build_transport_settlement_request(
        request_id,h['transport_departure_time'],'EARTH:X','OFF:T1',
        'settlement_support','transport_provider',requested,
        h['public_support_cost'],rel.id,tech.id)
