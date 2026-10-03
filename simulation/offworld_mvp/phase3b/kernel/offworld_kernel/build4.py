from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from .build3 import Build3Kernel, RunIdentity
from .kernel import InvariantError
from .model import *

@dataclass
class OwnershipStake:
    vehicle_id: str
    owner_id: str
    owner_domicile: str
    share: D

@dataclass
class ConstructionWIP:
    id: str
    project_id: str
    node_id: str
    accumulated_cost: D = D('0')
    commissioned: D = D('0')

@dataclass
class SupplyCapacity:
    node_id: str
    year: int
    capacity: D
    used: D = D('0')
    @property
    def available(self): return self.capacity-self.used

@dataclass
class CarryReservation:
    id: str
    node_id: str
    project_id: str
    amount: D
    reserved_year: int
    expiry_year: int
    spent: D = D('0')
    lapsed: D = D('0')
    @property
    def outstanding(self): return self.amount-self.spent-self.lapsed

class Build4Kernel(Build3Kernel):
    def __init__(self, run_identity: RunIdentity, *args, **kwargs):
        super().__init__(run_identity, *args, **kwargs)
        self.ownership_stakes = []
        self.wip = {}
        self.supply = {}
        self.carry_reservations = {}
        self.boundary_net = {}
        self.asset_depreciation = {}
        self.knowledge_amortization = {}
        self.event_log = []

    def audit(self, kind, year, **data):
        cooked = {k: str(v) if isinstance(v,D) else v for k,v in data.items()}
        self.event_log.append({'seq':len(self.event_log)+1,'kind':kind,'year':year,**cooked})


    def register_vehicle_ownership(self, vehicle_id, contributions):
        total=sum((D(amount) for _,amount,_ in contributions),D('0'))
        if total<=0: raise InvariantError('ownership contribution total')
        self.ownership_stakes=[s for s in self.ownership_stakes if s.vehicle_id!=vehicle_id]
        for owner,amount,domicile in contributions:
            self.ownership_stakes.append(OwnershipStake(vehicle_id,owner,domicile,D(amount)/total))
        self.assert_vehicle_ownership(vehicle_id)

    def assert_vehicle_ownership(self, vehicle_id):
        total=sum((s.share for s in self.ownership_stakes if s.vehicle_id==vehicle_id),D('0'))
        if total!=D('1'): raise InvariantError('A7 ownership reconciliation')

    def set_supply_capacity(self,node_id,year,capacity):
        self.supply[(node_id,year)]=SupplyCapacity(node_id,year,D(capacity))

    def consume_supply(self,node_id,year,amount):
        s=self.supply[(node_id,year)]; amount=D(amount)
        if amount<0 or amount>s.available: raise InvariantError('M2 local supply capacity exceeded')
        s.used+=amount

    def create_wip(self,wip_id,project_id,node_id):
        if wip_id in self.wip: raise InvariantError('duplicate WIP')
        self.wip[wip_id]=ConstructionWIP(wip_id,project_id,node_id)

    def add_wip_expenditure(self,year,wip_id,supplier_account,amount,financing_origin_nodes=()):
        w=self.wip[wip_id]; p=self.state.projects[w.project_id]; amount=D(amount)
        supplier=self.state.accounts[supplier_account].node_id
        if self.state.nodes[supplier].kind==NodeKind.OFFWORLD: self.consume_supply(supplier,year,amount)
        tx=self.transfer(year,p.cash_account_id,supplier_account,amount,TxPurpose.CAPEX,
                         supplier_location=supplier,asset_location=w.node_id,parent_ids=(w.project_id,wip_id))
        w.accumulated_cost+=amount
        self.state.fcf_events.append(FixedCapitalFormationEvent(self._id('fcf'),year,w.project_id,wip_id,
            tuple(sorted(p.owners)),tuple(financing_origin_nodes),supplier,w.node_id,amount,'WIP',(tx.id,)))
        self.audit('WIP_ADDITION',year,wip=wip_id,amount=amount)
        return tx

    def commission_wip(self,year,wip_id,asset_id,capacity=D('0')):
        w=self.wip[wip_id]
        if w.accumulated_cost<=0 or w.commissioned!=0: raise InvariantError('invalid commissioning')
        self.state.assets[asset_id]=Asset(asset_id,w.project_id,w.node_id,AssetKind.PRODUCTIVE,w.accumulated_cost,D(capacity))
        w.commissioned=w.accumulated_cost
        self.audit('COMMISSION',year,wip=wip_id,asset=asset_id,value=w.commissioned)

    def depreciate(self,year,asset_id,rate):
        a=self.state.assets[asset_id]; rate=D(rate)
        if a.kind!=AssetKind.PRODUCTIVE or not D('0')<=rate<=D('1'): raise InvariantError('invalid depreciation')
        amount=a.book_value*rate; a.book_value-=amount; self.asset_depreciation[(asset_id,year)]=amount
        self.audit('DEPRECIATE',year,asset=asset_id,amount=amount); return amount

    def amortize_knowledge(self,year,asset_id,rate):
        a=self.state.assets[asset_id]; rate=D(rate)
        if a.kind!=AssetKind.KNOWLEDGE or not D('0')<=rate<=D('1'): raise InvariantError('invalid knowledge amortization')
        amount=a.book_value*rate; a.book_value-=amount; self.knowledge_amortization[(asset_id,year)]=amount
        self.audit('KNOWLEDGE_AMORTIZE',year,asset=asset_id,amount=amount); return amount
