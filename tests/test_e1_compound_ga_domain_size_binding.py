import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "engineering" / "experience_one" / "qualification" / "e1_compound_ga_domain_size_binding.py"

spec = importlib.util.spec_from_file_location("e1_compound_ga_domain_size_binding", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CompoundGADomainSizeBindingTests(unittest.TestCase):
    def setUp(self):
        self.result = module.qualify_compound_ga_domain_size_binding()

    def test_domain_size_is_vessel_configuration_bound_not_celestial_exclusion_radius(self):
        self.assertEqual(self.result["status"], "PASS")
        self.assertEqual(
            self.result["binding_rule"],
            "CERTIFIED_TRANSLATION_DOMAIN_IS_VESSEL_CONFIGURATION_BOUND_NOT_CELESTIAL_EXCLUSION_RADIUS",
        )
        self.assertFalse(self.result["body_centered_exclusion_radius_defined"])
        self.assertFalse(self.result["collapse_radius_repurposed_as_domain_size"])

    def test_required_certification_state_matches_current_canon(self):
        required = self.result["required_certification_state"]
        self.assertEqual(
            set(required),
            {
                "domain_membership",
                "attachment_state",
                "mass_state_model",
                "node_topology",
                "hull_lattice_configuration",
            },
        )

    def test_rejected_shortcuts_remain_rejected(self):
        rejected = set(self.result["rejected_domain_size_shortcuts"])
        self.assertTrue(
            {
                "HILL_RADIUS",
                "LAPLACE_SOI",
                "SURFACE_RADIUS_MULTIPLE",
                "CURRENT_COLLAPSE_RADIUS",
                "UNIVERSAL_RAMP_DISPLACEMENT_MULTIPLE",
            }.issubset(rejected)
        )

    def test_numeric_extent_is_explicitly_unresolved_not_zero(self):
        axis = self.result["domain_size_axis"]
        self.assertEqual(axis["status"], "QUALIFIED_BINDING_RULE_NUMERIC_EXTENT_UNRESOLVED")
        self.assertFalse(axis["numeric_extent_defined"])
        self.assertFalse(axis["treated_as_zero"])
        self.assertFalse(axis["hull_dimensions_substituted_for_certified_domain"])
        self.assertIn("certified translation-domain geometry", axis["required_evidence"])

    def test_authority_boundary_and_next_step_are_explicit(self):
        self.assertFalse(self.result["admissibility_threshold_defined"])
        self.assertFalse(self.result["runtime_policy_bound"])
        self.assertEqual(self.result["runtime_policy_mutation"], "ZERO")
        self.assertEqual(self.result["campaign_state_mutation"], "ZERO")
        self.assertEqual(self.result["llm_calculation_authority"], "ZERO")
        self.assertEqual(
            self.result["qualified_next_step"],
            "QUALIFY_LOOM_AND_LATTICE_COHERENCE_MODEL_FORM_WITHOUT_BINDING_RUNTIME_POLICY",
        )


if __name__ == "__main__":
    unittest.main()
