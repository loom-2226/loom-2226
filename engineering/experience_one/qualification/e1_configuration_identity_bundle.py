#!/usr/bin/env python3
from __future__ import annotations

"""Qualify presence of the committed E1 vessel configuration identity bundle.

This is an identity/evidence step only. It promotes already-earned mass-state and
node-topology evidence, while preserving hull/lattice configuration as unresolved
until a governed configuration identity actually exists.
"""

import json
from typing import Any, Mapping

from engineering.experience_one.qualification import e1_wayfarer_configuration_evidence as wayfarer_evidence

SCHEMA = "LOOM_E1_CONFIGURATION_IDENTITY_BUNDLE_V1"
REQUIRED = [
    "ship",
    "mass_state_model",
    "node_topology",
    "hull_lattice_configuration",
]


def _known(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip().upper()
    return bool(text) and text not in {"UNKNOWN", "UNRESOLVED", "NOT_AVAILABLE", "NONE"}


def evaluate_configuration(state: Mapping[str, Any]) -> dict[str, Any]:
    missing = sorted(name for name in REQUIRED if not _known(state.get(name)))
    complete = not missing
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "required_configuration_identity": REQUIRED,
        "ship": state.get("ship", "UNKNOWN"),
        "configuration": {name: state.get(name, "UNKNOWN") for name in REQUIRED},
        "missing_required_evidence": missing,
        "configuration_identity_complete": complete,
        "disposition": "CONFIGURATION_IDENTITY_PRESENT" if complete else "INDETERMINATE_NOT_CERTIFIABLE",
        "binding_rule": "CERTIFIED_TRANSLATION_DOMAIN_IS_VESSEL_CONFIGURATION_BOUND_NOT_CELESTIAL_EXCLUSION_RADIUS",
        "policy": {
            "ship_identity_alone_is_sufficient": False,
            "infer_unknown_values": False,
            "invent_configuration_values": False,
            "hull_dimensions_substitute_for_domain_geometry": False,
        },
        "authority": {
            "certifies_domain_membership_or_attachment": False,
            "certifies_domain_size": False,
            "certifies_lattice_coherence": False,
            "certifies_overall_ga": False,
            "campaign_state_mutation": "ZERO",
            "runtime_policy_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
    }


def build_current_e1_inventory() -> dict[str, Any]:
    earned = wayfarer_evidence.build_evidence()
    mass = earned["mass_state_model"]
    topo = earned["node_topology"]
    hull = earned["hull_lattice_configuration"]
    return evaluate_configuration({
        "ship": earned["ship"],
        "mass_state_model": mass.get("model_id", "UNKNOWN") if mass.get("state") == "PRESENT_QUALIFIED_SUPPORT" else "UNKNOWN",
        "node_topology": topo.get("topology_id", "UNKNOWN") if topo.get("state") == "PRESENT_QUALIFIED_SUPPORT" else "UNKNOWN",
        "hull_lattice_configuration": "UNKNOWN" if hull.get("state") != "PRESENT_QUALIFIED_SUPPORT" else hull.get("configuration_id", "UNKNOWN"),
    })


def main() -> int:
    print(json.dumps(build_current_e1_inventory(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
