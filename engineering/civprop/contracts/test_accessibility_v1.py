"""Contract tests for CIVPROP Accessibility Service V1."""
from __future__ import annotations

import copy
import unittest

from .accessibility_v1 import (
    AccessibilityRequest,
    AccessibilityRuntime,
    load_accessibility_package,
)
from .actor_state_v1 import load_actor_state_package


def _actor_state():
    return load_actor_state_package({
        "format": "CIVPROP_ACTOR_STATE_V1",
        "contract_version": "1.0.0",
        "as_of_year": 2026,
        "actors": [{
            "actor_id": "AUS",
            "actor_type": "STATE",
            "identity": {"display_name": "Australia", "provenance_refs": ["test"]},
            "budget": {
                "spendable_allocation": {
                    "status": "UNKNOWN", "amount": None, "unit": None,
                    "scope": "GENERAL", "provenance_refs": [],
                },
                "committed_funds": [],
            },
            "ownership": {"status": "UNKNOWN", "records": []},
            "operation": {"status": "UNKNOWN", "records": []},
            "access_rights": {"status": "KNOWN_RECORDS", "records": [{
                "record_id": "access", "subject_id": "ROO_VER",
                "status": "OBSERVED_SCOPED_ACCESS", "scope": "ROO_VER_ONLY",
                "provider_id": "INTUITIVE_MACHINES",
                "capability_id": "LUNAR_PAYLOAD_DELIVERY_ACCESS",
                "valid_from": 2026, "valid_to": None, "provenance_refs": ["test"],
            }]},
            "contracts": {"status": "UNKNOWN", "records": []},
            "provider_service_access": {"status": "KNOWN_RECORDS", "records": [{
                "record_id": "provider", "subject_id": "ROO_VER_WITH_NASA_MNP",
                "status": "OBSERVED_INDIRECT_PROVIDER_SERVICE_PATH",
                "scope": "NASA CLPS CT-4 / Intuitive Machines IM-5",
                "provider_id": "INTUITIVE_MACHINES",
                "capability_id": "LUNAR_PAYLOAD_DELIVERY_ACCESS",
                "valid_from": 2026, "valid_to": None,
                "provenance_refs": ["test"], "target_landing_year": 2030,
            }]},
            "installed_capability": {"status": "UNKNOWN", "records": []},
            "acquired_capability": {"status": "UNKNOWN", "records": []},
            "experience": {"status": "UNKNOWN", "records": []},
            "owned_infrastructure": {"status": "UNKNOWN", "records": []},
            "relationships": {"status": "UNKNOWN", "records": []},
        }],
        "events": [],
    }).actors[0]


def _package():
    return {
        "format": "CIVPROP_ACCESSIBILITY_V1",
        "contract_version": "1.0.0",
        "epoch_policy": "ANNUAL_REFERENCE_EPOCH_JULY_01_UTC",
        "location_bindings": [
            {"location_id": "EARTH_SURFACE", "body_id": "EARTH"},
            {"location_id": "LUNA_SURFACE", "body_id": "MOON"},
        ],
        "geometry_samples": [{
            "origin_body_id": "EARTH",
            "destination_body_id": "MOON",
            "epoch_utc": "2030-07-01T00:00:00Z",
            "straight_line_separation_km": 401540.02139136905,
            "relative_speed_km_s": 0.9836733938012038,
            "uncertainty_km": None,
            "reference_frame": "J2000/ECLIPTIC",
            "source_status": "QUALIFIED",
            "navigation_grade": True,
            "provenance_refs": ["DE440:test"],
        }],
        "service_paths": [{
            "service_id": "ROOVER_IM5",
            "actor_id": "AUS",
            "provider_id": "INTUITIVE_MACHINES",
            "subject_id": "ROO_VER_WITH_NASA_MNP",
            "origin_location_id": "EARTH_SURFACE",
            "destination_location_id": "LUNA_SURFACE",
            "mission_class": "NAMED_PAYLOAD_DELIVERY",
            "service_class": "CLPS_LUNAR_DELIVERY",
            "valid_from_year": 2026,
            "valid_to_year": None,
            "target_year": 2030,
            "status": "UNKNOWN",
            "limiting_constraints": [
                "launch window unknown",
                "transfer trajectory unknown",
            ],
            "provenance_refs": ["ROOVER:test"],
            "cost_components": [
                {"component_id": "SERVICE_PRICE", "status": "UNKNOWN",
                 "value": None, "unit": "AUD", "uncertainty": None},
                {"component_id": "TRANSFER_DURATION", "status": "UNKNOWN",
                 "value": None, "unit": "s", "uncertainty": None},
                {"component_id": "DELTA_V", "status": "UNKNOWN",
                 "value": None, "unit": "km/s", "uncertainty": None},
            ],
            "generalized_cost": {"status": "UNKNOWN", "value": None, "unit": None,
                                 "uncertainty": None},
        }],
    }


class AccessibilityV1Tests(unittest.TestCase):
    def test_geometry_is_context_not_route_length(self):
        runtime = AccessibilityRuntime(load_accessibility_package(_package()))
        result = runtime.assess(
            AccessibilityRequest(
                actor_id="AUS", origin_location_id="EARTH_SURFACE",
                destination_location_id="LUNA_SURFACE",
                epoch_utc="2030-07-01T00:00:00Z",
                mission_class="GENERIC_PROJECT_DEPLOYMENT",
                service_class="PROJECT_LOGISTICS",
            ),
            actor_state=_actor_state(), technology_state={},
        )
        self.assertEqual(result.status, "UNKNOWN")
        self.assertEqual(result.geometry.straight_line_separation_km, 401540.02139136905)
        self.assertEqual(result.geometry.distance_semantics,
                         "BODY_CENTER_STRAIGHT_LINE_CONTEXT_NOT_ROUTE_LENGTH")
        self.assertIsNone(result.generalized_cost.value)
        self.assertIn("NO_MATCHING_SCOPED_SERVICE_PATH", result.limiting_constraints)

    def test_named_scoped_service_does_not_become_end_to_end_feasible(self):
        runtime = AccessibilityRuntime(load_accessibility_package(_package()))
        result = runtime.assess(
            AccessibilityRequest(
                actor_id="AUS", origin_location_id="EARTH_SURFACE",
                destination_location_id="LUNA_SURFACE",
                epoch_utc="2030-07-01T00:00:00Z",
                mission_class="NAMED_PAYLOAD_DELIVERY",
                service_class="CLPS_LUNAR_DELIVERY",
                subject_id="ROO_VER_WITH_NASA_MNP",
            ),
            actor_state=_actor_state(), technology_state={},
        )
        self.assertEqual(result.status, "UNKNOWN")
        self.assertEqual(result.matched_service_id, "ROOVER_IM5")
        self.assertIn("launch window unknown", result.limiting_constraints)
        self.assertEqual(
            {x.component_id for x in result.generalized_cost.components},
            {"STRAIGHT_LINE_BODY_CENTER_SEPARATION", "RELATIVE_BODY_SPEED",
             "SERVICE_PRICE", "TRANSFER_DURATION", "DELTA_V"},
        )

    def test_explicit_service_conflict_is_infeasible_only_for_that_path(self):
        package = _package()
        package["service_paths"][0]["destination_location_id"] = "LUNA_SURFACE"
        runtime = AccessibilityRuntime(load_accessibility_package(package))
        result = runtime.assess(
            AccessibilityRequest(
                actor_id="AUS", origin_location_id="EARTH_SURFACE",
                destination_location_id="EARTH_SURFACE",
                epoch_utc="2030-07-01T00:00:00Z",
                mission_class="NAMED_PAYLOAD_DELIVERY",
                service_class="CLPS_LUNAR_DELIVERY",
                subject_id="ROO_VER_WITH_NASA_MNP",
                requested_service_id="ROOVER_IM5",
            ),
            actor_state=_actor_state(), technology_state={},
        )
        self.assertEqual(result.status, "INFEASIBLE")
        self.assertIn("REQUEST_OUTSIDE_NAMED_SERVICE_SCOPE", result.limiting_constraints)

    def test_unknown_cost_cannot_carry_invented_scalar(self):
        package = _package()
        package["service_paths"][0]["generalized_cost"] = {
            "status": "UNKNOWN", "value": 7.0, "unit": "scenario_credit",
            "uncertainty": None,
        }
        with self.assertRaises(ValueError):
            load_accessibility_package(package)

    def test_feasible_cost_requires_decomposed_known_components(self):
        package = _package()
        path = package["service_paths"][0]
        path["status"] = "FEASIBLE"
        path["cost_components"] = [
            {"component_id": "SERVICE_PRICE", "status": "KNOWN",
             "value": 10.0, "unit": "AUD/kg", "uncertainty": 1.0},
        ]
        path["generalized_cost"] = {
            "status": "KNOWN", "value": 10.0, "unit": "AUD/kg",
            "uncertainty": 1.0,
        }
        runtime = AccessibilityRuntime(load_accessibility_package(package))
        result = runtime.assess(
            AccessibilityRequest(
                actor_id="AUS", origin_location_id="EARTH_SURFACE",
                destination_location_id="LUNA_SURFACE",
                epoch_utc="2030-07-01T00:00:00Z",
                mission_class="NAMED_PAYLOAD_DELIVERY",
                service_class="CLPS_LUNAR_DELIVERY",
                subject_id="ROO_VER_WITH_NASA_MNP",
            ),
            actor_state=_actor_state(), technology_state={},
        )
        self.assertEqual(result.status, "FEASIBLE")
        self.assertEqual(result.generalized_cost.value, 10.0)
        self.assertEqual(result.generalized_cost.unit, "AUD/kg")


if __name__ == "__main__":
    unittest.main()
