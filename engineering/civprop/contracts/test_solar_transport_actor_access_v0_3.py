import unittest
from engineering.civprop.contracts.solar_transport_opportunity_v0_3 import TransferOpportunity
from engineering.civprop.contracts.solar_transport_actor_access_v0_3 import assess_actor_transport
def opp(year=2035):
 return TransferOpportunity("EARTH","MARS",f"{year}-06-01T00:00:00Z",f"{year}-12-01T00:00:00Z",183,3.2,2.8,10.24,6.0,
 "LAMBERT_UNIVERSAL_ZERO_REV_PROGRADE","TEST","GEOMETRY_OPPORTUNITY_ONLY",("SPICE_TEST",))
TL={"TRN-MOD-NEP":{"frontier_year":2050},"SPEC-MOD-TORCH":{"frontier_year":2120},"SPEC-MOD-METRIC-SHIP":{"frontier_year":2205}}
BASE={"ORBITAL_LAUNCH":"ACCESS","SPACECRAFT_OPS":"OPERATIONAL","DEEP_SPACE":"OPERATIONAL"}
class ActorTransportV03Tests(unittest.TestCase):
 def test_chemical_screenable_when_actor_has_baseline_capabilities(self):
  x=assess_actor_transport(opp(),"CHEMICAL_IMPULSIVE","NASA",BASE,TL)
  self.assertEqual(x.status,"SCREENABLE_GEOMETRY_AND_ACTOR_ACCESS")
 def test_nep_before_anchor_is_infeasible_even_if_actor_claimed_capable(self):
  c=BASE|{"NUCLEAR_ELECTRIC_SPACECRAFT":"OPERATIONAL"}
  x=assess_actor_transport(opp(2049),"NUCLEAR_ELECTRIC","X",c,TL)
  self.assertEqual(x.status,"INFEASIBLE"); self.assertIn("TECHNOLOGY_BEFORE_CONSIDERATION_ANCHOR",x.limiting_constraints)
 def test_nep_anchor_does_not_unlock_actor_or_solver(self):
  x=assess_actor_transport(opp(2050),"NUCLEAR_ELECTRIC","NASA",BASE,TL)
  self.assertEqual(x.status,"UNKNOWN")
  self.assertEqual(x.technology_frontier_status,"CONSIDERATION_ANCHOR_REACHED_NOT_ACHIEVEMENT")
  self.assertIn("ACTOR_CAPABILITY_UNKNOWN",x.limiting_constraints)
  self.assertIn("PROPULSION_PERFORMANCE_SOLVER_NOT_IMPLEMENTED",x.limiting_constraints)
 def test_development_is_not_usable(self):
  c=BASE|{"DEEP_SPACE":"DEVELOPMENT"}
  x=assess_actor_transport(opp(),"CHEMICAL_IMPULSIVE","X",c,TL)
  self.assertEqual(x.status,"UNKNOWN"); self.assertEqual(x.actor_capability_status,"CONDITIONAL")
 def test_speculative_regime_stays_solver_gated_after_anchor(self):
  c=BASE|{"FUSION_TORCH_SPACECRAFT":"OPERATIONAL"}
  x=assess_actor_transport(opp(2121),"FUSION_TORCH","X",c,TL)
  self.assertEqual(x.status,"UNKNOWN"); self.assertIn("PROPULSION_PERFORMANCE_SOLVER_NOT_IMPLEMENTED",x.limiting_constraints)
if __name__=="__main__": unittest.main()
