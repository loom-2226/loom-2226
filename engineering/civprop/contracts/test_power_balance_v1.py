"""Hostile tests for CIVPROP Power Balance V1."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from .demand_pressure_v1 import load_demand_pressure_package
from .power_balance_v1 import (
    PowerBalanceRuntime,
    load_power_balance_package,
)


HERE = Path(__file__).resolve().parent
POWER_PARAMETERS = HERE / "power_balance_v1.json"
SCENARIO = HERE.parent / "compiled_inputs/earth_luna_2026_2036_v1/scenario_v1.json"


def _state(*, bio=0.0, transient=0.0, power=0.0):
    return SimpleNamespace(
        biological_population=float(bio),
        transient_population=float(transient),
        workforce=0.0,
        capital=0.0,
        power=float(power),
        resource=0.0,
        industrial=0.0,
        habitat=0.0,
        shipyard=0.0,
        transport=0.0,
    )


def _facility(
    *,
    archetype="INDUSTRIAL_WORKSHOP",
    facility_id="fac-1",
    location="LUNA_SURFACE",
    power=0.0,
):
    return SimpleNamespace(
        facility_id=facility_id,
        project_archetype_id=archetype,
        location_id=location,
        owner_actor_id="AUS",
        committed_year=2026,
        commissioned_year=2030,
        status="ACTIVE",
        capital=1.0,
        capacities=SimpleNamespace(
            power=float(power),
            resource=0.0,
            industrial=100.0,
            habitat=0.0,
            shipyard=0.0,
            transport=0.0,
        ),
    )


def _known_package(
    *,
    population_average_factor=0.5,
    initial_availability=0.5,
    initial_firm=0.8,
    reserve=0.1,
    facility_peak=0.2,
    facility_average_factor=0.5,
):
    raw = json.loads(POWER_PARAMETERS.read_text())
    raw["population_average_to_peak_factor"] = {
        "status": "KNOWN",
        "value": float(population_average_factor),
        "unit": "fraction",
        "provenance_refs": ["test:population-average-factor"],
    }
    raw["initial_compatibility_generation"]["availability_factor"] = {
        "status": "KNOWN",
        "value": float(initial_availability),
        "unit": "fraction",
        "provenance_refs": ["test:initial-availability"],
    }
    raw["initial_compatibility_generation"]["firm_capacity_fraction"] = {
        "status": "KNOWN",
        "value": float(initial_firm),
        "unit": "fraction",
        "provenance_refs": ["test:initial-firm"],
    }
    raw["reserve_margin_fraction"] = {
        "status": "KNOWN",
        "value": float(reserve),
        "unit": "fraction",
        "provenance_refs": ["test:reserve"],
    }
    for model in raw["facility_load_models"]:
        if model["project_archetype_id"] == "INDUSTRIAL_WORKSHOP":
            model["peak_load_mw_per_facility"] = {
                "status": "KNOWN",
                "value": float(facility_peak),
                "unit": "MW/facility",
                "provenance_refs": ["test:facility-peak"],
            }
            model["average_to_peak_factor"] = {
                "status": "KNOWN",
                "value": float(facility_average_factor),
                "unit": "fraction",
                "provenance_refs": ["test:facility-average-factor"],
            }
    return load_power_balance_package(raw)


class PowerBalanceV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        scenario = json.loads(SCENARIO.read_text())
        cls.demand = load_demand_pressure_package(
            scenario["demand_pressure_v1"]
        )

    def test_default_boundary_uses_timeline_without_auto_unlock(self):
        package = load_power_balance_package(
            json.loads(POWER_PARAMETERS.read_text())
        )
        self.assertEqual(package.scope, "NON_EARTH_SURFACE")
        self.assertIn("EARTH_SURFACE", package.excluded_location_ids)
        self.assertEqual(package.storage_model_status, "NOT_MODELED_V1")
        self.assertFalse(package.timeline_context.auto_unlock)
        self.assertEqual(
            package.timeline_context.industrial_milestone_id,
            "ENE-MOD-INDUSTRIAL",
        )
        self.assertEqual(
            package.timeline_context.industrial_threshold_year,
            2040,
        )
        self.assertEqual(
            package.initial_compatibility_generation.availability_factor.status,
            "UNKNOWN",
        )
        self.assertEqual(package.reserve_margin_fraction.status, "UNKNOWN")

    def test_population_peak_load_reuses_power_demand_drivers_only(self):
        runtime = PowerBalanceRuntime(
            _known_package(),
            self.demand,
        )
        state, _ = runtime.step_location(
            year=2030,
            location_id="EARTH_ORBIT",
            state=_state(transient=200, power=5),
            facilities=(),
        )
        self.assertEqual(state.population_peak_load_mw, 5.0)
        self.assertEqual(state.facility_peak_load_mw, 0.0)
        self.assertEqual(state.peak_demand_mw, 5.0)
        self.assertAlmostEqual(state.average_demand_mw, 2.5)
        self.assertEqual(state.atlas_power_peak_mw, 5.0)
        self.assertEqual(state.atlas_power_average_mw, 2.5)

    def test_installed_capacity_is_not_average_generation(self):
        runtime = PowerBalanceRuntime(
            _known_package(initial_availability=0.5, initial_firm=0.8),
            self.demand,
        )
        state, _ = runtime.step_location(
            year=2030,
            location_id="EARTH_ORBIT",
            state=_state(transient=40, power=2),
            facilities=(),
        )
        self.assertEqual(state.installed_generation_capacity_mw, 2.0)
        self.assertEqual(state.average_generation_mw, 1.0)
        self.assertEqual(state.firm_generation_capacity_mw, 1.6)
        self.assertNotEqual(
            state.installed_generation_capacity_mw,
            state.average_generation_mw,
        )

    def test_unknown_availability_does_not_turn_installed_mw_into_mwh(self):
        package = load_power_balance_package(
            json.loads(POWER_PARAMETERS.read_text())
        )
        runtime = PowerBalanceRuntime(package, self.demand)
        state, flows = runtime.step_location(
            year=2030,
            location_id="EARTH_ORBIT",
            state=_state(transient=200, power=5),
            facilities=(),
        )
        self.assertEqual(state.installed_generation_capacity_mw, 5.0)
        self.assertEqual(state.peak_demand_mw, 5.0)
        self.assertIsNone(state.average_generation_mw)
        self.assertIsNone(state.average_demand_mw)
        self.assertIsNone(state.generated_energy_mwh)
        self.assertIsNone(state.consumed_energy_mwh)
        self.assertEqual(state.energy_balance_status, "UNKNOWN")
        self.assertEqual(flows, ())

    def test_facility_load_is_explicit_and_limiting_values_are_known(self):
        runtime = PowerBalanceRuntime(
            _known_package(
                population_average_factor=0.5,
                facility_peak=0.4,
                facility_average_factor=0.25,
            ),
            self.demand,
        )
        state, _ = runtime.step_location(
            year=2030,
            location_id="LUNA_SURFACE",
            state=_state(bio=10, power=1),
            facilities=(_facility(),),
        )
        self.assertAlmostEqual(state.population_peak_load_mw, 0.25)
        self.assertAlmostEqual(state.facility_peak_load_mw, 0.4)
        self.assertAlmostEqual(state.peak_demand_mw, 0.65)
        self.assertAlmostEqual(state.average_demand_mw, 0.225)
        self.assertEqual(len(state.load_components), 3)

    def test_known_surplus_closes_energy_and_emits_curtailment(self):
        runtime = PowerBalanceRuntime(
            _known_package(
                population_average_factor=0.5,
                initial_availability=0.5,
                initial_firm=1.0,
                reserve=0.0,
            ),
            self.demand,
        )
        state, flows = runtime.step_location(
            year=2030,
            location_id="EARTH_ORBIT",
            state=_state(transient=40, power=2),
            facilities=(),
        )
        # peak = 1 MW, average demand = .5 MW, generation = 1 MW
        self.assertEqual(state.energy_balance_status, "CLOSED")
        self.assertAlmostEqual(state.average_demand_mw, 0.5)
        self.assertAlmostEqual(state.average_generation_mw, 1.0)
        self.assertAlmostEqual(state.consumed_energy_mwh, 4380.0)
        self.assertAlmostEqual(state.generated_energy_mwh, 8760.0)
        self.assertAlmostEqual(state.unserved_energy_mwh, 0.0)
        self.assertAlmostEqual(state.curtailed_energy_mwh, 4380.0)
        self.assertAlmostEqual(state.energy_closure_residual_mwh, 0.0)
        self.assertEqual(
            {x.flow_type for x in flows},
            {"GENERATION", "SERVED_LOAD", "CURTAILMENT"},
        )

    def test_known_shortfall_closes_and_power_service_ratio_throttles(self):
        runtime = PowerBalanceRuntime(
            _known_package(
                population_average_factor=1.0,
                initial_availability=0.5,
                initial_firm=0.5,
                reserve=0.0,
            ),
            self.demand,
        )
        state, flows = runtime.step_location(
            year=2030,
            location_id="EARTH_ORBIT",
            state=_state(transient=40, power=1),
            facilities=(),
        )
        # demand 1 MW average/peak; available avg+firm = .5 MW
        self.assertEqual(state.energy_balance_status, "CLOSED")
        self.assertAlmostEqual(state.unserved_energy_mwh, 4380.0)
        self.assertAlmostEqual(state.energy_service_ratio, 0.5)
        self.assertAlmostEqual(state.peak_service_ratio, 0.5)
        self.assertAlmostEqual(state.power_service_ratio, 0.5)
        self.assertIn("UNSERVED_LOAD", {x.flow_type for x in flows})

    def test_power_plant_capacity_is_generation_component_not_timeline_magic(self):
        raw = json.loads(POWER_PARAMETERS.read_text())
        for model in raw["generation_models"]:
            if model["project_archetype_id"] == "POWER_PLANT":
                model["availability_factor"] = {
                    "status": "KNOWN",
                    "value": 1.0,
                    "unit": "fraction",
                    "provenance_refs": ["test:plant-availability"],
                }
                model["firm_capacity_fraction"] = {
                    "status": "KNOWN",
                    "value": 1.0,
                    "unit": "fraction",
                    "provenance_refs": ["test:plant-firm"],
                }
        raw["population_average_to_peak_factor"] = {
            "status": "KNOWN",
            "value": 1.0,
            "unit": "fraction",
            "provenance_refs": ["test:average-factor"],
        }
        raw["reserve_margin_fraction"] = {
            "status": "KNOWN",
            "value": 0.0,
            "unit": "fraction",
            "provenance_refs": ["test:reserve"],
        }
        runtime = PowerBalanceRuntime(
            load_power_balance_package(raw),
            self.demand,
        )
        plant = _facility(
            archetype="POWER_PLANT",
            facility_id="power-1",
            power=0.04,
        )
        state, _ = runtime.step_location(
            year=2045,
            location_id="LUNA_SURFACE",
            state=_state(power=0.04),
            facilities=(plant,),
        )
        self.assertEqual(state.installed_generation_capacity_mw, 0.04)
        self.assertEqual(
            [x.source_type for x in state.generation_components],
            ["FACILITY_GENERATOR"],
        )
        self.assertFalse(runtime.package.timeline_context.auto_unlock)

    def test_zero_capacity_zero_load_closes_even_with_unknown_factors(self):
        runtime = PowerBalanceRuntime(
            load_power_balance_package(
                json.loads(POWER_PARAMETERS.read_text())
            ),
            self.demand,
        )
        state, flows = runtime.step_location(
            year=2030,
            location_id="LUNA_SURFACE",
            state=_state(),
            facilities=(),
        )
        self.assertEqual(state.installed_generation_capacity_mw, 0.0)
        self.assertEqual(state.peak_demand_mw, 0.0)
        self.assertEqual(state.average_generation_mw, 0.0)
        self.assertEqual(state.average_demand_mw, 0.0)
        self.assertEqual(state.energy_balance_status, "CLOSED")
        self.assertEqual(state.generated_energy_mwh, 0.0)
        self.assertEqual(state.consumed_energy_mwh, 0.0)
        self.assertEqual(state.power_service_ratio, 1.0)
        self.assertEqual(flows, ())

    def test_earth_surface_is_out_of_scope(self):
        runtime = PowerBalanceRuntime(
            _known_package(),
            self.demand,
        )
        self.assertTrue(runtime.is_excluded("EARTH_SURFACE"))


if __name__ == "__main__":
    unittest.main()
