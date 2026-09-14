from __future__ import annotations

import unittest


class TestWayfarerRCSActuatorRequirementEnvelope(unittest.TestCase):
    def test_sampled_command_reducer_derives_bounds_without_selecting_hardware(self):
        from src.wayfarer_rcs_actuator_requirement_envelope import summarize_mount_command_trace

        trace = [
            {"t_s": 0.0, "mount_id": "M1", "thrust_N": 1000.0, "force_unit": [1.0, 0.0, 0.0]},
            {"t_s": 1.0, "mount_id": "M1", "thrust_N": 2000.0, "force_unit": [0.0, 1.0, 0.0]},
            {"t_s": 2.0, "mount_id": "M1", "thrust_N": 0.0, "force_unit": None},
        ]
        out = summarize_mount_command_trace(trace, sample_period_s=1.0)
        self.assertEqual(out["sample_period_s"], 1.0)
        self.assertAlmostEqual(out["minimum_nonzero_sampled_impulse_Ns"], 1000.0)
        self.assertAlmostEqual(out["maximum_sampled_thrust_step_N"], 2000.0)
        self.assertAlmostEqual(out["maximum_sampled_direction_step_deg"], 90.0)
        self.assertFalse(out["hardware_selected"])

    def test_contract_keeps_actual_actuator_hardware_unqualified(self):
        from src.wayfarer_rcs_actuator_requirement_envelope import requirement_authority_contract

        contract = requirement_authority_contract()
        self.assertTrue(contract["sampled_flight_demand_envelope_derivable"])
        self.assertFalse(contract["minimum_impulse_bit_certified"])
        self.assertFalse(contract["valve_dynamics_certified"])
        self.assertFalse(contract["gimbal_dynamics_certified"])
        self.assertFalse(contract["final_thruster_hardware_certified"])
        self.assertEqual(contract["campaign_state_mutation"], "ZERO")
        self.assertEqual(contract["llm_calculation_authority"], "ZERO")

    def test_no_hardware_value_is_silently_promoted(self):
        from src.wayfarer_rcs_actuator_requirement_envelope import REQUIREMENT_CONTRACT

        forbidden = {
            "selected_minimum_impulse_bit_Ns",
            "selected_valve_latency_s",
            "selected_gimbal_slew_deg_s",
            "selected_gimbal_accel_deg_s2",
        }
        self.assertTrue(forbidden.isdisjoint(REQUIREMENT_CONTRACT.keys()))
        self.assertEqual(REQUIREMENT_CONTRACT["interpretation"], "SAMPLED_DEMAND_REQUIREMENTS_NOT_HARDWARE_QUALIFICATION")


if __name__ == "__main__":
    unittest.main()
