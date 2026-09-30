"""Hostile contract tests for CIVPROP Demand/Pressure V1."""
from __future__ import annotations

from types import SimpleNamespace
import unittest

from .demand_pressure_v1 import (
    DemandPressureRuntime,
    load_demand_pressure_package,
)


def _package():
    return {
        "format": "CIVPROP_DEMAND_PRESSURE_V1",
        "contract_version": "1.0.0",
        "scope": "NON_EARTH_SURFACE",
        "excluded_location_ids": ["EARTH_SURFACE"],
        "channels": [
            {
                "channel_id": "HABITAT",
                "unit": "person",
                "available_field": "habitat",
                "decay": 0.60,
                "gain": 0.24,
                "drivers": [
                    {"field": "biological_population", "coefficient": 1.0,
                     "coefficient_unit": "person/person"},
                    {"field": "transient_population", "coefficient": 1.0,
                     "coefficient_unit": "person/person"},
                ],
            },
            {
                "channel_id": "TRANSPORT",
                "unit": "scenario_capacity_unit",
                "available_field": "transport",
                "decay": 0.60,
                "gain": 0.24,
                "drivers": [
                    {"field": "transient_population", "coefficient": 0.04,
                     "coefficient_unit": "scenario_capacity_unit/person"},
                ],
            },
            {
                "channel_id": "INDUSTRIAL",
                "unit": "scenario_capacity_unit",
                "available_field": "industrial",
                "decay": 0.60,
                "gain": 0.24,
                "drivers": [
                    {"field": "workforce", "coefficient": 0.04,
                     "coefficient_unit": "scenario_capacity_unit/person"},
                ],
            },
            {
                "channel_id": "RESOURCE",
                "unit": "scenario_capacity_unit",
                "available_field": "resource",
                "decay": 0.60,
                "gain": 0.24,
                "drivers": [
                    {"field": "biological_population", "coefficient": 0.01,
                     "coefficient_unit": "scenario_capacity_unit/person"},
                    {"field": "transient_population", "coefficient": 0.01,
                     "coefficient_unit": "scenario_capacity_unit/person"},
                ],
            },
            {
                "channel_id": "POWER",
                "unit": "MW_equivalent",
                "available_field": "power",
                "decay": 0.60,
                "gain": 0.24,
                "drivers": [
                    {"field": "biological_population", "coefficient": 0.025,
                     "coefficient_unit": "MW_equivalent/person"},
                    {"field": "transient_population", "coefficient": 0.025,
                     "coefficient_unit": "MW_equivalent/person"},
                ],
            },
        ],
        "strategic_requirements": [],
        "parameter_status": "UNCALIBRATED_CAUSAL_MODEL_PARAMETER_V1",
    }


def _state(**overrides):
    values = dict(
        biological_population=0.0,
        transient_population=0.0,
        workforce=0.0,
        habitat=0.0,
        transport=0.0,
        industrial=0.0,
        resource=0.0,
        power=0.0,
        shipyard=0.0,
        capital=0.0,
    )
    values.update(overrides)
    return SimpleNamespace(**values)


class DemandPressureV1Tests(unittest.TestCase):
    def setUp(self):
        self.runtime = DemandPressureRuntime(load_demand_pressure_package(_package()))

    def test_no_state_requirement_means_no_demand_and_no_pressure(self):
        observations = self.runtime.derive(
            {"LUNA_SURFACE": _state()},
            year=2030,
        )
        self.assertTrue(observations)
        self.assertTrue(all(x.required == 0.0 for x in observations))
        self.assertTrue(all(x.unmet == 0.0 for x in observations))
        pressure = self.runtime.advance_pressure({}, observations)
        self.assertTrue(all(value == 0.0 for value in pressure.values()))

    def test_habitat_shortage_is_state_derived_and_capacity_relief_removes_new_demand(self):
        first = self.runtime.derive(
            {"EARTH_ORBIT": _state(transient_population=200.0, habitat=50.0,
                                   transport=8.0, industrial=2.0,
                                   workforce=50.0, power=5.0)},
            year=2026,
        )
        habitat = next(x for x in first if x.channel_id == "HABITAT")
        self.assertEqual(habitat.required, 200.0)
        self.assertEqual(habitat.available, 50.0)
        self.assertEqual(habitat.unmet, 150.0)
        pressure1 = self.runtime.advance_pressure({}, first)
        self.assertAlmostEqual(pressure1[("EARTH_ORBIT", "HABITAT")], 36.0)

        relieved = self.runtime.derive(
            {"EARTH_ORBIT": _state(transient_population=200.0, habitat=220.0,
                                   transport=8.0, industrial=2.0,
                                   workforce=50.0, power=5.0)},
            year=2027,
        )
        habitat2 = next(x for x in relieved if x.channel_id == "HABITAT")
        self.assertEqual(habitat2.unmet, 0.0)
        pressure2 = self.runtime.advance_pressure(pressure1, relieved)
        self.assertAlmostEqual(
            pressure2[("EARTH_ORBIT", "HABITAT")],
            pressure1[("EARTH_ORBIT", "HABITAT")] * 0.60,
        )

    def test_balanced_local_state_does_not_create_fake_congestion(self):
        observations = self.runtime.derive(
            {"EARTH_ORBIT": _state(
                transient_population=200.0,
                workforce=50.0,
                habitat=200.0,
                transport=8.0,
                industrial=2.0,
                resource=2.0,
                power=5.0,
            )},
            year=2026,
        )
        self.assertTrue(all(x.unmet == 0.0 for x in observations))

    def test_explicit_strategic_requirement_can_create_demand_without_population(self):
        package = _package()
        package["strategic_requirements"] = [{
            "requirement_id": "TEST_STRATEGIC_LOGISTICS",
            "actor_id": "AUS",
            "location_id": "LUNA_SURFACE",
            "channel_id": "TRANSPORT",
            "amount": 3.0,
            "unit": "scenario_capacity_unit",
            "valid_from_year": 2030,
            "valid_to_year": 2031,
            "provenance_refs": ["test:declared_requirement"],
        }]
        runtime = DemandPressureRuntime(load_demand_pressure_package(package))
        observations = runtime.derive({"LUNA_SURFACE": _state()}, year=2030)
        transport = next(x for x in observations if x.channel_id == "TRANSPORT")
        self.assertEqual(transport.required, 3.0)
        self.assertEqual(transport.unmet, 3.0)
        self.assertIn("strategic:TEST_STRATEGIC_LOGISTICS", transport.driver_components)

        after = runtime.derive({"LUNA_SURFACE": _state()}, year=2032)
        transport_after = next(x for x in after if x.channel_id == "TRANSPORT")
        self.assertEqual(transport_after.required, 0.0)

    def test_units_must_match_strategic_channel(self):
        package = _package()
        package["strategic_requirements"] = [{
            "requirement_id": "BAD",
            "actor_id": "AUS",
            "location_id": "LUNA_SURFACE",
            "channel_id": "TRANSPORT",
            "amount": 1.0,
            "unit": "person",
            "valid_from_year": 2030,
            "valid_to_year": None,
            "provenance_refs": ["test"],
        }]
        with self.assertRaises(ValueError):
            load_demand_pressure_package(package)

    def test_excluded_earth_surface_never_generates_offworld_demand(self):
        observations = self.runtime.derive(
            {"EARTH_SURFACE": _state(
                biological_population=8_000_000_000,
                workforce=3_000_000_000,
            )},
            year=2026,
        )
        self.assertEqual(observations, ())


if __name__ == "__main__":
    unittest.main()
