import tempfile,unittest,json
from pathlib import Path
from engineering.civprop.solar_bundle_v0_3 import build_bundle_dir
from engineering.civprop.method_lab.contracts import load_bundle
class SolarBundleV03Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.t=tempfile.TemporaryDirectory(); cls.p=build_bundle_dir(Path(cls.t.name))
  cls.s=json.load(open(cls.p/'scenario_v1.json')); cls.c=json.load(open(cls.p/'compiler_manifest_v1.json'))
 def test_bundle_loads_through_promoted_validator(self):
  b=load_bundle(self.p); self.assertEqual((b.scenario.start_year,b.scenario.end_year),(2026,2226))
 def test_full_solar_locations_are_zero_state_candidates(self):
  self.assertGreater(len(self.s['locations']),100)
  ceres=next(x for x in self.s['locations'] if x['location_id']=='CERES_ORBITAL')
  self.assertEqual(ceres['initial_state']['capital'],0); self.assertEqual(ceres['initial_state']['biological_population'],0)
 def test_placeholder_is_explicit_and_spice_absent(self):
  x=self.s['authority_context']['solar_v0_3']['transport_opportunity_surface']
  self.assertEqual(x['value'],1.0); self.assertEqual(x['gap_owner'],'GAP-016')
  self.assertFalse(self.s['authority_context']['solar_v0_3']['spice_consumed'])
 def test_gap14_held(self):
  self.assertEqual(self.c['gap_resolution']['GAP-014'],'OPEN')
  self.assertEqual(self.c['gap_resolution']['GAP-016'],'OPEN_EXPLICIT_PLACEHOLDER')
 def test_mission_never_inserted_as_facility(self):
  self.assertFalse(any(x['project_archetype_id']=='PROSPECTING_SURVEY' for x in self.s['project_archetypes']))
if __name__=='__main__': unittest.main()
