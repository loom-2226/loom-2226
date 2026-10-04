from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal as D
from enum import Enum
from hashlib import sha256
import json


TRANSPORT_SETTLEMENT_REQUIRED_FACT_KEYS=(
    'settlement.STAGE',
    'settlement.HABITAT_HEADROOM',
    'settlement.REQUESTED_RESIDENTS',
    'population.EARTH_AVAILABLE',
    'settlement.PUBLIC_SUPPORT_COST',
    'transport.AVAILABLE',
    'transport.RELATIONSHIP_ID',
    'technology.STATE_ID',
    'transport.CAPACITY',
    'transport.COST_PER_PASSENGER',
    'transport.TRAVEL_TIME',
    'transport.ENERGY_PER_PASSENGER',
    'transport.LOSS_RISK',
)


@dataclass(frozen=True)
class TechnologyCapabilityState:
    id: str
    effective_from: D
    effective_to: D
    qualified_capabilities: tuple[str,...]
    source_ref: str
    epistemic_status: str
    state_version: str='TECHNOLOGY_CAPABILITY_STATE_V1'

    def validate(self):
        if not self.id or not self.source_ref or not self.epistemic_status:
            raise ValueError('technology capability state identity/provenance incomplete')
        if D(self.effective_from)<0 or D(self.effective_to)<D(self.effective_from):
            raise ValueError('technology capability state effective period invalid')
        if len(set(self.qualified_capabilities))!=len(self.qualified_capabilities):
            raise ValueError('technology capability identifiers must be unique')
        if any(not str(x) for x in self.qualified_capabilities):
            raise ValueError('technology capability identifier missing')
        return self

    def applies(self,effective_time):
        t=D(effective_time)
        return D(self.effective_from)<=t<=D(self.effective_to)

    def qualifies(self,capability_id,effective_time):
        return self.applies(effective_time) and str(capability_id) in self.qualified_capabilities

    def fingerprint(self):
        payload={
            'id':self.id,
            'effective_from':str(self.effective_from),
            'effective_to':str(self.effective_to),
            'qualified_capabilities':tuple(self.qualified_capabilities),
            'source_ref':self.source_ref,
            'epistemic_status':self.epistemic_status,
            'state_version':self.state_version,
        }
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()


@dataclass(frozen=True)
class TransportRelationship:
    id: str
    origin_node_id: str
    destination_node_id: str
    effective_from: D
    effective_to: D
    required_capability_id: str
    cost_per_passenger: D
    travel_time: D
    energy_per_passenger: D
    loss_risk: D
    capacity: int
    passenger_class: str
    source_ref: str
    epistemic_status: str
    relationship_version: str='TRANSPORT_RELATIONSHIP_V1'

    def validate(self):
        if not self.id or not self.origin_node_id or not self.destination_node_id:
            raise ValueError('transport relationship identity incomplete')
        if self.origin_node_id==self.destination_node_id:
            raise ValueError('transport relationship origin/destination must differ')
        if not self.required_capability_id or not self.passenger_class:
            raise ValueError('transport relationship capability/class missing')
        if not self.source_ref or not self.epistemic_status:
            raise ValueError('transport relationship provenance/standing missing')
        if D(self.effective_from)<0 or D(self.effective_to)<D(self.effective_from):
            raise ValueError('transport relationship effective period invalid')
        if D(self.cost_per_passenger)<0:
            raise ValueError('transport Cost must be nonnegative')
        if D(self.travel_time)<=0:
            raise ValueError('transport TravelTime must be positive')
        if D(self.energy_per_passenger)<0:
            raise ValueError('transport Energy must be nonnegative')
        if D(self.loss_risk)<0 or D(self.loss_risk)>1:
            raise ValueError('transport LossRisk must be within [0,1]')
        if int(self.capacity)<=0:
            raise ValueError('transport Capacity must be positive')
        return self

    def applies(self,effective_time):
        t=D(effective_time)
        return D(self.effective_from)<=t<=D(self.effective_to)

    def fingerprint(self):
        payload={
            'id':self.id,
            'origin_node_id':self.origin_node_id,
            'destination_node_id':self.destination_node_id,
            'effective_from':str(self.effective_from),
            'effective_to':str(self.effective_to),
            'required_capability_id':self.required_capability_id,
            'Cost':str(self.cost_per_passenger),
            'TravelTime':str(self.travel_time),
            'Energy':str(self.energy_per_passenger),
            'LossRisk':str(self.loss_risk),
            'Capacity':self.capacity,
            'passenger_class':self.passenger_class,
            'source_ref':self.source_ref,
            'epistemic_status':self.epistemic_status,
            'relationship_version':self.relationship_version,
        }
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()


@dataclass(frozen=True)
class TransportQualificationRecord:
    technology_state_id: str
    relationship_id: str
    effective_time: D
    available: bool
    reason: str
    required_capability_id: str
    record_version: str='TRANSPORT_QUALIFICATION_RECORD_V1'


class TransportSettlementDecisionOutcome(str,Enum):
    AUTHORIZE='AUTHORIZE'
    DEFER='DEFER'
    BLOCKED_UNKNOWN='BLOCKED_UNKNOWN'


class TransportSettlementReasonCode(str,Enum):
    SETTLEMENT_TRANSPORT_AUTHORIZED='SETTLEMENT_TRANSPORT_AUTHORIZED'
    STAGE_BLOCK='STAGE_BLOCK'
    NO_REQUESTED_RESIDENTS='NO_REQUESTED_RESIDENTS'
    HABITAT_CAPACITY_LIMIT='HABITAT_CAPACITY_LIMIT'
    ORIGIN_POPULATION_LIMIT='ORIGIN_POPULATION_LIMIT'
    TRANSPORT_UNAVAILABLE='TRANSPORT_UNAVAILABLE'
    TRANSPORT_CAPACITY_LIMIT='TRANSPORT_CAPACITY_LIMIT'
    LOSS_RISK_UNSUPPORTED='LOSS_RISK_UNSUPPORTED'
    INSUFFICIENT_PUBLIC_FUNDS='INSUFFICIENT_PUBLIC_FUNDS'
    CAPABILITY_OR_OBJECTIVE_BLOCK='CAPABILITY_OR_OBJECTIVE_BLOCK'
    BLOCKED_REQUIRED_INPUT_UNKNOWN='BLOCKED_REQUIRED_INPUT_UNKNOWN'


@dataclass(frozen=True)
class TransportSettlementRequest:
    id: str
    departure_time: D
    origin_node_id: str
    destination_node_id: str
    support_account_id: str
    transport_account_id: str
    requested_residents: int
    support_cost: D
    transport_relationship_id: str
    technology_state_id: str
    required_fact_keys: tuple[str,...]=()
    currency_unit: str='MODEL_CURRENCY'
    population_unit: str='PEOPLE_EQUIVALENT'
    time_unit: str='SIM_TIME'
    request_version: str='TRANSPORT_SETTLEMENT_REQUEST_V1'

    def validate_protocol(self):
        if not all((self.id,self.origin_node_id,self.destination_node_id,
                    self.support_account_id,self.transport_account_id,
                    self.transport_relationship_id,self.technology_state_id)):
            raise ValueError('transport settlement request identity incomplete')
        if self.origin_node_id==self.destination_node_id:
            raise ValueError('transport settlement request direction invalid')
        if D(self.departure_time)<0 or self.requested_residents<0 or D(self.support_cost)<0:
            raise ValueError('transport settlement request values invalid')
        if tuple(self.required_fact_keys)!=TRANSPORT_SETTLEMENT_REQUIRED_FACT_KEYS:
            raise ValueError('transport settlement request must declare exact Test 012A fact contract')
        if not self.currency_unit or not self.population_unit or not self.time_unit:
            raise ValueError('transport settlement request units missing')
        return self


@dataclass(frozen=True)
class TransportSettlementDecision:
    id: str
    request_id: str
    actor_id: str
    outcome: TransportSettlementDecisionOutcome
    authorized_residents: int
    support_amount: D
    transport_amount: D
    relationship_id: str
    technology_state_id: str
    departure_time: D
    arrival_time: D
    reason: str
    reason_code: TransportSettlementReasonCode
    unknown_input_keys: tuple[str,...]=()
    input_snapshot_ref: str=''
    policy_version: str=''
    decision_version: str='TRANSPORT_SETTLEMENT_DECISION_V1'

    def validate_protocol(self,request:TransportSettlementRequest|None=None):
        if not self.id or not self.request_id or not self.actor_id:
            raise ValueError('transport settlement decision identity incomplete')
        if not self.input_snapshot_ref or not self.policy_version:
            raise ValueError('transport settlement decision requires snapshot and policy version')
        if self.authorized_residents<0 or min(D(self.support_amount),D(self.transport_amount))<0:
            raise ValueError('negative transport settlement authorization')
        if self.outcome==TransportSettlementDecisionOutcome.AUTHORIZE:
            if self.authorized_residents<=0:
                raise ValueError('AUTHORIZE requires positive resident count')
            if not self.relationship_id or not self.technology_state_id:
                raise ValueError('AUTHORIZE requires transport/technology identity')
            if D(self.arrival_time)<=D(self.departure_time):
                raise ValueError('transport arrival must follow departure')
        else:
            if self.authorized_residents!=0 or D(self.support_amount)!=0 or D(self.transport_amount)!=0:
                raise ValueError('non-AUTHORIZE transport decision cannot authorize values')
        if self.unknown_input_keys and self.outcome!=TransportSettlementDecisionOutcome.BLOCKED_UNKNOWN:
            raise ValueError('required unknown transport inputs must produce BLOCKED_UNKNOWN')
        if self.outcome==TransportSettlementDecisionOutcome.BLOCKED_UNKNOWN:
            if not self.unknown_input_keys:
                raise ValueError('BLOCKED_UNKNOWN requires unknown transport inputs')
            if self.reason_code!=TransportSettlementReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN:
                raise ValueError('BLOCKED_UNKNOWN requires blocked-unknown reason code')
        if request is not None:
            request.validate_protocol()
            if request.id!=self.request_id:
                raise ValueError('transport settlement decision/request lineage mismatch')
            if self.outcome==TransportSettlementDecisionOutcome.AUTHORIZE:
                if self.authorized_residents>request.requested_residents:
                    raise ValueError('transport settlement authorization exceeds request')
                if D(self.support_amount)!=D(request.support_cost):
                    raise ValueError('transport settlement support amount/request mismatch')
                if self.relationship_id!=request.transport_relationship_id:
                    raise ValueError('transport settlement relationship/request mismatch')
                if self.technology_state_id!=request.technology_state_id:
                    raise ValueError('transport settlement technology/request mismatch')
                if D(self.departure_time)!=D(request.departure_time):
                    raise ValueError('transport settlement departure/request mismatch')
        return self


@dataclass(frozen=True)
class PassengerTransportDepartureRecord:
    departure_id: str
    decision_id: str
    request_id: str
    actor_id: str
    technology_state_id: str
    relationship_id: str
    origin_node_id: str
    destination_node_id: str
    passengers: int
    support_amount: D
    transport_amount: D
    departure_time: D
    arrival_time: D
    earth_population_before: int
    earth_population_after: int
    in_transit_before: int
    in_transit_after: int
    total_population_before: int
    total_population_after: int
    subsidy_before: D
    subsidy_after: D
    support_transaction_id: str
    transport_transaction_id: str
    departure_event_id: str
    record_version: str='PASSENGER_TRANSPORT_DEPARTURE_RECORD_V1'

    def validate(self):
        if not self.departure_id or self.passengers<=0:
            raise ValueError('invalid passenger departure')
        if D(self.arrival_time)<=D(self.departure_time):
            raise ValueError('passenger departure arrival time invalid')
        if self.earth_population_after!=self.earth_population_before-self.passengers:
            raise ValueError('Earth departure population rollforward mismatch')
        if self.in_transit_after!=self.in_transit_before+self.passengers:
            raise ValueError('in-transit population rollforward mismatch')
        if self.total_population_after!=self.total_population_before:
            raise ValueError('population conservation mismatch at departure')
        if D(self.subsidy_after)!=D(self.subsidy_before)+D(self.support_amount):
            raise ValueError('settlement subsidy rollforward mismatch at departure')
        return self


@dataclass(frozen=True)
class PassengerTransportArrivalRecord:
    departure_id: str
    relationship_id: str
    destination_node_id: str
    passengers: int
    arrival_time: D
    in_transit_before: int
    in_transit_after: int
    offworld_population_before: int
    offworld_population_after: int
    total_population_before: int
    total_population_after: int
    arrival_event_id: str
    stage_event_id: str
    record_version: str='PASSENGER_TRANSPORT_ARRIVAL_RECORD_V1'

    def validate(self):
        if not self.departure_id or self.passengers<=0:
            raise ValueError('invalid passenger arrival')
        if self.in_transit_after!=self.in_transit_before-self.passengers:
            raise ValueError('in-transit arrival rollforward mismatch')
        if self.offworld_population_after!=self.offworld_population_before+self.passengers:
            raise ValueError('offworld arrival population rollforward mismatch')
        if self.total_population_after!=self.total_population_before:
            raise ValueError('population conservation mismatch at arrival')
        return self
