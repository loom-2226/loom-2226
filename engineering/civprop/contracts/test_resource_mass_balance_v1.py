"""Hostile tests for CIVPROP Resource Mass Balance V1."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from .resource_mass_balance_v1 import (
    ResourceMassBalanceRuntime,
    load_resource_mass_balance_package,
    load_resource_physical_realization,
)


HERE = Path(__file__).resolve().parent
PARAMETERS = HERE / "resource_mass_balance_v1.json"


def _physical(
    *,
    realization_status="KNOWN",
    stock_status="KNOWN",
    stock=1000.0,
    grade_status="KNOWN",
    grade=0.2,
    inventory_status="KNOWN",
    inventory=0.0,
):
    return load_resource_physical_realization(
        {
            "format": "CIVPROP_RESOURCE_PHYSICAL_REALIZATION_V1",
            "contract_version": "1.0.0",
            "resources": [
                {
                    "resource_id": "MOON_POLAR_WATER",
                    "location_id": "LUNA_SURFACE",
                    "realization_status": realization_status,
                    "stock_status": stock_status,
                    "opening_stock_tonnes": stock,
                    "grade_status": grade_status,
                    "grade_mass_fraction": grade,
                    "inventory_status": inventory_status,
                    "opening_inventory_tonnes": inventory,
                    "provenance_refs": ["test:physical-realization"],
                }
            ],
        }
    )


def _known_package(*, extraction_capacity=1000.0, recovery=0.5):
    raw = json.loads(PARAMETERS.read_text())
    process = raw["process_models"][0]
    process["extraction_feed_capacity_per_facility"] = {
        "status": "KNOWN",
        "value": float(extraction_capacity),
        "unit": "tonnes/year",
        "provenance_refs": ["test:extraction-capacity"],
    }
    process["recovery_fraction"] = {
        "status": "KNOWN",
        "value": float(recovery),
        "unit": "fraction",
        "provenance_refs": ["test:recovery"],
    }
    process["parameter_status"] = "SYNTHETIC_TEST_PARAMETERIZATION"
    return load_resource_mass_balance_package(raw)


def _facility(*, capacity=100.0, facility_id="fac-test"):
    capacities = SimpleNamespace(resource=float(capacity))
    return SimpleNamespace(
        facility_id=facility_id,
        project_archetype_id="RESOURCE_PLANT",
        location_id="LUNA_SURFACE",
        status="ACTIVE",
        capacities=capacities,
    )


class ResourceMassBalanceV1Tests(unittest.TestCase):
    def test_default_boundary_preserves_unquantified_evidence_and_unknown_process(self):
        package = load_resource_mass_balance_package(
            json.loads(PARAMETERS.read_text())
        )
        resource = package.resources[0]
        process = package.process_models[0]
        self.assertEqual(resource.evidence_state, "PRESENT_UNQUANTIFIED")
        self.assertEqual(resource.region_id, "MOON_POLAR_PSR")
        self.assertEqual(
            process.extraction_feed_capacity_per_facility.status,
            "UNKNOWN",
        )
        self.assertIsNone(
            process.extraction_feed_capacity_per_facility.value
        )
        self.assertEqual(process.recovery_fraction.status, "UNKNOWN")
        self.assertIsNone(process.recovery_fraction.value)

    def test_unknown_abundance_remains_unknown_not_zero(self):
        package = _known_package()
        physical = _physical(
            realization_status="UNKNOWN",
            stock_status="UNKNOWN",
            stock=None,
            grade_status="UNKNOWN",
            grade=None,
            inventory_status="UNKNOWN",
            inventory=None,
        )
        runtime = ResourceMassBalanceRuntime(package, physical)
        states, flows = runtime.step(
            year=2030,
            facilities=(_facility(),),
        )
        state = states[0]
        self.assertEqual(state.production_status, "PHYSICAL_STATE_UNKNOWN")
        self.assertIsNone(state.opening_stock_tonnes)
        self.assertIsNone(state.grade_mass_fraction)
        self.assertIsNone(state.extracted_feed_tonnes)
        self.assertIsNone(state.recovered_product_tonnes)
        self.assertIsNone(state.closing_stock_tonnes)
        self.assertEqual(flows, ())

    def test_no_facility_means_zero_extraction_but_does_not_change_stock(self):
        runtime = ResourceMassBalanceRuntime(
            _known_package(),
            _physical(),
        )
        states, flows = runtime.step(year=2026, facilities=())
        state = states[0]
        self.assertEqual(
            state.production_status,
            "NO_ACTIVE_PROCESS_CAPACITY",
        )
        self.assertEqual(state.extracted_feed_tonnes, 0.0)
        self.assertEqual(state.recovered_product_tonnes, 0.0)
        self.assertEqual(state.opening_stock_tonnes, 1000.0)
        self.assertEqual(state.closing_stock_tonnes, 1000.0)
        self.assertEqual(flows, ())

    def test_known_chain_conserves_stock_recovery_tailings_and_inventory(self):
        runtime = ResourceMassBalanceRuntime(
            _known_package(extraction_capacity=1000.0, recovery=0.5),
            _physical(stock=1000.0, grade=0.2, inventory=0.0),
        )
        states, flows = runtime.step(
            year=2030,
            facilities=(_facility(capacity=100.0),),
        )
        state = states[0]
        self.assertEqual(state.production_status, "DEPLETED")
        self.assertAlmostEqual(state.extracted_feed_tonnes, 1000.0)
        self.assertAlmostEqual(state.contained_resource_tonnes, 200.0)
        self.assertAlmostEqual(state.recovered_product_tonnes, 100.0)
        self.assertAlmostEqual(
            state.unrecovered_contained_tonnes,
            100.0,
        )
        self.assertAlmostEqual(state.process_tailings_tonnes, 900.0)
        self.assertAlmostEqual(state.closing_stock_tonnes, 0.0)
        self.assertAlmostEqual(state.closing_inventory_tonnes, 100.0)
        self.assertEqual(
            {x.flow_type for x in flows},
            {"EXTRACTED_FEED", "RECOVERED_PRODUCT", "PROCESS_TAILINGS"},
        )

    def test_processing_capacity_constrains_extraction_and_product(self):
        runtime = ResourceMassBalanceRuntime(
            _known_package(extraction_capacity=5000.0, recovery=0.5),
            _physical(stock=5000.0, grade=0.2, inventory=0.0),
        )
        state = runtime.step(
            year=2030,
            facilities=(_facility(capacity=25.0),),
        )[0][0]
        self.assertAlmostEqual(state.extracted_feed_tonnes, 250.0)
        self.assertAlmostEqual(state.recovered_product_tonnes, 25.0)
        self.assertLessEqual(
            state.recovered_product_tonnes,
            state.processing_product_capacity_tpy,
        )

    def test_extraction_capacity_constrains_feed(self):
        runtime = ResourceMassBalanceRuntime(
            _known_package(extraction_capacity=100.0, recovery=0.5),
            _physical(stock=5000.0, grade=0.2, inventory=0.0),
        )
        state = runtime.step(
            year=2030,
            facilities=(_facility(capacity=1000.0),),
        )[0][0]
        self.assertAlmostEqual(state.extracted_feed_tonnes, 100.0)
        self.assertAlmostEqual(state.recovered_product_tonnes, 10.0)

    def test_depletion_constrains_future_production(self):
        runtime = ResourceMassBalanceRuntime(
            _known_package(extraction_capacity=1000.0, recovery=1.0),
            _physical(stock=150.0, grade=0.5, inventory=0.0),
        )
        first = runtime.step(
            year=2030,
            facilities=(_facility(capacity=100.0),),
        )[0][0]
        second = runtime.step(
            year=2031,
            facilities=(_facility(capacity=100.0),),
        )[0][0]
        self.assertEqual(first.closing_stock_tonnes, 0.0)
        self.assertEqual(first.recovered_product_tonnes, 75.0)
        self.assertEqual(second.opening_stock_tonnes, 0.0)
        self.assertEqual(second.extracted_feed_tonnes, 0.0)
        self.assertEqual(second.recovered_product_tonnes, 0.0)
        self.assertEqual(second.production_status, "DEPLETED")

    def test_inventory_sinks_must_close_and_cannot_overdraw(self):
        runtime = ResourceMassBalanceRuntime(
            _known_package(extraction_capacity=100.0, recovery=1.0),
            _physical(stock=1000.0, grade=0.5, inventory=10.0),
        )
        key = ("MOON_POLAR_WATER", "LUNA_SURFACE")
        state, flows = runtime.step(
            year=2030,
            facilities=(_facility(capacity=100.0),),
            consumption_tonnes={key: 20.0},
            outbound_tonnes={key: 5.0},
        )
        state = state[0]
        self.assertEqual(state.recovered_product_tonnes, 50.0)
        self.assertEqual(state.closing_inventory_tonnes, 35.0)
        self.assertEqual(
            {x.flow_type for x in flows},
            {
                "EXTRACTED_FEED",
                "RECOVERED_PRODUCT",
                "PROCESS_TAILINGS",
                "INVENTORY_CONSUMPTION",
                "INVENTORY_OUTBOUND",
            },
        )

        fresh = ResourceMassBalanceRuntime(
            _known_package(extraction_capacity=100.0, recovery=1.0),
            _physical(stock=1000.0, grade=0.5, inventory=0.0),
        )
        with self.assertRaises(ValueError):
            fresh.step(
                year=2030,
                facilities=(_facility(capacity=100.0),),
                consumption_tonnes={key: 60.0},
            )

    def test_duplicate_process_scope_fails_closed(self):
        raw = json.loads(PARAMETERS.read_text())
        duplicate = copy.deepcopy(raw["process_models"][0])
        duplicate["process_model_id"] = "DUPLICATE_PROCESS_MODEL"
        raw["process_models"].append(duplicate)
        with self.assertRaises(ValueError):
            load_resource_mass_balance_package(raw)

    def test_invalid_recovery_and_grade_fail_closed(self):
        raw = json.loads(PARAMETERS.read_text())
        raw["process_models"][0]["recovery_fraction"] = {
            "status": "KNOWN",
            "value": 1.01,
            "unit": "fraction",
            "provenance_refs": ["test:bad"],
        }
        with self.assertRaises(ValueError):
            load_resource_mass_balance_package(raw)

        with self.assertRaises(ValueError):
            _physical(grade=1.01)

    def test_evidence_presence_does_not_create_physical_inventory(self):
        package = load_resource_mass_balance_package(
            json.loads(PARAMETERS.read_text())
        )
        physical = _physical(
            realization_status="UNKNOWN",
            stock_status="UNKNOWN",
            stock=None,
            grade_status="UNKNOWN",
            grade=None,
            inventory_status="UNKNOWN",
            inventory=None,
        )
        runtime = ResourceMassBalanceRuntime(package, physical)
        state = runtime.step(year=2026, facilities=())[0][0]
        self.assertEqual(package.resources[0].evidence_state, "PRESENT_UNQUANTIFIED")
        self.assertIsNone(state.opening_stock_tonnes)
        self.assertIsNone(state.grade_mass_fraction)
        self.assertIsNone(state.closing_stock_tonnes)


if __name__ == "__main__":
    unittest.main()
