"""Regression tests for the additive Earth-v4 2226 demographic correction."""

import csv
import hashlib
import json
import unittest
from pathlib import Path

from build_demographic_correction import (
    HERE,
    OUT_CSV,
    OUT_JSON,
    OUT_MANIFEST,
    build,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DemographicCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated = build()
        cls.recorded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    def test_recorded_output_reproduces_from_current_sources(self):
        self.assertEqual(self.generated, self.recorded)
        self.assertEqual(self.recorded["status"],
                         "SELECTED_2226_CANON_CONSTRAINED_COUNTRY_ALLOCATION")
        self.assertEqual(self.recorded["method"]["free_parameters_added"], 0)

    def test_country_coverage_and_parent_conservation(self):
        rows = self.recorded["countries"]
        self.assertEqual(len(rows), 237)
        self.assertEqual(len({row["iso3"] for row in rows}), 237)
        self.assertEqual(
            sum(row["allocation_class"] == "RECOVERED_V2_1_NAMED_80_RENORMALIZED"
                for row in rows), 80)
        self.assertEqual(
            sum(row["allocation_class"] == "WPP_2100_SHARE_OF_RECOVERED_V2_1_ROW_RESIDUAL"
                for row in rows), 157)
        self.assertTrue(all(row["population_2226"] > 0 for row in rows))
        total = sum(row["population_2226"] for row in rows)
        self.assertAlmostEqual(total, 8312538895.185726, places=3)
    def test_top_ten_is_stable_and_outlier_regression_is_closed(self):
        top = [row["iso3"] for row in self.recorded["top_20_population_2226"][:10]]
        self.assertEqual(top, ["IND", "CHN", "PAK", "USA", "COD",
                               "NGA", "IDN", "ETH", "BGD", "EGY"])
        by_iso = {row["iso3"]: row for row in self.recorded["countries"]}
        self.assertGreater(by_iso["CHN"]["population_2226"], 900_000_000)
        self.assertLess(by_iso["COD"]["population_2226"], 400_000_000)
        self.assertLess(by_iso["ETH"]["population_2226"], 200_000_000)
        self.assertLess(by_iso["TZA"]["population_2226"], 150_000_000)
        self.assertLess(by_iso["AGO"]["population_2226"], 100_000_000)

    def test_old_half_life_values_are_comparison_only(self):
        rows = self.recorded["countries"]
        self.assertTrue(all(
            row["population_2226"] != row["superseded_v4_diagnostic_central_population_2226"]
            for row in rows
        ))
        self.assertTrue(self.recorded["boundaries"]["does_not_select_v4_half_life_sensitivity"])
        self.assertTrue(self.recorded["boundaries"]["no_selected_2101_2225_annual_trajectory"])
    def test_csv_matches_json_population_rows(self):
        with OUT_CSV.open(encoding="utf-8", newline="") as handle:
            csv_rows = list(csv.DictReader(handle))
        self.assertEqual(len(csv_rows), 237)
        csv_by_iso = {row["iso3"]: float(row["population_2226"]) for row in csv_rows}
        json_by_iso = {row["iso3"]: row["population_2226"] for row in self.recorded["countries"]}
        self.assertEqual(csv_by_iso, json_by_iso)

    def test_manifest_pins_all_generated_inputs(self):
        manifest = json.loads(OUT_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema"],
                         "loom-earth-v4-demographic-correction-manifest-v1")
        self.assertEqual(manifest["selected_year"], 2226)
        self.assertEqual(manifest["target_baseline"],
                         "EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24")
        for item in manifest["files"].values():
            path = HERE.parents[2] / item["path"]
            self.assertTrue(path.is_file())
            self.assertEqual(sha256(path), item["sha256"])
            self.assertEqual(path.stat().st_size, item["bytes"])


if __name__ == "__main__":
    unittest.main()
