#!/usr/bin/env python3
from __future__ import annotations

import json

from src.loom_planetary_environment import PlanetaryEnvironmentState


FORBIDDEN_FIELDS = {
    "admissible",
    "admissibility_score",
    "metric_policy",
    "collapse_radius_km",
    "loom_coherence",
}


def qualification_report() -> dict[str, object]:
    fields = tuple(PlanetaryEnvironmentState.__dataclass_fields__)
    forbidden_present = sorted(FORBIDDEN_FIELDS.intersection(fields))
    return {
        "schema": "LOOM_E1_PLANETARY_ENVIRONMENT_INTERFACE_V1",
        "status": "PASS" if not forbidden_present else "FAIL",
        "classification": "INTERFACE_CONTRACT_ONLY_NO_ENVIRONMENT_MODEL",
        "state_fields": list(fields),
        "forbidden_fields_present": forbidden_present,
        "uncertainty_required": "uncertainty" in fields,
        "provenance_required": "provenance" in fields,
        "loom_coherence_location": "SEPARATE_UNRESOLVED_PHYSICS_SEAM",
        "admissibility_authority": "ZERO",
        "environment_model_authority": "ZERO_INTERFACE_ONLY",
        "authority_note": "NO_2226_VALUES_NO_THRESHOLD_NO_SCORE_NO_METRIC_POLICY_NO_CAMPAIGN_MUTATION_LLM_AUTHORITY_ZERO",
        "next_action": "QUALIFY_PROVIDER_MODEL_SEPARATELY_BEFORE_ANY_ENDPOINT_ENVIRONMENT_USE",
    }


def main() -> int:
    report = qualification_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
