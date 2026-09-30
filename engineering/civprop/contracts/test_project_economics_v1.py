"""Contract tests for CIVPROP Project Economics V1."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from .project_economics_v1 import (
    ProjectEconomicsRuntime,
    load_project_economics_package,
)


HERE = Path(__file__).resolve().parent
PARAMETERS = HERE / "project_economics_v1.json"


class ProjectEconomicsV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(PARAMETERS.read_text())
        cls.package = load_project_economics_package(cls.raw)
        cls.runtime = ProjectEconomicsRuntime(cls.package)

    def test_default_parameter_set_has_no_method_lab_currency_or_capacity_units(self):
        text = json.dumps(self.raw, sort_keys=True)
        self.assertNotIn("scenario_credit", text)
        self.assertNotIn("scenario_capacity_unit", text)
        self.assertNotIn("METHOD_LAB_SYNTHETIC_V1", text)
        self.assertEqual(self.package.capital_unit, "USD_2026_billion")
        self.assertEqual(self.package.dimension_units["power"], "MW")
        self.assertEqual(self.package.dimension_units["habitat"], "person")
        self.assertEqual(self.package.dimension_units["transport"], "tonnes/year")

    def test_all_runtime_projects_have_versioned_parameters(self):
        expected = {
            "PROSPECTING_SURVEY",
            "LOGISTICS_NODE",
            "POWER_PLANT",
            "HABITAT",
            "RESOURCE_PLANT",
            "INDUSTRIAL_WORKSHOP",
            "SURFACE_PORT",
            "SHIPYARD",
        }
        self.assertEqual({x.project_archetype_id for x in self.package.projects}, expected)

    def test_power_output_preserves_qualified_40kw_reference_without_promoting_cost(self):
        project = next(
            x for x in self.package.projects
            if x.project_archetype_id == "POWER_PLANT"
        )
        self.assertEqual(project.outputs["power"].status, "QUALIFIED_REFERENCE")
        self.assertEqual(project.outputs["power"].nominal, 0.04)
        self.assertEqual(project.outputs["power"].unit, "MW")
        self.assertEqual(project.capital_cost.status, "SCENARIO_ASSUMPTION")

    def test_technology_epoch_changes_are_explicit_and_consumed(self):
        p2026 = self.runtime.resolve("HABITAT", year=2026)
        p2036 = self.runtime.resolve("HABITAT", year=2036)
        self.assertLess(p2036.capital_cost, p2026.capital_cost)
        self.assertGreater(
            p2036.output_capacities["habitat"],
            p2026.output_capacities["habitat"],
        )
        self.assertLessEqual(
            p2036.construction_lag_years,
            p2026.construction_lag_years,
        )

    def test_scale_behavior_is_explicit_and_non_linear_for_capital(self):
        one = self.runtime.resolve(
            "INDUSTRIAL_WORKSHOP", year=2026, scale=1.0
        )
        two = self.runtime.resolve(
            "INDUSTRIAL_WORKSHOP", year=2026, scale=2.0
        )
        self.assertAlmostEqual(
            two.capital_cost / one.capital_cost,
            2.0 ** 0.90,
            places=12,
        )
        self.assertAlmostEqual(
            two.output_capacities["industrial"]
            / one.output_capacities["industrial"],
            2.0,
            places=12,
        )

    def test_quantity_range_must_be_ordered(self):
        bad = copy.deepcopy(self.raw)
        bad["projects"][0]["capital_cost"]["low"] = 10
        bad["projects"][0]["capital_cost"]["nominal"] = 1
        with self.assertRaises(ValueError):
            load_project_economics_package(bad)

    def test_capacity_unit_must_match_dimension_contract(self):
        bad = copy.deepcopy(self.raw)
        habitat = next(
            x for x in bad["projects"]
            if x["project_archetype_id"] == "HABITAT"
        )
        habitat["outputs"]["habitat"]["unit"] = "tonnes/year"
        with self.assertRaises(ValueError):
            load_project_economics_package(bad)

    def test_dorrington_olsen_is_not_misapplied_to_lunar_facilities(self):
        boundary = next(
            x for x in self.raw["domain_model_boundaries"]
            if x["model_id"] == "DORRINGTON_OLSEN_M2"
        )
        self.assertEqual(
            boundary["use_status"],
            "NOT_APPLIED_TO_EARTH_LUNA_FACILITY_COSTS",
        )
        self.assertIn("asteroid", boundary["reason"].lower())


if __name__ == "__main__":
    unittest.main()
