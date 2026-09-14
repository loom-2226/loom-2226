"""Neptune-relative reference geometry layered onto ordinary environment state.

This module derives only Neptune-relative radius against the existing navigation-grade
celestial-state authority and a qualified mean-radius reference. It does not define an
atmospheric cutoff, density profile, local 2226 atmosphere, EM/plasma/radiation state,
Geometric Admissibility, Loom coherence, or metric policy.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Protocol

from src.loom_neptune_atmosphere_reference import NeptuneAtmosphereReferenceProvider
from src.loom_planetary_environment import EnvironmentQuery, PlanetaryEnvironmentState
from src.loom_spatial_state_authority import CANONICAL_FRAME, SpatialState

NEPTUNE_REFERENCE_MEAN_RADIUS_KM = 24622.0


class CelestialResolver(Protocol):
    def resolve(self, entity_id: str, epoch_utc: str) -> SpatialState | None:
        ...


@dataclass(frozen=True)
class NeptuneSpatialAtmosphereAssessment:
    relative_radius_km: float
    altitude_from_reference_mean_radius_km: float
    reference_mean_radius_km: float
    geometry_regime: str


class NeptuneSpatialAtmosphereProvider:
    """Reference-only Neptune environment provider with body-relative geometry."""

    def __init__(
        self,
        celestial_resolver: CelestialResolver,
        *,
        reference_mean_radius_km: float = NEPTUNE_REFERENCE_MEAN_RADIUS_KM,
    ) -> None:
        radius = float(reference_mean_radius_km)
        if not math.isfinite(radius) or radius <= 0.0:
            raise ValueError("reference_mean_radius_km must be finite and positive")
        self._resolver = celestial_resolver
        self._reference_mean_radius_km = radius
        self._reference_environment = NeptuneAtmosphereReferenceProvider()

    def _relative_vector(self, query: EnvironmentQuery) -> tuple[float, float, float]:
        if query.body_id != "NE":
            raise ValueError("NeptuneSpatialAtmosphereProvider only supports body_id='NE'")
        if query.reference_frame != CANONICAL_FRAME:
            raise ValueError(f"query reference_frame must be {CANONICAL_FRAME}")

        center = self._resolver.resolve("NE", query.epoch_utc)
        if center is None:
            raise ValueError("no Neptune center state available for requested epoch")
        if center.reference_frame != CANONICAL_FRAME:
            raise ValueError("Neptune center is not in canonical celestial frame")
        if center.navigation_grade is not True:
            raise ValueError("Neptune center must be navigation-grade")
        if center.epoch_utc != query.epoch_utc:
            raise ValueError("Neptune center epoch does not match environment query epoch")

        return tuple(float(query.position_km[i]) - float(center.position_km[i]) for i in range(3))

    def spatial_assessment(self, query: EnvironmentQuery) -> NeptuneSpatialAtmosphereAssessment:
        relative = self._relative_vector(query)
        radius = math.sqrt(sum(component * component for component in relative))
        altitude = radius - self._reference_mean_radius_km
        tolerance = 1e-9
        if altitude > tolerance:
            regime = "ABOVE_REFERENCE_MEAN_RADIUS_GEOMETRY"
        elif altitude < -tolerance:
            regime = "INSIDE_REFERENCE_MEAN_RADIUS_GEOMETRY"
        else:
            regime = "AT_REFERENCE_MEAN_RADIUS_GEOMETRY"
        return NeptuneSpatialAtmosphereAssessment(
            relative_radius_km=radius,
            altitude_from_reference_mean_radius_km=altitude,
            reference_mean_radius_km=self._reference_mean_radius_km,
            geometry_regime=regime,
        )

    def environment_state(self, query: EnvironmentQuery) -> PlanetaryEnvironmentState:
        assessment = self.spatial_assessment(query)
        base = self._reference_environment.environment_state(query)
        return PlanetaryEnvironmentState(
            query=query,
            atmospheric_regime=base.atmospheric_regime,
            mass_density_kg_m3=None,
            magnetic_field_t=None,
            plasma_number_density_m3=None,
            ionizing_radiation_dose_rate_gy_s=None,
            uncertainty=type(base.uncertainty)(
                model_class="NEPTUNE_RELATIVE_REFERENCE_GEOMETRY_ONLY",
                numeric_envelope=None,
                notes=base.uncertainty.notes
                + (
                    "MEAN_RADIUS_IS_REFERENCE_GEOMETRY_NOT_ATMOSPHERIC_BOUNDARY",
                    f"GEOMETRY_REGIME={assessment.geometry_regime}",
                    "NO_LOCAL_DENSITY_MODEL",
                ),
            ),
            provenance=type(base.provenance)(
                source_ids=base.provenance.source_ids + ("CELESTIAL_STATE_AUTHORITY", "REFERENCE_PHYSICAL_CONSTANTS_v0.1"),
                source_class="BODY_LEVEL_ATMOSPHERE_REFERENCE_PLUS_NAVIGATION_GRADE_RELATIVE_GEOMETRY",
                qualification="RELATIVE_GEOMETRY_ONLY_NOT_LOCAL_2226_ATMOSPHERIC_STATE",
            ),
        )
