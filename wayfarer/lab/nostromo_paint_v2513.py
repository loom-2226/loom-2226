#!/usr/bin/env python3
"""Wayfarer v2.5.13 NOSTROMO: four seeded CANON_FINISH glTF material tones, never new solids.

Partition EXISTING GLB triangles by the approved axial/azimuth seam cells.
Indices and PBR materials change; vertex positions, triangles, source mass,
envelope and pressure bodies never change. Printed decals are separate SVG.
"""
from __future__ import annotations
from bisect import bisect_right
from collections import defaultdict
from copy import deepcopy
import hashlib
import math
import struct

SEED = "WAYFARER-NOSTROMO-v2.5.13-20261111"
PLATED = {
    "dry:armor", "dry:skin_service", "dry:skin_midship", "dry:skin_aft",
    "dry:door_port", "dry:door_starboard", "dry:thrust_cone",
    "dry:tank_shell_out",
}
TONES = (.94, .98, 1.02, 1.06)
SEAMS = (0, 40, 140, 180, 220, 270, 320, 360)
COMP = {5121: "B", 5123: "H", 5125: "I", 5126: "f"}
SIZES = {5121: 1, 5123: 2, 5125: 4, 5126: 4}


def _srgb_to_linear(v):
    return ((v + .055) / 1.055) ** 2.4 if v > .04045 else v / 12.92


def _linear_to_srgb(v):
    return 1.055 * (max(v, 0.) ** (1. / 2.4)) - .055 if v > .0031308 else 12.92 * max(v, 0.)


def _tone_linear(value, tone):
    return _srgb_to_linear(min(1., max(0., _linear_to_srgb(value) * tone)))


def _zone(name, x):
    # Detail gathers around real functions. Ordinary plates stay quiet.
    return ((2.35 <= x <= 4.0) or (14. <= x <= 19.5)
            or (31.8 <= x <= 35.0))


def _cell(name, p):
    x, y, z = p
    az = math.degrees(math.atan2(z, y)) % 360.
    if _zone(name, x):
        return ("cluster", int(math.floor(x / .65)), int(az // 30.))
    axial = int(math.floor((x - 14.) / 2.)) if x >= 14. else int(math.floor(x / 2.6))
    return ("calm", axial, bisect_right(SEAMS, az) - 1)


def _tone(role, cell):
    key = (SEED + "|" + role + "|" + ":".join(map(str, cell))).encode()
    variant = int.from_bytes(hashlib.sha256(key).digest()[:8], "big") % 4
    return variant, TONES[variant]


def apply(data, tail):
    """Return (repacked BIN tail, evidence), preserving all source triangles."""
    assert len(data["buffers"]) == 1 and len(tail) >= 8
    size, kind = struct.unpack_from("<II", tail)
    if kind != 0x004e4942 or len(tail) != 8 + size:
        raise RuntimeError("STOP export: NOSTROMO malformed BIN chunk")
    binary = bytearray(tail[8:])

    def view(raw, target=None):
        while len(binary) % 4:
            binary.append(0)
        offset = len(binary)
        binary.extend(raw)
        desc = dict(buffer=0, byteOffset=offset, byteLength=len(raw))
        if target is not None:
            desc["target"] = target
        index = len(data["bufferViews"])
        data["bufferViews"].append(desc)
        return index

    def accessor(number):
        acc = data["accessors"][number]
        if "sparse" in acc or "bufferView" not in acc:
            raise RuntimeError("STOP export: NOSTROMO sparse accessor")
        if acc["componentType"] not in COMP or acc["type"] not in ("SCALAR", "VEC3"):
            raise RuntimeError("STOP export: NOSTROMO unsupported accessor")
        comps = 3 if acc["type"] == "VEC3" else 1
        size = comps * SIZES[acc["componentType"]]
        bv = data["bufferViews"][acc["bufferView"]]
        stride = bv.get("byteStride", size)
        offset = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
        fmt = "<" + COMP[acc["componentType"]] * comps
        return [struct.unpack_from(fmt, binary, offset + i * stride)
                for i in range(acc["count"])]

    source_image_count=len(data.get("images",[]))
    source_texture_count=len(data.get("textures",[]))
    material_cache = {}
    source_triangles = output_triangles = 0
    plated_meshes = 0
    by_finish = defaultdict(set)
    tones = []
    seen_mesh_indices = set()
    for node in data["nodes"]:
        name = node.get("name", "")
        if "mesh" not in node or name not in PLATED:
            continue
        mid = node["mesh"]
        if mid in seen_mesh_indices:
            raise RuntimeError("STOP export: NOSTROMO shared mutable mesh " + name)
        seen_mesh_indices.add(mid)
        role = node.get("extras", {}).get("finish_role")
        if not role or role == "source_palette_preserved":
            raise RuntimeError("STOP export: NOSTROMO absent approved role " + name)
        mesh = data["meshes"][mid]
        replacements = []
        node_cells = set()
        for prim in mesh["primitives"]:
            if prim.get("mode", 4) != 4 or prim.get("targets"):
                raise RuntimeError("STOP export: NOSTROMO requires static triangle primitive")
            pos_id = prim["attributes"]["POSITION"]
            if data["accessors"][pos_id]["type"] != "VEC3":
                raise RuntimeError("STOP export: NOSTROMO missing VEC3 positions")
            positions = accessor(pos_id)
            if "indices" in prim:
                ids = [int(x[0]) for x in accessor(prim["indices"])]
            else:
                ids = list(range(len(positions)))
            if len(ids) % 3 or any(i < 0 or i >= len(positions) for i in ids):
                raise RuntimeError("STOP export: NOSTROMO triangle index integrity")
            groups = defaultdict(list)
            for t in range(0, len(ids), 3):
                tri = ids[t:t + 3]
                centroid = tuple(sum(positions[k][axis] for k in tri) / 3.
                                 for axis in range(3))
                cell = _cell(name, centroid)
                variant,tone=_tone(role,cell)
                groups[variant].extend(tri)
                node_cells.add(cell)
            source_triangles += len(ids) // 3
            if sum(map(len, groups.values())) != len(ids):
                raise RuntimeError("STOP export: NOSTROMO lost triangles")
            for variant in sorted(groups):
                tri_ids = groups[variant]
                tone = TONES[variant]
                tones.append(tone)
                source_mat_id = prim["material"]
                cache_key = (source_mat_id, variant)
                if cache_key not in material_cache:
                    src = data["materials"][source_mat_id]
                    mat = deepcopy(src)
                    pbr = mat["pbrMetallicRoughness"]
                    old = pbr["baseColorFactor"]
                    pbr["baseColorFactor"] = [_tone_linear(v, tone) for v in old[:3]] + old[3:]
                    mat["name"] = "CANON_FINISH/" + role + "/PANEL_" + str(variant)
                    mat["extras"] = dict(panel_tone_srgb_factor=tone, panel_variant=variant,
                                         seed=SEED, print_decal_geometry=False)
                    material_cache[cache_key] = len(data["materials"])
                    data["materials"].append(mat)
                by_finish[role].add(variant)
                iview = view(struct.pack("<" + "I" * len(tri_ids), *tri_ids), 34963)
                index_id = len(data["accessors"])
                data["accessors"].append(dict(bufferView=iview, byteOffset=0,
                    componentType=5125, count=len(tri_ids), type="SCALAR",
                    min=[min(tri_ids)], max=[max(tri_ids)]))
                piece = dict(prim)
                piece["indices"] = index_id
                piece["attributes"] = dict(prim["attributes"])
                piece["material"] = material_cache[cache_key]
                replacements.append(piece)
                output_triangles += len(tri_ids) // 3
        mesh["primitives"] = replacements
        node.setdefault("extras", {}).update(
            nostromo_plate_count=len(node_cells), nostromo_paint_seed=SEED,
            nostromo_plain_materials=True, print_markings_not_in_glb=True,
            source_mass_rebooking_t=0)
        plated_meshes += 1
    if plated_meshes < 7:
        raise RuntimeError("STOP export: NOSTROMO no plated / painted surfaces")
    if source_triangles != output_triangles:
        raise RuntimeError("STOP export: NOSTROMO triangle conservation failure")
    if any(not (.94 <= t <= 1.06) for t in tones) or any(len(v)>4 for v in by_finish.values()):
        raise RuntimeError("STOP export: NOSTROMO panel tone/variant bound")
    if len(data.get("images",[]))!=source_image_count or len(data.get("textures",[]))!=source_texture_count:
        raise RuntimeError("STOP export: NOSTROMO must not add textures")
    while len(binary) % 4:
        binary.append(0)
    data["buffers"][0]["byteLength"] = len(binary)
    tail = struct.pack("<II", len(binary), 0x004e4942) + bytes(binary)
    data.setdefault("asset", {}).setdefault("extras", {})["nostromo_finish_seed"] = SEED
    evidence = dict(seed=SEED, plated_meshes=plated_meshes,
        panel_materials_added=len(material_cache),
        tone_variants_srgb=list(TONES),
        material_variants_by_finish={k:sorted(v) for k,v in by_finish.items()},
        panel_srgb_tone_min=min(tones), panel_srgb_tone_max=max(tones),
        panel_srgb_tone_bound=.06,
        source_triangles=source_triangles, output_triangles=output_triangles,
        original_vertex_positions_preserved=True,
        source_mass_rebooking_t=0, geometry_added=False, protrusions_added=False,
        texture_system_added=False, decal_texture_embedded=False,
        source_images_count=source_image_count,source_textures_count=source_texture_count,
        registry_flanks_in_glb=0,plain_gltf_materials=True,
        print_decal_artwork="wayfarer/render/decals/WAYFARER_NOSTROMO_DECALS_v2513.svg")
    return tail, evidence
