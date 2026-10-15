"""In-memory Build 8 Box 3 tests: existing portfolio policy, two actual projects."""
import json
import unittest
from decimal import Decimal as D

from .box3_two_project_choice import run_two_project_choice


class Box3TwoProjectChoiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.low = run_two_project_choice("NEGATIVE")
        cls.high = run_two_project_choice("POSITIVE")

    def test_distinct_projects_real_offworld_capital(self):
        for r in (self.low, self.high):
            self.assertEqual(r["scenario_inputs"]["opening_shared_capital"], "100")
            self.assertEqual(sum(map(D, r["scenario_inputs"]["commitments"].values())), D("120"))
            self.assertEqual(r["before"]["A"], {
                "balance": "0", "project_status": "PROPOSED",
                "activity_status": "PROPOSED"})
            self.assertEqual(r["before"]["B"], r["before"]["A"])
            self.assertEqual(r["after"]["A"], {
                "balance": "60", "project_status": "DEVELOPMENT",
                "activity_status": "COMPLETED"})
            self.assertEqual(r["after"]["B"], r["before"]["B"])
            self.assertEqual(r["funding_transaction"]["source"], "SPN:POOL")
            self.assertEqual(r["funding_transaction"]["destination"], "cash:A")
            self.assertEqual(r["funding_transaction"]["amount"], "60")
            self.assertEqual(r["funding_transaction"]["purpose"], "OTHER_INVESTMENT")
            self.assertTrue(r["funding_transaction"]["funded_project_status_event_id"].startswith("evt-"))

    def test_existing_policy_selected_and_remainder_explicitly_deferred(self):
        for r in (self.low, self.high):
            self.assertEqual(r["decision"]["selected"], "ACT-A")
            self.assertEqual(r["decision"]["outcome"], "AUTHORIZE")
            self.assertEqual(r["decision"]["reason"], "SELECTED_PRIORITY_AFFORDABLE")
            self.assertEqual(r["unfunded"]["disposition"], "DEFERRED_NOT_ABANDONED")
            self.assertEqual(r["unfunded"]["reason"], "INSUFFICIENT_AVAILABLE_CAPITAL")
            self.assertEqual(r["unfunded"]["project_status"], "PROPOSED")
            self.assertTrue(r["unfunded"]["recorded_event_id"].startswith("evt-"))
            self.assertEqual(r["initial_snapshot"]["account_balance"], "100")
            self.assertEqual(r["remaining_snapshot"]["account_balance"], "40")
            self.assertEqual(r["initial_snapshot"]["facts"]["portfolio.AVAILABLE_CAPITAL"]["value"], "100")
            self.assertEqual(r["remaining_snapshot"]["facts"]["portfolio.AVAILABLE_CAPITAL"]["value"], "40")

    def test_no_hidden_truth_enters_either_policy_snapshot(self):
        for r in (self.low, self.high):
            for key in ("initial_snapshot", "remaining_snapshot"):
                snapshot = r[key]
                self.assertEqual(len(snapshot["admitted_observations"]), 1)
                self.assertEqual(
                    snapshot["facts"]["observation.VISIBLE_SIGNAL"]["value"],
                    r["scenario_inputs"]["signal"])
                self.assertEqual(
                    snapshot["facts"]["observation.VISIBLE_SIGNAL"]["source"],
                    "SYNTHETIC:SPN_ADMITTED_OBSERVATION")
                self.assertEqual(snapshot["priors"], {
                    "BODY:SYNTHETIC:VOLATILES_PRESENT": "0.5"})
                self.assertNotIn("hidden_truth", snapshot)
                self.assertNotIn("world_seed", snapshot)
                self.assertNotIn("body_truth", snapshot)
                self.assertNotIn("resources", snapshot)
                self.assertTrue(all(f["source"].startswith(("KERNEL:", "SYNTHETIC:"))
                                    for f in snapshot["facts"].values()))
        self.assertEqual(
            self.low["initial_snapshot"]["beliefs"],
            {"BODY:SYNTHETIC:VOLATILES_PRESENT": "0.2"})
        self.assertEqual(
            self.high["initial_snapshot"]["beliefs"],
            {"BODY:SYNTHETIC:VOLATILES_PRESENT": "0.8"})

    def test_every_year_gauge_matches_unchanged_kernel_shadow(self):
        for r in (self.low, self.high):
            rows = r["gauge"]
            self.assertEqual([a["year"] for a in rows], [1, 2, 3])
            for row in rows:
                draw = D(row["offworld_draw"])
                self.assertEqual(D(row["new_capital_draw"]) +
                                 D(row["recycled_returned_cash_spent"]), draw)
                self.assertEqual(D(row["project_A_capital_received"]) +
                                 D(row["project_B_capital_received"]) +
                                 D(row["unattributed_capital"]), draw)
                for zero in ("recycled_returned_cash_spent", "unattributed_capital",
                             "returns_received", "study_spending",
                             "offworld_purchases_from_earth",
                             "earth_side_transport_spending_for_offworld_projects"):
                    self.assertEqual(D(row[zero]), D(0))
            self.assertEqual([row["offworld_draw"] for row in rows], ["0", "60", "0"])
            self.assertEqual([row["project_A_capital_received"] for row in rows],
                             ["0", "60", "0"])
            self.assertEqual([row["project_B_capital_received"] for row in rows],
                             ["0", "0", "0"])

    def test_beliefs_change_but_policy_choice_does_not(self):
        self.assertNotEqual(self.low["initial_snapshot"]["beliefs"],
                            self.high["initial_snapshot"]["beliefs"])
        self.assertEqual(self.low["decision"]["selected"],
                         self.high["decision"]["selected"])
        self.assertEqual(self.low["gauge"], self.high["gauge"])

    def test_replay_is_identical_for_each_scenario(self):
        for signal, expected in (("NEGATIVE", self.low), ("POSITIVE", self.high)):
            again = run_two_project_choice(signal)
            self.assertEqual(again, expected)
            self.assertEqual(json.dumps(again, sort_keys=True),
                             json.dumps(expected, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
