import copy
import unittest
from decimal import Decimal as D
from simulation.offworld_mvp.build8.three_arm_stage1.sponsor_ledger_slice import run,check_ledger,canonical
from simulation.offworld_mvp.build8.three_arm_stage1.outcome_resolver import resolve

class ThinSliceTests(unittest.TestCase):
 def test_three_cases_replay(self):
  first=run(); second=run();self.assertEqual(canonical(first),canonical(second))
  cases={x['case_id']:x for x in first['cases']}
  self.assertEqual(set(cases),{'affordable','unaffordable','infeasible'})
  self.assertEqual(cases['affordable']['decision'],'ACCEPT')
  self.assertIn(cases['affordable']['outcome']['outcome'],('DELIVERED','FAILED'))
  self.assertTrue(cases['affordable']['best_departure_date'])
  self.assertTrue(cases['affordable']['best_flight_days'])
  for name in ('unaffordable','infeasible'):
   self.assertEqual(cases[name]['decision'],'REJECT')
   self.assertEqual(cases[name]['outcome']['outcome'],'NOT_EXECUTED')
   self.assertEqual(D(cases[name]['spent_usd']),D(0))
  self.assertEqual(cases['infeasible']['quote_status'],'INFEASIBLE')
 def test_corruption_fails(self):
  x=run()['cases'][0]
  with self.assertRaisesRegex(AssertionError,'LEDGER_CONSERVATION_FAILED'):
   check_ledger(D(x['initial_budget_usd']),D(x['spent_usd']),D(x['balance_usd'])+D('1'))
 def test_resolver_replay_and_seed(self):
  self.assertEqual(resolve('seed',D('0.9'),'case'),resolve('seed',D('0.9'),'case'))
  self.assertNotEqual(resolve('seed',D('0.9'),'case')['draw'],resolve('other',D('0.9'),'case')['draw'])
if __name__=='__main__':unittest.main()
