from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal as D
from hashlib import sha256
import json


SETTLEMENT_STAGE_RULE_VERSION='SETTLEMENT_STAGE_RULE_TEST011A_V0_1'


@dataclass(frozen=True)
class SettlementInfrastructurePlan:
    id: str
    year: int
    node_id: str
    source_account_id: str
    supplier_account_id: str
    infrastructure_cost: D
    habitat_capacity: int
    source_ref: str
    epistemic_status: str
    plan_version: str='SETTLEMENT_INFRASTRUCTURE_PLAN_V1'

    def validate(self):
        if not self.id or not self.node_id or not self.source_account_id or not self.supplier_account_id:
            raise ValueError('settlement infrastructure plan identity incomplete')
        if self.year<0 or D(self.infrastructure_cost)<0 or self.habitat_capacity<=0:
            raise ValueError('settlement infrastructure plan values invalid')
        if not self.source_ref or not self.epistemic_status:
            raise ValueError('settlement infrastructure plan provenance/standing missing')
        return self

    def fingerprint(self):
        payload={
            'id':self.id,'year':self.year,'node_id':self.node_id,
            'source_account_id':self.source_account_id,
            'supplier_account_id':self.supplier_account_id,
            'infrastructure_cost':str(self.infrastructure_cost),
            'habitat_capacity':self.habitat_capacity,
            'source_ref':self.source_ref,'epistemic_status':self.epistemic_status,
            'plan_version':self.plan_version,
        }
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()


@dataclass(frozen=True)
class SettlementInfrastructureRecord:
    year: int
    plan_id: str
    node_id: str
    outcome: str
    cost: D
    habitat_capacity_added: int
    infrastructure_before: D
    infrastructure_after: D
    habitat_capacity_before: int
    habitat_capacity_after: int
    transaction_id: str
    event_id: str
    record_version: str='SETTLEMENT_INFRASTRUCTURE_RECORD_V1'

    def validate(self):
        if self.outcome not in {'INSTALLED','BLOCKED_INSUFFICIENT_FUNDS'}:
            raise ValueError('unknown settlement infrastructure outcome')
        if min(D(self.cost),D(self.infrastructure_before),D(self.infrastructure_after))<0:
            raise ValueError('negative settlement infrastructure value')
        if min(self.habitat_capacity_added,self.habitat_capacity_before,self.habitat_capacity_after)<0:
            raise ValueError('negative settlement habitat capacity')
        if self.outcome=='INSTALLED':
            if not self.transaction_id:
                raise ValueError('installed infrastructure requires transaction')
            if D(self.infrastructure_after)!=D(self.infrastructure_before)+D(self.cost):
                raise ValueError('settlement infrastructure rollforward mismatch')
            if self.habitat_capacity_after!=self.habitat_capacity_before+self.habitat_capacity_added:
                raise ValueError('settlement habitat capacity rollforward mismatch')
        else:
            if self.transaction_id or D(self.cost)!=D('0') or self.habitat_capacity_added!=0:
                raise ValueError('blocked infrastructure attempt cannot realize cost/capacity')
            if D(self.infrastructure_after)!=D(self.infrastructure_before) or self.habitat_capacity_after!=self.habitat_capacity_before:
                raise ValueError('blocked infrastructure attempt changed state')
        return self


@dataclass(frozen=True)
class SettlementStageRecord:
    year: int
    node_id: str
    prior_stage: str
    new_stage: str
    productive_capital: D
    production_capacity: D
    population: int
    infrastructure: D
    habitat_capacity: int
    external_subsidy: D
    event_id: str
    rule_version: str=SETTLEMENT_STAGE_RULE_VERSION

    def validate(self):
        if self.new_stage not in {'PROSPECTING','EXTRACTION_ENCLAVE','DEPENDENT_SETTLEMENT'}:
            raise ValueError('unsupported Test 011A settlement stage')
        if min(D(self.productive_capital),D(self.production_capacity),D(self.infrastructure),D(self.external_subsidy))<0:
            raise ValueError('negative settlement aggregate value')
        if self.population<0 or self.habitat_capacity<0:
            raise ValueError('negative settlement population/capacity')
        return self


@dataclass(frozen=True)
class SettlementSupportExecutionRecord:
    year: int
    actor_id: str
    decision_id: str
    node_id: str
    authorized_residents: int
    support_amount: D
    earth_population_before: int
    earth_population_after: int
    offworld_population_before: int
    offworld_population_after: int
    total_population_before: int
    total_population_after: int
    subsidy_before: D
    subsidy_after: D
    support_transaction_id: str
    migration_event_id: str
    stage_event_id: str
    record_version: str='SETTLEMENT_SUPPORT_EXECUTION_RECORD_V1'

    def validate(self):
        if self.authorized_residents<=0 or D(self.support_amount)<0:
            raise ValueError('invalid settlement support execution')
        if self.earth_population_after!=self.earth_population_before-self.authorized_residents:
            raise ValueError('Earth migration rollforward mismatch')
        if self.offworld_population_after!=self.offworld_population_before+self.authorized_residents:
            raise ValueError('offworld migration rollforward mismatch')
        if self.total_population_after!=self.total_population_before:
            raise ValueError('population conservation mismatch')
        if D(self.subsidy_after)!=D(self.subsidy_before)+D(self.support_amount):
            raise ValueError('settlement subsidy rollforward mismatch')
        return self


def derive_settlement_stage(productive_capacity,population,infrastructure,
                            habitat_capacity,external_subsidy):
    capacity=D(productive_capacity)
    infrastructure=D(infrastructure)
    subsidy=D(external_subsidy)
    population=int(population)
    habitat_capacity=int(habitat_capacity)
    if capacity<=0:
        return 'PROSPECTING'
    if population>0 and infrastructure>0 and habitat_capacity>=population and subsidy>0:
        return 'DEPENDENT_SETTLEMENT'
    return 'EXTRACTION_ENCLAVE'
