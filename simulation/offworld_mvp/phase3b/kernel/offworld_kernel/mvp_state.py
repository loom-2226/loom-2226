from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
from .model import D

class RuntimeObjectClass(str, Enum):
    SYSTEM='SYSTEM'; AGGREGATE='AGGREGATE'; AGENT='AGENT'; ENTITY_ASSET='ENTITY_ASSET'

@dataclass
class SystemState:
    id: str
    process_type: str
    owned_state_refs: set[str]=field(default_factory=set)
    runtime_class: RuntimeObjectClass=RuntimeObjectClass.SYSTEM

@dataclass
class AggregateState:
    id: str
    node_id: str
    account_id: str
    member_count: int
    asset_refs: set[str]=field(default_factory=set)
    resource_holdings: Dict[str,D]=field(default_factory=dict)
    claim_holdings: Dict[str,D]=field(default_factory=dict)
    history_refs: List[str]=field(default_factory=list)
    runtime_class: RuntimeObjectClass=RuntimeObjectClass.AGGREGATE

@dataclass
class EntityAssetRef:
    id: str
    domain_type: str
    state_ref: str
    runtime_class: RuntimeObjectClass=RuntimeObjectClass.ENTITY_ASSET

class AgentKind(str, Enum):
    PUBLIC='PUBLIC'; PRIVATE_SPONSOR='PRIVATE_SPONSOR'; PRIVATE_FINANCIER='PRIVATE_FINANCIER'; LOCAL_FINANCIER='LOCAL_FINANCIER'

class ActionKind(str, Enum):
    EXPLORE='EXPLORE'; REQUEST_FINANCE='REQUEST_FINANCE'; FINANCE='FINANCE'; DEVELOP='DEVELOP'; EXTRACT='EXTRACT'; SELL='SELL'; MIGRATE='MIGRATE'; REINVEST='REINVEST'

@dataclass
class AgentState:
    id: str
    kind: AgentKind
    node_id: str
    account_id: str
    capabilities: set[str]=field(default_factory=set)
    objectives: tuple[str,...]=()
    runtime_class: RuntimeObjectClass=RuntimeObjectClass.AGENT
    decision_policy: str='SCRIPTED_VALIDATION_ONLY'
    information: set[str]=field(default_factory=set)
    beliefs: Dict[str,D]=field(default_factory=dict)
    history: List[str]=field(default_factory=list)
    asset_refs: set[str]=field(default_factory=set)
    resource_holdings: Dict[str,D]=field(default_factory=dict)
    claim_holdings: Dict[str,D]=field(default_factory=dict)
    lineage_refs: List[str]=field(default_factory=list)

BUILD5_REQUIRED_UNDERWRITING_KEYS=(
    'underwriting.PRICE',
    'underwriting.EXPLORATION_CAPEX',
    'underwriting.DEVELOPMENT_CAPEX',
    'underwriting.OPERATING_COST',
    'underwriting.LEAD_TIME',
)

class FinancingDecisionOutcome(str, Enum):
    APPROVE='APPROVE'
    REJECT='REJECT'
    DEFER='DEFER'
    BLOCKED_UNKNOWN='BLOCKED_UNKNOWN'

class FinancingReasonCode(str, Enum):
    SCRIPTED_VALIDATION='SCRIPTED_VALIDATION'
    APPROVED_POLICY_RULE='APPROVED_POLICY_RULE'
    REJECTED_RETURN='REJECTED_RETURN'
    REJECTED_RISK='REJECTED_RISK'
    DEFER_MORE_INFORMATION='DEFER_MORE_INFORMATION'
    BLOCKED_REQUIRED_INPUT_UNKNOWN='BLOCKED_REQUIRED_INPUT_UNKNOWN'
    REQUEST_INVALID='REQUEST_INVALID'
    INSUFFICIENT_CAPITAL='INSUFFICIENT_CAPITAL'
    CAPABILITY_OR_AUTHORITY_BLOCK='CAPABILITY_OR_AUTHORITY_BLOCK'

@dataclass(frozen=True)
class FinancingRequest:
    id: str
    year: int
    sponsor_id: str
    project_id: str
    amount: D
    stage: str
    disclosed_observation_ids: tuple[str,...]=()
    required_underwriting_keys: tuple[str,...]=()
    currency_unit: str='MODEL_CURRENCY'
    request_version: str='FINANCING_REQUEST_V1'

    def validate_protocol(self):
        if not self.id or not self.sponsor_id or not self.project_id or not self.stage:
            raise ValueError('financing request identity/stage incomplete')
        if D(self.amount)<=0:
            raise ValueError('financing request amount must be positive')
        if not self.currency_unit:
            raise ValueError('financing request currency/unit missing')
        if tuple(self.required_underwriting_keys)!=BUILD5_REQUIRED_UNDERWRITING_KEYS:
            raise ValueError('financing request must declare exact Build 5 underwriting input contract')
        if len(set(self.disclosed_observation_ids))!=len(self.disclosed_observation_ids):
            raise ValueError('duplicate disclosed observation id')
        return self

@dataclass(frozen=True)
class FinancingDecision:
    id: str
    request_id: str
    financier_id: str
    approved: bool
    amount: D
    instrument: str
    reason: str
    outcome: FinancingDecisionOutcome|None=None
    reason_code: FinancingReasonCode|None=None
    unknown_input_keys: tuple[str,...]=()
    input_snapshot_ref: str=''
    policy_version: str=''
    decision_version: str='FINANCING_DECISION_V1'

    def __post_init__(self):
        if self.outcome is None:
            object.__setattr__(self,'outcome',FinancingDecisionOutcome.APPROVE if self.approved else FinancingDecisionOutcome.REJECT)
        if self.reason_code is None:
            object.__setattr__(self,'reason_code',FinancingReasonCode.SCRIPTED_VALIDATION)

    def validate_protocol(self,request:FinancingRequest|None=None):
        amount=D(self.amount)
        if not self.id or not self.request_id or not self.financier_id:
            raise ValueError('financing decision identity incomplete')
        if not self.input_snapshot_ref or not self.policy_version:
            raise ValueError('financing decision requires snapshot and policy version')
        if amount<0:
            raise ValueError('negative financing decision amount')
        if self.outcome==FinancingDecisionOutcome.APPROVE:
            if not self.approved or amount<=0 or not self.instrument:
                raise ValueError('APPROVE requires approved=true, positive amount, and instrument')
        else:
            if self.approved or amount!=D('0'):
                raise ValueError('non-APPROVE outcome must not approve or fund')
        if self.unknown_input_keys and self.outcome!=FinancingDecisionOutcome.BLOCKED_UNKNOWN:
            raise ValueError('required unknown inputs must produce BLOCKED_UNKNOWN')
        if self.outcome==FinancingDecisionOutcome.BLOCKED_UNKNOWN:
            if not self.unknown_input_keys:
                raise ValueError('BLOCKED_UNKNOWN requires unknown input keys')
            if self.reason_code!=FinancingReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN:
                raise ValueError('BLOCKED_UNKNOWN requires blocked-unknown reason code')
        if request is not None:
            request.validate_protocol()
            if request.id!=self.request_id:
                raise ValueError('decision/request lineage mismatch')
            if self.outcome==FinancingDecisionOutcome.APPROVE and amount>D(request.amount):
                raise ValueError('approved amount exceeds request')
        return self

@dataclass
class ScenarioResource:
    id: str; node_id: str; family: str; in_situ: D; accessible: D; recoverable: D; remaining: D

@dataclass(frozen=True)
class Observation:
    id: str; year: int; actor_id: str; resource_id: str; channel: str; signal: str; public: bool

@dataclass
class ColonyState:
    node_id: str
    population: int=0
    cash: D=D('0')
    productive_capital: D=D('0')
    infrastructure: D=D('0')
    resource_inventory: D=D('0')
    import_inventory: D=D('0')
    production_capacity: D=D('0')
    operating_need: D=D('0')
    external_subsidy: D=D('0')
    stage: str='PROSPECTING'

@dataclass(frozen=True)
class CausalEvent:
    id: str; year: int; actor_id: str; action: ActionKind; inputs: tuple[str,...]; result: str; parent_ids: tuple[str,...]=()

@dataclass
class PopulationLedger:
    earth: int
    offworld: Dict[str,int]=field(default_factory=dict)
    def total(self): return self.earth + sum(self.offworld.values())
