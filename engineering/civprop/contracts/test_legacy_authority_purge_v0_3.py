import tempfile, unittest
from pathlib import Path
from engineering.civprop.solar_bundle_v0_3 import build_bundle_dir
from engineering.civprop.method_lab.contracts import load_bundle
from engineering.civprop.contracts.legacy_authority_purge_v0_3 import purge_legacy_authority
from engineering.civprop.method_lab.prototypes.common import actor_tech_status

class LegacyAuthorityPurgeV03Test(unittest.TestCase):
 def bundle(self):
  td=tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup)
  return load_bundle(build_bundle_dir(Path(td.name)))

 def test_future_frontier_and_parallel_capability_are_quarantined(self):
  p=purge_legacy_authority(self.bundle()).bundle
  self.assertEqual(p.scenario.technology_frontier,())
  self.assertEqual(p.scenario.actor_capability,())
  self.assertEqual(actor_tech_status(p,'CNSA','LUNAR_SURFACE_OPERATIONS',2028),'UNKNOWN')

 def test_machinery_actor_budget_events_capability_access_and_behavior_are_quarantined(self):
  p=purge_legacy_authority(self.bundle()).bundle
  self.assertEqual(p.scenario.actor_state_v1.events,())
  for a in p.scenario.actor_state_v1.actors:
   self.assertEqual(a.budget.spendable_allocation.status,'UNKNOWN')
   self.assertIsNone(a.budget.spendable_allocation.amount)
   self.assertEqual(a.installed_capability.status,'UNKNOWN')
   self.assertEqual(a.provider_service_access.status,'UNKNOWN')
   self.assertEqual(a.experience.status,'UNKNOWN')

 def test_generic_and_placeholder_services_removed_but_qualified_evidence_survives(self):
  p=purge_legacy_authority(self.bundle()).bundle
  refs=[r for x in p.scenario.accessibility_v1.service_paths for r in x.provenance_refs]
  self.assertFalse(any('MACHINERY_TEST' in r or 'EXPLICIT_PLACEHOLDER:GAP-016' in r for r in refs))
  self.assertTrue(any('SERVICE_EVIDENCE:' in r for r in refs))

 def test_scenario_lunar_prior_and_bootstrap_demand_are_quarantined(self):
  p=purge_legacy_authority(self.bundle()).bundle
  self.assertEqual(p.scenario.demand_pressure_v1.strategic_requirements,())
  self.assertFalse(any(q.question_id=='MOON_POLAR_WATER_PRESENT' for q in p.scenario.mission_knowledge_v1.questions))
  self.assertFalse(any(m.mission_archetype_id=='LUNAR_RESOURCE_PROSPECTING_SURVEY' for m in p.scenario.mission_knowledge_v1.missions))

 def test_promoted_demographic_authority_is_retained(self):
  b=self.bundle(); p=purge_legacy_authority(b)
  self.assertIs(p.bundle.scenario.demographic_authority_v1,b.scenario.demographic_authority_v1)
  self.assertTrue(any(x.authority_surface=='demographic_authority_v1' and x.action=='RETAIN' for x in p.inventory))

if __name__=='__main__': unittest.main()
