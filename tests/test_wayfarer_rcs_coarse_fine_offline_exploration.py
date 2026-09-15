import unittest
from unittest.mock import patch

from src.wayfarer_rcs_coarse_fine_offline_exploration import (
    EXPLORATION_CASES,
    EXPLORATION_PARAMETERS,
    build_offline_exploration_plan,
    execute_offline_exploration,
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

    def test_executor_runs_cartesian_grid_across_all_cases_and_derives_pass_region(self):
        def fake_case(name, spec, *, coarse_fraction, fine_fraction, trace_mib_ns):
            passed = coarse_fraction <= 0.20 and fine_fraction <= 0.50
            return {"pass": passed, "duration_s": 10.0,
                    "terminal_velocity_error_m_s": 0.001,
                    "terminal_attitude_error_deg": 0.01,
                    "terminal_body_rate_deg_s": 0.001,
                    "max_mount_realization_error_N": fine_fraction,
                    "coarse_total_impulse_Ns": coarse_fraction * 100.0,
                    "fine_total_impulse_Ns": fine_fraction * 100.0}

        with patch("src.wayfarer_rcs_coarse_fine_offline_exploration.build_actuator_requirement_envelope") as demand, patch(
            "src.wayfarer_rcs_coarse_fine_offline_exploration._simulate_case", side_effect=fake_case
        ) as simulate:
            demand.return_value = {"aggregate_sampled_actuator_demand": {"sampled_exact_trace_mib_upper_bound_Ns": 9.0}}
            result = execute_offline_exploration()

        self.assertEqual(simulate.call_count, len(EXPLORATION_PARAMETERS) * len(EXPLORATION_CASES))
        self.assertEqual(result["execution"]["point_count"], len(EXPLORATION_PARAMETERS))
        self.assertEqual(result["execution"]["case_runs"], len(EXPLORATION_PARAMETERS) * len(EXPLORATION_CASES))
        self.assertEqual(result["source_demand"]["sampled_exact_trace_mib_upper_bound_Ns"], 9.0)
        self.assertEqual(
            {(p["coarse_activation_fraction"], p["fine_quantization_fraction"]) for p in result["pass_region"]},
            {(0.10, 0.25), (0.10, 0.50), (0.20, 0.25), (0.20, 0.50)},
        )
        self.assertEqual(result["authority"]["claim"], "NUMERICAL_PASS_REGION_ONLY")
        self.assertFalse(result["authority"]["final_thruster_hardware_certified"])
        self.assertEqual(result["authority"]["campaign_state_mutation"], "ZERO")
        self.assertEqual(result["authority"]["llm_calculation_authority"], "ZERO")


if __name__ == "__main__":
    unittest.main()
