"""Typed ordinary planetary-environment seam for Navigator-adjacent use.

This module defines data contracts only. It does not implement a Neptune model,
calculate Geometric Admissibility, expose Loom coherence, choose collapse radii,
or mutate campaign/runtime state.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

Vector3 = tuple[float, float, float]


@dataclass(frozen=True)
class EnvironmentQuery:
    body_id: str
    epoch_utc: str
    reference_frame: str
    position_km: Vector3


@dataclass(frozen=True)
class EnvironmentUncertainty:
    model_class: str
    numeric_envelope: dict[str, float] | None
    notes: tuple[str, ...]


@dataclass(frozen=True)
class EnvironmentProvenance:
    source_ids: tuple[str, ...]
    source_class: str
    qualification: str


@dataclass(frozen=True)
class PlanetaryEnvironmentState:
    query: EnvironmentQuery
    atmospheric_regime: str | None
    mass_density_kg_m3: float | None
    magnetic_field_t: Vector3 | None
    plasma_number_density_m3: float | None
    ionizing_radiation_dose_rate_gy_s: float | None
    uncertainty: EnvironmentUncertainty
    provenance: EnvironmentProvenance


class PlanetaryEnvironmentProvider(Protocol):
    """Ordinary-physics provider contract; no metric/admissibility authority."""

    def environment_state(self, query: EnvironmentQuery) -> PlanetaryEnvironmentState:
        ...
