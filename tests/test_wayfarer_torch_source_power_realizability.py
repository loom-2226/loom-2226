import unittest
from src.wayfarer_torch_source_power_realizability import build_envelope, evaluate_candidate

class TorchSourcePowerRealizabilityTests(unittest.TestCase):
    def test_no_unearned_efficiency_defaults(self):
        r=build_envelope()
        self.assertIsNone(r["candidate_inputs"]["directed_energy_fraction"])
        self.assertIsNone(r["candidate_inputs"]["fusion_gain_Q"])
        self.assertIsNone(r["candidate_inputs"]["specific_power_W_kg"])

    def test_required_source_power_is_only_derived_from_explicit_fraction(self):
        c=evaluate_candidate("LIMIT", directed_energy_fraction=0.8, fusion_gain_Q=10.0, specific_power_W_kg=1e8)
        self.assertAlmostEqual(c["required_fusion_output_W"], 12781129528125.0/0.8)
        self.assertAlmostEqual(c["minimum_external_driver_power_W_if_Q_definition_applies"], c["required_fusion_output_W"]/10.0)
        self.assertAlmostEqual(c["minimum_source_system_mass_kg_at_specific_power"], c["required_fusion_output_W"]/1e8)
        self.assertFalse(c["certified"])

    def test_rejects_invalid_physical_parameters(self):
        with self.assertRaises(ValueError): evaluate_candidate("FAST", 0.0, 10.0, 1e8)
        with self.assertRaises(ValueError): evaluate_candidate("FAST", 1.1, 10.0, 1e8)
        with self.assertRaises(ValueError): evaluate_candidate("FAST", 0.8, 0.0, 1e8)
        with self.assertRaises(ValueError): evaluate_candidate("FAST", 0.8, 10.0, 0.0)

    def test_scale_gate_is_explicit(self):
        r=build_envelope()
        self.assertEqual(r["realizability_decision"], "OPEN_NEEDS_PHYSICAL_BOUNDS")
        self.assertIn("FUSION_GAIN_Q_BY_MODE", r["blocking_holds"])
        self.assertIn("SOURCE_SYSTEM_SPECIFIC_POWER", r["blocking_holds"])
        self.assertIn("DIRECTED_ENERGY_FRACTION_FROM_PHYSICAL_PARTITION", r["blocking_holds"])

    def test_power_firewall(self):
        r=build_envelope()
        self.assertEqual(r["power_firewall"], "FUSION_OUTPUT_AND_DRIVER_POWER_ARE_NOT_AUTOMATICALLY_VEHICLE_ELECTRICAL_LOAD_OR_WASTE_HEAT")

if __name__ == "__main__": unittest.main()
