"""Nine authored price/life sensitivities. New files only; parent sources unchanged."""
import hashlib
import inspect
import json
import textwrap
from decimal import Decimal as D
from pathlib import Path
from simulation.offworld_mvp.build8.three_arm_stage1.buyer_budget_sweep_kt_20261022 import run_sweep as s

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / 'scenario.json'
AUTHORED = json.loads(CONFIG_PATH.read_text())
SOURCE = json.loads((HERE.parent / 'buyer_budget_sweep_kt_20261022' / 'high_report.json').read_text())['scenario']
EXPECTED_DB = 'e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde'
EXPECTED_ROUTE1 = '4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430'

# The prior campaign explicitly sells at operation years 1 and 2 despite
# four operating events. Replace only that dispatch in memory, never on disk.
core_campaign = s.m.PortfolioCampaign.__mro__[1]
core_globals = __import__(core_campaign.__module__, fromlist=["PortfolioCampaign"]).__dict__
original = inspect.getsource(core_campaign.on_year)
needle = "if year in (p.offset_year('operation_year_1'),p.offset_year('operation_year_2')):"
assert original.count(needle) == 1
assert original.count('super().on_year(year,k,rows)') == 1
patched = textwrap.dedent(original).replace(needle,
    "if year in tuple(p.offset_year('operation_year_'+str(i)) for i in range(1,self.sale_cap+1)):")
patched = patched.replace('super().on_year(year,k,rows)', 'AllBodyCampaign.on_year(self,year,k,rows)')
namespace = {}
exec(compile(patched, '<in-memory-sale-cap>', 'exec'), core_globals, namespace)
core_campaign.on_year = namespace['on_year']
assert 'sale_cap' in patched

# The source's family assignment is intentionally uniform VOLATILES.
# All four family prices are scaled, but only VOLATILES can be exercised.
s.HERE = HERE
s.SCENARIO_PATH = CONFIG_PATH
s.CONFIG = AUTHORED
s.m.HERE = HERE
s.m.OUT = HERE
s.base.OUT = HERE
s.m.write = s.write

original_case_scenario = s.case_scenario
def authored_case_scenario(payload, case):
    result = original_case_scenario(payload, case)
    result['price_life_sweep'] = {
        'price_multiplier':case['price_multiplier'],
        'sale_cap':case['sale_cap'],
        'operating_events_available':4,
        'authored_scenario_sha256':hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest(),
        'classification':'TEST_ONLY_NONCANON',
    }
    for name, family in AUTHORED['material_families'].items():
        result['material_families'][name] = dict(family)
        result['material_families'][name]['unit_sale_price'] = str(
            D(family['unit_sale_price']) * D(case['price_multiplier']))
    return result
s.case_scenario = authored_case_scenario

# run_case reads parent.OUT/scenario.json for its portfolio scenario.
# Give it the same new authored family table without touching parent files.
parent_scenario = json.loads((HERE.parent/'multi_project_final_kt_20261022'/'scenario.json').read_text())
parent_scenario['material_families'] = AUTHORED['material_families']
(HERE/'scenario_portfolio.json').write_text(json.dumps(parent_scenario,sort_keys=True,indent=2)+'\n')
class ParentOutput:
    def __truediv__(self, name):
        if name == 'scenario.json':
            return HERE/'scenario_portfolio.json'
        return HERE/name
s.parent.OUT = ParentOutput()

scenario, scenario_bytes, price_bytes, prices, audit = s.m.load_inputs()
s.m._total_money = s._conservation_total
s.base.boundary._total_money = s._conservation_total
actual_db = hashlib.sha256(Path('data/LOOM_2226.sqlite3').read_bytes()).hexdigest()
assert actual_db == EXPECTED_DB, actual_db
assert AUTHORED['clock'] == {'start_year':2026,'end_year':2226}
assert AUTHORED['coverage'] == {'bodies':90,'sponsors':20}
assert AUTHORED['sales_caps'] == [2,3,4]
assert AUTHORED['price_multipliers'] == ['1','3','10']
assert SOURCE['full_clock']['body_count'] == 90
assert SOURCE['full_clock']['sponsor_count'] == 20
assert SOURCE['project']['schedule_offsets']['operation_year_4'] == 18
assert D(AUTHORED['material_families']['VOLATILES']['recoverable']) / D(AUTHORED['material_families']['VOLATILES']['quantity_per_operation']) == 4

cases = []
for mult in AUTHORED['price_multipliers']:
    for cap in AUTHORED['sales_caps']:
        cases.append({'name':f'price_x{mult}_sales_{cap}', 'mission_type':'rendezvous',
                      'conversion':True, 'annual_inflow':'1000',
                      'price_multiplier':mult, 'sale_cap':cap})
identity = {'authored_scenario_sha256':hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest(),
            'world_db_sha256':actual_db,'base_scenario_sha256':hashlib.sha256(scenario_bytes).hexdigest(),
            'price_table_sha256':hashlib.sha256(price_bytes).hexdigest(), 'cases':cases,
            'sale_cap_provenance':AUTHORED['cap_provenance']}
identity['sweep_identity_sha256'] = hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest()
s.write('input_identity.json',identity)

results=[]
for case in cases:
    s.FundedCampaign.sale_cap = case['sale_cap']
    report = s.run_case(case, scenario, scenario_bytes, price_bytes, prices, audit)
    starts = [x for y in report['per_year'] for x in (y['dominant_started'] or [])]
    committed = sum((D(x['total_capital_commitment']) for x in starts),D(0))
    returned = D(report['money_returned'])
    row = {'case':case['name'], 'price_multiplier':case['price_multiplier'], 'sale_cap':case['sale_cap'],
           'projects_started':report['projects_started'],
           'sponsors_ever_started':report['distinct_started_sponsors'],
           'bodies_ever_started':report['distinct_started_bodies'],
           'last_start_year':max((x['year'] for x in starts),default=None),
           'total_committed':str(committed),'total_returned':str(returned),
           'returned_over_committed':str(returned/committed) if committed else None,
           'sponsor_capital_deferrals':sum(x['sponsor_budget_no_affordable_candidate'] + x['sponsor_capital_blocked'] for x in report['annual_diagnostics']),
           'scenario_sha256':report['scenario_sha256']}
    results.append(row)
    print(json.dumps(row,sort_keys=True),flush=True)

# These are validation checks, not additional simulation sweeps.
firewall = s.base.tripwire_check()
parity = s.m.ceres_equivalence(scenario,prices)
from simulation.offworld_mvp.build8.route1_all_body_campaign_pr3b import AllBodyCampaign
from simulation.offworld_mvp.build8.three_arm_stage1.RENDEZVOUS_V2_PAIRED_REPLAY_TEST_ONLY import replay
route1 = replay(AllBodyCampaign(body_count=90,ceilings_enabled=True))
assert route1 == EXPECTED_ROUTE1, f'Route 1 control mismatch: {route1}'
assert firewall['deliberate_hidden_field'] == 'REJECTED',firewall
s.write('summary.json',{'classification':'TEST_ONLY_NONCANON','input_identity':identity,
                        'cases':results,'route1_control_hash':route1,
                        'route1_control_pass':True,'ceres_equivalence':parity,
                        'selection_firewall':firewall,
                        'organics_note':AUTHORED['organics_placeholder_origin']})
print('SWEEP COMPLETE: 9 cases, controls passed',flush=True)
