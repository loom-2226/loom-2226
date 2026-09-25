from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Decision = Literal["PASS", "REVIEW", "REJECT"]


@dataclass(frozen=True)
class RawArtifact:
    artifact_id: str
    original_url: str
    retrieved_at: str
    sha256: str
    byte_count: int
    content_type: str | None
    provider: str | None
    path: str


@dataclass(frozen=True)
class SourceCandidate:
    source_type: str
    provider: str
    title: str
    url: str
    publication_date: str
    retrieved_at: str
    citation_text: str
    persistent_identifier: str | None = None
    doi: str | None = None
    authors: str | None = None
    product_name: str | None = None
    product_version: str | None = None
    raw_artifact: RawArtifact | None = None


@dataclass(frozen=True)
class ObservationCandidate:
    body_id: str
    source_id: str
    mission: str | None = None
    spacecraft: str | None = None
    instrument: str | None = None
    observation_method: str | None = None
    observation_product_id: str | None = None
    observation_time_start: str | None = None
    observation_time_end: str | None = None
    spatial_context: str | None = None
    region_id: int | None = None
    region_ref: str | None = None


@dataclass(frozen=True)
class FactCandidate:
    body_id: str
    source_id: str
    property_code: str
    evidence_class: str
    value_semantics: str
    reported_value_text: str | None
    reported_unit: str | None
    normalized_value: float | None
    normalized_unit: str | None
    uncertainty_plus: float | None = None
    uncertainty_minus: float | None = None
    value_min: float | None = None
    value_max: float | None = None
    region_id: int | None = None
    region_ref: str | None = None
    observation_ref: str | None = None
    measurement_method: str | None = None
    spatial_context: str | None = None
    temporal_context: str | None = None
    confidence_class: str = "UNKNOWN"
    assertion_role: str = "PRIMARY"
    fact_status: str = "CANDIDATE"
    knowledge_valid_from: str | None = None
    knowledge_valid_until: str | None = None
    supersedes_fact_id: int | None = None
    source_locator: str | None = None
    notes: str | None = None
    preferred_fact_requested: bool = False


@dataclass(frozen=True)
class MaterialCandidate:
    body_id: str
    source_id: str
    material_family: str
    evidence_class: str
    region_id: int | None = None
    observation_ref: str | None = None
    region_ref: str | None = None
    material_species: str | None = None
    physical_form: str | None = None
    host_material: str | None = None
    location_context: str | None = None
    abundance_semantics: str = "UNKNOWN"
    abundance_value: float | None = None
    abundance_min: float | None = None
    abundance_max: float | None = None
    abundance_unit: str | None = None
    reported_abundance: str | None = None
    areal_extent: float | None = None
    areal_extent_unit: str | None = None
    measurement_method: str | None = None
    confidence_class: str = "UNKNOWN"
    fact_status: str = "CANDIDATE"
    notes: str | None = None


@dataclass(frozen=True)
class RegionCandidate:
    body_id: str
    source_id: str
    region_type: str
    canonical_name: str | None = None
    region_id: int | None = None
    region_ref: str | None = None
    latitude_min_deg: float | None = None
    latitude_max_deg: float | None = None
    longitude_min_deg: float | None = None
    longitude_max_deg: float | None = None
    reference_frame: str | None = None
    description: str | None = None
    confidence_class: str = "UNKNOWN"
    notes: str | None = None


@dataclass(frozen=True)
class ActivityCandidate:
    body_id: str
    source_id: str
    activity_type: str
    description: str
    evidence_class: str
    region_ref: str | None = None
    observation_ref: str | None = None
    confidence_class: str = "UNKNOWN"
    notes: str | None = None


@dataclass(frozen=True)
class ModelProductCandidate:
    body_id: str
    source_id: str
    model_type: str
    model_name: str
    region_id: int | None = None
    region_ref: str | None = None
    model_version: str | None = None
    reference_frame: str | None = None
    resolution_description: str | None = None
    persistent_identifier: str | None = None
    product_url: str | None = None
    sha256: str | None = None
    byte_count: int | None = None
    notes: str | None = None
    artifact_path: str | None = None


@dataclass(frozen=True)
class GravityModelCandidate:
    body_id: str
    source_id: str
    model_name: str
    model_version: str | None = None
    gravitational_parameter: float | None = None
    gm_unit: str = "km^3/s^2"
    reference_radius: float | None = None
    reference_radius_unit: str = "km"
    maximum_degree: int | None = None
    maximum_order: int | None = None
    normalization: str | None = None
    coefficient_convention: str | None = None
    reference_frame: str | None = None
    reference_epoch: str | None = None
    persistent_identifier: str | None = None
    product_url: str | None = None
    sha256: str | None = None
    byte_count: int | None = None
    validity_notes: str | None = None
    notes: str | None = None
    artifact_path: str | None = None


@dataclass(frozen=True)
class OrientationModelCandidate:
    body_id: str
    source_id: str
    model_name: str
    model_version: str | None = None
    model_authority: str | None = None
    reference_frame: str | None = None
    reference_epoch: str | None = None
    pole_ra_deg: float | None = None
    pole_dec_deg: float | None = None
    pole_ra_rate: float | None = None
    pole_dec_rate: float | None = None
    prime_meridian_deg: float | None = None
    prime_meridian_rate: float | None = None
    rotation_period_seconds: float | None = None
    rotation_state: str | None = None
    libration_model: str | None = None
    persistent_identifier: str | None = None
    product_url: str | None = None
    sha256: str | None = None
    byte_count: int | None = None
    notes: str | None = None
    artifact_path: str | None = None


@dataclass(frozen=True)
class DerivedQuantityCandidate:
    body_id: str
    property_code: str
    value_numeric: float
    unit: str
    derivation_method: str
    derivation_version: str
    input_property_codes: tuple[str, ...]
    reference_epoch: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class StagingRecord:
    source: SourceCandidate
    observations: tuple[ObservationCandidate, ...] = ()
    facts: tuple[FactCandidate, ...] = ()
    materials: tuple[MaterialCandidate, ...] = ()
    regions: tuple[RegionCandidate, ...] = ()
    model_products: tuple[ModelProductCandidate, ...] = ()
    gravity_models: tuple[GravityModelCandidate, ...] = ()
    derived_quantities: tuple[DerivedQuantityCandidate, ...] = ()
    activities: tuple[ActivityCandidate, ...] = ()
    orientation_models: tuple[OrientationModelCandidate, ...] = ()
    extractor_name: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    decision: Decision


@dataclass(frozen=True)
class ValidationReport:
    decision: Decision
    findings: tuple[Finding, ...]
