#!/usr/bin/env python3
import json


SATISFIED_STATES = {"SATISFIED", "SATISFIED_NON_MATERIAL"}


def evaluate_ga(axes):
    hard_fail = sorted(
        key for key, value in axes.items()
        if value["decision_state"] == "HARD_FAIL"
    )
    unresolved = sorted(
        key for key, value in axes.items()
        if value["decision_state"] == "UNRESOLVED_REQUIRED"
    )

    if hard_fail:
        decision = "INADMISSIBLE"
    elif unresolved:
        decision = "INDETERMINATE_NOT_CERTIFIABLE"
    elif all(value["decision_state"] in SATISFIED_STATES for value in axes.values()):
        decision = "ADMISSIBLE"
    else:
        raise ValueError("Unsupported GA decision_state")

    return {
        "decision": decision,
        "blocking_axes": hard_fail,
        "unresolved_required_axes": unresolved,
    }


def qualify_compound_ga_decision_rule():
    axes = {
        "local_geometry": {
            "decision_state": "UNRESOLVED_REQUIRED",
            "earned_evidence": "J2_CORRECTED_LOCAL_TIDAL_REFERENCE_QUALIFIED",
            "missing_for_certification": "QUALIFIED_GEOMETRY_ADMISSIBILITY_CRITERION_OR_BOUND",
        },
        "local_stress_energy": {
            "decision_state": "SATISFIED_NON_MATERIAL",
            "earned_evidence": "LOCAL_STRESS_ENERGY_NOT_MATERIAL_AT_ONE_PERCENT_STANDARD_GR_SCREEN_PRESERVE_2226_ENVIRONMENT_UNCERTAINTY",
            "scope": "STANDARD_GR_MATERIALITY_SCREEN_ONLY",
        },
        "causal_structure": {
            "decision_state": "UNRESOLVED_REQUIRED",
            "earned_evidence": "STANDARD_GR_CAUSAL_PATHOLOGY_NOT_MATERIAL_AT_E1_NEPTUNE_ENDPOINT",
            "missing_for_certification": "LOOM_SPECIFIC_METRIC_DOMAIN_CAUSAL_STRUCTURE_OR_GOVERNED_EQUIVALENT",
        },
        "domain_size": {
            "decision_state": "UNRESOLVED_REQUIRED",
            "earned_evidence": "CERTIFIED_TRANSLATION_DOMAIN_IS_VESSEL_CONFIGURATION_BOUND_NOT_CELESTIAL_EXCLUSION_RADIUS",
            "missing_for_certification": "GOVERNED_NUMERIC_TRANSLATION_DOMAIN_GEOMETRY_FOR_COMMITTED_CONFIGURATION",
        },
        "loom_coherence": {
            "decision_state": "UNRESOLVED_REQUIRED",
            "earned_evidence": "ROUTE_TOPOLOGY_RELATIONAL_ACCESS_MODEL_FORM_QUALIFIED",
            "missing_for_certification": "GOVERNED_ROUTE_COHERENCE_ACCEPTANCE_CRITERION_FOR_THIS_CONFIGURATION_AND_DIRECTION",
        },
        "lattice_coherence": {
            "decision_state": "UNRESOLVED_REQUIRED",
            "earned_evidence": "VESSEL_DOMAIN_FORMATION_AND_HARDWARE_MODEL_FORM_QUALIFIED",
            "missing_for_certification": "GOVERNED_LATTICE_COHERENCE_ACCEPTANCE_CRITERION_FOR_COMMITTED_CONFIGURATION",
        },
    }

    current = evaluate_ga(axes)

    return {
        "schema": "LOOM_E1_COMPOUND_GA_DECISION_RULE_V1",
        "status": "PASS",
        "decision_rule": {
            "representation": "FAIL_CLOSED_THREE_STATE_AXIS_CONJUNCTION",
            "hard_fail_precedence": True,
            "unresolved_required_means": "INDETERMINATE_NOT_CERTIFIABLE",
            "all_required_axes_satisfied_means": "ADMISSIBLE",
            "any_qualified_hard_fail_means": "INADMISSIBLE",
            "cross_axis_compensation_allowed": False,
            "weights_defined": False,
            "scalar_score_defined": False,
            "unknown_equals_failure": False,
        },
        "current_e1_axes": axes,
        "current_e1_evaluation": current,
        "uncertainty_policy": {
            "unknown_treated_as_zero": False,
            "unknown_treated_as_satisfied": False,
            "unknown_blocks_certification": True,
            "partial_evidence_preserved": True,
            "negative_materiality_screen_promoted_to_full_axis_solution": False,
        },
        "interpretation": (
            "THE_DECISION_RULE_IS_QUALIFIED_BUT_CURRENT_E1_NEPTUNE_GA_REMAINS_"
            "INDETERMINATE_BECAUSE_REQUIRED_AXIS_ACCEPTANCE_EVIDENCE_IS_STILL_MISSING"
        ),
        "current_endpoint_rejected": False,
        "current_endpoint_certified_by_this_rule": False,
        "earned_operational_handoff_preserved": True,
        "runtime_policy_bound": False,
        "runtime_policy_mutation": "ZERO",
        "campaign_state_mutation": "ZERO",
        "llm_calculation_authority": "ZERO",
        "authority_note": (
            "DECISION_RULE_ONLY_UNKNOWN_IS_NOT_PASS_UNKNOWN_IS_NOT_FAIL_NO_WEIGHTS_NO_COMPENSATION_"
            "NO_RUNTIME_BINDING_NO_ENDPOINT_REJECTION"
        ),
        "qualified_next_step": "QUALIFY_MINIMUM_E1_AXIS_ACCEPTANCE_EVIDENCE_REQUIRED_FOR_CERTIFIABLE_GA_OUTCOME",
    }


def main():
    print(json.dumps(qualify_compound_ga_decision_rule(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
