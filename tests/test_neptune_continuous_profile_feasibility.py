import unittest

from engineering.experience_one.qualification.e1_neptune_continuous_profile_feasibility import build_report


class NeptuneContinuousProfileFeasibilityTests(unittest.TestCase):
    def test_current_sources_do_not_earn_continuous_profile(self):
        report = build_report()
        self.assertEqual(report["status"], "PASS")
        self.assertFalse(report["continuous_profile_earned"])
        self.assertEqual(report["continuous_profile_authority"], "ZERO")
        self.assertEqual(report["digitization_authority"], "ZERO")
        self.assertEqual(report["interpolation_authority"], "ZERO")
        self.assertEqual(report["extrapolation_authority"], "ZERO")

    def test_published_profile_claim_is_separated_from_archived_tabular_data(self):
        report = build_report()
        self.assertTrue(report["published_vertical_profile_exists"])
        self.assertFalse(report["neptune_reduced_tabular_profile_found"])
        self.assertIn("LINDAL_1992_AJ_NEPTUNE_OCCULTATION", report["source_ids"])
        self.assertIn("LINDAL_ET_AL_1990_GRL_NEPTUNE_OCCULTATION", report["source_ids"])

    def test_no_local_2226_or_density_authority_is_created(self):
        report = build_report()
        self.assertFalse(report["local_2226_endpoint_values_earned"])
        self.assertEqual(report["density_authority"], "ZERO")
        self.assertEqual(report["admissibility_authority"], "ZERO")
        self.assertEqual(report["loom_coherence_authority"], "ZERO")


if __name__ == "__main__":
    unittest.main()
