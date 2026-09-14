#!/usr/bin/env python3
from __future__ import annotations

"""Classify E1 runtime configuration state needed for domain membership/attachment.

Configuration identity is already qualified. Authored runtime state comes from the
typed E1 runtime-configuration input. Domain membership remains derived-only and is
not inferred from identity or authored by this classifier.
"""

import json
from typing import Any, Mapping

from engineering.experience_one.qualification.e1_runtime_configuration_input import (
    SCHEMA as RUNTIME_INPUT_SCHEMA,
    build_default_e1_runtime_configuration,
)

SCHEMA = "LOOM_E1_DOMAIN_MEMBERSHIP_ATTACHMENT_STATE_V1"
REQUIRED = [
    "launch_attachment_state",
    "external_attachment_state",
    "deployable_structure_state",
    "domain_membership_state",
]


def _known(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip().upper()
    return bool(text) and text not in {"UNKNOWN", "UNRESOLVED", "NOT_AVAILABLE", "NONE"}


def evaluate_runtime_configuration_state(state: Mapping[str, Any]) -> dict[str, Any]:
    missing = sorted(name for name in REQUIRED if not _known(state.get(name)))
    complete = not missing
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "configuration_identity": state.get("configuration_identity", "UNKNOWN"),
        "runtime_input_source": state.get("runtime_input_source", "UNSPECIFIED"),
        "runtime_state": {name: state.get(name, "UNKNOWN") for name in REQUIRED},
        "missing_required_evidence": missing,
        "disposition": "RUNTIME_CONFIGURATION_STATE_PRESENT" if complete else "INDETERMINATE_NOT_CERTIFIABLE",
        "policy": {
            "infer_launch_docked_from_baseline": False,
            "infer_radiators_stowed_from_mode": False,
            "infer_domain_membership_from_configuration_identity": False,
            "infer_external_attachment_state": False,
            "domain_membership_is_derived_only": True,
            "manual_domain_membership_override_allowed": False,
            "hull_dimensions_substitute_for_domain_geometry": False,
        },
        "authority": {
            "certifies_runtime_configuration_state": complete,
            "certifies_domain_geometry": False,
            "certifies_domain_size": False,
            "certifies_lattice_coherence": False,
            "certifies_overall_ga": False,
            "campaign_state_mutation": "ZERO",
            "runtime_policy_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
    }


def build_current_e1_runtime_inventory() -> dict[str, Any]:
    runtime_input = build_default_e1_runtime_configuration().to_evidence()
    authored = runtime_input["authored_state"]
    derived = runtime_input["derived_state"]
    return evaluate_runtime_configuration_state({
        "configuration_identity": runtime_input["configuration_identity"],
        "runtime_input_source": RUNTIME_INPUT_SCHEMA,
        "launch_attachment_state": authored["launch_attachment_state"],
        "external_attachment_state": authored["external_attachment_state"],
        "deployable_structure_state": authored["deployable_structure_state"],
        "domain_membership_state": derived["domain_membership_state"],
    })


def main() -> int:
    result = build_current_e1_runtime_inventory()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("QUALIFICATION_AXIS=domain_membership_and_attachment_state")
    print(f"QUALIFICATION_DISPOSITION={result['disposition']}")
    missing = ",".join(result["missing_required_evidence"]) or "NONE"
    print(f"QUALIFICATION_MISSING_REQUIRED_EVIDENCE={missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
