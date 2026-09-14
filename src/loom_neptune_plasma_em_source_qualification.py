def qualification_report():
    return {
        "schema": "LOOM_E1_NEPTUNE_PLASMA_EM_SOURCE_QUALIFICATION_V1",
        "status": "PASS",
        "body": "NE",
        "classification": "HISTORICAL_MACHINE_READABLE_SOURCE_QUALIFICATION_ONLY",
        "historic_machine_readable_sources_found": True,
        "source_epoch_class": "VOYAGER2_1989_NEPTUNE_ENCOUNTER",
        "source_families": [
            "VOYAGER2_PLS_NEPTUNE",
            "VOYAGER2_MAG_NEPTUNE",
            "VOYAGER2_PWS_NEPTUNE",
            "VOYAGER2_LECP_NEPTUNE",
        ],
        "earned_observables": {
            "PLS": [
                "ion_density",
                "ion_temperature",
                "ion_velocity",
                "electron_moments_or_spectral_fits_where_available",
            ],
            "MAG": [
                "magnetic_field_vector_along_voyager_trajectory",
            ],
            "PWS": [
                "wave_electric_field_spectral_intensity_along_voyager_trajectory",
            ],
            "LECP": [
                "energetic_particle_counting_rates_or_flux_along_voyager_trajectory",
            ],
        },
        "source_scope": {
            "PLS": "derived Neptune encounter plasma products including solar wind, magnetosheath, and magnetosphere intervals",
            "MAG": "Neptune encounter magnetic-field data in heliographic and Neptune longitude system coordinates at resampled rates",
            "PWS": "Neptune encounter plasma-wave electric-field spectral measurements",
            "LECP": "Neptune encounter low-energy charged-particle counting-rate/flux measurements",
        },
        "trajectory_binding": "VOYAGER2_SPACECRAFT_TRAJECTORY_AND_1989_ENCOUNTER_EPOCH",
        "local_2226_endpoint_values_earned": False,
        "endpoint_authority": "ZERO",
        "spatial_interpolation_authority": "ZERO",
        "temporal_extrapolation_authority": "ZERO",
        "admissibility_authority": "ZERO",
        "loom_coherence_authority": "ZERO",
        "runtime_policy_authority": "ZERO",
        "authority_note": "HISTORICAL_MACHINE_READABLE_SOURCES_EXIST_BUT_ARE_TRAJECTORY_AND_EPOCH_BOUND_NO_2226_PROPAGATION_NO_SPATIAL_INTERPOLATION_NO_THRESHOLD_NO_SCORE_NO_RUNTIME_POLICY_NO_CAMPAIGN_MUTATION_LLM_AUTHORITY_ZERO",
        "next_action": "INGEST_OR_ADAPT_ONE_PDS_MACHINE_READABLE_SOURCE_FAMILY_WITH_EXPLICIT_TIME_POSITION_FRAME_AND_UNCERTAINTY_BEFORE_ANY_LOCAL_PROVIDER_OUTPUT",
        "source_ids": [
            "PDS_URN_NASA_PDS_VG2_PLS_NEP_1_0",
            "PDS_URN_NASA_PDS_VG2_MAG_NEP_1_0",
            "PDS_VG2_NEP_PWS_EDITED_SPECTRUM_ANALYZER_4SEC_V1_0",
            "PDS_VG2_LECP_NEPTUNE_ENCOUNTER_PRODUCTS",
        ],
    }
