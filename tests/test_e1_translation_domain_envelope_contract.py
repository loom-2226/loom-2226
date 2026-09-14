import unittest

from engineering.experience_one.qualification.e1_translation_domain_envelope_contract import (
    qualify_e1_translation_domain_envelope_contract,
)


class TranslationDomainEnvelopeContractTests(unittest.TestCase):
    def setUp(self):
        self.result = qualify_e1_translation_domain_envelope_contract()

    def test_domain_is_configuration_bound_not_body_centered(self):
        self.assertEqual(
            self.result["binding_rule"],
            "CERTIFIED_TRANSLATION_DOMAIN_IS_VESSEL_CONFIGURATION_BOUND_NOT_CELESTIAL_EXCLUSION_RADIUS",
        )
        self.assertFalse(self.result["policy"]["body_centered_radius_substitution_allowed"])
        self.assertFalse(self.result["policy"]["hull_dimension_substitution_allowed"])
        self.assertFalse(self.result["policy"]["node_count_substitution_allowed"])

    def test_membership_requires_certified_boundary_containment(self):
        membership = self.result["membership_contract"]
        self.assertEqual(
            membership["rule"],
            "MEMBER_IFF_COMMITTED_COMPONENT_GEOMETRY_IS_CONTAINED_BY_CERTIFIED_TRANSLATION_DOMAIN_BOUNDARY",
        )
        self.assertFalse(membership["structural_integration_alone_certifies_membership"])
        self.assertFalse(membership["mass_state_inclusion_alone_certifies_membership"])
        self.assertFalse(membership["attachment_state_alone_certifies_membership"])

    def test_current_e1_envelope_instantiation_remains_unresolved(self):
        self.assertEqual(
            self.result["disposition"],
            "ENVELOPE_CONTRACT_QUALIFIED_INSTANTIATION_UNRESOLVED",
        )
        self.assertFalse(self.result["current_e1_instantiation"]["certified_boundary_present"])
        self.assertFalse(self.result["current_e1_instantiation"]["numeric_extent_defined"])
        self.assertIn(
            "certified_translation_domain_boundary_solution",
            self.result["current_e1_instantiation"]["missing_required_evidence"],
        )
        self.assertIn(
            "committed_component_geometry_envelope",
            self.result["current_e1_instantiation"]["missing_required_evidence"],
        )

    def test_open_schematic_detail_is_preserved(self):
        current = self.result["current_e1_instantiation"]
        self.assertEqual(current["distributed_boundary_metric_nodes"], 208)
        self.assertEqual(current["exact_node_placement"], "OPEN")
        self.assertFalse(current["exact_node_placement_promoted_to_known"])
        self.assertFalse(self.result["authority"]["certifies_domain_membership"])
        self.assertFalse(self.result["authority"]["certifies_domain_size"])
        self.assertFalse(self.result["authority"]["certifies_overall_ga"])


if __name__ == "__main__":
    unittest.main()
