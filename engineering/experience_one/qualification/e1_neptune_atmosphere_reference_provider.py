#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.loom_neptune_atmosphere_reference_provider import NeptuneAtmosphereReferenceProvider
from src.loom_planetary_environment import EnvironmentQuery


def qualification_report() -> dict[str, object]:
    query = EnvironmentQuery(
        body_id="NE",
        epoch_utc="2226-08-22T09:07:59Z",
        reference_frame="J2000",
        position_km=(26085.768742219727, 0.0, 0.0),
    )
    state = NeptuneAtmosphereReferenceProvider().environment_state(query)

    unearned_values_absent = all(
        value is None
        for value in (
            state.mass_density_kg_m3,
            state.magnetic_field_t,
            state.plasma_number_density_m3,
            state.ionizing_radiation_dose_rate_gy_s,
        )
    )
    reference_only = (
        state.provenance.qualification
        == "BODY_LEVEL_REFERENCE_ONLY_NOT_LOCAL_2226_ENDPOINT_STATE"
    )
    status = "PASS" if unearned_values_absent and reference_only else "FAIL"

    return {
        "schema": "LOOM_E1_NEPTUNE_ATMOSPHERE_REFERENCE_PROVIDER_V1",
        "status": status,
        "body": query.body_id,
        "classification": "BODY_LEVEL_ATMOSPHERE_REFERENCE_ONLY",
        "atmospheric_regime": state.atmospheric_regime,
        "source_ids": list(state.provenance.source_ids),
        "qualification": state.provenance.qualification,
        "numeric_uncertainty_envelope": state.uncertainty.numeric_envelope,
        "uncertainty_notes": list(state.uncertainty.notes),
        "local_endpoint_values_earned": False,
        "unearned_values_absent": unearned_values_absent,
        "admissibility_authority": "ZERO",
        "loom_coherence_authority": "ZERO",
        "authority_note": "REFERENCE_ONLY_NO_LOCAL_2226_DENSITY_NO_EM_NO_PLASMA_NO_RADIATION_NO_THRESHOLD_NO_SCORE_NO_RUNTIME_POLICY_NO_CAMPAIGN_MUTATION_LLM_AUTHORITY_ZERO",
        "next_action": "EARN_A_LOCAL_SPATIAL_ATMOSPHERE_OR_PARTICLE_MODEL_SEPARATELY_BEFORE_ENDPOINT_USE",
    }


def main() -> int:
    report = qualification_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
