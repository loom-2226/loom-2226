import unittest

from src.wayfarer_torch_plume_clearance_envelope import (
    build_envelope,
    evaluate_plume_candidate,
)


class TorchPlumeClearanceEnvelopeTests(unittest.TestCase):
    def test_authority_firewall(self):
        r = build_envelope()
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(
            r["authority"]["claim"],
            "E1_TORCH_PHYSICAL_PLUME_AND_EXTERNAL_CLEARANCE_ENVELOPE_ONLY",
        )
        self.assertFalse(r["authority"]["physical_plume_certified"])
        self.assertFalse(r["authority"]["external_clearance_certified"])
        self.assertFalse(r["authority"]["nozzle_geometry_certified"])

    def test_no_plume_geometry_is_invented(self):
        r = build_envelope()
        c = r["candidate_inputs"]
        self.assertIsNone(c["nozzle_exit_radius_m"])
        self.assertIsNone(c["plume_half_angle_deg"])
        self.assertIsNone(c["plume_length_m"])
        self.assertIsNone(c["exclusion_margin_m"])

    def test_candidate_requires_explicit_geometry_and_positive_bounds(self):
        with self.assertRaises(ValueError):
            evaluate_plume_candidate("LIMIT", 3.0, 0.0, 100.0, 2.0)
        with self.assertRaises(ValueError):
            evaluate_plume_candidate("LIMIT", -1.0, 5.0, 100.0, 2.0)

    def test_explicit_candidate_derives_conservative_radial_envelope_only(self):
        e = evaluate_plume_candidate("FAST", 3.0, 5.0, 100.0, 2.0)
        self.assertGreater(e["plume_radius_at_length_m"], 3.0)
        self.assertGreater(e["clearance_radius_with_margin_m"], e["plume_radius_at_length_m"])
        self.assertEqual(e["status"], "SENSITIVITY_ONLY_NOT_CERTIFIED")

    def test_external_hardware_classes_are_explicit(self):
        r = build_envelope()
        classes = r["required_clearance_classes"]
        self.assertIn("RCS_THRUSTERS_AND_PLUMES", classes)
        self.assertIn("RADIATORS_DEPLOYED_AND_STOWED", classes)
        self.assertIn("SENSORS_ANTENNAS_AND_COMMUNICATIONS", classes)
        self.assertIn("DOCKING_CARGO_AND_SERVICE_ENVELOPES", classes)

    def test_next_step_is_integrated_torch_vehicle_architecture(self):
        self.assertEqual(
            build_envelope()["qualified_next_step"],
            "INTEGRATED_TORCH_VEHICLE_ARCHITECTURE_AND_COMPONENT_FREEZE_READINESS_REVIEW",
        )


if __name__ == "__main__":
    unittest.main()
