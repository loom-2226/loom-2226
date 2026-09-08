from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from html import escape
from pathlib import Path
from typing import Dict, Iterable, Mapping, Sequence, Tuple

from model_permutation_experiment import execute_designer_response
from physical_design_core import BoxGeometry, CandidateDesign, CylinderXGeometry, PhysicalDesignError
from wayfarer_s1_solver import solve

VISUAL_EVIDENCE_VERSION = "LOOM_WAYFARER_VISUAL_EVIDENCE_v0.1"
VISUAL_EVIDENCE_AUTHORITY = "REVIEW_EVIDENCE_ONLY"
STATUS = ("ENGINEERING_RESEARCH", "NON_CANON", "NON_PRODUCTION")


@dataclass(frozen=True)
class ViewSpec:
    view_id: str
    horizontal_axis: str
    vertical_axis: str
    min_u_m: float
    max_u_m: float
    min_v_m: float
    max_v_m: float


@dataclass(frozen=True)
class VisualArtifact:
    artifact_id: str
    candidate_id: str
    view_id: str
    sha256: str
    content: str
    authority_status: str = VISUAL_EVIDENCE_AUTHORITY


@dataclass(frozen=True)
class VisualEvidencePackage:
    version: str
    parent_candidate_id: str
    child_candidate_id: str
    views: Tuple[ViewSpec, ...]
    artifacts: Tuple[VisualArtifact, ...]
    source_response_sha256: str
    package_sha256: str
    authority_status: str = VISUAL_EVIDENCE_AUTHORITY
    flight_dynamics_authority: bool = False
    canon_changed: bool = False
    production_shipclasses_changed: bool = False


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _axis_index(axis: str) -> int:
    try:
        return {"x": 0, "y": 1, "z": 2}[axis]
    except KeyError as exc:
        raise PhysicalDesignError(f"unsupported visual axis {axis!r}") from exc


def _geometry_span(geometry: object, axis: str) -> float:
    if isinstance(geometry, BoxGeometry):
        return {"x": geometry.x_m, "y": geometry.y_m, "z": geometry.z_m}[axis]
    if isinstance(geometry, CylinderXGeometry):
        return geometry.length_m if axis == "x" else geometry.diameter_m
    raise PhysicalDesignError(f"unsupported admitted geometry {type(geometry).__name__}")


def _candidate_bounds(candidate: CandidateDesign, horizontal_axis: str, vertical_axis: str) -> Tuple[float, float, float, float]:
    type_map = {row.type_id: row for row in candidate.component_types}
    ui, vi = _axis_index(horizontal_axis), _axis_index(vertical_axis)
    u0 = u1 = v0 = v1 = None

    def include(u_min: float, u_max: float, v_min: float, v_max: float) -> None:
        nonlocal u0, u1, v0, v1
        u0 = u_min if u0 is None else min(u0, u_min)
        u1 = u_max if u1 is None else max(u1, u_max)
        v0 = v_min if v0 is None else min(v0, v_min)
        v1 = v_max if v1 is None else max(v1, v_max)

    for instance in candidate.component_instances:
        if not instance.active:
            continue
        ctype = type_map.get(instance.component_type_id)
        if ctype is None or ctype.admitted_geometry is None:
            continue
        center = instance.transform.translation_m
        hu = _geometry_span(ctype.admitted_geometry, horizontal_axis) / 2.0
        hv = _geometry_span(ctype.admitted_geometry, vertical_axis) / 2.0
        include(center[ui] - hu, center[ui] + hu, center[vi] - hv, center[vi] + hv)

    for point in candidate.point_masses:
        u, v = float(point.centroid_m[ui]), float(point.centroid_m[vi])
        include(u - 0.15, u + 0.15, v - 0.15, v + 0.15)

    if u0 is None:
        raise PhysicalDesignError("candidate contains no drawable admitted geometry or point masses")
    return float(u0), float(u1), float(v0), float(v1)


def _shared_view(parent: CandidateDesign, child: CandidateDesign, view_id: str, horizontal_axis: str, vertical_axis: str) -> ViewSpec:
    p = _candidate_bounds(parent, horizontal_axis, vertical_axis)
    c = _candidate_bounds(child, horizontal_axis, vertical_axis)
    u0, u1 = min(p[0], c[0]), max(p[1], c[1])
    v0, v1 = min(p[2], c[2]), max(p[3], c[3])
    pad_u = max(1.0, 0.05 * max(1.0, u1 - u0))
    pad_v = max(1.0, 0.10 * max(1.0, v1 - v0))
    return ViewSpec(view_id, horizontal_axis, vertical_axis, u0 - pad_u, u1 + pad_u, v0 - pad_v, v1 + pad_v)


def _project(view: ViewSpec, u_m: float, v_m: float, width: int, height: int, margin: int = 55) -> Tuple[float, float]:
    usable_w = width - 2 * margin
    usable_h = height - 2 * margin
    x = margin + (u_m - view.min_u_m) * usable_w / (view.max_u_m - view.min_u_m)
    y = height - margin - (v_m - view.min_v_m) * usable_h / (view.max_v_m - view.min_v_m)
    return x, y


def _svg(candidate: CandidateDesign, view: ViewSpec, title: str) -> str:
    width, height, margin = 1200, 600, 55
    type_map = {row.type_id: row for row in candidate.component_types}
    ui, vi = _axis_index(view.horizontal_axis), _axis_index(view.vertical_axis)
    rows = []
    rows.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    rows.append('<rect width="100%" height="100%" fill="white"/>')
    rows.append('<g fill="none" stroke="black" stroke-width="1.5">')
    rows.append(f'<rect x="{margin}" y="{margin}" width="{width-2*margin}" height="{height-2*margin}"/>')
    rows.append('</g>')
    rows.append(f'<text x="{margin}" y="28" font-family="monospace" font-size="18">{escape(title)}</text>')
    rows.append(f'<text x="{margin}" y="48" font-family="monospace" font-size="12">candidate={escape(candidate.candidate_id)}  view={escape(view.view_id)}  axes={view.horizontal_axis}/{view.vertical_axis}  authority={VISUAL_EVIDENCE_AUTHORITY}</text>')

    for instance in sorted(candidate.component_instances, key=lambda row: row.instance_id):
        if not instance.active:
            continue
        ctype = type_map.get(instance.component_type_id)
        if ctype is None or ctype.admitted_geometry is None:
            continue
        center = instance.transform.translation_m
        hu = _geometry_span(ctype.admitted_geometry, view.horizontal_axis) / 2.0
        hv = _geometry_span(ctype.admitted_geometry, view.vertical_axis) / 2.0
        x0, y1 = _project(view, center[ui] - hu, center[vi] - hv, width, height, margin)
        x1, y0 = _project(view, center[ui] + hu, center[vi] + hv, width, height, margin)
        rows.append(f'<rect x="{x0:.3f}" y="{y0:.3f}" width="{x1-x0:.3f}" height="{y1-y0:.3f}" fill="none" stroke="black" stroke-width="2"/>')
        cx, cy = _project(view, center[ui], center[vi], width, height, margin)
        rows.append(f'<line x1="{cx-6:.3f}" y1="{cy:.3f}" x2="{cx+6:.3f}" y2="{cy:.3f}" stroke="black"/>')
        rows.append(f'<line x1="{cx:.3f}" y1="{cy-6:.3f}" x2="{cx:.3f}" y2="{cy+6:.3f}" stroke="black"/>')
        rows.append(f'<text x="{cx+8:.3f}" y="{cy-8:.3f}" font-family="monospace" font-size="11">{escape(instance.instance_id)}</text>')

    for point in sorted(candidate.point_masses, key=lambda row: row.source_id):
        cx, cy = _project(view, float(point.centroid_m[ui]), float(point.centroid_m[vi]), width, height, margin)
        rows.append(f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="3.2" fill="black"/>')
        rows.append(f'<text x="{cx+5:.3f}" y="{cy+12:.3f}" font-family="monospace" font-size="9">{escape(point.source_id)}</text>')

    rows.append(f'<text x="{margin}" y="{height-18}" font-family="monospace" font-size="11">shared bounds: {view.horizontal_axis}=[{view.min_u_m:.3f},{view.max_u_m:.3f}] m; {view.vertical_axis}=[{view.min_v_m:.3f},{view.max_v_m:.3f}] m</text>')
    rows.append('</svg>')
    return "\n".join(rows) + "\n"


def build_visual_evidence(parent: CandidateDesign, child: CandidateDesign, *, source_response_sha256: str) -> VisualEvidencePackage:
    views = (
        _shared_view(parent, child, "LONGITUDINAL_XZ", "x", "z"),
        _shared_view(parent, child, "PLAN_XY", "x", "y"),
    )
    artifacts = []
    for candidate, role in ((parent, "parent"), (child, "child")):
        for view in views:
            content = _svg(candidate, view, f"WAYFARER {role.upper()} — {view.view_id}")
            artifacts.append(VisualArtifact(
                artifact_id=f"{role}_{view.view_id.lower()}.svg",
                candidate_id=candidate.candidate_id,
                view_id=view.view_id,
                sha256=_sha(content),
                content=content,
            ))
    clean = {
        "version": VISUAL_EVIDENCE_VERSION,
        "parent_candidate_id": parent.candidate_id,
        "child_candidate_id": child.candidate_id,
        "views": [asdict(row) for row in views],
        "artifacts": [{k: v for k, v in asdict(row).items() if k != "content"} for row in artifacts],
        "source_response_sha256": source_response_sha256,
        "authority_status": VISUAL_EVIDENCE_AUTHORITY,
        "flight_dynamics_authority": False,
        "canon_changed": False,
        "production_shipclasses_changed": False,
    }
    return VisualEvidencePackage(
        version=VISUAL_EVIDENCE_VERSION,
        parent_candidate_id=parent.candidate_id,
        child_candidate_id=child.candidate_id,
        views=views,
        artifacts=tuple(artifacts),
        source_response_sha256=source_response_sha256,
        package_sha256=_sha(_canonical(clean)),
    )


def build_run001_visual_evidence(raw_designer_response: str, seed: int = 2226) -> VisualEvidencePackage:
    parent = solve(seed).candidate
    _, _, child, _, _, _ = execute_designer_response(raw_designer_response, seed=seed)
    return build_visual_evidence(parent, child, source_response_sha256=_sha(raw_designer_response))


def write_visual_evidence(package: VisualEvidencePackage, output_dir: Path) -> Mapping[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: Dict[str, str] = {}
    for artifact in package.artifacts:
        path = output_dir / artifact.artifact_id
        path.write_text(artifact.content, encoding="utf-8")
        written[artifact.artifact_id] = artifact.sha256
    manifest = {
        "version": package.version,
        "status": STATUS,
        "parent_candidate_id": package.parent_candidate_id,
        "child_candidate_id": package.child_candidate_id,
        "views": [asdict(row) for row in package.views],
        "artifacts": [{k: v for k, v in asdict(row).items() if k != "content"} for row in package.artifacts],
        "source_response_sha256": package.source_response_sha256,
        "package_sha256": package.package_sha256,
        "authority_status": package.authority_status,
        "flight_dynamics_authority": package.flight_dynamics_authority,
        "canon_changed": package.canon_changed,
        "production_shipclasses_changed": package.production_shipclasses_changed,
    }
    text = json.dumps(manifest, sort_keys=True, indent=2) + "\n"
    (output_dir / "visual_evidence_manifest.json").write_text(text, encoding="utf-8")
    written["visual_evidence_manifest.json"] = _sha(text)
    return written
