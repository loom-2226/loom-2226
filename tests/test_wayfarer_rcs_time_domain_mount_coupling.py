from __future__ import annotations

import unittest

from src.wayfarer_rcs_time_domain_mount_coupling import (
    ACTUATOR_CONTRACT,
    build_time_domain_mount_coupling_qualification,
)


class WayfarerRCSTimeDomainMountCouplingTests(unittest.TestCase):
    def test_actuator_contract_is_explicit_and_non_hardware_certifying(self):
        self.assertEqual(ACTUATOR_CONTRACT["command_domain"], "CONTINUOUS_MOUNT_FORCE_VECTOR")
        self.assertEqual(ACTUATOR_CONTRACT["allocation_location"], "INSIDE_COUPLED_LOCAL_FLIGHT_TIME_LOOP")
        self.assertFalse(ACTUATOR_CONTRACT["minimum_impulse_bit_modeled"])
        self.assertFalse(ACTUATOR_CONTRACT["valve_dynamics_modeled"])
        self.assertFalse(ACTUATOR_CONTRACT["gimbal_dynamics_modeled"])
        self.assertFalse(ACTUATOR_CONTRACT["plume_geometry_modeled"])
        self.assertFalse(ACTUATOR_CONTRACT["structural_mount_compliance_modeled"])
        self.assertFalse(ACTUATOR_CONTRACT["final_thruster_hardware_certified"])

    def test_mount_allocator_is_closed_inside_time_domain_loop(self):
        result = build_time_domain_mount_coupling_qualification()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(
            result["disposition"],
            "MOUNT_LEVEL_ALLOCATION_BOUND_INTO_COUPLED_LOCAL_FLIGHT_TIME_LOOP",
        )
        self.assertTrue(result["authority"]["mount_level_allocator_in_time_loop"])
        self.assertTrue(result["authority"]["allocated_achieved_wrench_drives_vehicle_state"])
        self.assertFalse(result["authority"]["minimum_impulse_bit_certified"])
        self.assertFalse(result["authority"]["plume_interference_certified"])
        self.assertFalse(result["authority"]["structural_mount_loads_certified"])
        self.assertFalse(result["authority"]["final_thruster_hardware_certified"])
        self.assertGreater(result["summary"]["allocation_calls"], 0)
        self.assertLessEqual(result["summary"]["worst_relative_normalized_residual"], 1.0e-4)
        self.assertLessEqual(result["summary"]["max_mount_utilization_fraction"], 1.0 + 1.0e-9)

    def test_remaining_open_hardware_items_are_preserved(self):
        result = build_time_domain_mount_coupling_qualification()
        self.assertEqual(
            result["remaining_open"],
            [
                "minimum_impulse_bit_and_valve_gimbal_dynamics",
                "finite_plume_and_external_hardware_interference",
                "structural_rcs_mount_loads",
            ],
        )


if __name__ == "__main__":
    unittest.main()
