import unittest

from src.wayfarer_rcs_coarse_fine_offline_exploration import (
    EXPLORATION_CASES,
    EXPLORATION_PARAMETERS,
    build_offline_exploration_plan,
)
from src.wayfarer_rcs_time_domain_mount_coupling import _CASES


class CoarseFineOfflineExplorationContractTests(unittest.TestCase):
    def test_exploration_covers_all_canonical_coupled_cases(self):
        self.assertEqual(tuple(_CASES), EXPLORATION_CASES)

    def test_grid_contains_pixel_witness_and_multiple_independent_axes(self):
        self.assertIn((0.20, 0.50), EXPLORATION_PARAMETERS)
        coarse = {row[0] for row in EXPLORATION_PARAMETERS}
        fine = {row[1] for row in EXPLORATION_PARAMETERS}
        self.assertGreaterEqual(len(coarse), 3)
        self.assertGreaterEqual(len(fine), 3)
        self.assertEqual(len(EXPLORATION_PARAMETERS), len(coarse) * len(fine))

    def test_plan_is_exploratory_not_hardware_authority(self):
        plan = build_offline_exploration_plan()
        self.assertEqual(plan["execution_authority"], "OFFLINE_ENGINEERING_EXPLORATION")
        self.assertFalse(plan["authority"]["final_thruster_hardware_certified"])
        self.assertFalse(plan["authority"]["minimum_impulse_bit_certified"])
        self.assertFalse(plan["authority"]["valve_dynamics_certified"])
        self.assertFalse(plan["authority"]["vectoring_mechanism_certified"])
        self.assertEqual(plan["authority"]["campaign_state_mutation"], "ZERO")
        self.assertEqual(plan["authority"]["llm_calculation_authority"], "ZERO")

    def test_pixel_is_not_assigned_full_sweep(self):
        plan = build_offline_exploration_plan()
        self.assertEqual(plan["pixel_contract"]["full_sweep"], "PROHIBITED")
        self.assertEqual(plan["pixel_contract"]["qualification_mode"], "BOUNDARY_AND_WITNESS_REPLAY_ONLY")


if __name__ == "__main__":
    unittest.main()
