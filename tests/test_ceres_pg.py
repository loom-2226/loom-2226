"""Ceres development PostgreSQL migration and parity tests; no service mutation."""
from __future__ import annotations

import importlib.util
import json
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ceres_pg", ROOT / "tools/ceres_pg.py")
ceres_pg = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ceres_pg)


class CeresPostgresUnitTests(unittest.TestCase):
    def test_earth_qualification_no_longer_requires_live_ceres_snapshot(self):
        text = (ROOT / "tools/earth_temporal_pg.py").read_text()
        self.assertIn("RETIRED_FORENSIC_BASELINE", text)
        self.assertNotIn('ceres!="VALIDATED"', text)

    def test_copy_encoding_preserves_null_literal_and_binary(self):
        self.assertEqual(ceres_pg.copy_cell(None), r"\N")
        self.assertEqual(ceres_pg.copy_cell(r"\N"), r'"\N"')
        self.assertEqual(ceres_pg.copy_cell('a,"b"\n'), '"a,""b""\n"')
        self.assertEqual(ceres_pg.copy_cell(b"\x00\xff"), r'"\x00ff"')

    def test_source_contract_is_exact_and_ceres_selection_keeps_legacy_dimensions(self):
        spec = ceres_pg.contract()
        media = Path(os.environ.get("CERES_PG_MEDIA_DB", ceres_pg.SOURCE_PATHS["MEDIA"]))
        if not media.is_file():
            self.skipTest("Hash-pinned MEDIA release asset not staged")
        paths = {**ceres_pg.SOURCE_PATHS, "MEDIA": media}
        self.assertEqual(ceres_pg.validate_inputs(spec, paths), spec["source_sha256"])
        selected, manifest = ceres_pg.selected_rows(spec, paths)
        self.assertEqual(len(manifest), 5)
        self.assertEqual(len(selected[("MEDIA", "media_assets")]), 6)
        self.assertEqual(len(selected[("CIVSTATE", "civ_influence_edge")]), 55)
        self.assertEqual(sum(r["influence_domain"] == "HISTORICAL_LINEAGE"
                             for r in selected[("CIVSTATE", "civ_influence_edge")]), 30)
        self.assertEqual(len(selected[("CIVSTATE", "civ_census_node_relation")]), 11)
        self.assertEqual(len(selected[("CIVSTATE", "civ_social_pressure")]), 40)
        self.assertEqual(len(selected[("CIVSTATE", "civ_subject")]), 349)
        self.assertEqual(sum(len(rows) for rows in selected.values()), 518)

    def test_existing_coverage_has_no_silent_field_or_identity_omission(self):
        path = ROOT / "docs/database_semantics/LOOM_CERES_POSTGRES_DEV_COVERAGE_v0.1.json"
        if not path.is_file():
            self.skipTest("Development PostgreSQL coverage report not yet generated")
        report = json.loads(path.read_text())
        self.assertEqual(report["status"], "PASS")
        self.assertFalse(report["discrepancies"])
        self.assertEqual(sum(len(t["columns"]) for t in report["tables"]), 279)
        self.assertEqual(sum(len(v["columns"]) for v in report["views"]), 50)
        self.assertTrue(all(c["exact_values_match"] for t in report["tables"] for c in t["columns"]))
        self.assertTrue(all(c["exact_values_match"] for v in report["views"] for c in v["columns"]))
        self.assertTrue(all(c["postgres_column"].startswith(t["postgres_table"] + ".")
                            for t in report["tables"] for c in t["columns"]))
        self.assertTrue(all(c["postgres_column"].startswith(v["postgres_view"] + ".")
                            for v in report["views"] for c in v["columns"]))
        self.assertEqual(len(report["consumed_identities"]), 117)
        self.assertTrue(all(x["value_or_expression_parity"] for x in report["consumed_identities"]))
        self.assertEqual(report["row_lineage"]["all_rows"], 534)
        self.assertTrue(report["referential_integrity"]["all_validated"])


@unittest.skipUnless(os.environ.get("CERES_RETIREMENT_INTEGRATION") == "1", "Requires disposable cleaned PostgreSQL")
class CeresPostgresIntegrationTests(unittest.TestCase):
    def test_cleaned_database_has_no_operational_ceres_snapshot(self):
        database = os.environ.get("CERES_RETIREMENT_DB", "loom_dev")
        result = ceres_pg.psql(database, "SELECT count(*) FROM loom_control.snapshot WHERE snapshot_id='ceres-v1-0231e5f7da744728ab5021268b6f239b'")
        self.assertEqual(result, "0")


if __name__ == "__main__":
    unittest.main()
