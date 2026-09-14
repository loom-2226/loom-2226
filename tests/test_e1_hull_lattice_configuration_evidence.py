import unittest

from engineering.experience_one.qualification.e1_hull_lattice_configuration_evidence import (
    build_current_e1_hull_lattice_configuration,
)


class HullLatticeConfigurationEvidenceTests(unittest.TestCase):
    def test_governing_structural_grammar_is_preserved_without_inventing_node_placement(self):
        evidence = build_current_e1_hull_lattice_configuration()
        self.assertEqual(evidence["status"], "PASS")
        self.assertEqual(evidence["configuration_id"], "WAYFARER_REFERENCE_SCHEMATIC_V2_4A")
        self.assertEqual(evidence["primary_structural_grammar"]["axial_longerons"], 4)
        self.assertEqual(evidence["primary_structural_grammar"]["working_fluid_remass_tanks"], 4)
        self.assertEqual(evidence["primary_structural_grammar"]["radiator_assemblies"], 4)
        self.assertEqual(evidence["primary_structural_grammar"]["primary_axial_torch_nozzle_systems"], 1)
        self.assertEqual(evidence["relational_node_topology"]["distributed_boundary_metric_nodes"], 208)
        self.assertEqual(evidence["relational_node_topology"]["exact_node_placement"], "OPEN")

    def test_integrated_launch_attachment_is_part_of_governing_configuration(self):
        evidence = build_current_e1_hull_lattice_configuration()
        launch = evidence["integrated_launch_bay"]
        self.assertEqual(launch["packaging"], "SEMI_RECESSED_UNPRESSURIZED_INTEGRATED_PRIMARY_STRUCTURE")
        self.assertTrue(launch["attachment_state_required_in_dependent_solutions"])

    def test_configuration_identity_does_not_claim_domain_geometry_or_membership(self):
        evidence = build_current_e1_hull_lattice_configuration()
        self.assertTrue(evidence["configuration_identity_present"])
        self.assertFalse(evidence["authority"]["certifies_domain_geometry"])
        self.assertFalse(evidence["authority"]["certifies_domain_membership_or_attachment"])
        self.assertFalse(evidence["authority"]["certifies_lattice_coherence"])
        self.assertFalse(evidence["policy"]["exact_hull_contour_required_for_configuration_identity"])
        self.assertFalse(evidence["policy"]["node_count_substitutes_for_exact_node_placement"])


if __name__ == "__main__":
    unittest.main()
