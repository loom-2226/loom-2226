"""PR C opt-in tests. Separate from the frozen Build 8 CI ten-test selection."""
import json
import unittest
from decimal import Decimal as D
from .box3_belief_funding_choice import run_belief_funding_choice as run


class BeliefDrivenFundingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Fixed, declared grid; no scenario adjustments after observing outcomes.
        cls.grid = {a: run(a) for a in ("20%", "50%", "80%")}
        cls.hurdles = {str(h): run("50%", hurdle=D(h)) for h in ("0", "20", "150")}

    def test_belief_grid_from_admitted_existing_updates(self):
        self.assertEqual([self.grid[a]["candidates"]["A"]["belief"]
                          for a in ("20%", "50%", "80%")], ["0.2", "0.5", "0.8"])
        self.assertEqual([self.grid[a]["candidates"]["B"]["belief"]
                          for a in ("20%", "50%", "80%")], ["0.5"] * 3)
        for r in self.grid.values():
            self.assertEqual(r["scenario_inputs"]["initial_prior"], "0.5")
            self.assertEqual(r["scenario_inputs"]["likelihoods"],
                             {"detection": "0.8", "false_positive": "0.2"})
            self.assertEqual(r["scenario_inputs"]["belief_signals"]["B"],
                             ["POSITIVE", "NEGATIVE"])

    def test_grid_choice_changes_only_where_expected(self):
        self.assertEqual([self.grid[a]["decision"]["selected"]
                          for a in ("20%", "50%", "80%")],
                         ["ACT-B", "ACT-A", "ACT-A"])
        self.assertEqual(self.grid["20%"]["candidates"]["B"]["priority"], 1)
        self.assertEqual(self.grid["50%"]["candidates"]["A"]["priority"], 1)
        self.assertEqual(self.grid["80%"]["candidates"]["A"]["priority"], 1)

    def test_assigned_success_value_changes_choice_at_same_belief(self):
        alternative = run("50%", assigned_values={"A": D("100"), "B": D("200")})
        self.assertEqual(self.grid["50%"]["decision"]["selected"], "ACT-A")
        self.assertEqual(alternative["decision"]["selected"], "ACT-B")
        self.assertEqual(alternative["candidates"]["A"]["expected_net_value"], "-10.0")
        self.assertEqual(alternative["candidates"]["B"]["expected_net_value"], "40.0")

    def test_low_medium_high_hurdles(self):
        self.assertEqual(self.hurdles["0"]["offered_to_policy"], ["ACT-A", "ACT-B"])
        self.assertEqual(self.hurdles["20"]["offered_to_policy"], ["ACT-A"])
        self.assertEqual(self.hurdles["150"]["offered_to_policy"], [])
        self.assertEqual(self.hurdles["0"]["decision"]["selected"], "ACT-A")
        self.assertEqual(self.hurdles["20"]["decision"]["selected"], "ACT-A")
        self.assertIsNone(self.hurdles["150"]["decision"]["selected"])

    def test_all_below_declines_with_untouched_capital(self):
        r = self.hurdles["150"]
        self.assertEqual(r["decision"]["outcome"], "DECLINED")
        self.assertEqual(r["decision"]["reason"], "ALL_EXPECTED_NET_VALUES_BELOW_HURDLE")
        self.assertEqual(r["decision"]["hurdle"], "150")
        self.assertEqual(r["decision"]["expected_net_values"], {"A": "40.0", "B": "5.0"})
        self.assertIsNone(r["funding_transaction"])
        self.assertEqual(r["final_sponsor_capital"], "100")
        self.assertEqual([g["offworld_draw"] for g in r["gauge"]], ["0", "0", "0"])
        for t in ("A", "B"):
            self.assertEqual(r["after"][t], r["before"][t])
            self.assertEqual(r["unfunded"][t]["disposition"], "WAITING_BELOW_HURDLE")

    def test_one_above_one_below_retains_waiting_project(self):
        r = self.hurdles["20"]
        self.assertEqual(r["offered_to_policy"], ["ACT-A"])
        self.assertEqual(r["decision"]["selected"], "ACT-A")
        self.assertEqual(r["unfunded"]["B"]["reason"], "BELOW_HURDLE")
        self.assertEqual(r["after"]["B"]["project_status"], "PROPOSED")
        self.assertEqual(r["after"]["B"]["activity_status"], "PROPOSED")

    def test_both_above_single_capital_pool_deferred_by_existing_policy(self):
        r = self.hurdles["0"]
        self.assertEqual([r["candidates"][t]["above_or_at_hurdle"]
                          for t in ("A", "B")], [True, True])
        self.assertEqual(r["scenario_inputs"]["opening_shared_capital"], "100")
        self.assertEqual(r["decision"]["selected"], "ACT-A")
        self.assertEqual(r["unfunded"]["B"]["reason"], "INSUFFICIENT_AVAILABLE_CAPITAL")
        self.assertEqual(r["unfunded"]["B"]["disposition"], "DEFERRED_NOT_ABANDONED")
        self.assertEqual(r["final_sponsor_capital"], "40")

    def test_same_beliefs_values_two_sponsors_different_hurdles(self):
        low = run("50%", sponsor_id="SPN_LOW", hurdle=D("0"))
        high = run("50%", sponsor_id="SPN_HIGH", hurdle=D("150"))
        for t in ("A", "B"):
            self.assertEqual(low["candidates"][t]["belief"], high["candidates"][t]["belief"])
            self.assertEqual(low["candidates"][t]["value_if_successful"],
                             high["candidates"][t]["value_if_successful"])
        self.assertEqual(low["decision"]["selected"], "ACT-A")
        self.assertEqual(high["decision"]["outcome"], "DECLINED")

    def test_tie_break_is_project_then_activity(self):
        # Fixed equal valuations at fixed equal posterior (both EV = 40).
        r = run("50%", assigned_values={"A": D("200"), "B": D("200")})
        self.assertEqual(r["ranked_projects"], ["P-A", "P-B"])
        self.assertEqual(r["candidates"]["A"]["priority"], 1)
        self.assertEqual(r["decision"]["selected"], "ACT-A")

    def test_real_transfer_each_year_ledger_and_waiting_state(self):
        cases = list(self.grid.values()) + list(self.hurdles.values())
        cases.append(run("50%", assigned_values={"A": "100", "B": "200"}))
        for r in cases:
            paid = r["funding_transaction"]
            funded = r["decision"]["selected"]
            if funded:
                tag = funded[-1]
                self.assertEqual(paid["source"], r["scenario_inputs"]["sponsor_id"] + ":POOL")
                self.assertEqual(paid["destination"], "cash:" + tag)
                self.assertEqual(paid["purpose"], "OTHER_INVESTMENT")
                self.assertEqual(paid["amount"], "60")
                self.assertEqual(paid["parent_ids"],
                                 [r["decision"]["id"], r["decision"]["selected"]])
                self.assertEqual(r["after"][tag]["project_status"], "DEVELOPMENT")
                self.assertEqual(r["after"][tag]["activity_status"], "COMPLETED")
            for g in r["gauge"]:
                draw = D(g["offworld_draw"])
                self.assertEqual(D(g["new_capital_draw"]) +
                                 D(g["recycled_returned_cash_spent"]), draw)
                self.assertEqual(D(g["project_A_capital_received"]) +
                                 D(g["project_B_capital_received"]) +
                                 D(g["unattributed_capital"]), draw)
                for key in ("recycled_returned_cash_spent", "unattributed_capital",
                            "returns_received", "study_spending", "offworld_purchases_from_earth",
                            "earth_side_transport_spending_for_offworld_projects"):
                    self.assertEqual(D(g[key]), D(0))
            self.assertEqual([g["year"] for g in r["gauge"]], [1, 2, 3])
            self.assertEqual([g["offworld_draw"] for g in r["gauge"]],
                             ["0", "60", "0"] if funded else ["0", "0", "0"])

    def test_no_hidden_truth_reaches_any_visible_snapshot(self):
        for r in list(self.grid.values()) + list(self.hurdles.values()):
            for name in ("initial_snapshot", "remaining_snapshot"):
                snap = r[name]
                if snap is None:
                    continue
                self.assertEqual(snap["actor"], r["scenario_inputs"]["sponsor_id"])
                self.assertEqual(len(snap["admitted_observations"]),
                                 sum(map(len, r["scenario_inputs"]["belief_signals"].values())))
                self.assertEqual(set(snap["beliefs"]), set(snap["priors"]))
                self.assertEqual(snap["priors"], {
                    "BODY:SYNTHETIC:PROJECT:A:VOLATILES_PRESENT": "0.5",
                    "BODY:SYNTHETIC:PROJECT:B:VOLATILES_PRESENT": "0.5"})
                self.assertTrue(all(f["source"].startswith(("KERNEL:", "SPONSOR:", "SYNTHETIC:"))
                                    for f in snap["facts"].values()))
                self.assertFalse(set(snap).intersection(
                    {"hidden_truth", "world_seed", "body_truth", "resources", "kernel"}))
            # No below-hurdle activity is offered to the frozen policy.
            for t in ("A", "B"):
                if not r["candidates"][t]["above_or_at_hurdle"]:
                    self.assertNotIn("ACT-" + t, r["offered_to_policy"])

    def test_deterministic_replay_full_report(self):
        specs = [
            ("20%", "50%", None, "0", "SPN"),
            ("50%", "50%", None, "20", "SPN"),
            ("80%", "50%", None, "150", "SPN"),
            ("50%", "50%", {"A": "100", "B": "200"}, "0", "SPN"),
            ("50%", "50%", None, "150", "SPN_HIGH"),
        ]
        for a, b, values, hurdle, sponsor in specs:
            x = run(a, b, assigned_values=values, hurdle=D(hurdle), sponsor_id=sponsor)
            y = run(a, b, assigned_values=values, hurdle=D(hurdle), sponsor_id=sponsor)
            self.assertEqual(x, y)
            self.assertEqual(json.dumps(x, sort_keys=True), json.dumps(y, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
