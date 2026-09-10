import math
import unittest

from qualification.synthesis.shipyard_navigator_handoff import (
    HANDOFF_AUTHORITY,
    ShipyardNavigatorHandoffError,
    build_navigator_engineering_payload,
    evaluate_shipyard_contract_with_navigator_shadow,
)
from qualification.synthesis.vehicle_dynamics_contract import build_wayfarer_contract_family


class ShipyardNavigatorHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = build_wayfarer_contract_family(2226)[0]

    def test_payload_maps_validated_cruise_card_without_authority_escalation(self):
        payload = build_navigator_engineering_payload(
            self.contract,
            mode="CRUISE",
            dv_hat=(2.0, 0.0, 0.0),
        )
        card = next(row for row in self.contract.torch_cards if row.mode == "CRUISE")
        burn = payload["leg"]["terminal_burn"]
        self.assertEqual(payload["authority"], HANDOFF_AUTHORITY)
        self.assertEqual(payload["torch"], "CRUISE")
        self.assertEqual(burn["thrust_N"], card.thrust_n_at_contract_mass)
        self.assertEqual(burn["ve_km_s"], card.exhaust_velocity_km_s)
        self.assertEqual(burn["mdot_kg_s"], card.mass_flow_kg_s_at_contract_mass)
        self.assertEqual(burn["dv_hat"], (1.0, 0.0, 0.0))
        self.assertEqual(burn["shipyard_contract_hash"], self.contract.contract_hash)
        self.assertIsNone(burn["thermal_numeric_margin"])
        self.assertFalse(payload["flight_dynamics_authority"])
        self.assertFalse(payload["route_authority"])
        self.assertFalse(payload["guidance_authority"])
        self.assertFalse(payload["thermal_qualification"])
        self.assertFalse(payload["vectoring_qualification"])
        self.assertFalse(payload["canon_changed"])
        self.assertFalse(payload["production_shipclasses_changed"])

    def test_existing_navigator_d2i_consumer_accepts_shipyard_contract(self):
        mass_t = self.contract.wet_mass_kg / 1000.0
        trajectory = {
            "samples": [
                {
                    "epoch_utc": "2226-01-01T00:00:00Z",
                    "sample_index": 0,
                    "ordinary_pos_x_km": 0.0,
                    "wet_mass_t": mass_t,
                    "ordinary_accel_g": 1.0,
                },
                {
                    "epoch_utc": "2226-01-01T00:01:00Z",
                    "sample_index": 1,
                    "ordinary_pos_x_km": 1.0,
                    "wet_mass_t": mass_t,
                    "ordinary_accel_g": 1.0,
                },
            ]
        }
        guidance_shadow = {
            "report": {
                "guidance_accel_limit_km_s2": 0.001,
                "max_guidance_correction_km_s2": 0.0,
                "samples": [
                    {
                        "epoch_utc": "2226-01-01T00:00:00Z",
                        "reference_position_km": (0.0, 0.0, 0.0),
                        "shadow_position_km": (0.0, 0.0, 0.0),
                        "reference_velocity_km_s": (0.0, 0.0, 0.0),
                        "shadow_velocity_km_s": (0.0, 0.0, 0.0),
                    },
                    {
                        "epoch_utc": "2226-01-01T00:01:00Z",
                        "reference_position_km": (1.0, 0.0, 0.0),
                        "shadow_position_km": (1.0, 0.0, 0.0),
                        "reference_velocity_km_s": (0.0, 0.0, 0.0),
                        "shadow_velocity_km_s": (0.0, 0.0, 0.0),
                        "guidance_correction_km_s2": 0.0,
                    },
                ],
            }
        }
        result = evaluate_shipyard_contract_with_navigator_shadow(
            self.contract,
            mode="CRUISE",
            trajectory=trajectory,
            guidance_shadow=guidance_shadow,
        )
        report = result["navigator_report"]
        self.assertTrue(result["consumer_boundary_exercised"])
        self.assertFalse(result["full_m1_closed"])
        self.assertFalse(result["m2_candidate_differentiation_closed"])
        self.assertFalse(result["flight_dynamics_authority"])
        self.assertEqual(report["status"], "OPEN_VECTORING_AND_THERMAL_QUALIFICATION")
        self.assertTrue(report["sampled_thrust_magnitude_within_mode_envelope"])
        self.assertTrue(math.isclose(report["estimated_remass_delta_t_over_qualified_interval"], 0.0, abs_tol=1e-12))
        self.assertEqual(report["vectoring_qualification"], "OPEN_NO_CERTIFIED_THRUST_VECTOR_OR_GIMBAL_ENVELOPE")
        self.assertEqual(report["thermal_qualification"], "OPEN_NO_NUMERIC_THERMAL_MARGIN")

    def test_invalid_mode_and_direction_fail_closed(self):
        with self.assertRaises(ShipyardNavigatorHandoffError):
            build_navigator_engineering_payload(self.contract, mode="MAGIC")
        with self.assertRaises(ShipyardNavigatorHandoffError):
            build_navigator_engineering_payload(self.contract, mode="CRUISE", dv_hat=(0.0, 0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
