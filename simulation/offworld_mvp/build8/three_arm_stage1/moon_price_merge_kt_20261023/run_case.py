"""New-file-only generic treasury receipt appropriation sensitivity, TEST_ONLY."""
import hashlib, inspect, json, textwrap
from collections import defaultdict
from decimal import Decimal as D
from pathlib import Path
from simulation.offworld_mvp.build8.three_arm_stage1.buyer_budget_sweep_kt_20261022 import run_sweep as s
from simulation.offworld_mvp.build8.sponsor_executor_network_trial import PUBLIC_PARTICIPATION, PRIVATE_PARTICIPATION
from simulation.offworld_mvp.build8.return_routing import DESTINATIONS, SOURCE

HERE=Path(__file__).resolve().parent
CONFIG=json.loads((HERE/'scenario.json').read_text())
PREVIOUS=HERE.parent/'price_life_sweep_kt_20261023'
DB=Path('data/LOOM_2226.sqlite3')
BEFORE=hashlib.sha256(DB.read_bytes()).hexdigest()
assert BEFORE=='e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde'
assert DESTINATIONS[(SOURCE,'public_agency')]==('country_treasury',3)
assert CONFIG['treasury_return_appropriation_share_levels']==['1']
assert CONFIG['sales_caps']==[4]
assert CONFIG['price_multipliers']==['1']

# V3 copies preserve all previously committed lifecycle and portfolio evidence.
from simulation.offworld_mvp.build8.three_arm_stage1.moon_price_merge_kt_20261023 import run_multi_project as v3
from simulation.offworld_mvp.build8.three_arm_stage1.sponsor_refill_v3_kt_20261023 import general_project as v3gp
from simulation.offworld_mvp.build8.three_arm_stage1.multi_project_final_kt_20261022 import run_final as final
v3.SCENARIO=json.loads((HERE.parent/'multi_project_final_kt_20261022/scenario.json').read_text())
v3.SCENARIO['scripted_appropriations_enabled']=False
s.m=v3
s.base=__import__('simulation.offworld_mvp.build8.three_arm_stage1.multi_project_rule_selection_kt_20261022.run_selection',fromlist=['run_selection'])
# FinalCampaign normally inherits the earlier portfolio. Keep the selection
# behavior, but use the v3 copied portfolio as its only campaign parent.
from simulation.offworld_mvp.build8.three_arm_stage1.multi_project_rule_selection_kt_20261022 import run_selection as selection
from simulation.offworld_mvp.build8.three_arm_stage1.multi_project_rule_selection_kt_20261022 import selection_rule
class V3RendezvousCampaign(v3.PortfolioCampaign):
    _policy_filter=selection.RuleCampaign._policy_filter
    def _start_proposal(self,kernel,candidate,year):
        try:
            return super()._start_proposal(kernel,candidate,year)
        except AttributeError as exc:
            identity=(candidate['body'],candidate['sponsor'])
            if ('NoneType' not in str(exc) or identity not in self.project_states
                or not any(x['body']==identity[0] and x['sponsor']==identity[1]
                           and x['year']==year for x in self.started)):
                raise
            candidate['mission_tx']=None
            return True
# Rebuild the established buyer/selection/boundary mixin chain on v3.
class V3Boundary(v3.PortfolioCampaign):
    def on_year(self,year,k,rows):
        self.initial_total=v3._total_money(k)
        super().on_year(year,k,rows)
class V3Selected(V3Boundary):
    _policy_filter=selection.RuleCampaign._policy_filter
    _start_proposal=selection.RuleCampaign._start_proposal
class V3Final(V3Selected):
    pass
# Existing buyer-funded campaign must resolve to V3Final, not legacy parents.
s.parent.FinalCampaign=V3RendezvousCampaign

# Ensure v3 portfolio lifecycle also inherits shared-treasury creation.
# The original shared treasury start handles multiple projects owned by one
# state, while the v3 lifecycle supplies the changed operating rules.
class V3SharedTreasuryLifecycle(s.SharedTreasuryLifecycle):
    _operate=v3gp.EconomicLifecycle._operate
    _appropriate=v3gp.EconomicLifecycle._appropriate
v3.PortfolioLifecycle=V3SharedTreasuryLifecycle
legacy_module=__import__("simulation.offworld_mvp.build8.three_arm_stage1.multi_project_campaign_kt_20261022.run_multi_project",fromlist=["PortfolioLifecycle"])
legacy_module.PortfolioLifecycle=V3SharedTreasuryLifecycle
legacy_module.PortfolioCampaign.__init__=v3.PortfolioCampaign.__init__
legacy_module.PortfolioCampaign.on_year=v3.PortfolioCampaign.on_year
legacy_module.PortfolioCampaign._definition=v3.PortfolioCampaign._definition
# Existing buyer-funded mixins ultimately dispatch into this portfolio class.
# Replace its implementation methods with the v3 copied methods for this
# process only; committed source remains unchanged.
legacy=s.m.PortfolioCampaign
for method in ('__init__','on_year','_definition','_start_proposal'):
    setattr(legacy,method,getattr(v3.PortfolioCampaign,method))
instances=[]
class RefillCampaign(s.FundedCampaign):
    _start_proposal=s.FundedCampaign._start_proposal
    sale_cap=4
    # Preserve the original tested buyer/selection mixin MRO. Route only the
    # portfolio implementation and lifecycle through their v3 copies.
    _definition=V3RendezvousCampaign._definition
    _start_proposal=s.FundedCampaign._start_proposal
    def __init__(self,*args,refill_share,**kwargs):
        self.refill_share=D(refill_share)
        self.refill_rows=[]
        self.processed_receipts=set()
        super().__init__(*args,**kwargs)
        instances.append(self)
    def _definition(self,*args):
        definition=V3RendezvousCampaign._definition(self,*args)
        definition['financier_id']=definition['project_id']+':FINANCIER'
        # Suppress old fixed two-receipt appropriations; each eligible receipt
        # instead authors its own exact amount at decision time.
        definition['appropriations']=[]
        definition['scripted_appropriations_enabled']=False
        return definition
    def on_year(self,year,k,rows):
        super().on_year(year,k,rows)
        # Use actual recorded owner-return receipts, never projected prices.
        # Run after normal callback: funds become available for next annual selection.
        for key,p in self.project_states.items():
            destination=p.owner_destination
            if destination['destination_kind']!='country_treasury':
                continue
            for receipt in p.return_receipts:
                if receipt['kind']!='owner':continue
                receipt_key=(p.project,receipt['return_tx'])
                eligible=int(receipt['year'])+int(destination['delay_years'])
                if receipt_key in self.processed_receipts or eligible>year:continue
                amount=D(receipt['amount'])*self.refill_share
                self.processed_receipts.add(receipt_key)
                if amount==0:continue
                # Existing EconomicLifecycle._appropriate validates receipt,
                # routing, delay, treasury cash, provenance and kernel transfer.
                rule={'receipt_offset':int(receipt['year'])-p.start_year,
                      'paid_offset':int(year)-p.start_year,
                      'amount':str(amount),'reason':'TEST_ONLY_AUTHORED_TREASURY_RETURN_SHARE'}
                p.definition['appropriations'].append(rule)
                try:v3gp.EconomicLifecycle._appropriate(self.lifecycles[key],k,year)
                finally:p.definition['appropriations'].pop()
                record=p.appropriations[-1]
                assert record['source_return_tx']==receipt['return_tx']
                assert record['destination_account']=='route1:budget:'+p.sponsor
                self.refill_rows.append({'year':year,'project':p.project,'sponsor':p.sponsor,
                    'source':destination['account'],'receipt_tx':receipt['return_tx'],
                    'refill_tx':record['tx'],'amount':str(amount),
                    'eligible_year':eligible})
        k.assert_invariants()

# Reuse the existing runner's effective scenario and report generation.
s.FundedCampaign=RefillCampaign
s.HERE=HERE;s.CONFIG=CONFIG;s.SCENARIO_PATH=HERE/'scenario.json'
s.m.HERE=HERE;s.m.OUT=HERE;s.base.OUT=HERE;s.m.write=s.write
s.m._total_money=s._conservation_total

s.parent.OUT=PREVIOUS
base_scenario,scenario_bytes,price_bytes,prices,audit=s.m.load_inputs()
audit=json.loads((HERE/'merged_prices.json').read_text())
price_bytes=(HERE/'merged_prices.json').read_bytes()
assert sum(x['status']=='PRICED_TEST_ONLY' for x in audit['matrix'] if x['calendar_year']==2026 and x['mission_type']=='rendezvous')==87
parent_portfolio=json.loads((PREVIOUS/'scenario_portfolio.json').read_text())
(HERE/'scenario_portfolio.json').write_text(json.dumps(parent_portfolio,sort_keys=True,indent=2)+'\n')
class ParentOutput:
    def __truediv__(self,name):
        return HERE/'scenario_portfolio.json' if name=='scenario.json' else HERE/name
s.parent.OUT=ParentOutput()
old_case=s.case_scenario
def effective_case(base,case):
    d=old_case(base,case)
    d['sponsor_refill_sweep']={'treasury_return_appropriation_share':case['refill_share'],
       'sale_cap':4,'price_multiplier':case['price_multiplier'],
       'authored_scenario_sha256':hashlib.sha256((HERE/'scenario.json').read_bytes()).hexdigest(),
       'classification':'TEST_ONLY_NONCANON'}
    for name,family in CONFIG['material_families'].items():
        d['material_families'][name]=dict(family)
        d['material_families'][name]['unit_sale_price']=str(D(family['unit_sale_price'])*D(case['price_multiplier']))
    return d
s.case_scenario=effective_case

# Step 1: all sponsors' economic owner is the state of the country of
# their actual Route 1 sponsor agent; private sponsor labels do not change
# the authored public_agency PROJECT owner type.
from simulation.offworld_mvp.build8.route1_cast_payments import run_cast_payments
from simulation.offworld_mvp.build8.route1_all_body_campaign_pr3b import AllBodyCampaign
from simulation.offworld_mvp.build8.three_arm_stage1.RENDEZVOUS_V2_PAIRED_REPLAY_TEST_ONLY import replay
route1=replay(AllBodyCampaign(body_count=90,ceilings_enabled=True))
assert route1==s.m.EXPECTED_ROUTE1,(route1,s.m.EXPECTED_ROUTE1)
parity=s.m.ceres_equivalence(base_scenario,prices)
assert parity['result']=='PASS'
firewall=s.base.tripwire_check();assert firewall['deliberate_hidden_field']=='REJECTED'

cases=[{'name':f'share_{share.replace(".","p")}_price_x{price}_sales_4',
        'mission_type':'rendezvous','conversion':True,'annual_inflow':'1000',
        'price_multiplier':price,'refill_share':share}
       for share in CONFIG['treasury_return_appropriation_share_levels']
       for price in CONFIG['price_multipliers']]
identity={'authored_scenario_sha256':hashlib.sha256((HERE/'scenario.json').read_bytes()).hexdigest(),
          'world_db_before_sha256':BEFORE,'base_scenario_sha256':hashlib.sha256(scenario_bytes).hexdigest(),
          'price_table_sha256':hashlib.sha256(price_bytes).hexdigest(),
          'return_routing':{str(k):v for k,v in DESTINATIONS.items()},'cases':cases}
identity['run_identity_sha256']=hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest()
s.write('input_identity.json',identity)
rows=[];sponsor_report=None
for case in cases:
    RefillCampaign.current_share=case['refill_share']
    # Existing run_case calls the campaign with the fixed buyer args only.
    # The authored case share is read from the class for that run.
    original_init=RefillCampaign.__init__
    def case_init(self,*args,**kwargs):
        return original_init(self,*args,refill_share=RefillCampaign.current_share,**kwargs)
    RefillCampaign.__init__=case_init
    try:report=s.run_case(case,base_scenario,scenario_bytes,price_bytes,prices,audit)
    finally:RefillCampaign.__init__=original_init
    campaign=instances[-1]
    if sponsor_report is None:
        sponsor_report=[]
        for sponsor in sorted(campaign.requesters):
            # Every actual project owner is STATE:<sponsor agent Earth country>.
            country=next((p.owner_destination['country'] for p in campaign.project_states.values() if p.sponsor==sponsor),None)
            if country is None:
                # Sponsors without starts still have authored participation country;
                # do not misrepresent a project return that never occurred.
                from simulation.offworld_mvp.build8.sponsor_executor_network_trial import PUBLIC,PRIVATE
                countries=(PUBLIC.get(sponsor) or PRIVATE.get(sponsor) or ())
                country=countries[0] if countries else 'NO_PROJECT_OWNER'
            sponsor_report.append({'sponsor':sponsor,'project_owner_type':'public_agency',
               'project_owner':'STATE:'+country if country!='NO_PROJECT_OWNER' else None,
               'return_destination':'treasury:'+country if country!='NO_PROJECT_OWNER' else None,
               'appropriation_required':True,'had_project':any(p.sponsor==sponsor for p in campaign.project_states.values())})
    starts=[x for y in report['per_year'] for x in (y['dominant_started'] or [])]
    committed=sum((D(x['total_capital_commitment']) for x in starts),D(0))
    returned=D(report['money_returned'])
    refilled=sum((D(x['amount']) for x in campaign.refill_rows),D(0))
    # The actual final balances determine budget exhaustion, not the count of
    # unsuccessful proposals accumulated over 201 years.
    final_balances={sponsor:str(campaign._last_kernel.state.accounts['route1:budget:'+sponsor].balance)
                    for sponsor in campaign.requesters} if hasattr(campaign,'_last_kernel') else None
    row={'case':case['name'],'refill_share':case['refill_share'],'price_multiplier':case['price_multiplier'],
       'projects_started':report['projects_started'],'sponsors_ever_started':report['distinct_started_sponsors'],
       'bodies_ever_started':report['distinct_started_bodies'],
       'last_start_year':max((x['year'] for x in starts),default=None),
       'total_committed':str(committed),'total_returned':str(returned),
       'total_refilled':str(refilled),
       'sponsors_out_of_budget':report.get('sponsors_out_of_budget_final'),
       'refill_transactions':len(campaign.refill_rows),
       'scenario_sha256':report['scenario_sha256']}
    # Budget exhaustion from final annual rollup (reported by existing campaign).
    row['sponsors_out_of_budget']=len(report['per_year'][-1].get('sponsors_exhausted',[]))
    rows.append(row)
    print(json.dumps(row,sort_keys=True),flush=True)

AFTER=hashlib.sha256(DB.read_bytes()).hexdigest();assert BEFORE==AFTER
s.write('sponsor_owner_routing.json',sponsor_report)
s.write('summary.json',{'classification':'TEST_ONLY_NONCANON','identity':identity,
  'cases':rows,'sponsors':sponsor_report,'route1_hash':route1,'route1_pass':True,
  'ceres_equivalence':parity,'selector_firewall':firewall,
  'db_sha256_before':BEFORE,'db_sha256_after':AFTER})
print('COMPLETE 1/1; DB unchanged; controls pass',flush=True)
