from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from dev.atlas_research_protocol.validate import load_json, qualify


ROOT = Path(__file__).resolve().parent


class TransferQualificationTests(unittest.TestCase):
    def setUp(self):
        self.campaign = load_json(ROOT / "campaign.json")

    def test_frozen_campaign_validates_and_is_v102(self):
        result = qualify(self.campaign, None, ROOT)
        self.assertEqual("PASS", result["status"], result)
        self.assertEqual("1.0.2", self.campaign["implementation_version"])
        self.assertEqual("1.0.2", self.campaign["coverage_contract_version"])

    def test_all_covered_lanes_have_explicit_basis(self):
        for name, lane in self.campaign["lanes"].items():
            if lane["coverage"] == "COVERED":
                self.assertTrue(lane.get("coverage_basis"), name)
                for item in lane["coverage_basis"]:
                    self.assertIn(item["state"], {"SUPPORTED", "UNKNOWN", "SOURCE_NOT_FOUND", "NOT_APPLICABLE"})

    def test_artifact_hashes_and_cutoff_are_preserved(self):
        for artifact in self.campaign["artifacts"]:
            path = ROOT / artifact["local_path"]
            self.assertEqual(artifact["sha256"], hashlib.sha256(path.read_bytes()).hexdigest(), artifact["artifact_id"])
            self.assertEqual(artifact["byte_count"], path.stat().st_size)
        self.assertTrue(all((s.get("publication_date") or "") <= self.campaign["knowledge_cutoff"] for s in self.campaign["sources"]))

    def test_candidate_only_and_no_forbidden_frontier(self):
        self.assertTrue(all(a["status"] == "CANDIDATE" for a in self.campaign["assertions"]))
        self.assertFalse(any(e["phase"] in {"ENGINEERING_DERIVED", "ECONOMIC_DERIVED"} for e in self.campaign["epistemic_frontier"]))

    def test_blindness_record_excludes_ceres_material(self):
        blind = load_json(ROOT / "blindness_record.json")
        self.assertFalse(blind["research_phase_answer_key_access"])
        self.assertTrue(all(not Path(p).exists() for p in blind["excluded_paths_verified_absent"]))

    def test_frozen_manifest_matches_campaign(self):
        frozen = load_json(ROOT / "frozen_manifest.json")
        campaign_bytes = (ROOT / "campaign.json").read_bytes()
        self.assertEqual(frozen["campaign_sha256"], hashlib.sha256(campaign_bytes).hexdigest())
        self.assertTrue(frozen["frozen"])


if __name__ == "__main__":
    unittest.main()
