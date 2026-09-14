#!/usr/bin/env python3
from __future__ import annotations

"""Bounded Neptune environmental-source gap analysis for E1.

This is external-research synthesis only. It classifies which missing Geometric
Admissibility input families have established planetary-science source paths,
which remain epoch/location sensitive, and which are LOOM-specific unresolved
physics. It does not create a 2226 Neptune endpoint state, threshold, score, or
runtime metric policy.
"""

import json
from typing import Any


SOURCES: dict[str, dict[str, str]] = {
    "NASA_NEPTUNE_FACTS": {
        "authority": "NASA Science",
        "title": "Neptune: Facts",
        "url": "https://science.nasa.gov/neptune/neptune-facts/",
        "supports": "bulk atmospheric composition and established descriptive atmosphere context",
    },
    "VOYAGER2_RADIO_OCCULTATION": {
        "authority": "NASA Technical Reports Server / Voyager 2",
        "title": "The atmosphere of Neptune - Results of radio occultation measurements with the Voyager 2 spacecraft",
        "url": "https://ntrs.nasa.gov/citations/19900065496",
        "supports": "historic vertical temperature/composition profiles from the 1989 occultation",
    },
    "PDS_VG2_PLS_NEPTUNE": {
        "authority": "NASA Planetary Data System",
        "title": "Voyager 2 PLS Neptune 48s In/Out Bound Magnetospheric Proton Data Collection",
        "url": "https://pds.nasa.gov/ds-view/pds/viewCollection.jsp?identifier=urn:nasa:pds:vg2-pls-nep:data-pro-magsphere&version=1.0",
        "supports": "historic derived proton density, temperature, and velocity measurements during the 1989 encounter",
    },
    "PDS_VG2_MAG_NEPTUNE": {
        "authority": "NASA Planetary Data System",
        "title": "VG2 MAG Neptune Encounter Document Collection",
        "url": "https://pds.nasa.gov/ds-view/pds/viewCollection.jsp?identifier=urn:nasa:pds:vg2-mag-nep:document&version=1.0",
        "supports": "historic Voyager 2 Neptune magnetic-field encounter data lineage",
    },
    "PDS_VG2_PWS_NEPTUNE": {
        "authority": "NASA Planetary Data System",
        "title": "VG2 NEP PWS Resampled Summary Spectrum Analyzer 48sec V1.0",
        "url": "https://pds.nasa.gov/ds-view/pds/viewDataset.jsp?dsid=VG2-N-PWS-4-SUMM-SA-48SEC-V1.0",
        "supports": "historic calibrated wave electric-field intensities in the Neptune magnetosphere",
    },
    "NTRS_PARTICLES_FIELDS_NEPTUNE": {
        "authority": "NASA Technical Reports Server",
        "title": "Particles and fields measurements at Neptune with Voyager 2",
        "url": "https://ntrs.nasa.gov/citations/19920062659",
        "supports": "historic magnetic-field, plasma, particles, plasma-wave and radio-emission measurements; plasma density order-of-magnitude context",
    },
    "NTRS_ENERGETIC_PARTICLES_NEPTUNE": {
        "authority": "NASA Technical Reports Server",
        "title": "Energetic charged particles in the magnetosphere of Neptune",
        "url": "https://ntrs.nasa.gov/citations/19900031380",
        "supports": "historic energetic electron/proton flux structure in the Neptune magnetosphere",
    },
    "JPL_HORIZONS_LIMITATIONS": {
        "authority": "NASA/JPL Solar System Dynamics",
        "title": "Horizons System Manual - Statement of Ephemeris Limitations",
        "url": "https://ssd.jpl.nasa.gov/horizons/manual.html",
        "supports": "ephemeris/model uncertainty is real, time-varying, and not represented by printed numeric precision alone",
    },
}


def _source(*ids: str) -> list[dict[str, str]]:
    return [{"id": source_id, **SOURCES[source_id]} for source_id in ids]


def build_source_gap_report() -> dict[str, Any]:
    families: dict[str, dict[str, Any]] = {
        "atmospheric_classification": {
            "disposition": "SOURCEABLE_ESTABLISHED",
            "qualified_for_2226_endpoint": False,
            "sources": _source("NASA_NEPTUNE_FACTS", "VOYAGER2_RADIO_OCCULTATION"),
            "what_is_earned": "Neptune has an established H2/He/CH4-dominated atmosphere and historic vertical atmospheric measurements.",
            "remaining_gap": "No governed LOOM field yet maps this source lineage into the 2226 endpoint environment.",
            "guardrails": [
                "BULK_COMPOSITION_IS_NOT_LOCAL_ENDPOINT_DENSITY",
                "HISTORIC_1989_PROFILE_IS_NOT_AUTOMATICALLY_2226_STATE",
            ],
        },
        "local_matter_density": {
            "disposition": "SOURCEABLE_BUT_EPOCH_AND_LOCATION_SENSITIVE",
            "qualified_for_2226_endpoint": False,
            "sources": _source("PDS_VG2_PLS_NEPTUNE", "NTRS_PARTICLES_FIELDS_NEPTUNE", "VOYAGER2_RADIO_OCCULTATION"),
            "what_is_earned": "Historic atmospheric and magnetospheric particle-density measurements exist.",
            "remaining_gap": "A local density at a proposed collapse endpoint requires a spatial/altitude regime and an epoch-aware environmental model; encounter samples cannot be copied forward to 2226.",
            "guardrails": [
                "VOYAGER_SAMPLE_IS_NOT_2226_ENDPOINT_STATE",
                "ATMOSPHERIC_AND_MAGNETOSPHERIC_DENSITY_REGIMES_MUST_NOT_BE_CONFLATED",
            ],
        },
        "electromagnetic_environment": {
            "disposition": "SOURCEABLE_BUT_EPOCH_AND_LOCATION_SENSITIVE",
            "qualified_for_2226_endpoint": False,
            "sources": _source(
                "PDS_VG2_MAG_NEPTUNE",
                "PDS_VG2_PWS_NEPTUNE",
                "NTRS_PARTICLES_FIELDS_NEPTUNE",
                "NTRS_ENERGETIC_PARTICLES_NEPTUNE",
            ),
            "what_is_earned": "Historic Neptune magnetic-field, plasma-wave, charged-particle, and radiation-belt observations exist.",
            "remaining_gap": "The Neptune field is spatially complex and the local EM/particle environment is not a static scalar. LOOM lacks an epoch/location-resolved 2226 environment model at the candidate endpoint.",
            "guardrails": [
                "MAGNETIC_FIELD_IS_VECTOR_AND_LOCATION_DEPENDENT",
                "RADIATION_AND_PLASMA_ENVIRONMENT_IS_NOT_STATIC",
                "HISTORIC_ENCOUNTER_DATA_REQUIRES_MODEL_BEFORE_2226_USE",
            ],
        },
        "physical_uncertainty": {
            "disposition": "REQUIRES_EXPLICIT_MODEL_UNCERTAINTY",
            "qualified_for_2226_endpoint": False,
            "sources": _source("JPL_HORIZONS_LIMITATIONS"),
            "what_is_earned": "Authoritative ephemeris systems explicitly recognize observation/model error and time-varying uncertainty.",
            "remaining_gap": "LOOM currently carries provenance/navigation grade but not a qualified numerical uncertainty envelope for the complete 2226 endpoint environment.",
            "guardrails": [
                "PRINTED_PRECISION_IS_NOT_PHYSICAL_ACCURACY",
                "NAVIGATION_GRADE_IS_NOT_A_COMPLETE_ENVIRONMENTAL_UNCERTAINTY_MODEL",
            ],
        },
        "loom_coherence": {
            "disposition": "UNRESOLVED_LOOM_SPECIFIC_PHYSICS",
            "qualified_for_2226_endpoint": False,
            "sources": [],
            "what_is_earned": "No external planetary-science source establishes a Loom coherence observable or metric-admissibility threshold.",
            "remaining_gap": "Must remain unresolved until governed LOOM/RF research earns a physical observable and qualification path.",
            "guardrails": [
                "NO_EXTERNAL_PLANETARY_SCIENCE_PROXY",
                "NO_RF_THRESHOLD_INVENTION",
                "NO_FICTIONAL_CALIBRATION_FROM_MISSING_DATA",
            ],
        },
    }

    return {
        "schema": "LOOM_E1_NEPTUNE_ENVIRONMENT_SOURCE_GAP_V1",
        "status": "PASS",
        "body": "NE",
        "classification": "EXTERNAL_RESEARCH_SYNTHESIS_DATA_ACQUISITION_GAP_ONLY",
        "families": families,
        "blocking_families": [
            "local_matter_density",
            "electromagnetic_environment",
            "physical_uncertainty",
            "loom_coherence",
        ],
        "compound_admissibility_model": "BLOCKED",
        "metric_policy_adoption": "BLOCKED",
        "authority_note": "RESEARCH_SYNTHESIS_ONLY_NO_2226_ENDPOINT_STATE_NO_THRESHOLD_NO_SCORE_NO_RUNTIME_POLICY_NO_CAMPAIGN_MUTATION_LLM_AUTHORITY_ZERO",
        "interpretation": "ESTABLISHED_SOURCEABILITY_DOES_NOT_EQUAL_2226_ENDPOINT_QUALIFICATION",
        "next_action": "DEFINE_GOVERNED_ENVIRONMENT_MODEL_INPUTS_BEFORE_ANY_COMPOUND_GEOMETRIC_ADMISSIBILITY_FUNCTION",
    }


def main() -> int:
    print(json.dumps(build_source_gap_report(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
