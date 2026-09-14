#!/usr/bin/env python3
from __future__ import annotations

"""Authored E1 initial configuration lock for the Ceres→Neptune scenario.

These values are scenario initial conditions, not recovered empirical facts and not
physics-derived outputs. Domain membership remains derived-only and is intentionally
not authored here.
"""

import json
from typing import Any

from engineering.experience_one.qualification.e1_runtime_configuration_input import (
    DeployableStructureState,
    ExternalAttachmentState,
    LaunchAttachmentState,
    RuntimeConfigurationInput,
)

SCHEMA = "LOOM_E1_INITIAL_CONFIGURATION_STATE_V1"
EPOCH_UTC = "2226-08-22T01:32:00Z"
ROUTE = ["CERES", "NEPTUNE_SYSTEM"]


class E1InitialRuntimeConfiguration(RuntimeConfigurationInput):
    def to_evidence(self) -> dict[str, Any]:
        evidence = super().to_evidence()
        evidence["scenario_lock"] = {
            "schema": SCHEMA,
            "kind": "E1_AUTHORED_INITIAL_CONDITION",
            "epoch_utc": EPOCH_UTC,
            "route": ROUTE,
            "rationale": {
                "launch_attachment_state": "REFERENCE_COURIER_DEPARTS_WITH_NORMAL_CARRIED_LAUNCH",
                "external_attachment_state": "E1_TRANSLATION_COMMIT_USES_SELF_CONTAINED_FREE_FLIGHT_CONFIGURATION",
                "deployable_structure_state": "E1_TRANSLATION_COMMIT_USES_STOWED_DEPLOYABLE_CONFIGURATION_FOR_STABLE_TOPOLOGY",
            },
            "not_claimed_as": [
                "RECOVERED_RUNTIME_FACT",
                "NAVIGATOR_DERIVED_STATE",
                "PHYSICS_DERIVED_STATE",
                "DOMAIN_MEMBERSHIP_CERTIFICATION",
            ],
        }
        return evidence


def build_e1_initial_configuration_state() -> E1InitialRuntimeConfiguration:
    return E1InitialRuntimeConfiguration(
        launch_attachment_state=LaunchAttachmentState.DOCKED,
        external_attachment_state=ExternalAttachmentState.FREE,
        deployable_structure_state=DeployableStructureState.STOWED,
    )


def main() -> int:
    result = build_e1_initial_configuration_state().to_evidence()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("QUALIFICATION_AXIS=runtime_configuration_input")
    print(f"QUALIFICATION_DISPOSITION={result['disposition']}")
    missing = ",".join(result["missing_authored_scenario_inputs"]) or "NONE"
    print(f"QUALIFICATION_MISSING_REQUIRED_EVIDENCE={missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
