import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "v0_1" / "results"


class V01SensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid = json.loads((RESULTS / "sensitivity_grid.json").read_text())
        cls.selected = json.loads((RESULTS / "selected_scenario.json").read_text())

    def test_grid_is_exactly_three_by_three(self):
        runs = self.grid["runs"]
        self.assertEqual(9, len(runs))
        self.assertEqual(3, len({row["medical"] for row in runs}))
        self.assertEqual(3, len({row["synthetic"] for row in runs}))
        self.assertEqual(9, len({row["scenario"] for row in runs}))

    def test_all_runs_qualified(self):
        self.assertEqual("PASS", self.grid["qualification"])
        self.assertEqual([], self.grid["failures"])
        self.assertTrue(all(row["qualification"] == "PASS" for row in self.grid["runs"]))

    def test_medical_population_is_monotonic(self):
        central_synth = [row for row in self.grid["runs"] if row["synthetic"] == "SYNTH_CENTRAL"]
        values = {row["medical"]: row["biological_population"] for row in central_synth}
        self.assertLess(values["MED_CONSERVATIVE"], values["MED_CENTRAL"])
        self.assertLess(values["MED_CENTRAL"], values["MED_HIGH"])

    def test_synthetic_stock_is_monotonic(self):
        central_med = [row for row in self.grid["runs"] if row["medical"] == "MED_CENTRAL"]
        values = {row["synthetic"]: row["synthetic_population"] for row in central_med}
        self.assertLess(values["SYNTH_LOW"], values["SYNTH_CENTRAL"])
        self.assertLess(values["SYNTH_CENTRAL"], values["SYNTH_HIGH"])

    def test_middle_case_is_selected_without_endpoint_target(self):
        self.assertEqual("MED_CENTRAL__SYNTH_CENTRAL", self.selected["selection"])
        self.assertIn("parameter-middle", self.selected["selection_reason"])

    def test_allocation_repair_removes_local_small_denominator_pathology(self):
        metrics = json.loads((RESULTS / "allocation_concentration_before_after.json").read_text())
        before, after = metrics["v0_before"], metrics["v0_1_selected_after"]
        self.assertLess(after["maximum_country_synthetic_labor_share"],
                        before["maximum_country_synthetic_labor_share"])
        self.assertLess(after["maximum_country_automation_share"],
                        before["maximum_country_automation_share"])
        self.assertLess(after["synthetic"]["hhi"], before["synthetic"]["hhi"])
        self.assertLess(after["automation"]["hhi"], before["automation"]["hhi"])


if __name__ == "__main__":
    unittest.main()
