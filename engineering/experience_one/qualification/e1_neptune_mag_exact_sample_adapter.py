import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.loom_neptune_mag_exact_sample_adapter import (
    HistoricalMagneticFieldSample,
    NeptuneMagExactSampleProvider,
)
from src.loom_planetary_environment import EnvironmentQuery


sample = HistoricalMagneticFieldSample(
    body_id="NE",
    epoch_utc="1989-08-25T03:56:00Z",
    reference_frame="NEPTUNE_LONGITUDE_SYSTEM",
    position_km=(24765.0, 0.0, 0.0),
    magnetic_field_nt=(100.0, -20.0, 5.0),
    source_id="QUALIFICATION_FIXTURE_NOT_PDS_OBSERVATION",
    sample_cadence_s=12.0,
    coordinate_semantics="R_RADIAL_OUTWARD_PHI_EAST_LONGITUDINAL_THETA_COLATITUDINAL",
)
provider = NeptuneMagExactSampleProvider(sample)
query = EnvironmentQuery(
    body_id=sample.body_id,
    epoch_utc=sample.epoch_utc,
    reference_frame=sample.reference_frame,
    position_km=sample.position_km,
)
state = provider.environment_state(query)

report = {
    "schema": "LOOM_E1_NEPTUNE_MAG_EXACT_SAMPLE_ADAPTER_V1",
    "status": "PASS",
    "body": "NE",
    "classification": "HISTORICAL_EXACT_SAMPLE_ADAPTER_ONLY",
    "source_family": "VOYAGER2_MAG_NEPTUNE",
    "pds_bundle_id": "PDS_URN_NASA_PDS_VG2_MAG_NEP_1_0",
    "pds_bundle_doi": "10.17189/cv12-7d61",
    "pds_bundle_time_coverage_utc": [
        "1989-08-22T00:00:47.663Z",
        "1989-08-30T00:00:44.851Z",
    ],
    "qualified_source_frames": [
        "HELIOGRAPHIC_RTN_SOURCE_FAMILY",
        "NEPTUNE_LONGITUDE_SYSTEM_SOURCE_FAMILY",
    ],
    "nls_coordinate_semantics": "R_RADIAL_OUTWARD_PHI_EAST_LONGITUDINAL_THETA_COLATITUDINAL",
    "adapter_matching_rule": "EXACT_BODY_EPOCH_FRAME_POSITION_OR_FAIL_CLOSED",
    "magnetic_field_vector_output_supported": state.magnetic_field_t is not None,
    "qualification_fixture_is_pds_observation": False,
    "qualification_fixture_purpose": "TEST_UNIT_CONVERSION_AND_FAIL_CLOSED_ADAPTER_BEHAVIOR_ONLY",
    "source_numeric_uncertainty_ingested": False,
    "spatial_interpolation_authority": provider.spatial_interpolation_authority,
    "temporal_extrapolation_authority": provider.temporal_extrapolation_authority,
    "local_2226_endpoint_values_earned": False,
    "endpoint_2226_authority": provider.endpoint_2226_authority,
    "admissibility_authority": provider.admissibility_authority,
    "loom_coherence_authority": provider.loom_coherence_authority,
    "runtime_policy_authority": "ZERO",
    "authority_note": "EXACT_HISTORICAL_SAMPLE_ADAPTER_ONLY_NO_IMPLICIT_FRAME_TRANSFORM_NO_SPATIAL_INTERPOLATION_NO_TEMPORAL_EXTRAPOLATION_NO_2226_PROPAGATION_NO_THRESHOLD_NO_SCORE_NO_RUNTIME_POLICY_NO_CAMPAIGN_MUTATION_LLM_AUTHORITY_ZERO",
    "next_action": "INGEST_ONE_REAL_PDS_MAG_ASCII_COLLECTION_WITH_EXPLICIT_RECORD_PARSER_AND_SOURCE_POSITION_BEFORE_ANY_HISTORICAL_SAMPLE_IS_EXPOSED_AS_DATA",
}

print(json.dumps(report, indent=2, sort_keys=True))
