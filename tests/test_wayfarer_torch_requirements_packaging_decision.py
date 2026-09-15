import unittest
from src.wayfarer_torch_requirements_packaging_decision import build_review

class TorchRequirementsPackagingDecisionTests(unittest.TestCase):
    def test_no_silent_requirement_reduction(self):
        r=build_review()
        self.assertFalse(r["decision"]["reduce_performance_cards"])
        self.assertFalse(r["decision"]["increase_propulsion_mass_allocation"])
        self.assertFalse(r["decision"]["select_source_architecture"])

    def test_breakthrough_requirement_is_preserved(self):
        r=build_review()
        self.assertEqual(r["decision"]["disposition"],"PRESERVE_CURRENT_VEHICLE_REQUIREMENTS_AND_CARRY_SOURCE_REALIZABILITY_AS_EXPLICIT_TECHNOLOGY_HOLD")
        self.assertEqual(r["component_freeze_readiness"],"NOT_READY")

    def test_packaging_remains_candidate(self):
        r=build_review()
        self.assertEqual(r["packaging"]["status"],"NON_GOVERNING_CANDIDATE_CLEARANCE_ENVELOPE_ONLY")
        self.assertIsNone(r["packaging"]["earned_source_mass_budget_kg"])

    def test_next_step(self):
        self.assertEqual(build_review()["qualified_next_step"],"TORCH_WORKING_FLUID_IDENTITY_AND_FEED_PATH_TRADE")

if __name__=="__main__": unittest.main()
