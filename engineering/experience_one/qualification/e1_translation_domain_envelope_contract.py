#!/usr/bin/env python3
from __future__ import annotations

"""Qualify the minimum E1 translation-domain certification-envelope contract.

This artifact defines what a certifiable vessel-bound translation domain must contain
without inventing the missing boundary geometry. It preserves the governing rule that
domain membership is derived from a certified domain solution for the committed vessel
configuration, not inferred from structural integration, nominal hull dimensions, node
count, or a celestial-mechanics stand-off radius.
"""

import json

SCHEMA = "LOOM_E1_TRANSLATION_DOMAIN_ENVELOPE_CONTRACT_V1"
CONFIGURATION_ID = "WAYFARER_REFERENCE_SCHEMATIC_V2_4A"


def qualify_e1_translation_domain_envelope_contract():
    missing = [
        "certified_translation_domain_boundary_solution",
        "committed_component_geometry_envelope",
        "domain_membership_containment_result",
    ]

    return {
        "schema": SCHEMA,
        "status": "PASS",
        "binding_rule": "CERTIFIED_TRANSLATION_DOMAIN_IS_VESSEL_CONFIGURATION_BOUND_NOT_CELESTIAL_EXCLUSION_RADIUS",
        "configuration_identity": CONFIGURATION_ID,
        "governing_lineage": {
            "engineering_canon": "canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md",
            "wayfarer_schematic": "canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md",
            "domain_size_binding": "engineering/experience_one/qualification/e1_compound_ga_domain_size_binding.py",
            "domain_membership_dependency": "engineering/experience_one/qualification/e1_domain_membership_derivation.py",
        },
        "certification_envelope_contract": {
            "domain_kind": "VESSEL_CONFIGURATION_BOUND_TRANSLATION_DOMAIN",
            "boundary_basis": "GOVERNED_DISTRIBUTED_NODE_FIELD_SOLUTION_FOR_COMMITTED_CONFIGURATION",
            "configuration_change_invalidates_solution": True,
            "anisotropic_domain_allowed": True,
            "time_varying_domain_allowed": True,
            "numeric_extent_required_for_final_domain_size_certification": True,
            "must_account_for_runtime_attachment_and_deployable_state": True,
            "must_preserve_uncertainty_and_provenance": True,
        },
        "membership_contract": {
            "rule": "MEMBER_IFF_COMMITTED_COMPONENT_GEOMETRY_IS_CONTAINED_BY_CERTIFIED_TRANSLATION_DOMAIN_BOUNDARY",
            "structural_integration_alone_certifies_membership": False,
            "mass_state_inclusion_alone_certifies_membership": False,
            "attachment_state_alone_certifies_membership": False,
            "nominal_hull_envelope_alone_certifies_membership": False,
            "membership_requires_same_committed_configuration": True,
        },
        "current_e1_instantiation": {
            "launch_attachment_state": "DOCKED",
            "external_attachment_state": "FREE",
            "deployable_structure_state": "STOWED",
            "distributed_boundary_metric_nodes": 208,
            "exact_node_placement": "OPEN",
            "exact_node_placement_promoted_to_known": False,
            "certified_boundary_present": False,
            "numeric_extent_defined": False,
            "membership_state": "UNKNOWN",
            "missing_required_evidence": missing,
        },
        "policy": {
            "body_centered_radius_substitution_allowed": False,
            "hill_or_soi_substitution_allowed": False,
            "collapse_radius_substitution_allowed": False,
            "hull_dimension_substitution_allowed": False,
            "node_count_substitution_allowed": False,
            "open_schematic_detail_promoted_to_known": False,
            "unknown_membership_treated_as_member": False,
        },
        "disposition": "ENVELOPE_CONTRACT_QUALIFIED_INSTANTIATION_UNRESOLVED",
        "qualified_next_step": "RESOLVE_MINIMUM_WAYFARER_COMPONENT_AND_NODE_GEOMETRY_THEN_SOLVE_CERTIFIED_TRANSLATION_DOMAIN_BOUNDARY",
        "authority": {
            "certifies_envelope_contract": True,
            "certifies_boundary_geometry": False,
            "certifies_domain_membership": False,
            "certifies_domain_size": False,
            "certifies_local_geometry_compatibility": False,
            "certifies_causal_compatibility": False,
            "certifies_lattice_coherence": False,
            "certifies_overall_ga": False,
            "campaign_state_mutation": "ZERO",
            "runtime_policy_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
    }


def main() -> int:
    result = qualify_e1_translation_domain_envelope_contract()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("QUALIFICATION_AXIS=translation_domain_certification_envelope")
    print(f"QUALIFICATION_DISPOSITION={result['disposition']}")
    missing = ",".join(result["current_e1_instantiation"]["missing_required_evidence"]) or "NONE"
    print(f"QUALIFICATION_MISSING_REQUIRED_EVIDENCE={missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
