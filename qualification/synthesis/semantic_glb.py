from __future__ import annotations

import hashlib
import json
import math
import struct
from typing import Dict, Iterable, Tuple

from governed_ship_synthesis import GovernedSynthesisPackage, validate_package
from semantic_geometry import SemanticGeometryPackage, validate_semantic_geometry

SEMANTIC_GLB_VERSION = "LOOM_SEMANTIC_GLB_v0.1"
SEMANTIC_GLB_AUTHORITY = "DERIVED_ENGINEERING_TRACEABLE_GLB_ONLY"


class SemanticGLBError(ValueError):
    pass


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json_bytes(payload: object) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _pad4(data: bytes, pad: bytes) -> bytes:
    return data + pad * ((-len(data)) % 4)


def _finite_vec3(vertex: Iterable[float]) -> Tuple[float, float, float]:
    values = tuple(float(v) for v in vertex)
    if len(values) != 3 or any(not math.isfinite(v) for v in values):
        raise SemanticGLBError("GLB vertex must be a finite vec3")
    return values  # type: ignore[return-value]


def _append_aligned(buffer: bytearray, payload: bytes) -> Tuple[int, int]:
    while len(buffer) % 4:
        buffer.append(0)
    offset = len(buffer)
    buffer.extend(payload)
    return offset, len(payload)


def _encode_indices(indices):
    maximum = max(indices)
    if maximum <= 65535:
        return struct.pack("<" + "H" * len(indices), *indices), 5123
    return struct.pack("<" + "I" * len(indices), *indices), 5125


def build_semantic_glb(source: GovernedSynthesisPackage, semantic: SemanticGeometryPackage):
    validate_package(source)
    validate_semantic_geometry(semantic, source)
    if len(source.geometry.primitives) != len(semantic.objects):
        raise SemanticGLBError("source/semantic primitive count mismatch")
    sem_by_primitive = {row.primitive_id: row for row in semantic.objects}
    if len(sem_by_primitive) != len(semantic.objects):
        raise SemanticGLBError("duplicate semantic primitive mapping")

    binary = bytearray(); buffer_views = []; accessors = []; meshes = []; nodes = []; materials = []
    material_by_class: Dict[str, int] = {}
    class_colors = {
        "ADMITTED_SPATIAL_ENVELOPE": [0.45, 0.70, 0.90, 1.0],
        "STRUCTURAL_HYPOTHESIS": [0.82, 0.82, 0.82, 1.0],
        "SOURCE_NODE_PROXY": [0.95, 0.62, 0.28, 1.0],
    }

    for primitive in source.geometry.primitives:
        sem = sem_by_primitive[primitive.primitive_id]
        vertices = tuple(_finite_vec3(v) for v in primitive.vertices_m)
        if not vertices:
            raise SemanticGLBError(f"empty vertex set: {primitive.primitive_id}")
        flat = [c for v in vertices for c in v]
        pb = struct.pack("<" + "f" * len(flat), *flat)
        po, pl = _append_aligned(binary, pb)
        pv = len(buffer_views)
        buffer_views.append({"buffer": 0, "byteOffset": po, "byteLength": pl, "target": 34962})
        pa = len(accessors)
        accessors.append({"bufferView": pv, "byteOffset": 0, "componentType": 5126, "count": len(vertices), "type": "VEC3", "min": [min(v[i] for v in vertices) for i in range(3)], "max": [max(v[i] for v in vertices) for i in range(3)]})

        inds = []
        for tri in primitive.triangles:
            if len(tri) != 3:
                raise SemanticGLBError(f"non-triangle primitive: {primitive.primitive_id}")
            for idx in tri:
                value = int(idx)
                if value < 0 or value >= len(vertices):
                    raise SemanticGLBError(f"triangle index out of range: {primitive.primitive_id}")
                inds.append(value)
        if not inds:
            raise SemanticGLBError(f"empty triangle set: {primitive.primitive_id}")
        ib, index_component_type = _encode_indices(inds)
        io, il = _append_aligned(binary, ib)
        iv = len(buffer_views)
        buffer_views.append({"buffer": 0, "byteOffset": io, "byteLength": il, "target": 34963})
        ia = len(accessors)
        accessors.append({"bufferView": iv, "byteOffset": 0, "componentType": index_component_type, "count": len(inds), "type": "SCALAR", "min": [min(inds)], "max": [max(inds)]})

        if sem.semantic_class not in material_by_class:
            material_by_class[sem.semantic_class] = len(materials)
            materials.append({"name": sem.semantic_class, "doubleSided": True, "pbrMetallicRoughness": {"baseColorFactor": class_colors.get(sem.semantic_class, [0.7, 0.7, 0.7, 1.0]), "metallicFactor": 0.0, "roughnessFactor": 0.9}})
        mi = len(meshes)
        meshes.append({"name": primitive.primitive_id, "primitives": [{"attributes": {"POSITION": pa}, "indices": ia, "material": material_by_class[sem.semantic_class], "mode": 4}]})
        nodes.append({"name": sem.semantic_object_id, "mesh": mi, "extras": {"semantic_object_id": sem.semantic_object_id, "primitive_id": sem.primitive_id, "primitive_kind": sem.primitive_kind, "source_object_id": sem.source_object_id, "source_component_id": sem.source_component_id, "source_kind": sem.source_kind, "semantic_class": sem.semantic_class, "system_id": sem.system_id, "function": sem.function, "geometry_role": sem.geometry_role, "visual_mutability": sem.visual_mutability, "engineering_status": sem.engineering_status, "authority_status": sem.authority_status, "provenance_refs": list(sem.provenance_refs)}})

    gltf = {"asset": {"version": "2.0", "generator": SEMANTIC_GLB_VERSION, "extras": {"authority_status": SEMANTIC_GLB_AUTHORITY, "source_design_candidate_id": semantic.source_design_candidate_id, "source_design_candidate_hash": semantic.source_design_candidate_hash, "source_governed_package_hash": semantic.source_governed_package_hash, "source_geometry_hash": semantic.source_geometry_hash, "source_semantic_package_hash": semantic.package_hash, "flight_dynamics_authority": False, "canon_changed": False, "production_shipclasses_changed": False}}, "scene": 0, "scenes": [{"name": "LOOM_WAYFARER_SEMANTIC_SCENE", "nodes": list(range(len(nodes)))}], "nodes": nodes, "meshes": meshes, "materials": materials, "accessors": accessors, "bufferViews": buffer_views, "buffers": [{"byteLength": len(binary)}]}
    jc = _pad4(_canonical_json_bytes(gltf), b" "); bc = _pad4(bytes(binary), b"\x00")
    total = 12 + 8 + len(jc) + 8 + len(bc)
    glb = struct.pack("<4sII", b"glTF", 2, total) + struct.pack("<II", len(jc), 0x4E4F534A) + jc + struct.pack("<II", len(bc), 0x004E4942) + bc
    if len(glb) != total:
        raise SemanticGLBError("GLB length mismatch")
    manifest = {"version": SEMANTIC_GLB_VERSION, "authority_status": SEMANTIC_GLB_AUTHORITY, "source_design_candidate_id": semantic.source_design_candidate_id, "source_design_candidate_hash": semantic.source_design_candidate_hash, "source_governed_package_hash": semantic.source_governed_package_hash, "source_geometry_hash": semantic.source_geometry_hash, "source_semantic_package_hash": semantic.package_hash, "glb_sha256": _sha256_bytes(glb), "glb_byte_length": len(glb), "object_count": len(nodes), "open_semantic_items": list(semantic.open_semantic_items), "flight_dynamics_authority": False, "canon_changed": False, "production_shipclasses_changed": False}
    return glb, manifest


def canonical_manifest_json(manifest: dict) -> str:
    if manifest.get("authority_status") != SEMANTIC_GLB_AUTHORITY:
        raise SemanticGLBError("GLB manifest authority escalation")
    if manifest.get("flight_dynamics_authority") or manifest.get("canon_changed") or manifest.get("production_shipclasses_changed"):
        raise SemanticGLBError("GLB manifest may not mutate frozen authority")
    return _canonical_json_bytes(manifest).decode("utf-8")
