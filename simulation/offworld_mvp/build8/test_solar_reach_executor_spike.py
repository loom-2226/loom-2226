"""Source-eligible body choice and Executor competition: no named world targets."""
import copy
from decimal import Decimal as D
from hashlib import sha256
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from .solar_reach_executor_spike import (load, report, simulate, full_catalog,
                                          eligible_public_catalog)


def scenario_sha(data):
    return sha256((json.dumps(data, sort_keys=True, indent=2)+"\n").encode()).hexdigest()


class SolarReachChoiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.sha = load()
        cls.results = report()
        cls.small = cls.results["results"]["SMALL"]["run"]
        cls.large = cls.results["results"]["LONG"]["run"]
        cls.first = cls.small["awards"][0]
        cls.sponsor = cls.first["sponsor"]

    def altered(self, data, cast="SMALL"):
        return simulate(data, cast, scenario_sha(data))

    def test_full_catalog_clock_and_replays(self):
        catalog = full_catalog(self.data)
        eligible = eligible_public_catalog(self.data, catalog)
        for name, result in self.results["results"].items():
            r = result["run"]
            self.assertEqual(r["catalog_count"], len(catalog))
            self.assertEqual(r["eligible_count"], len(eligible))
            self.assertEqual(r["year_count"],
                             self.data["clock"]["last_year"] -
                             self.data["clock"]["first_year"] + 1)
            self.assertEqual(r["body_year_rows"], len(catalog)*r["year_count"])
            self.assertEqual(result["verified_replays"],
                             self.data["replay_policy"]["total_executions_per_cast"]-1)
            self.assertEqual(len(set(result["replay_hashes"])),1)
            self.assertEqual(D(r["initial_money"]),D(r["ending_money"]))
            self.assertTrue(r["annual_conservation"])
            self.assertEqual(len(r["choices"]),
                             r["year_count"]*len(self.data["casts"][name]["sponsors"]))
            self.assertTrue(all(c["evaluated"]==len(eligible) for c in r["choices"]))
            self.assertTrue(r["belief_yearly_sha256"])

    def test_ineligible_public_entities_remain_visible(self):
        catalog=full_catalog(self.data)
        eligible=eligible_public_catalog(self.data,catalog)
        excluded={row["body_id"] for row in catalog
                  if row["body_class"] in ("BARYCENTER", "SPACECRAFT", "STAR")}
        self.assertTrue(excluded)
        self.assertFalse(excluded & set(eligible))
        self.assertFalse(excluded & {a["body"] for a in self.small["awards"]})
        self.assertEqual(self.small["catalog_count"],len(catalog))

    def test_unavailable_selected_body_moves_choice(self):
        doc = copy.deepcopy(self.data)
        sponsor = next(s for s in doc["casts"]["SMALL"]["sponsors"]
                       if s["name"]==self.sponsor)
        sponsor["decision"]["unavailable_bodies"].append(self.first["body"])
        r = self.altered(doc)
        self.assertEqual(r["eligible_count"],self.small["eligible_count"])
        self.assertNotEqual(r["awards"][0]["body"],self.first["body"])
        self.assertNotEqual(r["run_id"],self.small["run_id"])

    def test_value_and_reach_shift_move_choice(self):
        for key, mutation in self.data["body_choice_mutations"].items():
            if key=="remove_chosen":
                continue
            with self.subTest(key=key):
                doc=copy.deepcopy(self.data)
                sponsor=next(s for s in doc["casts"]["SMALL"]["sponsors"]
                             if s["name"]==self.sponsor)
                sponsor["decision"]["body_overrides"][self.first["body"]] = {
                    mutation["key"]:mutation["delta"]}
                r=self.altered(doc)
                self.assertNotEqual(r["awards"][0]["body"],self.first["body"])
                self.assertNotEqual(r["replay_hash"],self.small["replay_hash"])

    def test_add_sponsor_with_distinct_values_targets_elsewhere(self):
        doc=copy.deepcopy(self.data)
        additional=next(s for s in doc["casts"]["LONG"]["sponsors"]
                        if s["name"] not in {s["name"] for s in doc["casts"]["SMALL"]["sponsors"]})
        doc["casts"]["SMALL"]["sponsors"].append(copy.deepcopy(additional))
        r=self.altered(doc)
        destinations={c["sponsor"]:c["body"] for c in r["awards"]
                      if c["start"]==self.first["start"]}
        self.assertIn(additional["name"],destinations)
        self.assertNotEqual(destinations[additional["name"]],destinations[self.sponsor])
        self.assertEqual(r["catalog_count"],self.small["catalog_count"])

    def test_failure_changes_later_executor_decision(self):
        first=self.first
        self.assertEqual(first["outcome"],"FAILED")
        bids=[b for b in self.small["bids"]
              if b["year"]==first["start"] and b["sponsor"]==first["sponsor"]]
        self.assertTrue(all(b["action"]=="BID" for b in bids))
        later=next(c for c in self.small["awards"] if c["start"]>first["finish"]-1)
        self.assertNotEqual(later["executor"],first["executor"])
        after=next(b for b in self.small["bids"]
                   if b["year"]==later["start"] and b["sponsor"]==later["sponsor"]
                   and b["executor"]==first["executor"])
        self.assertEqual((after["action"],after["reason"]),
                         ("DECLINE","RELIABILITY_HURDLE"))
        doc=copy.deepcopy(self.data)
        doc["test_only_delivery_outcomes"][first["sponsor"]][first["sequence"]] = (
            doc["test_only_controls"]["alternate_first_outcome"])
        r=self.altered(doc)
        self.assertNotEqual(r["replay_hash"],self.small["replay_hash"])
        next_bid=next(b for b in r["bids"]
                     if b["year"]==later["start"] and b["sponsor"]==later["sponsor"]
                     and b["executor"]==first["executor"])
        self.assertEqual(next_bid["action"],"BID")

    def test_five_authored_executor_knobs(self):
        for knob, mutation in self.data["knob_mutations"].items():
            with self.subTest(knob=knob):
                doc=copy.deepcopy(self.data)
                role="executors" if "executor" in mutation else "sponsors"
                name=mutation.get("executor",mutation.get("sponsor"))
                obj=next(x for x in doc["casts"]["SMALL"][role] if x["name"]==name)
                parts=mutation["field"].split(".")
                for part in parts[:-1]:
                    obj=obj[part]
                obj[parts[-1]]=mutation["value"]
                r=self.altered(doc)
                self.assertNotEqual(r["run_id"],self.small["run_id"])
                self.assertNotEqual(r["replay_hash"],self.small["replay_hash"])
                self.assertTrue(r["annual_conservation"])
                if knob=="funding":
                    self.assertFalse(r["awards"])
                else:
                    self.assertNotEqual(r["awards"][0]["executor"],self.first["executor"])

    def test_source_pin_is_fail_closed(self):
        old=Path.read_bytes
        def mutated(path):
            result=old(path)
            if path.name=="master_cast_candidate.json":
                return result+b"x"
            return result
        with patch.object(Path,"read_bytes",mutated):
            with self.assertRaisesRegex(ValueError,"SOURCE_PIN_MISMATCH"):
                load()


if __name__=="__main__":
    unittest.main()
