import unittest

from engineering.experience_one.qualification import e1_wayfarer_configuration_evidence as evidence
from engineering.experience_one.qualification import e1_configuration_identity_bundle as bundle


class E1WayfarerConfigurationEvidenceTests(unittest.TestCase):
    def test_mass_state_model_is_promoted_from_current_engineering_authority(self):
        report = evidence.build_evidence()
        mass = report["mass_state_model"]
        self.assertEqual(mass["state"], "PRESENT_QUALIFIED_SUPPORT")
        self.assertEqual(mass["dry_mass_t"], 858.5)
        self.assertEqual(mass["working_fluid_water_t"], 300.0)
        self.assertEqual(mass["wet_mass_t"], 1158.5)
        self.assertEqual(mass["normal_remass_t"], 250.0)
        self.assertEqual(mass["protected_water_reserve_t"], 50.0)
        self.assertTrue(mass["normal_remass_is_within_working_fluid_inventory"])

    def test_node_topology_is_promoted_from_current_governing_canon(self):
        report = evidence.build_evidence()
        topo = report["node_topology"]
        self.assertEqual(topo["state"], "PRESENT_QUALIFIED_SUPPORT")
        self.assertEqual(topo["distributed_boundary_metric_nodes"], 208)
        self.assertEqual(topo["architecture"], "UNIFIED_RELATIONAL_PROPULSION_PLANT")

    def test_hull_lattice_configuration_remains_unresolved(self):
        report = evidence.build_evidence()
        hull = report["hull_lattice_configuration"]
        self.assertEqual(hull["state"], "UNRESOLVED")
        self.assertFalse(hull["configuration_identity_claimed"])

    def test_partial_evidence_does_not_certify_membership_or_lattice(self):
        report = evidence.build_evidence()
        self.assertFalse(report["authority"]["certifies_domain_membership_or_attachment"])
        self.assertFalse(report["authority"]["certifies_lattice_coherence"])
        self.assertFalse(report["authority"]["certifies_overall_ga"])

    def test_identity_bundle_reduces_to_hull_lattice_only(self):
        report = bundle.build_current_e1_inventory()
        self.assertEqual(report["configuration"]["ship"], "WAYFARER_BASELINE")
        self.assertNotEqual(report["configuration"]["mass_state_model"], "UNKNOWN")
        self.assertNotEqual(report["configuration"]["node_topology"], "UNKNOWN")
        self.assertEqual(report["configuration"]["hull_lattice_configuration"], "UNKNOWN")
        self.assertEqual(report["missing_required_evidence"], ["hull_lattice_configuration"])
        self.assertFalse(report["configuration_identity_complete"])


if __name__ == "__main__":
    unittest.main()
