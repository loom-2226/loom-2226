import unittest

from engineering.experience_one.qualification.e1_domain_membership_derivation import (
    build_e1_domain_membership_derivation,
)


class DomainMembershipDerivationTests(unittest.TestCase):
    def test_current_configuration_requires_certified_domain_solution(self):
        result = build_e1_domain_membership_derivation()
        self.assertEqual(result["configuration_identity"], "WAYFARER_REFERENCE_SCHEMATIC_V2_4A")
        self.assertEqual(result["runtime_state"]["launch_attachment_state"], "DOCKED")
        self.assertEqual(result["runtime_state"]["external_attachment_state"], "FREE")
        self.assertEqual(result["runtime_state"]["deployable_structure_state"], "STOWED")
        self.assertEqual(result["derived_state"]["domain_membership_state"], "UNKNOWN")
        self.assertEqual(
            result["disposition"],
            "DOMAIN_MEMBERSHIP_REQUIRES_CERTIFIED_DOMAIN_SOLUTION",
        )
        self.assertEqual(
            result["missing_required_evidence"],
            ["translation_domain_geometry_or_certification_envelope"],
        )

    def test_packaging_does_not_auto_certify_membership(self):
        result = build_e1_domain_membership_derivation()
        self.assertTrue(result["configuration_evidence"]["docked_launch_is_committed_configuration_component"])
        self.assertTrue(result["configuration_evidence"]["external_attachment_set_is_empty"])
        self.assertTrue(result["configuration_evidence"]["deployable_topology_is_stowed"])
        self.assertFalse(result["policy"]["structural_integration_implies_domain_membership"])
        self.assertFalse(result["policy"]["mass_state_inclusion_implies_domain_membership"])
        self.assertFalse(result["policy"]["node_count_implies_domain_membership"])
        self.assertFalse(result["authority"]["certifies_domain_membership"])
        self.assertFalse(result["authority"]["certifies_domain_geometry"])
        self.assertFalse(result["authority"]["certifies_domain_size"])


if __name__ == "__main__":
    unittest.main()
