from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Dict, Iterable, Tuple

from governed_ship_synthesis import GovernedSynthesisPackage, SpatialRegion, validate_package
from minimum_spatial_validation import (
    CHECK_REVIEW as R2_CHECK_REVIEW,
    PAIRWISE_OVERLAP,
    MinimumSpatialValidationPackage,
    build_minimum_spatial_validation,
    validate_minimum_spatial_validation,
)
from semantic_geometry import (
    SEMANTIC_CLASS_ADMITTED_ENVELOPE,
    SemanticGeometryPackage,
    validate_semantic_geometry,
)
from spatial_rule_contract import (
    DOMAIN_ADMITTED_COMPLETE,
    DOMAIN_CLEARANCE,
    DOMAIN_DOCKING,
    DOMAIN_LOOM,
    DOMAIN_OPEN,
    DOMAIN_PLUME,
    DOMAIN_ROBOT,
    DOMAIN_SERVICE,
    DOMAIN_DEPLOYMENT,
    REQUIRED_DOMAINS,
    AxisAlignedExclusionRule,
    PairClearanceRule,
    SpatialRuleContractPackage,
    build_wayfarer_spatial_rule_contract,
    validate_spatial_rule_contract,
)

R2A_VERSION = "LOOM_SPATIAL_VALIDATION_WITH_RULES_R2A_v0.1"
R2A_AUTHORITY = "DERIVED_SPATIAL_RULE_EVALUATION_ONLY"

CHECK_PASS = "PASS_WITHIN_R2A_SCOPE"
CHECK_OPEN = "OPEN_SPATIAL_RULE_DOMAIN"
CHECK_REVIEW = "REVIEW_REQUIRED_SPATIAL_RULE_VIOLATION"

READINESS_READY = "READY_FOR_NON_AUTHORITATIVE_VISUAL_REALIZATION"
READINESS_BLOCKED = "BLOCKED_FOR_VISUAL_REALIZATION_BY_OPEN_OR_REVIEW"


class SpatialValidationWithRulesError(ValueError):
    """Fail-closed error for R2A spatial-rule evaluation."""


def _sha(payload: object) -> str:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _vec3(values: Iterable[float], label: str) -> Tuple[float, float, float]:
    out = tuple(float(v) for v in values)
    if len(out) != 3 or any(not math.isfinite(v) for v in out):
        raise SpatialValidationWithRulesError(f"{label} must contain three finite values")
    return out  # type: ignore[return-value]


@dataclass(frozen=True)
class SpatialRuleEvaluation:
    evaluation_id: str
    domain: str
    status: str
    rule_id: str
    subject_ids: Tuple[str, ...]
    metric_m: float
    threshold_m: float
    evidence_basis: str
    detail: str
    authority_status: str = R2A_AUTHORITY


@dataclass(frozen=True)
class SpatialValidationWithRulesPackage:
    version: str
    source_design_candidate_id: str
    source_governed_package_hash: str
    source_semantic_package_hash: str
    source_r2_package_hash: str
    source_rule_contract_hash: str
    evaluations: Tuple[SpatialRuleEvaluation, ...]
    preserved_open_items: Tuple[str, ...]
    readiness_status: str
    visual_realization_ready: bool
    package_hash: str
    authority_status: str = R2A_AUTHORITY
    flight_dynamics_authority: bool = False
    structural_qualification: bool = False
    canon_changed: bool = False
    production_shipclasses_changed: bool = False
    design_state_mutated: bool = False


def _axis_interval(center: float, size: float) -> Tuple[float, float]:
    half = size / 2.0
    return center - half, center + half


def _axis_separation(a_center: float, a_size: float, b_center: float, b_size: float) -> float:
    alo, ahi = _axis_interval(a_center, a_size)
    blo, bhi = _axis_interval(b_center, b_size)
    if ahi < blo:
        return blo - ahi
    if bhi < alo:
        return alo - bhi
    return -min(ahi, bhi) + max(alo, blo)


def _aabb_separations(a: SpatialRegion, b_center: Tuple[float, float, float], b_dims: Tuple[float, float, float]) -> Tuple[float, float, float]:
    ac = _vec3(a.center_m, f"{a.region_id}.center_m")
    ad = _vec3(a.dimensions_m, f"{a.region_id}.dimensions_m")
    return tuple(_axis_separation(ac[i], ad[i], b_center[i], b_dims[i]) for i in range(3))  # type: ignore[return-value]


def _euclidean_aabb_gap(a: SpatialRegion, b: SpatialRegion) -> float:
    bc = _vec3(b.center_m, f"{b.region_id}.center_m")
    bd = _vec3(b.dimensions_m, f"{b.region_id}.dimensions_m")
    sep = _aabb_separations(a, bc, bd)
    return math.sqrt(sum(max(v, 0.0) ** 2 for v in sep))


def _semantic_region_map(source: GovernedSynthesisPackage, semantic: SemanticGeometryPackage) -> Dict[str, SpatialRegion]:
    region_by_id = {row.region_id: row for row in source.packaging.regions}
    result: Dict[str, SpatialRegion] = {}
    for obj in semantic.objects:
        if obj.semantic_class != SEMANTIC_CLASS_ADMITTED_ENVELOPE:
            continue
        region = region_by_id.get(obj.source_object_id)
        if region is None:
            raise SpatialValidationWithRulesError("semantic admitted envelope has no source packaging region")
        result[obj.semantic_object_id] = region
    if len(result) != len(source.packaging.regions):
        raise SpatialValidationWithRulesError("incomplete admitted-envelope semantic mapping")
    return result


def _open_domain_evaluation(domain: str) -> SpatialRuleEvaluation:
    return SpatialRuleEvaluation(
        evaluation_id=f"R2A::OPEN::{domain}",
        domain=domain,
        status=CHECK_OPEN,
        rule_id="",
        subject_ids=(),
        metric_m=0.0,
        threshold_m=0.0,
        evidence_basis="SPATIAL_RULE_DOMAIN_OPEN_NOT_ADMITTED",
        detail="No admitted complete governed rule set exists for this spatial domain. R2A does not invent geometry or thresholds.",
    )


def _evaluate_clearance(rule: PairClearanceRule, mapping: Dict[str, SpatialRegion]) -> SpatialRuleEvaluation:
    a = mapping[rule.semantic_object_a]
    b = mapping[rule.semantic_object_b]
    gap = _euclidean_aabb_gap(a, b)
    status = CHECK_PASS if gap >= rule.minimum_clearance_m else CHECK_REVIEW
    return SpatialRuleEvaluation(
        evaluation_id=f"R2A::RULE::{rule.rule_id}",
        domain=DOMAIN_CLEARANCE,
        status=status,
        rule_id=rule.rule_id,
        subject_ids=tuple(sorted((rule.semantic_object_a, rule.semantic_object_b))),
        metric_m=gap,
        threshold_m=float(rule.minimum_clearance_m),
        evidence_basis="ADMITTED_PACKAGING_AABB_PLUS_GOVERNED_MINIMUM_CLEARANCE_RULE",
        detail=(
            "AABB separation satisfies the admitted minimum clearance rule."
            if status == CHECK_PASS
            else "AABB separation does not satisfy the admitted minimum clearance rule; engineering review or architecture change is required."
        ),
    )


def _evaluate_exclusion(rule: AxisAlignedExclusionRule, mapping: Dict[str, SpatialRegion]) -> Tuple[SpatialRuleEvaluation, ...]:
    center = _vec3(rule.center_m, f"{rule.rule_id}.center_m")
    dims = _vec3(rule.dimensions_m, f"{rule.rule_id}.dimensions_m")
    rows = []
    for subject_id in sorted(rule.prohibited_semantic_object_ids):
        region = mapping[subject_id]
        sep = _aabb_separations(region, center, dims)
        gap = math.sqrt(sum(max(v, 0.0) ** 2 for v in sep))
        intrusion = all(v <= 0.0 for v in sep)
        rows.append(
            SpatialRuleEvaluation(
                evaluation_id=f"R2A::RULE::{rule.rule_id}::{subject_id}",
                domain=rule.domain,
                status=CHECK_REVIEW if intrusion else CHECK_PASS,
                rule_id=rule.rule_id,
                subject_ids=(subject_id,),
                metric_m=gap,
                threshold_m=0.0,
                evidence_basis="ADMITTED_PACKAGING_AABB_PLUS_GOVERNED_EXCLUSION_ENVELOPE",
                detail=(
                    "Prohibited admitted envelope overlaps or contacts the governed exclusion envelope."
                    if intrusion
                    else "Prohibited admitted envelope remains outside the governed exclusion envelope."
                ),
            )
        )
    return tuple(rows)


def _hash_without_hash(package: SpatialValidationWithRulesPackage) -> str:
    payload = asdict(package)
    payload["package_hash"] = ""
    return _sha(payload)


def validate_spatial_validation_with_rules(
    package: SpatialValidationWithRulesPackage,
    source: GovernedSynthesisPackage,
    semantic: SemanticGeometryPackage,
    r2: MinimumSpatialValidationPackage,
    rules: SpatialRuleContractPackage,
) -> None:
    validate_package(source)
    validate_semantic_geometry(semantic, source)
    validate_minimum_spatial_validation(r2, source, semantic)
    validate_spatial_rule_contract(rules, source, semantic)

    if package.version != R2A_VERSION or package.authority_status != R2A_AUTHORITY:
        raise SpatialValidationWithRulesError("R2A version/authority mismatch")
    if (
        package.flight_dynamics_authority
        or package.structural_qualification
        or package.canon_changed
        or package.production_shipclasses_changed
        or package.design_state_mutated
    ):
        raise SpatialValidationWithRulesError("R2A may not mutate or escalate authority")
    if package.source_design_candidate_id != source.design_state.candidate_id:
        raise SpatialValidationWithRulesError("candidate id mismatch")
    if package.source_governed_package_hash != source.package_hash:
        raise SpatialValidationWithRulesError("governed package hash mismatch")
    if package.source_semantic_package_hash != semantic.package_hash:
        raise SpatialValidationWithRulesError("semantic package hash mismatch")
    if package.source_r2_package_hash != r2.package_hash:
        raise SpatialValidationWithRulesError("R2 package hash mismatch")
    if package.source_rule_contract_hash != rules.package_hash:
        raise SpatialValidationWithRulesError("spatial-rule contract hash mismatch")
    if package.preserved_open_items != semantic.open_semantic_items:
        raise SpatialValidationWithRulesError("R2A must preserve semantic OPEN items exactly")

    eval_ids = [row.evaluation_id for row in package.evaluations]
    if len(eval_ids) != len(set(eval_ids)):
        raise SpatialValidationWithRulesError("duplicate R2A evaluation id")
    allowed_status = {CHECK_PASS, CHECK_OPEN, CHECK_REVIEW}
    for row in package.evaluations:
        if row.authority_status != R2A_AUTHORITY or row.status not in allowed_status:
            raise SpatialValidationWithRulesError("invalid R2A evaluation authority/status")
        if row.domain not in REQUIRED_DOMAINS:
            raise SpatialValidationWithRulesError("invalid R2A domain")
        if not math.isfinite(row.metric_m) or not math.isfinite(row.threshold_m):
            raise SpatialValidationWithRulesError("R2A metric/threshold must be finite")

    status_by_domain = {row.domain: row.status for row in rules.domains}
    for domain in REQUIRED_DOMAINS:
        rows = [row for row in package.evaluations if row.domain == domain]
        if status_by_domain[domain] == DOMAIN_OPEN:
            if len(rows) != 1 or rows[0].status != CHECK_OPEN:
                raise SpatialValidationWithRulesError("OPEN rule domain must remain exactly one explicit OPEN evaluation")
        elif status_by_domain[domain] == DOMAIN_ADMITTED_COMPLETE:
            if not rows or any(row.status == CHECK_OPEN for row in rows):
                raise SpatialValidationWithRulesError("ADMITTED_COMPLETE domain must be evaluated, not left OPEN")

    base_pair_review = any(
        row.check_type == PAIRWISE_OVERLAP and row.status == R2_CHECK_REVIEW
        for row in r2.checks
    )
    rule_blocker = any(row.status in {CHECK_OPEN, CHECK_REVIEW} for row in package.evaluations)
    expected_ready = not base_pair_review and not rule_blocker
    if package.visual_realization_ready != expected_ready:
        raise SpatialValidationWithRulesError("R2A readiness flag inconsistent with evidence")
    expected_status = READINESS_READY if expected_ready else READINESS_BLOCKED
    if package.readiness_status != expected_status:
        raise SpatialValidationWithRulesError("R2A readiness status inconsistent with evidence")
    if package.package_hash != _hash_without_hash(package):
        raise SpatialValidationWithRulesError("R2A package hash mismatch")


def build_spatial_validation_with_rules(
    source: GovernedSynthesisPackage,
    semantic: SemanticGeometryPackage,
    *,
    r2: MinimumSpatialValidationPackage | None = None,
    rules: SpatialRuleContractPackage | None = None,
) -> SpatialValidationWithRulesPackage:
    validate_package(source)
    validate_semantic_geometry(semantic, source)
    if r2 is None:
        r2 = build_minimum_spatial_validation(source, semantic)
    validate_minimum_spatial_validation(r2, source, semantic)
    if rules is None:
        rules = build_wayfarer_spatial_rule_contract(source, semantic)
    validate_spatial_rule_contract(rules, source, semantic)

    mapping = _semantic_region_map(source, semantic)
    domain_status = {row.domain: row.status for row in rules.domains}
    evaluations = []
    for domain in REQUIRED_DOMAINS:
        if domain_status[domain] == DOMAIN_OPEN:
            evaluations.append(_open_domain_evaluation(domain))
            continue
        if domain == DOMAIN_CLEARANCE:
            for rule in sorted(rules.pair_clearance_rules, key=lambda row: row.rule_id):
                evaluations.append(_evaluate_clearance(rule, mapping))
        else:
            domain_rules = sorted((row for row in rules.exclusion_rules if row.domain == domain), key=lambda row: row.rule_id)
            for rule in domain_rules:
                evaluations.extend(_evaluate_exclusion(rule, mapping))

    base_pair_review = any(
        row.check_type == PAIRWISE_OVERLAP and row.status == R2_CHECK_REVIEW
        for row in r2.checks
    )
    rule_blocker = any(row.status in {CHECK_OPEN, CHECK_REVIEW} for row in evaluations)
    ready = not base_pair_review and not rule_blocker

    provisional = SpatialValidationWithRulesPackage(
        version=R2A_VERSION,
        source_design_candidate_id=source.design_state.candidate_id,
        source_governed_package_hash=source.package_hash,
        source_semantic_package_hash=semantic.package_hash,
        source_r2_package_hash=r2.package_hash,
        source_rule_contract_hash=rules.package_hash,
        evaluations=tuple(evaluations),
        preserved_open_items=semantic.open_semantic_items,
        readiness_status=READINESS_READY if ready else READINESS_BLOCKED,
        visual_realization_ready=ready,
        package_hash="",
    )
    final = SpatialValidationWithRulesPackage(
        version=provisional.version,
        source_design_candidate_id=provisional.source_design_candidate_id,
        source_governed_package_hash=provisional.source_governed_package_hash,
        source_semantic_package_hash=provisional.source_semantic_package_hash,
        source_r2_package_hash=provisional.source_r2_package_hash,
        source_rule_contract_hash=provisional.source_rule_contract_hash,
        evaluations=provisional.evaluations,
        preserved_open_items=provisional.preserved_open_items,
        readiness_status=provisional.readiness_status,
        visual_realization_ready=provisional.visual_realization_ready,
        package_hash=_hash_without_hash(provisional),
    )
    validate_spatial_validation_with_rules(final, source, semantic, r2, rules)
    return final


def canonical_json(
    package: SpatialValidationWithRulesPackage,
    source: GovernedSynthesisPackage,
    semantic: SemanticGeometryPackage,
    r2: MinimumSpatialValidationPackage,
    rules: SpatialRuleContractPackage,
) -> str:
    validate_spatial_validation_with_rules(package, source, semantic, r2, rules)
    return json.dumps(asdict(package), sort_keys=True, separators=(",", ":"), allow_nan=False)
