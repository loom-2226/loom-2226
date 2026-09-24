import copy
import json
import math
import sys
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from model import (  # noqa: E402
    blended_normalized_weights,
    bounded_weighted_allocation,
    fertility_kernel,
    interpolate_anchors,
    labor_from_cohorts,
    machine_task_step,
    medicine_mortality_multiplier,
    propagate_one_year,
    synthetic_step,
)


class LeanSuccessorModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parameters = json.loads((PROJECT / "parameters.json").read_text())

    def test_anchor_interpolation_is_piecewise_linear_and_exact(self):
        anchors = [[2100, 0.0], [2200, 1.0], [2226, 0.5]]
        self.assertEqual(interpolate_anchors(anchors, 2100), 0.0)
        self.assertAlmostEqual(interpolate_anchors(anchors, 2150), 0.5)
        self.assertEqual(interpolate_anchors(anchors, 2226), 0.5)

    def test_fertility_kernel_sums_to_tfr_over_five_year_bins(self):
        weights = fertility_kernel(1.88, 39.0, 10.0, range(15, 75, 5))
        self.assertAlmostEqual(sum(weights.values()) * 5.0, 1.88, places=12)
        self.assertTrue(all(value >= 0 for value in weights.values()))

    def test_medicine_reduces_mortality_without_creating_immortality(self):
        p = self.parameters
        early = medicine_mortality_multiplier(100, 2100, p)
        late = medicine_mortality_multiplier(100, 2226, p)
        self.assertEqual(early, 1.0)
        self.assertGreater(late, 0.0)
        self.assertLess(late, early)

    def test_cohort_step_reconciles_births_deaths_and_population(self):
        cohorts = {sex: {age: 1000.0 for age in range(0, 160, 5)} for sex in ("M", "F")}
        q = {sex: {age: 0.01 for age in range(0, 160, 5)} for sex in ("M", "F")}
        before = sum(sum(row.values()) for row in cohorts.values())
        result = propagate_one_year(cohorts, q, 1.8, 30.0, 7.0, 0.5121951219512195)
        after = sum(sum(row.values()) for row in result["cohorts"].values())
        self.assertAlmostEqual(after, before + result["births"] - result["deaths"], places=8)
        self.assertTrue(all(value >= 0 for row in result["cohorts"].values() for value in row.values()))

    def test_biological_labor_is_bounded_by_people_and_capability(self):
        cohorts = {sex: {age: 1000.0 for age in range(0, 160, 5)} for sex in ("M", "F")}
        result = labor_from_cohorts(cohorts, 2226, self.parameters, calibration=1.0)
        population = sum(sum(row.values()) for row in cohorts.values())
        self.assertLessEqual(result["effective_biological_labor"], result["labor_capable_population"])
        self.assertLessEqual(result["effective_biological_labor"], population)
        self.assertEqual(result["under_20_labor"], 0.0)

    def test_synthetic_stock_and_labor_require_population(self):
        result = synthetic_step(
            stock=0.0,
            biological_population=1_000_000.0,
            support_index=1.0,
            year=2101,
            parameters=self.parameters,
        )
        self.assertGreater(result["population"], 0.0)
        self.assertGreaterEqual(result["effective_labor"], 0.0)
        zero = synthetic_step(0.0, 0.0, 1.0, 2101, self.parameters)
        self.assertEqual(zero["population"], 0.0)
        self.assertEqual(zero["effective_labor"], 0.0)

    def test_machine_capacity_is_not_a_person_stock(self):
        person = synthetic_step(100.0, 0.0, 1.0, 2101, self.parameters)
        machine_capacity = 500.0
        recognized_persons = 1_000.0 + person["population"]
        self.assertEqual(recognized_persons, 1_000.0 + person["population"])
        self.assertNotEqual(recognized_persons, recognized_persons + machine_capacity)

        machine = machine_task_step(0.0, 2.0, 1_000.0, self.parameters)
        self.assertGreater(machine["capacity"], 0.0)
        self.assertFalse(machine["counted_as_population"])

    def test_blended_allocation_is_normalized_and_not_intensity_only(self):
        weights = blended_normalized_weights(
            {"BIG": 90.0, "SMALL": 10.0},
            {"BIG": 1.0, "SMALL": 100.0},
            absolute_weight=0.75,
        )
        self.assertAlmostEqual(1.0, sum(weights.values()))
        self.assertGreater(weights["BIG"], weights["SMALL"])
        self.assertGreater(weights["SMALL"], 0.0)

    def test_bounded_allocation_preserves_global_capacity(self):
        allocation = bounded_weighted_allocation(
            total=12.0,
            weights={"A": 0.9, "B": 0.1},
            capacities={"A": 5.0, "B": 20.0},
        )
        self.assertAlmostEqual(12.0, sum(allocation.values()))
        self.assertLessEqual(allocation["A"], 5.0)
        self.assertLessEqual(allocation["B"], 20.0)

    def test_model_functions_are_deterministic(self):
        cohorts = {sex: {age: float(age + 10) for age in range(0, 160, 5)} for sex in ("M", "F")}
        q = {sex: {age: min(0.9, 0.0001 * (age + 1)) for age in range(0, 160, 5)} for sex in ("M", "F")}
        a = propagate_one_year(copy.deepcopy(cohorts), q, 1.8, 35.0, 8.0, 0.5121951219512195)
        b = propagate_one_year(copy.deepcopy(cohorts), q, 1.8, 35.0, 8.0, 0.5121951219512195)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
