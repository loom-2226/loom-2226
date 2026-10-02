import tempfile, unittest
from pathlib import Path
from engineering.civprop.solar_bundle_v0_3 import build_bundle_dir
from engineering.civprop.method_lab.contracts import load_bundle
from engineering.civprop.method_lab.causal_world_v0_3 import run_causal_world

class LegacyAuthorityCausalWorldV03Test(unittest.TestCase):
 def test_legacy_fixture_cannot_create_lunar_missions_or_scripted_budget(self):
  with tempfile.TemporaryDirectory() as td:
   b=load_bundle(build_bundle_dir(Path(td)))
   r=run_causal_world(bundle=b,seed=42,start_year=2026,end_year=2060)
  self.assertFalse(any(m.mission_archetype_id=='LUNAR_RESOURCE_PROSPECTING_SURVEY' for m in r.missions))
  self.assertFalse(any(d.mission_archetype_id=='LUNAR_RESOURCE_PROSPECTING_SURVEY' for d in r.mission_decisions))
  surfaces={x.authority_surface:x for x in r.legacy_authority_inventory}
  self.assertEqual(surfaces['actor_future_events'].count,2600)
  self.assertEqual(surfaces['technology_frontier'].action,'QUARANTINE')
  self.assertEqual(surfaces['demographic_authority_v1'].action,'RETAIN')

if __name__=='__main__': unittest.main()
