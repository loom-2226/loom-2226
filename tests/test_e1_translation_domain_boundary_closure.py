import unittest

from engineering.experience_one.qualification.e1_translation_domain_boundary_closure import (
    qualify_translation_domain_boundary_closure,
)


class E1TranslationDomainBoundaryClosureTests(unittest.TestCase):
    def test_current_evidence_fails_closed_without_inventing_geometry(self):
        r = qualify_translation_domain_boundary_closure()
        self.assertEqual(r["answer"], "NO")
        self.assertEqual(r["disposition"], "INDETERMINATE_NOT_CERTIFIABLE")
        self.assertFalse(r["authority"]["certifies_boundary_geometry"])
        self.assertTrue(r["missing_required_evidence"])

    def test_scalar_area_cannot_be_promoted_to_shape(self):
        r = qualify_translation_domain_boundary_closure()
        self.assertIn("SCALAR_BOUNDARY_AREA_WITH_ASSUMED_SHAPE", r["rejected_substitutions"])
        self.assertIn("No shape may be inferred", r["anchor_semantics_warning"])

    def test_foundational_ontology_is_not_required_by_interface(self):
        r = qualify_translation_domain_boundary_closure()
        p = r["ontology_policy"]
        self.assertFalse(p["tick_tock_required"])
        self.assertFalse(p["cell_complex_required"])
        self.assertFalse(p["fundamental_weave_metric_required"])
        self.assertTrue(p["navigator_depends_on_observable_contract_not_ontology"])

    def test_no_authority_is_accidentally_created(self):
        a = qualify_translation_domain_boundary_closure()["authority"]
        self.assertEqual(a["runtime_policy_mutation"], "ZERO")
        self.assertEqual(a["campaign_state_mutation"], "ZERO")
        self.assertEqual(a["llm_calculation_authority"], "ZERO")
        self.assertEqual(a["canon_mutation"], "ZERO")


if __name__ == "__main__":
    unittest.main()
