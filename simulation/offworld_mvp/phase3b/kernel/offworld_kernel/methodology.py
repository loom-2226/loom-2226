from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
import json
from typing import Dict, Tuple
from .build4 import Build4Kernel, OwnershipStake
from .kernel import InvariantError
from .model import D, TxPurpose, AssetKind, NodeKind, AccountKind
from .mvp_state import AgentState, AggregateState, EntityAssetRef, RuntimeObjectClass, SystemState, ColonyState, OperatingCycleDecisionOutcome, SaleDecisionOutcome, SurplusDistributionDecisionOutcome, SettlementSupportDecisionOutcome
from .scheduler import DeterministicScheduler
from .resolution import ResolutionExposurePlan, ResolutionExposureRecord
from .accounting import SurplusDecompositionRecord
from .project_lifecycle import (
    ProjectDevelopmentPlan, DevelopmentStageRecord, DevelopmentStageOutcome,
    DevelopmentResolutionRecord, DevelopmentResolutionOutcome,
)
from .surface_prospecting import (
    SurfaceProspectingModel, SurfaceProspectingWorldRecord,
    ObservationBeliefUpdateRecord,
)
from .operating import OperatingCostRecord, ExtractionResolutionRecord
from .enterprise import (
    EnterpriseReviewDecisionOutcome, EnterpriseReviewRequest, EnterpriseReviewDecision,
    EnterpriseReviewRecord,
)
from .market import CommodityMarketEnvelope, MarketClearingRecord
from .distribution import FinancingReturnClaim, OwnerDistributionAllocation, SurplusDistributionRecord
from .settlement import (
    SettlementInfrastructurePlan, SettlementInfrastructureRecord,
    SettlementStageRecord, SettlementSupportExecutionRecord,
    derive_settlement_stage,
)
from .mvp_state import ActionKind
from .transport import (
    TechnologyCapabilityState, TransportRelationship, TransportQualificationRecord,
    TransportSettlementDecisionOutcome, TransportSettlementRequest, TransportSettlementDecision,
    PassengerTransportDepartureRecord, PassengerTransportArrivalRecord,
)

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
        'set_resource_constraint','reserve_earth_supply','spend_reserved_capex','explore_paid','surface_prospect_paid','update_agent_belief_from_observation','resolve_exploration',
        'extract_bounded','sell_to_market','dispose_surplus',
        'audit','register_vehicle_ownership','distribute_vehicle_to_owners','set_supply_capacity','consume_supply',
        'create_wip','add_wip_expenditure','commission_wip','write_off_wip','depreciate','amortize_knowledge',
        'create_carry_reservation','spend_carry_reservation','lapse_carry_reservation','lapse_commitment',
        'boundary_purchase','consume_market_resource',
        'add_system','add_aggregate','add_entity_asset_ref','expose_agent_from_aggregate','expose_agent_by_plan','record_surplus_decomposition',
        'register_development_plan','execute_development_stage','resolve_development_plan',
        'spend_operating_cycle','resolve_operating_extraction','execute_enterprise_review','register_market_envelope','clear_market_sale',
        'register_financing_return_claim','execute_surplus_distribution',
        'register_settlement_infrastructure_plan','execute_settlement_infrastructure',
        'update_settlement_stage','execute_public_settlement_support',
        'register_technology_capability_state','register_transport_relationship',
        'execute_transport_settlement_departure','execute_passenger_transport_arrival'
    })
    SCHEDULED_READONLY_METHODS=frozenset({
        'realized_fcf','productive_capital','assert_invariants','fingerprint',
        'assert_mvp_invariants','mvp_fingerprint','keyed_draw','build3_fingerprint',
        'assert_vehicle_ownership','assert_build4_invariants','build4_fingerprint','uniformity_sample',
        'assert_methodology_invariants','methodology_fingerprint','decision_epoch_state_fingerprint','market_remaining_demand','financing_return_remaining',
        'settlement_habitat_headroom','settlement_stage_for','transport_qualification','earth_shadow_at'
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
        self.surface_prospecting_records: list[SurfaceProspectingWorldRecord]=[]
        self.observation_belief_update_records: list[ObservationBeliefUpdateRecord]=[]
        self.operating_cost_records: list[OperatingCostRecord]=[]
        self.extraction_resolution_records: list[ExtractionResolutionRecord]=[]
        self.enterprise_review_records: list[EnterpriseReviewRecord]=[]
        self.market_envelopes: Dict[str,CommodityMarketEnvelope]={}
        self.market_clearing_records: list[MarketClearingRecord]=[]
        self.financing_return_claims: Dict[str,FinancingReturnClaim]={}
        self.surplus_distribution_records: list[SurplusDistributionRecord]=[]
        self.settlement_infrastructure_plans: Dict[str,SettlementInfrastructurePlan]={}
        self.settlement_infrastructure_records: list[SettlementInfrastructureRecord]=[]
        self.settlement_stage_records: list[SettlementStageRecord]=[]
        self.settlement_support_records: list[SettlementSupportExecutionRecord]=[]
        self.technology_capability_states: Dict[str,TechnologyCapabilityState]={}
        self.transport_relationships: Dict[str,TransportRelationship]={}
        self.passenger_transport_departures: list[PassengerTransportDepartureRecord]=[]
        self.passenger_transport_arrivals: list[PassengerTransportArrivalRecord]=[]
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

    def surface_prospect_paid(self,year,actor_id,resource_id,project_id,supplier_account,
                             cost,prerequisite_observation_id,model:SurfaceProspectingModel,
                             parent_ids=()):
        model.validate()
        year=int(year); cost=D(cost)
        if actor_id not in self.agents:
            raise InvariantError('surface prospector agent missing')
        actor=self.agents[actor_id]
        if actor.kind.value!='PUBLIC':
            raise InvariantError('surface prospecting fixture requires public Agent')
        if 'EXPLORE' not in actor.capabilities or 'SURFACE_PROSPECT' not in actor.capabilities:
            raise InvariantError('agent lacks surface prospecting capability')
        if prerequisite_observation_id not in self.observations:
            raise InvariantError('surface prerequisite observation missing')
        if prerequisite_observation_id not in actor.information:
            raise InvariantError('surface prerequisite observation not possessed')
        prior_obs=self.observations[prerequisite_observation_id]
        if prior_obs.channel!='REMOTE':
            raise InvariantError('surface prerequisite must be REMOTE observation')
        if prior_obs.resource_id!=resource_id:
            raise InvariantError('surface prerequisite resource mismatch')
        if cost<=0:
            raise InvariantError('surface prospecting cost must be positive')

        parents=tuple(dict.fromkeys((prerequisite_observation_id,*tuple(parent_ids))))
        obs,asset_id,draw=self.explore_paid(
            year,actor_id,resource_id,project_id,supplier_account,cost,
            channel='SURFACE',public=False,
            false_positive=D(model.world_false_positive),
            false_negative=D(model.world_false_negative),
            update_belief=False,parent_ids=parents)
        tx_id=self.state.transactions[-1].id
        rec=SurfaceProspectingWorldRecord(
            year,actor_id,resource_id,prerequisite_observation_id,obs.id,
            model.model_id,D(model.world_false_positive),D(model.world_false_negative),
            D(draw),obs.signal,tx_id,asset_id)
        self.surface_prospecting_records.append(rec)
        return obs,asset_id,draw,rec

    def update_agent_belief_from_observation(self,year,agent_id,observation_id,belief_key,
                                             detection_rate,false_positive_rate,
                                             model_id,source_ref):
        year=int(year); det=D(detection_rate); fp=D(false_positive_rate)
        if agent_id not in self.agents:
            raise InvariantError('belief update agent missing')
        if observation_id not in self.observations:
            raise InvariantError('belief update observation missing')
        actor=self.agents[agent_id]
        if observation_id not in actor.information:
            raise InvariantError('belief update observation not admitted')
        if not (D('0')<=det<=D('1') and D('0')<=fp<=D('1')) or det<=fp:
            raise InvariantError('invalid agent-side observation likelihoods')
        obs=self.observations[observation_id]
        prior=D(actor.beliefs.get(belief_key,actor.priors.get(belief_key,D('0.5'))))
        if not D('0')<=prior<=D('1'):
            raise InvariantError('belief prior outside [0,1]')
        if obs.signal=='POSITIVE':
            numerator=det*prior
            denominator=numerator+fp*(D('1')-prior)
        elif obs.signal=='NEGATIVE':
            numerator=(D('1')-det)*prior
            denominator=numerator+(D('1')-fp)*(D('1')-prior)
        else:
            raise InvariantError('unsupported observation signal for belief update')
        if denominator==0:
            raise InvariantError('belief update denominator zero')
        posterior=numerator/denominator
        actor.beliefs[belief_key]=posterior
        evt=self.event(
            year,agent_id,ActionKind.EXPLORE,'BELIEF_UPDATED',
            (observation_id,belief_key,str(prior),str(posterior),str(model_id)),
            (observation_id,))
        rec=ObservationBeliefUpdateRecord(
            year,agent_id,observation_id,belief_key,prior,posterior,det,fp,
            str(model_id),str(source_ref),evt.id)
        self.observation_belief_update_records.append(rec)
        return rec

    def spend_operating_cycle(self,year,actor_id,request,decision,supplier_account,unit_opex):
        year=int(year); unit_opex=D(unit_opex)
        request.validate_protocol(); decision.validate_protocol(request)
        if decision.outcome!=OperatingCycleDecisionOutcome.OPERATE:
            raise InvariantError('operating cost spend requires OPERATE decision')
        if actor_id!=decision.actor_id or actor_id not in self.agents:
            raise InvariantError('operating actor/decision mismatch')
        actor=self.agents[actor_id]
        if actor.kind.value!='PRIVATE_SPONSOR':
            raise InvariantError('operating actor not private sponsor')
        if 'OPERATE' not in actor.capabilities or 'EXTRACT' not in actor.capabilities:
            raise InvariantError('operating actor lacks capability')
        if request.project_id not in self.state.projects:
            raise InvariantError('operating project missing')
        project=self.state.projects[request.project_id]
        if project.status!='OPERATING':
            raise InvariantError('operating cycle requires OPERATING project')
        if request.asset_id not in self.state.assets:
            raise InvariantError('operating asset missing')
        asset=self.state.assets[request.asset_id]
        if asset.kind!=AssetKind.PRODUCTIVE or asset.project_id!=project.id or asset.node_id!=project.node_id:
            raise InvariantError('operating asset/project mismatch')
        planned=D(decision.planned_quantity)
        if planned<=0 or planned>D(asset.capacity):
            raise InvariantError('planned operating quantity exceeds productive capacity')
        if unit_opex<0:
            raise InvariantError('negative unit operating cost')
        total=planned*unit_opex
        if total!=D(decision.authorized_opex):
            raise InvariantError('authorized operating cost does not reconcile quantity*unit cost')
        if self.state.accounts[project.cash_account_id].balance<total:
            raise InvariantError('project cash below authorized operating cost')
        if supplier_account not in self.state.accounts:
            raise InvariantError('operating supplier missing')
        supplier_node=self.state.accounts[supplier_account].node_id
        if self.state.nodes[supplier_node].kind==NodeKind.EARTH and total>0:
            constraint=self.resource_constraints.get((supplier_node,year))
            if constraint is None or total>constraint.available:
                raise InvariantError('operating supplier capacity unavailable')
            self.reserve_earth_supply(supplier_node,year,total)
            constraint.reserved-=total
            constraint.spent+=total
        elif total>0:
            self.consume_supply(supplier_node,year,total)

        tx=self.transfer(
            year,project.cash_account_id,supplier_account,total,TxPurpose.OPEX,
            supplier_location=supplier_node,asset_location=asset.node_id,
            parent_ids=(decision.id,request.id,asset.id))
        evt=self.event(
            year,actor_id,ActionKind.OPERATE,'OPEX_SPENT',
            (request.project_id,request.asset_id,str(planned),str(unit_opex),str(total),tx.id),
            (decision.id,))
        rec=OperatingCostRecord(
            year,actor_id,decision.id,request.project_id,request.asset_id,
            supplier_account,planned,unit_opex,total,tx.id,evt.id)
        self.operating_cost_records.append(rec)
        return rec

    def resolve_operating_extraction(self,year,actor_id,request,decision,cost_record):
        year=int(year)
        request.validate_protocol(); decision.validate_protocol(request)
        if decision.outcome!=OperatingCycleDecisionOutcome.OPERATE:
            raise InvariantError('extraction resolution requires OPERATE decision')
        if cost_record.decision_id!=decision.id or cost_record.actor_id!=actor_id:
            raise InvariantError('operating cost/extraction decision lineage mismatch')
        if any(r.decision_id==decision.id for r in self.extraction_resolution_records):
            raise InvariantError('operating extraction already resolved')
        project=self.state.projects[request.project_id]
        if project.status!='OPERATING':
            raise InvariantError('extraction requires OPERATING project')
        asset=self.state.assets.get(request.asset_id)
        if asset is None or asset.kind!=AssetKind.PRODUCTIVE or asset.project_id!=project.id:
            raise InvariantError('extraction productive asset invalid')
        if request.resource_id not in self.resources:
            raise InvariantError('extraction resource missing')
        resource=self.resources[request.resource_id]
        if resource.node_id!=project.node_id:
            raise InvariantError('extraction resource/project location mismatch')
        planned=D(decision.planned_quantity)
        if planned>D(asset.capacity):
            raise InvariantError('extraction plan exceeds productive capacity')
        before_resource=D(resource.remaining)
        colony=self.colonies.setdefault(resource.node_id,ColonyState(resource.node_id))
        before_inventory=D(colony.resource_inventory)
        actual=min(planned,before_resource)
        if actual<0:
            raise InvariantError('negative realized extraction')
        resource.remaining-=actual
        colony.resource_inventory+=actual
        result='FULL_OUTPUT' if actual==planned else ('ZERO_OUTPUT' if actual==0 else 'PARTIAL_OUTPUT')
        evt=self.event(
            year,actor_id,ActionKind.EXTRACT,result,
            (request.resource_id,str(actual),str(planned),request.project_id,request.asset_id),
            (decision.id,cost_record.event_id))
        rec=ExtractionResolutionRecord(
            year,actor_id,decision.id,request.project_id,request.asset_id,request.resource_id,
            planned,actual,before_resource,D(resource.remaining),before_inventory,
            D(colony.resource_inventory),evt.id)
        self.extraction_resolution_records.append(rec)
        return rec

    def execute_enterprise_review(self,year,actor_id,request:EnterpriseReviewRequest,
                                  decision:EnterpriseReviewDecision):
        year=int(year); request.validate_protocol(); decision.validate_protocol(request)
        if decision.outcome not in {EnterpriseReviewDecisionOutcome.CONTINUE,EnterpriseReviewDecisionOutcome.CLOSE}:
            raise InvariantError('enterprise-review execution requires CONTINUE/CLOSE decision')
        if year!=request.year:
            raise InvariantError('enterprise-review year mismatch')
        if any(r.decision_id==decision.id or r.extraction_event_id==request.extraction_event_id
               for r in self.enterprise_review_records):
            raise InvariantError('enterprise-review already executed')
        if actor_id!=decision.actor_id or actor_id not in self.agents:
            raise InvariantError('enterprise-review actor/decision mismatch')
        actor=self.agents[actor_id]
        if actor.kind.value!='PRIVATE_SPONSOR':
            raise InvariantError('enterprise-review actor must be private sponsor')
        project=self.state.projects.get(request.project_id)
        if project is None or project.status!='OPERATING':
            raise InvariantError('enterprise-review requires OPERATING project')
        extraction=next((r for r in self.extraction_resolution_records
                         if r.extraction_event_id==request.extraction_event_id),None)
        if extraction is None or extraction.project_id!=request.project_id:
            raise InvariantError('enterprise-review extraction lineage missing')
        if extraction.year>year:
            raise InvariantError('enterprise-review precedes extraction')
        planned=D(extraction.planned_quantity); actual=D(extraction.actual_extracted)
        status_before=project.status
        if decision.outcome==EnterpriseReviewDecisionOutcome.CONTINUE:
            if actual<=0 or 'OPERATE' not in actor.capabilities:
                raise InvariantError('enterprise-review CONTINUE not supported by realized output/capability')
            action=ActionKind.OPERATE; result='ENTERPRISE_CONTINUE'
        else:
            if actual!=0 or 'CLOSE_PROJECT' not in actor.capabilities:
                raise InvariantError('enterprise-review CLOSE not supported by realized output/capability')
            project.status='CLOSED'
            action=ActionKind.CLOSE; result='CLOSED'
        evt=self.event(
            year,actor_id,action,result,
            (request.project_id,request.extraction_event_id,str(planned),str(actual)),
            (decision.id,request.extraction_event_id))
        rec=EnterpriseReviewRecord(
            year,actor_id,decision.id,request.id,request.project_id,request.extraction_event_id,
            planned,actual,decision.outcome,status_before,project.status,evt.id)
        try:
            rec.validate()
        except ValueError as e:
            raise InvariantError(str(e)) from e
        self.enterprise_review_records.append(rec)
        return rec

    def register_settlement_infrastructure_plan(self,plan:SettlementInfrastructurePlan):
        plan.validate()
        if plan.id in self.settlement_infrastructure_plans:
            raise InvariantError('duplicate settlement infrastructure plan')
        if plan.node_id not in self.state.nodes or self.state.nodes[plan.node_id].kind!=NodeKind.OFFWORLD:
            raise InvariantError('settlement infrastructure plan requires offworld node')
        for aid in (plan.source_account_id,plan.supplier_account_id):
            if aid not in self.state.accounts:
                raise InvariantError('settlement infrastructure plan account missing')
            if self.state.accounts[aid].node_id!=plan.node_id:
                raise InvariantError('settlement infrastructure plan account/node mismatch')
        self.settlement_infrastructure_plans[plan.id]=plan
        return plan

    def settlement_habitat_headroom(self,node_id):
        c=self.colonies.setdefault(node_id,ColonyState(node_id))
        return max(0,int(c.habitat_capacity)-int(c.population))

    def settlement_stage_for(self,node_id):
        c=self.colonies.setdefault(node_id,ColonyState(node_id))
        return derive_settlement_stage(
            c.production_capacity,c.population,c.infrastructure,
            c.habitat_capacity,c.external_subsidy)

    def execute_settlement_infrastructure(self,year,plan_id,actor_id='SPN',parent_ids=()):
        year=int(year)
        if plan_id not in self.settlement_infrastructure_plans:
            raise InvariantError('settlement infrastructure plan missing')
        plan=self.settlement_infrastructure_plans[plan_id]
        plan.validate()
        if year!=plan.year:
            raise InvariantError('settlement infrastructure plan year mismatch')
        if any(r.plan_id==plan.id and r.outcome=='INSTALLED'
               for r in self.settlement_infrastructure_records):
            raise InvariantError('settlement infrastructure plan already installed')
        source=self.state.accounts.get(plan.source_account_id)
        supplier=self.state.accounts.get(plan.supplier_account_id)
        if source is None or supplier is None:
            raise InvariantError('settlement infrastructure account missing')
        if source.node_id!=plan.node_id or supplier.node_id!=plan.node_id:
            raise InvariantError('settlement infrastructure account/node mismatch')
        colony=self.colonies.setdefault(plan.node_id,ColonyState(plan.node_id))
        before_infra=D(colony.infrastructure)
        before_capacity=int(colony.habitat_capacity)
        cost=D(plan.infrastructure_cost)
        if source.balance<cost:
            evt=self.event(
                year,actor_id,ActionKind.CONSTRUCT,'BLOCKED_INSUFFICIENT_FUNDS',
                (plan.id,str(cost),str(source.balance)),tuple(parent_ids))
            rec=SettlementInfrastructureRecord(
                year,plan.id,plan.node_id,'BLOCKED_INSUFFICIENT_FUNDS',
                D('0'),0,before_infra,before_infra,before_capacity,before_capacity,
                '',evt.id)
            rec.validate()
            self.settlement_infrastructure_records.append(rec)
            return rec

        tx=self.transfer(
            year,plan.source_account_id,plan.supplier_account_id,cost,TxPurpose.CAPEX,
            supplier_location=supplier.node_id,asset_location=plan.node_id,
            parent_ids=(plan.id,*tuple(parent_ids)))
        colony.infrastructure+=cost
        colony.habitat_capacity+=int(plan.habitat_capacity)
        evt=self.event(
            year,actor_id,ActionKind.CONSTRUCT,'SETTLEMENT_INFRASTRUCTURE_INSTALLED',
            (plan.id,str(cost),str(plan.habitat_capacity),tx.id),tuple(parent_ids))
        rec=SettlementInfrastructureRecord(
            year,plan.id,plan.node_id,'INSTALLED',cost,int(plan.habitat_capacity),
            before_infra,D(colony.infrastructure),before_capacity,int(colony.habitat_capacity),
            tx.id,evt.id)
        rec.validate()
        self.settlement_infrastructure_records.append(rec)
        return rec

    def update_settlement_stage(self,year,node_id,actor_id='SETTLEMENT_STAGE_SYSTEM',parent_ids=()):
        year=int(year)
        if node_id not in self.state.nodes or self.state.nodes[node_id].kind!=NodeKind.OFFWORLD:
            raise InvariantError('settlement stage requires offworld node')
        colony=self.colonies.setdefault(node_id,ColonyState(node_id))
        productive=[
            a for a in self.state.assets.values()
            if a.node_id==node_id and a.kind==AssetKind.PRODUCTIVE
        ]
        colony.productive_capital=sum((D(a.book_value) for a in productive),D('0'))
        colony.production_capacity=sum((D(a.capacity) for a in productive),D('0'))
        prior=colony.stage
        stage=derive_settlement_stage(
            colony.production_capacity,colony.population,colony.infrastructure,
            colony.habitat_capacity,colony.external_subsidy)
        colony.stage=stage
        evt=self.event(
            year,actor_id,ActionKind.SETTLE,stage,
            (node_id,str(colony.population),str(colony.infrastructure),
             str(colony.habitat_capacity),str(colony.productive_capital),
             str(colony.production_capacity),str(colony.external_subsidy)),
            tuple(parent_ids))
        rec=SettlementStageRecord(
            year,node_id,prior,stage,D(colony.productive_capital),
            D(colony.production_capacity),int(colony.population),
            D(colony.infrastructure),int(colony.habitat_capacity),
            D(colony.external_subsidy),evt.id)
        rec.validate()
        self.settlement_stage_records.append(rec)
        return rec

    def execute_public_settlement_support(self,year,actor_id,request,decision,parent_ids=()):
        year=int(year)
        request.validate_protocol(); decision.validate_protocol(request)
        if decision.outcome!=SettlementSupportDecisionOutcome.AUTHORIZE:
            raise InvariantError('settlement support execution requires AUTHORIZE decision')
        if any(r.decision_id==decision.id for r in self.settlement_support_records):
            raise InvariantError('settlement support decision already executed')
        if actor_id!=decision.actor_id or actor_id not in self.agents:
            raise InvariantError('settlement support actor/decision mismatch')
        actor=self.agents[actor_id]
        if actor.kind.value!='PUBLIC':
            raise InvariantError('settlement support actor must be public')
        if 'MIGRATE' not in actor.capabilities or 'SETTLEMENT_SUPPORT' not in actor.capabilities:
            raise InvariantError('public Agent lacks settlement support capability')
        if 'PUBLIC_SETTLEMENT' not in actor.objectives:
            raise InvariantError('public Agent lacks settlement support objective')
        if request.year!=year:
            raise InvariantError('settlement support year mismatch')
        if request.node_id not in self.colonies:
            raise InvariantError('settlement colony missing')
        colony=self.colonies[request.node_id]
        if colony.stage!='EXTRACTION_ENCLAVE':
            raise InvariantError('settlement support requires EXTRACTION_ENCLAVE')
        if request.support_account_id not in self.state.accounts:
            raise InvariantError('settlement support account missing')
        support_account=self.state.accounts[request.support_account_id]
        if support_account.node_id!=request.node_id:
            raise InvariantError('settlement support account/node mismatch')
        if self.population is None:
            raise InvariantError('settlement support population ledger missing')
        residents=int(decision.authorized_residents)
        if residents<=0 or residents>request.requested_residents:
            raise InvariantError('invalid authorized settlement population')
        if residents>self.settlement_habitat_headroom(request.node_id):
            raise InvariantError('settlement migration exceeds habitat headroom')
        if residents>self.population.earth:
            raise InvariantError('settlement migration exceeds Earth population')
        support=D(decision.support_amount)
        if support!=D(request.support_cost):
            raise InvariantError('settlement support amount/request mismatch')
        if self.state.accounts[actor.account_id].balance<support:
            raise InvariantError('public settlement support funds unavailable')

        earth_before=int(self.population.earth)
        off_before=int(self.population.offworld.get(request.node_id,0))
        total_before=int(self.population.total())
        subsidy_before=D(colony.external_subsidy)

        txid=''
        if support>0:
            tx=self.transfer(
                year,actor.account_id,request.support_account_id,support,
                TxPurpose.PUBLIC_SUBSIDY,
                parent_ids=(decision.id,request.id,*tuple(parent_ids)))
            txid=tx.id
            colony.external_subsidy+=support
            colony.cash+=support

        migration_event=self.migrate(
            year,actor_id,request.node_id,residents,
            parent_ids=(decision.id,request.id,*((txid,) if txid else ()),*tuple(parent_ids)))
        stage_record=self.update_settlement_stage(
            year,request.node_id,parent_ids=(decision.id,migration_event.id,*tuple(parent_ids)))
        if stage_record.new_stage!='DEPENDENT_SETTLEMENT':
            raise InvariantError('authorized settlement support did not produce dependent settlement')

        rec=SettlementSupportExecutionRecord(
            year,actor_id,decision.id,request.node_id,residents,support,
            earth_before,int(self.population.earth),off_before,
            int(self.population.offworld.get(request.node_id,0)),
            total_before,int(self.population.total()),subsidy_before,
            D(colony.external_subsidy),txid,migration_event.id,stage_record.event_id)
        rec.validate()
        self.settlement_support_records.append(rec)
        return rec

    def register_technology_capability_state(self,state:TechnologyCapabilityState):
        state.validate()
        if state.id in self.technology_capability_states:
            raise InvariantError('duplicate technology capability state')
        self.technology_capability_states[state.id]=state
        return state

    def register_transport_relationship(self,relationship:TransportRelationship):
        relationship.validate()
        if relationship.id in self.transport_relationships:
            raise InvariantError('duplicate transport relationship')
        origin=self.state.nodes.get(relationship.origin_node_id)
        destination=self.state.nodes.get(relationship.destination_node_id)
        if origin is None or destination is None:
            raise InvariantError('transport relationship node missing')
        if origin.kind!=NodeKind.EARTH or destination.kind!=NodeKind.OFFWORLD:
            raise InvariantError('Test 012A passenger transport requires EARTH -> OFFWORLD direction')
        self.transport_relationships[relationship.id]=relationship
        return relationship

    def transport_qualification(self,technology_state_id,relationship_id,effective_time):
        t=D(effective_time)
        state=self.technology_capability_states.get(str(technology_state_id))
        relationship=self.transport_relationships.get(str(relationship_id))
        if relationship is None:
            return TransportQualificationRecord(
                str(technology_state_id),str(relationship_id),t,False,
                'RELATIONSHIP_MISSING','')
        if state is None:
            return TransportQualificationRecord(
                str(technology_state_id),str(relationship_id),t,False,
                'TECHNOLOGY_STATE_MISSING',relationship.required_capability_id)
        state.validate(); relationship.validate()
        if not relationship.applies(t):
            return TransportQualificationRecord(
                state.id,relationship.id,t,False,'RELATIONSHIP_OUTSIDE_EFFECTIVE_PERIOD',
                relationship.required_capability_id)
        if not state.applies(t):
            return TransportQualificationRecord(
                state.id,relationship.id,t,False,'TECHNOLOGY_STATE_OUTSIDE_EFFECTIVE_PERIOD',
                relationship.required_capability_id)
        if not state.qualifies(relationship.required_capability_id,t):
            return TransportQualificationRecord(
                state.id,relationship.id,t,False,'REQUIRED_CAPABILITY_NOT_QUALIFIED',
                relationship.required_capability_id)
        return TransportQualificationRecord(
            state.id,relationship.id,t,True,'QUALIFIED',
            relationship.required_capability_id)

    def execute_transport_settlement_departure(
            self,actor_id,request:TransportSettlementRequest,
            decision:TransportSettlementDecision,parent_ids=()):
        request.validate_protocol(); decision.validate_protocol(request)
        if decision.outcome!=TransportSettlementDecisionOutcome.AUTHORIZE:
            raise InvariantError('passenger transport departure requires AUTHORIZE decision')
        if any(r.decision_id==decision.id for r in self.passenger_transport_departures):
            raise InvariantError('transport settlement decision already departed')
        if actor_id!=decision.actor_id or actor_id not in self.agents:
            raise InvariantError('transport settlement actor/decision mismatch')
        actor=self.agents[actor_id]
        if actor.kind.value!='PUBLIC':
            raise InvariantError('transport settlement actor must be public')
        if 'MIGRATE' not in actor.capabilities or 'SETTLEMENT_SUPPORT' not in actor.capabilities:
            raise InvariantError('public Agent lacks settlement transport capability')
        if 'PUBLIC_SETTLEMENT' not in actor.objectives:
            raise InvariantError('public Agent lacks settlement support objective')

        relationship=self.transport_relationships.get(request.transport_relationship_id)
        state=self.technology_capability_states.get(request.technology_state_id)
        if relationship is None or state is None:
            raise InvariantError('transport/technology state missing at execution')
        q=self.transport_qualification(state.id,relationship.id,request.departure_time)
        if not q.available:
            raise InvariantError('transport relationship not technology-qualified at execution')
        if relationship.origin_node_id!=request.origin_node_id or relationship.destination_node_id!=request.destination_node_id:
            raise InvariantError('transport request direction/relationship mismatch')
        if relationship.loss_risk!=D('0'):
            raise InvariantError('Test 012A execution requires zero loss risk')

        origin=self.state.nodes.get(request.origin_node_id)
        destination=self.state.nodes.get(request.destination_node_id)
        if origin is None or destination is None or origin.kind!=NodeKind.EARTH or destination.kind!=NodeKind.OFFWORLD:
            raise InvariantError('transport request node direction invalid')
        colony=self.colonies.get(request.destination_node_id)
        if colony is None or colony.stage!='EXTRACTION_ENCLAVE':
            raise InvariantError('transport settlement departure requires EXTRACTION_ENCLAVE')

        residents=int(decision.authorized_residents)
        if residents<=0 or residents>request.requested_residents:
            raise InvariantError('invalid authorized passenger count')
        if residents>relationship.capacity:
            raise InvariantError('passenger transport exceeds relationship capacity')
        if residents>self.settlement_habitat_headroom(request.destination_node_id):
            raise InvariantError('passenger transport exceeds habitat headroom')
        if self.population is None or residents>self.population.earth:
            raise InvariantError('passenger transport exceeds Earth population')

        expected_support=D(request.support_cost)
        expected_transport=D(relationship.cost_per_passenger)*D(residents)
        expected_arrival=D(request.departure_time)+D(relationship.travel_time)
        if D(decision.support_amount)!=expected_support:
            raise InvariantError('transport settlement support amount drift')
        if D(decision.transport_amount)!=expected_transport:
            raise InvariantError('transport charge/relationship mismatch')
        if D(decision.departure_time)!=D(request.departure_time) or D(decision.arrival_time)!=expected_arrival:
            raise InvariantError('transport timing/relationship mismatch')

        if request.support_account_id not in self.state.accounts or request.transport_account_id not in self.state.accounts:
            raise InvariantError('transport settlement destination account missing')
        if self.state.accounts[request.support_account_id].node_id!=request.destination_node_id:
            raise InvariantError('settlement support account/node mismatch')
        if self.state.accounts[request.transport_account_id].node_id!=request.origin_node_id:
            raise InvariantError('transport provider account/origin mismatch')
        total_cost=expected_support+expected_transport
        if self.state.accounts[actor.account_id].balance<total_cost:
            raise InvariantError('public funds unavailable for support plus transport')

        departure_id='TRDEP-'+sha256(
            ('|'.join((decision.id,relationship.id,str(request.departure_time)))).encode()
        ).hexdigest()[:20]
        if departure_id in self.population.in_transit:
            raise InvariantError('duplicate passenger departure identity')

        earth_before=int(self.population.earth)
        transit_before=int(self.population.in_transit.get(departure_id,0))
        total_before=int(self.population.total())
        subsidy_before=D(colony.external_subsidy)

        support_txid=''
        if expected_support>0:
            tx=self.transfer(
                int(D(request.departure_time)),actor.account_id,request.support_account_id,
                expected_support,TxPurpose.PUBLIC_SUBSIDY,
                parent_ids=(decision.id,request.id,relationship.id,state.id,*tuple(parent_ids)))
            support_txid=tx.id
            colony.external_subsidy+=expected_support
            colony.cash+=expected_support

        transport_txid=''
        if expected_transport>0:
            tx=self.transfer(
                int(D(request.departure_time)),actor.account_id,request.transport_account_id,
                expected_transport,TxPurpose.TRANSPORT_PAYMENT,
                parent_ids=(decision.id,request.id,relationship.id,state.id,*tuple(parent_ids)))
            transport_txid=tx.id

        self.population.earth-=residents
        self._record_earth_migration(int(D(request.departure_time)),residents)
        self.population.in_transit[departure_id]=residents
        if self.population.total()!=total_before:
            raise InvariantError('population conservation failure at transport departure')

        evt=self.event(
            int(D(request.departure_time)),actor_id,ActionKind.TRANSPORT,'PASSENGER_DEPARTURE',
            (departure_id,relationship.id,state.id,request.origin_node_id,
             request.destination_node_id,str(residents),str(request.departure_time),
             str(expected_arrival),str(relationship.cost_per_passenger),
             str(relationship.travel_time),str(relationship.energy_per_passenger),
             str(relationship.loss_risk),str(relationship.capacity)),
            tuple(parent_ids))

        rec=PassengerTransportDepartureRecord(
            departure_id,decision.id,request.id,actor_id,state.id,relationship.id,
            request.origin_node_id,request.destination_node_id,residents,
            expected_support,expected_transport,D(request.departure_time),expected_arrival,
            earth_before,int(self.population.earth),transit_before,
            int(self.population.in_transit[departure_id]),total_before,int(self.population.total()),
            subsidy_before,D(colony.external_subsidy),support_txid,transport_txid,evt.id)
        rec.validate()
        self.passenger_transport_departures.append(rec)
        return rec

    def execute_passenger_transport_arrival(self,effective_time,departure_id,parent_ids=()):
        t=D(effective_time)
        departures=[r for r in self.passenger_transport_departures if r.departure_id==departure_id]
        if len(departures)!=1:
            raise InvariantError('passenger transport departure missing or ambiguous')
        if any(r.departure_id==departure_id for r in self.passenger_transport_arrivals):
            raise InvariantError('passenger transport departure already arrived')
        dep=departures[0]
        if t!=D(dep.arrival_time):
            raise InvariantError('passenger transport arrival time mismatch')
        if self.population is None:
            raise InvariantError('passenger transport population ledger missing')
        transit_before=int(self.population.in_transit.get(departure_id,0))
        if transit_before!=dep.passengers:
            raise InvariantError('passenger in-transit stock does not match departure')
        off_before=int(self.population.offworld.get(dep.destination_node_id,0))
        total_before=int(self.population.total())

        self.population.in_transit.pop(departure_id)
        self.population.offworld[dep.destination_node_id]=off_before+dep.passengers
        colony=self.colonies.setdefault(dep.destination_node_id,ColonyState(dep.destination_node_id))
        colony.population+=dep.passengers
        if self.population.total()!=total_before:
            raise InvariantError('population conservation failure at transport arrival')

        evt=self.event(
            int(t),dep.actor_id,ActionKind.TRANSPORT,'PASSENGER_ARRIVAL',
            (departure_id,dep.relationship_id,dep.destination_node_id,
             str(dep.passengers),str(t)),
            (dep.departure_event_id,*tuple(parent_ids)))
        stage=self.update_settlement_stage(
            int(t),dep.destination_node_id,
            parent_ids=(evt.id,dep.departure_event_id,*tuple(parent_ids)))
        if stage.new_stage!='DEPENDENT_SETTLEMENT':
            raise InvariantError('passenger arrival did not produce dependent settlement')

        rec=PassengerTransportArrivalRecord(
            departure_id,dep.relationship_id,dep.destination_node_id,dep.passengers,t,
            transit_before,int(self.population.in_transit.get(departure_id,0)),
            off_before,int(self.population.offworld[dep.destination_node_id]),
            total_before,int(self.population.total()),evt.id,stage.event_id)
        rec.validate()
        self.passenger_transport_arrivals.append(rec)
        return rec

    def register_financing_return_claim(self,claim:FinancingReturnClaim):
        claim.validate()
        if claim.id in self.financing_return_claims:
            raise InvariantError('duplicate financing return claim')
        if claim.project_id not in self.state.projects:
            raise InvariantError('financing return claim project missing')
        if claim.financier_id not in self.agents:
            raise InvariantError('financing return claim financier missing')
        financier=self.agents[claim.financier_id]
        if financier.kind.value!='PRIVATE_FINANCIER':
            raise InvariantError('financing return claim actor not private financier')
        if claim.destination_account_id not in self.state.accounts:
            raise InvariantError('financing return destination account missing')
        destination=self.state.accounts[claim.destination_account_id]
        if destination.owner_id!=claim.financier_id:
            raise InvariantError('financing return destination ownership mismatch')
        self.financing_return_claims[claim.id]=claim
        return claim

    def financing_return_remaining(self,claim_id):
        if claim_id not in self.financing_return_claims:
            raise InvariantError('financing return claim missing')
        claim=self.financing_return_claims[claim_id]
        settled=sum((D(r.financier_return) for r in self.surplus_distribution_records
                     if r.financing_return_claim_id==claim_id),D('0'))
        remaining=D(claim.maximum_return_amount)-settled
        if remaining<0:
            raise InvariantError('financing return claim over-settled')
        return remaining

    def _distribution_owner_account(self,owner_id):
        if owner_id in self.agents:
            aid=self.agents[owner_id].account_id
            if aid not in self.state.accounts:
                raise InvariantError('owner agent account missing')
            return aid
        candidates=[
            aid for aid,a in self.state.accounts.items()
            if a.owner_id==owner_id and a.kind==AccountKind.FUNDS
        ]
        if len(candidates)!=1:
            raise InvariantError('owner distribution account is not uniquely resolvable')
        return candidates[0]

    def execute_surplus_distribution(self,year,actor_id,request,decision,
                                     local_reinvestment_account_id):
        year=int(year)
        request.validate_protocol(); decision.validate_protocol(request)
        if decision.outcome!=SurplusDistributionDecisionOutcome.DISTRIBUTE:
            raise InvariantError('surplus execution requires DISTRIBUTE decision')
        if any(r.decision_id==decision.id for r in self.surplus_distribution_records):
            raise InvariantError('surplus distribution decision already executed')
        if actor_id!=decision.actor_id or actor_id not in self.agents:
            raise InvariantError('surplus actor/decision mismatch')
        actor=self.agents[actor_id]
        if actor.kind.value!='PRIVATE_SPONSOR' or 'DISTRIBUTE_SURPLUS' not in actor.capabilities:
            raise InvariantError('surplus actor lacks sponsor distribution authority')
        if request.project_id not in self.state.projects:
            raise InvariantError('surplus project missing')
        project=self.state.projects[request.project_id]
        if project.status!='OPERATING':
            raise InvariantError('surplus distribution requires OPERATING project')
        if request.financing_return_claim_id not in self.financing_return_claims:
            raise InvariantError('surplus financing-return claim missing')
        claim=self.financing_return_claims[request.financing_return_claim_id]
        if claim.project_id!=project.id:
            raise InvariantError('financing-return claim/project mismatch')
        destination=self.state.accounts.get(claim.destination_account_id)
        if destination is None or destination.owner_id!=claim.financier_id:
            raise InvariantError('financing-return destination mismatch')
        for cid in claim.source_commitment_ids:
            c=self.state.commitments.get(cid)
            if c is None:
                raise InvariantError('financing-return source commitment missing')
            if c.project_id!=project.id or c.financier_id!=claim.financier_id:
                raise InvariantError('financing-return source commitment mismatch')
            if D(c.disbursed)<=0:
                raise InvariantError('financing-return source commitment has no disbursed capital')
        remaining_claim=self.financing_return_remaining(claim.id)
        if D(decision.financier_return)>remaining_claim:
            raise InvariantError('financing return exceeds remaining claim')
        if local_reinvestment_account_id not in self.state.accounts:
            raise InvariantError('local reinvestment account missing')
        local_account=self.state.accounts[local_reinvestment_account_id]
        if local_account.node_id!=project.node_id:
            raise InvariantError('local reinvestment account location mismatch')

        opening=D(self.state.accounts[project.cash_account_id].balance)
        reserve=D(decision.reserve)
        financier_return=D(decision.financier_return)
        local_reinvestment=D(decision.local_reinvestment)
        owner_distribution=D(decision.owner_distribution)
        allocated=reserve+financier_return+local_reinvestment+owner_distribution
        if opening!=allocated:
            raise InvariantError('surplus decision no longer matches current project cash')
        if not project.owners or sum((D(v) for v in project.owners.values()),D('0'))!=D('1'):
            raise InvariantError('surplus project ownership invalid')

        txids=[]
        if financier_return>0:
            tx=self.transfer(
                year,project.cash_account_id,claim.destination_account_id,
                financier_return,TxPurpose.FINANCIER_RETURN,
                parent_ids=(decision.id,request.id,claim.id))
            txids.append(tx.id)

        if local_reinvestment>0:
            tx=self.transfer(
                year,project.cash_account_id,local_reinvestment_account_id,
                local_reinvestment,TxPurpose.LOCAL_REINVESTMENT,
                parent_ids=(decision.id,request.id,project.id))
            txids.append(tx.id)

        owner_allocations=[]
        owners=tuple(sorted(project.owners.items()))
        remaining_owner=owner_distribution
        for i,(owner_id,share) in enumerate(owners):
            share=D(share)
            amount=remaining_owner if i==len(owners)-1 else owner_distribution*share
            remaining_owner-=amount
            if amount<0:
                raise InvariantError('negative owner distribution')
            if amount==0:
                continue
            account_id=self._distribution_owner_account(owner_id)
            tx=self.transfer(
                year,project.cash_account_id,account_id,amount,
                TxPurpose.OWNER_DISTRIBUTION,
                parent_ids=(decision.id,request.id,project.id,owner_id))
            txids.append(tx.id)
            owner_allocations.append(
                OwnerDistributionAllocation(owner_id,account_id,share,amount,tx.id))

        closing=D(self.state.accounts[project.cash_account_id].balance)
        if closing!=reserve:
            raise InvariantError('surplus reserve/cash reconciliation failed')
        evt=self.event(
            year,actor_id,ActionKind.DISTRIBUTE,'SURPLUS_ALLOCATED',
            (project.id,str(opening),str(reserve),str(financier_return),
             str(local_reinvestment),str(owner_distribution),claim.id),
            (decision.id,))
        rec=SurplusDistributionRecord(
            year,project.id,actor_id,decision.id,claim.id,opening,reserve,
            financier_return,local_reinvestment,local_reinvestment_account_id,
            owner_distribution,tuple(owner_allocations),closing,tuple(txids),evt.id)
        try:
            rec.validate()
        except ValueError as e:
            raise InvariantError(str(e)) from e
        self.surplus_distribution_records.append(rec)
        return rec

    def register_market_envelope(self,envelope:CommodityMarketEnvelope):
        envelope.validate()
        if envelope.id in self.market_envelopes:
            raise InvariantError('duplicate market envelope')
        if envelope.resource_id not in self.resources:
            raise InvariantError('market envelope resource missing')
        if envelope.buyer_account_id not in self.state.accounts:
            raise InvariantError('market envelope buyer account missing')
        if self.state.accounts[envelope.buyer_account_id].kind!=AccountKind.EARTH_BOUNDARY:
            raise InvariantError('market envelope buyer must be EARTH_BOUNDARY')
        self.market_envelopes[envelope.id]=envelope
        return envelope

    def market_remaining_demand(self,market_state_id):
        if market_state_id not in self.market_envelopes:
            raise InvariantError('market envelope missing')
        envelope=self.market_envelopes[market_state_id]
        cleared=sum((D(r.cleared_quantity) for r in self.market_clearing_records
                     if r.market_state_id==market_state_id),D('0'))
        remaining=D(envelope.demand_quantity)-cleared
        if remaining<0:
            raise InvariantError('market demand over-cleared')
        return remaining

    def clear_market_sale(self,year,actor_id,request,decision):
        year=int(year)
        request.validate_protocol(); decision.validate_protocol(request)
        if decision.outcome!=SaleDecisionOutcome.OFFER:
            raise InvariantError('market clearing requires OFFER decision')
        if any(r.decision_id==decision.id for r in self.market_clearing_records):
            raise InvariantError('sale decision already cleared')
        if actor_id!=decision.actor_id or actor_id not in self.agents:
            raise InvariantError('market actor/decision mismatch')
        actor=self.agents[actor_id]
        if actor.kind.value!='PRIVATE_SPONSOR' or 'SELL' not in actor.capabilities:
            raise InvariantError('market actor lacks sponsor SELL authority')
        if request.observation_id not in self.observations or request.observation_id not in actor.information:
            raise InvariantError('sale information prerequisite unavailable')
        if request.market_state_id not in self.market_envelopes:
            raise InvariantError('sale market envelope missing')
        envelope=self.market_envelopes[request.market_state_id]
        envelope.validate()
        if envelope.year!=year or request.year!=year:
            raise InvariantError('sale year/market envelope mismatch')
        if envelope.resource_id!=request.resource_id:
            raise InvariantError('sale resource/market envelope mismatch')
        if request.project_id not in self.state.projects:
            raise InvariantError('sale project missing')
        project=self.state.projects[request.project_id]
        if project.status!='OPERATING':
            raise InvariantError('sale requires OPERATING project')
        if request.resource_id not in self.resources:
            raise InvariantError('sale resource missing')
        resource=self.resources[request.resource_id]
        if resource.node_id!=project.node_id:
            raise InvariantError('sale resource/project location mismatch')
        buyer=self.state.accounts.get(envelope.buyer_account_id)
        if buyer is None or buyer.kind!=AccountKind.EARTH_BOUNDARY:
            raise InvariantError('sale buyer must be EARTH_BOUNDARY')
        if D(envelope.unit_price)<=0:
            raise InvariantError('market clearing requires positive price')

        colony=self.colonies.setdefault(resource.node_id,ColonyState(resource.node_id))
        local_before=D(colony.resource_inventory)
        demand_before=self.market_remaining_demand(envelope.id)
        offered=D(decision.offered_quantity)
        if offered<=0:
            raise InvariantError('sale offer must be positive')
        cleared=min(offered,local_before,demand_before)
        if cleared<=0:
            raise InvariantError('no market-clearing quantity available')

        market_key=(buyer.node_id,request.resource_id)
        market_before=D(self.market_resource_inventory.get(market_key,D('0')))
        value=cleared*D(envelope.unit_price)
        tx=self.boundary_purchase(
            year,envelope.buyer_account_id,project.cash_account_id,value,
            request.resource_id,cleared,
            parent_ids=(decision.id,request.id,envelope.id))
        colony.resource_inventory-=cleared
        local_after=D(colony.resource_inventory)
        market_after=D(self.market_resource_inventory.get(market_key,D('0')))
        demand_after=demand_before-cleared
        evt=self.event(
            year,actor_id,ActionKind.SELL,'CLEARED',
            (request.resource_id,str(cleared),str(envelope.unit_price),str(value),
             tx.id,envelope.id,request.project_id),
            (decision.id,))
        rec=MarketClearingRecord(
            year,envelope.id,actor_id,decision.id,request.project_id,request.resource_id,
            offered,demand_before,cleared,demand_after,D(envelope.unit_price),value,
            local_before,local_after,market_before,market_after,tx.id,evt.id)
        self.market_clearing_records.append(rec)
        return rec

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
        for c in self.colonies.values():
            if c.population<0 or c.habitat_capacity<0:
                raise InvariantError('negative colony population/habitat capacity')
            if min(D(c.cash),D(c.productive_capital),D(c.infrastructure),
                   D(c.resource_inventory),D(c.import_inventory),
                   D(c.production_capacity),D(c.operating_need),D(c.external_subsidy))<0:
                raise InvariantError('negative colony stock-flow state')
        if self.population is not None:
            if (self.population.earth<0 or any(v<0 for v in self.population.offworld.values())
                    or any(v<0 for v in self.population.in_transit.values())):
                raise InvariantError('negative population ledger')
            for node,count in self.population.offworld.items():
                colony=self.colonies.get(node)
                if colony is not None and colony.population!=count:
                    raise InvariantError('population ledger/colony mismatch')
        for plan in self.settlement_infrastructure_plans.values():
            try:
                plan.validate()
            except ValueError as e:
                raise InvariantError(str(e)) from e
        successful_plans=set()
        txids_all={t.id:t for t in self.state.transactions}
        for r in self.settlement_infrastructure_records:
            try:
                r.validate()
            except ValueError as e:
                raise InvariantError(str(e)) from e
            if r.outcome=='INSTALLED':
                if r.plan_id in successful_plans:
                    raise InvariantError('duplicate installed settlement infrastructure plan')
                successful_plans.add(r.plan_id)
                tx=txids_all.get(r.transaction_id)
                if tx is None or tx.purpose!=TxPurpose.CAPEX or D(tx.amount)!=D(r.cost):
                    raise InvariantError('settlement infrastructure transaction drift')
        for r in self.settlement_stage_records:
            try:
                r.validate()
            except ValueError as e:
                raise InvariantError(str(e)) from e
        for node in {r.node_id for r in self.settlement_stage_records}:
            colony=self.colonies[node]
            expected=derive_settlement_stage(
                colony.production_capacity,colony.population,colony.infrastructure,
                colony.habitat_capacity,colony.external_subsidy)
            if colony.stage!=expected:
                raise InvariantError('settlement stage drift')
        seen_support=set()
        for r in self.settlement_support_records:
            if r.decision_id in seen_support:
                raise InvariantError('duplicate settlement support decision')
            seen_support.add(r.decision_id)
            try:
                r.validate()
            except ValueError as e:
                raise InvariantError(str(e)) from e
            if r.support_amount>0:
                tx=txids_all.get(r.support_transaction_id)
                if tx is None or tx.purpose!=TxPurpose.PUBLIC_SUBSIDY or D(tx.amount)!=D(r.support_amount):
                    raise InvariantError('settlement support transaction drift')
        for state in self.technology_capability_states.values():
            try:
                state.validate()
            except ValueError as e:
                raise InvariantError(str(e)) from e
        for relationship in self.transport_relationships.values():
            try:
                relationship.validate()
            except ValueError as e:
                raise InvariantError(str(e)) from e
            origin=self.state.nodes.get(relationship.origin_node_id)
            destination=self.state.nodes.get(relationship.destination_node_id)
            if origin is None or destination is None or origin.kind!=NodeKind.EARTH or destination.kind!=NodeKind.OFFWORLD:
                raise InvariantError('transport relationship direction/node drift')
        arrival_by_departure={r.departure_id:r for r in self.passenger_transport_arrivals}
        if len(arrival_by_departure)!=len(self.passenger_transport_arrivals):
            raise InvariantError('duplicate passenger transport arrival')
        seen_transport_decisions=set()
        for r in self.passenger_transport_departures:
            if r.decision_id in seen_transport_decisions:
                raise InvariantError('duplicate transport settlement decision departure')
            seen_transport_decisions.add(r.decision_id)
            try:
                r.validate()
            except ValueError as e:
                raise InvariantError(str(e)) from e
            if r.support_amount>0:
                tx=txids_all.get(r.support_transaction_id)
                if tx is None or tx.purpose!=TxPurpose.PUBLIC_SUBSIDY or D(tx.amount)!=D(r.support_amount):
                    raise InvariantError('transport settlement support transaction drift')
            if r.transport_amount>0:
                tx=txids_all.get(r.transport_transaction_id)
                if tx is None or tx.purpose!=TxPurpose.TRANSPORT_PAYMENT or D(tx.amount)!=D(r.transport_amount):
                    raise InvariantError('passenger transport payment transaction drift')
            if r.departure_id in arrival_by_departure:
                if self.population is not None and self.population.in_transit.get(r.departure_id,0)!=0:
                    raise InvariantError('arrived passenger batch remains in transit')
            else:
                if self.population is None or self.population.in_transit.get(r.departure_id,0)!=r.passengers:
                    raise InvariantError('pending passenger batch in-transit stock drift')
        for r in self.passenger_transport_arrivals:
            try:
                r.validate()
            except ValueError as e:
                raise InvariantError(str(e)) from e
            if not any(d.departure_id==r.departure_id for d in self.passenger_transport_departures):
                raise InvariantError('passenger arrival missing departure lineage')
        for c in self.financing_return_claims.values():
            try:
                c.validate()
            except ValueError as e:
                raise InvariantError(str(e)) from e
            if c.project_id not in self.state.projects:
                raise InvariantError('financing return claim project drift')
            if c.destination_account_id not in self.state.accounts:
                raise InvariantError('financing return destination drift')
            if self.financing_return_remaining(c.id)<0:
                raise InvariantError('negative financing return remaining')
        seen_distributions=set()
        for r in self.surplus_distribution_records:
            if r.decision_id in seen_distributions:
                raise InvariantError('duplicate surplus distribution decision')
            seen_distributions.add(r.decision_id)
            try:
                r.validate()
            except ValueError as e:
                raise InvariantError(str(e)) from e
            if r.financing_return_claim_id not in self.financing_return_claims:
                raise InvariantError('surplus distribution claim lineage missing')
            p=self.state.projects.get(r.project_id)
            if p is None:
                raise InvariantError('surplus distribution project missing')
            if sum((D(a.ownership_share) for a in r.owner_allocations),D('0')) not in (D('0'),D('1')):
                # Zero is legal when no owner residual was paid.
                raise InvariantError('owner allocation share reconciliation')
        for e in self.market_envelopes.values():
            e.validate()
            if e.resource_id not in self.resources or e.buyer_account_id not in self.state.accounts:
                raise InvariantError('market envelope lineage missing')
            if self.state.accounts[e.buyer_account_id].kind!=AccountKind.EARTH_BOUNDARY:
                raise InvariantError('market envelope buyer-kind drift')
            if self.market_remaining_demand(e.id)<0:
                raise InvariantError('negative remaining market demand')
        txids={t.id:t for t in self.state.transactions}
        seen_sale=set()
        for r in self.market_clearing_records:
            if r.decision_id in seen_sale:
                raise InvariantError('duplicate market clearing decision')
            seen_sale.add(r.decision_id)
            if r.market_state_id not in self.market_envelopes:
                raise InvariantError('market clearing envelope missing')
            env=self.market_envelopes[r.market_state_id]
            if D(r.cleared_quantity)<=0 or D(r.cleared_quantity)>D(r.offered_quantity):
                raise InvariantError('market cleared quantity invalid')
            if D(r.demand_after)!=D(r.demand_before)-D(r.cleared_quantity):
                raise InvariantError('market demand rollforward drift')
            if D(r.local_inventory_after)!=D(r.local_inventory_before)-D(r.cleared_quantity):
                raise InvariantError('local sale inventory rollforward drift')
            if D(r.market_inventory_after)!=D(r.market_inventory_before)+D(r.cleared_quantity):
                raise InvariantError('market inventory rollforward drift')
            if D(r.transaction_value)!=D(r.cleared_quantity)*D(r.unit_price):
                raise InvariantError('market value arithmetic drift')
            tx=txids.get(r.transaction_id)
            if tx is None or tx.purpose!=TxPurpose.REVENUE or D(tx.amount)!=D(r.transaction_value):
                raise InvariantError('market revenue transaction drift')
            if tx.source_account!=env.buyer_account_id or tx.destination_account!=self.state.projects[r.project_id].cash_account_id:
                raise InvariantError('market revenue counterparty drift')
        seen_operating=set()
        for r in self.operating_cost_records:
            if r.decision_id in seen_operating:
                raise InvariantError('duplicate operating cost decision')
            seen_operating.add(r.decision_id)
            if D(r.total_opex)!=D(r.planned_quantity)*D(r.unit_opex):
                raise InvariantError('operating cost arithmetic drift')
            tx=txids.get(r.transaction_id)
            if tx is None or tx.purpose!=TxPurpose.OPEX or D(tx.amount)!=D(r.total_opex):
                raise InvariantError('operating cost transaction drift')
        seen_extract=set()
        for r in self.extraction_resolution_records:
            if r.decision_id in seen_extract:
                raise InvariantError('duplicate extraction resolution')
            seen_extract.add(r.decision_id)
            if D(r.actual_extracted)<0 or D(r.actual_extracted)>D(r.planned_quantity):
                raise InvariantError('extraction quantity drift')
            if D(r.resource_after)!=D(r.resource_before)-D(r.actual_extracted):
                raise InvariantError('extraction resource rollforward drift')
            if D(r.inventory_after)!=D(r.inventory_before)+D(r.actual_extracted):
                raise InvariantError('extraction inventory rollforward drift')
        extraction_by_event={r.extraction_event_id:r for r in self.extraction_resolution_records}
        reviewed=set()
        for r in self.enterprise_review_records:
            if r.extraction_event_id in reviewed or r.extraction_event_id not in extraction_by_event:
                raise InvariantError('enterprise-review extraction lineage drift')
            reviewed.add(r.extraction_event_id)
            try:
                r.validate()
            except ValueError as e:
                raise InvariantError(str(e)) from e
            x=extraction_by_event[r.extraction_event_id]
            if (x.project_id!=r.project_id or D(x.planned_quantity)!=D(r.planned_quantity)
                    or D(x.actual_extracted)!=D(r.actual_output)):
                raise InvariantError('enterprise-review output lineage drift')
        for r in self.surface_prospecting_records:
            if r.observation_id not in self.observations:
                raise InvariantError('surface observation record missing observation')
            o=self.observations[r.observation_id]
            if o.channel!='SURFACE' or o.resource_id!=r.resource_id or o.actor_id!=r.actor_id:
                raise InvariantError('surface observation record drift')
            if r.prerequisite_observation_id not in self.observations:
                raise InvariantError('surface prerequisite lineage missing')
        for r in self.observation_belief_update_records:
            if r.observation_id not in self.observations or r.agent_id not in self.agents:
                raise InvariantError('belief update lineage missing')
            if not (D('0')<=D(r.prior)<=D('1') and D('0')<=D(r.posterior)<=D('1')):
                raise InvariantError('belief update probability drift')
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
             for r in self.development_resolution_records],
          'surface_prospecting_records':[(r.year,r.actor_id,r.resource_id,r.prerequisite_observation_id,
             r.observation_id,r.world_model_id,str(r.world_false_positive),str(r.world_false_negative),
             str(r.deterministic_draw),r.signal,r.expenditure_transaction_id,r.exploration_asset_id,r.record_version)
             for r in self.surface_prospecting_records],
          'observation_belief_update_records':[(r.year,r.agent_id,r.observation_id,r.belief_key,str(r.prior),
             str(r.posterior),str(r.detection_rate),str(r.false_positive_rate),r.model_id,r.source_ref,
             r.event_id,r.record_version) for r in self.observation_belief_update_records],
          'operating_cost_records':[(r.year,r.actor_id,r.decision_id,r.project_id,r.asset_id,r.supplier_account_id,
             str(r.planned_quantity),str(r.unit_opex),str(r.total_opex),r.transaction_id,r.event_id,r.record_version)
             for r in self.operating_cost_records],
          'extraction_resolution_records':[(r.year,r.actor_id,r.decision_id,r.project_id,r.asset_id,r.resource_id,
             str(r.planned_quantity),str(r.actual_extracted),str(r.resource_before),str(r.resource_after),
             str(r.inventory_before),str(r.inventory_after),r.extraction_event_id,r.record_version)
             for r in self.extraction_resolution_records],
          'enterprise_review_records':[(r.year,r.actor_id,r.decision_id,r.request_id,r.project_id,
             r.extraction_event_id,str(r.planned_quantity),str(r.actual_output),r.outcome.value,
             r.status_before,r.status_after,r.event_id,r.record_version)
             for r in self.enterprise_review_records],
          'market_envelopes':sorted((e.id,e.year,e.resource_id,e.buyer_account_id,str(e.unit_price),
             str(e.demand_quantity),e.currency_unit,e.quantity_unit,e.source_ref,e.epistemic_status,e.envelope_version)
             for e in self.market_envelopes.values()),
          'market_clearing_records':[(r.year,r.market_state_id,r.actor_id,r.decision_id,r.project_id,r.resource_id,
             str(r.offered_quantity),str(r.demand_before),str(r.cleared_quantity),str(r.demand_after),
             str(r.unit_price),str(r.transaction_value),str(r.local_inventory_before),str(r.local_inventory_after),
             str(r.market_inventory_before),str(r.market_inventory_after),r.transaction_id,r.event_id,r.record_version)
             for r in self.market_clearing_records],
          'financing_return_claims':sorted((c.id,c.financier_id,c.project_id,c.destination_account_id,
             str(c.maximum_return_amount),c.source_commitment_ids,c.source_ref,c.epistemic_status,c.claim_version)
             for c in self.financing_return_claims.values()),
          'surplus_distribution_records':[(r.year,r.project_id,r.actor_id,r.decision_id,r.financing_return_claim_id,
             str(r.opening_project_cash),str(r.reserve),str(r.financier_return),str(r.local_reinvestment),
             r.local_reinvestment_account_id,str(r.owner_distribution),
             tuple((a.owner_id,a.destination_account_id,str(a.ownership_share),str(a.amount),a.transaction_id)
                   for a in r.owner_allocations),
             str(r.closing_project_cash),r.transaction_ids,r.event_id,r.record_version)
             for r in self.surplus_distribution_records],
          'settlement_infrastructure_plans':sorted((x.id,x.year,x.node_id,x.source_account_id,x.supplier_account_id,
             str(x.infrastructure_cost),x.habitat_capacity,x.source_ref,x.epistemic_status,x.plan_version)
             for x in self.settlement_infrastructure_plans.values()),
          'settlement_infrastructure_records':[(r.year,r.plan_id,r.node_id,r.outcome,str(r.cost),
             r.habitat_capacity_added,str(r.infrastructure_before),str(r.infrastructure_after),
             r.habitat_capacity_before,r.habitat_capacity_after,r.transaction_id,r.event_id,r.record_version)
             for r in self.settlement_infrastructure_records],
          'settlement_stage_records':[(r.year,r.node_id,r.prior_stage,r.new_stage,str(r.productive_capital),
             str(r.production_capacity),r.population,str(r.infrastructure),r.habitat_capacity,
             str(r.external_subsidy),r.event_id,r.rule_version)
             for r in self.settlement_stage_records],
          'settlement_support_records':[(r.year,r.actor_id,r.decision_id,r.node_id,r.authorized_residents,
             str(r.support_amount),r.earth_population_before,r.earth_population_after,
             r.offworld_population_before,r.offworld_population_after,r.total_population_before,
             r.total_population_after,str(r.subsidy_before),str(r.subsidy_after),
             r.support_transaction_id,r.migration_event_id,r.stage_event_id,r.record_version)
             for r in self.settlement_support_records],
          'technology_capability_states':sorted((
             x.id,str(x.effective_from),str(x.effective_to),x.qualified_capabilities,
             x.source_ref,x.epistemic_status,x.state_version)
             for x in self.technology_capability_states.values()),
          'transport_relationships':sorted((
             x.id,x.origin_node_id,x.destination_node_id,str(x.effective_from),str(x.effective_to),
             x.required_capability_id,str(x.cost_per_passenger),str(x.travel_time),
             str(x.energy_per_passenger),str(x.loss_risk),x.capacity,x.passenger_class,
             x.source_ref,x.epistemic_status,x.relationship_version)
             for x in self.transport_relationships.values()),
          'passenger_transport_departures':[(
             r.departure_id,r.decision_id,r.request_id,r.actor_id,r.technology_state_id,
             r.relationship_id,r.origin_node_id,r.destination_node_id,r.passengers,
             str(r.support_amount),str(r.transport_amount),str(r.departure_time),str(r.arrival_time),
             r.earth_population_before,r.earth_population_after,r.in_transit_before,r.in_transit_after,
             r.total_population_before,r.total_population_after,str(r.subsidy_before),str(r.subsidy_after),
             r.support_transaction_id,r.transport_transaction_id,r.departure_event_id,r.record_version)
             for r in self.passenger_transport_departures],
          'passenger_transport_arrivals':[(
             r.departure_id,r.relationship_id,r.destination_node_id,r.passengers,str(r.arrival_time),
             r.in_transit_before,r.in_transit_after,r.offworld_population_before,
             r.offworld_population_after,r.total_population_before,r.total_population_after,
             r.arrival_event_id,r.stage_event_id,r.record_version)
             for r in self.passenger_transport_arrivals]}
        if include_scheduler:
            payload['scheduler']=self.scheduler.fingerprint()
        return payload

    def decision_epoch_state_fingerprint(self):
        payload=self._methodology_payload(include_scheduler=False)
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

    def methodology_fingerprint(self):
        payload=self._methodology_payload(include_scheduler=True)
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
