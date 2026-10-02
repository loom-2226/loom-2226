import json,unittest
from pathlib import Path
from engineering.civprop.contracts.actor_baseline_2026_v0_3 import *
P=Path(__file__).resolve().parents[1]/"candidate_inputs"/"LOOM_GROUP_AGENT_SEED_2026_v0.3.json"
AUTH=[
SectorAuthority2026("BULK_MATERIALS",33860920725402.50,3323835278982.61,80531591768796.60,811089115.88),
SectorAuthority2026("CERTIFICATION_METROLOGY",9803526721410.36,1225364406797.12,18678858129729.70,70560095.56),
SectorAuthority2026("COMPUTE",12868094625981.10,1401189703624.52,23962509184434.00,73462544.11),
SectorAuthority2026("SERVICES",62628086069760.90,9334327591816.65,121349755002995.00,960505037.41),
SectorAuthority2026("SHIPS_AEROSPACE",1466145977833.90,102049089262.84,2219947324377.19,6670083.45),
SectorAuthority2026("TRANSPORT_LOGISTICS",15595302374864.30,1498724762476.51,42542313442868.20,160534957.01)]
class T(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with open(P) as f: cls.seed=json.load(f)
  cls.rows=build_actor_baseline_2026(cls.seed,AUTH); cls.by={x.actor_id:x for x in cls.rows}
 def test_complete_unique(self): self.assertEqual((len(self.rows),len(self.by)),(233,233))
 def test_all_numeric_estimates_have_provenance(self):
  self.assertTrue(all(x.source_refs and x.estimate_method for x in self.rows))
 def test_historical_zero(self):
  for k in ("PRO_PLANETARY_RESOURCES","PRO_DEEP_SPACE_INDUSTRIES"):
   self.assertFalse(self.by[k].functional_2026); self.assertEqual(self.by[k].financial_capacity_estimate,0)
 def test_proposal_not_current(self):
  self.assertFalse(self.by["CERT_LORS101"].functional_2026)
 def test_large_exceeds_small_same_category(self):
  self.assertGreater(self.by["CAR_SPACEX"].financial_capacity_estimate,self.by["CAR_PLD"].financial_capacity_estimate)
 def test_bounds(self):
  for x in self.rows:
   self.assertLessEqual(x.financial_capacity_low,x.financial_capacity_estimate)
   self.assertLessEqual(x.financial_capacity_estimate,x.financial_capacity_high)
 def test_category_estimates_remain_inside_sector_envelope(self):
  bysec={x.sector:x for x in AUTH}
  cats=set(x.category for x in self.rows)
  for cat in cats:
   rows=[x for x in self.rows if x.category==cat and x.functional_2026]
   if not rows: continue
   self.assertLess(sum(x.financial_capacity_estimate for x in rows),bysec[rows[0].economic_sector].investment)
 def test_functional_count_and_statuses(self):
  self.assertEqual(sum(x.functional_2026 for x in self.rows),228)
  self.assertEqual(sum(x.lifecycle_status=="HISTORICAL" for x in self.rows),2)
  self.assertEqual(sum(x.lifecycle_status=="PROPOSAL_OR_PENDING" for x in self.rows),3)
 def test_deterministic(self):
  self.assertEqual(baseline_digest(self.rows),baseline_digest(build_actor_baseline_2026(self.seed,AUTH)))
if __name__=="__main__": unittest.main()
