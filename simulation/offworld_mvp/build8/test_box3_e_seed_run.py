"""Local-only tests for Build 8 E. Not added to any CI selection."""
import unittest
from decimal import Decimal as D

from .box3_d1_repeat_attempts import Box3D1, PaidAttempt, AttemptDeclined
from .box3_e_seed_run import (
    N, SIGMAS, PREFIX, _seed, _count_assessment, run_experiment, forced_arm, sponsor_arm,
)


class Box3ESeedRunTests(unittest.TestCase):
    def test_01_seed_identity_is_fixed_and_bounded(self):
        self.assertEqual(N, 10000)
        self.assertEqual(SIGMAS, 3)
        self.assertEqual(_seed(0), PREFIX + "00000")
        self.assertEqual(_seed(9999), PREFIX + "09999")
        for bad in (-1, 10000):
            with self.assertRaises(ValueError):
                _seed(bad)

    def test_02_each_forced_arm_uses_three_paid_d1_observations(self):
        for present in (True, False):
            measured = forced_arm(synthetic_present=present, sample_size=8)
            self.assertEqual(measured["paid_attempts"], 24)
            self.assertEqual(measured["total_paid_model_currency"], 240)
            self.assertEqual(sum(measured["first_detection"].values()), 8)
            self.assertEqual(
                measured["cumulative_misses"]["cumulative_miss_3"],
                measured["first_detection"]["all_three_missed"])

    def test_03_sponsor_calls_actual_d1_choice_and_reconciles_money(self):
        result = sponsor_arm(sample_size=8)
        self.assertEqual(sum(result["stopped_on_decision"].values()), 8)
        self.assertEqual(result["stopped_on_decision"]["1"], 0)
        self.assertEqual(result["stopped_on_decision"]["2"], 0)
        self.assertEqual(result["stopped_on_decision"]["3"], 0)
        self.assertEqual(result["stopped_on_decision"]["5"], 0)
        self.assertEqual(result["total_paid_model_currency"],
                         10 * sum(int(n) * k for n, k
                                  in result["paid_attempts_per_seed"].items()))

    def test_04_small_replay_has_identical_outcome_hashes_not_timings(self):
        a = run_experiment(16)
        b = run_experiment(16)
        self.assertEqual(a["measurement"], b["measurement"])
        self.assertEqual(a["measurement"]["aggregate_sha256"],
                         b["measurement"]["aggregate_sha256"])
        self.assertEqual(a["measurement"]["present"]["seeds"], 16)

    def test_05_sigma_rule_correct_and_inclusive(self):
        x = _count_assessment(8000, 0.8, 10000)
        self.assertEqual((x["expected"], x["three_sigma_tolerance"]),
                         (8000, 120.0))
        self.assertTrue(x["within_tolerance"])
        self.assertFalse(_count_assessment(8121, 0.8, 10000)["within_tolerance"])

    def test_06_no_d1_or_kernel_edits_for_experiment(self):
        # Local check that the actual D1 path is what is exercised,
        # including the expected stop at decision 4 under three negatives
        # only when naturally drawn, and immutable paid identifiers.
        x = Box3D1(synthetic_conditional_present=True,
                   run_name="BUILD8_BOX3_E_SEED:00000")
        paid = [x.try_attempt() for _ in range(3)]
        self.assertTrue(all(isinstance(x, PaidAttempt) for x in paid))
        self.assertEqual([p.attempt_number for p in paid], [1, 2, 3])
        self.assertEqual(len(x.kernel.state.transactions), 3)
        self.assertEqual(x.kernel.state.accounts["SPN:POOL"].balance, D("20"))
        self.assertEqual(x.try_attempt(attempt_number=2), paid[1])
        self.assertEqual(len(x.kernel.state.transactions), 3)
        self.assertEqual(x.kernel.state.projects["P-REGION"].status, "PROPOSED")


if __name__ == "__main__":
    unittest.main()
