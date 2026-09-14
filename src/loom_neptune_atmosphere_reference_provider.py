"""Minimal Neptune atmosphere reference provider.

This provider exposes only the body-level atmospheric classification already
supported by authoritative NASA/Voyager sources. It is deliberately not a
local 2226 endpoint atmosphere model and supplies no density, EM, plasma, or
radiation state.
"""
from __future__ import annotations

from src.loom_planetary_environment import (
    EnvironmentProvenance,
    EnvironmentQuery,
    EnvironmentUncertainty,
    PlanetaryEnvironmentState,
)


class NeptuneAtmosphereReferenceProvider:
    """Reference-only Neptune atmosphere classification; no endpoint authority."""

    SOURCE_IDS = (
        "NASA_NEPTUNE_FACTS",
        "VOYAGER2_RADIO_OCCULTATION",
    )

    def environment_state(self, query: EnvironmentQuery) -> PlanetaryEnvironmentState:
        if query.body_id != "NE":
            raise ValueError("NeptuneAtmosphereReferenceProvider accepts body_id='NE' only")

        return PlanetaryEnvironmentState(
            query=query,
            atmospheric_regime="BULK_REFERENCE_H2_HE_CH4_DOMINATED_ATMOSPHERE",
            mass_density_kg_m3=None,
            magnetic_field_t=None,
            plasma_number_density_m3=None,
            ionizing_radiation_dose_rate_gy_s=None,
            uncertainty=EnvironmentUncertainty(
                model_class="BODY_LEVEL_REFERENCE_ONLY_NO_LOCAL_MODEL",
                numeric_envelope=None,
                notes=(
                    "NO_LOCAL_DENSITY_MODEL",
                    "NO_2226_ATMOSPHERIC_PROFILE",
                    "HISTORIC_VOYAGER_PROFILE_NOT_COPIED_FORWARD",
                ),
            ),
            provenance=EnvironmentProvenance(
                source_ids=self.SOURCE_IDS,
                source_class="NASA_JPL_VOYAGER_REFERENCE_SOURCES",
                qualification="BODY_LEVEL_REFERENCE_ONLY_NOT_LOCAL_2226_ENDPOINT_STATE",
            ),
        )
