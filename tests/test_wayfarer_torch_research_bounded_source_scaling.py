import unittest
from src.wayfarer_torch_research_bounded_source_scaling import build_scaling_review

class TorchResearchBoundedSourceScalingTests(unittest.TestCase):
    def test_external_anchors_are_not_wayfarer_parameters(self):
        r=build_scaling_review()
        self.assertEqual(r["external_research"]["authority"], "EXTERNAL_RESEARCH_SYNTHESIS")
        self.assertFalse(r["authority"]["external_anchor_promoted_to_wayfarer_parameter"])
        self.assertIsNone(r["wayfarer_candidate_inputs"]["source_specific_power_W_kg"])

    def test_present_dfd_anchor_fails_by_orders_of_magnitude(self):
        r=build_scaling_review()
        self.assertGreater(r["scaling_diagnostics"]["LIMIT"]["source_mass_t_at_1500_W_kg"], 8_000_000)
        self.assertGreater(r["scaling_diagnostics"]["LIMIT"]["improvement_over_1500_W_kg_for_160_t"], 50_000)

    def test_160_t_allocation_is_not_source_mass_certification(self):
        r=build_scaling_review()
        self.assertEqual(r["candidate_propulsion_allocation_t"],160.0)
        self.assertFalse(r["authority"]["candidate_propulsion_allocation_closed"])
        self.assertGreater(r["minimum_jet_specific_power_if_entire_160_t_were_source_W_kg"]["LIMIT"], 70_000_000)

    def test_research_direction_survives_only_conditionally(self):
        r=build_scaling_review()
        self.assertEqual(r["technology_direction_decision"],"RETAIN_AS_RESEARCH_TOPOLOGY_ONLY_PHYSICAL_SCALE_NOT_CLOSED")
        self.assertIn("ORDERS_OF_MAGNITUDE_SOURCE_SPECIFIC_POWER_ADVANCE",r["blocking_holds"])

    def test_next_step(self):
        self.assertEqual(build_scaling_review()["qualified_next_step"],"TORCH_ENERGY_PARTITION_AND_MASS_BUDGET_FEASIBILITY_ENVELOPE")

if __name__=="__main__": unittest.main()
