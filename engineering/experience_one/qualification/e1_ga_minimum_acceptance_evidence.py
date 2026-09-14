#!/usr/bin/env python3
import json


def qualify_e1_ga_minimum_acceptance_evidence():
    axis_acceptance_contract = {
        "local_geometry": {
            "current_state": "UNRESOLVED_REQUIRED",
            "earned_evidence": "J2_CORRECTED_LOCAL_TIDAL_REFERENCE_QUALIFIED",
            "minimum_acceptance_evidence": (
                "governed compatibility result showing the qualified local geometry/tidal envelope is acceptable "
                "across the certified translation domain for the committed E1 configuration"
            ),
            "supported_by_package": "endpoint_domain_physical_compatibility",
            "additional_acceptance_evidence_required": True,
        },
        "local_stress_energy": {
            "current_state": "SATISFIED_NON_MATERIAL",
            "earned_evidence": "LOCAL_STRESS_ENERGY_NOT_MATERIAL_AT_ONE_PERCENT_STANDARD_GR_SCREEN_PRESERVE_2226_ENVIRONMENT_UNCERTAINTY",
            "minimum_acceptance_evidence": "already satisfied by qualified standard-GR materiality screen",
            "supported_by_package": None,
            "additional_acceptance_evidence_required": False,
        },
        "causal_structure": {
            "current_state": "UNRESOLVED_REQUIRED",
            "earned_evidence": "STANDARD_GR_CAUSAL_PATHOLOGY_NOT_MATERIAL_AT_E1_NEPTUNE_ENDPOINT",
            "minimum_acceptance_evidence": (
                "governed endpoint/domain causal-compatibility result for the operational metric-domain model, "
                "or an explicitly qualified equivalent certification invariant"
            ),
            "supported_by_package": "endpoint_domain_physical_compatibility",
            "additional_acceptance_evidence_required": True,
        },
        "domain_size": {
            "current_state": "UNRESOLVED_REQUIRED",
            "earned_evidence": "CERTIFIED_TRANSLATION_DOMAIN_IS_VESSEL_CONFIGURATION_BOUND_NOT_CELESTIAL_EXCLUSION_RADIUS",
            "minimum_acceptance_evidence": (
                "governed translation-domain geometry or certification envelope tied to the committed vessel configuration, "
                "including domain membership and attachment state"
            ),
            "supported_by_package": "endpoint_domain_physical_compatibility",
            "additional_acceptance_evidence_required": True,
        },
        "loom_coherence": {
            "current_state": "UNRESOLVED_REQUIRED",
            "earned_evidence": "ROUTE_TOPOLOGY_RELATIONAL_ACCESS_MODEL_FORM_QUALIFIED",
            "minimum_acceptance_evidence": (
                "direction-specific governed route solution for E1 containing route evidence, destination state, momentum mapping, "
                "route burden/uncertainty, and a certifiable relational-access disposition"
            ),
            "supported_by_package": "route_vessel_coherence",
            "additional_acceptance_evidence_required": True,
        },
        "lattice_coherence": {
            "current_state": "UNRESOLVED_REQUIRED",
            "earned_evidence": "VESSEL_DOMAIN_FORMATION_AND_HARDWARE_MODEL_FORM_QUALIFIED",
            "minimum_acceptance_evidence": (
                "governed committed-configuration formation result containing configuration identity, domain membership, "
                "formation/integrity state, hardware condition, and required thermal/bank margins"
            ),
            "supported_by_package": "route_vessel_coherence",
            "additional_acceptance_evidence_required": True,
        },
    }

    minimum_evidence_packages = {
        "endpoint_domain_physical_compatibility": {
            "supports_axes": ["local_geometry", "causal_structure", "domain_size"],
            "purpose": "CERTIFY_ENDPOINT_AND_TRANSLATION_DOMAIN_PHYSICAL_COMPATIBILITY_FOR_COMMITTED_E1_CONFIGURATION",
            "must_preserve_axis_level_results": True,
            "single_package_does_not_merge_axes": True,
            "required_contents": [
                "committed_configuration_identity",
                "translation_domain_geometry_or_certification_envelope",
                "qualified_local_geometry_compatibility_result",
                "qualified_causal_compatibility_result_or_equivalent_invariant",
                "uncertainty_and_provenance",
            ],
        },
        "route_vessel_coherence": {
            "supports_axes": ["loom_coherence", "lattice_coherence"],
            "purpose": "CERTIFY_DIRECTION_SPECIFIC_ROUTE_ACCESS_AND_VESSEL_FORMATION_FOR_SAME_COMMITTED_CONFIGURATION",
            "must_preserve_axis_level_results": True,
            "single_package_does_not_merge_axes": True,
            "required_contents": [
                "route_solution_identity_and_direction",
                "route_evidence_destination_state_and_momentum_mapping",
                "route_burden_and_uncertainty",
                "configuration_identity_and_domain_membership",
                "formation_and_integrity_state",
                "hardware_thermal_and_bank_margins",
                "certification_disposition",
            ],
        },
    }

    return {
        "schema": "LOOM_E1_GA_MINIMUM_ACCEPTANCE_EVIDENCE_V1",
        "status": "PASS",
        "axis_acceptance_contract": axis_acceptance_contract,
        "minimum_evidence_packages": minimum_evidence_packages,
        "evidence_policy": {
            "package_level_shortcut_to_admissible_allowed": False,
            "cross_axis_compensation_allowed": False,
            "missing_axis_evidence_treated_as_satisfied": False,
            "same_committed_configuration_required_across_packages": True,
            "provenance_required": True,
            "uncertainty_required": True,
        },
        "current_e1_state": "INDETERMINATE_NOT_CERTIFIABLE",
        "remaining_additional_axis_evidence_count": 5,
        "remaining_minimum_evidence_package_count": 2,
        "current_endpoint_certified_by_this_contract": False,
        "earned_operational_handoff_preserved": True,
        "runtime_policy_bound": False,
        "runtime_policy_mutation": "ZERO",
        "campaign_state_mutation": "ZERO",
        "llm_calculation_authority": "ZERO",
        "decision": "MINIMUM_E1_GA_ACCEPTANCE_EVIDENCE_CONTRACT_QUALIFIED_TWO_EVIDENCE_PACKAGES_REQUIRED",
        "authority_note": (
            "ACCEPTANCE_CONTRACT_ONLY_NO_NEW_PHYSICS_THRESHOLD_NO_AXIS_MERGE_NO_CROSS_AXIS_COMPENSATION_"
            "NO_RUNTIME_BINDING_NO_ENDPOINT_MOVEMENT"
        ),
        "qualified_next_step": "BUILD_E1_GA_ACCEPTANCE_EVIDENCE_ADAPTER_AND_REPORT_MISSING_FIELDS",
    }


def main():
    print(json.dumps(qualify_e1_ga_minimum_acceptance_evidence(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
