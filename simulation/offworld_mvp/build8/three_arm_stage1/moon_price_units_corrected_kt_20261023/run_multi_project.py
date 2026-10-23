"""Opt-in portfolio full-clock experiment; all artifacts stay beside this file."""
from __future__ import annotations
import csv, hashlib, json, time
from collections import Counter, defaultdict
from copy import deepcopy
from decimal import Decimal as D
from pathlib import Path

from simulation.offworld_mvp.build8.route1_cast_payments import run_cast_payments
from simulation.offworld_mvp.build8.route1_all_body_campaign_pr3b import AllBodyCampaign, ALL_BODIES
from simulation.offworld_mvp.build8.route1_body_campaign import ORDER
from simulation.offworld_mvp.build8.sponsor_executor_network_trial import EXECUTORS
from simulation.offworld_mvp.build8.ceres_downstream import CeresDownstream, T as CERES_T
from simulation.offworld_mvp.build8.three_arm_stage1.sponsor_refill_v3_kt_20261023.general_project import (
    ProjectState, EconomicLifecycle, scenario_identity, _total_money)
from offworld_kernel.mvp_state import ScenarioResource
from simulation.offworld_mvp.build8.three_arm_stage1.general_project_v2_kt_20261022.run_step2_4 import (
    ordered_projection, first_difference, jsonable)
from simulation.offworld_mvp.build8.three_arm_stage1.RENDEZVOUS_V2_PAIRED_REPLAY_TEST_ONLY import replay
from simulation.offworld_mvp.build6e.generated_world import load_inputs as load_generated_world_inputs
from simulation.offworld_mvp.phase3b.kernel.offworld_kernel.policy import FactState, SnapshotFact, build_decision_snapshot
from simulation.offworld_mvp.phase3b.kernel.offworld_kernel.project_activity import build_sponsor_portfolio_request
from simulation.offworld_mvp.phase3b.kernel.offworld_kernel.policy_runner import run_sponsor_portfolio_policy

HERE=Path(__file__).resolve().parent
STAGE1=HERE.parent
V2=STAGE1/'general_project_v2_kt_20261022'
SCENARIO_PATH=V2/'scenario_step2_4.json'
PRICE_PATH=STAGE1/'A_VEHICLE_MISSION_PAIRS.csv'
AUDIT_PATH=STAGE1/'general_project_rule_kt_20261022'/'price_provenance_audit.json'
EXPECTED_ROUTE1='4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430'
SCENARIO=json.loads((HERE/'scenario.json').read_text())


def load_inputs():
    sb=SCENARIO_PATH.read_bytes(); scenario=json.loads(sb)
    pb=PRICE_PATH.read_bytes(); prices=list(csv.DictReader(pb.decode('utf-8-sig').splitlines()))
    return scenario,sb,pb,prices,json.loads(AUDIT_PATH.read_text())

def write(name,obj):
    (HERE/name).write_text(json.dumps(jsonable(obj),sort_keys=True,indent=2)+'\n')

def run(campaign,scenario):
    start=int(SCENARIO['clock']['start_year']); end=int(SCENARIO['clock']['end_year'])
    campaign.record_states(start)
    t=time.perf_counter()
    result=run_cast_payments(share=CERES_T('share'),end_year=end,
        run_setting={'name':'general_project_campaign','campaign':campaign})
    return result,time.perf_counter()-t

class PortfolioLifecycle(EconomicLifecycle):
    """Project-scoped adapter for the legacy P/MINE-P recovery API."""
    def _construction(self,kernel,year):
        p=self.p
        cost=(p.value('construction_stage_1') if year==p.offset_year('construction_year_1')
              else p.value('construction_stage_2'))
        kernel.set_resource_constraint('EARTH:'+p.definition['executor_location'],year,cost,
                                       p.family_value('earth_supply_fraction'))
        stage=kernel.execute_development_stage(year,p.plan)
        assert stage.outcome.value=='SPENT'
        p.physical.append(dict(year=year,stage='CONSTRUCTION',amount=str(cost),
            tx=stage.transaction_id,project_cash=str(kernel.state.accounts[p.cash].balance),
            supplier_balance=str(kernel.state.accounts[self.supplier].balance)))
        if year==p.offset_year('construction_year_2'):
            commissioned=kernel.resolve_development_plan(year,p.plan)
            assert commissioned.outcome.value=='OPERATING'
            # The existing implementation hard-codes legacy singleton IDs.
            # Temporarily alias those keys to this real project's objects so
            # the kernel's validated state transition remains authoritative.
            if 'P' in kernel.state.projects or 'MINE-P' in kernel.state.assets:
                raise RuntimeError('legacy recovery aliases are already occupied')
            kernel.state.projects['P']=kernel.state.projects[p.project]
            kernel.state.assets['MINE-P']=kernel.state.assets[p.asset]
            try:
                kernel.assess_resource_recoverability(year,p.resource,ScenarioResource(
                    p.resource,p.node,p.definition['material_family'],p.family_value('in_situ'),
                    p.family_value('accessible'),p.family_value('recoverable'),p.family_value('recoverable')))
            finally:
                del kernel.state.projects['P']; del kernel.state.assets['MINE-P']
            p.physical.append(dict(year=year,stage='COMMISSIONED',asset=p.asset,
                capacity=str(kernel.state.assets[p.asset].capacity),
                remaining=str(kernel.resources[p.resource].remaining)))

class PortfolioCampaign(AllBodyCampaign):
    """Route1 study pipeline plus rule-generated, independently stateful projects."""
    def __init__(self,scenario,prices,audit,conversion=True,mission_type=None):
        AllBodyCampaign.__init__(self,body_count=90,ceilings_enabled=True)
        self.scenario=scenario; self.conversion=conversion
        self.sale_cap=int(scenario.get("sponsor_refill_sweep",{}).get("sale_cap",4))
        self.mission_type=mission_type or SCENARIO['mission']['type']
        self.project_states={}; self.lifecycles={}; self.started=[]; self.project_completed=[]
        self.project_rows=[]; self.year_rows=[]; self.unpriced=[]; self.ties=[]
        self.pending_candidates={}
        self.placeholder=0; self.receipt_by_id={}
        self.body_index={b:i for i,b in enumerate(self.bodies)}
        world,_=load_generated_world_inputs()
        self.world_material_applicability={b:world[b]['material_model_applicability'] for b in self.bodies}
        self.family_by_body={b:SCENARIO['family_assignment']['family'] for b in self.bodies}
        self.family_status_by_body={b:SCENARIO['family_assignment']['status'] for b in self.bodies}
        self.main_quotes={}; self.flyby_quotes={}; self.rv_quotes={}
        # Separate source populations. For physical decisions use the recovered
        # combined rendezvous quote when available, otherwise the dedicated V2
        # rendezvous quote. Never average or add unlike quote rows.
        for r in audit['matrix']:
            if r['calendar_year']!=SCENARIO['mission']['quote_year'] or r['status']!='PRICED_TEST_ONLY': continue
            body=r['body']; mission=r['mission_type']; rec=r['quotes']
            if not rec: continue
            if mission==self.mission_type:
                if self.mission_type==SCENARIO['mission']['flyby_comparison_type']:
                    selected=next((x for x in rec if x['source']=='vehicle_flyby'),None) or next(iter(rec),None)
                else:
                    selected=next((x for x in rec if x['source']=='pr427_complete_moon_giant'),None) or next((x for x in rec if x['source']=='recovered_combined_59'),None)
                    selected=selected or next((x for x in rec if x['source']=='rendezvous_v2_90'),None)
                if selected:
                    fields=selected['price_fields']; val=next((fields[k] for k in ('lowest_price_usd','total_usd','model_units') if fields.get(k)),None)
                    if val is not None: self.main_quotes[body]=(D(val),selected)
                self.rv_quotes[body]=rec
            if mission==SCENARIO['mission']['flyby_comparison_type']:
                self.flyby_quotes[body]=rec
        self.all_unpriced=[dict(body=b,mission_type=self.mission_type,calendar_year=SCENARIO['mission']['quote_year'],
            reason=(f"No supported {SCENARIO['mission']['quote_year']} {self.mission_type} quote in pinned source." if b not in self.main_quotes else None))
            for b in self.bodies if b not in self.main_quotes]
        self.mission_rows={r['body']:r for r in prices if r.get('mission_type_id')==self.mission_type and r.get('status')=='PRICED_TEST_ONLY'}
        self.lifecycle_base=deepcopy(scenario['project'])
        self.last_year=SCENARIO['clock']['start_year']
        self.initial_total=None

    def _definition(self,body,sponsor,executor,eligibility):
        i=self.body_index[body]; tag=f'{i:03d}_{body}_{sponsor}'
        d=deepcopy(self.lifecycle_base); d.update(body=body,sponsor=sponsor,executor=executor,
            executor_location=EXECUTORS[executor][0],material_family=self.family_by_body[body],
            project_id='PORTFOLIO:'+tag,start_year=eligibility-13)
        d['operator_grants']=[]
        # Retain the Ceres-validated lifecycle offsets: finance begins at the
        # reviewed-positive eligibility year (base year is eligibility - 13).
        family=self.scenario['material_families'][d['material_family']]
        operation_amount=D(family['quantity_per_operation'])*D(family['unit_opex'])
        d['appropriations']=[
            {'receipt_offset':15,'paid_offset':18,'amount':str(operation_amount),'reason':'Owner-return-funded synthetic operation 1'},
            {'receipt_offset':16,'paid_offset':19,'amount':str(operation_amount),'reason':'Owner-return-funded synthetic operation 2'}]
        if not self.scenario.get('scripted_appropriations_enabled', True):
            d['appropriations'] = []
        d['scripted_appropriations_enabled'] = self.scenario.get('scripted_appropriations_enabled', True)
        for key in ('accounts','ids'):
            d[key]=deepcopy(d[key])
        stem='portfolio:'+tag
        d['accounts'].update(project_cash=stem+':cash',financier_cash=stem+':financier',reinvestment=stem+':reinvest')
        ids=d['ids']; ids.update(node='OFF:'+stem,asset='ASSET:'+stem,resource='RESOURCE:'+stem,
            commitment='COMMIT:'+stem,return_claim='CLAIM:'+stem,plan='PLAN:'+stem,wip='WIP:'+stem,
            policy='BOX3_REVIEWED_POSITIVE_STUDY:'+tag,development_plan_basis='TEST_ONLY:'+stem,
            financing_claim_basis='TEST_ONLY:'+stem,financing_claim_scope='SYNTHETIC_NOT_A_FORECAST:'+stem,
            operate_request_prefix=stem+':operate:',operate_decision_prefix=stem+':operate:decision:',
            operate_decision_evidence_prefix='TEST_ONLY:'+stem+':operate:',
            market_prefix=stem+':market:',sale_request_prefix=stem+':sale:',
            sale_decision_prefix=stem+':sale:decision:',sale_decision_evidence_prefix='TEST_ONLY:'+stem+':market:',
            distribution_request_prefix=stem+':dist:',distribution_decision_prefix=stem+':dist:decision:',
            distribution_decision_evidence_prefix='TEST_ONLY:'+stem+':dist:')
        return d

    def _positive_a1_candidates(self,year):
        out=[]
        for r in self.studies:
            if r['stage']!='A1' or r['year']!=year or r['result']!='SUPPORTS_ADVANCE': continue
            b,s=r['body'],r['sponsor']
            key=(b,s)
            if key in self.project_states: continue
            if not SCENARIO['family_assignment']['supports_extraction_proxy']:
                self.project_rows.append(dict(year=year,body=b,sponsor=s,outcome='DEFERRED_FAMILY_NOT_EXTRACTION_SUPPORTING',family_status='PLACEHOLDER'))
                continue
            receipt=next((x for x in self.receipts if x['disbursement_id']==r['disbursement_id']),None)
            if receipt is None or receipt['delivery']!='DELIVERED': continue
            ex=receipt['executor']; q=self.main_quotes.get(b)
            if q is None:
                self.unpriced.append(dict(body=b,sponsor=s,eligibility_year=year,mission_type=self.mission_type,reason=f"No supported {SCENARIO['mission']['quote_year']} {self.mission_type} quote in its pinned source."))
                continue
            usd,source=q
            price=usd/D(self.scenario['price_inputs']['usd_per_model_currency']) if self.conversion else D(0)
            d=self._definition(b,s,ex,year); state=ProjectState(d,self.scenario['material_families'])
            required=price+state.value('physical_construction_cost')+state.value('operating_float')
            out.append(dict(body=b,sponsor=s,executor=ex,eligibility_year=year,roster_index=self.body_index[b],
                mission_usd=str(usd),mission_model_currency=str(price),source=source,
                commitment=str(required),state=state,review=r,receipt=receipt,family_status='PLACEHOLDER'))
        return out

    def _policy_filter(self,k,candidates,year):
        selected=[]; self.last_policy_decisions=[]
        for sponsor in self.requesters:
            group=[c for c in candidates if c['sponsor']==sponsor]
            if not group: continue
            # Priority encodes lowest total commitment, then earliest eligible year, then roster index.
            group.sort(key=lambda c:(D(c['commitment']),c['eligibility_year'],c['roster_index']))
            aid_by_id={}; facts=[SnapshotFact('portfolio.AVAILABLE_CAPITAL',FactState.KNOWN,
                str(k.project_activity_available_capital(sponsor)),'KERNEL:UNCOMMITTED_SPONSOR_CASH')]
            for rank,c in enumerate(group,1):
                aid=f"MP:{year}:{sponsor}:{c['body']}"; aid_by_id[aid]=c
                fields=(('PROJECT_ID',c['state'].project),('PROJECT_STATUS','PROPOSED'),('STATUS','PROPOSED'),
                    ('COMMITMENT',c['commitment']),('PRIORITY',str(rank)),('WINDOW_VALID','1'))
                facts.extend(SnapshotFact(f'activity.{aid}.{key}',FactState.KNOWN,str(value),'SCENARIO:PORTFOLIO_CANDIDATE') for key,value in fields)
            snap=build_decision_snapshot(k,sponsor,f'MULTI_PROJECT:{year}:{sponsor}',year,facts)
            request=build_sponsor_portfolio_request(f'MULTI_PROJECT:PORTFOLIO:{year}:{sponsor}',year,tuple(aid_by_id))
            dec=run_sponsor_portfolio_policy(snap,request,'MULTI_PROJECT:SPONSOR_POLICY').decision
            self.last_policy_decisions.append(dict(year=year,sponsor=sponsor,outcome=dec.outcome.value,
                reason=dec.reason_code.value,selected_activity_id=dec.selected_activity_id,
                selected_body=aid_by_id[dec.selected_activity_id]['body'] if dec.selected_activity_id else None,
                available_capital=str(snap.account_balance),policy_version=dec.policy_version))
            if dec.selected_activity_id: selected.append(aid_by_id[dec.selected_activity_id])
            else:
                self.project_rows.append(dict(year=year,sponsor=sponsor,outcome='DEFERRED_BY_SPONSOR_PORTFOLIO_POLICY',
                    policy_reason=dec.reason_code.value,eligible_candidates=[c['body'] for c in group],
                    retry='REATTEMPT_NEXT_ANNUAL_POLICY_CALLBACK'))
        return selected

    def _start_proposal(self,k,candidate,year):
        p=candidate['state']; flow=PortfolioLifecycle(p,self.scenario); budget='route1:budget:'+p.sponsor
        # Distinct buyer account per project, so every independent project has
        # finite demand/cash and its own settlement checks.
        buyer=deepcopy(candidate['state'].definition['buyer']); buyer['account']='BUYER:'+p.project
        candidate['state'].definition['buyer']=buyer; flow=PortfolioLifecycle(p,self.scenario)
        if budget not in k.state.accounts or k.state.accounts[budget].balance < D(candidate['commitment']):
            self.project_rows.append(dict(year=year,body=p.body,sponsor=p.sponsor,
                eligibility_year=candidate['eligibility_year'],roster_index=candidate['roster_index'],
                total_capital_commitment=candidate['commitment'],outcome='DEFERRED_INSUFFICIENT_SPONSOR_CAPITAL',
                sponsor_cash=str(k.state.accounts[budget].balance) if budget in k.state.accounts else '0'))
            return False
        if buyer['account'] not in k.state.accounts:
            from offworld_kernel.model import AccountKind, TxPurpose
            market=k.state.accounts['earth_market']
            if market.balance < D(buyer['endowment']):
                self.project_rows.append(dict(year=year,body=p.body,sponsor=p.sponsor,
                    eligibility_year=candidate['eligibility_year'],roster_index=candidate['roster_index'],
                    total_capital_commitment=candidate['commitment'],outcome='DEFERRED_INSUFFICIENT_BUYER_ENDOWMENT'))
                return False
            k.add_account(buyer['account'],'EARTH_MARKET',market.node_id,AccountKind.EARTH_BOUNDARY)
            assert k.state.accounts[buyer['account']].balance==0
            k.transfer(year,'earth_market',buyer['account'],D(buyer['endowment']),TxPurpose.OTHER_INVESTMENT,
                parent_ids=(candidate['receipt']['disbursement_id'],))
        country=k.agents[p.sponsor].node_id.removeprefix('EARTH:')
        p.definition['operator_grants']=[{'operator':p.sponsor,'owner':'STATE:'+country,
            'reason':'TEST_ONLY sponsor is authorized to operate its own reviewed-positive project'}]
        p.observation_id=candidate['review'].get('observation_id')
        supplier=flow.supplier
        if supplier not in k.state.accounts:
            from offworld_kernel.model import AccountKind
            k.add_account(supplier,p.executor,'EARTH:'+p.definition['executor_location'],AccountKind.SUPPLIER)
        price=D(candidate['mission_model_currency'])
        qtx=None
        if price>0:
            qtx=k.transfer(year,budget,supplier,price,__import__('offworld_kernel.model',fromlist=['TxPurpose']).TxPurpose.CAPEX,
                           parent_ids=(candidate['receipt']['disbursement_id'],))
        k.audit('PORTFOLIO_MISSION_PRICE_SETTLED',year,project=p.project,body=p.body,sponsor=p.sponsor,
                mission_type=self.mission_type,source=candidate['source']['source'],source_year=SCENARIO['mission']['quote_year'],
                held=year>SCENARIO['mission']['hold_after_year'],source_usd=candidate['mission_usd'],converted_price=str(price),
                classification='PRICED_TEST_ONLY_PHYSICAL_MISSION')
        flow._start(k,year,candidate['receipt']['disbursement_id'],candidate['review']['result'])
        flow._construction(k,year)
        self.project_states[(p.body,p.sponsor)]=p; self.lifecycles[(p.body,p.sponsor)]=flow
        self.started.append(dict(year=year,body=p.body,sponsor=p.sponsor,executor=p.executor,
            eligibility_year=candidate['eligibility_year'],roster_index=candidate['roster_index'],
            total_capital_commitment=candidate['commitment'],mission_price_transaction=None if qtx is None else qtx.id,
            study_receipt=candidate['receipt']['disbursement_id'],project_id=p.project))
        candidate['mission_tx']=qtx.id
        self.project_rows.append(dict(year=year,body=p.body,sponsor=p.sponsor,
            eligibility_year=candidate['eligibility_year'],roster_index=candidate['roster_index'],
            total_capital_commitment=candidate['commitment'],outcome='STARTED',project_id=p.project))
        return True

    def on_year(self,year,k,rows):
        self.initial_total=_total_money(k)
        AllBodyCampaign.on_year(self,year,k,rows)
        if self.initial_total is None: self.initial_total=_total_money(k)
        fresh=self._positive_a1_candidates(year)
        for c in fresh: self.pending_candidates[(c['body'],c['sponsor'])]=c
        candidates=list(self.pending_candidates.values())
        tie_groups=defaultdict(list)
        for c in candidates: tie_groups[D(c['commitment'])].append(c)
        for cost,group in tie_groups.items():
            by_sponsor=defaultdict(list)
            for c in group: by_sponsor[c['sponsor']].append(c)
            for sponsor,same_cost in by_sponsor.items():
                if len(same_cost)>1:self.ties.append(dict(year=year,sponsor=sponsor,commitment=str(cost),projects=[{'body':x['body'],'eligibility_year':x['eligibility_year'],'roster_index':x['roster_index']} for x in same_cost]))
        candidates=self._policy_filter(k,candidates,year)
        dominant=(dict(body=candidates[0]['body'],sponsor=candidates[0]['sponsor'],
            commitment=candidates[0]['commitment'],eligibility_year=candidates[0]['eligibility_year'],
            roster_index=candidates[0]['roster_index']) if candidates else None)
        started_before=len(self.started)
        for c in candidates:
            # Deferred candidates are reconsidered by policy at later annual callbacks.
            if self._start_proposal(k,c,year): self.pending_candidates.pop((c['body'],c['sponsor']),None)
        starts_now=[x for x in self.started if x['year']==year]
        for key,p in list(self.project_states.items()):
            flow=self.lifecycles[key]
            if p.start_year==year: continue
            if year==p.offset_year('construction_year_2'):
                flow._construction(k,year)
            elif year in p.schedule.values() and year>p.offset_year('construction_year_2'):
                if p.definition.get('scripted_appropriations_enabled', True) and year in (p.offset_year('operation_year_4'),p.offset_year('appropriation_year_2')): flow._appropriate(k,year)
                if year!=p.offset_year('appropriation_year_2'):
                    flow._operate(k,year,getattr(p,'observation_id',None),False)
                    if year in tuple(p.offset_year('operation_year_'+str(i)) for i in range(1,getattr(self,'sale_cap',2)+1)):
                        flow._sell(k,year,getattr(p,'observation_id',None)); flow._distribute(k,year)
                if year==p.offset_year('operation_year_4'): self.project_completed.append(dict(year=year,project_id=p.project,body=p.body,sponsor=p.sponsor))
        start_bodies={x['body'] for x in starts_now}; start_sponsors={x['sponsor'] for x in starts_now}
        self.year_rows.append(dict(year=year,projects_started=len(starts_now),projects_completed=sum(x['year']==year for x in self.project_completed),
            sales=sum(len(p.sales) and any(y==year for y in p.sales) for p in self.project_states.values()),
            returns=sum(sum(r['year']==year for r in p.return_receipts) for p in self.project_states.values()),
            sponsors_exhausted=tuple(sorted(s for s in self.requesters if k.state.accounts['route1:budget:'+s].balance==0)),
            body_count_started=len(start_bodies),sponsor_count_started=len(start_sponsors),
            placeholder_outputs=sum(len(p.realized_outputs) for p in self.project_states.values()),
            kernel_total_money=str(_total_money(k)),lowest_commitment_candidate=dominant,
            dominant_started=(self.started[started_before:] or None)))
        k.assert_invariants()
        total=_total_money(k)
        if total!=self.initial_total: raise AssertionError(f'global money conservation failed in {year}: {total} != {self.initial_total}')

    def report_portfolio(self):
        yearly=list(self.year_rows)
        start_year=SCENARIO['clock']['start_year']
        if not yearly or yearly[0]['year']>start_year:
            yearly.insert(0,dict(year=start_year,projects_started=0,projects_completed=0,sales=0,returns=0,
                sponsors_exhausted=(),body_count_started=0,sponsor_count_started=0,placeholder_outputs=0,
                kernel_total_money='NOT_CAPTURED',lowest_commitment_candidate=None,dominant_started=None))
        return dict(yearly=yearly,started=self.started,completed=self.project_completed,
            projects=[dict(project_id=p.project,body=p.body,sponsor=p.sponsor,executor=p.executor,
                start_year=p.start_year,material_family=p.definition['material_family'],
                physical=p.physical,sales=[(y,r.transaction_id) for y,r in p.sales.items()],
                returns=p.return_receipts,appropriations=p.appropriations,
                placeholder_outputs=p.realized_outputs) for p in self.project_states.values()],
            unpriced=self.unpriced,all_unpriced=self.all_unpriced,candidate_dispositions=self.project_rows,
            ties=self.ties,body_count=len(self.bodies),sponsor_count=len(self.requesters),
            roster=self.bodies,roster_index=self.body_index,family_by_body=self.family_by_body,
            family_status_by_body=self.family_status_by_body,world_material_applicability=self.world_material_applicability,
            family_assignment_basis='PLACEHOLDER generic authored scenario proxy; generated-world inputs expose applicability only; establishes neither geology nor extraction support',
            sponsor_policy_decisions=getattr(self,'last_policy_decisions',[]),
            zero_conversion_control=not self.conversion)

def ceres_equivalence(scenario,prices):
    ref=CeresDownstream(); generic=__import__('simulation.offworld_mvp.build8.three_arm_stage1.general_project_v2_kt_20261022.general_project',fromlist=['GeneralProjectCampaign']).GeneralProjectCampaign(scenario,prices,project_override=scenario['project'])
    outputs=[]; elapsed=[]
    start=int(SCENARIO['clock']['start_year']); end=int(SCENARIO['clock']['end_year'])
    for campaign,name in ((ref,'ceres_downstream'),(generic,'general_project_campaign')):
        campaign.record_states(start); t=time.perf_counter(); result=run_cast_payments(share=CERES_T('share'),end_year=end,run_setting={'name':name,'campaign':campaign}); elapsed.append(time.perf_counter()-t);outputs.append(ordered_projection(result['kernel']))
    diff=first_difference(outputs[0],outputs[1]); write('ceres_equivalence_reference_projection.json',outputs[0]);write('ceres_equivalence_generic_projection.json',outputs[1])
    event_count=len(outputs[0]['events'].get('kernel.events',[]))
    report=dict(result='PASS' if diff is None and len(outputs[0]['transactions'])==8798 and event_count==290 else 'FAIL',transaction_counts=[len(x['transactions']) for x in outputs],event_count=len(outputs[0]['events'].get('kernel.events',[])),event_collection_counts={k:len(v) for k,v in outputs[0]['events'].items()},ordered_zero_tolerance=diff is None,first_mismatch=diff,runtimes=elapsed)
    write('ceres_equivalence_report.json',report)
    if diff is not None or report['result']!='PASS': raise RuntimeError('Ceres zero-tolerance equivalence failed')
    return report

def main():
    scenario,sb,pb,prices,audit=load_inputs()
    write('input_identity.json',dict(scenario_sha256=hashlib.sha256(sb).hexdigest(),price_table_sha256=hashlib.sha256(pb).hexdigest(),audit_sha256=hashlib.sha256(AUDIT_PATH.read_bytes()).hexdigest(),authored_scenario_sha256=hashlib.sha256((HERE/'scenario.json').read_bytes()).hexdigest(),run_identity=scenario_identity(scenario,pb),scenario_price_policy=SCENARIO['mission'],family_assignment=SCENARIO['family_assignment'],price_sources={k:v['sha256'] for k,v in audit['sources'].items()}))
    ceres=ceres_equivalence(scenario,prices)
    full=[]
    cases=((True,'full_clock',SCENARIO['mission']['type']),(False,'zero_conversion_control',SCENARIO['mission']['type']),(True,'a1_flyby_comparison',SCENARIO['mission']['flyby_comparison_type']))
    for conversion,name,mission_type in cases:
        c=PortfolioCampaign(scenario,prices,audit,conversion,mission_type); result,elapsed=run(c,scenario); rpt=c.report_portfolio()
        # Required full coverage is tied to the campaign clock callback count.
        expected_years=SCENARIO['clock']['end_year']-SCENARIO['clock']['start_year']+1
        if len(rpt['yearly'])!=expected_years: raise RuntimeError(f'incomplete annual coverage: {len(rpt["yearly"])}')
        # Project state/account independence and conservation are checked every year.
        report=dict(run=name,year_range=[SCENARIO['clock']['start_year'],SCENARIO['clock']['end_year']],year_count=len(rpt['yearly']),runtime_seconds=elapsed,
            conversion_enabled=conversion,mission_type=mission_type,scenario_price_policy=SCENARIO['mission'],family_assignment=SCENARIO['family_assignment'],
            campaign_sponsors=len(c.requesters),bodies=len(c.bodies),projects=rpt['projects'],
            project_start_events=rpt['started'],project_completion_events=rpt['completed'],
            per_year=rpt['yearly'],unpriced=rpt['unpriced'],tie_count=len(rpt['ties']),tie_groups=rpt['ties'],
            candidate_dispositions=rpt['candidate_dispositions'],all_unpriced_reasons=rpt['all_unpriced'],
            dominance=[dict(year=y['year'],lowest_commitment_candidate=y['lowest_commitment_candidate'],dominant_started=y['dominant_started']) for y in rpt['yearly']],
            evidence_status_table=[dict(status='REAL',count=0),dict(status='PLACEHOLDER',count=len(rpt['family_status_by_body'])),dict(status='TEST_ONLY_STUDY',count=len(c.studies))],
            non_ceres_chain=[p for p in rpt['projects'] if p['body']!='CERES'],kernel_transactions=len(result['kernel'].state.transactions),zero_conversion_control=not conversion,
            source_inventory=audit['sources'],roster=rpt['roster'],family_assignment_by_body=rpt['family_by_body'],
            family_status_by_body=rpt['family_status_by_body'],family_assignment_basis=rpt['family_assignment_basis'],
            sponsor_policy_decisions=rpt['sponsor_policy_decisions'])
        write(name+'_report.json',report);full.append(report)
    control=AllBodyCampaign(body_count=90,ceilings_enabled=True); control_hash=replay(control)
    write('route1_control_report.json',dict(actual_sha256=control_hash,expected_sha256=EXPECTED_ROUTE1,pass_exact=control_hash==EXPECTED_ROUTE1))
    if control_hash!=EXPECTED_ROUTE1: raise RuntimeError('Route1 control hash mismatch')
    print(json.dumps(dict(ceres=ceres,campaigns={r['run']:dict(years=r['year_count'],projects=len(r['projects']),ties=r['tie_count'],unpriced=len(r['unpriced']),non_ceres=len(r['non_ceres_chain'])) for r in full},route1_control=control_hash),sort_keys=True))
if __name__=='__main__': main()
