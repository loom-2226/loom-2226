#!/usr/bin/env python3
import json


EARNED_ENDPOINT = {
    "body": "NEPTUNE",
    "collapse_radius_km": 26085.768742,
    "endpoint_status": "EARNED_OPERATIONAL_HANDOFF_NOT_FUNDAMENTAL_BOUNDARY",
    "endpoint_moved_or_resolved_again": False,
}

REQUIRED_CERTIFICATION_STATE = [
    "domain_membership",
    "attachment_state",
    "mass_state_model",
    "node_topology",
    "hull_lattice_configuration",
]

REJECTED_DOMAIN_SIZE_SHORTCUTS = [
    "HILL_RADIUS",
    "LAPLACE_SOI",
    "SURFACE_RADIUS_MULTIPLE",
    "CURRENT_COLLAPSE_RADIUS",
    "UNIVERSAL_RAMP_DISPLACEMENT_MULTIPLE",
]


def qualify_compound_ga_domain_size_binding():
    return {
        "schema": "LOOM_E1_COMPOUND_GA_DOMAIN_SIZE_BINDING_V1",
        "status": "PASS",
        "endpoint": EARNED_ENDPOINT,
        "binding_rule": "CERTIFIED_TRANSLATION_DOMAIN_IS_VESSEL_CONFIGURATION_BOUND_NOT_CELESTIAL_EXCLUSION_RADIUS",
        "lineage": {
            "metric_transit_semantics": "RELATIONAL_DISPLACEMENT_NOT_ORDINARY_SPACE_OCCUPANCY",
            "hill_or_soi_direct_collapse_policy": "REJECTED_AS_CURRENT_ABSTRACTION",
            "universal_ramp_displacement_multiple": "RETIRED_AS_PHYSICAL_CLEARANCE_LAW",
            "source_metric_admissibility": "engineering/experience_one/E1_METRIC_ADMISSIBILITY_LINEAGE_v0.1.md",
            "source_current_canon": "canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md",
        },
        "required_certification_state": REQUIRED_CERTIFICATION_STATE,
        "rejected_domain_size_shortcuts": REJECTED_DOMAIN_SIZE_SHORTCUTS,
        "body_centered_exclusion_radius_defined": False,
        "collapse_radius_repurposed_as_domain_size": False,
        "domain_size_axis": {
            "status": "QUALIFIED_BINDING_RULE_NUMERIC_EXTENT_UNRESOLVED",
            "meaning": "SPATIAL_EXTENT_OF_CERTIFIED_VESSEL_TRANSLATION_DOMAIN_FOR_THE_COMMITTED_CONFIGURATION",
            "numeric_extent_defined": False,
            "treated_as_zero": False,
            "hull_dimensions_substituted_for_certified_domain": False,
            "configuration_change_invalidates_solution": True,
            "required_evidence": (
                "governed certified translation-domain geometry for the committed vessel configuration, "
                "including membership and attachment state rather than a celestial-mechanics proxy"
            ),
        },
        "decision": "DOMAIN_SIZE_BINDING_RULE_QUALIFIED_NUMERIC_TRANSLATION_DOMAIN_EXTENT_REMAINS_UNRESOLVED",
        "admissibility_threshold_defined": False,
        "runtime_policy_bound": False,
        "runtime_policy_mutation": "ZERO",
        "campaign_state_mutation": "ZERO",
        "llm_calculation_authority": "ZERO",
        "authority_note": (
            "NO_BODY_CENTERED_EXCLUSION_RADIUS_NO_HILL_OR_SOI_NO_SURFACE_MULTIPLE_NO_COLLAPSE_RADIUS_REUSE_"
            "NO_UNIVERSAL_RAMP_MULTIPLE_NO_HULL_DIMENSION_SUBSTITUTION_NO_RUNTIME_BINDING"
        ),
        "qualified_next_step": "QUALIFY_LOOM_AND_LATTICE_COHERENCE_MODEL_FORM_WITHOUT_BINDING_RUNTIME_POLICY",
    }


def main():
    print(json.dumps(qualify_compound_ga_domain_size_binding(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
