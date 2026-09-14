import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).parents[1] / "engineering" / "experience_one" / "qualification" / "e1_ga_minimum_acceptance_evidence.py"
spec = importlib.util.spec_from_file_location("e1_ga_minimum_acceptance_evidence", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class E1GAMinimumAcceptanceEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.result = module.qualify_e1_ga_minimum_acceptance_evidence()

    def test_passes_as_acceptance_contract_only(self):
        self.assertEqual(self.result["status"], "PASS")
        self.assertEqual(
            self.result["decision"],
            "MINIMUM_E1_GA_ACCEPTANCE_EVIDENCE_CONTRACT_QUALIFIED_TWO_EVIDENCE_PACKAGES_REQUIRED",
        )

    def test_six_axes_remain_separate(self):
        axes = self.result["axis_acceptance_contract"]
        self.assertEqual(
            set(axes),
            {
                "local_geometry",
                "local_stress_energy",
                "causal_structure",
                "domain_size",
                "loom_coherence",
                "lattice_coherence",
            },
        )

    def test_remaining_blockers_reduce_to_two_packages(self):
        packages = self.result["minimum_evidence_packages"]
        self.assertEqual(set(packages), {"endpoint_domain_physical_compatibility", "route_vessel_coherence"})
        self.assertEqual(
            set(packages["endpoint_domain_physical_compatibility"]["supports_axes"]),
            {"local_geometry", "causal_structure", "domain_size"},
        )
        self.assertEqual(
            set(packages["route_vessel_coherence"]["supports_axes"]),
            {"loom_coherence", "lattice_coherence"},
        )

    def test_stress_energy_is_already_satisfied_non_material(self):
        axis = self.result["axis_acceptance_contract"]["local_stress_energy"]
        self.assertEqual(axis["current_state"], "SATISFIED_NON_MATERIAL")
        self.assertFalse(axis["additional_acceptance_evidence_required"])

    def test_packages_cannot_substitute_for_axis_evidence(self):
        policy = self.result["evidence_policy"]
        self.assertFalse(policy["package_level_shortcut_to_admissible_allowed"])
        self.assertFalse(policy["cross_axis_compensation_allowed"])
        self.assertFalse(policy["missing_axis_evidence_treated_as_satisfied"])

    def test_contract_does_not_bind_runtime_or_move_endpoint(self):
        self.assertFalse(self.result["runtime_policy_bound"])
        self.assertFalse(self.result["current_endpoint_certified_by_this_contract"])
        self.assertTrue(self.result["earned_operational_handoff_preserved"])
        self.assertEqual(self.result["runtime_policy_mutation"], "ZERO")
        self.assertEqual(self.result["campaign_state_mutation"], "ZERO")
        self.assertEqual(self.result["llm_calculation_authority"], "ZERO")


if __name__ == "__main__":
    unittest.main()
