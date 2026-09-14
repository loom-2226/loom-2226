"""Historical Neptune atmosphere reference anchors from Voyager 2 radio occultation.

These anchors preserve only discrete values explicitly supported by the source lineage.
They do not define a continuous atmospheric profile, density law, 2226 endpoint state,
Geometric Admissibility, Loom coherence, or metric policy.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NeptuneAtmosphereReferenceAnchor:
    anchor_id: str
    altitude_from_one_bar_km: float
    pressure_pa: float
    temperature_k: float
    temperature_uncertainty_k: float
    h2_number_fraction_min: float | None
    h2_number_fraction_max: float | None
    source_ids: tuple[str, ...]
    source_epoch_class: str
    qualified_for_2226_endpoint: bool
    interpolation_authority: str
    extrapolation_authority: str
    notes: tuple[str, ...]


NEPTUNE_VOYAGER2_REFERENCE_ANCHORS: tuple[NeptuneAtmosphereReferenceAnchor, ...] = (
    NeptuneAtmosphereReferenceAnchor(
        anchor_id="VOYAGER2_NEPTUNE_1BAR_REFERENCE",
        altitude_from_one_bar_km=0.0,
        pressure_pa=100_000.0,
        temperature_k=72.0,
        temperature_uncertainty_k=2.0,
        h2_number_fraction_min=None,
        h2_number_fraction_max=None,
        source_ids=("LINDAL_1992_AJ_NEPTUNE_OCCULTATION",),
        source_epoch_class="VOYAGER2_1989_HISTORICAL_REFERENCE",
        qualified_for_2226_endpoint=False,
        interpolation_authority="ZERO",
        extrapolation_authority="ZERO",
        notes=(
            "ONE_BAR_LEVEL_IS_A_PRESSURE_REFERENCE_NOT_A_SOLID_SURFACE",
            "HISTORICAL_OCCULTATION_REFERENCE_NOT_2226_ENDPOINT_STATE",
        ),
    ),
    NeptuneAtmosphereReferenceAnchor(
        anchor_id="VOYAGER2_NEPTUNE_TROPOPAUSE_REFERENCE",
        altitude_from_one_bar_km=40.0,
        pressure_pa=10_000.0,
        temperature_k=52.0,
        temperature_uncertainty_k=2.0,
        h2_number_fraction_min=0.78,
        h2_number_fraction_max=0.84,
        source_ids=(
            "LINDAL_1992_AJ_NEPTUNE_OCCULTATION",
            "LINDAL_ET_AL_1990_GRL_NEPTUNE_OCCULTATION",
        ),
        source_epoch_class="VOYAGER2_1989_HISTORICAL_REFERENCE",
        qualified_for_2226_endpoint=False,
        interpolation_authority="ZERO",
        extrapolation_authority="ZERO",
        notes=(
            "TROPOPAUSE_APPROX_40_KM_ABOVE_ONE_BAR_LEVEL",
            "PRESSURE_APPROX_100_MBAR",
            "H2_NUMBER_FRACTION_RANGE_FROM_OCCULTATION_PLUS_IR_COMPARISON",
            "HISTORICAL_OCCULTATION_REFERENCE_NOT_2226_ENDPOINT_STATE",
        ),
    ),
)


def reference_anchor_by_id(anchor_id: str) -> NeptuneAtmosphereReferenceAnchor:
    for anchor in NEPTUNE_VOYAGER2_REFERENCE_ANCHORS:
        if anchor.anchor_id == anchor_id:
            return anchor
    raise KeyError(anchor_id)
