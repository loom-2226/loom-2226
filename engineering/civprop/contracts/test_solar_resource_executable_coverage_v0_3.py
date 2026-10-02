from pathlib import Path
import unittest
from .solar_resource_executable_coverage_v0_3 import audit
ROOT=Path(__file__).resolve().parents[3]
class TestSolarResourceExecutableCoverageV03(unittest.TestCase):
 def setUp(self):
  self.x=audit(ROOT/'dev/solar_civprop_m4b/reports/M4B_COVERAGE_MATRIX.csv',ROOT/'engineering/civprop/contracts/mission_knowledge_v1.json')
 def test_m4b_counts_preserved(self):
  self.assertEqual((self.x['resource_lanes'],self.x['supported_lanes'],self.x['unknown_after_search_lanes']),(380,37,343))
 def test_moon_not_uniquely_enriched(self):
  self.assertEqual(self.x['moon']['supported_resource_families'],3)
  ids={x['body_id'] for x in self.x['bodies_with_at_least_moon_evidence_coverage']}
  self.assertTrue({'MOON','MARS','BENNU','RYUGU','CERES'}.issubset(ids))
 def test_executable_mission_package_is_lunar_only(self):
  self.assertEqual(self.x['mission_destinations'],['LUNA_SURFACE'])
  self.assertEqual(self.x['mission_knowledge_questions'],1)
if __name__=='__main__': unittest.main()
