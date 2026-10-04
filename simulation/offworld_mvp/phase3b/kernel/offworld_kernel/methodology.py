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
from .project_lifecycle import (
    ProjectDevelopmentPlan, DevelopmentStageRecord, DevelopmentStageOutcome,
    DevelopmentResolutionRecord, DevelopmentResolutionOutcome,
)
from .mvp_state import ActionKind

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

@dataclass(frozen=True)
class DecisionEpochRecord:
    chain_id: str
    epoch_id: str
    ordinal: int
    parent_result_fingerprint: str
    plan_fingerprint: str
    initial_fingerprint: str
    final_fingerprint: str
    execution_fingerprint: str
    result_fingerprint: str

class MethodologyHardenedBuild4Kernel(Build4Kernel):
    """Build-4-derived methodology baseline. No autonomous decision-policy authority."""

    SCHEDULED_MUTATION_METHODS=frozenset({
        'add_node','add_account','add_project','add_commitment','transfer','disburse','spend_capex','capitalize',
        'add_agent','add_resource','event','observe','publish_observation','submit_financing_request','transition_project_status','request_finance','decide_finance','extract','sell','migrate',
        'set_resource_constraint','reserve_earth_supply','spend_reserved_capex','explore_paid','resolve_exploration',
        'extract_bounded','sell_to_market','dispose_surplus',
        'audit','register_vehicle_ownership','distribute_vehicle_to_owners','set_supply_capacity','consume_supply',
        'create_wip','add_wip_expenditure','commission_wip','write_off_wip','depreciate','amortize_knowledge',
        'create_carry_reservation','spend_carry_reservation','lapse_carry_reservation','lapse_commitment',
        'boundary_purchase','consume_market_resource',
        'add_system','add_aggregate','add_entity_asset_ref','expose_agent_from_aggregate','expose_agent_by_plan','record_surplus_decomposition',
        'register_development_plan','execute_development_stage','resolve_development_plan'
    })
    SCHEDULED_READONLY_METHODS=frozenset({
        'realized_fcf','productive_capital','assert_invariants','fingerprint',
        'assert_mvp_invariants','mvp_fingerprint','keyed_draw','build3_fingerprint',
        'assert_vehicle_ownership','assert_build4_invariants','build4_fingerprint','uniformity_sample',
        'assert_methodology_invariants','methodology_fingerprint','decision_epoch_state_fingerprint'
    })
    SCHEDULED_CONTROL_METHODS=frozenset({
        'seal_for_scheduled_execution','scheduled_event_context','begin_decision_epoch','complete_decision_epoch'
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
        self.decision_epoch_records: list[DecisionEpochRecord]=[]
        self.development_plans: Dict[str,ProjectDevelopmentPlan]={}
        self.development_stage_records: list[DevelopmentStageRecord]=[]
        self.development_resolution_records: list[DevelopmentResolutionRecord]=[]
        self.decision_epoch_chain_id: str|None=None
        self.active_decision_epoch_id: str|None=None
        self._decision_epoch_open_state_fingerprint=None
        self._decision_epoch_expected_between_fingerprint=None
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
            epoch_chain=super().__getattribute__('decision_epoch_chain_id') is not None
        except AttributeError:
            return attr
        if guarded and depth<=0 and (strict or epoch_chain):
            def blocked(*args,**kwargs):
                mode='scheduled-run' if strict else 'decision-epoch chain'
                raise InvariantError(f'direct mutation blocked in {mode} mode: {name}')
            return blocked
        return attr

    def register_development_plan(self,plan:ProjectDevelopmentPlan):
        plan.validate()
        if plan.id in self.development_plans:
            raise InvariantError('duplicate development plan')
        if plan.project_id not in self.state.projects:
            raise InvariantError('development plan project missing')
        if plan.supplier_account_id not in self.state.accounts:
            raise InvariantError('development plan supplier missing')
        if plan.asset_node_id not in self.state.nodes:
            raise InvariantError('development plan asset node missing')
        if any(w.id==plan.wip_id for w in self.wip.values()):
            raise InvariantError('development plan WIP identity already exists')
        if plan.asset_id in self.state.assets:
            raise InvariantError('development plan asset identity already exists')
        self.development_plans[plan.id]=plan
        return plan

    def execute_development_stage(self,year,plan_id):
        year=int(year)
        if plan_id not in self.development_plans:
            raise InvariantError('development plan missing')
        plan=self.development_plans[plan_id]
        project=self.state.projects[plan.project_id]
        if project.status!='DEVELOPMENT':
            raise InvariantError('construction stage requires DEVELOPMENT project')
        planned=dict(plan.stage_schedule)
        if year not in planned:
            raise InvariantError('construction stage year not declared by plan')
        if any(r.plan_id==plan_id and r.year==year for r in self.development_stage_records):
            raise InvariantError('development stage already resolved')
        amount=D(planned[year])
        reason='SPENT'
        outcome=DevelopmentStageOutcome.SPENT
        tx_id=''

        if self.state.accounts[project.cash_account_id].balance<amount:
            outcome=DevelopmentStageOutcome.BLOCKED_PROJECT_CASH
            reason='PROJECT_CASH_BELOW_DECLARED_STAGE'
        else:
            supplier_node=self.state.accounts[plan.supplier_account_id].node_id
            if self.state.nodes[supplier_node].kind.value=='EARTH':
                c=self.resource_constraints.get((supplier_node,year))
                if c is None or amount>c.available:
                    outcome=DevelopmentStageOutcome.BLOCKED_SUPPLY
                    reason='EARTH_RESOURCE_ALLOCATION_CAPACITY'
                else:
                    self.reserve_earth_supply(supplier_node,year,amount)
            else:
                supply=self.supply.get((supplier_node,year))
                if supply is None or amount>supply.available:
                    outcome=DevelopmentStageOutcome.BLOCKED_SUPPLY
                    reason='OFFWORLD_SUPPLY_CAPACITY'

        if outcome==DevelopmentStageOutcome.SPENT:
            if plan.wip_id not in self.wip:
                self.create_wip(plan.wip_id,plan.project_id,plan.asset_node_id)
            origins=tuple(sorted({
                t.source_location for t in self.state.transactions
                if t.destination_account==project.cash_account_id
                and t.purpose in {TxPurpose.DISBURSE,TxPurpose.LOCAL_REINVESTMENT,TxPurpose.OTHER_INVESTMENT}
            }))
            tx=self.add_wip_expenditure(
                year,plan.wip_id,plan.supplier_account_id,amount,
                financing_origin_nodes=origins)
            tx_id=tx.id

        develop_parent=next((
            e.id for e in reversed(self.events)
            if e.action==ActionKind.DEVELOP and e.result=='DEVELOPMENT'
            and plan.project_id in e.inputs
        ),'')
        parents=tuple(x for x in (plan.id,develop_parent) if x)
        evt=self.event(
            year,'CONSTRUCTION_SYSTEM',ActionKind.CONSTRUCT,outcome.value,
            (plan.id,plan.project_id,plan.wip_id,str(amount),reason,tx_id),parents)
        rec=DevelopmentStageRecord(
            plan.id,plan.project_id,year,amount,outcome,reason,tx_id,evt.id)
        self.development_stage_records.append(rec)
        return rec

    def resolve_development_plan(self,year,plan_id):
        year=int(year)
        if plan_id not in self.development_plans:
            raise InvariantError('development plan missing')
        if any(r.plan_id==plan_id for r in self.development_resolution_records):
            raise InvariantError('development plan already resolved')
        plan=self.development_plans[plan_id]
        if year<int(plan.completion_year):
            raise InvariantError('development completion resolved too early')
        project=self.state.projects[plan.project_id]
        if project.status!='DEVELOPMENT':
            raise InvariantError('development resolution requires DEVELOPMENT project')

        stages=[r for r in self.development_stage_records if r.plan_id==plan_id]
        spent_years={r.year for r in stages if r.outcome==DevelopmentStageOutcome.SPENT}
        required_years={int(y) for y,_ in plan.stage_schedule}
        w=self.wip.get(plan.wip_id)
        accumulated=D('0') if w is None else D(w.accumulated_cost)
        success=(
            spent_years==required_years
            and w is not None
            and accumulated==D(plan.required_cost)
            and w.remaining_wip==D(plan.required_cost)
        )

        if success:
            self.commission_wip(year,plan.wip_id,plan.asset_id,D(plan.commissioned_capacity))
            project.status='OPERATING'
            w=self.wip[plan.wip_id]
            stage_parents=tuple(r.event_id for r in stages if r.event_id)
            evt=self.event(
                year,'DEVELOPMENT_RESOLUTION_SYSTEM',ActionKind.CONSTRUCT,'OPERATING',
                (plan.id,plan.project_id,plan.asset_id,str(plan.required_cost)),
                (plan.id,*stage_parents))
            rec=DevelopmentResolutionRecord(
                plan.id,plan.project_id,year,DevelopmentResolutionOutcome.OPERATING,
                D(plan.required_cost),D(w.accumulated_cost),D(w.commissioned),D(w.written_off),
                plan.asset_id,'FULL_DECLARED_DEVELOPMENT_COST_COMMISSIONED',evt.id)
        else:
            written=D('0')
            if w is not None:
                written=self.write_off_wip(year,plan.wip_id,'INCOMPLETE_DEVELOPMENT')
            project.status='FAILED'
            accumulated=D('0') if w is None else D(w.accumulated_cost)
            commissioned=D('0') if w is None else D(w.commissioned)
            written_total=D('0') if w is None else D(w.written_off)
            stage_parents=tuple(r.event_id for r in stages if r.event_id)
            evt=self.event(
                year,'DEVELOPMENT_RESOLUTION_SYSTEM',ActionKind.FAIL,'FAILED',
                (plan.id,plan.project_id,str(accumulated),str(written),str(plan.required_cost)),
                (plan.id,*stage_parents))
            rec=DevelopmentResolutionRecord(
                plan.id,plan.project_id,year,DevelopmentResolutionOutcome.FAILED,
                D(plan.required_cost),accumulated,commissioned,written_total,'',
                'INCOMPLETE_DECLARED_DEVELOPMENT',evt.id)
        self.development_resolution_records.append(rec)
        return rec

    def seal_for_scheduled_execution(self,state_fingerprint,plan_fingerprint):
        if self._strict_scheduled_execution:
            raise InvariantError('kernel already sealed for scheduled execution')
        if self.active_decision_epoch_id is not None:
            current=self.decision_epoch_state_fingerprint()
            if current!=self._decision_epoch_open_state_fingerprint:
                raise InvariantError('decision-epoch persistent state changed before seal')
        self._scheduled_seal_state_fingerprint=str(state_fingerprint)
        self._scheduled_seal_plan_fingerprint=str(plan_fingerprint)
        self._scheduled_execution_token=object()
        self._strict_scheduled_execution=True
        return self._scheduled_execution_token

    def begin_decision_epoch(self,epoch_id,chain_id=None):
        if self._strict_scheduled_execution:
            raise InvariantError('cannot begin decision epoch while kernel sealed')
        if self.active_decision_epoch_id is not None:
            raise InvariantError('decision epoch already active')
        epoch_id=str(epoch_id)
        if not epoch_id:
            raise InvariantError('decision epoch id required')
        if any(r.epoch_id==epoch_id for r in self.decision_epoch_records):
            raise InvariantError('duplicate decision epoch id')
        if self.decision_epoch_chain_id is None:
            if not chain_id:
                raise InvariantError('first decision epoch requires chain id')
            self.decision_epoch_chain_id=str(chain_id)
        elif chain_id is not None and str(chain_id)!=self.decision_epoch_chain_id:
            raise InvariantError('decision epoch chain id mismatch')
        if self._decision_epoch_expected_between_fingerprint is not None:
            if self.decision_epoch_state_fingerprint()!=self._decision_epoch_expected_between_fingerprint:
                raise InvariantError('persistent state tampered between decision epochs')
        self.scheduler=DeterministicScheduler()
        self.active_decision_epoch_id=epoch_id
        self._decision_epoch_open_state_fingerprint=self.decision_epoch_state_fingerprint()
        return self._decision_epoch_open_state_fingerprint

    def complete_decision_epoch(self,execution_token,run_result):
        if self.active_decision_epoch_id is None:
            raise InvariantError('no active decision epoch')
        if not self._strict_scheduled_execution or execution_token is not self._scheduled_execution_token:
            raise InvariantError('decision epoch completion requires active runtime token')
        if self._scheduled_execution_depth!=0:
            raise InvariantError('cannot complete decision epoch inside scheduled event')
        if run_result.plan_fingerprint!=self._scheduled_seal_plan_fingerprint:
            raise InvariantError('decision epoch plan fingerprint mismatch')
        if run_result.final_fingerprint!=self.methodology_fingerprint():
            raise InvariantError('decision epoch final fingerprint mismatch')
        parent=self.decision_epoch_records[-1].result_fingerprint if self.decision_epoch_records else ''
        record=DecisionEpochRecord(
            self.decision_epoch_chain_id,self.active_decision_epoch_id,len(self.decision_epoch_records)+1,parent,
            run_result.plan_fingerprint,run_result.initial_fingerprint,run_result.final_fingerprint,
            run_result.execution_fingerprint,run_result.result_fingerprint)
        self.decision_epoch_records.append(record)
        self._strict_scheduled_execution=False
        self._scheduled_execution_token=None
        self._scheduled_seal_state_fingerprint=None
        self._scheduled_seal_plan_fingerprint=None
        self.active_decision_epoch_id=None
        self._decision_epoch_open_state_fingerprint=None
        self._decision_epoch_expected_between_fingerprint=self.decision_epoch_state_fingerprint()
        return record

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
        for plan in self.development_plans.values():
            plan.validate()
        seen_stage=set()
        txids={t.id for t in self.state.transactions}
        for r in self.development_stage_records:
            if r.plan_id not in self.development_plans:
                raise InvariantError('development stage plan missing')
            key=(r.plan_id,r.year)
            if key in seen_stage:
                raise InvariantError('duplicate development stage record')
            seen_stage.add(key)
            planned=dict(self.development_plans[r.plan_id].stage_schedule)
            if r.year not in planned or D(r.planned_amount)!=D(planned[r.year]):
                raise InvariantError('development stage amount/year drift')
            if r.outcome==DevelopmentStageOutcome.SPENT:
                if not r.transaction_id or r.transaction_id not in txids:
                    raise InvariantError('spent development stage transaction missing')
            elif r.transaction_id:
                raise InvariantError('blocked development stage cannot carry transaction')
        seen_resolution=set()
        for r in self.development_resolution_records:
            if r.plan_id not in self.development_plans or r.plan_id in seen_resolution:
                raise InvariantError('development resolution identity drift')
            seen_resolution.add(r.plan_id)
            plan=self.development_plans[r.plan_id]
            if D(r.required_cost)!=D(plan.required_cost):
                raise InvariantError('development resolution required-cost drift')
            if r.outcome==DevelopmentResolutionOutcome.OPERATING:
                if not r.asset_id or D(r.commissioned)!=D(plan.required_cost) or D(r.written_off)!=0:
                    raise InvariantError('operating development resolution invalid')
            elif r.outcome==DevelopmentResolutionOutcome.FAILED:
                if r.asset_id or D(r.commissioned)!=0 or D(r.accumulated_cost)!=D(r.written_off):
                    raise InvariantError('failed development resolution invalid')

    def _methodology_payload(self,include_scheduler=True):
        payload={
          'methodology_version':self.methodology_version,
          'accounting_boundary_version':self.accounting_boundary_version,
          'build4':self.build4_fingerprint(),
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
             for r in self.surplus_decompositions],
          'decision_epoch_chain_id':self.decision_epoch_chain_id,
          'active_decision_epoch_id':self.active_decision_epoch_id,
          'decision_epoch_records':[(r.chain_id,r.epoch_id,r.ordinal,r.parent_result_fingerprint,
             r.plan_fingerprint,r.initial_fingerprint,r.final_fingerprint,r.execution_fingerprint,r.result_fingerprint)
             for r in self.decision_epoch_records],
          'development_plans':sorted((p.id,p.project_id,p.wip_id,p.asset_id,p.supplier_account_id,p.asset_node_id,
             str(p.required_cost),tuple((int(y),str(a)) for y,a in p.stage_schedule),p.completion_year,
             str(p.commissioned_capacity),p.source_ref,p.plan_version) for p in self.development_plans.values()),
          'development_stage_records':[(r.plan_id,r.project_id,r.year,str(r.planned_amount),r.outcome.value,
             r.reason,r.transaction_id,r.event_id,r.record_version) for r in self.development_stage_records],
          'development_resolution_records':[(r.plan_id,r.project_id,r.year,r.outcome.value,str(r.required_cost),
             str(r.accumulated_cost),str(r.commissioned),str(r.written_off),r.asset_id,r.reason,r.event_id,r.record_version)
             for r in self.development_resolution_records]}
        if include_scheduler:
            payload['scheduler']=self.scheduler.fingerprint()
        return payload

    def decision_epoch_state_fingerprint(self):
        payload=self._methodology_payload(include_scheduler=False)
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

    def methodology_fingerprint(self):
        payload=self._methodology_payload(include_scheduler=True)
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
