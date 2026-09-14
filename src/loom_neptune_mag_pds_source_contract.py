"""Source contract for first real Voyager 2 Neptune MAG ingestion.

This freezes the verified source pairing before parser work. It does not parse data,
ingest records, interpolate samples, transform frames, or provide any 2226 endpoint,
admissibility, or Loom-coherence authority.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NeptuneMagPdsSourceContract:
    mag_collection_lidvid: str
    mag_collection_doi: str
    mag_collection_name: str
    mag_sample_cadence_s: float
    mag_coordinate_system: str
    mag_representation: str
    mag_time_start_utc: str
    mag_time_stop_utc: str
    trajectory_collection_name: str
    trajectory_coordinate_system: str
    trajectory_sample_cadence_s: float
    require_matching_trajectory_epoch: bool
    require_source_position: bool
    pairing_rule: str
    frame_transform_authority: str
    interpolation_authority: str
    endpoint_2226_authority: str
    admissibility_authority: str
    loom_coherence_authority: str
    parser_implemented: bool
    real_record_ingested: bool


NEPTUNE_MAG_PDS_SOURCE_CONTRACT = NeptuneMagPdsSourceContract(
    mag_collection_lidvid="urn:nasa:pds:vg2-mag-nep:data-nls-12s-asc::1.0",
    mag_collection_doi="10.17189/e467-dz93",
    mag_collection_name="VG2 MAG Neptune Resampled NLS Coords 12s and SHA Model ASCII Data Collection",
    mag_sample_cadence_s=12.0,
    mag_coordinate_system="NEPTUNE_LONGITUDE_SYSTEM",
    mag_representation="ASCII",
    mag_time_start_utc="1989-08-24T18:00:00.557Z",
    mag_time_stop_utc="1989-08-26T08:19:48.379Z",
    trajectory_collection_name="Voyager 2 Neptune West Longitude System Coords 12s Trajectory Data Collection",
    trajectory_coordinate_system="NEPTUNE_WEST_LONGITUDE_SYSTEM",
    trajectory_sample_cadence_s=12.0,
    require_matching_trajectory_epoch=True,
    require_source_position=True,
    pairing_rule="EXACT_EPOCH_ONLY_NO_INTERPOLATION",
    frame_transform_authority="ZERO",
    interpolation_authority="ZERO",
    endpoint_2226_authority="ZERO",
    admissibility_authority="ZERO",
    loom_coherence_authority="ZERO",
    parser_implemented=False,
    real_record_ingested=False,
)
