from __future__ import annotations

import hashlib
import itertools
import json
import math
from dataclasses import asdict, dataclass
from typing import Dict, Iterable, Tuple

from governed_ship_synthesis import GovernedSynthesisPackage, SpatialRegion, validate_package
from semantic_geometry import (
    SEMANTIC_CLASS_ADMITTED_ENVELOPE,
    SemanticGeometryPackage,
    validate_semantic_geometry,
)

SPATIAL_VALIDATION_VERSION = "LOOM_MINIMUM_SPATIAL_VALIDATION_R2_v0.1"
SPATIAL_VALIDATION_AUTHORITY = "DERIVED_SPATIAL_VALIDATION_EVIDENCE_ONLY"
SPATIAL_VALIDATION_STATUS = (
    "ENGINEERING_RESEARCH",
    "NON_CANON",
    "NON_PRODUCTION",
    "NO_FLIGHT_DYNAMICS_AUTHORITY",
    "NO_STRUCTURAL_QUALIFICATION",
    "NO_BACKPROP_TO_DESIGN_STATE",
)

CHECK_PASS = "PASS_WITHIN_R2_SCOPE"
CHECK_OPEN = "OPEN_MISSING_ADMITTED_RULE"
CHECK_REVIEW = "REVIEW_REQUIRED_OVERLAP_OR_CONTACT"

READINESS_READY = "READY_FOR_NON_AUTHORITATIVE_VISUAL_REALIZATION"
READINESS_BLOCKED = "BLOCKED_FOR_VISUAL_REALIZATION_BY_OPEN_OR_REVIEW"

PAIRWISE_OVERLAP = "ADMITTED_ENVELOPE_PAIRWISE_OVERLAP"
DECLARED_CLEARANCE = "DECLARED_CLEARANCE_RULE_COVERAGE"
DEPLOYMENT_INTERFERENCE = "DEPLOYMENT_ENVELOPE_COVERAGE"
THRUST_PLUME = "THRUST_PLUME_EXCLUSION_COVERAGE"
DOCKING_ACCESS = "DOCKING_ACCESS_ENVELOPE_COVERAGE"
OPEN_HANDLING = "SOURCE_OPEN_ITEM_PRESERVATION"


class MinimumSpatialValidationError(ValueError):
    """Fail-closed error for R2 minimum spatial validation."""


def _sha(payload: object) -> str:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _finite_vec3(values: Iterable[float], label: str) -> Tuple[float, float, float]:
    out = tuple(float(v) for v in values)
    if len(out) != 3 or any(not math.isfinite(v) for v in out):
        raise MinimumSpatialValidationError(f"{label} must contain three finite values")
    return out  # type: ignore[return-value]


@dataclass(frozen=True)
class SpatialValidationCheck:
    check_id: str
    check_type: str
    status: str
    subject_ids: Tuple[str, ...]
    metric_m: Tuple[float, float, float]
    evidence_basis: str
    detail: str
    authority_status: str = SPATIAL_VALIDATION_AUTHORITY


@dataclass(frozen=True)
class MinimumSpatialValidationPackage:
    version: str
    source_design_candidate_id: str
    source_governed_package_hash: str
    source_semantic_package_hash: str
    checks: Tuple[SpatialValidationCheck, ...]
    preserved_open_items: Tuple[str, ...]
    readiness_status: str
    visual_realization_ready: bool
    package_hash: str
    authority_status: str = SPATIAL_VALIDATION_AUTHORITY
    flight_dynamics_authority: bool = False
    structural_qualification: bool = False
    canon_changed: bool = False
    production_shipclasses_changed: bool = False
    design_state_mutated: bool = False


def _region_semantic_ids(
    source: GovernedSynthesisPackage,
    semantic: SemanticGeometryPackage,
) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for obj in semantic.objects:
        if obj.semantic_class != SEMANTIC_CLASS_ADMITTED_ENVELOPE:
            continue
        if obj.source_object_id in mapping:
            raise MinimumSpatialValidationError(f"duplicate semantic region mapping {obj.source_object_id}")
        mapping[obj.source_object_id] = obj.semantic_object_id
    expected = {row.region_id for row in source.packaging.regions}
    if set(mapping) != expected:
        raise MinimumSpatialValidationError("R2 requires complete semantic mapping for admitted packaging regions")
    return mapping


def _axis_interval(region: SpatialRegion, axis: int) -> Tuple[float, float]:
    center = _finite_vec3(region.center_m, f"{region.region_id}.center_m")[axis]
    dims = _finite_vec3(region.dimensions_m, f"{region.region_id}.dimensions_m")
    size = dims[axis]
    if size <= 0.0:
        raise MinimumSpatialValidationError(f"{region.region_id} has non-positive spatial dimension")
    half = size / 2.0
    return center - half, center + half


def _signed_axis_separation(a: SpatialRegion, b: SpatialRegion, axis: int) -> float:
    alo, ahi = _axis_interval(a, axis)
    blo, bhi = _axis_interval(b, axis)
    if ahi < blo:
        return blo - ahi
    if bhi < alo:
        return alo - bhi
    return -min(ahi, bhi) + max(alo, blo)


def _pair_check(a: SpatialRegion, b: SpatialRegion, semantic_ids: Dict[str, str]) -> SpatialValidationCheck:
    sep = tuple(_signed_axis_separation(a, b, axis) for axis in range(3))
    # An overlap/contact condition exists only when no axis has positive separation.
    overlap_or_contact = all(value <= 0.0 for value in sep)
    status = CHECK_REVIEW if overlap_or_contact else CHECK_PASS
    detail = (
        "Admitted axis-aligned packaging envelopes overlap or contact in all three axes. R2 cannot infer whether the relationship is allowed, nested, joined, or prohibited; engineering review/rule evidence is required."
        if overlap_or_contact
        else "Admitted axis-aligned packaging envelopes are separated on at least one axis; no envelope overlap is detected by the R2 conservative AABB screen."
    )
    subjects = tuple(sorted((semantic_ids[a.region_id], semantic_ids[b.region_id])))
    return SpatialValidationCheck(
        check_id=f"R2::PAIR::{subjects[0]}::{subjects[1]}",
        check_type=PAIRWISE_OVERLAP,
        status=status,
        subject_ids=subjects,
        metric_m=sep,  # positive = gap on that axis; <=0 = contact/overlap on that axis
        evidence_basis="ADMITTED_PACKAGING_REGION_AABB_ONLY",
        detail=detail,
    )


def _open_rule_check(check_type: str, detail: str) -> SpatialValidationCheck:
    return SpatialValidationCheck(
        check_id=f"R2::OPEN::{check_type}",
        check_type=check_type,
        status=CHECK_OPEN,
        subject_ids=(),
        metric_m=(0.0, 0.0, 0.0),
        evidence_basis="NO_ADMITTED_RULE_OR_ENVELOPE_IN_CURRENT_GOVERNED_SOURCE",
        detail=detail,
    )


def _hash_without_hash(package: MinimumSpatialValidationPackage) -> str:
    payload = asdict(package)
    payload["package_hash"] = ""
    return _sha(payload)


def validate_minimum_spatial_validation(
    package: MinimumSpatialValidationPackage,
    source: GovernedSynthesisPackage,
    semantic: SemanticGeometryPackage,
) -> None:
    validate_package(source)
    validate_semantic_geometry(semantic, source)
    if package.version != SPATIAL_VALIDATION_VERSION:
        raise MinimumSpatialValidationError("R2 version mismatch")
    if package.authority_status != SPATIAL_VALIDATION_AUTHORITY:
        raise MinimumSpatialValidationError("R2 authority escalation")
    if (
        package.flight_dynamics_authority
        or package.structural_qualification
        or package.canon_changed
        or package.production_shipclasses_changed
        or package.design_state_mutated
    ):
        raise MinimumSpatialValidationError("R2 may not mutate or escalate engineering authority")
    if package.source_design_candidate_id != source.design_state.candidate_id:
        raise MinimumSpatialValidationError("candidate id mismatch")
    if package.source_governed_package_hash != source.package_hash:
        raise MinimumSpatialValidationError("governed package hash mismatch")
    if package.source_semantic_package_hash != semantic.package_hash:
        raise MinimumSpatialValidationError("semantic package hash mismatch")
    if package.preserved_open_items != semantic.open_semantic_items:
        raise MinimumSpatialValidationError("R2 must preserve source OPEN items exactly")

    ids = [row.check_id for row in package.checks]
    if len(ids) != len(set(ids)):
        raise MinimumSpatialValidationError("duplicate R2 check id")
    allowed_status = {CHECK_PASS, CHECK_OPEN, CHECK_REVIEW}
    allowed_type = {
        PAIRWISE_OVERLAP,
        DECLARED_CLEARANCE,
        DEPLOYMENT_INTERFERENCE,
        THRUST_PLUME,
        DOCKING_ACCESS,
        OPEN_HANDLING,
    }
    for row in package.checks:
        if row.authority_status != SPATIAL_VALIDATION_AUTHORITY:
            raise MinimumSpatialValidationError("R2 check authority escalation")
        if row.status not in allowed_status or row.check_type not in allowed_type:
            raise MinimumSpatialValidationError("unknown R2 check status/type")
        _finite_vec3(row.metric_m, f"{row.check_id}.metric_m")

    pair_checks = [row for row in package.checks if row.check_type == PAIRWISE_OVERLAP]
    expected_pair_count = len(source.packaging.regions) * (len(source.packaging.regions) - 1) // 2
    if len(pair_checks) != expected_pair_count:
        raise MinimumSpatialValidationError("R2 pairwise coverage incomplete")

    required_open_types = {DECLARED_CLEARANCE, DEPLOYMENT_INTERFERENCE, THRUST_PLUME, DOCKING_ACCESS}
    open_by_type = {row.check_type for row in package.checks if row.status == CHECK_OPEN}
    if not required_open_types.issubset(open_by_type):
        raise MinimumSpatialValidationError("R2 may not silently close missing spatial-rule domains")

    blockers = any(row.status in {CHECK_OPEN, CHECK_REVIEW} for row in package.checks)
    expected_ready = not blockers
    if package.visual_realization_ready != expected_ready:
        raise MinimumSpatialValidationError("R2 readiness flag inconsistent with check evidence")
    expected_status = READINESS_READY if expected_ready else READINESS_BLOCKED
    if package.readiness_status != expected_status:
        raise MinimumSpatialValidationError("R2 readiness status inconsistent with check evidence")
    if package.package_hash != _hash_without_hash(package):
        raise MinimumSpatialValidationError("R2 package hash mismatch")


def build_minimum_spatial_validation(
    source: GovernedSynthesisPackage,
    semantic: SemanticGeometryPackage,
) -> MinimumSpatialValidationPackage:
    validate_package(source)
    validate_semantic_geometry(semantic, source)
    semantic_ids = _region_semantic_ids(source, semantic)

    regions = tuple(sorted(source.packaging.regions, key=lambda row: row.region_id))
    pair_checks = tuple(_pair_check(a, b, semantic_ids) for a, b in itertools.combinations(regions, 2))

    open_checks = (
        _open_rule_check(
            DECLARED_CLEARANCE,
            "No admitted inter-system clearance requirements are present in the current governed source. R2 therefore does not invent a minimum clearance distance.",
        ),
        _open_rule_check(
            DEPLOYMENT_INTERFERENCE,
            "No admitted deployment swept volumes or deployment-state geometry are present in the current governed source.",
        ),
        _open_rule_check(
            THRUST_PLUME,
            "No admitted torch/plume exclusion geometry or plume-rule contract is present in the current governed source.",
        ),
        _open_rule_check(
            DOCKING_ACCESS,
            "No admitted docking approach/access corridor envelope is present in the current governed source.",
        ),
    )
    open_preservation = SpatialValidationCheck(
        check_id="R2::SOURCE_OPEN_ITEM_PRESERVATION",
        check_type=OPEN_HANDLING,
        status=CHECK_PASS,
        subject_ids=(),
        metric_m=(0.0, 0.0, 0.0),
        evidence_basis="SEMANTIC_OPEN_ITEMS_CARRIED_FORWARD_EXACTLY",
        detail="R2 preserves all source semantic OPEN items and does not convert them into geometry, clearance, or engineering PASS claims.",
    )
    checks = pair_checks + open_checks + (open_preservation,)
    blockers = any(row.status in {CHECK_OPEN, CHECK_REVIEW} for row in checks)

    provisional = MinimumSpatialValidationPackage(
        version=SPATIAL_VALIDATION_VERSION,
        source_design_candidate_id=source.design_state.candidate_id,
        source_governed_package_hash=source.package_hash,
        source_semantic_package_hash=semantic.package_hash,
        checks=checks,
        preserved_open_items=semantic.open_semantic_items,
        readiness_status=READINESS_BLOCKED if blockers else READINESS_READY,
        visual_realization_ready=not blockers,
        package_hash="",
    )
    final = MinimumSpatialValidationPackage(
        version=provisional.version,
        source_design_candidate_id=provisional.source_design_candidate_id,
        source_governed_package_hash=provisional.source_governed_package_hash,
        source_semantic_package_hash=provisional.source_semantic_package_hash,
        checks=provisional.checks,
        preserved_open_items=provisional.preserved_open_items,
        readiness_status=provisional.readiness_status,
        visual_realization_ready=provisional.visual_realization_ready,
        package_hash=_hash_without_hash(provisional),
    )
    validate_minimum_spatial_validation(final, source, semantic)
    return final


def canonical_json(
    package: MinimumSpatialValidationPackage,
    source: GovernedSynthesisPackage,
    semantic: SemanticGeometryPackage,
) -> str:
    validate_minimum_spatial_validation(package, source, semantic)
    return json.dumps(asdict(package), sort_keys=True, separators=(",", ":"), allow_nan=False)
