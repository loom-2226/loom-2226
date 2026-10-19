import copy, unittest
from decimal import Decimal as D
from simulation.offworld_mvp.build8.three_arm_stage1.sponsor_selection import run
from simulation.offworld_mvp.build8.three_arm_stage1.sponsor_ledger_slice import canonical,check_ledger
from simulation.offworld_mvp.build8.three_arm_stage1.outcome_resolver import resolve
import json
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/'SPONSOR_SELECTION_SCENARIO.json'
def scenario(): return json.loads(PATH.read_text())
class SelectionTests(unittest.TestCase):
 def test_replays_and_ranking(self):
  a=run();self.assertEqual(canonical(a),canonical(run()))
  s,t=a['sponsors'];self.assertEqual((s['selected_candidate_id'],t['selected_candidate_id']),('amun','bennu'))
  for x in (s,t):
   self.assertEqual(x['success_chance_test_only'],'0.9')
   rows={r['candidate_id']:r for r in x['candidates']}
   self.assertEqual(rows['expensive']['exclusion_reason'],'UNAFFORDABLE')
   self.assertEqual(rows['infeasible']['exclusion_reason'],'INFEASIBLE')
   self.assertEqual(rows['missing']['exclusion_reason'],'MISSING')
   self.assertEqual(rows['unpriced']['exclusion_reason'],'INFEASIBLE')
   self.assertEqual(D(x['ledger']['spent_usd']),D(rows[x['selected_candidate_id']]['quote_usd']))
   check_ledger(*(D(x['ledger'][k]) for k in ('initial_budget_usd','spent_usd','balance_usd')))
   self.assertGreater(D(rows[x['selected_candidate_id']]['expected_surplus_test_only_usd']),D(rows['bennu' if x is s else 'amun']['expected_surplus_test_only_usd']))
 def test_tie_order_and_threshold(self):
  a=scenario();a['sponsors']=[a['sponsors'][0]]
  a['sponsors'][0]['values']['bennu']=['600000000','0']
  # Make expected surplus exactly equal using the pinned price difference.
  baseline=run(scenario_override=a)['sponsors'][0]
  rows={r['candidate_id']:r for r in baseline['candidates']}
  delta=D(rows['bennu']['expected_surplus_test_only_usd'])-D(rows['amun']['expected_surplus_test_only_usd'])
  a['sponsors'][0]['values']['bennu'][0]=str(D(a['sponsors'][0]['values']['bennu'][0])-delta/D('0.9'))
  first=run(scenario_override=a)['sponsors'][0]
  self.assertEqual(D(next(r for r in first['candidates'] if r['candidate_id']=='amun')['expected_surplus_test_only_usd']),D(next(r for r in first['candidates'] if r['candidate_id']=='bennu')['expected_surplus_test_only_usd']))
  self.assertEqual(first['selected_candidate_id'],'bennu')
  a['candidates'].reverse()
  self.assertEqual(run(scenario_override=a)['sponsors'][0]['selected_candidate_id'],'bennu')
  threshold=next(r for r in first['candidates'] if r['candidate_id']=='bennu')['expected_surplus_test_only_usd']
  a['minimum_surplus_usd']=threshold
  self.assertEqual(run(scenario_override=a)['sponsors'][0]['decision'],'ACCEPT')
  a['minimum_surplus_usd']=str(D(threshold)+1)
  self.assertEqual(run(scenario_override=a)['sponsors'][0]['decision'],'REJECT')
  a['sponsors'][0]['defer']=True
  self.assertEqual(run(scenario_override=a)['sponsors'][0]['decision'],'DEFER')
 def test_isolation_failure_and_identity(self):
  a=scenario();baseline=run(scenario_override=a)
  a['sponsors'][0]['values']['amun'][0]='610000000'
  changed=run(scenario_override=a)
  self.assertNotEqual(baseline['run_identity'],changed['run_identity'])
  self.assertEqual(baseline['sponsors'][0]['ledger'],changed['sponsors'][0]['ledger'])
  x=baseline['sponsors'][0]['ledger']
  with self.assertRaisesRegex(AssertionError,'LEDGER_CONSERVATION_FAILED'):
   check_ledger(D(x['initial_budget_usd']),D(x['spent_usd']),D(x['balance_usd'])+1)
  for key,value in [('minimum_surplus_usd','10'),('tie_break','INVALID'),('quote_run_identity','invalid'),('executor_cast_id','INVALID')]:
   b=scenario();b[key]=value
   try: other=run(scenario_override=b)
   except (ValueError,StopIteration,KeyError):continue
   self.assertNotEqual(baseline['run_identity'],other['run_identity'])
  for outcome,seed in [('DELIVERED','stage1-seed'),('FAILED','stage1-failure-6')]:
   b=scenario();b['sponsors']=[b['sponsors'][0]]
   # Find a seed for the actual sponsor/candidate resolver ID.
   if outcome=='FAILED':
    seed=next('selection-fail-'+str(i) for i in range(100) if resolve('selection-fail-'+str(i),D('0.9'),'science|amun')['outcome']=='FAILED')
   b['outcome_seed']=seed
   r=run(scenario_override=b)['sponsors'][0]
   self.assertEqual(r['outcome']['outcome'],outcome)
   self.assertEqual(D(r['ledger']['spent_usd']),D(r['ledger']['selected_quote_usd']))
  b=scenario();b['candidates']=b['candidates'][:1]
  self.assertNotEqual(baseline['run_identity'],run(scenario_override=b)['run_identity'])
  b=scenario();b['sponsors'][0]['initial_budget_usd']='1'
  self.assertEqual(run(scenario_override=b)['sponsors'][0]['ledger']['spent_usd'],'0')
if __name__=='__main__':unittest.main()
