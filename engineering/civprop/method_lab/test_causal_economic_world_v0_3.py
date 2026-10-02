import unittest
from engineering.civprop.method_lab.test_causal_world_v0_3 import CausalWorldV03Tests
from engineering.civprop.method_lab.causal_world_v0_3 import run_causal_world

class CausalEconomicWorldV03(CausalWorldV03Tests):
 def test_state_driven_economic_constraints_are_visible(self):
  r=run_causal_world(bundle=self.bundle,seed=42,start_year=2026,end_year=2026)
  self.assertTrue(r.economic_constraints)
  self.assertTrue(r.economic_pressures)
  self.assertEqual(len(r.economic_constraints),len(r.economic_pressures))
 def test_production_opportunities_fail_closed_without_threshold_authority(self):
  r=run_causal_world(bundle=self.bundle,seed=42,start_year=2026,end_year=2026)
  self.assertTrue(r.economic_opportunities)
  self.assertTrue(all(x.status=='BLOCKED' for x in r.economic_opportunities))
  self.assertTrue(all('PRESSURE_OR_THRESHOLD_UNKNOWN' in x.reason_codes for x in r.economic_opportunities))
 def test_no_economic_feedback_creates_actor_budget(self):
  before={x.actor_id:x.budget.spendable_allocation for x in self.bundle.scenario.actor_state_v1.actors}
  run_causal_world(bundle=self.bundle,seed=42,start_year=2026,end_year=2026)
  after={x.actor_id:x.budget.spendable_allocation for x in self.bundle.scenario.actor_state_v1.actors}
  self.assertEqual(before,after)
 def test_earth_is_not_silently_added_to_excluded_causal_demand_scope(self):
  r=run_causal_world(bundle=self.bundle,seed=42,start_year=2026,end_year=2026)
  excluded=set(self.bundle.scenario.demand_pressure_v1.excluded_location_ids)
  earth=[x for x in r.economic_constraints if x.location_id=='EARTH_SURFACE']
  self.assertEqual(bool(earth),'EARTH_SURFACE' not in excluded)

if __name__=='__main__': unittest.main()
