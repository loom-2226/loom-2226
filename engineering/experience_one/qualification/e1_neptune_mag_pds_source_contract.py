import json

from src.loom_neptune_mag_pds_source_contract import NEPTUNE_MAG_PDS_SOURCE_CONTRACT as c

report = {
    "schema": "LOOM_E1_NEPTUNE_MAG_PDS_SOURCE_CONTRACT_V1",
    "status": "PASS",
    "mag_collection_lidvid": c.mag_collection_lidvid,
    "mag_collection_doi": c.mag_collection_doi,
    "mag_collection_name": c.mag_collection_name,
    "mag_sample_cadence_s": c.mag_sample_cadence_s,
    "mag_coordinate_system": c.mag_coordinate_system,
    "mag_representation": c.mag_representation,
    "mag_time_coverage_utc": [c.mag_time_start_utc, c.mag_time_stop_utc],
    "trajectory_collection_name": c.trajectory_collection_name,
    "trajectory_coordinate_system": c.trajectory_coordinate_system,
    "trajectory_sample_cadence_s": c.trajectory_sample_cadence_s,
    "source_position_required": c.require_source_position,
    "trajectory_epoch_match_required": c.require_matching_trajectory_epoch,
    "pairing_rule": c.pairing_rule,
    "frame_transform_authority": c.frame_transform_authority,
    "interpolation_authority": c.interpolation_authority,
    "parser_implemented": c.parser_implemented,
    "real_record_ingested": c.real_record_ingested,
    "endpoint_2226_authority": c.endpoint_2226_authority,
    "admissibility_authority": c.admissibility_authority,
    "loom_coherence_authority": c.loom_coherence_authority,
    "next_action": "FETCH_PDS4_COLLECTION_LABELS_AND_DATA_MEMBERS_THEN_IMPLEMENT_EXPLICIT_ASCII_RECORD_PARSER_WITH_EXACT_EPOCH_TRAJECTORY_JOIN",
}
print(json.dumps(report, indent=2, sort_keys=True))
