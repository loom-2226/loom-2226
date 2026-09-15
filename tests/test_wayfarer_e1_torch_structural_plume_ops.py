import unittest

from src.wayfarer_e1_torch_structural_plume_ops import build_structural_plume_ops_envelope


class WayfarerE1TorchStructuralPlumeOpsTests(unittest.TestCase):
    def setUp(self):
        self.r = build_structural_plume_ops_envelope()

    def test_t4_is_interface_closure_not_component_certification(self):
        self.assertEqual(self.r["status"], "E1_INTEGRATION_ENVELOPE_WITH_TECHNOLOGY_HOLDS")
        a = self.r["authority"]
        self.assertFalse(a["thrust_frame_certified"])
        self.assertFalse(a["physical_plume_certified"])
        self.assertFalse(a["rcs_installation_certified"])
        self.assertFalse(a["thermal_hardware_certified"])

    def test_exact_axial_load_envelope_is_inherited(self):
        modes = self.r["axial_thrust_envelope_N"]
        self.assertAlmostEqual(modes["ECON"], 3408301.2075)
        self.assertAlmostEqual(modes["LIMIT"], 85207530.1875)
        self.assertEqual(self.r["governing_known_axial_load_mode"], "LIMIT")

    def test_structural_unknowns_are_not_defaulted(self):
        s = self.r["structural_interface"]
        self.assertEqual(s["primary_load_path"], "FOUR_LONGERON_AXIAL_THRUST_FRAME_INTERFACE")
        self.assertIsNone(s["structural_design_factor"])
        self.assertIsNone(s["dynamic_amplification_factor"])
        self.assertIsNone(s["side_load_fraction"])
        self.assertIsNone(s["fatigue_spectrum"])
        self.assertIsNone(s["local_reinforcement_design"])

    def test_candidate_packaging_remains_candidate(self):
        p = self.r["aft_packaging_interface"]
        self.assertEqual(p["status"], "NON_GOVERNING_CANDIDATE")
        self.assertEqual(p["shadow_shield_x_m"], [38.0, 43.0])
        self.assertEqual(p["reactor_thrust_frame_x_m"], [43.0, 50.0])
        self.assertEqual(p["magnetic_nozzle_x_m"], [50.0, 57.0])

    def test_plume_geometry_is_not_invented(self):
        p = self.r["plume_external_clearance_interface"]
        self.assertIsNone(p["plume_half_angle_deg"])
        self.assertIsNone(p["plume_length_m"])
        self.assertIsNone(p["clearance_margin_m"])
        self.assertIn("PHYSICAL_PLUME_MODEL_AND_CLEARANCE_SWEEP", p["holds"])
        self.assertIn("RADIATORS_DEPLOYED_AND_STOWED", p["required_clearance_classes"])

    def test_rcs_and_thermal_holds_are_preserved(self):
        self.assertEqual(len(self.r["rcs_integration_holds"]), 5)
        self.assertIn("WORKING_FLUID_CYCLE_EXHAUST_VELOCITY_AND_THERMAL_LOAD", self.r["rcs_integration_holds"])
        self.assertIn("SHIELD_MAGNET_AND_THERMAL_LIFETIME_OPEN", self.r["thermal_and_lifetime_holds"])

    def test_operational_exclusions_are_explicit(self):
        o = self.r["operational_interface"]
        self.assertTrue(o["torch_high_metric_mutually_exclusive"])
        self.assertIn("NO_TORCH_OPERATION_DURING_HIGH_METRIC_THERMAL_OR_FIELD_OPERATION", o["exclusions"])
        self.assertIn("TRANSITION_PRECONDITIONS_OPEN_PENDING_FEED_FIELD_THERMAL_AND_ATTITUDE_DYNAMICS", o["holds"])


if __name__ == "__main__":
    unittest.main()
