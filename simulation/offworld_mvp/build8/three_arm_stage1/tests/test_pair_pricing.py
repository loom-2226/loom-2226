import copy,json,unittest
from pathlib import Path
from simulation.offworld_mvp.build8.three_arm_stage1 import pair_pricing as p
E=json.loads((Path(__file__).resolve().parents[1]/'experiment.json').read_text())
class PairPricingTest(unittest.TestCase):
 def test_identity_sensitive_to_limits_terms_pairs(self):
  original=p.identity(E,'manifest','config')
  for change in ('departure_limit_km_s','arrival_limit_km_s'):
   d=copy.deepcopy(E);d['vehicle_classes'][0][change]='9';self.assertNotEqual(original,p.identity(d,'manifest','config'))
  d=copy.deepcopy(E);d['mission_types'][1]['charged_speed_terms'].append('arrival_vinf_km_s');self.assertNotEqual(original,p.identity(d,'manifest','config'))
  d=copy.deepcopy(E);d['selected_mission_types']=['rendezvous'];self.assertNotEqual(original,p.identity(d,'manifest','config'))
 def test_pair_evaluation(self):
  v,m=p.pairs(E)[0];fly=p.pairs(E)[1][1]
  g={'trajectories':[{'departure_vinf_km_s':6.1,'arrival_vinf_km_s':12,'flight_days':100}]}
  self.assertEqual(p.evaluate(g,v,m,E)['status'],'INFEASIBLE')
  q=p.evaluate(g,v,fly,E);self.assertEqual(q['status'],'PRICED_TEST_ONLY');self.assertEqual(q['price'],str(__import__('decimal').Decimal(E['price_rate_usd_millions_per_km_s'])*__import__('decimal').Decimal('6.1')))
if __name__=='__main__':unittest.main()
