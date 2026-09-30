"""Contract tests for CIVPROP Infrastructure Archetype V1.

Tests are intentionally written before the contract/catalog implementation.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

from .infrastructure_v1 import (
    ALLOWED_PLACEMENTS,
    CAPACITY_DIMENSIONS,
    PARAMETER_STATUS_METHOD_LAB,
    load_infrastructure_catalog,
    validate_infrastructure_catalog,
)


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
CATALOG = HERE / "infrastructure_archetypes_v1.json"
METHOD_LAB_SCENARIO = REPO_ROOT / "engineering/civprop/method_lab/scenario_v1.json"


class InfrastructureArchetypeV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_infrastructure_catalog(CATALOG)
        cls.method_lab = json.loads(METHOD_LAB_SCENARIO.read_text())

    def test_catalog_validates(self):
        validate_infrastructure_catalog(self.catalog)

    def test_v1_families_cover_atlas_infrastructure_spine(self):
        self.assertEqual(
            {a.family for a in self.catalog.archetypes},
            {
                "TRANSPORT",
                "POWER",
                "HABITAT",
                "RESOURCE",
                "MANUFACTURING",
                "SHIPYARD",
            },
        )

    def test_archetypes_are_semantics_not_economics(self):
        raw = json.loads(CATALOG.read_text())
        for archetype in raw["archetypes"]:
            self.assertNotIn("capital_cost", archetype)
            self.assertNotIn("construction_lag_years", archetype)
            self.assertNotIn("output_capacities", archetype)
            self.assertNotIn("minimum_input_capacities", archetype)

    def test_all_archetypes_have_explicit_placement_and_capacity_roles(self):
        for archetype in self.catalog.archetypes:
            self.assertTrue(archetype.allowed_placements)
            self.assertTrue(set(archetype.allowed_placements) <= ALLOWED_PLACEMENTS)
            self.assertTrue(archetype.output_capacity_dimensions)
            self.assertTrue(
                set(archetype.output_capacity_dimensions) <= CAPACITY_DIMENSIONS
            )
            self.assertTrue(
                set(archetype.input_capacity_dimensions) <= CAPACITY_DIMENSIONS
            )

    def test_method_lab_parameter_set_preserves_existing_assumptions_exactly(self):
        expected = {
            x["project_archetype_id"]: x
            for x in self.method_lab["project_archetypes"]
            if x["project_kind"] == "FACILITY"
        }
        observed = {
            p.archetype_id: p
            for p in self.catalog.parameterizations
            if p.parameter_status == PARAMETER_STATUS_METHOD_LAB
        }
        self.assertEqual(set(observed), set(expected))

        for archetype_id, old in expected.items():
            p = observed[archetype_id]
            self.assertEqual(p.capital_cost, old["capital_cost"])
            self.assertEqual(p.capital_unit, "scenario_credit")
            self.assertEqual(
                p.construction_lag_years,
                old["construction_lag_years"],
            )
            self.assertEqual(
                dict(p.minimum_input_capacities),
                {
                    key: float(value)
                    for key, value in old["minimum_input_capacities"].items()
                },
            )
            self.assertEqual(
                dict(p.output_capacities),
                {
                    key: float(value)
                    for key, value in old["output_capacities"].items()
                },
            )

    def test_prospecting_mission_is_not_in_infrastructure_catalog(self):
        self.assertNotIn(
            "PROSPECTING_SURVEY",
            {a.archetype_id for a in self.catalog.archetypes},
        )

    def test_new_atlas_spine_modules_are_semantic_not_fake_calibrated(self):
        shipyard = self.catalog.by_id("SHIPYARD")
        self.assertEqual(shipyard.family, "SHIPYARD")
        self.assertEqual(set(shipyard.allowed_placements), {"ORBITAL", "FREE_SPACE"})
        self.assertIn("shipyard", shipyard.output_capacity_dimensions)

        surface_port = self.catalog.by_id("SURFACE_PORT")
        self.assertEqual(surface_port.family, "TRANSPORT")
        self.assertEqual(surface_port.allowed_placements, ("SURFACE",))
        self.assertIn("transport", surface_port.output_capacity_dimensions)

        parameterized = {p.archetype_id for p in self.catalog.parameterizations}
        self.assertNotIn("SHIPYARD", parameterized)
        self.assertNotIn("SURFACE_PORT", parameterized)

    def test_catalog_does_not_hard_code_ceres_answer_sheet(self):
        text = CATALOG.read_text()
        for forbidden in (
            "CER-P01",
            "CER-P02",
            "CER-P03",
            "CER-P04",
            "CER-P05",
            "Occator",
            "Ceres Belt Exchange",
            "Ceres Shipyard Arc",
        ):
            self.assertNotIn(forbidden, text)

    def test_archetype_ids_are_stable_generic_modules(self):
        self.assertEqual(
            {a.archetype_id for a in self.catalog.archetypes},
            {
                "SURFACE_PORT",
                "LOGISTICS_NODE",
                "POWER_PLANT",
                "HABITAT",
                "RESOURCE_PLANT",
                "INDUSTRIAL_WORKSHOP",
                "SHIPYARD",
            },
        )

    def test_resource_v1_is_explicitly_surface_only(self):
        resource = self.catalog.by_id("RESOURCE_PLANT")
        self.assertEqual(resource.allowed_placements, ("SURFACE",))

    def test_parameterizations_have_scope_and_provenance(self):
        for p in self.catalog.parameterizations:
            self.assertTrue(p.scope)
            self.assertTrue(p.provenance_ref)
            self.assertGreater(p.capital_cost, 0)
            self.assertGreaterEqual(p.construction_lag_years, 1)


if __name__ == "__main__":
    unittest.main()
