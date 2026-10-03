from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

D = Decimal
class NodeKind(str, Enum): EARTH='EARTH'; OFFWORLD='OFFWORLD'
class AccountKind(str, Enum): FUNDS='FUNDS'; PROJECT_CASH='PROJECT_CASH'; EARTH_BOUNDARY='EARTH_BOUNDARY'; SUPPLIER='SUPPLIER'
class AssetKind(str, Enum): WIP='WIP'; EXPLORATION_WIP='EXPLORATION_WIP'; KNOWLEDGE='KNOWLEDGE'; PRODUCTIVE='PRODUCTIVE'
class TxPurpose(str, Enum):
    DISBURSE='DISBURSE'; CAPEX='CAPEX'; EXPLORATION='EXPLORATION'; OPEX='OPEX'; REVENUE='REVENUE'
    RETURN_TO_EARTH='RETURN_TO_EARTH'; LOCAL_RETENTION='LOCAL_RETENTION'; LOCAL_REINVESTMENT='LOCAL_REINVESTMENT'; OTHER_INVESTMENT='OTHER_INVESTMENT'; RESERVE='RESERVE'

@dataclass(frozen=True)
class Node: id: str; kind: NodeKind
@dataclass
class Account: id: str; owner_id: str; node_id: str; kind: AccountKind; balance: D = D('0')
@dataclass(frozen=True)
class Transaction:
    id: str; year: int; source_account: str; destination_account: str; amount: D; purpose: TxPurpose
    source_location: str; destination_location: str; supplier_location: Optional[str]=None; asset_location: Optional[str]=None; parent_ids: tuple[str,...]=()
@dataclass
class Commitment:
    id: str; financier_id: str; project_id: str; amount: D; committed: D=D('0'); disbursed: D=D('0'); lapsed: D=D('0')
    @property
    def outstanding(self): return self.committed-self.disbursed-self.lapsed
@dataclass
class Project: id: str; node_id: str; cash_account_id: str; owners: Dict[str,D]=field(default_factory=dict); status: str='PROPOSED'
@dataclass
class Asset: id: str; project_id: str; node_id: str; kind: AssetKind; book_value: D; capacity: D=D('0')
@dataclass(frozen=True)
class FixedCapitalFormationEvent:
    id: str; year: int; project_id: str; asset_id: str; owner_ids: tuple[str,...]; financing_origin_nodes: tuple[str,...]
    supplier_node: str; asset_node: str; amount: D; asset_class: str; parent_ids: tuple[str,...]
@dataclass
class EarthImpactLedger:
    qualifying_supplied_expenditure: Dict[tuple[str,int],D]=field(default_factory=dict)
    terrestrial_fcf_delta: Dict[tuple[str,int],D]=field(default_factory=dict)
@dataclass
class KernelState:
    nodes: Dict[str,Node]=field(default_factory=dict); accounts: Dict[str,Account]=field(default_factory=dict)
    commitments: Dict[str,Commitment]=field(default_factory=dict); projects: Dict[str,Project]=field(default_factory=dict)
    assets: Dict[str,Asset]=field(default_factory=dict); transactions: List[Transaction]=field(default_factory=list)
    fcf_events: List[FixedCapitalFormationEvent]=field(default_factory=list); earth_impact: EarthImpactLedger=field(default_factory=EarthImpactLedger)