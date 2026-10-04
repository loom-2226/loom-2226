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
    EXPLORE='EXPLORE'; PUBLISH='PUBLISH'; REQUEST_FINANCE='REQUEST_FINANCE'; FINANCE='FINANCE'; DEVELOP='DEVELOP'; CONSTRUCT='CONSTRUCT'; OPERATE='OPERATE'; FAIL='FAIL'; ABANDON='ABANDON'; EXTRACT='EXTRACT'; SELL='SELL'; MIGRATE='MIGRATE'; REINVEST='REINVEST'

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
    priors: Dict[str,D]=field(default_factory=dict)


BUILD5_SPONSOR_REQUIRED_FACT_KEYS=(
    'project.STATUS',
    'project.CASH_BALANCE',
    'underwriting.DEVELOPMENT_CAPEX',
)
BUILD5_SPONSOR_REQUIRED_BELIEF_KEYS=('resource_exists',)
BUILD5_SPONSOR_REQUIRED_PRIOR_KEYS=('resource_exists',)

class SponsorProjectDecisionOutcome(str, Enum):
    REQUEST_FINANCE='REQUEST_FINANCE'
    DEVELOP='DEVELOP'
    DEFER='DEFER'
    ABANDON='ABANDON'
    BLOCKED_UNKNOWN='BLOCKED_UNKNOWN'

class SponsorProjectReasonCode(str, Enum):
    POSITIVE_EVIDENCE_FINANCE_REQUIRED='POSITIVE_EVIDENCE_FINANCE_REQUIRED'
    POSITIVE_EVIDENCE_FUNDED='POSITIVE_EVIDENCE_FUNDED'
    NO_RELEVANT_INFORMATION='NO_RELEVANT_INFORMATION'
    NONPOSITIVE_EVIDENCE='NONPOSITIVE_EVIDENCE'
    CAPABILITY_OR_OBJECTIVE_BLOCK='CAPABILITY_OR_OBJECTIVE_BLOCK'
    PROJECT_STATE_BLOCK='PROJECT_STATE_BLOCK'
    BLOCKED_REQUIRED_INPUT_UNKNOWN='BLOCKED_REQUIRED_INPUT_UNKNOWN'

@dataclass(frozen=True)
class SponsorProjectDecisionRequest:
    id: str
    year: int
    project_id: str
    resource_id: str
    observation_id: str
    required_fact_keys: tuple[str,...]=()
    required_belief_keys: tuple[str,...]=()
    required_prior_keys: tuple[str,...]=()
    currency_unit: str='MODEL_CURRENCY'
    request_version: str='SPONSOR_PROJECT_DECISION_REQUEST_V1'

    def validate_protocol(self):
        if not self.id or not self.project_id or not self.resource_id:
            raise ValueError('sponsor project decision request identity incomplete')
        if self.year<0:
            raise ValueError('sponsor project decision request year invalid')
        if tuple(self.required_fact_keys)!=BUILD5_SPONSOR_REQUIRED_FACT_KEYS:
            raise ValueError('sponsor request must declare exact Test 005A fact contract')
        if tuple(self.required_belief_keys)!=BUILD5_SPONSOR_REQUIRED_BELIEF_KEYS:
            raise ValueError('sponsor request must declare exact Test 005A belief contract')
        if tuple(self.required_prior_keys)!=BUILD5_SPONSOR_REQUIRED_PRIOR_KEYS:
            raise ValueError('sponsor request must declare exact Test 005A prior contract')
        if not self.currency_unit:
            raise ValueError('sponsor request currency/unit missing')
        return self

@dataclass(frozen=True)
class SponsorProjectDecision:
    id: str
    request_id: str
    actor_id: str
    outcome: SponsorProjectDecisionOutcome
    requested_financing: D
    reason: str
    reason_code: SponsorProjectReasonCode
    unknown_input_keys: tuple[str,...]=()
    input_snapshot_ref: str=''
    policy_version: str=''
    decision_version: str='SPONSOR_PROJECT_DECISION_V1'

    def validate_protocol(self,request:SponsorProjectDecisionRequest|None=None):
        amount=D(self.requested_financing)
        if not self.id or not self.request_id or not self.actor_id:
            raise ValueError('sponsor project decision identity incomplete')
        if not self.input_snapshot_ref or not self.policy_version:
            raise ValueError('sponsor project decision requires snapshot and policy version')
        if self.outcome==SponsorProjectDecisionOutcome.REQUEST_FINANCE:
            if amount<=0:
                raise ValueError('REQUEST_FINANCE requires positive requested financing')
        elif amount!=D('0'):
            raise ValueError('non-financing sponsor outcome cannot request financing')
        if self.unknown_input_keys and self.outcome!=SponsorProjectDecisionOutcome.BLOCKED_UNKNOWN:
            raise ValueError('required unknown sponsor inputs must produce BLOCKED_UNKNOWN')
        if self.outcome==SponsorProjectDecisionOutcome.BLOCKED_UNKNOWN:
            if not self.unknown_input_keys:
                raise ValueError('BLOCKED_UNKNOWN requires unknown sponsor inputs')
            if self.reason_code!=SponsorProjectReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN:
                raise ValueError('BLOCKED_UNKNOWN requires blocked-unknown reason code')
        if request is not None:
            request.validate_protocol()
            if request.id!=self.request_id:
                raise ValueError('sponsor decision/request lineage mismatch')
        return self

BUILD5_OPERATING_REQUIRED_FACT_KEYS=(
    'project.STATUS',
    'project.CASH_BALANCE',
    'asset.CAPACITY',
    'underwriting.OPERATING_COST',
)
BUILD5_OPERATING_REQUIRED_BELIEF_KEYS=('resource_exists',)
BUILD5_OPERATING_REQUIRED_PRIOR_KEYS=('resource_exists',)

class OperatingCycleDecisionOutcome(str, Enum):
    REQUEST_FINANCE='REQUEST_FINANCE'
    OPERATE='OPERATE'
    DEFER='DEFER'
    BLOCKED_UNKNOWN='BLOCKED_UNKNOWN'

class OperatingCycleReasonCode(str, Enum):
    POSITIVE_EVIDENCE_FINANCE_REQUIRED='POSITIVE_EVIDENCE_FINANCE_REQUIRED'
    OPERATING_CYCLE_AUTHORIZED='OPERATING_CYCLE_AUTHORIZED'
    NONPOSITIVE_EVIDENCE='NONPOSITIVE_EVIDENCE'
    NO_RELEVANT_INFORMATION='NO_RELEVANT_INFORMATION'
    CAPABILITY_OR_OBJECTIVE_BLOCK='CAPABILITY_OR_OBJECTIVE_BLOCK'
    PROJECT_STATE_BLOCK='PROJECT_STATE_BLOCK'
    ASSET_OR_CAPACITY_BLOCK='ASSET_OR_CAPACITY_BLOCK'
    BLOCKED_REQUIRED_INPUT_UNKNOWN='BLOCKED_REQUIRED_INPUT_UNKNOWN'

@dataclass(frozen=True)
class OperatingCycleRequest:
    id: str
    year: int
    project_id: str
    resource_id: str
    asset_id: str
    observation_id: str
    required_fact_keys: tuple[str,...]=()
    required_belief_keys: tuple[str,...]=()
    required_prior_keys: tuple[str,...]=()
    currency_unit: str='MODEL_CURRENCY'
    quantity_unit: str='MODEL_RESOURCE_UNIT_BY_FAMILY'
    request_version: str='OPERATING_CYCLE_REQUEST_V1'

    def validate_protocol(self):
        if not self.id or not self.project_id or not self.resource_id or not self.asset_id:
            raise ValueError('operating-cycle request identity incomplete')
        if self.year<0:
            raise ValueError('operating-cycle request year invalid')
        if tuple(self.required_fact_keys)!=BUILD5_OPERATING_REQUIRED_FACT_KEYS:
            raise ValueError('operating request must declare exact Test 008A fact contract')
        if tuple(self.required_belief_keys)!=BUILD5_OPERATING_REQUIRED_BELIEF_KEYS:
            raise ValueError('operating request must declare exact Test 008A belief contract')
        if tuple(self.required_prior_keys)!=BUILD5_OPERATING_REQUIRED_PRIOR_KEYS:
            raise ValueError('operating request must declare exact Test 008A prior contract')
        if not self.currency_unit or not self.quantity_unit:
            raise ValueError('operating request unit contract missing')
        return self

@dataclass(frozen=True)
class OperatingCycleDecision:
    id: str
    request_id: str
    actor_id: str
    outcome: OperatingCycleDecisionOutcome
    requested_financing: D
    planned_quantity: D
    authorized_opex: D
    reason: str
    reason_code: OperatingCycleReasonCode
    unknown_input_keys: tuple[str,...]=()
    input_snapshot_ref: str=''
    policy_version: str=''
    decision_version: str='OPERATING_CYCLE_DECISION_V1'

    def validate_protocol(self,request:OperatingCycleRequest|None=None):
        financing=D(self.requested_financing)
        quantity=D(self.planned_quantity)
        opex=D(self.authorized_opex)
        if not self.id or not self.request_id or not self.actor_id:
            raise ValueError('operating-cycle decision identity incomplete')
        if not self.input_snapshot_ref or not self.policy_version:
            raise ValueError('operating-cycle decision requires snapshot and policy version')
        if min(financing,quantity,opex)<0:
            raise ValueError('negative operating-cycle decision value')
        if self.outcome==OperatingCycleDecisionOutcome.REQUEST_FINANCE:
            if financing<=0 or quantity!=0 or opex!=0:
                raise ValueError('REQUEST_FINANCE requires positive finance and no operation authorization')
        elif self.outcome==OperatingCycleDecisionOutcome.OPERATE:
            if financing!=0 or quantity<=0:
                raise ValueError('OPERATE requires positive planned quantity and no financing request')
        elif financing!=0 or quantity!=0 or opex!=0:
            raise ValueError('non-operating/non-financing outcome cannot authorize values')
        if self.unknown_input_keys and self.outcome!=OperatingCycleDecisionOutcome.BLOCKED_UNKNOWN:
            raise ValueError('required unknown operating inputs must produce BLOCKED_UNKNOWN')
        if self.outcome==OperatingCycleDecisionOutcome.BLOCKED_UNKNOWN:
            if not self.unknown_input_keys:
                raise ValueError('BLOCKED_UNKNOWN requires unknown operating inputs')
            if self.reason_code!=OperatingCycleReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN:
                raise ValueError('BLOCKED_UNKNOWN requires blocked-unknown reason code')
        if request is not None:
            request.validate_protocol()
            if request.id!=self.request_id:
                raise ValueError('operating decision/request lineage mismatch')
        return self

BUILD5_SALE_REQUIRED_FACT_KEYS=(
    'project.STATUS',
    'inventory.AVAILABLE',
    'market.UNIT_PRICE',
    'market.REMAINING_DEMAND',
)

class SaleDecisionOutcome(str, Enum):
    OFFER='OFFER'
    DEFER='DEFER'
    BLOCKED_UNKNOWN='BLOCKED_UNKNOWN'

class SaleReasonCode(str, Enum):
    MARKET_OFFER_AUTHORIZED='MARKET_OFFER_AUTHORIZED'
    NO_SELLABLE_INVENTORY='NO_SELLABLE_INVENTORY'
    NO_POSITIVE_PRICE='NO_POSITIVE_PRICE'
    NO_MARKET_DEMAND='NO_MARKET_DEMAND'
    NO_RELEVANT_INFORMATION='NO_RELEVANT_INFORMATION'
    CAPABILITY_OR_OBJECTIVE_BLOCK='CAPABILITY_OR_OBJECTIVE_BLOCK'
    PROJECT_STATE_BLOCK='PROJECT_STATE_BLOCK'
    BLOCKED_REQUIRED_INPUT_UNKNOWN='BLOCKED_REQUIRED_INPUT_UNKNOWN'

@dataclass(frozen=True)
class SaleDecisionRequest:
    id: str
    year: int
    project_id: str
    resource_id: str
    market_state_id: str
    observation_id: str
    required_fact_keys: tuple[str,...]=()
    currency_unit: str='MODEL_CURRENCY'
    quantity_unit: str='MODEL_RESOURCE_UNIT_BY_FAMILY'
    request_version: str='SALE_DECISION_REQUEST_V1'

    def validate_protocol(self):
        if not self.id or not self.project_id or not self.resource_id or not self.market_state_id:
            raise ValueError('sale request identity incomplete')
        if self.year<0:
            raise ValueError('sale request year invalid')
        if tuple(self.required_fact_keys)!=BUILD5_SALE_REQUIRED_FACT_KEYS:
            raise ValueError('sale request must declare exact Test 009A fact contract')
        if not self.currency_unit or not self.quantity_unit:
            raise ValueError('sale request unit contract missing')
        return self

@dataclass(frozen=True)
class SaleDecision:
    id: str
    request_id: str
    actor_id: str
    outcome: SaleDecisionOutcome
    offered_quantity: D
    reason: str
    reason_code: SaleReasonCode
    unknown_input_keys: tuple[str,...]=()
    input_snapshot_ref: str=''
    policy_version: str=''
    decision_version: str='SALE_DECISION_V1'

    def validate_protocol(self,request:SaleDecisionRequest|None=None):
        q=D(self.offered_quantity)
        if not self.id or not self.request_id or not self.actor_id:
            raise ValueError('sale decision identity incomplete')
        if not self.input_snapshot_ref or not self.policy_version:
            raise ValueError('sale decision requires snapshot and policy version')
        if q<0:
            raise ValueError('negative sale offer')
        if self.outcome==SaleDecisionOutcome.OFFER:
            if q<=0:
                raise ValueError('OFFER requires positive offered quantity')
        elif q!=D('0'):
            raise ValueError('non-OFFER sale decision cannot offer quantity')
        if self.unknown_input_keys and self.outcome!=SaleDecisionOutcome.BLOCKED_UNKNOWN:
            raise ValueError('required unknown sale inputs must produce BLOCKED_UNKNOWN')
        if self.outcome==SaleDecisionOutcome.BLOCKED_UNKNOWN:
            if not self.unknown_input_keys:
                raise ValueError('BLOCKED_UNKNOWN requires unknown sale inputs')
            if self.reason_code!=SaleReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN:
                raise ValueError('BLOCKED_UNKNOWN requires blocked-unknown reason code')
        if request is not None:
            request.validate_protocol()
            if request.id!=self.request_id:
                raise ValueError('sale decision/request lineage mismatch')
        return self

BUILD5_REQUIRED_UNDERWRITING_KEYS=(
    'underwriting.PRICE',
    'underwriting.EXPLORATION_CAPEX',
    'underwriting.DEVELOPMENT_CAPEX',
    'underwriting.OPERATING_COST',
    'underwriting.LEAD_TIME',
)
BUILD5_REQUIRED_BELIEF_KEYS=('resource_exists',)
BUILD5_REQUIRED_PRIOR_KEYS=('resource_exists',)

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
    BELOW_RETURN='BELOW_RETURN'
    CEILING='CEILING'
    CONCENTRATION='CONCENTRATION'
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
    required_belief_keys: tuple[str,...]=()
    required_prior_keys: tuple[str,...]=()
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
        if tuple(self.required_belief_keys)!=BUILD5_REQUIRED_BELIEF_KEYS:
            raise ValueError('financing request must declare exact Build 5 belief contract')
        if tuple(self.required_prior_keys)!=BUILD5_REQUIRED_PRIOR_KEYS:
            raise ValueError('financing request must declare exact Build 5 prior contract')
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


BUILD5_PUBLIC_EXPLORATION_REQUIRED_FACT_KEYS_BY_CHANNEL={
    'REMOTE':('exploration.REMOTE_COST',),
    'SURFACE':('exploration.SURFACE_COST',),
}
# Historical Test 002A compatibility alias.
BUILD5_PUBLIC_EXPLORATION_REQUIRED_FACT_KEYS=BUILD5_PUBLIC_EXPLORATION_REQUIRED_FACT_KEYS_BY_CHANNEL['REMOTE']

class ExplorationDecisionOutcome(str, Enum):
    AUTHORIZE='AUTHORIZE'
    DECLINE='DECLINE'
    DEFER='DEFER'
    BLOCKED_UNKNOWN='BLOCKED_UNKNOWN'

class ExplorationReasonCode(str, Enum):
    APPROVED_PUBLIC_INFORMATION_MISSION='APPROVED_PUBLIC_INFORMATION_MISSION'
    APPROVED_SURFACE_INFORMATION_MISSION='APPROVED_SURFACE_INFORMATION_MISSION'
    INSUFFICIENT_BUDGET='INSUFFICIENT_BUDGET'
    CAPABILITY_OR_OBJECTIVE_BLOCK='CAPABILITY_OR_OBJECTIVE_BLOCK'
    DEFER_UNSUPPORTED_CHANNEL='DEFER_UNSUPPORTED_CHANNEL'
    DEFER_PREREQUISITE_OBSERVATION='DEFER_PREREQUISITE_OBSERVATION'
    BLOCKED_REQUIRED_INPUT_UNKNOWN='BLOCKED_REQUIRED_INPUT_UNKNOWN'

@dataclass(frozen=True)
class ExplorationRequest:
    id: str
    year: int
    project_id: str
    resource_id: str
    channel: str
    required_fact_keys: tuple[str,...]=()
    prerequisite_observation_id: str=''
    currency_unit: str='MODEL_CURRENCY'
    request_version: str='EXPLORATION_REQUEST_V1'

    def validate_protocol(self):
        if not self.id or not self.project_id or not self.resource_id:
            raise ValueError('exploration request identity incomplete')
        if self.year<0:
            raise ValueError('exploration request year invalid')
        if self.channel not in BUILD5_PUBLIC_EXPLORATION_REQUIRED_FACT_KEYS_BY_CHANNEL:
            raise ValueError('unsupported exploration channel')
        expected=BUILD5_PUBLIC_EXPLORATION_REQUIRED_FACT_KEYS_BY_CHANNEL[self.channel]
        if tuple(self.required_fact_keys)!=tuple(expected):
            raise ValueError('exploration request fact contract/channel mismatch')
        if self.channel=='REMOTE':
            if self.prerequisite_observation_id:
                raise ValueError('REMOTE request cannot require prior observation')
        elif self.channel=='SURFACE':
            if not self.prerequisite_observation_id:
                raise ValueError('SURFACE request requires prior observation')
        if not self.currency_unit:
            raise ValueError('exploration request currency/unit missing')
        return self

@dataclass(frozen=True)
class ExplorationDecision:
    id: str
    request_id: str
    actor_id: str
    authorized: bool
    authorized_cost: D
    channel: str
    reason: str
    outcome: ExplorationDecisionOutcome
    reason_code: ExplorationReasonCode
    unknown_input_keys: tuple[str,...]=()
    input_snapshot_ref: str=''
    policy_version: str=''
    decision_version: str='EXPLORATION_DECISION_V1'

    def validate_protocol(self,request:ExplorationRequest|None=None):
        cost=D(self.authorized_cost)
        if not self.id or not self.request_id or not self.actor_id:
            raise ValueError('exploration decision identity incomplete')
        if not self.input_snapshot_ref or not self.policy_version:
            raise ValueError('exploration decision requires snapshot and policy version')
        if self.outcome==ExplorationDecisionOutcome.AUTHORIZE:
            if not self.authorized or cost<=0:
                raise ValueError('AUTHORIZE requires authorized=true and positive cost')
            if self.channel not in {'REMOTE','SURFACE'}:
                raise ValueError('AUTHORIZE channel invalid')
        else:
            if self.authorized or cost!=D('0'):
                raise ValueError('non-AUTHORIZE exploration decision cannot authorize spending')
        if self.unknown_input_keys and self.outcome!=ExplorationDecisionOutcome.BLOCKED_UNKNOWN:
            raise ValueError('required unknown exploration inputs must produce BLOCKED_UNKNOWN')
        if self.outcome==ExplorationDecisionOutcome.BLOCKED_UNKNOWN:
            if not self.unknown_input_keys:
                raise ValueError('BLOCKED_UNKNOWN requires unknown input keys')
            if self.reason_code!=ExplorationReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN:
                raise ValueError('BLOCKED_UNKNOWN requires blocked-unknown reason code')
        if request is not None:
            request.validate_protocol()
            if request.id!=self.request_id:
                raise ValueError('exploration decision/request lineage mismatch')
            if self.channel!=request.channel:
                raise ValueError('exploration decision/request channel mismatch')
        return self


class PublicationDecisionOutcome(str, Enum):
    PUBLISH='PUBLISH'
    WITHHOLD='WITHHOLD'

class PublicationReasonCode(str, Enum):
    PUBLISH_PUBLIC_INFORMATION='PUBLISH_PUBLIC_INFORMATION'
    OBSERVATION_NOT_POSSESSED='OBSERVATION_NOT_POSSESSED'
    OBJECTIVE_OR_CLASS_BLOCK='OBJECTIVE_OR_CLASS_BLOCK'

@dataclass(frozen=True)
class PublicationRequest:
    id: str
    year: int
    observation_id: str
    audience: str='PUBLIC_FINANCIERS'
    request_version: str='PUBLICATION_REQUEST_V1'

    def validate_protocol(self):
        if not self.id or not self.observation_id or not self.audience:
            raise ValueError('publication request identity incomplete')
        if self.year<0:
            raise ValueError('publication request year invalid')
        return self

@dataclass(frozen=True)
class PublicationDecision:
    id: str
    request_id: str
    actor_id: str
    publish: bool
    reason: str
    outcome: PublicationDecisionOutcome
    reason_code: PublicationReasonCode
    input_snapshot_ref: str
    policy_version: str
    decision_version: str='PUBLICATION_DECISION_V1'

    def validate_protocol(self,request:PublicationRequest|None=None):
        if not self.id or not self.request_id or not self.actor_id:
            raise ValueError('publication decision identity incomplete')
        if not self.input_snapshot_ref or not self.policy_version:
            raise ValueError('publication decision requires snapshot and policy version')
        if self.publish!=(self.outcome==PublicationDecisionOutcome.PUBLISH):
            raise ValueError('publication decision boolean/outcome mismatch')
        if request is not None:
            request.validate_protocol()
            if request.id!=self.request_id:
                raise ValueError('publication decision/request lineage mismatch')
        return self

@dataclass(frozen=True)
class PublicInformationArtifact:
    id: str
    year: int
    publisher_id: str
    source_observation_id: str
    resource_id: str
    channel: str
    signal: str
    audience: str
    recipient_ids: tuple[str,...]
    artifact_version: str='PUBLIC_INFORMATION_ARTIFACT_V1'

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
