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
assert CONFIG['treasury_return_appropriation_share_levels']==['0','0.5','1']
assert CONFIG['sales_caps']==[4]
assert CONFIG['price_multipliers']==['1','3','10']

# Sale cap from accepted prior sweep, replacing only in-memory dispatch.
core=s.m.PortfolioCampaign.__mro__[1]
core_globals=__import__(core.__module__,fromlist=['PortfolioCampaign']).__dict__
source=inspect.getsource(core.on_year)
needle="if year in (p.offset_year('operation_year_1'),p.offset_year('operation_year_2')):"
assert source.count(needle)==1
patched=textwrap.dedent(source).replace(needle,"if year in tuple(p.offset_year('operation_year_'+str(i)) for i in range(1,self.sale_cap+1)):")
patched=patched.replace('super().on_year(year,k,rows)','AllBodyCampaign.on_year(self,year,k,rows)')
ns={};exec(compile(patched,'<sale-cap-4-in-memory>','exec'),core_globals,ns)
core.on_year=ns['on_year']

instances=[]
class RefillCampaign(s.FundedCampaign):
    sale_cap=4
    def __init__(self,*args,refill_share,**kwargs):
        self.refill_share=D(refill_share)
        self.refill_rows=[]
        self.processed_receipts=set()
        super().__init__(*args,**kwargs)
        instances.append(self)
    def _definition(self,*args):
        definition=super()._definition(*args)
        # Suppress old fixed two-receipt appropriations; each eligible receipt
        # instead authors its own exact amount at decision time.
        definition['appropriations']=[]
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
                try:self.lifecycles[key]._appropriate(k,year)
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
s.base.boundary._total_money=s._conservation_total
s.parent.OUT=PREVIOUS
base_scenario,scenario_bytes,price_bytes,prices,audit=s.m.load_inputs()
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
print('COMPLETE 9/9; DB unchanged; controls pass',flush=True)
