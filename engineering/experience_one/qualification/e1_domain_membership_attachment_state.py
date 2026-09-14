#!/usr/bin/env python3
from __future__ import annotations

"""Classify E1 runtime configuration state needed for domain membership/attachment.

Configuration identity is already qualified. This module deliberately does not infer
runtime attachment, deployable structure, or domain membership state from that identity.
"""

import json
from typing import Any, Mapping

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
        "runtime_state": {name: state.get(name, "UNKNOWN") for name in REQUIRED},
        "missing_required_evidence": missing,
        "disposition": "RUNTIME_CONFIGURATION_STATE_PRESENT" if complete else "INDETERMINATE_NOT_CERTIFIABLE",
        "policy": {
            "infer_launch_docked_from_baseline": False,
            "infer_radiators_stowed_from_mode": False,
            "infer_domain_membership_from_configuration_identity": False,
            "infer_external_attachment_state": False,
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
    return evaluate_runtime_configuration_state({
        "configuration_identity": "WAYFARER_REFERENCE_SCHEMATIC_V2_4A",
        "launch_attachment_state": "UNKNOWN",
        "external_attachment_state": "UNKNOWN",
        "deployable_structure_state": "UNKNOWN",
        "domain_membership_state": "UNKNOWN",
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
