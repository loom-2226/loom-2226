import csv
import json
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


class CandidateArtifactTests(unittest.TestCase):
    def load(self, name):
        return json.loads((RESULTS / name).read_text(encoding="utf-8"))

    def test_independent_validation_passed(self):
        report = self.load("independent_validation.json")
        self.assertEqual("PASS", report["status"])
        self.assertEqual([], report["failures"])

    def test_annual_paths_cover_2100_through_2226(self):
        years = list(range(2100, 2227))
        for name in ("annual_biological_summary.json", "annual_synthetic_summary.json",
                     "annual_labor_composition.json", "annual_economic_summary.json"):
            self.assertEqual(years, [row["year"] for row in self.load(name)])

    def test_population_categories_are_separate(self):
        bio = self.load("annual_biological_summary.json")[-1]
        synth = self.load("annual_synthetic_summary.json")[-1]
        labor = self.load("annual_labor_composition.json")[-1]
        validation = self.load("independent_validation.json")
        self.assertAlmostEqual(
            bio["population"] + synth["population"],
            validation["terminal"]["recognized_person_population"], places=5)
        self.assertNotEqual(labor["machine_task_capacity"], synth["population"])
        self.assertGreater(labor["machine_task_capacity"], 0)

    def test_labor_components_reconstruct(self):
        for row in self.load("annual_labor_composition.json"):
            self.assertTrue(math.isclose(
                row["total_effective_labor"],
                row["biological_labor"] + row["synthetic_labor"] + row["machine_task_capacity"],
                rel_tol=1e-12, abs_tol=1e-6))

    def test_demography_has_237_unique_areas(self):
        with (RESULTS / "country_demography_2226.csv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(237, len(rows))
        self.assertEqual(237, len({row["iso3"] for row in rows}))

    def test_economics_remains_80_economies(self):
        rows = self.load("countries_2226.json")
        self.assertEqual(80, len(rows))
        self.assertEqual(80, len({row["iso3"] for row in rows}))

    def test_promoted_authorities_are_comparators(self):
        comparison = self.load("COMPARISON_CURRENT_V4_TO_CANDIDATE.json")
        promoted = comparison["current_promoted_bridge_v4"]
        self.assertEqual(8312538895.185726, promoted["biological_population_2226"])
        self.assertIsNone(promoted["synthetic_population_2226"])
        self.assertNotEqual(
            promoted["biological_population_2226"],
            comparison["candidate_2226"]["biological_population"])


if __name__ == "__main__":
    unittest.main()
