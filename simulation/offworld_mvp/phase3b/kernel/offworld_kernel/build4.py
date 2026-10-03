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


    def create_carry_reservation(self,rid,node_id,project_id,amount,reserved_year,expiry_year):
        amount=D(amount)
        if expiry_year<reserved_year or amount<0: raise InvariantError('invalid carry reservation')
        self.carry_reservations[rid]=CarryReservation(rid,node_id,project_id,amount,reserved_year,expiry_year)
        self.audit('RESERVE',reserved_year,reservation=rid,amount=amount)

    def spend_carry_reservation(self,year,rid,amount):
        r=self.carry_reservations[rid]; amount=D(amount)
        if year>r.expiry_year or amount<0 or amount>r.outstanding: raise InvariantError('reservation unavailable')
        r.spent+=amount; self.audit('RESERVATION_SPEND',year,reservation=rid,amount=amount)

    def lapse_carry_reservation(self,year,rid):
        r=self.carry_reservations[rid]
        if year<r.reserved_year: raise InvariantError('premature lapse')
        amount=r.outstanding; r.lapsed+=amount; self.audit('RESERVATION_LAPSE',year,reservation=rid,amount=amount)

    def lapse_commitment(self,year,cid,amount=None):
        c=self.state.commitments[cid]; amount=c.outstanding if amount is None else D(amount)
        if amount<0 or amount>c.outstanding: raise InvariantError('invalid lapse')
        c.lapsed+=amount; self.audit('COMMITMENT_LAPSE',year,commitment=cid,amount=amount)

    def boundary_purchase(self,year,boundary_account,seller_account,amount,resource_id,quantity):
        amount=D(amount); q=D(quantity); b=self.state.accounts[boundary_account]; s=self.state.accounts[seller_account]
        if b.kind!=AccountKind.EARTH_BOUNDARY or amount<0 or q<0: raise InvariantError('invalid boundary purchase')
        b.balance-=amount; s.balance+=amount
        self.boundary_net[boundary_account]=self.boundary_net.get(boundary_account,D('0'))-amount
        tx=Transaction(self._id('tx'),year,boundary_account,seller_account,amount,TxPurpose.REVENUE,b.node_id,s.node_id,parent_ids=(resource_id,))
        self.state.transactions.append(tx)
        key=(b.node_id,resource_id); self.market_resource_inventory[key]=self.market_resource_inventory.get(key,D('0'))+q
        self.audit('BOUNDARY_PURCHASE',year,account=boundary_account,amount=amount,resource=resource_id,quantity=q)
        return tx

    def consume_market_resource(self,year,node_id,resource_id,quantity):
        key=(node_id,resource_id); q=D(quantity); have=self.market_resource_inventory.get(key,D('0'))
        if q<0 or q>have: raise InvariantError('market resource unavailable')
        self.market_resource_inventory[key]=have-q; self.audit('RESOURCE_CONSUME',year,node=node_id,resource=resource_id,quantity=q)

    def assert_build4_invariants(self):
        self.assert_mvp_invariants()
        for c in self.state.commitments.values():
            if c.committed!=c.disbursed+c.lapsed+c.outstanding: raise InvariantError('A3 commitment identity')
        for w in self.wip.values():
            if w.accumulated_cost<0 or w.commissioned<0 or w.commissioned>w.accumulated_cost: raise InvariantError('A5 WIP rollforward')
        for vehicle in {s.vehicle_id for s in self.ownership_stakes}: self.assert_vehicle_ownership(vehicle)
        for s in self.supply.values():
            if s.used<0 or s.used>s.capacity: raise InvariantError('M2 supply')
        for r in self.carry_reservations.values():
            if r.amount!=r.spent+r.lapsed+r.outstanding or r.outstanding<0: raise InvariantError('reservation identity')
        if any(q<0 for q in self.market_resource_inventory.values()): raise InvariantError('A9 market resource')
        if any(a.balance<0 for a in self.state.accounts.values() if a.kind!=AccountKind.EARTH_BOUNDARY): raise InvariantError('A2 negative non-boundary account')

    def build4_fingerprint(self):
        payload={'build3':self.build3_fingerprint(),'events':self.event_log,
          'ownership':sorted((s.vehicle_id,s.owner_id,s.owner_domicile,str(s.share)) for s in self.ownership_stakes),
          'wip':sorted((w.id,w.project_id,w.node_id,str(w.accumulated_cost),str(w.commissioned)) for w in self.wip.values()),
          'supply':sorted((n,y,str(s.capacity),str(s.used)) for (n,y),s in self.supply.items()),
          'carry':sorted((r.id,r.node_id,r.project_id,str(r.amount),r.reserved_year,r.expiry_year,str(r.spent),str(r.lapsed)) for r in self.carry_reservations.values()),
          'boundary':sorted((k,str(v)) for k,v in self.boundary_net.items()),
          'depreciation':sorted((a,y,str(v)) for (a,y),v in self.asset_depreciation.items()),
          'knowledge_amortization':sorted((a,y,str(v)) for (a,y),v in self.knowledge_amortization.items())}
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

    def uniformity_sample(self,n=10000):
        vals=[float(self.keyed_draw('UNIFORMITY',i)) for i in range(n)]
        return sum(vals)/n,min(vals),max(vals)
