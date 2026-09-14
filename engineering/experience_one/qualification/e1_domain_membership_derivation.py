#!/usr/bin/env python3
from __future__ import annotations

"""Derive the E1 domain-membership prerequisite boundary.

The committed runtime configuration determines what the relational-domain solution
must account for. It does not by itself certify that those components are members of
the translation domain. Membership remains unknown until a governed translation-
domain geometry or equivalent certification envelope is available for this exact
configuration.
"""

import json
from typing import Any

from engineering.experience_one.qualification.e1_initial_configuration_state import (
    build_e1_initial_configuration_state,
)

SCHEMA = "LOOM_E1_DOMAIN_MEMBERSHIP_DERIVATION_V1"
REQUIRED_DOMAIN_EVIDENCE = ["translation_domain_geometry_or_certification_envelope"]


def build_e1_domain_membership_derivation() -> dict[str, Any]:
    runtime = build_e1_initial_configuration_state().to_evidence()
    authored = runtime["authored_state"]
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "configuration_identity": runtime["configuration_identity"],
        "runtime_state": {
            "launch_attachment_state": authored["launch_attachment_state"],
            "external_attachment_state": authored["external_attachment_state"],
            "deployable_structure_state": authored["deployable_structure_state"],
        },
        "configuration_evidence": {
            "docked_launch_is_committed_configuration_component": authored["launch_attachment_state"] == "DOCKED",
            "external_attachment_set_is_empty": authored["external_attachment_state"] == "FREE",
            "deployable_topology_is_stowed": authored["deployable_structure_state"] == "STOWED",
            "launch_packaging_authority": "CANON_II_WAYFARER_SCHEMATIC_AMENDMENT_V2_4A",
            "launch_packaging_semantics": "SEMI_RECESSED_SUBSTANTIALLY_ENCLOSED_PRIMARY_STRUCTURE_COMPONENT",
            "relational_domain_solution_must_explicitly_account_for_launch_state": True,
        },
        "derived_state": {"domain_membership_state": "UNKNOWN"},
        "missing_required_evidence": REQUIRED_DOMAIN_EVIDENCE,
        "disposition": "DOMAIN_MEMBERSHIP_REQUIRES_CERTIFIED_DOMAIN_SOLUTION",
        "dependency": {
            "blocked_axis": "domain_membership_state",
            "upstream_axis": "translation_domain_geometry_or_certification_envelope",
            "package_order_implication": "PACKAGE_B_DOMAIN_MEMBERSHIP_DEPENDS_ON_PACKAGE_A_DOMAIN_SOLUTION",
        },
        "policy": {
            "domain_membership_is_derived_only": True,
            "manual_domain_membership_override_allowed": False,
            "structural_integration_implies_domain_membership": False,
            "mass_state_inclusion_implies_domain_membership": False,
            "node_count_implies_domain_membership": False,
            "hull_dimensions_substitute_for_domain_geometry": False,
            "body_centered_radius_substitutes_for_domain_geometry": False,
            "configuration_change_requires_membership_requalification": True,
        },
        "authority": {
            "certifies_configuration_membership_obligations": True,
            "certifies_domain_membership": False,
            "certifies_domain_geometry": False,
            "certifies_domain_size": False,
            "certifies_lattice_coherence": False,
            "certifies_overall_ga": False,
            "campaign_state_mutation": "ZERO",
            "runtime_policy_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
    }


def main() -> int:
    result = build_e1_domain_membership_derivation()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("QUALIFICATION_AXIS=domain_membership_derivation")
    print(f"QUALIFICATION_DISPOSITION={result['disposition']}")
    missing = ",".join(result["missing_required_evidence"]) or "NONE"
    print(f"QUALIFICATION_MISSING_REQUIRED_EVIDENCE={missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
