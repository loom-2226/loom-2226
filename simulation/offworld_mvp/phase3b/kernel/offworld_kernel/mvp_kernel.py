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
        self.observations: Dict[str,Observation]={}; self.public_information: Dict[str,PublicInformationArtifact]={}; self.financing_requests: Dict[str,FinancingRequest]={}
        self.financing_decisions: Dict[str,FinancingDecision]={}; self.colonies: Dict[str,ColonyState]={}
        self.events: List[CausalEvent]=[]; self.population: Optional[PopulationLedger]=None

    def add_agent(self,a:AgentState):
        if a.runtime_class != RuntimeObjectClass.AGENT: raise InvariantError('non-agent cannot enter agent registry')
        if a.id in self.agents or a.account_id not in self.state.accounts: raise InvariantError('invalid agent')
        self.agents[a.id]=a

    def add_resource(self,r:ScenarioResource):
        if D(r.in_situ)<0 or (r.accessible is not None and not D('0')<=r.accessible<=r.in_situ) or (
            (r.recoverable is None) != (r.remaining is None)) or (
            r.recoverable is not None and (r.accessible is None or not D('0')<=r.remaining<=r.recoverable<=r.accessible)):
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
        signal='POSITIVE' if remaining_in_situ(r)>D('0') else 'NEGATIVE'
        o=Observation(self._id('obs'),year,actor_id,resource_id,channel,signal,public); self.observations[o.id]=o
        recipients=self.agents.values() if public else (a,)
        for x in recipients:
            x.information.add(o.id)
            prior=x.beliefs.get(resource_id,D('0.5'))
            x.beliefs[resource_id]=min(D('0.95'),prior+D('0.30')) if signal=='POSITIVE' else max(D('0.05'),prior-D('0.30'))
        self.event(year,actor_id,ActionKind.EXPLORE,signal,(resource_id,o.id)); return o

    def publish_observation(self,year,actor_id,observation_id,audience,recipient_models):
        """SYSTEM-side publication/transfer of an observation already possessed by the publisher.

        recipient_models entries are (agent_id, belief_key, detection_rate, false_positive_rate).
        They are recipient-side informational parameters. Hidden resource truth is not consulted here.
        """
        if actor_id not in self.agents:
            raise InvariantError('publisher agent missing')
        publisher=self.agents[actor_id]
        if observation_id not in self.observations or observation_id not in publisher.information:
            raise InvariantError('publisher does not possess observation')
        obs=self.observations[observation_id]
        recipients=[]
        for entry in recipient_models:
            if len(entry)!=4:
                raise InvariantError('recipient observation model malformed')
            recipient_id,belief_key,detection_rate,false_positive_rate=entry
            if recipient_id not in self.agents:
                raise InvariantError('publication recipient missing')
            detection=D(detection_rate); fp=D(false_positive_rate)
            if not (D('0')<=detection<=D('1')) or not (D('0')<=fp<=D('1')):
                raise InvariantError('recipient observation likelihood outside [0,1]')
            recipient=self.agents[recipient_id]
            if belief_key not in recipient.priors and belief_key not in recipient.beliefs:
                raise InvariantError('recipient prior/belief missing for published observation')
            prior=D(recipient.beliefs.get(belief_key,recipient.priors.get(belief_key)))
            if not (D('0')<=prior<=D('1')):
                raise InvariantError('recipient prior outside [0,1]')
            if obs.signal=='POSITIVE':
                num=detection*prior
                den=num+fp*(D('1')-prior)
            elif obs.signal=='NEGATIVE':
                num=(D('1')-detection)*prior
                den=num+(D('1')-fp)*(D('1')-prior)
            else:
                raise InvariantError('unsupported published observation signal')
            if den==0:
                raise InvariantError('degenerate recipient observation likelihood')
            recipient.beliefs[belief_key]=num/den
            recipients.append(str(recipient_id))

        artifact=PublicInformationArtifact(
            self._id('pubinfo'),int(year),str(actor_id),obs.id,obs.resource_id,obs.channel,
            obs.signal,str(audience),tuple(sorted(recipients)))
        self.public_information[artifact.id]=artifact
        for recipient_id in artifact.recipient_ids:
            recipient=self.agents[recipient_id]
            recipient.information.add(obs.id)
            recipient.information.add(artifact.id)
        self.event(year,actor_id,ActionKind.PUBLISH,'PUBLISHED',
                   (obs.id,artifact.id,artifact.audience,*artifact.recipient_ids))
        return artifact

    def submit_financing_request(self,request:FinancingRequest,parent_ids=()):
        request.validate_protocol()
        if request.id in self.financing_requests:
            raise InvariantError('duplicate financing request')
        if request.sponsor_id not in self.agents:
            raise InvariantError('financing request sponsor missing')
        sponsor=self.agents[request.sponsor_id]
        if sponsor.kind!=AgentKind.PRIVATE_SPONSOR:
            raise InvariantError('requester not sponsor')
        if request.project_id not in self.state.projects:
            raise InvariantError('financing request project missing')
        for oid in request.disclosed_observation_ids:
            if oid not in sponsor.information:
                raise InvariantError('cannot disclose unknown observation')
        self.financing_requests[request.id]=request
        self.event(request.year,request.sponsor_id,ActionKind.REQUEST_FINANCE,'REQUESTED',
                   (request.id,request.project_id,str(request.amount)),tuple(parent_ids))
        return request

    def transition_project_status(self,year,actor_id,project_id,new_status,reason_ref=''):
        if actor_id not in self.agents:
            raise InvariantError('project transition actor missing')
        if project_id not in self.state.projects:
            raise InvariantError('project transition project missing')
        actor=self.agents[actor_id]
        if actor.kind!=AgentKind.PRIVATE_SPONSOR:
            raise InvariantError('project transition requires sponsor')
        p=self.state.projects[project_id]
        old=str(p.status); new=str(new_status)
        # Test 005A earns only sponsor-controlled entry to DEVELOPMENT or
        # ABANDONED from pre-development states. Later lifecycle transitions
        # require their own governed semantics rather than inheriting a guess.
        allowed={
            'PROPOSED':{'DEVELOPMENT','ABANDONED'},
            'EXPLORING':{'DEVELOPMENT','ABANDONED'},
        }
        if old not in allowed or new not in allowed[old]:
            raise InvariantError(f'invalid bounded sponsor project transition: {old}->{new}')
        if new=='DEVELOPMENT' and 'DEVELOP' not in actor.capabilities:
            raise InvariantError('sponsor lacks development capability')
        p.status=new
        action=ActionKind.DEVELOP if new=='DEVELOPMENT' else ActionKind.ABANDON
        parents=(str(reason_ref),) if reason_ref else ()
        self.event(year,actor_id,action,new,(project_id,old,new),parents)
        return p

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
        if r.remaining is None: raise InvariantError('BLOCKED_UNKNOWN_RECOVERY')
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

    def migrate(self,year,actor_id,node_id,count,parent_ids=()):
        if self.population is None or count<0 or self.population.earth<count: raise InvariantError('invalid migration')
        if 'MIGRATE' not in self.agents[actor_id].capabilities: raise InvariantError('agent lacks migration capability')
        before=self.population.total(); self.population.earth-=count; self.population.offworld[node_id]=self.population.offworld.get(node_id,0)+count
        self._record_earth_migration(year,count)
        self.colonies.setdefault(node_id,ColonyState(node_id)).population+=count
        if self.population.total()!=before: raise InvariantError('population conservation')
        return self.event(year,actor_id,ActionKind.MIGRATE,'MIGRATED',(node_id,str(count)),tuple(parent_ids))

    def assert_mvp_invariants(self):
        self.assert_invariants()
        for r in self.resources.values():
            if D(r.in_situ)<0 or (r.accessible is not None and not D('0')<=r.accessible<=r.in_situ) or (
                (r.recoverable is None)!=(r.remaining is None)) or (
                r.recoverable is not None and (r.accessible is None or not D('0')<=r.remaining<=r.recoverable<=r.accessible)):
                raise InvariantError('resource conservation')
        if self.population and self.population.total()<0: raise InvariantError('population')
        for d in self.financing_decisions.values():
            if d.request_id not in self.financing_requests or d.financier_id not in self.agents: raise InvariantError('decision lineage')

    def mvp_fingerprint(self):
        payload={'base':self.fingerprint(),'agents':sorted((a.id,a.kind.value,a.node_id,a.account_id,tuple(sorted(a.capabilities)),tuple(a.objectives),a.runtime_class.value,a.decision_policy,tuple(sorted(a.information)),tuple(sorted((k,str(v)) for k,v in a.beliefs.items())),tuple(sorted((k,str(v)) for k,v in a.priors.items())),tuple(a.history),tuple(sorted(a.asset_refs)),tuple(sorted((k,str(v)) for k,v in a.resource_holdings.items())),tuple(sorted((k,str(v)) for k,v in a.claim_holdings.items())),tuple(a.lineage_refs)) for a in self.agents.values()),
        'projects':sorted((p.id,p.node_id,p.cash_account_id,tuple(sorted((k,str(v)) for k,v in p.owners.items())),p.status) for p in self.state.projects.values()),
        'commitments':sorted((c.id,c.financier_id,c.project_id,str(c.amount),str(c.committed),str(c.disbursed),str(c.lapsed)) for c in self.state.commitments.values()),
        'resources':sorted((r.id,r.node_id,r.family,str(r.in_situ),str(r.accessible),str(r.recoverable),str(r.remaining)) for r in self.resources.values()),
        'obs':sorted((o.id,o.actor_id,o.resource_id,o.signal,o.public) for o in self.observations.values()),
        'public_information':sorted((a.id,a.publisher_id,a.source_observation_id,a.resource_id,a.channel,a.signal,a.audience,a.recipient_ids) for a in self.public_information.values()),
        'colonies':sorted((c.node_id,c.population,str(c.cash),str(c.productive_capital),str(c.infrastructure),c.habitat_capacity,str(c.resource_inventory),str(c.import_inventory),str(c.production_capacity),str(c.operating_need),str(c.external_subsidy),c.stage) for c in self.colonies.values()),
        'events':[(e.id,e.year,e.actor_id,e.action.value,e.result,e.inputs,e.parent_ids) for e in self.events],
        'population':None if self.population is None else (self.population.earth,sorted(self.population.offworld.items()),sorted(self.population.in_transit.items()))}
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
