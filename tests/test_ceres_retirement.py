import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CeresRetirementContractTests(unittest.TestCase):
    def setUp(self):
        self.sql = (ROOT / "data/postgres/migrations/011_retire_ceres_postgres.sql").read_text()

    def test_migration_is_snapshot_scoped_and_fail_closed(self):
        self.assertIn("ceres-v1-0231e5f7da744728ab5021268b6f239b", self.sql)
        self.assertIn("Ceres retirement precondition failed", self.sql)
        self.assertIn("Ceres retirement postcondition failed", self.sql)
        self.assertNotIn("CASCADE", self.sql)
        self.assertIn("DROP VIEW loom_ceres.", self.sql)

    def test_earth_preservation_contract_has_required_surfaces(self):
        tool = (ROOT / "tools/earth_preservation.py").read_text()
        for term in ("earth_schema", "earth_data", "earth_metadata", "narrator", "overall_sha256", "--compare"):
            self.assertIn(term, tool)

    def test_retirement_archive_contract_has_required_payloads(self):
        tool = (ROOT / "tools/ceres_retirement_archive.py").read_text()
        for schema in ("loom_control", "loom_world", "loom_civ", "loom_media", "loom_ceres"):
            self.assertIn(schema, tool)
        self.assertIn("EXACT_PAYLOAD_PASS", tool)

    def test_earth_disposition_is_not_tied_to_live_ceres(self):
        earth = (ROOT / "tools/earth_temporal_pg.py").read_text()
        self.assertIn("RETIRED_FORENSIC_BASELINE", earth)
        self.assertNotIn('ceres!="VALIDATED"', earth)

    def test_pre_manifest_is_machine_readable_when_present(self):
        path = ROOT / "docs/database_semantics/EARTH_AUTHORITY_PRESERVATION_PRE_CERES_RETIREMENT.json"
        self.assertTrue(path.exists())
        data = json.loads(path.read_text())
        self.assertEqual(data["snapshot_id"], "earth-v0-1-9934d0ac-20260925")
        self.assertEqual(data["snapshot"]["state"], "VALIDATED")
        self.assertEqual(data["earth_metadata"]["rows"]["snapshot_source"][0]["snapshot_id"], data["snapshot_id"])


if __name__ == "__main__":
    unittest.main()
