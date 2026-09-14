import unittest

from src.loom_neptune_plasma_em_source_qualification import qualification_report


class NeptunePlasmaEmSourceQualificationTests(unittest.TestCase):
    def test_historic_machine_readable_sources_are_distinguished_from_2226_state(self):
        report = qualification_report()
        self.assertTrue(report["historic_machine_readable_sources_found"])
        self.assertFalse(report["local_2226_endpoint_values_earned"])
        self.assertEqual(report["endpoint_authority"], "ZERO")

    def test_core_source_families_are_present(self):
        report = qualification_report()
        families = set(report["source_families"])
        self.assertIn("VOYAGER2_PLS_NEPTUNE", families)
        self.assertIn("VOYAGER2_MAG_NEPTUNE", families)
        self.assertIn("VOYAGER2_PWS_NEPTUNE", families)
        self.assertIn("VOYAGER2_LECP_NEPTUNE", families)

    def test_no_policy_or_loom_authority_leaks(self):
        report = qualification_report()
        self.assertEqual(report["admissibility_authority"], "ZERO")
        self.assertEqual(report["loom_coherence_authority"], "ZERO")
        self.assertEqual(report["runtime_policy_authority"], "ZERO")


if __name__ == "__main__":
    unittest.main()
