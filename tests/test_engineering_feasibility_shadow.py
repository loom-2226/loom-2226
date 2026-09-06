from __future__ import annotations

import unittest

from loom.navigation.engineering_feasibility_shadow import (
    D2I_ENGINEERING_FEASIBILITY_CONTRACT,
    EngineeringFeasibilityError,
    evaluate_engineering_feasibility_shadow,
)


class EngineeringFeasibilityShadowTests(unittest.TestCase):
    def _trajectory(self):
        return {
            "samples": [
                {"sample_index": 1, "epoch_utc": "2226-01-01T00:00:00Z",
                 "ordinary_pos_x_km": 0.0, "ordinary_pos_y_km": 0.0, "ordinary_pos_z_km": 0.0,
                 "ordinary_vel_x_km_s": 0.0, "ordinary_vel_y_km_s": 0.0, "ordinary_vel_z_km_s": 0.0,
                 "ordinary_accel_g": 0.5, "wet_mass_t": 1000.0},
                {"sample_index": 2, "epoch_utc": "2226-01-01T00:01:00Z",
                 "ordinary_pos_x_km": 60.0, "ordinary_pos_y_km": 0.0, "ordinary_pos_z_km": 0.0,
                 "ordinary_vel_x_km_s": 1.0, "ordinary_vel_y_km_s": 0.0, "ordinary_vel_z_km_s": 0.0,
                 "ordinary_accel_g": 0.5, "wet_mass_t": 999.0},
                {"sample_index": 3, "epoch_utc": "2226-01-01T00:02:00Z",
                 "ordinary_pos_x_km": 120.0, "ordinary_pos_y_km": 0.0, "ordinary_pos_z_km": 0.0,
                 "ordinary_vel_x_km_s": 1.0, "ordinary_vel_y_km_s": 0.0, "ordinary_vel_z_km_s": 0.0,
                 "ordinary_accel_g": 0.5, "wet_mass_t": 998.0},
            ]
        }

    def _route_payload(self, thrust_n=8_000_000.0):
        return {
            "torch": "CRUISE", "thermal": "SUSTAINABLE",
            "leg": {"terminal_burn": {
                "thrust_N": thrust_n,
                "ve_km_s": 2000.0,
                "mdot_kg_s": 4.0,
                "dv_hat": [1.0, 0.0, 0.0],
                "thermal_posture": "SUSTAINABLE",
                "thermal_numeric_margin": None,
            }}
        }

    def _guidance(self, mid_shadow_y=0.0, mid_shadow_vy=0.0, peak=0.001):
        return {"report": {
            "guidance_accel_limit_km_s2": 0.02,
            "max_guidance_correction_km_s2": peak,
            "samples": [
                {"epoch_utc": "2226-01-01T00:00:00Z",
                 "reference_position_km": [0.0,0.0,0.0], "shadow_position_km": [0.0,0.0,0.0],
                 "reference_velocity_km_s": [0.0,0.0,0.0], "shadow_velocity_km_s": [0.0,0.0,0.0],
                 "guidance_correction_km_s2": 0.0},
                {"epoch_utc": "2226-01-01T00:01:00Z",
                 "reference_position_km": [60.0,0.0,0.0], "shadow_position_km": [60.0,mid_shadow_y,0.0],
                 "reference_velocity_km_s": [1.0,0.0,0.0], "shadow_velocity_km_s": [1.0,mid_shadow_vy,0.0],
                 "guidance_correction_km_s2": peak},
                {"epoch_utc": "2226-01-01T00:02:00Z",
                 "reference_position_km": [120.0,0.0,0.0], "shadow_position_km": [120.0,0.0,0.0],
                 "reference_velocity_km_s": [1.0,0.0,0.0], "shadow_velocity_km_s": [1.0,0.0,0.0],
                 "guidance_correction_km_s2": peak},
            ]
        }}

    def test_sampled_vector_envelope_pass_stays_open_for_vectoring_and_thermal(self):
        out = evaluate_engineering_feasibility_shadow(
            self._trajectory(), self._route_payload(), self._guidance(mid_shadow_y=-0.3, peak=0.001)
        )
        self.assertEqual(out["contract"], D2I_ENGINEERING_FEASIBILITY_CONTRACT)
        self.assertTrue(out["sampled_thrust_magnitude_within_mode_envelope"])
        self.assertEqual(out["status"], "OPEN_VECTORING_AND_THERMAL_QUALIFICATION")
        self.assertEqual(out["vectoring_qualification"], "OPEN_NO_CERTIFIED_THRUST_VECTOR_OR_GIMBAL_ENVELOPE")
        self.assertEqual(out["thermal_qualification"], "OPEN_NO_NUMERIC_THERMAL_MARGIN")
        self.assertGreater(out["estimated_required_remass_t_over_qualified_interval"], 0.0)
        self.assertFalse(out["qualification"]["route_mutation"])

    def test_sampled_thrust_overage_fails_magnitude_envelope(self):
        guidance = self._guidance(mid_shadow_y=0.0, mid_shadow_vy=0.0, peak=0.02)
        # Force a large correction along +x at the middle sample by placing the shadow behind reference.
        guidance["report"]["samples"][1]["shadow_position_km"] = [40.0,0.0,0.0]
        out = evaluate_engineering_feasibility_shadow(
            self._trajectory(), self._route_payload(thrust_n=5_000_000.0), guidance
        )
        self.assertFalse(out["sampled_thrust_magnitude_within_mode_envelope"])
        self.assertEqual(out["status"], "FAIL_SAMPLED_THRUST_MAGNITUDE")
        self.assertLess(out["minimum_sampled_thrust_accel_margin_km_s2"], 0.0)

    def test_between_sample_peak_is_explicitly_open(self):
        out = evaluate_engineering_feasibility_shadow(
            self._trajectory(), self._route_payload(), self._guidance(mid_shadow_y=-0.01, peak=0.015)
        )
        self.assertTrue(out["between_sample_peak_correction_open"])
        self.assertEqual(out["qualification"]["between_sample_vector_envelope"], "OPEN_D2H_REPORT_ONLY_EXPOSES_PEAK_MAGNITUDE")

    def test_missing_terminal_burn_fails_closed(self):
        with self.assertRaises(EngineeringFeasibilityError):
            evaluate_engineering_feasibility_shadow(self._trajectory(), {}, self._guidance())


if __name__ == "__main__":
    unittest.main()
