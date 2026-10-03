from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
from .model import D

class RuntimeObjectClass(str, Enum):
    SYSTEM='SYSTEM'; AGGREGATE='AGGREGATE'; AGENT='AGENT'; ENTITY_ASSET='ENTITY_ASSET'

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
    runtime_class: RuntimeObjectClass=RuntimeObjectClass.AGENT
    objectives: tuple[str,...]=()
    decision_policy: str='SCRIPTED_VALIDATION_ONLY'
    information: set[str]=field(default_factory=set)
    beliefs: Dict[str,D]=field(default_factory=dict)
    history: List[str]=field(default_factory=list)

@dataclass(frozen=True)
class FinancingRequest:
    id: str; year: int; sponsor_id: str; project_id: str; amount: D; stage: str; disclosed_observation_ids: tuple[str,...]=()

@dataclass(frozen=True)
class FinancingDecision:
    id: str; request_id: str; financier_id: str; approved: bool; amount: D; instrument: str; reason: str

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
