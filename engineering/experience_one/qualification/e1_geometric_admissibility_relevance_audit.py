#!/usr/bin/env python3
from __future__ import annotations

"""Read-only relevance audit for E1 Geometric Admissibility inputs.

This audit does not define a threshold, score, exclusion radius, runtime policy,
or new physics. It organizes already-named canon factors by their role in the
parent problem so engineering work follows demonstrated relevance rather than
mere data availability.
"""

import json
from typing import Any


CANON_BASIS = (
    "Foundational Canon v1.5 §6.11: translation viability depends on the geometry "
    "of the entire domain and endpoint state, including curvature, curvature "
    "gradients/tidal shear, stress-energy/matter density, electromagnetic "
    "conditions, causal structure, domain size, Loom coherence, lattice "
    "coherence, and uncertainty."
)


def build_relevance_audit() -> dict[str, Any]:
    factors = [
        {
            "family": "curvature",
            "role": "DIRECT_GEOMETRIC_DRIVER",
            "canon_status": "EXPLICITLY_NAMED",
            "current_evidence": "NEPTUNE_GM_AND_REFERENCE_GEOMETRY_PRESENT_LOCAL_CURVATURE_NOT_YET_QUALIFIED_AT_COLLAPSE_ENDPOINT",
            "decision_leverage": "HIGH_WITHOUT_SPECULATIVE_COUPLING",
            "work_priority": "NEXT_ENGINEERING",
            "plain_language": "How strongly spacetime is curved at the endpoint. This is closer to the actual geometry question than a conventional orbital boundary is.",
        },
        {
            "family": "curvature_gradients_tidal_shear",
            "role": "DIRECT_GEOMETRIC_DRIVER",
            "canon_status": "EXPLICITLY_NAMED",
            "current_evidence": "NEPTUNE_GRAVITY_INPUTS_PRESENT_LOCAL_GRADIENT_AND_TIDAL_TENSOR_NOT_YET_QUALIFIED_AT_COLLAPSE_ENDPOINT",
            "decision_leverage": "HIGH_WITHOUT_SPECULATIVE_COUPLING",
            "work_priority": "NEXT_ENGINEERING",
            "plain_language": "How quickly gravity/curvature changes across the relevant region. This captures differential gravity rather than just gravity strength.",
        },
        {
            "family": "stress_energy_matter_density",
            "role": "SOURCE_ENVIRONMENT_TERM",
            "canon_status": "EXPLICITLY_NAMED",
            "current_evidence": "ATMOSPHERE_CLASS_AND_BOUNDED_HISTORICAL_REFERENCE_MODEL_EXIST_LOCAL_2226_DENSITY_AT_ENDPOINT_NOT_QUALIFIED",
            "decision_leverage": "MATERIAL_BUT_REQUIRES_LOCAL_STATE",
            "work_priority": "AFTER_LOCAL_GEOMETRY",
            "plain_language": "Matter and energy present in the endpoint region. We need the local state, not merely the fact that Neptune has an atmosphere.",
        },
        {
            "family": "electromagnetic_conditions",
            "role": "EXPLICIT_CANDIDATE_WITH_UNEARNED_COUPLING",
            "canon_status": "EXPLICITLY_NAMED",
            "current_evidence": "HISTORICAL_NEPTUNE_SOURCE_FAMILIES_IDENTIFIED_NO_2226_ENDPOINT_FIELD_AND_NO_QUALIFIED_METRIC_COUPLING_RULE",
            "decision_leverage": "UNKNOWN_UNTIL_COUPLING_SEMANTICS_ARE_EARNED",
            "work_priority": "HOLD_UNTIL_COUPLING_IS_EARNED",
            "plain_language": "Electric/magnetic conditions are named by canon, but we do not yet know how strongly they affect metric collapse. More MAG data does not answer that physics question.",
        },
        {
            "family": "causal_structure",
            "role": "DIRECT_GEOMETRIC_DRIVER",
            "canon_status": "EXPLICITLY_NAMED",
            "current_evidence": "NO_SEPARATE_QUALIFIED_ENDPOINT_REPRESENTATION_YET",
            "decision_leverage": "LIKELY_DERIVED_FROM_THE_QUALIFIED_SPACETIME_MODEL",
            "work_priority": "AFTER_LOCAL_GEOMETRY",
            "plain_language": "Whether the local spacetime relationships support the required endpoint connection. This should come from the spacetime model, not a new environmental sensor feed.",
        },
        {
            "family": "domain_size",
            "role": "DIRECT_DOMAIN_TERM",
            "canon_status": "EXPLICITLY_NAMED",
            "current_evidence": "NO_QUALIFIED_BINDING_BETWEEN_OPERATIONAL_METRIC_DOMAIN_SIZE_AND_ADMISSIBILITY",
            "decision_leverage": "POTENTIALLY_HIGH_BUT_BINDING_SEMANTICS_MISSING",
            "work_priority": "PHYSICS_BINDING_REQUIRED",
            "plain_language": "The size of the region that must remain geometrically compatible during the transition. We have not yet earned the rule connecting that size to the endpoint test.",
        },
        {
            "family": "loom_coherence",
            "role": "LOOM_SPECIFIC_PHYSICS_TERM",
            "canon_status": "EXPLICITLY_NAMED",
            "current_evidence": "NO_QUALIFIED_MEASUREMENT_OR_ENDPOINT_MODEL",
            "decision_leverage": "CONCEPTUALLY_HIGH_BUT_NOT_OPERATIONALIZED",
            "work_priority": "PHYSICS_BLOCKED",
            "plain_language": "A Loom-specific compatibility term. It may be central eventually, but engineering cannot fabricate a measurement model before the physics earns one.",
        },
        {
            "family": "lattice_coherence",
            "role": "LOOM_SPECIFIC_PHYSICS_TERM",
            "canon_status": "EXPLICITLY_NAMED",
            "current_evidence": "NO_QUALIFIED_MEASUREMENT_OR_ENDPOINT_MODEL",
            "decision_leverage": "CONCEPTUALLY_HIGH_BUT_NOT_OPERATIONALIZED",
            "work_priority": "PHYSICS_BLOCKED",
            "plain_language": "Compatibility of the engineered Loom/lattice state with the endpoint domain. The governing observable is not yet qualified.",
        },
        {
            "family": "uncertainty",
            "role": "EPISTEMIC_DECISION_GATE",
            "canon_status": "EXPLICITLY_NAMED",
            "current_evidence": "PHYSICAL_INPUT_UNCERTAINTY_NOT_YET_PROPAGATED_AS_A_COMPOUND_ENDPOINT_BUDGET",
            "decision_leverage": "GATES_WHETHER_A_RESULT_IS_SAFE_TO_USE",
            "work_priority": "PROPAGATE_WITH_EACH_QUALIFIED_MODEL",
            "plain_language": "Not another force. It is how sure we are about the quantities that actually drive admissibility, and therefore whether the endpoint decision can be trusted.",
        },
    ]

    context_only = [
        {
            "quantity": "Hill radius",
            "ordinary_role": "THIRD_BODY_GRAVITATIONAL_DOMINANCE_CONTEXT",
            "admissibility_boundary_authority": "ZERO",
            "reason": "Useful orbital context, but prior forced-radius work found no earned metric-collapse boundary at the Hill scale.",
        },
        {
            "quantity": "Laplace sphere of influence",
            "ordinary_role": "PATCHED_CONIC_ORBITAL_CONTEXT",
            "admissibility_boundary_authority": "ZERO",
            "reason": "Useful navigation/orbital context, not a demonstrated Geometric Admissibility threshold.",
        },
        {
            "quantity": "Neptune GM / mean radius",
            "ordinary_role": "INPUTS_TO_LOCAL_GRAVITATIONAL_GEOMETRY",
            "admissibility_boundary_authority": "ZERO",
            "reason": "Inputs to a local model are not themselves a collapse threshold.",
        },
    ]

    return {
        "schema": "LOOM_E1_GEOMETRIC_ADMISSIBILITY_RELEVANCE_AUDIT_V1",
        "status": "PASS",
        "scope": "READ_ONLY_PRIORITY_AND_ROLE_CLASSIFICATION",
        "canon_basis": CANON_BASIS,
        "scoring_authority": "ZERO",
        "threshold_authority": "ZERO",
        "runtime_policy_authority": "ZERO",
        "campaign_mutation_authority": "ZERO",
        "factors": factors,
        "context_only": context_only,
        "priority_interpretation": {
            "NEXT_ENGINEERING": "Can advance the parent question using already-grounded ordinary spacetime inputs without inventing a new coupling law.",
            "AFTER_LOCAL_GEOMETRY": "Relevant, but should follow the first direct local-geometry calculation so effort stays ordered.",
            "HOLD_UNTIL_COUPLING_IS_EARNED": "Named by canon, but collecting more source data does not help until the coupling to admissibility is defined.",
            "PHYSICS_BINDING_REQUIRED": "Potentially important but the rule connecting it to admissibility is not yet qualified.",
            "PHYSICS_BLOCKED": "Cannot be operationalized honestly until RF/Loom physics supplies a measurable or computable definition.",
            "PROPAGATE_WITH_EACH_QUALIFIED_MODEL": "Uncertainty accompanies every driver rather than becoming a separate environmental rabbit hole.",
        },
        "next_action": "QUALIFY_LOCAL_CURVATURE_AND_TIDAL_SHEAR_AT_THE_EARNED_NEPTUNE_COLLAPSE_ENDPOINT_WITHOUT_DEFINING_A_NEW_THRESHOLD",
        "authority_note": "NO_NUMERIC_IMPORTANCE_SCORE_NO_NEW_PHYSICS_NO_EXCLUSION_RADIUS_NO_HILL_OR_SOI_POLICY_NO_EM_COUPLING_INFERENCE_LLM_AUTHORITY_ZERO",
    }


def main() -> int:
    print(json.dumps(build_relevance_audit(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
