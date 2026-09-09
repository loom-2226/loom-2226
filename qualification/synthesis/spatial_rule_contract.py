from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Iterable, Tuple

from governed_ship_synthesis import GovernedSynthesisPackage, validate_package
from semantic_geometry import (
    SEMANTIC_CLASS_ADMITTED_ENVELOPE,
    SemanticGeometryPackage,
    validate_semantic_geometry,
)

SPATIAL_RULE_CONTRACT_VERSION = "LOOM_SPATIAL_RULE_CONTRACT_R2A_v0.1"
SPATIAL_RULE_CONTRACT_AUTHORITY = "SPATIAL_RULE_CONTRACT_EVIDENCE_ONLY"

DOMAIN_CLEARANCE = "CLEARANCE"
DOMAIN_DEPLOYMENT = "DEPLOYMENT"
DOMAIN_PLUME = "PLUME_EXCLUSION"
DOMAIN_DOCKING = "DOCKING_ACCESS"
DOMAIN_SERVICE = "SERVICE_ACCESS"
DOMAIN_ROBOT = "ROBOT_ACCESS"
DOMAIN_LOOM = "LOOM_DOMAIN"

REQUIRED_DOMAINS = (
    DOMAIN_CLEARANCE,
    DOMAIN_DEPLOYMENT,
    DOMAIN_PLUME,
    DOMAIN_DOCKING,
    DOMAIN_SERVICE,
    DOMAIN_ROBOT,
    DOMAIN_LOOM,
)

DOMAIN_OPEN = "OPEN_NOT_ADMITTED"
DOMAIN_ADMITTED_COMPLETE = "ADMITTED_COMPLETE"

RULE_PAIR_CLEARANCE = "PAIR_MINIMUM_CLEARANCE"
RULE_AABB_EXCLUSION = "AXIS_ALIGNED_EXCLUSION_ENVELOPE"


class SpatialRuleContractError(ValueError):
    """Fail-closed error for the governed spatial-rule contract."""


def _sha(payload: object) -> str:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _nonempty(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SpatialRuleContractError(f"{label} must be a non-empty string")
    return value.strip()


def _finite_positive(value: float, label: str) -> float:
    out = float(value)
    if not math.isfinite(out) or out <= 0.0:
        raise SpatialRuleContractError(f"{label} must be finite and positive")
    return out


def _vec3(values: Iterable[float], label: str) -> Tuple[float, float, float]:
    out = tuple(float(v) for v in values)
    if len(out) != 3 or any(not math.isfinite(v) for v in out):
        raise SpatialRuleContractError(f"{label} must contain three finite values")
    return out  # type: ignore[return-value]


@dataclass(frozen=True)
class SpatialRuleDomainState:
    domain: str
    status: str
    rationale: str
    provenance_refs: Tuple[str, ...]
    authority_status: str = SPATIAL_RULE_CONTRACT_AUTHORITY


@dataclass(frozen=True)
class PairClearanceRule:
    rule_id: str
    semantic_object_a: str
    semantic_object_b: str
    minimum_clearance_m: float
    rationale: str
    provenance_refs: Tuple[str, ...]
    domain: str = DOMAIN_CLEARANCE
    rule_kind: str = RULE_PAIR_CLEARANCE
    authority_status: str = SPATIAL_RULE_CONTRACT_AUTHORITY


@dataclass(frozen=True)
class AxisAlignedExclusionRule:
    rule_id: str
    domain: str
    center_m: Tuple[float, float, float]
    dimensions_m: Tuple[float, float, float]
    prohibited_semantic_object_ids: Tuple[str, ...]
    rationale: str
    provenance_refs: Tuple[str, ...]
    rule_kind: str = RULE_AABB_EXCLUSION
    authority_status: str = SPATIAL_RULE_CONTRACT_AUTHORITY


@dataclass(frozen=True)
class SpatialRuleContractPackage:
    version: str
    source_design_candidate_id: str
    source_governed_package_hash: str
    source_semantic_package_hash: str
    domains: Tuple[SpatialRuleDomainState, ...]
    pair_clearance_rules: Tuple[PairClearanceRule, ...]
    exclusion_rules: Tuple[AxisAlignedExclusionRule, ...]
    package_hash: str
    authority_status: str = SPATIAL_RULE_CONTRACT_AUTHORITY
    flight_dynamics_authority: bool = False
    structural_qualification: bool = False
    canon_changed: bool = False
    production_shipclasses_changed: bool = False
    design_state_mutated: bool = False


def _hash_without_hash(package: SpatialRuleContractPackage) -> str:
    payload = asdict(package)
    payload["package_hash"] = ""
    return _sha(payload)


def validate_spatial_rule_contract(
    package: SpatialRuleContractPackage,
    source: GovernedSynthesisPackage,
    semantic: SemanticGeometryPackage,
) -> None:
    validate_package(source)
    validate_semantic_geometry(semantic, source)

    if package.version != SPATIAL_RULE_CONTRACT_VERSION:
        raise SpatialRuleContractError("spatial-rule contract version mismatch")
    if package.authority_status != SPATIAL_RULE_CONTRACT_AUTHORITY:
        raise SpatialRuleContractError("spatial-rule contract authority escalation")
    if (
        package.flight_dynamics_authority
        or package.structural_qualification
        or package.canon_changed
        or package.production_shipclasses_changed
        or package.design_state_mutated
    ):
        raise SpatialRuleContractError("spatial-rule contract may not mutate or escalate authority")
    if package.source_design_candidate_id != source.design_state.candidate_id:
        raise SpatialRuleContractError("candidate id mismatch")
    if package.source_governed_package_hash != source.package_hash:
        raise SpatialRuleContractError("governed package hash mismatch")
    if package.source_semantic_package_hash != semantic.package_hash:
        raise SpatialRuleContractError("semantic package hash mismatch")

    domains = [row.domain for row in package.domains]
    if tuple(sorted(domains)) != tuple(sorted(REQUIRED_DOMAINS)) or len(domains) != len(set(domains)):
        raise SpatialRuleContractError("required spatial-rule domains must appear exactly once")

    allowed_status = {DOMAIN_OPEN, DOMAIN_ADMITTED_COMPLETE}
    for row in package.domains:
        if row.authority_status != SPATIAL_RULE_CONTRACT_AUTHORITY:
            raise SpatialRuleContractError("domain authority escalation")
        if row.status not in allowed_status:
            raise SpatialRuleContractError("unknown spatial-rule domain status")
        _nonempty(row.rationale, "domain rationale")
        if not row.provenance_refs:
            raise SpatialRuleContractError("domain provenance is required")

    admitted_envelope_ids = {
        row.semantic_object_id
        for row in semantic.objects
        if row.semantic_class == SEMANTIC_CLASS_ADMITTED_ENVELOPE
    }
    rule_ids = []

    for row in package.pair_clearance_rules:
        rule_ids.append(row.rule_id)
        if row.authority_status != SPATIAL_RULE_CONTRACT_AUTHORITY:
            raise SpatialRuleContractError("clearance rule authority escalation")
        if row.rule_kind != RULE_PAIR_CLEARANCE or row.domain != DOMAIN_CLEARANCE:
            raise SpatialRuleContractError("invalid pair-clearance rule type/domain")
        _nonempty(row.rule_id, "clearance rule_id")
        if row.semantic_object_a == row.semantic_object_b:
            raise SpatialRuleContractError("clearance rule may not target same semantic object twice")
        if row.semantic_object_a not in admitted_envelope_ids or row.semantic_object_b not in admitted_envelope_ids:
            raise SpatialRuleContractError("R2A clearance rule requires admitted-envelope semantic objects")
        _finite_positive(row.minimum_clearance_m, "minimum_clearance_m")
        _nonempty(row.rationale, "clearance rationale")
        if not row.provenance_refs:
            raise SpatialRuleContractError("clearance provenance is required")

    exclusion_domains = {DOMAIN_DEPLOYMENT, DOMAIN_PLUME, DOMAIN_DOCKING, DOMAIN_SERVICE, DOMAIN_ROBOT, DOMAIN_LOOM}
    for row in package.exclusion_rules:
        rule_ids.append(row.rule_id)
        if row.authority_status != SPATIAL_RULE_CONTRACT_AUTHORITY:
            raise SpatialRuleContractError("exclusion rule authority escalation")
        if row.rule_kind != RULE_AABB_EXCLUSION or row.domain not in exclusion_domains:
            raise SpatialRuleContractError("invalid exclusion rule kind/domain")
        _nonempty(row.rule_id, "exclusion rule_id")
        _vec3(row.center_m, f"{row.rule_id}.center_m")
        dims = _vec3(row.dimensions_m, f"{row.rule_id}.dimensions_m")
        if any(v <= 0.0 for v in dims):
            raise SpatialRuleContractError("exclusion rule dimensions must be positive")
        if not row.prohibited_semantic_object_ids:
            raise SpatialRuleContractError("exclusion rule must name prohibited semantic objects")
        if any(obj_id not in admitted_envelope_ids for obj_id in row.prohibited_semantic_object_ids):
            raise SpatialRuleContractError("R2A exclusion rule requires admitted-envelope semantic objects")
        if len(row.prohibited_semantic_object_ids) != len(set(row.prohibited_semantic_object_ids)):
            raise SpatialRuleContractError("duplicate prohibited semantic object")
        _nonempty(row.rationale, "exclusion rationale")
        if not row.provenance_refs:
            raise SpatialRuleContractError("exclusion provenance is required")

    if len(rule_ids) != len(set(rule_ids)):
        raise SpatialRuleContractError("duplicate spatial rule_id")

    domain_status = {row.domain: row.status for row in package.domains}
    if domain_status[DOMAIN_CLEARANCE] == DOMAIN_OPEN and package.pair_clearance_rules:
        raise SpatialRuleContractError("OPEN clearance domain may not carry admitted clearance rules")
    if domain_status[DOMAIN_CLEARANCE] == DOMAIN_ADMITTED_COMPLETE and not package.pair_clearance_rules:
        raise SpatialRuleContractError("ADMITTED_COMPLETE clearance domain requires explicit governed rules")
    for domain in exclusion_domains:
        rows = tuple(row for row in package.exclusion_rules if row.domain == domain)
        if domain_status[domain] == DOMAIN_OPEN and rows:
            raise SpatialRuleContractError(f"OPEN {domain} domain may not carry admitted rules")
        if domain_status[domain] == DOMAIN_ADMITTED_COMPLETE and not rows:
            raise SpatialRuleContractError(f"ADMITTED_COMPLETE {domain} domain requires explicit governed rules")

    if package.package_hash != _hash_without_hash(package):
        raise SpatialRuleContractError("spatial-rule contract package hash mismatch")


def build_spatial_rule_contract(
    source: GovernedSynthesisPackage,
    semantic: SemanticGeometryPackage,
    *,
    domains: Tuple[SpatialRuleDomainState, ...],
    pair_clearance_rules: Tuple[PairClearanceRule, ...] = (),
    exclusion_rules: Tuple[AxisAlignedExclusionRule, ...] = (),
) -> SpatialRuleContractPackage:
    provisional = SpatialRuleContractPackage(
        version=SPATIAL_RULE_CONTRACT_VERSION,
        source_design_candidate_id=source.design_state.candidate_id,
        source_governed_package_hash=source.package_hash,
        source_semantic_package_hash=semantic.package_hash,
        domains=domains,
        pair_clearance_rules=pair_clearance_rules,
        exclusion_rules=exclusion_rules,
        package_hash="",
    )
    final = SpatialRuleContractPackage(
        version=provisional.version,
        source_design_candidate_id=provisional.source_design_candidate_id,
        source_governed_package_hash=provisional.source_governed_package_hash,
        source_semantic_package_hash=provisional.source_semantic_package_hash,
        domains=provisional.domains,
        pair_clearance_rules=provisional.pair_clearance_rules,
        exclusion_rules=provisional.exclusion_rules,
        package_hash=_hash_without_hash(provisional),
    )
    validate_spatial_rule_contract(final, source, semantic)
    return final


def build_wayfarer_spatial_rule_contract(
    source: GovernedSynthesisPackage,
    semantic: SemanticGeometryPackage,
) -> SpatialRuleContractPackage:
    validate_package(source)
    validate_semantic_geometry(semantic, source)
    domains = tuple(
        SpatialRuleDomainState(
            domain=domain,
            status=DOMAIN_OPEN,
            rationale=(
                "No admitted governed spatial rule is present for this domain in the current Wayfarer source. "
                "R2A registers the domain explicitly and does not invent geometry or thresholds."
            ),
            provenance_refs=(source.design_state.candidate_id, semantic.package_hash),
        )
        for domain in REQUIRED_DOMAINS
    )
    return build_spatial_rule_contract(source, semantic, domains=domains)


def canonical_json(
    package: SpatialRuleContractPackage,
    source: GovernedSynthesisPackage,
    semantic: SemanticGeometryPackage,
) -> str:
    validate_spatial_rule_contract(package, source, semantic)
    return json.dumps(asdict(package), sort_keys=True, separators=(",", ":"), allow_nan=False)
