"""Cast-only, full-public-catalog, full-clock Executor feedback tests."""
import copy
import json
import unittest
from hashlib import sha256
from pathlib import Path
from decimal import Decimal

from .solar_reach_executor_spike import CAST, decide_bid, full_catalog, load, report, simulate


def changed(data):
    return sha256((json.dumps(data, sort_keys=True, indent=2) + "\n").encode()).hexdigest()


class SolarExecutorSpikeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.source_sha = load()
        cls.full_report = report()
        cls.short = cls.full_report["results"]["SMALL"]["run"]
        cls.long = cls.full_report["results"]["LONG"]["run"]

    def test_full_world_and_two_replays_each(self):
        for name in self.data["casts"]:
            row = self.full_report["results"][name]
            run = row["run"]
            self.assertEqual(row["verified_replays"],
                             self.data["replay_policy"]["total_executions_per_cast"]-1)
            self.assertEqual(run["catalog_count"], len(full_catalog(self.data)))
            self.assertEqual(run["year_count"], self.data["clock"]["last_year"]
                             - self.data["clock"]["first_year"] + 1)
            self.assertEqual(run["body_year_rows"], run["catalog_count"]*run["year_count"])
            self.assertEqual(Decimal(run["initial_money"]), Decimal(run["ending_money"]))
            self.assertTrue(run["annual_conservation"])
            self.assertTrue(run["replay_hash"])

    def test_contested_award_and_later_failure_feedback(self):
        early = self.short["awards"][0]
        later = self.short["awards"][1]
        expectation = self.data["baseline_expectations"]["SMALL"]
        self.assertEqual(early["executor"], expectation["initial_winner"])
        self.assertEqual(early["outcome"], expectation["initial_outcome"])
        self.assertEqual(later["executor"], expectation["later_winner"])
        initial_bids = [b for b in self.short["bids"] if b["want"]==early["id"]]
        self.assertEqual({b["executor"] for b in initial_bids},
                         {x["name"] for x in self.data["casts"]["SMALL"]["executors"]})
        self.assertTrue(all(b["action"] == "BID" for b in initial_bids))
        after = [b for b in self.short["bids"] if b["want"]==later["id"]
                 and b["executor"]=="Thales Alenia Space"]
        self.assertEqual([(b["action"], b["reason"]) for b in after],
                         [(expectation["post_failure_decision"],
                           expectation["post_failure_reason"])])
        initial = next(x for x in self.data["casts"]["SMALL"]["executors"]
                       if x["name"]=="Thales Alenia Space")["beliefs"]
        final = self.short["final_executor_state"]["Thales Alenia Space"]["beliefs"]
        self.assertEqual(final["failure"], str(int(initial["failure"])+1))
        self.assertEqual(final["success"], initial["success"])
        self.assertNotEqual(final["market_price"], initial["market_price"])
        self.assertTrue(self.short["transactions"])

    def test_actual_outcome_changes_later_bid_and_award(self):
        altered = copy.deepcopy(self.data)
        control = self.data["feedback_control"]
        altered["test_only_delivery_outcomes"][
            control["contract_id"]] = control["alternate_test_only_outcome"]
        r = simulate(altered, "SMALL", changed(altered))
        self.assertNotEqual(r["replay_hash"], self.short["replay_hash"])
        first = self.short["awards"][0]["id"]
        self.assertEqual([b for b in r["bids"] if b["want"]==first],
                         [b for b in self.short["bids"] if b["want"]==first])
        self.assertEqual(r["awards"][1]["executor"],
                         control["expected_later_winner"])
        self.assertTrue(r["annual_conservation"])

    def test_same_code_long_cast_with_more_real_competition(self):
        self.assertGreater(len(self.data["casts"]["LONG"]["executors"]),
                           len(self.data["casts"]["SMALL"]["executors"]))
        self.assertGreater(len(self.long["awards"]),len(self.short["awards"]))
        self.assertNotEqual(self.short["run_id"],self.long["run_id"])
        self.assertEqual(self.short["catalog_count"],self.long["catalog_count"])
        self.assertEqual(self.short["year_count"],self.long["year_count"])

    def test_five_knobs_have_real_consequences(self):
        base_first = self.short["awards"][0]["executor"]
        base_hash = self.short["replay_hash"]
        expected = set(("capacity","margin","price_belief","reliability_prior","funding"))
        self.assertEqual(set(self.data["knob_mutations"]), expected)
        for knob, mutation in self.data["knob_mutations"].items():
            with self.subTest(knob=knob):
                candidate = copy.deepcopy(self.data)
                cast = candidate["casts"][mutation["cast"]]
                role = "executors" if "executor" in mutation else "sponsors"
                target = next(x for x in cast[role]
                              if x["name"] == mutation.get("executor",mutation.get("sponsor")))
                parts=mutation["field"].split(".")
                obj=target
                for part in parts[:-1]:
                    obj=obj[part]
                obj[parts[-1]]=mutation["value"]
                r=simulate(candidate,"SMALL",changed(candidate))
                self.assertNotEqual(r["run_id"],self.short["run_id"])
                self.assertNotEqual(r["replay_hash"],base_hash)
                if knob=="funding":
                    self.assertFalse(r["awards"])
                    self.assertTrue(any(b["action"]=="BID" for b in r["bids"]))
                else:
                    self.assertNotEqual(r["awards"][0]["executor"],base_first)
                    altered_thales = next(b for b in r["bids"]
                            if b["want"]==self.short["awards"][0]["id"]
                            and b["executor"]=="Thales Alenia Space")
                    self.assertEqual(altered_thales["action"],
                                     mutation["expected_bid_action"])
                    if altered_thales["action"] == "BID":
                        self.assertGreater(Decimal(altered_thales["price"]),
                                           Decimal(self.short["awards"][0]["price"]))
                self.assertTrue(r["annual_conservation"])

    def test_source_pin_fails_closed(self):
        from unittest.mock import patch
        original = Path.read_bytes
        def tampered(path):
            raw = original(path)
            return raw + b"x" if path.name == "master_cast_candidate.json" else raw
        with patch.object(Path, "read_bytes", tampered):
            with self.assertRaisesRegex(ValueError, "SOURCE_PIN_MISMATCH"):
                load()


if __name__ == "__main__":
    unittest.main()
