import unittest

from engineering.experience_one.qualification import e1_configuration_identity_bundle as bundle


class E1ConfigurationIdentityBundleTests(unittest.TestCase):
    def test_ship_identity_alone_is_not_complete_configuration_identity(self):
        report = bundle.evaluate_configuration({"ship": "WAYFARER_BASELINE"})
        self.assertEqual(report["disposition"], "INDETERMINATE_NOT_CERTIFIABLE")
        self.assertEqual(
            report["missing_required_evidence"],
            ["hull_lattice_configuration", "mass_state_model", "node_topology"],
        )
        self.assertFalse(report["configuration_identity_complete"])

    def test_complete_bundle_can_be_marked_present_without_certifying_domain_membership(self):
        report = bundle.evaluate_configuration({
            "ship": "WAYFARER_BASELINE",
            "mass_state_model": "COMMITTED_MASS_STATE_MODEL",
            "node_topology": "COMMITTED_NODE_TOPOLOGY",
            "hull_lattice_configuration": "COMMITTED_HULL_LATTICE_CONFIGURATION",
        })
        self.assertEqual(report["disposition"], "CONFIGURATION_IDENTITY_PRESENT")
        self.assertEqual(report["missing_required_evidence"], [])
        self.assertTrue(report["configuration_identity_complete"])
        self.assertTrue(report["authority"]["certifies_configuration_identity"])
        self.assertFalse(report["authority"]["certifies_domain_membership_or_attachment"])
        self.assertFalse(report["authority"]["certifies_domain_size"])

    def test_unknown_values_do_not_count_as_evidence(self):
        report = bundle.evaluate_configuration({
            "ship": "WAYFARER_BASELINE",
            "mass_state_model": "UNKNOWN",
            "node_topology": "UNRESOLVED",
            "hull_lattice_configuration": None,
        })
        self.assertEqual(len(report["missing_required_evidence"]), 3)

    def test_current_inventory_has_complete_identity_but_no_domain_claim(self):
        report = bundle.build_current_e1_inventory()
        self.assertEqual(report["ship"], "WAYFARER_BASELINE")
        self.assertEqual(report["disposition"], "CONFIGURATION_IDENTITY_PRESENT")
        self.assertEqual(report["missing_required_evidence"], [])
        self.assertTrue(report["configuration_identity_complete"])
        self.assertEqual(
            report["configuration"]["hull_lattice_configuration"],
            "WAYFARER_REFERENCE_SCHEMATIC_V2_4A",
        )
        self.assertFalse(report["authority"]["certifies_domain_membership_or_attachment"])


if __name__ == "__main__":
    unittest.main()
