from __future__ import annotations

import argparse
import json
import math
import struct
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

EXPORTER_VERSION = "0.1"
GROUP_COLORS = {
    "habitat": (0.72, 0.71, 0.66, 1.0),
    "tanks": (0.55, 0.55, 0.53, 1.0),
    "structure": (0.24, 0.27, 0.30, 1.0),
    "launch_bay": (0.38, 0.34, 0.29, 1.0),
    "launch": (0.70, 0.67, 0.58, 1.0),
    "radiators": (0.08, 0.09, 0.10, 1.0),
    "propulsion": (0.31, 0.31, 0.33, 1.0),
    "docking": (0.58, 0.54, 0.47, 1.0),
}
DEFAULT_COLOR = (0.5, 0.5, 0.5, 1.0)


def loom_to_gltf(v: Sequence[float]) -> Tuple[float, float, float]:
    """Map LOOM (X,Y,Z) to right-handed glTF/Godot-friendly (X,Z,-Y)."""
    return float(v[0]), float(v[2]), -float(v[1])


def _sub(a, b):
    return a[0] - b[0], a[1] - b[1], a[2] - b[2]


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _normal(v):
    n = math.sqrt(sum(x * x for x in v))
    return (0.0, 1.0, 0.0) if n <= 1e-12 else tuple(x / n for x in v)


def flat_mesh(tris: Iterable[Tuple[Sequence[float], Sequence[float], Sequence[float]]]):
    positions: List[Tuple[float, float, float]] = []
    normals: List[Tuple[float, float, float]] = []
    indices: List[int] = []
    for tri in tris:
        a, b, c = (loom_to_gltf(p) for p in tri)
        n = _normal(_cross(_sub(b, a), _sub(c, a)))
        base = len(positions)
        positions.extend((a, b, c))
        normals.extend((n, n, n))
        indices.extend((base, base + 1, base + 2))
    return positions, normals, indices


def box_tris(x: float, y: float, z: float):
    hx, hy, hz = x / 2, y / 2, z / 2
    p = [
        (-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
        (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz),
    ]
    faces = [
        (0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
        (0, 1, 5), (0, 5, 4), (3, 7, 6), (3, 6, 2),
        (0, 4, 7), (0, 7, 3), (1, 2, 6), (1, 6, 5),
    ]
    return [(p[a], p[b], p[c]) for a, b, c in faces]


def cylinder_tris(length: float, diameter: float, axis: str = "x", segments: int = 20):
    r, half, tris = diameter / 2, length / 2, []

    def pt(axial, u, v):
        return (axial, u, v) if axis == "x" else (u, v, axial)

    for i in range(segments):
        a0, a1 = 2 * math.pi * i / segments, 2 * math.pi * (i + 1) / segments
        u0, v0 = r * math.cos(a0), r * math.sin(a0)
        u1, v1 = r * math.cos(a1), r * math.sin(a1)
        p00, p01 = pt(-half, u0, v0), pt(-half, u1, v1)
        p10, p11 = pt(half, u0, v0), pt(half, u1, v1)
        tris.extend(((p00, p10, p11), (p00, p11, p01)))
        tris.extend(((pt(-half, 0, 0), p01, p00), (pt(half, 0, 0), p10, p11)))
    return tris


def frustum_x_tris(length: float, front_diameter: float, aft_diameter: float, segments: int = 24):
    r0, r1 = front_diameter / 2, aft_diameter / 2
    x0, x1, tris = -length / 2, length / 2, []
    for i in range(segments):
        a0, a1 = 2 * math.pi * i / segments, 2 * math.pi * (i + 1) / segments
        p00 = (x0, r0 * math.cos(a0), r0 * math.sin(a0))
        p01 = (x0, r0 * math.cos(a1), r0 * math.sin(a1))
        p10 = (x1, r1 * math.cos(a0), r1 * math.sin(a0))
        p11 = (x1, r1 * math.cos(a1), r1 * math.sin(a1))
        tris.extend(((p00, p10, p11), (p00, p11, p01)))
    return tris


def _rotate_x(p, angle):
    x, y, z = p
    c, s = math.cos(angle), math.sin(angle)
    return x, y * c - z * s, y * s + z * c


def _translate(p, t):
    return p[0] + t[0], p[1] + t[1], p[2] + t[2]


def radiator_tris(component: Mapping[str, Any], state: str):
    d = component["dimensions"]
    az = math.radians(float(d["azimuth_deg"]))
    if state == "DEPLOYED":
        dims = (float(d["root_length_m"]), float(d["panel_chord_m"]), 0.12)
        offset = (0.0, math.cos(az) * 8.0, math.sin(az) * 8.0)
    else:
        dims = (float(d["root_length_m"]), 0.18, 6.5)
        offset = (0.0, 0.0, 0.0)
    return [tuple(_translate(_rotate_x(p, az), offset) for p in tri) for tri in box_tris(*dims)]


def component_mesh(component: Mapping[str, Any], radiator_state: str):
    kind, d = component["kind"], component["dimensions"]
    if kind == "box":
        tris = box_tris(float(d["x_m"]), float(d["y_m"]), float(d["z_m"]))
    elif kind == "cylinder_x":
        tris = cylinder_tris(float(d["length_m"]), float(d["diameter_m"]), "x")
    elif kind == "nozzle_x":
        aperture = float(d["aperture_diameter_m"])
        tris = frustum_x_tris(float(d["length_m"]), aperture * 0.56, aperture)
    elif kind == "collar_z":
        tris = cylinder_tris(float(d["depth_m"]), float(d["diameter_m"]), "z")
    elif kind == "radiator_placeholder":
        tris = radiator_tris(component, radiator_state)
    else:
        return None
    return flat_mesh(tris)


def _pad4(data: bytes, byte: bytes) -> bytes:
    return data + byte * ((-len(data)) % 4)


def build_glb_bytes(
    payload: Mapping[str, Any],
    launch_state: str = "DOCKED",
    radiator_state: str = "STOWED",
) -> bytes:
    if payload.get("schema") != "LOOM.Wayfarer.Geometry":
        raise ValueError("Input is not LOOM.Wayfarer.Geometry")
    if launch_state not in {"DOCKED", "ABSENT"}:
        raise ValueError("launch_state must be DOCKED or ABSENT")
    if radiator_state not in {"STOWED", "DEPLOYED"}:
        raise ValueError("radiator_state must be STOWED or DEPLOYED")

    gltf: Dict[str, Any] = {
        "asset": {
            "version": "2.0",
            "generator": f"LOOM Wayfarer GLB Exporter v{EXPORTER_VERSION}",
            "extras": {
                "source_schema": payload.get("schema"),
                "source_schema_version": payload.get("schema_version"),
                "coordinate_mapping": "LOOM (X,Y,Z) -> glTF (X,Z,-Y)",
                "authority": "interchange derivative; LOOM SQL/geometry JSON remains authoritative",
            },
        },
        "scene": 0,
        "scenes": [{"nodes": [], "extras": {"launch_state": launch_state, "radiator_state": radiator_state}}],
        "nodes": [], "meshes": [], "materials": [], "bufferViews": [], "accessors": [],
        "buffers": [{"byteLength": 0}],
    }
    binary = bytearray()
    material_map = {}

    def material_index(group, status):
        key = (group, status)
        if key in material_map:
            return material_map[key]
        rgba = list(GROUP_COLORS.get(group, DEFAULT_COLOR))
        rgba[3] = 0.45 if status == "OPEN" else 1.0
        mat = {
            "name": f"{group}_{status}",
            "pbrMetallicRoughness": {
                "baseColorFactor": rgba,
                "metallicFactor": 0.35,
                "roughnessFactor": 0.58,
            },
        }
        if rgba[3] < 1:
            mat.update({"alphaMode": "BLEND", "doubleSided": True})
        material_map[key] = len(gltf["materials"])
        gltf["materials"].append(mat)
        return material_map[key]

    def add_view(data, target):
        while len(binary) % 4:
            binary.append(0)
        offset = len(binary)
        binary.extend(data)
        idx = len(gltf["bufferViews"])
        gltf["bufferViews"].append({"buffer": 0, "byteOffset": offset, "byteLength": len(data), "target": target})
        return idx

    def add_accessor(view, component_type, count, kind, mins=None, maxs=None):
        accessor = {
            "bufferView": view, "byteOffset": 0, "componentType": component_type,
            "count": count, "type": kind,
        }
        if mins is not None:
            accessor["min"] = list(mins)
        if maxs is not None:
            accessor["max"] = list(maxs)
        gltf["accessors"].append(accessor)
        return len(gltf["accessors"]) - 1

    for component in payload.get("components", []):
        if component.get("id") == "planetary_launch" and launch_state == "ABSENT":
            continue
        mesh = component_mesh(component, radiator_state)
        if mesh is None:
            continue
        positions, normals, indices = mesh
        pdat = struct.pack("<" + "f" * (3 * len(positions)), *(x for row in positions for x in row))
        ndat = struct.pack("<" + "f" * (3 * len(normals)), *(x for row in normals for x in row))
        idat = struct.pack("<" + "I" * len(indices), *indices)
        pv, nv, iv = add_view(pdat, 34962), add_view(ndat, 34962), add_view(idat, 34963)
        mins = tuple(min(row[i] for row in positions) for i in range(3))
        maxs = tuple(max(row[i] for row in positions) for i in range(3))
        pa = add_accessor(pv, 5126, len(positions), "VEC3", mins, maxs)
        na = add_accessor(nv, 5126, len(normals), "VEC3")
        ia = add_accessor(iv, 5125, len(indices), "SCALAR")
        gltf["meshes"].append({
            "name": component["id"],
            "primitives": [{
                "attributes": {"POSITION": pa, "NORMAL": na},
                "indices": ia,
                "material": material_index(component.get("group", "other"), component.get("status", "OPEN")),
            }],
        })
        center = loom_to_gltf(component.get("center_m", (0, 0, 0)))
        gltf["nodes"].append({
            "name": component["id"],
            "mesh": len(gltf["meshes"]) - 1,
            "translation": list(center),
            "extras": {
                "loom_component_id": component.get("id"),
                "loom_kind": component.get("kind"),
                "loom_group": component.get("group"),
                "loom_status": component.get("status"),
                "loom_source": component.get("source"),
                "loom_center_m": component.get("center_m"),
                "loom_dimensions": component.get("dimensions"),
            },
        })
        gltf["scenes"][0]["nodes"].append(len(gltf["nodes"]) - 1)

    gltf["buffers"][0]["byteLength"] = len(binary)
    json_chunk = _pad4(json.dumps(gltf, separators=(",", ":"), sort_keys=True).encode("utf-8"), b" ")
    bin_chunk = _pad4(bytes(binary), b"\x00")
    total = 12 + 8 + len(json_chunk) + 8 + len(bin_chunk)
    return (
        struct.pack("<4sII", b"glTF", 2, total)
        + struct.pack("<II", len(json_chunk), 0x4E4F534A) + json_chunk
        + struct.pack("<II", len(bin_chunk), 0x004E4942) + bin_chunk
    )


def export_glb(input_path: Path, output_path: Path, launch_state: str, radiator_state: str) -> int:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    data = build_glb_bytes(payload, launch_state, radiator_state)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)
    return len(data)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Export deterministic LOOM Wayfarer geometry JSON to binary glTF (.glb).")
    parser.add_argument("--input", default="geometry/wayfarer_geometry.json")
    parser.add_argument("--output", default="geometry/wayfarer.glb")
    parser.add_argument("--launch", choices=["DOCKED", "ABSENT"], default="DOCKED")
    parser.add_argument("--radiators", choices=["STOWED", "DEPLOYED"], default="STOWED")
    args = parser.parse_args(argv)
    size = export_glb(Path(args.input), Path(args.output), args.launch, args.radiators)
    print(f"LOOM Wayfarer GLB: {args.output} ({size} bytes) launch={args.launch} radiators={args.radiators}")


if __name__ == "__main__":
    main()
