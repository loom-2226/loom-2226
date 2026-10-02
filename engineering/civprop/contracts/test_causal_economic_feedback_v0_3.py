import unittest
from .causal_economic_feedback_v0_3 import *
class CausalEconomicFeedback(unittest.TestCase):
 def c(self,r=10,a=6): return observe_constraint(year=2030,location_id='LUNA_SURFACE',channel_id='POWER',required=r,available=a,provenance_refs=('PHYSICAL_STATE',))
 def test_shortage_is_physical_balance(self):
  c=self.c(); self.assertEqual((c.unmet,c.service_ratio,c.status),(4,0.6,'RESOLVED_PHYSICAL_BALANCE'))
 def test_surplus_does_not_become_negative_shortage(self): self.assertEqual(self.c(r=5,a=8).unmet,0)
 def test_unknown_capacity_stays_unknown(self): self.assertEqual(self.c(a=None).status,'UNKNOWN')
 def test_pressure_has_memory(self):
  p=advance_pressure(constraint=self.c(),previous_pressure=2,decay=.5,gain=1); self.assertEqual(p.pressure,5)
 def test_unknown_prior_pressure_stays_unknown(self): self.assertEqual(advance_pressure(constraint=self.c(),previous_pressure=None,decay=.5,gain=1).status,'UNKNOWN')
 def test_pressure_can_create_opportunity(self):
  p=advance_pressure(constraint=self.c(),previous_pressure=0,decay=.5,gain=1); self.assertEqual(opportunity_from_pressure(pressure=p,threshold=3).status,'ELIGIBLE')
 def test_below_threshold_blocks(self):
  p=advance_pressure(constraint=self.c(r=10,a=9),previous_pressure=0,decay=.5,gain=1); self.assertEqual(opportunity_from_pressure(pressure=p,threshold=3).status,'BLOCKED')
 def test_unknown_threshold_blocks(self):
  p=advance_pressure(constraint=self.c(),previous_pressure=0,decay=.5,gain=1); self.assertEqual(opportunity_from_pressure(pressure=p,threshold=None).status,'BLOCKED')
 def test_opportunity_does_not_create_actor_budget(self):
  p=advance_pressure(constraint=self.c(),previous_pressure=0,decay=.5,gain=1); o=opportunity_from_pressure(pressure=p,threshold=3); self.assertIsNone(assert_no_budget_inference(opportunity=o))
if __name__=='__main__': unittest.main()
