from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
import json
from typing import Dict, Tuple
from .build4 import Build4Kernel
from .kernel import InvariantError
from .model import D
from .mvp_state import AgentState, AggregateState, EntityAssetRef, RuntimeObjectClass, SystemState
from .scheduler import DeterministicScheduler

@dataclass(frozen=True)
class ResolutionRecord:
    resolution_id: str
    year: int
    aggregate_id: str
    agent_id: str
    cash_reclassified: D
    members_reclassified: int
    asset_refs: Tuple[str,...]
    resource_reclassified: Tuple[Tuple[str,D],...]
    claim_reclassified: Tuple[Tuple[str,D],...]
    history_refs: Tuple[str,...]
    transaction_count_before: int
    transaction_count_after: int
    cash_total_before: D
    cash_total_after: D

class MethodologyHardenedBuild4Kernel(Build4Kernel):
    """Build-4-derived methodology baseline. No autonomous decision-policy authority."""
    methodology_version='BUILD4_MVP_METHODOLOGY_R1'
    accounting_boundary_version='PHASE3B_MVP_ACCOUNTING_BOUNDARY_0_1'

    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.scheduler=DeterministicScheduler()
        self.systems: Dict[str,SystemState]={}
        self.aggregates: Dict[str,AggregateState]={}
        self.entity_asset_refs: Dict[str,EntityAssetRef]={}
        self.resolution_records: list[ResolutionRecord]=[]

    def add_system(self,s:SystemState):
        if s.runtime_class!=RuntimeObjectClass.SYSTEM or s.id in self.systems:
            raise InvariantError('invalid system object')
        self.systems[s.id]=s

    def add_aggregate(self,a:AggregateState):
        if a.runtime_class!=RuntimeObjectClass.AGGREGATE:
            raise InvariantError('invalid aggregate class')
        if a.id in self.aggregates or a.account_id not in self.state.accounts or a.member_count<0:
            raise InvariantError('invalid aggregate object')
        if any(v<0 for v in a.resource_holdings.values()) or any(v<0 for v in a.claim_holdings.values()):
            raise InvariantError('negative aggregate holdings')
        self.aggregates[a.id]=a

    def add_entity_asset_ref(self,e:EntityAssetRef):
        if e.runtime_class!=RuntimeObjectClass.ENTITY_ASSET or e.id in self.entity_asset_refs:
            raise InvariantError('invalid entity/asset ref')
        self.entity_asset_refs[e.id]=e

    def expose_agent_from_aggregate(self,year,aggregate_id,agent:AgentState,cash_amount=D('0'),members=1,
                                    asset_refs=(),resource_holdings=None,claim_holdings=None,history_refs=()):
        """Resolution change only: reclassifies existing represented state; it is not an economic transaction."""
        agg=self.aggregates[aggregate_id]
        cash=D(cash_amount); members=int(members)
        resources={k:D(v) for k,v in (resource_holdings or {}).items()}
        claims={k:D(v) for k,v in (claim_holdings or {}).items()}
        assets=set(asset_refs); histories=tuple(history_refs)

        if agent.runtime_class!=RuntimeObjectClass.AGENT or agent.id in self.agents:
            raise InvariantError('resolution target must be new AGENT')
        if agent.account_id not in self.state.accounts:
            raise InvariantError('resolution target account missing')
        if cash<0 or self.state.accounts[agg.account_id].balance<cash:
            raise InvariantError('aggregate cash insufficient')
        if members<0 or agg.member_count<members:
            raise InvariantError('aggregate member count insufficient')
        if not assets.issubset(agg.asset_refs):
            raise InvariantError('aggregate asset allocation unavailable')
        for k,v in resources.items():
            if v<0 or agg.resource_holdings.get(k,D('0'))<v: raise InvariantError('aggregate resource allocation unavailable')
        for k,v in claims.items():
            if v<0 or agg.claim_holdings.get(k,D('0'))<v: raise InvariantError('aggregate claim allocation unavailable')
        if not set(histories).issubset(set(agg.history_refs)):
            raise InvariantError('aggregate history lineage unavailable')

        agg_acct=self.state.accounts[agg.account_id]; agent_acct=self.state.accounts[agent.account_id]
        tx_before=len(self.state.transactions); cash_before=agg_acct.balance+agent_acct.balance

        # Atomic representational reclassification after all validation. No Transaction is emitted.
        agg_acct.balance-=cash; agent_acct.balance+=cash
        agg.member_count-=members
        agg.asset_refs-=assets; agent.asset_refs|=assets
        for k,v in resources.items():
            agg.resource_holdings[k]=agg.resource_holdings.get(k,D('0'))-v
            agent.resource_holdings[k]=agent.resource_holdings.get(k,D('0'))+v
        for k,v in claims.items():
            agg.claim_holdings[k]=agg.claim_holdings.get(k,D('0'))-v
            agent.claim_holdings[k]=agent.claim_holdings.get(k,D('0'))+v

        rid=self._id('resolution')
        agent.lineage_refs.extend([*histories,rid])
        self.add_agent(agent)

        record=ResolutionRecord(rid,year,aggregate_id,agent.id,cash,members,tuple(sorted(assets)),
            tuple(sorted(resources.items())),tuple(sorted(claims.items())),histories,
            tx_before,len(self.state.transactions),cash_before,agg_acct.balance+agent_acct.balance)
        self.resolution_records.append(record)
        self.audit('AGGREGATE_TO_AGENT',year,resolution_id=rid,aggregate=aggregate_id,agent=agent.id,
                   cash=cash,members=members,assets=','.join(sorted(assets)))
        return record

    def assert_methodology_invariants(self):
        self.assert_build4_invariants()
        for s in self.systems.values():
            if s.runtime_class!=RuntimeObjectClass.SYSTEM: raise InvariantError('system class drift')
        for a in self.aggregates.values():
            if a.runtime_class!=RuntimeObjectClass.AGGREGATE or a.member_count<0: raise InvariantError('aggregate class/state drift')
            if any(v<0 for v in a.resource_holdings.values()) or any(v<0 for v in a.claim_holdings.values()):
                raise InvariantError('aggregate holdings negative')
        for r in self.resolution_records:
            if r.transaction_count_before!=r.transaction_count_after: raise InvariantError('resolution incorrectly emitted economic transaction')
            if r.cash_total_before!=r.cash_total_after: raise InvariantError('resolution cash reconciliation')
        if 'EARTH_MARKET_v0' in self.agents: raise InvariantError('EARTH_MARKET_v0 cannot be agent')

    def methodology_fingerprint(self):
        payload={
          'methodology_version':self.methodology_version,
          'accounting_boundary_version':self.accounting_boundary_version,
          'build4':self.build4_fingerprint(),
          'scheduler':self.scheduler.fingerprint(),
          'systems':sorted((s.id,s.process_type,tuple(sorted(s.owned_state_refs))) for s in self.systems.values()),
          'aggregates':sorted((a.id,a.node_id,a.account_id,a.member_count,tuple(sorted(a.asset_refs)),
             tuple(sorted((k,str(v)) for k,v in a.resource_holdings.items())),
             tuple(sorted((k,str(v)) for k,v in a.claim_holdings.items())),tuple(a.history_refs)) for a in self.aggregates.values()),
          'entity_asset_refs':sorted((e.id,e.domain_type,e.state_ref) for e in self.entity_asset_refs.values()),
          'resolutions':[(r.resolution_id,r.year,r.aggregate_id,r.agent_id,str(r.cash_reclassified),r.members_reclassified,
             r.asset_refs,tuple((k,str(v)) for k,v in r.resource_reclassified),tuple((k,str(v)) for k,v in r.claim_reclassified),
             r.history_refs,r.transaction_count_before,r.transaction_count_after,str(r.cash_total_before),str(r.cash_total_after))
             for r in self.resolution_records]}
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
