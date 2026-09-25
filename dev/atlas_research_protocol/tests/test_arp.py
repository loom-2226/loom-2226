from __future__ import annotations

import copy
import hashlib
import json
import sqlite3
import unittest
from pathlib import Path

from dev.atlas_research_protocol.validate import efficiency_metrics, load_json, qualify, valid_time
from dev.atlas_research_protocol.state import remaining_work


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


class ARPTest(unittest.TestCase):
    def setUp(self) -> None:
        self.campaign = load_json(ROOT / "fixtures/campaign_reference.json")
        self.policy = load_json(ROOT / "policies/source_authority.json")

    def assertFails(self, mutate, code: str) -> None:
        campaign = copy.deepcopy(self.campaign)
        mutate(campaign)
        result = qualify(campaign, self.policy, REPO)
        self.assertEqual("FAIL", result["status"])
        self.assertTrue(any(error.startswith(code + ":") for error in result["errors"]), result)

    def test_reference_campaign_passes_and_is_resumable(self):
        result = qualify(self.campaign, self.policy, REPO)
        self.assertEqual({"status": "PASS", "errors": [], "blocking": False}, result)
        self.assertEqual("RESUMABLE", self.campaign["status"])
        self.assertTrue(self.campaign["unresolved_gaps"])
        profile = load_json(ROOT / "profiles/body_profiles.json")["profiles"][self.campaign["body_profile"]]
        remaining = remaining_work(self.campaign, profile)
        self.assertTrue(remaining["resumable"])
        self.assertIn("geology_geotechnical", remaining["remaining_lanes"])

    def test_artifact_hash_and_byte_count_are_checked(self):
        bad = copy.deepcopy(self.campaign)
        bad["artifacts"][0]["sha256"] = "0" * 64
        result = qualify(bad, self.policy, REPO)
        self.assertEqual("FAIL", result["status"])
        self.assertTrue(any(e.startswith("ARTIFACT_HASH:") for e in result["errors"]))

    def test_secondary_source_cannot_replace_represented_primary(self):
        self.assertFails(lambda c: c["sources"][0].update(authority_role="SECONDARY", primary_available=True), "AUTHORITY_LAUNDERING")

    def test_publications_sharing_lineage_are_not_independent(self):
        def mutate(c):
            a = copy.deepcopy(c["assertions"][0]); a["assertion_id"] = "SECOND"; a["canonical_assertion_key"] = "SECOND"; a["independent"] = True; c["assertions"].append(a)
        self.assertFails(mutate, "DUPLICATE_LINEAGE")

    def test_preprint_journal_and_derivative_publications_need_distinct_lineage(self):
        def mutate(c):
            a = copy.deepcopy(c["assertions"][0]); a["assertion_id"] = "JOURNAL-VERSION"; a["canonical_assertion_key"] = "JOURNAL-VERSION"; a["independent"] = True; a["source_id"] = c["sources"][0]["source_id"]; c["assertions"].append(a)
        self.assertFails(mutate, "DUPLICATE_LINEAGE")

    def test_scope_resolution_and_epistemic_laundering_fail(self):
        self.assertFails(lambda c: c["assertions"][0].update(scope_type="REGIONAL", scope_claim="GLOBAL"), "SCOPE_LAUNDERING")
        self.assertFails(lambda c: c["assertions"][0].update(resolution={"source_grain": "COARSE", "claimed_grain": "SITE"}), "RESOLUTION_LAUNDERING")
        self.assertFails(lambda c: c["assertions"][0].update(claim_kind="OBSERVATION", method_type="MODEL", evidence_class="IN_SITU_REMOTE"), "MODEL_PROMOTION")

    def test_cutoff_and_range_midpoint_fail(self):
        self.assertFails(lambda c: c["sources"][0].update(publication_date="2026-01-01"), "CUTOFF")
        self.assertFails(lambda c: c["assertions"][0].update(value_min=1, value_max=3, reported_value=2, reported_unit="km"), "RANGE_MIDPOINT")

    def test_unknown_and_frontier_promotion_fail(self):
        self.assertFails(lambda c: c["assertions"][0].update(research_coverage="UNKNOWN", reported_value=1, reported_unit="km"), "UNKNOWN_FABRICATION")
        self.assertFails(lambda c: c["epistemic_frontier"][0].update(phase="FUTURE_OBSERVABLE", state_at_cutoff="KNOWABLE"), "FRONTIER_PROMOTION")

    def test_repeated_campaign_execution_is_idempotent(self):
        def mutate(c):
            duplicate = copy.deepcopy(c["assertions"][0]); duplicate["assertion_id"] = "REPLAY"; c["assertions"].append(duplicate)
        self.assertFails(mutate, "DUPLICATE_ASSERTION")

    def test_forbidden_authority_sparse_completion_and_blocking_lien_fail(self):
        self.assertFails(lambda c: c["epistemic_frontier"][0].update(phase="ENGINEERING_DERIVED"), "CONTAMINATION")
        self.assertFails(lambda c: c.update(coverage_summary={"complete_claim": True}), "FALSE_COMPLETENESS")
        self.assertFails(lambda c: c["liens"].append({"lien_id": "BLOCK", "state": "OPEN", "severity": "BLOCKING", "target": "x", "finding": "unresolved"}), "BLOCKING_LIEN")

    def test_temporal_contract_is_strict(self):
        self.assertTrue(valid_time("2025-12-31"))
        self.assertTrue(valid_time("2025-12-31T23:59:59Z"))
        for value in ("banana", "2025-02-30", "2025-13-01", "2025-01-01T25:00:00Z"):
            self.assertFalse(valid_time(value))

    def test_metrics_include_independent_lineages_and_reuse(self):
        metrics = efficiency_metrics(self.campaign)
        self.assertEqual(1, metrics["artifacts_reused"])
        self.assertEqual(1, metrics["independent_evidence_lineages"])
        self.assertEqual(0, metrics["external_research_operations"])

    def test_ceres_gold_fixture_matches_qualified_specimen(self):
        gold = load_json(ROOT / "fixtures/ceres_gold.json")
        db = REPO / "dev/solar_facts_hcq01/v0_3_r1/LOOM_SOLAR_HCQ01_CERES_v0_3_R1.sqlite3"
        self.assertEqual(gold["database_sha256"], hashlib.sha256(db.read_bytes()).hexdigest())
        conn = sqlite3.connect(db)
        for table, expected in gold["expected_counts"].items():
            self.assertEqual(expected, conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0], table)
        self.assertEqual("ok", conn.execute("PRAGMA integrity_check").fetchone()[0])
        self.assertEqual([], conn.execute("PRAGMA foreign_key_check").fetchall())
        facts = {row[0]: row[1] for row in conn.execute("SELECT property_code, fact_status FROM fact")}
        self.assertEqual(8, len(facts)); self.assertTrue(all(status == "CANDIDATE" for status in facts.values()))
        self.assertEqual(0, conn.execute("SELECT count(*) FROM preferred_fact").fetchone()[0])

    def test_profiles_are_reusable_and_not_ceres_specific(self):
        profiles = load_json(ROOT / "profiles/body_profiles.json")["profiles"]
        self.assertEqual(8, len(profiles))
        self.assertNotEqual(profiles["gas_giant"]["applicable_lanes"], profiles["dwarf_planet"]["applicable_lanes"])
        self.assertIn("required_lanes", profiles["comet"])


if __name__ == "__main__":
    unittest.main()
