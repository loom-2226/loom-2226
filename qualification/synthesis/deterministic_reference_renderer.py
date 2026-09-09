from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from html import escape
from typing import Dict, Iterable, Tuple

from governed_ship_synthesis import GovernedSynthesisPackage, MeshPrimitive, validate_package
from minimum_spatial_validation import MinimumSpatialValidationPackage, validate_minimum_spatial_validation
from semantic_geometry import SemanticGeometryPackage, validate_semantic_geometry
from spatial_rule_contract import SpatialRuleContractPackage, validate_spatial_rule_contract
from spatial_validation_with_rules import SpatialValidationWithRulesPackage, validate_spatial_validation_with_rules

REFERENCE_RENDER_VERSION = "LOOM_DETERMINISTIC_REFERENCE_RENDERER_R3_v0.1"
REFERENCE_RENDER_AUTHORITY = "REFERENCE_RENDER_EVIDENCE_ONLY"
REFERENCE_RENDER_FORMAT = "image/svg+xml"
REFERENCE_RENDER_STATUS = (
    "ENGINEERING_RESEARCH",
    "NON_CANON",
    "NON_PRODUCTION",
    "NO_FLIGHT_DYNAMICS_AUTHORITY",
    "NO_STRUCTURAL_QUALIFICATION",
    "NON_AUTHORITATIVE_VISUAL_EVIDENCE",
)

PROJECTION_ORTHOGRAPHIC = "ORTHOGRAPHIC"
HANDOFF_READY = "VISUAL_REALIZATION_HANDOFF_READY"
HANDOFF_BLOCKED = "VISUAL_REALIZATION_HANDOFF_BLOCKED_BY_R2A"


class DeterministicReferenceRenderError(ValueError):
    """Fail-closed error for deterministic R3 reference rendering."""


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha_obj(value: object) -> str:
    return _sha_text(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False))


def _vec3(values: Iterable[float], label: str) -> Tuple[float, float, float]:
    out = tuple(float(v) for v in values)
    if len(out) != 3 or any(not math.isfinite(v) for v in out):
        raise DeterministicReferenceRenderError(f"{label} must contain exactly three finite values")
    return out  # type: ignore[return-value]


def _dot(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    return sum(a[i] * b[i] for i in range(3))


def _cross(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> Tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _sub(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> Tuple[float, float, float]:
    return tuple(a[i] - b[i] for i in range(3))  # type: ignore[return-value]


def _norm(v: Tuple[float, float, float], label: str) -> Tuple[float, float, float]:
    m = math.sqrt(_dot(v, v))
    if m <= 1e-12:
        raise DeterministicReferenceRenderError(f"{label} may not be zero length")
    return tuple(x / m for x in v)  # type: ignore[return-value]


@dataclass(frozen=True)
class ReferenceCameraSpec:
    view_id: str
    view_direction: Tuple[float, float, float]
    up_hint: Tuple[float, float, float]
    projection: str = PROJECTION_ORTHOGRAPHIC


@dataclass(frozen=True)
class ReferenceRenderArtifact:
    artifact_id: str
    view_id: str
    media_type: str
    width_px: int
    height_px: int
    content_sha256: str
    content: str
    authority_status: str = REFERENCE_RENDER_AUTHORITY


@dataclass(frozen=True)
class ReferenceRenderPackage:
    version: str
    source_design_candidate_id: str
    source_governed_package_hash: str
    source_semantic_package_hash: str
    source_r2_package_hash: str
    source_rule_contract_hash: str
    source_r2a_package_hash: str
    source_geometry_hash: str
    cameras: Tuple[ReferenceCameraSpec, ...]
    artifacts: Tuple[ReferenceRenderArtifact, ...]
    visual_realization_handoff_status: str
    visual_realization_ready: bool
    package_hash: str
    authority_status: str = REFERENCE_RENDER_AUTHORITY
    flight_dynamics_authority: bool = False
    structural_qualification: bool = False
    canon_changed: bool = False
    production_shipclasses_changed: bool = False
    design_state_mutated: bool = False


def standard_reference_cameras() -> Tuple[ReferenceCameraSpec, ...]:
    # Direction points from the spacecraft toward the camera. Axes are deterministic
    # and intentionally independent of device/browser state.
    return (
        ReferenceCameraSpec("FORE_PORT_3Q", (-1.0, -1.0, 0.65), (0.0, 0.0, 1.0)),
        ReferenceCameraSpec("FORE_STARBOARD_3Q", (-1.0, 1.0, 0.65), (0.0, 0.0, 1.0)),
        ReferenceCameraSpec("AFT_PORT_3Q", (1.0, -1.0, 0.65), (0.0, 0.0, 1.0)),
        ReferenceCameraSpec("AFT_STARBOARD_3Q", (1.0, 1.0, 0.65), (0.0, 0.0, 1.0)),
        ReferenceCameraSpec("PORT", (0.0, -1.0, 0.0), (0.0, 0.0, 1.0)),
        ReferenceCameraSpec("STARBOARD", (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        ReferenceCameraSpec("TOP", (0.0, 0.0, 1.0), (1.0, 0.0, 0.0)),
        ReferenceCameraSpec("FORE", (-1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
        ReferenceCameraSpec("AFT", (1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
    )


def _camera_basis(camera: ReferenceCameraSpec) -> Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]:
    if camera.projection != PROJECTION_ORTHOGRAPHIC:
        raise DeterministicReferenceRenderError("R3 v0.1 supports orthographic reference cameras only")
    toward_camera = _norm(_vec3(camera.view_direction, f"{camera.view_id}.view_direction"), "view_direction")
    up_hint = _norm(_vec3(camera.up_hint, f"{camera.view_id}.up_hint"), "up_hint")
    right = _cross(up_hint, toward_camera)
    right = _norm(right, "camera right")
    up = _norm(_cross(toward_camera, right), "camera up")
    return right, up, toward_camera


def _project_point(point: Tuple[float, float, float], basis: tuple) -> Tuple[float, float, float]:
    right, up, toward_camera = basis
    return _dot(point, right), _dot(point, up), _dot(point, toward_camera)


def _all_projected_bounds(source: GovernedSynthesisPackage, basis: tuple) -> Tuple[float, float, float, float]:
    points = [_project_point(tuple(v), basis) for p in source.geometry.primitives for v in p.vertices_m]
    if not points:
        raise DeterministicReferenceRenderError("source geometry contains no vertices")
    us = [p[0] for p in points]
    vs = [p[1] for p in points]
    u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
    du, dv = max(1e-6, u1 - u0), max(1e-6, v1 - v0)
    pad = 0.08
    return u0 - du * pad, u1 + du * pad, v0 - dv * pad, v1 + dv * pad


def _screen(u: float, v: float, bounds: tuple, width: int, height: int, margin: int) -> Tuple[float, float]:
    u0, u1, v0, v1 = bounds
    usable_w, usable_h = width - 2 * margin, height - 2 * margin
    scale = min(usable_w / (u1 - u0), usable_h / (v1 - v0))
    uc, vc = (u0 + u1) / 2.0, (v0 + v1) / 2.0
    return width / 2.0 + (u - uc) * scale, height / 2.0 - (v - vc) * scale


def _triangle_rows(source: GovernedSynthesisPackage, semantic: SemanticGeometryPackage, basis: tuple) -> list:
    semantic_by_primitive = {row.primitive_id: row for row in semantic.objects}
    rows = []
    for primitive in source.geometry.primitives:
        sem = semantic_by_primitive[primitive.primitive_id]
        projected = [_project_point(tuple(v), basis) for v in primitive.vertices_m]
        for tri_index, tri in enumerate(primitive.triangles):
            p3 = [tuple(primitive.vertices_m[i]) for i in tri]
            p2 = [projected[i] for i in tri]
            a, b, c = p3
            normal = _cross(_sub(b, a), _sub(c, a))
            nm = math.sqrt(_dot(normal, normal))
            facing = 0.0 if nm <= 1e-12 else abs(_dot(tuple(x / nm for x in normal), basis[2]))
            gray = int(round(228 - 88 * facing))
            depth = sum(p[2] for p in p2) / 3.0
            rows.append((depth, primitive.primitive_id, tri_index, gray, p2, sem))
    # Painter order: farthest first. Deterministic IDs break exact-depth ties.
    return sorted(rows, key=lambda row: (row[0], row[1], row[2]))


def _render_svg(
    source: GovernedSynthesisPackage,
    semantic: SemanticGeometryPackage,
    r2a: SpatialValidationWithRulesPackage,
    camera: ReferenceCameraSpec,
    *,
    width: int = 1400,
    height: int = 800,
) -> str:
    if width < 320 or height < 240:
        raise DeterministicReferenceRenderError("reference render dimensions are too small")
    basis = _camera_basis(camera)
    bounds = _all_projected_bounds(source, basis)
    margin = 52
    rows = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f4f4f2"/>',
        f'<text x="28" y="30" font-family="monospace" font-size="18">WAYFARER — {escape(camera.view_id)}</text>',
        f'<text x="28" y="50" font-family="monospace" font-size="11">authority={REFERENCE_RENDER_AUTHORITY}  candidate={escape(source.design_state.candidate_id)}</text>',
        f'<text x="28" y="68" font-family="monospace" font-size="11">r2a={escape(r2a.readiness_status)}  AI-HANDOFF={"READY" if r2a.visual_realization_ready else "BLOCKED"}</text>',
        '<g stroke="#252525" stroke-width="0.65" stroke-linejoin="round">',
    ]
    for _, primitive_id, tri_index, gray, p2, sem in _triangle_rows(source, semantic, basis):
        pts = [_screen(p[0], p[1], bounds, width, height, margin) for p in p2]
        points = " ".join(f"{x:.3f},{y:.3f}" for x, y in pts)
        rows.append(
            f'<polygon points="{points}" fill="rgb({gray},{gray},{gray})" '
            f'data-primitive-id="{escape(primitive_id)}" data-triangle-index="{tri_index}" '
            f'data-semantic-id="{escape(sem.semantic_object_id)}" data-semantic-class="{escape(sem.semantic_class)}"/>'
        )
    rows.extend((
        '</g>',
        f'<text x="28" y="{height-34}" font-family="monospace" font-size="10">governed={escape(source.package_hash[:16])} semantic={escape(semantic.package_hash[:16])} r2a={escape(r2a.package_hash[:16])}</text>',
        f'<text x="28" y="{height-18}" font-family="monospace" font-size="10">DETERMINISTIC REFERENCE EVIDENCE — NON-CANON — NON-PRODUCTION — NOT STRUCTURAL QUALIFICATION</text>',
        '</svg>',
    ))
    return "\n".join(rows) + "\n"


def _hash_without_hash(package: ReferenceRenderPackage) -> str:
    payload = asdict(package)
    payload["package_hash"] = ""
    for artifact in payload["artifacts"]:
        artifact["content"] = ""
    return _sha_obj(payload)


def validate_reference_render_package(
    package: ReferenceRenderPackage,
    source: GovernedSynthesisPackage,
    semantic: SemanticGeometryPackage,
    r2: MinimumSpatialValidationPackage,
    rules: SpatialRuleContractPackage,
    r2a: SpatialValidationWithRulesPackage,
) -> None:
    validate_package(source)
    validate_semantic_geometry(semantic, source)
    validate_minimum_spatial_validation(r2, source, semantic)
    validate_spatial_rule_contract(rules, source, semantic)
    validate_spatial_validation_with_rules(r2a, source, semantic, r2, rules)
    if package.version != REFERENCE_RENDER_VERSION or package.authority_status != REFERENCE_RENDER_AUTHORITY:
        raise DeterministicReferenceRenderError("R3 version/authority mismatch")
    if package.flight_dynamics_authority or package.structural_qualification or package.canon_changed or package.production_shipclasses_changed or package.design_state_mutated:
        raise DeterministicReferenceRenderError("R3 may not mutate or escalate authority")
    expected_bindings = (
        (package.source_design_candidate_id, source.design_state.candidate_id),
        (package.source_governed_package_hash, source.package_hash),
        (package.source_semantic_package_hash, semantic.package_hash),
        (package.source_r2_package_hash, r2.package_hash),
        (package.source_rule_contract_hash, rules.package_hash),
        (package.source_r2a_package_hash, r2a.package_hash),
        (package.source_geometry_hash, semantic.source_geometry_hash),
    )
    if any(a != b for a, b in expected_bindings):
        raise DeterministicReferenceRenderError("R3 source binding mismatch")
    expected_cameras = standard_reference_cameras()
    if package.cameras != expected_cameras:
        raise DeterministicReferenceRenderError("R3 camera set/order is not canonical")
    if len(package.artifacts) != len(expected_cameras):
        raise DeterministicReferenceRenderError("R3 artifact coverage incomplete")
    if tuple(row.view_id for row in package.artifacts) != tuple(row.view_id for row in expected_cameras):
        raise DeterministicReferenceRenderError("R3 artifact order must match canonical camera order")
    ids = [row.artifact_id for row in package.artifacts]
    if len(ids) != len(set(ids)):
        raise DeterministicReferenceRenderError("duplicate R3 artifact id")
    for artifact in package.artifacts:
        if artifact.authority_status != REFERENCE_RENDER_AUTHORITY or artifact.media_type != REFERENCE_RENDER_FORMAT:
            raise DeterministicReferenceRenderError("R3 artifact authority/media mismatch")
        if artifact.content_sha256 != _sha_text(artifact.content):
            raise DeterministicReferenceRenderError("R3 artifact content hash mismatch")
        if 'REFERENCE_RENDER_EVIDENCE_ONLY' not in artifact.content:
            raise DeterministicReferenceRenderError("R3 artifact must display reference-evidence authority")
    expected_ready = bool(r2a.visual_realization_ready)
    if package.visual_realization_ready != expected_ready:
        raise DeterministicReferenceRenderError("R3 may not alter R2A visual-realization readiness")
    expected_handoff = HANDOFF_READY if expected_ready else HANDOFF_BLOCKED
    if package.visual_realization_handoff_status != expected_handoff:
        raise DeterministicReferenceRenderError("R3 handoff status inconsistent with R2A")
    # Critical R3 rule: blocked handoff does NOT prohibit reference evidence generation.
    if not package.artifacts:
        raise DeterministicReferenceRenderError("R3 must emit reference evidence regardless of handoff readiness")
    if package.package_hash != _hash_without_hash(package):
        raise DeterministicReferenceRenderError("R3 package hash mismatch")


def build_reference_render_package(
    source: GovernedSynthesisPackage,
    semantic: SemanticGeometryPackage,
    r2: MinimumSpatialValidationPackage,
    rules: SpatialRuleContractPackage,
    r2a: SpatialValidationWithRulesPackage,
) -> ReferenceRenderPackage:
    validate_spatial_validation_with_rules(r2a, source, semantic, r2, rules)
    cameras = standard_reference_cameras()
    artifacts = []
    for camera in cameras:
        content = _render_svg(source, semantic, r2a, camera)
        artifacts.append(ReferenceRenderArtifact(
            artifact_id=f"wayfarer_{camera.view_id.lower()}_reference.svg",
            view_id=camera.view_id,
            media_type=REFERENCE_RENDER_FORMAT,
            width_px=1400,
            height_px=800,
            content_sha256=_sha_text(content),
            content=content,
        ))
    provisional = ReferenceRenderPackage(
        version=REFERENCE_RENDER_VERSION,
        source_design_candidate_id=source.design_state.candidate_id,
        source_governed_package_hash=source.package_hash,
        source_semantic_package_hash=semantic.package_hash,
        source_r2_package_hash=r2.package_hash,
        source_rule_contract_hash=rules.package_hash,
        source_r2a_package_hash=r2a.package_hash,
        source_geometry_hash=semantic.source_geometry_hash,
        cameras=cameras,
        artifacts=tuple(artifacts),
        visual_realization_handoff_status=HANDOFF_READY if r2a.visual_realization_ready else HANDOFF_BLOCKED,
        visual_realization_ready=bool(r2a.visual_realization_ready),
        package_hash="",
    )
    final = ReferenceRenderPackage(
        **{**provisional.__dict__, "package_hash": _hash_without_hash(provisional)}
    )
    validate_reference_render_package(final, source, semantic, r2, rules, r2a)
    return final


def canonical_manifest_json(package: ReferenceRenderPackage) -> str:
    payload = asdict(package)
    for artifact in payload["artifacts"]:
        artifact.pop("content", None)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
