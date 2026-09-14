#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.loom_neptune_atmosphere_reference_anchors import (
    NEPTUNE_VOYAGER2_REFERENCE_ANCHORS,
)


def main() -> int:
    anchors = [
        {
            "anchor_id": anchor.anchor_id,
            "altitude_from_one_bar_km": anchor.altitude_from_one_bar_km,
            "pressure_pa": anchor.pressure_pa,
            "temperature_k": anchor.temperature_k,
            "temperature_uncertainty_k": anchor.temperature_uncertainty_k,
            "h2_number_fraction_min": anchor.h2_number_fraction_min,
            "h2_number_fraction_max": anchor.h2_number_fraction_max,
            "source_ids": list(anchor.source_ids),
        }
        for anchor in NEPTUNE_VOYAGER2_REFERENCE_ANCHORS
    ]
    report = {
        "schema": "LOOM_E1_NEPTUNE_ATMOSPHERE_REFERENCE_ANCHORS_V1",
        "status": "PASS",
        "classification": "HISTORICAL_DISCRETE_REFERENCE_ANCHORS_ONLY",
        "body": "NE",
        "source_epoch_class": "VOYAGER2_1989_HISTORICAL_REFERENCE",
        "anchor_count": len(anchors),
        "anchors": anchors,
        "continuous_profile_earned": False,
        "local_2226_endpoint_values_earned": False,
        "interpolation_authority": "ZERO",
        "extrapolation_authority": "ZERO",
        "density_authority": "ZERO",
        "admissibility_authority": "ZERO",
        "loom_coherence_authority": "ZERO",
        "one_bar_semantics": "PRESSURE_REFERENCE_NOT_SOLID_SURFACE",
        "authority_note": "HISTORICAL_REFERENCE_POINTS_ONLY_NO_INTERPOLATION_NO_EXTRAPOLATION_NO_DENSITY_NO_2226_PROPAGATION_NO_THRESHOLD_NO_SCORE_NO_RUNTIME_POLICY_NO_CAMPAIGN_MUTATION_LLM_AUTHORITY_ZERO",
        "next_action": "QUALIFY_ANY_CONTINUOUS_PROFILE_OR_2226_EVOLUTION_MODEL_SEPARATELY_BEFORE_LOCAL_ENDPOINT_USE",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
