from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Dict, Tuple

from governed_ship_synthesis import (
    GEOMETRY_AUTHORITY,
    GovernedSynthesisPackage,
    MeshPrimitive,
    validate_package,
)

SEMANTIC_GEOMETRY_VERSION = "LOOM_SEMANTIC_GEOMETRY_v0.1"
SEMANTIC_GEOMETRY_AUTHORITY = "DERIVED_SEMANTIC_GEOMETRY_ONLY"
SEMANTIC_GEOMETRY_STATUS = (
    "ENGINEERING_RESEARCH",
    "NON_CANON",
    "NON_PRODUCTION",
    "NO_FLIGHT_DYNAMICS_AUTHORITY",
    "NO_STRUCTURAL_QUALIFICATION",
)

# R1 intentionally classifies only what the existing governed synthesis proves.
# It does not infer subsystem identity (tank/reactor/hab/etc.) from names or shape.
SEMANTIC_CLASS_ADMITTED_ENVELOPE = "ADMITTED_SPATIAL_ENVELOPE"
SEMANTIC_CLASS_STRUCTURAL_HYPOTHESIS = "STRUCTURAL_HYPOTHESIS"
SEMANTIC_CLASS_SOURCE_NODE_PROXY = "SOURCE_NODE_PROXY"

ROLE_ENGINEERING_ENVELOPE = "ENGINEERING_ENVELOPE"
ROLE_STRUCTURAL_EXPRESSION = "STRUCTURAL_EXPRESSION_PROXY"
ROLE_SOURCE_LOCATION = "SOURCE_LOCATION_PROXY"

MUTABILITY_CONSTRAINED_ENVELOPE = "PRESERVE_ENGINEERING_ENVELOPE_AND_POSITION"
MUTABILITY_STYLE_ONLY = "STYLE_ELABORATION_ALLOWED_NO_ENGINEERING_AUTHORITY"
MUTABILITY_PROXY_ONLY = "NON_AUTHORITATIVE_PROXY_DO_NOT_INFER_VOLUME"

STATUS_ADMITTED_ENVELOPE = "ADMITTED_GEOMETRY_SOURCE"
STATUS_STRUCTURAL_UNQUALIFIED = "NOT_STRUCTURALLY_QUALIFIED"
STATUS_SOURCE_NODE_ONLY = "SOURCE_NODE_ONLY_VOLUME_MAY_BE_OPEN"


class SemanticGeometryError(ValueError):
    """Fail-closed error for the R1 semantic-geometry research contract."""


def _sha(payload: object) -> str:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _nonempty(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SemanticGeometryError(f"{label} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True)
class SemanticGeometryObject:
    semantic_object_id: str
    primitive_id: str
    primitive_kind: str
    source_object_id: str
    source_component_id: str
    source_kind: str
    semantic_class: str
    system_id: str
    function: str
    geometry_role: str
    visual_mutability: str
    engineering_status: str
    source_geometry_authority: str
    provenance_refs: Tuple[str, ...]
    authority_status: str = SEMANTIC_GEOMETRY_AUTHORITY


@dataclass(frozen=True)
class SemanticGeometryPackage:
    version: str
    source_design_candidate_id: str
    source_design_candidate_hash: str
    source_governed_package_hash: str
    source_geometry_hash: str
    objects: Tuple[SemanticGeometryObject, ...]
    open_semantic_items: Tuple[str, ...]
    package_hash: str
    authority_status: str = SEMANTIC_GEOMETRY_AUTHORITY
    flight_dynamics_authority: bool = False
    canon_changed: bool = False
    production_shipclasses_changed: bool = False


def geometry_hash(package: GovernedSynthesisPackage) -> str:
    validate_package(package)
    return _sha(asdict(package.geometry))


def _primitive_maps(package: GovernedSynthesisPackage) -> Tuple[Dict[str, tuple], Dict[str, tuple], Dict[str, tuple]]:
    region_map: Dict[str, tuple] = {}
    for region in package.packaging.regions:
        primitive_id = f"MESH::{region.region_id}"
        if primitive_id in region_map:
            raise SemanticGeometryError(f"duplicate expected region primitive {primitive_id}")
        # Current packaging provenance is (candidate_id, instance_id, component_type_id).
        component_id = region.source_refs[1] if len(region.source_refs) >= 2 else ""
        region_map[primitive_id] = (region, component_id)

    member_map: Dict[str, tuple] = {}
    for member in package.structure.members:
        primitive_id = f"MESH::{member.member_id}"
        if primitive_id in member_map:
            raise SemanticGeometryError(f"duplicate expected structural primitive {primitive_id}")
        member_map[primitive_id] = (member, "")

    node_map: Dict[str, tuple] = {}
    for node in package.design_state.nodes:
        primitive_id = f"MESH::NODE::{node.node_id}"
        if primitive_id in node_map:
            raise SemanticGeometryError(f"duplicate expected source-node primitive {primitive_id}")
        component_id = node.source_id if node.source_kind == "COMPONENT_INSTANCE" else ""
        node_map[primitive_id] = (node, component_id)

    return region_map, member_map, node_map


def _semantic_for_primitive(
    primitive: MeshPrimitive,
    region_map: Dict[str, tuple],
    member_map: Dict[str, tuple],
    node_map: Dict[str, tuple],
) -> SemanticGeometryObject:
    if primitive.authority_status != GEOMETRY_AUTHORITY:
        raise SemanticGeometryError("source primitive authority escalation")

    if primitive.primitive_id in region_map:
        region, component_id = region_map[primitive.primitive_id]
        if primitive.primitive_kind != "REGION_ENVELOPE":
            raise SemanticGeometryError(f"region primitive kind mismatch: {primitive.primitive_id}")
        if tuple(primitive.source_refs) != tuple(region.source_refs):
            raise SemanticGeometryError(f"region primitive provenance mismatch: {primitive.primitive_id}")
        return SemanticGeometryObject(
            semantic_object_id=f"SEM::{primitive.primitive_id}",
            primitive_id=primitive.primitive_id,
            primitive_kind=primitive.primitive_kind,
            source_object_id=region.region_id,
            source_component_id=component_id,
            source_kind="PACKAGING_REGION",
            semantic_class=SEMANTIC_CLASS_ADMITTED_ENVELOPE,
            system_id="OPEN_NOT_CLASSIFIED_BY_R1",
            function="SPATIAL_ENVELOPE",
            geometry_role=ROLE_ENGINEERING_ENVELOPE,
            visual_mutability=MUTABILITY_CONSTRAINED_ENVELOPE,
            engineering_status=STATUS_ADMITTED_ENVELOPE,
            source_geometry_authority=primitive.authority_status,
            provenance_refs=tuple(primitive.source_refs),
        )

    if primitive.primitive_id in member_map:
        member, component_id = member_map[primitive.primitive_id]
        if primitive.primitive_kind != "STRUCTURAL_MEMBER":
            raise SemanticGeometryError(f"structural primitive kind mismatch: {primitive.primitive_id}")
        if tuple(primitive.source_refs) != tuple(member.source_refs):
            raise SemanticGeometryError(f"structural primitive provenance mismatch: {primitive.primitive_id}")
        return SemanticGeometryObject(
            semantic_object_id=f"SEM::{primitive.primitive_id}",
            primitive_id=primitive.primitive_id,
            primitive_kind=primitive.primitive_kind,
            source_object_id=member.member_id,
            source_component_id=component_id,
            source_kind="STRUCTURAL_MEMBER_HYPOTHESIS",
            semantic_class=SEMANTIC_CLASS_STRUCTURAL_HYPOTHESIS,
            system_id="OPEN_NOT_CLASSIFIED_BY_R1",
            function="COARSE_CONNECTIVITY_EXPRESSION",
            geometry_role=ROLE_STRUCTURAL_EXPRESSION,
            visual_mutability=MUTABILITY_STYLE_ONLY,
            engineering_status=STATUS_STRUCTURAL_UNQUALIFIED,
            source_geometry_authority=primitive.authority_status,
            provenance_refs=tuple(primitive.source_refs),
        )

    if primitive.primitive_id in node_map:
        node, component_id = node_map[primitive.primitive_id]
        if primitive.primitive_kind != "SOURCE_NODE":
            raise SemanticGeometryError(f"source-node primitive kind mismatch: {primitive.primitive_id}")
        if tuple(primitive.source_refs) != tuple(node.provenance_refs):
            raise SemanticGeometryError(f"source-node primitive provenance mismatch: {primitive.primitive_id}")
        return SemanticGeometryObject(
            semantic_object_id=f"SEM::{primitive.primitive_id}",
            primitive_id=primitive.primitive_id,
            primitive_kind=primitive.primitive_kind,
            source_object_id=node.node_id,
            source_component_id=component_id,
            source_kind=node.source_kind,
            semantic_class=SEMANTIC_CLASS_SOURCE_NODE_PROXY,
            system_id="OPEN_NOT_CLASSIFIED_BY_R1",
            function="SOURCE_LOCATION_MARKER",
            geometry_role=ROLE_SOURCE_LOCATION,
            visual_mutability=MUTABILITY_PROXY_ONLY,
            engineering_status=STATUS_SOURCE_NODE_ONLY,
            source_geometry_authority=primitive.authority_status,
            provenance_refs=tuple(primitive.source_refs),
        )

    raise SemanticGeometryError(f"unmapped geometry primitive fails closed: {primitive.primitive_id}")


def _hash_without_hash(package: SemanticGeometryPackage) -> str:
    payload = asdict(package)
    payload["package_hash"] = ""
    return _sha(payload)


def validate_semantic_geometry(
    package: SemanticGeometryPackage,
    source: GovernedSynthesisPackage,
) -> None:
    validate_package(source)
    if package.version != SEMANTIC_GEOMETRY_VERSION:
        raise SemanticGeometryError("semantic geometry version mismatch")
    if package.authority_status != SEMANTIC_GEOMETRY_AUTHORITY:
        raise SemanticGeometryError("semantic geometry authority escalation")
    if package.flight_dynamics_authority or package.canon_changed or package.production_shipclasses_changed:
        raise SemanticGeometryError("semantic geometry may not mutate frozen authority")
    if package.source_design_candidate_id != source.design_state.candidate_id:
        raise SemanticGeometryError("candidate id mismatch")
    if package.source_design_candidate_hash != source.design_state.candidate_source_hash:
        raise SemanticGeometryError("candidate source hash mismatch")
    if package.source_governed_package_hash != source.package_hash:
        raise SemanticGeometryError("governed source package hash mismatch")
    if package.source_geometry_hash != geometry_hash(source):
        raise SemanticGeometryError("source geometry hash mismatch")

    source_ids = tuple(row.primitive_id for row in source.geometry.primitives)
    semantic_ids = tuple(row.primitive_id for row in package.objects)
    if semantic_ids != source_ids:
        raise SemanticGeometryError("semantic objects must map 1:1 in source primitive order")
    if len(semantic_ids) != len(set(semantic_ids)):
        raise SemanticGeometryError("duplicate semantic primitive mapping")

    for row in package.objects:
        _nonempty(row.semantic_object_id, "semantic_object_id")
        _nonempty(row.source_object_id, "source_object_id")
        _nonempty(row.semantic_class, "semantic_class")
        _nonempty(row.system_id, "system_id")
        _nonempty(row.function, "function")
        _nonempty(row.geometry_role, "geometry_role")
        _nonempty(row.visual_mutability, "visual_mutability")
        _nonempty(row.engineering_status, "engineering_status")
        if row.authority_status != SEMANTIC_GEOMETRY_AUTHORITY:
            raise SemanticGeometryError("semantic object authority escalation")
        if row.source_geometry_authority != GEOMETRY_AUTHORITY:
            raise SemanticGeometryError("semantic object source authority mismatch")
        if row.semantic_class == SEMANTIC_CLASS_STRUCTURAL_HYPOTHESIS and row.engineering_status != STATUS_STRUCTURAL_UNQUALIFIED:
            raise SemanticGeometryError("structural hypothesis may not imply structural qualification")
        if row.semantic_class == SEMANTIC_CLASS_SOURCE_NODE_PROXY and row.visual_mutability != MUTABILITY_PROXY_ONLY:
            raise SemanticGeometryError("source-node proxy may not silently acquire volume")

    if package.package_hash != _hash_without_hash(package):
        raise SemanticGeometryError("semantic geometry package hash mismatch")


def build_semantic_geometry(source: GovernedSynthesisPackage) -> SemanticGeometryPackage:
    validate_package(source)
    region_map, member_map, node_map = _primitive_maps(source)
    objects = tuple(
        _semantic_for_primitive(primitive, region_map, member_map, node_map)
        for primitive in source.geometry.primitives
    )

    mapped_ids = {row.primitive_id for row in objects}
    expected_ids = set(region_map) | set(member_map) | set(node_map)
    if mapped_ids != expected_ids:
        missing = sorted(expected_ids - mapped_ids)
        extra = sorted(mapped_ids - expected_ids)
        raise SemanticGeometryError(f"semantic/source mapping mismatch missing={missing} extra={extra}")

    open_items = tuple(sorted(set(source.packaging.open_items))) + (
        "SYSTEM_CLASSIFICATION_OPEN_NOT_DERIVED_BY_R1",
        "AI_VISUAL_REALIZATION_NON_AUTHORITATIVE",
    )
    provisional = SemanticGeometryPackage(
        version=SEMANTIC_GEOMETRY_VERSION,
        source_design_candidate_id=source.design_state.candidate_id,
        source_design_candidate_hash=source.design_state.candidate_source_hash,
        source_governed_package_hash=source.package_hash,
        source_geometry_hash=geometry_hash(source),
        objects=objects,
        open_semantic_items=open_items,
        package_hash="",
    )
    final = SemanticGeometryPackage(
        version=provisional.version,
        source_design_candidate_id=provisional.source_design_candidate_id,
        source_design_candidate_hash=provisional.source_design_candidate_hash,
        source_governed_package_hash=provisional.source_governed_package_hash,
        source_geometry_hash=provisional.source_geometry_hash,
        objects=provisional.objects,
        open_semantic_items=provisional.open_semantic_items,
        package_hash=_hash_without_hash(provisional),
    )
    validate_semantic_geometry(final, source)
    return final


def canonical_json(package: SemanticGeometryPackage, source: GovernedSynthesisPackage) -> str:
    validate_semantic_geometry(package, source)
    return json.dumps(asdict(package), sort_keys=True, separators=(",", ":"), allow_nan=False)
