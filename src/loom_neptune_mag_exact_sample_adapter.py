"""Exact-sample historical Voyager 2 Neptune MAG adapter.

This adapter maps a source-qualified magnetic-field sample into the ordinary
planetary-environment interface only when body, epoch, frame, and position match
exactly. It provides no spatial interpolation, temporal extrapolation, 2226
endpoint state, Geometric Admissibility, Loom coherence, or runtime authority.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.loom_planetary_environment import (
    EnvironmentProvenance,
    EnvironmentQuery,
    EnvironmentUncertainty,
    PlanetaryEnvironmentState,
    Vector3,
)


@dataclass(frozen=True)
class HistoricalMagneticFieldSample:
    body_id: str
    epoch_utc: str
    reference_frame: str
    position_km: Vector3
    magnetic_field_nt: Vector3
    source_id: str
    sample_cadence_s: float
    coordinate_semantics: str


class NeptuneMagExactSampleProvider:
    """Expose one historical MAG sample with fail-closed exact matching."""

    spatial_interpolation_authority = "ZERO"
    temporal_extrapolation_authority = "ZERO"
    endpoint_2226_authority = "ZERO"
    admissibility_authority = "ZERO"
    loom_coherence_authority = "ZERO"

    def __init__(self, sample: HistoricalMagneticFieldSample):
        if sample.body_id != "NE":
            raise ValueError("Neptune MAG adapter accepts body_id='NE' only")
        if sample.sample_cadence_s <= 0:
            raise ValueError("sample_cadence_s must be positive")
        self.sample = sample

    @staticmethod
    def _nt_to_t(vector_nt: Vector3) -> Vector3:
        return tuple(component * 1.0e-9 for component in vector_nt)  # type: ignore[return-value]

    def environment_state(self, query: EnvironmentQuery) -> PlanetaryEnvironmentState:
        if query.body_id != self.sample.body_id:
            raise ValueError("BODY_MISMATCH_NO_CROSS_BODY_SUBSTITUTION")
        if query.epoch_utc != self.sample.epoch_utc:
            raise ValueError("EPOCH_MISMATCH_NO_TEMPORAL_EXTRAPOLATION")
        if query.reference_frame != self.sample.reference_frame:
            raise ValueError("FRAME_MISMATCH_NO_IMPLICIT_FRAME_TRANSFORM")
        if query.position_km != self.sample.position_km:
            raise ValueError("POSITION_MISMATCH_NO_SPATIAL_INTERPOLATION")

        return PlanetaryEnvironmentState(
            query=query,
            atmospheric_regime=None,
            mass_density_kg_m3=None,
            magnetic_field_t=self._nt_to_t(self.sample.magnetic_field_nt),
            plasma_number_density_m3=None,
            ionizing_radiation_dose_rate_gy_s=None,
            uncertainty=EnvironmentUncertainty(
                model_class="HISTORICAL_MEASURED_EXACT_SAMPLE_NO_INTERPOLATION",
                numeric_envelope=None,
                notes=(
                    f"SOURCE_SAMPLE_CADENCE_S={self.sample.sample_cadence_s}",
                    f"COORDINATE_SEMANTICS={self.sample.coordinate_semantics}",
                    "NO_SOURCE_NUMERIC_UNCERTAINTY_INGESTED_YET",
                    "NO_SPATIAL_INTERPOLATION",
                    "NO_TEMPORAL_EXTRAPOLATION",
                    "NO_2226_PROPAGATION",
                ),
            ),
            provenance=EnvironmentProvenance(
                source_ids=(self.sample.source_id,),
                source_class="NASA_PDS_VOYAGER2_MAG_NEPTUNE_HISTORICAL_EXACT_SAMPLE",
                qualification="HISTORICAL_TRAJECTORY_BOUND_EXACT_SAMPLE_ONLY",
            ),
        )
