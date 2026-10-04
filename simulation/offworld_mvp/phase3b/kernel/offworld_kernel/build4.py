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
    written_off: D = D('0')

    @property
    def remaining_wip(self):
        return self.accumulated_cost-self.commissioned-self.written_off

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
        self.boundary_opening_balance = {}
        self.asset_depreciation = {}
        self.knowledge_amortization = {}
        self.event_log = []

    def add_account(self,account_id,owner_id,node_id,kind,balance=D('0')):
        super().add_account(account_id,owner_id,node_id,kind,balance)
        if kind==AccountKind.EARTH_BOUNDARY:
            self.boundary_opening_balance[account_id]=D(balance)
            self.boundary_net.setdefault(account_id,D('0'))

    def transfer(self,year,source,destination,amount,purpose,supplier_location=None,asset_location=None,parent_ids=()):
        tx=super().transfer(year,source,destination,amount,purpose,supplier_location,asset_location,parent_ids)
        amount=D(amount)
        if self.state.accounts[source].kind==AccountKind.EARTH_BOUNDARY:
            self.boundary_net[source]=self.boundary_net.get(source,D('0'))-amount
        if self.state.accounts[destination].kind==AccountKind.EARTH_BOUNDARY:
            self.boundary_net[destination]=self.boundary_net.get(destination,D('0'))+amount
        return tx

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



    def distribute_vehicle_to_owners(self,year,vehicle_id,vehicle_account,owner_accounts,amount):
        amount=D(amount); stakes=[s for s in self.ownership_stakes if s.vehicle_id==vehicle_id]
        self.assert_vehicle_ownership(vehicle_id)
        if self.state.accounts[vehicle_account].balance<amount: raise InvariantError('vehicle funds unavailable')
        paid=D('0')
        for i,s in enumerate(stakes):
            part=amount-paid if i==len(stakes)-1 else amount*s.share
            self.transfer(year,vehicle_account,owner_accounts[s.owner_id],part,TxPurpose.RETURN_TO_EARTH)
            paid+=part
        if paid!=amount: raise InvariantError('A6 disposition not exhaustive')
        self.audit('OWNER_DISTRIBUTION',year,vehicle=vehicle_id,amount=amount)
        return paid

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
        if amount<=0 or w.commissioned!=0 or w.written_off!=0:
            raise InvariantError('invalid WIP expenditure')
        supplier=self.state.accounts[supplier_account].node_id
        if self.state.nodes[supplier].kind==NodeKind.OFFWORLD:
            self.consume_supply(supplier,year,amount)
        else:
            constraint=self.resource_constraints.get((supplier,year))
            if constraint is None or amount>constraint.reserved:
                raise InvariantError('unreserved Earth-supplied WIP expenditure')
            constraint.reserved-=amount; constraint.spent+=amount
            key=(supplier,year)
            total=self.state.earth_impact.qualifying_supplied_expenditure.get(key,D('0'))+amount
            self.state.earth_impact.qualifying_supplied_expenditure[key]=total
            self.state.earth_impact.terrestrial_fcf_delta[key]=-self.lambda_displacement*total
        tx=self.transfer(year,p.cash_account_id,supplier_account,amount,TxPurpose.CAPEX,
                         supplier_location=supplier,asset_location=w.node_id,parent_ids=(w.project_id,wip_id))
        w.accumulated_cost+=amount
        self.state.fcf_events.append(FixedCapitalFormationEvent(self._id('fcf'),year,w.project_id,wip_id,
            tuple(sorted(p.owners)),tuple(financing_origin_nodes),supplier,w.node_id,amount,'WIP',(tx.id,)))
        self.audit('WIP_ADDITION',year,wip=wip_id,amount=amount)
        return tx

    def commission_wip(self,year,wip_id,asset_id,capacity=D('0')):
        w=self.wip[wip_id]
        if w.accumulated_cost<=0 or w.commissioned!=0 or w.written_off!=0 or w.remaining_wip!=w.accumulated_cost:
            raise InvariantError('invalid commissioning')
        if asset_id in self.state.assets:
            raise InvariantError('duplicate commissioned asset')
        self.state.assets[asset_id]=Asset(asset_id,w.project_id,w.node_id,AssetKind.PRODUCTIVE,w.accumulated_cost,D(capacity))
        w.commissioned=w.accumulated_cost
        self.audit('COMMISSION',year,wip=wip_id,asset=asset_id,value=w.commissioned)

    def write_off_wip(self,year,wip_id,reason='DEVELOPMENT_FAILED'):
        w=self.wip[wip_id]
        amount=w.remaining_wip
        if amount<0:
            raise InvariantError('negative WIP remaining')
        if amount==0:
            return D('0')
        w.written_off+=amount
        self.audit('WIP_WRITE_OFF',year,wip=wip_id,amount=amount,reason=str(reason))
        return amount

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

    def boundary_purchase(self,year,boundary_account,seller_account,amount,resource_id,quantity,parent_ids=()):
        amount=D(amount); q=D(quantity); b=self.state.accounts[boundary_account]; s=self.state.accounts[seller_account]
        if b.kind!=AccountKind.EARTH_BOUNDARY or amount<0 or q<0: raise InvariantError('invalid boundary purchase')
        if boundary_account not in self.boundary_opening_balance:
            prior_ledger=sum((t.amount for t in self.state.transactions if t.destination_account==boundary_account),D('0'))-sum((t.amount for t in self.state.transactions if t.source_account==boundary_account),D('0'))
            self.boundary_opening_balance[boundary_account]=b.balance-prior_ledger
        b.balance-=amount; s.balance+=amount
        self.boundary_net[boundary_account]=self.boundary_net.get(boundary_account,D('0'))-amount
        parents=(resource_id,*tuple(parent_ids))
        tx=Transaction(self._id('tx'),year,boundary_account,seller_account,amount,TxPurpose.REVENUE,b.node_id,s.node_id,parent_ids=parents)
        self.state.transactions.append(tx)
        seller_project_offworld=(s.kind==AccountKind.PROJECT_CASH and self.state.nodes[s.node_id].kind==NodeKind.OFFWORLD)
        if seller_project_offworld:
            self._earth_shadow_add_currency('earth_purchases_from_offworld',b.node_id,year,amount)
        key=(b.node_id,resource_id); self.market_resource_inventory[key]=self.market_resource_inventory.get(key,D('0'))+q
        self.audit('BOUNDARY_PURCHASE',year,account=boundary_account,amount=amount,resource=resource_id,quantity=q)
        return tx

    def consume_market_resource(self,year,node_id,resource_id,quantity):
        key=(node_id,resource_id); q=D(quantity); have=self.market_resource_inventory.get(key,D('0'))
        if q<0 or q>have: raise InvariantError('market resource unavailable')
        self.market_resource_inventory[key]=have-q; self.audit('RESOURCE_CONSUME',year,node=node_id,resource=resource_id,quantity=q)

    def _assert_boundary_reconciliation(self):
        boundary_ids=[aid for aid,a in self.state.accounts.items() if a.kind==AccountKind.EARTH_BOUNDARY]
        for aid in boundary_ids:
            baseline=self.boundary_opening_balance.get(aid,D('0'))
            account_delta=self.state.accounts[aid].balance-baseline
            ledger_delta=sum((t.amount for t in self.state.transactions if t.destination_account==aid),D('0'))-sum((t.amount for t in self.state.transactions if t.source_account==aid),D('0'))
            mirror=self.boundary_net.get(aid,D('0'))
            if account_delta!=ledger_delta:
                raise InvariantError(f'boundary account/ledger reconciliation {aid}')
            if mirror!=ledger_delta:
                raise InvariantError(f'boundary mirror reconciliation {aid}')

    def assert_build4_invariants(self):
        self.assert_mvp_invariants()
        self._assert_boundary_reconciliation()
        for c in self.state.commitments.values():
            if c.committed!=c.disbursed+c.lapsed+c.outstanding: raise InvariantError('A3 commitment identity')
        for w in self.wip.values():
            if w.accumulated_cost<0 or w.commissioned<0 or w.written_off<0 or w.commissioned+w.written_off>w.accumulated_cost: raise InvariantError('A5 WIP rollforward')
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
          'wip':sorted((w.id,w.project_id,w.node_id,str(w.accumulated_cost),str(w.commissioned),str(w.written_off)) for w in self.wip.values()),
          'supply':sorted((n,y,str(s.capacity),str(s.used)) for (n,y),s in self.supply.items()),
          'carry':sorted((r.id,r.node_id,r.project_id,str(r.amount),r.reserved_year,r.expiry_year,str(r.spent),str(r.lapsed)) for r in self.carry_reservations.values()),
          'boundary':sorted((k,str(v)) for k,v in self.boundary_net.items()),
          'boundary_opening':sorted((k,str(v)) for k,v in self.boundary_opening_balance.items()),
          'depreciation':sorted((a,y,str(v)) for (a,y),v in self.asset_depreciation.items()),
          'knowledge_amortization':sorted((a,y,str(v)) for (a,y),v in self.knowledge_amortization.items())}
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

    def uniformity_sample(self,n=10000):
        vals=[float(self.keyed_draw('UNIFORMITY',i)) for i in range(n)]
        return sum(vals)/n,min(vals),max(vals)
