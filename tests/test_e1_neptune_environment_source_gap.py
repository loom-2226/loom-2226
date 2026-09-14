import unittest

from engineering.experience_one.qualification.e1_neptune_environment_source_gap import (
    build_source_gap_report,
)


class TestNeptuneEnvironmentSourceGap(unittest.TestCase):
    def test_sourceable_environment_is_not_promoted_to_2226_endpoint_state(self):
        report = build_source_gap_report()

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["body"], "NE")
        self.assertEqual(
            report["classification"],
            "EXTERNAL_RESEARCH_SYNTHESIS_DATA_ACQUISITION_GAP_ONLY",
        )

        families = report["families"]
        self.assertEqual(families["atmospheric_classification"]["disposition"], "SOURCEABLE_ESTABLISHED")
        self.assertEqual(families["local_matter_density"]["disposition"], "SOURCEABLE_BUT_EPOCH_AND_LOCATION_SENSITIVE")
        self.assertEqual(families["electromagnetic_environment"]["disposition"], "SOURCEABLE_BUT_EPOCH_AND_LOCATION_SENSITIVE")
        self.assertEqual(families["physical_uncertainty"]["disposition"], "REQUIRES_EXPLICIT_MODEL_UNCERTAINTY")

        for key in (
            "atmospheric_classification",
            "local_matter_density",
            "electromagnetic_environment",
            "physical_uncertainty",
        ):
            self.assertFalse(families[key]["qualified_for_2226_endpoint"])
            self.assertTrue(families[key]["sources"])

    def test_loom_coherence_remains_external_source_empty_and_unresolved(self):
        report = build_source_gap_report()
        coherence = report["families"]["loom_coherence"]

        self.assertEqual(coherence["disposition"], "UNRESOLVED_LOOM_SPECIFIC_PHYSICS")
        self.assertFalse(coherence["qualified_for_2226_endpoint"])
        self.assertEqual(coherence["sources"], [])
        self.assertIn("NO_EXTERNAL_PLANETARY_SCIENCE_PROXY", coherence["guardrails"])

    def test_report_forbids_compound_admissibility_until_gaps_are_qualified(self):
        report = build_source_gap_report()

        self.assertEqual(report["compound_admissibility_model"], "BLOCKED")
        self.assertEqual(report["metric_policy_adoption"], "BLOCKED")
        self.assertIn("loom_coherence", report["blocking_families"])
        self.assertIn("local_matter_density", report["blocking_families"])
        self.assertIn("electromagnetic_environment", report["blocking_families"])
        self.assertIn("physical_uncertainty", report["blocking_families"])


if __name__ == "__main__":
    unittest.main()
