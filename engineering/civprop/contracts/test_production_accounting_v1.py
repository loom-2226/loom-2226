"""Hostile tests for CIVPROP Production Accounting V1."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from .production_accounting_v1 import (
    ConstraintObservationV1,
    ProductionAccountingRuntime,
    load_production_accounting_package,
)


HERE = Path(__file__).resolve().parent
PARAMETERS = HERE / "production_accounting_v1.json"


def _facility(
    *,
    archetype="INDUSTRIAL_WORKSHOP",
    facility_id="fac-1",
    location="LUNA_SURFACE",
    owner="AUS",
    commissioned=2030,
    capital=1.5,
    industrial=100.0,
    resource=0.0,
):
    return SimpleNamespace(
        facility_id=facility_id,
        project_archetype_id=archetype,
        location_id=location,
        owner_actor_id=owner,
        committed_year=commissioned - 4,
        commissioned_year=commissioned,
        status="ACTIVE",
        capital=float(capital),
        capacities=SimpleNamespace(
            power=0.0,
            habitat=0.0,
            transport=0.0,
            industrial=float(industrial),
            resource=float(resource),
            shipyard=0.0,
        ),
    )


def _constraint(kind, ratio):
    return ConstraintObservationV1(
        constraint_id=kind,
        status="KNOWN",
        utilization_ratio=float(ratio),
        provenance_refs=(f"test:{kind}",),
    )


def _known_package():
    raw = json.loads(PARAMETERS.read_text())
    for model in raw["facility_models"]:
        if model["project_archetype_id"] == "INDUSTRIAL_WORKSHOP":
            for key, value in (
                ("unit_output_value", 0.002),
                ("intermediate_consumption_per_output", 0.0008),
                ("operating_cost_per_output", 0.0011),
            ):
                model["valuation"][key] = {
                    "status": "KNOWN",
                    "value": value,
                    "unit": "USD_2026_billion/tonne",
                    "provenance_refs": [f"test:{key}"],
                }
    return load_production_accounting_package(raw)


class ProductionAccountingV1Tests(unittest.TestCase):
    def test_default_boundary_covers_current_facility_archetypes(self):
        package = load_production_accounting_package(
            json.loads(PARAMETERS.read_text())
        )
        self.assertEqual(package.monetary_stock_unit, "USD_2026_billion")
        self.assertEqual(package.monetary_flow_unit, "USD_2026_billion/year")
        self.assertEqual(
            {x.project_archetype_id for x in package.facility_models},
            {
                "LOGISTICS_NODE",
                "POWER_PLANT",
                "HABITAT",
                "RESOURCE_PLANT",
                "INDUSTRIAL_WORKSHOP",
            },
        )
        self.assertTrue(
            all(
                x.valuation.unit_output_value.status == "UNKNOWN"
                for x in package.facility_models
            )
        )

    def test_unknown_required_constraint_propagates_unknown_not_zero(self):
        runtime = ProductionAccountingRuntime(_known_package())
        facility = _facility()
        state = runtime.evaluate_facility(
            year=2030,
            facility=facility,
            constraint_observations={
                "POWER": _constraint("POWER", 0.8),
                "LABOR_AUTOMATION": ConstraintObservationV1(
                    constraint_id="LABOR_AUTOMATION",
                    status="UNKNOWN",
                    utilization_ratio=None,
                    provenance_refs=("test:unknown-labor",),
                ),
                "MATERIALS": _constraint("MATERIALS", 1.0),
                "TRANSPORT": _constraint("TRANSPORT", 1.0),
            },
            resource_states=(),
        )
        self.assertEqual(state.utilization_status, "UNKNOWN")
        self.assertIsNone(state.realized_utilization)
        self.assertEqual(state.physical_output_status, "UNKNOWN")
        self.assertIsNone(state.physical_output_quantity)
        self.assertIsNone(state.gross_output)
        self.assertIsNone(state.value_added)

    def test_known_constraints_use_limiting_ratio(self):
        runtime = ProductionAccountingRuntime(_known_package())
        state = runtime.evaluate_facility(
            year=2030,
            facility=_facility(industrial=100.0),
            constraint_observations={
                "POWER": _constraint("POWER", 0.8),
                "LABOR_AUTOMATION": _constraint("LABOR_AUTOMATION", 0.6),
                "MATERIALS": _constraint("MATERIALS", 0.75),
                "TRANSPORT": _constraint("TRANSPORT", 0.9),
            },
            resource_states=(),
        )
        self.assertEqual(state.utilization_status, "KNOWN")
        self.assertAlmostEqual(state.realized_utilization, 0.6)
        self.assertEqual(state.controlling_constraint_id, "LABOR_AUTOMATION")
        self.assertAlmostEqual(state.physical_output_quantity, 60.0)
        self.assertEqual(state.physical_output_unit, "tonnes/year")

    def test_physical_output_can_be_known_while_valuation_unknown(self):
        package = load_production_accounting_package(
            json.loads(PARAMETERS.read_text())
        )
        runtime = ProductionAccountingRuntime(package)
        state = runtime.evaluate_facility(
            year=2030,
            facility=_facility(),
            constraint_observations={
                k: _constraint(k, 1.0)
                for k in (
                    "POWER",
                    "LABOR_AUTOMATION",
                    "MATERIALS",
                    "TRANSPORT",
                )
            },
            resource_states=(),
        )
        self.assertEqual(state.physical_output_status, "KNOWN")
        self.assertEqual(state.physical_output_quantity, 100.0)
        self.assertEqual(state.valuation_status, "UNKNOWN")
        self.assertIsNone(state.gross_output)
        self.assertIsNone(state.intermediate_consumption)
        self.assertIsNone(state.operating_cost)
        self.assertIsNone(state.value_added)

    def test_value_added_identity_and_operating_cost_are_distinct(self):
        runtime = ProductionAccountingRuntime(_known_package())
        state = runtime.evaluate_facility(
            year=2030,
            facility=_facility(),
            constraint_observations={
                k: _constraint(k, 1.0)
                for k in (
                    "POWER",
                    "LABOR_AUTOMATION",
                    "MATERIALS",
                    "TRANSPORT",
                )
            },
            resource_states=(),
        )
        self.assertAlmostEqual(state.physical_output_quantity, 100.0)
        self.assertAlmostEqual(state.gross_output, 0.2)
        self.assertAlmostEqual(state.intermediate_consumption, 0.08)
        self.assertAlmostEqual(state.operating_cost, 0.11)
        self.assertAlmostEqual(state.value_added, 0.12)
        self.assertNotAlmostEqual(state.value_added, state.gross_output - state.operating_cost)

    def test_zero_physical_output_has_zero_known_valuation(self):
        runtime = ProductionAccountingRuntime(_known_package())
        state = runtime.evaluate_facility(
            year=2030,
            facility=_facility(industrial=0.0),
            constraint_observations={
                k: _constraint(k, 1.0)
                for k in (
                    "POWER",
                    "LABOR_AUTOMATION",
                    "MATERIALS",
                    "TRANSPORT",
                )
            },
            resource_states=(),
        )
        self.assertEqual(state.physical_output_quantity, 0.0)
        self.assertEqual(state.gross_output, 0.0)
        self.assertEqual(state.intermediate_consumption, 0.0)
        self.assertEqual(state.operating_cost, 0.0)
        self.assertEqual(state.value_added, 0.0)

    def test_resource_output_cannot_exceed_gap8_recovered_product(self):
        runtime = ProductionAccountingRuntime(_known_package())
        facility = _facility(
            archetype="RESOURCE_PLANT",
            resource=100.0,
            industrial=25.0,
            capital=3.0,
        )
        resource_state = SimpleNamespace(
            year=2030,
            location_id="LUNA_SURFACE",
            resource_id="MOON_POLAR_WATER",
            recovered_product_tonnes=40.0,
        )
        state = runtime.evaluate_facility(
            year=2030,
            facility=facility,
            constraint_observations={
                "POWER": _constraint("POWER", 1.0),
                "LABOR_AUTOMATION": _constraint("LABOR_AUTOMATION", 1.0),
                "TRANSPORT": _constraint("TRANSPORT", 1.0),
            },
            resource_states=(resource_state,),
        )
        self.assertLessEqual(state.physical_output_quantity, 40.0)
        self.assertLessEqual(state.physical_output_quantity, 100.0)

    def test_multiple_resource_plants_share_aggregate_gap8_product_without_double_count(self):
        runtime = ProductionAccountingRuntime(_known_package())
        facilities = (
            _facility(
                archetype="RESOURCE_PLANT",
                facility_id="resource-1",
                resource=100.0,
                industrial=25.0,
                capital=3.0,
            ),
            _facility(
                archetype="RESOURCE_PLANT",
                facility_id="resource-2",
                resource=100.0,
                industrial=25.0,
                capital=3.0,
            ),
        )
        resource_state = SimpleNamespace(
            year=2030,
            location_id="LUNA_SURFACE",
            resource_id="MOON_POLAR_WATER",
            recovered_product_tonnes=100.0,
        )
        constraints = {
            "POWER": _constraint("POWER", 1.0),
            "LABOR_AUTOMATION": _constraint("LABOR_AUTOMATION", 1.0),
            "TRANSPORT": _constraint("TRANSPORT", 1.0),
        }
        states = tuple(
            runtime.evaluate_facility(
                year=2030,
                facility=facility,
                constraint_observations=constraints,
                resource_states=(resource_state,),
                peer_facilities=facilities,
            )
            for facility in facilities
        )
        self.assertEqual(
            [x.physical_output_ceiling for x in states],
            [50.0, 50.0],
        )
        self.assertAlmostEqual(
            sum(x.physical_output_quantity for x in states),
            100.0,
        )

    def test_commissioning_investment_and_gross_capital_have_no_depreciation(self):
        runtime = ProductionAccountingRuntime(_known_package())
        facility = _facility(commissioned=2030, capital=1.5)
        first = runtime.evaluate_facility(
            year=2030,
            facility=facility,
            constraint_observations={},
            resource_states=(),
        )
        later = runtime.evaluate_facility(
            year=2031,
            facility=facility,
            constraint_observations={},
            resource_states=(),
        )
        self.assertEqual(first.opening_gross_productive_capital, 0.0)
        self.assertEqual(first.commissioned_investment, 1.5)
        self.assertEqual(first.closing_gross_productive_capital, 1.5)
        self.assertEqual(later.opening_gross_productive_capital, 1.5)
        self.assertEqual(later.commissioned_investment, 0.0)
        self.assertEqual(later.closing_gross_productive_capital, 1.5)

    def test_aggregate_reconciles_facility_sector_location_and_body(self):
        runtime = ProductionAccountingRuntime(_known_package())
        constraints = {
            k: _constraint(k, 1.0)
            for k in (
                "POWER",
                "LABOR_AUTOMATION",
                "MATERIALS",
                "TRANSPORT",
            )
        }
        states = tuple(
            runtime.evaluate_facility(
                year=2030,
                facility=_facility(
                    facility_id=f"fac-{i}",
                    capital=1.5,
                    industrial=100.0,
                ),
                constraint_observations=constraints,
                resource_states=(),
            )
            for i in (1, 2)
        )
        sectors, locations, bodies = runtime.aggregate(
            year=2030,
            facility_states=states,
            location_to_body={"LUNA_SURFACE": "MOON"},
        )
        self.assertEqual(len(sectors), 1)
        self.assertEqual(len(locations), 1)
        self.assertEqual(len(bodies), 1)
        sector = sectors[0]
        location = locations[0]
        body = bodies[0]
        self.assertAlmostEqual(sector.physical_output_quantity, 200.0)
        self.assertAlmostEqual(sector.gross_output, 0.4)
        self.assertAlmostEqual(sector.value_added, 0.24)
        self.assertAlmostEqual(sector.commissioned_investment, 3.0)
        self.assertAlmostEqual(sector.closing_gross_productive_capital, 3.0)
        self.assertAlmostEqual(location.gross_output, sector.gross_output)
        self.assertAlmostEqual(body.gross_output, sector.gross_output)

    def test_invalid_constraint_ratio_fails_closed(self):
        with self.assertRaises(ValueError):
            ConstraintObservationV1(
                constraint_id="POWER",
                status="KNOWN",
                utilization_ratio=1.01,
                provenance_refs=("test:bad",),
            )


if __name__ == "__main__":
    unittest.main()
