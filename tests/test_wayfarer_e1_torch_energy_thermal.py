import unittest
from fractions import Fraction

from src.wayfarer_e1_torch_energy_thermal import (
    radiator_area_m2,
    source_thermal_envelope,
)


class TestWayfarerE1TorchEnergyThermal(unittest.TestCase):
    def test_source_output_requires_directed_fraction(self):
        r = source_thermal_envelope(mode="LIMIT")
        self.assertIsNone(r.source_output_w)
        self.assertIsNone(r.vehicle_deposition_w)
        self.assertIsNone(r.required_radiator_area_m2)
        self.assertIn("SOURCE_DIRECTED_FRACTION_OPEN", r.holds)
        self.assertIn("VEHICLE_DEPOSITION_FRACTION_OPEN", r.holds)

    def test_source_output_is_jet_power_over_directed_fraction(self):
        r = source_thermal_envelope(mode="ECON", source_directed_fraction=Fraction(4, 5))
        self.assertEqual(r.source_output_w, r.direct_kinetic_jet_power_w / Fraction(4, 5))
        self.assertIsNone(r.vehicle_deposition_w)

    def test_deposition_can_be_bounded_from_source_output(self):
        r = source_thermal_envelope(
            mode="CRUISE",
            source_directed_fraction=Fraction(9, 10),
            vehicle_deposition_fraction=Fraction(1, 100_000),
        )
        self.assertEqual(r.vehicle_deposition_w, r.source_output_w / 100_000)
        self.assertIsNotNone(r.required_radiator_area_m2)

    def test_radiator_area_uses_900K_interface_and_explicit_emissivity(self):
        area = radiator_area_m2(
            heat_rejection_w=Fraction(50_000_000),
            temperature_k=Fraction(900),
            emissivity=Fraction(9, 10),
        )
        self.assertGreater(float(area), 1000.0)
        self.assertLess(float(area), 2000.0)

    def test_radiator_sizing_refuses_hidden_emissivity(self):
        r = source_thermal_envelope(
            mode="FAST",
            source_directed_fraction=Fraction(1),
            vehicle_deposition_fraction=Fraction(1, 100_000),
            radiator_emissivity=None,
        )
        self.assertIsNotNone(r.vehicle_deposition_w)
        self.assertIsNone(r.required_radiator_area_m2)
        self.assertIn("RADIATOR_EMISSIVITY_OPEN", r.holds)

    def test_invalid_partition_is_rejected(self):
        with self.assertRaises(ValueError):
            source_thermal_envelope(mode="FAST", source_directed_fraction=Fraction(11, 10))
        with self.assertRaises(ValueError):
            source_thermal_envelope(mode="FAST", vehicle_deposition_fraction=Fraction(-1, 10))


if __name__ == "__main__":
    unittest.main()
