from __future__ import annotations
from hashlib import sha256
import json
from .kernel import Kernel, InvariantError
from .model import *
from .mvp_state import *

class MVPKernel(Kernel):
    """Authorized deterministic MVP causal-loop kernel. Policies are scripted validation drivers, not autonomous agents."""
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.agents: Dict[str,AgentState]={}; self.resources: Dict[str,ScenarioResource]={}
        self.observations: Dict[str,Observation]={}; self.financing_requests: Dict[str,FinancingRequest]={}
        self.financing_decisions: Dict[str,FinancingDecision]={}; self.colonies: Dict[str,ColonyState]={}
        self.events: List[CausalEvent]=[]; self.population: Optional[PopulationLedger]=None

    def add_agent(self,a:AgentState):
        if a.id in self.agents or a.account_id not in self.state.accounts: raise InvariantError('invalid agent')
        self.agents[a.id]=a

    def add_resource(self,r:ScenarioResource):
        if min(r.in_situ,r.accessible,r.recoverable,r.remaining)<0 or not (r.recoverable<=r.accessible<=r.in_situ) or r.remaining>r.recoverable:
            raise InvariantError('resource hierarchy')
        self.resources[r.id]=r

    def event(self,year,actor,action,result,inputs=(),parents=()):
        e=CausalEvent(self._id('evt'),year,actor,action,tuple(inputs),result,tuple(parents)); self.events.append(e)
        if actor in self.agents: self.agents[actor].history.append(e.id)
        return e

    def observe(self,year,actor_id,resource_id,channel,public=False):
        a=self.agents[actor_id]; r=self.resources[resource_id]
        if 'EXPLORE' not in a.capabilities: raise InvariantError('agent lacks exploration capability')
        # Deterministic validation observation. World truth is read only here; agent receives only the signal.
        signal='POSITIVE' if r.remaining>D('0') else 'NEGATIVE'
        o=Observation(self._id('obs'),year,actor_id,resource_id,channel,signal,public); self.observations[o.id]=o
        recipients=self.agents.values() if public else (a,)
        for x in recipients:
            x.information.add(o.id)
            prior=x.beliefs.get(resource_id,D('0.5'))
            x.beliefs[resource_id]=min(D('0.95'),prior+D('0.30')) if signal=='POSITIVE' else max(D('0.05'),prior-D('0.30'))
        self.event(year,actor_id,ActionKind.EXPLORE,signal,(resource_id,o.id)); return o

    def request_finance(self,year,sponsor_id,project_id,amount,stage,disclosed=()):
        if self.agents[sponsor_id].kind!=AgentKind.PRIVATE_SPONSOR: raise InvariantError('requester not sponsor')
        for oid in disclosed:
            if oid not in self.agents[sponsor_id].information: raise InvariantError('cannot disclose unknown observation')
        q=FinancingRequest(self._id('req'),year,sponsor_id,project_id,D(amount),stage,tuple(disclosed)); self.financing_requests[q.id]=q
        self.event(year,sponsor_id,ActionKind.REQUEST_FINANCE,'REQUESTED',(q.id,project_id)); return q

    def decide_finance(self,request_id,financier_id,approve,reason='SCRIPTED_FIXTURE',instrument='EQUITY'):
        q=self.financing_requests[request_id]; f=self.agents[financier_id]
        if f.kind not in {AgentKind.PUBLIC,AgentKind.PRIVATE_FINANCIER,AgentKind.LOCAL_FINANCIER}: raise InvariantError('not financier')
        # Disclosure is an information transfer, never hidden-truth access.
        for oid in q.disclosed_observation_ids:
            f.information.add(oid)
            o=self.observations[oid]; prior=f.beliefs.get(o.resource_id,D('0.5'))
            f.beliefs[o.resource_id]=min(D('0.95'),prior+D('0.30')) if o.signal=='POSITIVE' else max(D('0.05'),prior-D('0.30'))
        d=FinancingDecision(self._id('dec'),q.id,financier_id,bool(approve),q.amount if approve else D('0'),instrument,reason)
        self.financing_decisions[d.id]=d
        self.event(q.year,financier_id,ActionKind.FINANCE,'APPROVED' if approve else 'REJECTED',(q.id,d.id))
        if approve:
            cid=self._id('commit'); self.add_commitment(cid,financier_id,q.project_id,q.amount)
            self.disburse(q.year,cid,f.account_id,q.amount)
        return d

    def extract(self,year,actor_id,resource_id,quantity,inventory_account=None):
        a=self.agents[actor_id]; r=self.resources[resource_id]; q=D(quantity)
        if 'EXTRACT' not in a.capabilities or q<0 or q>r.remaining: raise InvariantError('invalid extraction')
        r.remaining-=q
        if r.node_id not in self.colonies: self.colonies[r.node_id]=ColonyState(r.node_id)
        self.colonies[r.node_id].resource_inventory+=q
        return self.event(year,actor_id,ActionKind.EXTRACT,'EXTRACTED',(resource_id,str(q)))

    def sell(self,year,actor_id,resource_id,quantity,unit_price,market_account):
        a=self.agents[actor_id]; r=self.resources[resource_id]; c=self.colonies[r.node_id]; q=D(quantity); price=D(unit_price)
        if q<0 or q>c.resource_inventory: raise InvariantError('inventory unavailable')
        value=q*price; c.resource_inventory-=q
        tx=self.transfer(year,market_account,a.account_id,value,TxPurpose.REVENUE,parent_ids=(resource_id,))
        self.event(year,actor_id,ActionKind.SELL,'SOLD',(resource_id,str(q),tx.id)); return value

    def migrate(self,year,actor_id,node_id,count):
        if self.population is None or count<0 or self.population.earth<count: raise InvariantError('invalid migration')
        if 'MIGRATE' not in self.agents[actor_id].capabilities: raise InvariantError('agent lacks migration capability')
        before=self.population.total(); self.population.earth-=count; self.population.offworld[node_id]=self.population.offworld.get(node_id,0)+count
        self.colonies.setdefault(node_id,ColonyState(node_id)).population+=count
        if self.population.total()!=before: raise InvariantError('population conservation')
        return self.event(year,actor_id,ActionKind.MIGRATE,'MIGRATED',(node_id,str(count)))

    def assert_mvp_invariants(self):
        self.assert_invariants()
        for r in self.resources.values():
            if min(r.remaining,r.recoverable,r.accessible,r.in_situ)<0 or not (r.remaining<=r.recoverable<=r.accessible<=r.in_situ): raise InvariantError('resource conservation')
        if self.population and self.population.total()<0: raise InvariantError('population')
        for d in self.financing_decisions.values():
            if d.request_id not in self.financing_requests or d.financier_id not in self.agents: raise InvariantError('decision lineage')

    def mvp_fingerprint(self):
        payload={'base':self.fingerprint(),'agents':sorted((a.id,a.kind.value,a.node_id,sorted(a.information),sorted((k,str(v)) for k,v in a.beliefs.items()),a.history) for a in self.agents.values()),
        'resources':sorted((r.id,str(r.in_situ),str(r.accessible),str(r.recoverable),str(r.remaining)) for r in self.resources.values()),
        'obs':sorted((o.id,o.actor_id,o.resource_id,o.signal,o.public) for o in self.observations.values()),
        'events':[(e.id,e.year,e.actor_id,e.action.value,e.result,e.inputs,e.parent_ids) for e in self.events],
        'population':None if self.population is None else (self.population.earth,sorted(self.population.offworld.items()))}
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
