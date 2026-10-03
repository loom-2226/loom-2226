from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from hashlib import sha256
import json
from typing import Dict
from .mvp_kernel import MVPKernel
from .kernel import InvariantError
from .mvp_state import *
from .model import *

@dataclass(frozen=True)
class RunIdentity:
    universe_id: str
    universe_version: str
    input_snapshot_id: str
    code_contract: str
    parameters: tuple[tuple[str,str],...]

@dataclass
class ResourceAllocationConstraint:
    node_id: str; year: int; reference_fcf: D; allocation_fraction: D; reserved: D=D('0'); spent: D=D('0')
    @property
    def ceiling(self): return self.reference_fcf*self.allocation_fraction
    @property
    def available(self): return self.ceiling-self.reserved-self.spent

class Build3Kernel(MVPKernel):
    """Build-3 deterministic validation kernel. Still not autonomous policy authority."""
    def __init__(self, run_identity:RunIdentity, *a, **kw):
        super().__init__(*a, **kw); self.run_identity=run_identity
        self.market_resource_inventory: Dict[tuple[str,str],D]={}
        self.resource_constraints: Dict[tuple[str,int],ResourceAllocationConstraint]={}
        self.exploration_resolution: Dict[str,str]={}

    def keyed_draw(self,*keys):
        raw='|'.join((self.run_identity.universe_id,self.run_identity.universe_version,*map(str,keys)))
        n=int.from_bytes(sha256(raw.encode()).digest()[:8],'big')
        return D(n)/D(2**64)

    def set_resource_constraint(self,node_id,year,reference_fcf,allocation_fraction):
        c=ResourceAllocationConstraint(node_id,year,D(reference_fcf),D(allocation_fraction))
        if c.reference_fcf<0 or not D('0')<=c.allocation_fraction<=D('1'): raise InvariantError('invalid allocation constraint')
        self.resource_constraints[(node_id,year)]=c; return c

    def reserve_earth_supply(self,node_id,year,amount):
        c=self.resource_constraints[(node_id,year)]; amount=D(amount)
        if amount<0 or amount>c.available: raise InvariantError('Earth FCF resource proxy ceiling exceeded')
        c.reserved+=amount

    def spend_reserved_capex(self,year,project_id,supplier_account,amount,asset_id,asset_node,asset_class='PRODUCTIVE',financing_origin_nodes=None):
        supplier=self.state.accounts[supplier_account].node_id; amount=D(amount)
        if self.state.nodes[supplier].kind==NodeKind.EARTH:
            c=self.resource_constraints[(supplier,year)]
            if amount>c.reserved: raise InvariantError('unreserved Earth-supplied expenditure')
            c.reserved-=amount; c.spent+=amount
        return self.spend_capex(year,project_id,supplier_account,amount,asset_id,asset_node,asset_class,financing_origin_nodes)

    def explore_paid(self,year,actor_id,resource_id,project_id,supplier_account,cost,channel='REMOTE',public=True,false_positive=D('0'),false_negative=D('0')):
        a=self.agents[actor_id]; r=self.resources[resource_id]; cost=D(cost); fp=D(false_positive); fn=D(false_negative)
        if 'EXPLORE' not in a.capabilities or not (D('0')<=fp<=D('1')) or not (D('0')<=fn<=D('1')): raise InvariantError('invalid exploration')
        p=self.state.projects[project_id]
        tx=self.transfer(year,p.cash_account_id,supplier_account,cost,TxPurpose.EXPLORATION,supplier_location=self.state.accounts[supplier_account].node_id,asset_location=r.node_id,parent_ids=(project_id,resource_id))
        aid=self._id('explore-wip'); self.state.assets[aid]=Asset(aid,project_id,r.node_id,AssetKind.EXPLORATION_WIP,cost)
        truth=r.remaining>D('0'); draw=self.keyed_draw('OBS',year,actor_id,resource_id,channel)
        positive=(draw>=fn) if truth else (draw<fp)
        signal='POSITIVE' if positive else 'NEGATIVE'
        o=Observation(self._id('obs'),year,actor_id,resource_id,channel,signal,public); self.observations[o.id]=o
        recipients=self.agents.values() if public else (a,)
        for x in recipients:
            x.information.add(o.id); prior=x.beliefs.get(resource_id,D('0.5'))
            x.beliefs[resource_id]=min(D('0.95'),prior+D('0.30')) if positive else max(D('0.05'),prior-D('0.30'))
        self.event(year,actor_id,ActionKind.EXPLORE,signal,(resource_id,o.id,tx.id,aid),())
        return o,aid,draw

    def resolve_exploration(self,asset_id,usable):
        a=self.state.assets[asset_id]
        if a.kind!=AssetKind.EXPLORATION_WIP: raise InvariantError('not exploration WIP')
        if usable:
            a.kind=AssetKind.KNOWLEDGE; self.exploration_resolution[asset_id]='KNOWLEDGE_ASSET'
        else:
            self.exploration_resolution[asset_id]='WRITE_OFF'; del self.state.assets[asset_id]
        return self.exploration_resolution[asset_id]

    def extract_bounded(self,year,actor_id,resource_id,requested):
        q=min(D(requested),self.resources[resource_id].remaining)
        self.extract(year,actor_id,resource_id,q); return q

    def sell_to_market(self,year,actor_id,resource_id,quantity,unit_price,market_account):
        q=D(quantity); value=self.sell(year,actor_id,resource_id,q,unit_price,market_account)
        node=self.state.accounts[market_account].node_id; key=(node,resource_id)
        self.market_resource_inventory[key]=self.market_resource_inventory.get(key,D('0'))+q
        return value

    def dispose_surplus(self,year,actor_id,source_account,amount,mode,earth_account=None,local_account=None):
        amount=D(amount)
        if mode=='ENCLAVE':
            if not earth_account: raise InvariantError('Earth return account required')
            tx=self.transfer(year,source_account,earth_account,amount,TxPurpose.RETURN_TO_EARTH)
            self.event(year,actor_id,ActionKind.REINVEST,'EARTH_RETURN',(tx.id,str(amount))); return 'EARTH_RETURN'
        if mode=='SETTLEMENT':
            if not local_account: raise InvariantError('local account required')
            tx=self.transfer(year,source_account,local_account,amount,TxPurpose.LOCAL_REINVESTMENT)
            self.event(year,actor_id,ActionKind.REINVEST,'LOCAL_REINVESTMENT',(tx.id,str(amount))); return 'LOCAL_REINVESTMENT'
        raise InvariantError('unknown disposition mode')

    def build3_fingerprint(self):
        payload={'mvp':self.mvp_fingerprint(),
          'run_identity':{'universe_id':self.run_identity.universe_id,'universe_version':self.run_identity.universe_version,
          'input_snapshot_id':self.run_identity.input_snapshot_id,'code_contract':self.run_identity.code_contract,'parameters':self.run_identity.parameters},
          'market_inventory':sorted((n,r,str(q)) for (n,r),q in self.market_resource_inventory.items()),
          'constraints':sorted((n,y,str(c.reference_fcf),str(c.allocation_fraction),str(c.reserved),str(c.spent)) for (n,y),c in self.resource_constraints.items()),
          'exploration_resolution':sorted(self.exploration_resolution.items())}
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
