#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.loom_neptune_spatial_atmosphere import NEPTUNE_REFERENCE_MEAN_RADIUS_KM


def qualification_report() -> dict[str, object]:
    return {
        "schema": "LOOM_E1_NEPTUNE_SPATIAL_ATMOSPHERE_PROVIDER_V1",
        "status": "PASS",
        "body": "NE",
        "classification": "NAVIGATION_GRADE_RELATIVE_GEOMETRY_PLUS_BODY_LEVEL_ATMOSPHERE_REFERENCE_ONLY",
        "reference_mean_radius_km": NEPTUNE_REFERENCE_MEAN_RADIUS_KM,
        "geometry_regimes": [
            "INSIDE_REFERENCE_MEAN_RADIUS_GEOMETRY",
            "AT_REFERENCE_MEAN_RADIUS_GEOMETRY",
            "ABOVE_REFERENCE_MEAN_RADIUS_GEOMETRY",
        ],
        "mean_radius_semantics": "REFERENCE_GEOMETRY_NOT_SOLID_SURFACE_NOT_ATMOSPHERIC_CUTOFF",
        "local_density_earned": False,
        "local_em_earned": False,
        "local_plasma_earned": False,
        "local_radiation_earned": False,
        "admissibility_authority": "ZERO",
        "loom_coherence_authority": "ZERO",
        "authority_note": "RELATIVE_GEOMETRY_ONLY_NO_LOCAL_2226_DENSITY_NO_ATMOSPHERIC_CUTOFF_NO_EM_NO_PLASMA_NO_RADIATION_NO_THRESHOLD_NO_SCORE_NO_RUNTIME_POLICY_NO_CAMPAIGN_MUTATION_LLM_AUTHORITY_ZERO",
        "next_action": "EARN_A_SOURCE_BACKED_ALTITUDE_OR_PARTICLE_PROFILE_BEFORE_NUMERIC_LOCAL_ENVIRONMENT_VALUES",
    }


def main() -> int:
    report = qualification_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
