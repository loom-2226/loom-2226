from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
import json
from typing import Dict, Tuple
from .build4 import Build4Kernel, OwnershipStake
from .kernel import InvariantError
from .model import D, TxPurpose
from .mvp_state import AgentState, AggregateState, EntityAssetRef, RuntimeObjectClass, SystemState
from .scheduler import DeterministicScheduler
from .resolution import ResolutionExposurePlan, ResolutionExposureRecord
from .accounting import SurplusDecompositionRecord

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

    SCHEDULED_MUTATION_METHODS=frozenset({
        'add_node','add_account','add_project','add_commitment','transfer','disburse','spend_capex','capitalize',
        'add_agent','add_resource','event','observe','request_finance','decide_finance','extract','sell','migrate',
        'set_resource_constraint','reserve_earth_supply','spend_reserved_capex','explore_paid','resolve_exploration',
        'extract_bounded','sell_to_market','dispose_surplus',
        'audit','register_vehicle_ownership','distribute_vehicle_to_owners','set_supply_capacity','consume_supply',
        'create_wip','add_wip_expenditure','commission_wip','depreciate','amortize_knowledge',
        'create_carry_reservation','spend_carry_reservation','lapse_carry_reservation','lapse_commitment',
        'boundary_purchase','consume_market_resource',
        'add_system','add_aggregate','add_entity_asset_ref','expose_agent_from_aggregate','expose_agent_by_plan','record_surplus_decomposition'
    })
    SCHEDULED_READONLY_METHODS=frozenset({
        'realized_fcf','productive_capital','assert_invariants','fingerprint',
        'assert_mvp_invariants','mvp_fingerprint','keyed_draw','build3_fingerprint',
        'assert_vehicle_ownership','assert_build4_invariants','build4_fingerprint','uniformity_sample',
        'assert_methodology_invariants','methodology_fingerprint'
    })
    SCHEDULED_CONTROL_METHODS=frozenset({
        'seal_for_scheduled_execution','scheduled_event_context'
    })
    methodology_version='BUILD4_MVP_METHODOLOGY_R1'
    accounting_boundary_version='PHASE3B_MVP_ACCOUNTING_BOUNDARY_0_1'

    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.scheduler=DeterministicScheduler()
        self.systems: Dict[str,SystemState]={}
        self.aggregates: Dict[str,AggregateState]={}
        self.entity_asset_refs: Dict[str,EntityAssetRef]={}
        self.resolution_records: list[ResolutionRecord]=[]
        self.resolution_exposure_records: list[ResolutionExposureRecord]=[]
        self.surplus_decompositions: list[SurplusDecompositionRecord]=[]
        self._strict_scheduled_execution=False
        self._scheduled_execution_depth=0
        self._scheduled_current_event_id=None
        self._scheduled_seal_state_fingerprint=None
        self._scheduled_seal_plan_fingerprint=None
        self._scheduled_execution_token=None

    def __getattribute__(self,name):
        attr=super().__getattribute__(name)
        if name.startswith('_') or not callable(attr):
            return attr
        try:
            guarded=name in super().__getattribute__('SCHEDULED_MUTATION_METHODS')
            strict=super().__getattribute__('_strict_scheduled_execution')
            depth=super().__getattribute__('_scheduled_execution_depth')
        except AttributeError:
            return attr
        if guarded and strict and depth<=0:
            def blocked(*args,**kwargs):
                raise InvariantError(f'direct mutation blocked in scheduled-run mode: {name}')
            return blocked
        return attr

    def seal_for_scheduled_execution(self,state_fingerprint,plan_fingerprint):
        if self._strict_scheduled_execution:
            raise InvariantError('kernel already sealed for scheduled execution')
        self._scheduled_seal_state_fingerprint=str(state_fingerprint)
        self._scheduled_seal_plan_fingerprint=str(plan_fingerprint)
        self._scheduled_execution_token=object()
        self._strict_scheduled_execution=True
        return self._scheduled_execution_token

    @contextmanager
    def scheduled_event_context(self,event_id,execution_token):
        if not self._strict_scheduled_execution:
            raise InvariantError('scheduled event context requires sealed scheduled-run mode')
        if execution_token is not self._scheduled_execution_token:
            raise InvariantError('scheduled event context requires runtime execution token')
        self._scheduled_execution_depth+=1
        prior=self._scheduled_current_event_id
        self._scheduled_current_event_id=str(event_id)
        try:
            yield
        finally:
            self._scheduled_current_event_id=prior
            self._scheduled_execution_depth-=1

    @property
    def strict_scheduled_execution(self):
        return self._strict_scheduled_execution

    @property
    def scheduled_current_event_id(self):
        return self._scheduled_current_event_id

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
            live=[s for s in self.ownership_stakes if s.vehicle_id==k and s.owner_id==agg.id]
            if live and sum((s.share for s in live),D('0'))<v:
                raise InvariantError('live ownership stake insufficient for resolution')
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
            live=[s for s in self.ownership_stakes if s.vehicle_id==k and s.owner_id==agg.id]
            if live:
                remaining=v
                for s in live:
                    take=min(s.share,remaining)
                    s.share-=take; remaining-=take
                    if remaining==0: break
                self.ownership_stakes=[s for s in self.ownership_stakes if s.share!=0]
                self.ownership_stakes.append(OwnershipStake(k,agent.id,agent.node_id,v))
                self.assert_vehicle_ownership(k)

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

    def expose_agent_by_plan(self,year,plan:ResolutionExposurePlan,agent:AgentState,asset_refs=()):
        if plan.aggregate_id not in self.aggregates:
            raise InvariantError('resolution exposure aggregate missing')
        if plan.selected_agent_id!=agent.id:
            raise InvariantError('resolution exposure selected agent mismatch')
        agg=self.aggregates[plan.aggregate_id]
        fraction=plan.validate_and_fraction(agg.member_count)

        cash=self.state.accounts[agg.account_id].balance*fraction
        resources={k:D(v)*fraction for k,v in agg.resource_holdings.items()}
        claims={k:D(v)*fraction for k,v in agg.claim_holdings.items()}
        histories=tuple(agg.history_refs)

        record=self.expose_agent_from_aggregate(
            year,plan.aggregate_id,agent,cash,plan.members_exposed,
            tuple(asset_refs),resources,claims,histories)

        exposure=ResolutionExposureRecord(
            plan.plan_id,record.resolution_id,plan.aggregate_id,agent.id,plan.members_exposed,
            plan.selection_basis.value,plan.selection_ref,plan.allocation_basis.value,
            plan.allocation_ref,fraction)
        self.resolution_exposure_records.append(exposure)
        self.audit('AGGREGATE_TO_AGENT_EXPOSURE_PLAN',year,
                   plan_id=plan.plan_id,resolution_id=record.resolution_id,
                   aggregate=plan.aggregate_id,agent=agent.id,
                   members=plan.members_exposed,selection_basis=plan.selection_basis.value,
                   selection_ref=plan.selection_ref,allocation_basis=plan.allocation_basis.value,
                   allocation_ref=plan.allocation_ref,allocation_fraction=fraction)
        return exposure

    def record_surplus_decomposition(self,year,project_id,surplus,reserve=D('0'),
                                     local_reinvestments=(),owner_returns=(),
                                     local_retentions=(),other_investments=()):
        if project_id not in self.state.projects: raise InvariantError('A6 project missing')
        surplus=D(surplus); reserve=D(reserve)
        routes=[
          ('local_reinvest',TxPurpose.LOCAL_REINVESTMENT,tuple(local_reinvestments)),
          ('return_to_earth',TxPurpose.RETURN_TO_EARTH,tuple(owner_returns)),
          ('local_retention',TxPurpose.LOCAL_RETENTION,tuple(local_retentions)),
          ('other_investment',TxPurpose.OTHER_INVESTMENT,tuple(other_investments))]
        totals={name:sum((D(amount) for _,amount in items),D('0')) for name,_,items in routes}
        rec=SurplusDecompositionRecord(year,project_id,surplus,reserve,
            totals['local_reinvest'],totals['return_to_earth'],totals['local_retention'],
            totals['other_investment'],()).validate()
        source=self.state.projects[project_id].cash_account_id
        routed=surplus-reserve
        if self.state.accounts[source].balance<routed: raise InvariantError('A6 surplus funds unavailable')
        txids=[]
        for _,purpose,items in routes:
            for destination,amount in items:
                tx=self.transfer(year,source,destination,D(amount),purpose,parent_ids=(project_id,'SURPLUS'))
                txids.append(tx.id)
        rec=SurplusDecompositionRecord(year,project_id,surplus,reserve,
            totals['local_reinvest'],totals['return_to_earth'],totals['local_retention'],
            totals['other_investment'],tuple(txids)).validate()
        self.surplus_decompositions.append(rec)
        self.audit('SURPLUS_DECOMPOSITION',year,project=project_id,surplus=surplus,reserve=reserve,
                   local_reinvest=rec.local_reinvest,return_to_earth=rec.return_to_earth,
                   local_retention=rec.local_retention,other_investment=rec.other_investment)
        return rec

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
        for r in self.surplus_decompositions: r.validate()

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
             for r in self.resolution_records],
          'resolution_exposure_records':[(r.plan_id,r.resolution_id,r.aggregate_id,r.agent_id,r.members_exposed,
             r.selection_basis,r.selection_ref,r.allocation_basis,r.allocation_ref,str(r.allocation_fraction))
             for r in self.resolution_exposure_records],
          'surplus_decompositions':[(r.year,r.project_id,str(r.surplus),str(r.reserve),str(r.local_reinvest),
             str(r.return_to_earth),str(r.local_retention),str(r.other_investment),r.transaction_ids)
             for r in self.surplus_decompositions]}
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
