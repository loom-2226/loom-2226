import unittest

from src.wayfarer_rcs_physical_architecture_trade import build_physical_architecture_trade


class TestWayfarerRCSPhysicalArchitectureTrade(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trade = build_physical_architecture_trade()

    def test_trade_consumes_qualified_requirement_envelope(self):
        self.assertEqual(self.trade["status"], "PASS")
        self.assertEqual(self.trade["source_requirement_claim"], "PHYSICAL_REQUIREMENT_ENVELOPE_ONLY")

    def test_preserves_candidate_not_hardware_selection_boundary(self):
        a = self.trade["authority"]
        self.assertEqual(a["claim"], "EVIDENCE_BACKED_PHYSICAL_ARCHITECTURE_TRADE_ONLY")
        self.assertFalse(a["final_thruster_hardware_certified"])
        self.assertFalse(a["working_fluid_certified"])
        self.assertFalse(a["vectoring_mechanism_certified"])
        self.assertEqual(a["campaign_state_mutation"], "ZERO")
        self.assertEqual(a["llm_calculation_authority"], "ZERO")

    def test_trade_keeps_required_candidate_families_open(self):
        families = {x["id"] for x in self.trade["candidate_families"]}
        self.assertIn("COMPOUND_COARSE_FINE_VECTORED_MOUNT", families)
        vectoring = set(self.trade["trade_axes"]["vectoring_mechanism_candidates"])
        self.assertIn("DIFFERENTIAL_INTERNAL_NOZZLES", vectoring)
        self.assertIn("FLUIDIC_OR_SECONDARY_INJECTION", vectoring)
        self.assertIn("MECHANICAL_GIMBAL_IF_EVIDENCE_SUPPORTS", vectoring)

    def test_evidence_supports_mechanism_families_not_wayfarer_values(self):
        findings = self.trade["evidence_findings"]
        self.assertTrue(findings["electronically_valved_variable_injection_geometry_supported"])
        self.assertTrue(findings["fluidic_secondary_injection_tvc_supported"])
        self.assertTrue(findings["mib_response_is_coupled_propulsion_gnc_quantity"])
        self.assertFalse(findings["wayfarer_45_degree_vector_cone_physically_demonstrated"])
        self.assertFalse(findings["wayfarer_numeric_hardware_values_supported"])

    def test_no_propellant_or_performance_value_is_invented(self):
        selection = self.trade["selection"]
        self.assertIsNone(selection["working_fluid"])
        self.assertIsNone(selection["exhaust_velocity_m_s"])
        self.assertIsNone(selection["minimum_impulse_bit_Ns"])
        self.assertIsNone(selection["valve_response_s"])
        self.assertIsNone(selection["vectoring_mechanism"])

    def test_next_step_is_governed_extrapolation_before_installation(self):
        self.assertEqual(
            self.trade["qualified_next_step"],
            "BUILD_GOVERNED_RCS_TECHNOLOGY_EXTRAPOLATION_AND_DOWNSELECT_THEN_RUN_INSTALLATION_FEASIBILITY",
        )


if __name__ == "__main__":
    unittest.main()
