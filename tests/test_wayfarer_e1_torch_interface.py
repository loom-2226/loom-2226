import unittest
from fractions import Fraction

from src.wayfarer_e1_torch_interface import (
    E1TorchState,
    OpenPhysicalClosure,
    evaluate_torch_interface,
)


class TestWayfarerE1TorchInterface(unittest.TestCase):
    def test_wet_fast_contract_uses_exact_card_truth(self):
        result = evaluate_torch_interface(
            mode="FAST",
            vehicle_mass_kg=Fraction(1_158_500),
            normal_remass_kg=Fraction(250_000),
            protected_water_kg=Fraction(50_000),
            torch_state=E1TorchState.ACTIVE,
            high_metric_active=False,
        )
        self.assertEqual(result.mdot_kg_s, Fraction(4869001725, 100_000_000))
        self.assertEqual(result.exhaust_velocity_m_s, Fraction(700_000))
        self.assertEqual(result.thrust_n, result.mdot_kg_s * result.exhaust_velocity_m_s)
        self.assertEqual(
            result.direct_kinetic_jet_power_w,
            Fraction(1, 2) * result.mdot_kg_s * result.exhaust_velocity_m_s**2,
        )
        self.assertEqual(result.acceleration_m_s2, result.thrust_n / Fraction(1_158_500))

    def test_protected_water_is_not_normal_remass(self):
        with self.assertRaisesRegex(ValueError, "normal remass"):
            evaluate_torch_interface(
                mode="ECON",
                vehicle_mass_kg=Fraction(900_000),
                normal_remass_kg=Fraction(250_001),
                protected_water_kg=Fraction(49_999),
                torch_state=E1TorchState.ACTIVE,
                high_metric_active=False,
            )

    def test_torch_and_high_metric_are_mutually_exclusive(self):
        with self.assertRaisesRegex(ValueError, "high-metric"):
            evaluate_torch_interface(
                mode="CRUISE",
                vehicle_mass_kg=Fraction(1_000_000),
                normal_remass_kg=Fraction(200_000),
                protected_water_kg=Fraction(50_000),
                torch_state=E1TorchState.ACTIVE,
                high_metric_active=True,
            )

    def test_open_physical_closure_has_no_hidden_defaults(self):
        open_items = OpenPhysicalClosure()
        self.assertIsNone(open_items.source_directed_fraction)
        self.assertIsNone(open_items.fusion_gain_q)
        self.assertIsNone(open_items.source_specific_power_w_per_kg)
        self.assertIsNone(open_items.nozzle_efficiency)
        self.assertIsNone(open_items.remass_species)
        self.assertIsNone(open_items.feed_hardware)

    def test_off_state_has_zero_outputs(self):
        result = evaluate_torch_interface(
            mode=None,
            vehicle_mass_kg=Fraction(908_500),
            normal_remass_kg=Fraction(0),
            protected_water_kg=Fraction(50_000),
            torch_state=E1TorchState.OFF,
            high_metric_active=False,
        )
        self.assertEqual(result.thrust_n, 0)
        self.assertEqual(result.mdot_kg_s, 0)
        self.assertEqual(result.direct_kinetic_jet_power_w, 0)


if __name__ == "__main__":
    unittest.main()
