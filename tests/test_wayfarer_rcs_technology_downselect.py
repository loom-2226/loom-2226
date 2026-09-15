import unittest

from src.wayfarer_rcs_technology_downselect import build_technology_downselect


class TestWayfarerRCSTechnologyDownselect(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = build_technology_downselect()

    def test_selects_architecture_family_not_component_values(self):
        s = self.result["selection"]
        self.assertEqual(s["mount_architecture"], "COMPOUND_COARSE_FINE_VECTORED_MOUNT")
        self.assertEqual(s["coarse_actuation"], "ELECTRONICALLY_METERED_THROTTLEABLE_LIQUID_THRUSTER_FAMILY")
        self.assertEqual(s["fine_actuation"], "DEDICATED_FAST_PULSED_FINE_AUTHORITY_ELEMENT")
        self.assertEqual(s["vectoring_architecture"], "INTERNAL_FLOW_VECTORING_PREFERRED_MECHANICAL_GIMBAL_RESERVE")
        self.assertIsNone(s["working_fluid"])
        self.assertIsNone(s["exhaust_velocity_m_s"])
        self.assertIsNone(s["minimum_impulse_bit_Ns"])
        self.assertIsNone(s["valve_response_s"])

    def test_downselect_is_explicitly_extrapolative(self):
        self.assertEqual(self.result["epistemic_class"], "GOVERNED_FUTURE_TECHNOLOGY_EXTRAPOLATION")
        self.assertFalse(self.result["authority"]["final_thruster_hardware_certified"])
        self.assertFalse(self.result["authority"]["propellant_selected"])

    def test_rejects_single_throttleable_element_as_fine_authority_assumption(self):
        self.assertEqual(
            self.result["design_decisions"]["fine_control"],
            "SEPARATE_FINE_ELEMENT_UNTIL_EVIDENCE_PROVES_COARSE_ELEMENT_CAN_MEET_MIB_AND_RESPONSE_REQUIREMENT",
        )

    def test_next_step_is_installation_feasibility(self):
        self.assertEqual(
            self.result["qualified_next_step"],
            "RUN_RCS_PLUME_THERMAL_STRUCTURAL_INSTALLATION_FEASIBILITY",
        )


if __name__ == "__main__":
    unittest.main()
