"""Contract tests for CIVPROP Actor State / Budget V1."""
from __future__ import annotations

import unittest

from .actor_state_v1 import (
    ActorStateRuntime,
    load_actor_state_package,
)


def fixture():
    return {
        "format": "CIVPROP_ACTOR_STATE_V1",
        "contract_version": "1.0.0",
        "as_of_year": 2026,
        "actors": [
            {
                "actor_id": "AUS",
                "actor_type": "STATE",
                "identity": {
                    "display_name": "Australia",
                    "provenance_refs": ["earth_area:AUS"],
                },
                "budget": {
                    "spendable_allocation": {
                        "status": "UNKNOWN",
                        "amount": None,
                        "unit": None,
                        "scope": "GENERAL_CIVPROP_PROJECT_DECISION_BUDGET",
                        "provenance_refs": [],
                    },
                    "committed_funds": [
                        {
                            "commitment_id": "ROOVER_42M",
                            "status": "OBSERVED_COMMITTED",
                            "amount": 42000000,
                            "unit": "AUD",
                            "scope": "ROO_VER_DEVELOPMENT_BUILD_OPERATION",
                            "provenance_refs": ["AUS_GOV_2025_08_29_ROO_VER_MISSION"],
                        }
                    ],
                },
                "ownership": {"status": "UNKNOWN", "records": []},
                "operation": {"status": "KNOWN_RECORDS", "records": []},
                "access_rights": {
                    "status": "KNOWN_RECORDS",
                    "records": [
                        {
                            "record_id": "ROOVER_CLPS_ACCESS",
                            "subject_id": "ROO_VER",
                            "status": "OBSERVED_SCOPED_ACCESS",
                            "scope": "ROO_VER_CLPS_CT4_ONLY",
                            "counterparty_id": "NASA",
                            "provider_id": "INTUITIVE_MACHINES",
                            "valid_from": 2026,
                            "valid_to": None,
                            "provenance_refs": ["NASA_2026_03_27_CLPS_CT4_ROO_VER"],
                        }
                    ],
                },
                "contracts": {"status": "UNKNOWN", "records": []},
                "provider_service_access": {"status": "KNOWN_RECORDS", "records": []},
                "installed_capability": {"status": "UNKNOWN", "records": []},
                "acquired_capability": {"status": "UNKNOWN", "records": []},
                "experience": {"status": "UNKNOWN", "records": []},
                "owned_infrastructure": {"status": "UNKNOWN", "records": []},
                "relationships": {"status": "KNOWN_RECORDS", "records": []},
            }
        ],
        "events": [],
    }


class ActorStateV1Tests(unittest.TestCase):
    def test_unknown_spendable_budget_is_not_zero_or_macro_capital(self):
        package = load_actor_state_package(fixture())
        runtime = ActorStateRuntime(package)
        budget = runtime.budget("AUS", 2026)
        self.assertEqual(budget.status, "UNKNOWN")
        self.assertIsNone(budget.amount)
        self.assertIsNone(budget.unit)
        self.assertEqual(runtime.committed_funds("AUS")[0].amount, 42000000)
        self.assertEqual(runtime.committed_funds("AUS")[0].unit, "AUD")

    def test_budget_becomes_known_only_through_auditable_allocation_event(self):
        data = fixture()
        data["events"] = [
            {
                "event_id": "ALLOC_2030",
                "year": 2030,
                "actor_id": "AUS",
                "event_type": "BUDGET_ALLOCATION_SET",
                "payload": {
                    "amount": 12,
                    "unit": "scenario_credit",
                    "scope": "GENERAL_CIVPROP_PROJECT_DECISION_BUDGET",
                },
                "provenance": {
                    "class": "CIVPROP_SIMULATED_EVENT",
                    "ref": "test:ALLOC_2030",
                },
            }
        ]
        runtime = ActorStateRuntime(load_actor_state_package(data))
        self.assertEqual(runtime.budget("AUS", 2029).status, "UNKNOWN")
        b = runtime.budget("AUS", 2030)
        self.assertEqual(b.status, "KNOWN")
        self.assertEqual(b.amount, 12)
        self.assertEqual(b.unit, "scenario_credit")

    def test_capability_does_not_come_from_access_and_changes_only_by_event(self):
        data = fixture()
        runtime = ActorStateRuntime(load_actor_state_package(data))
        self.assertEqual(
            runtime.capability_status("AUS", "LUNAR_SURFACE_OPERATIONS", 2026),
            "UNKNOWN",
        )
        data["events"] = [
            {
                "event_id": "CAP_2031",
                "year": 2031,
                "actor_id": "AUS",
                "event_type": "CAPABILITY_SET",
                "payload": {
                    "capability_id": "LUNAR_SURFACE_OPERATIONS",
                    "status": "USABLE",
                    "scope": "GENERIC_ENGINE_CAPABILITY",
                },
                "provenance": {
                    "class": "CIVPROP_SIMULATED_EVENT",
                    "ref": "test:CAP_2031",
                },
            }
        ]
        runtime = ActorStateRuntime(load_actor_state_package(data))
        self.assertEqual(
            runtime.capability_status("AUS", "LUNAR_SURFACE_OPERATIONS", 2030),
            "UNKNOWN",
        )
        self.assertEqual(
            runtime.capability_status("AUS", "LUNAR_SURFACE_OPERATIONS", 2031),
            "USABLE",
        )

    def test_fact_collections_preserve_unknown_distinct_from_known_none(self):
        data = fixture()
        data["actors"][0]["ownership"] = {"status": "KNOWN_NONE", "records": []}
        package = load_actor_state_package(data)
        actor = package.actors[0]
        self.assertEqual(actor.ownership.status, "KNOWN_NONE")
        self.assertEqual(actor.contracts.status, "UNKNOWN")

    def test_unproven_negative_or_invalid_budget_is_rejected(self):
        data = fixture()
        data["actors"][0]["budget"]["spendable_allocation"] = {
            "status": "KNOWN",
            "amount": -1,
            "unit": "scenario_credit",
            "scope": "GENERAL_CIVPROP_PROJECT_DECISION_BUDGET",
            "provenance_refs": ["bad"],
        }
        with self.assertRaises(ValueError):
            load_actor_state_package(data)


if __name__ == "__main__":
    unittest.main()
