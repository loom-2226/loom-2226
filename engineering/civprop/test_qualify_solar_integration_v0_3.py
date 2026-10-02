import unittest
from engineering.civprop.qualify_solar_integration_v0_3 import qualify
class SolarIntegrationQualificationV03Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.q=qualify()
 def test_hostile_checks_all_pass(self): self.assertTrue(all(self.q["checks"].values()))
 def test_verdict_is_pass_with_blockers(self): self.assertEqual(self.q["verdict"],"PASS_WITH_BLOCKERS")
 def test_not_falsely_ready_for_full_hybrid_run(self): self.assertFalse(self.q["ready_now"]["full_hybrid_solar_run"])
 def test_gap14_untouched(self): self.assertTrue(self.q["checks"]["GAP014_STILL_OPEN"])
 def test_blockers_are_explicit(self): self.assertGreaterEqual(len(self.q["blockers_before_full_solar_reference_run"]),4)
if __name__=="__main__": unittest.main()
