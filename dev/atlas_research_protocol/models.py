"""Small typed boundary objects for the Atlas Research Protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceCandidate:
    source_id: str
    provider: str
    authority_domain: str
    authority_role: str
    source_type: str
    locator: str
    persistent_identifier: str | None = None
    publication_date: str | None = None
    release_date: str | None = None
    version: str | None = None
    primary_available: bool = False


@dataclass(frozen=True)
class AcquiredArtifact:
    artifact_id: str
    source_id: str
    locator: str
    retrieved_at: str
    sha256: str
    byte_count: int
    media_type: str
    original_filename: str
    version: str | None = None


@dataclass(frozen=True)
class AssertionCandidate:
    assertion_id: str
    source_id: str
    artifact_id: str
    property_code: str
    evidence_class: str
    scope_type: str
    claim_kind: str
    method_type: str
    independent_evidence_lineage_id: str
    reported_unit: str | None = None
    normalized_unit: str | None = None
    reported_value: Any = None
    normalized_value: Any = None
    reported_uncertainty: Any = None
    normalized_uncertainty: Any = None
    uncertainty_unit: str | None = None
    normalization_method: str | None = None
    reported_precision: str | None = None
    value_min: Any = None
    value_max: Any = None
    resolution: dict[str, Any] = field(default_factory=dict)
    region_id: str | None = None
    status: str = "CANDIDATE"
    provenance_complete: bool = True
    canonical_assertion_key: str | None = None


@dataclass(frozen=True)
class FrontierEntry:
    variable: str
    phase: str
    state_at_cutoff: str
    research_coverage: str
    evidence_class: str | None
    limitation: str | None = None
    supporting_assertion_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class Lien:
    lien_id: str
    state: str
    severity: str
    target: str
    finding: str


def dataclass_from_dict(cls: type[Any], value: dict[str, Any]) -> Any:
    """Construct a contract object while keeping JSON the interchange boundary."""
    return cls(**value)
