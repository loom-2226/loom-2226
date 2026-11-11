#!/usr/bin/env python3
"""Wayfarer v2.5.13 NOSTROMO: deterministic materials/decal UVs, never new solids.

Partition EXISTING GLB triangles by the approved axial/azimuth seam cells.
Indices and PBR materials change; vertex positions, triangles, source mass,
envelope and pressure bodies never change. Printed decals are separate SVG.
"""
from __future__ import annotations
from bisect import bisect_right
from collections import defaultdict
from copy import deepcopy
import hashlib
import io
import math
import struct

from PIL import Image, ImageDraw, ImageFont

SEED = "WAYFARER-NOSTROMO-v2.5.13-20261111"
PLATED = {
    "dry:armor", "dry:skin_service", "dry:skin_midship", "dry:skin_aft",
    "dry:door_port", "dry:door_starboard", "dry:thrust_cone",
    "dry:tank_shell_out",
}
PAINTED = PLATED - {"dry:tank_shell_out"}
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


def _tone(name, cell):
    key = (SEED + "|" + name + "|" + ":".join(map(str, cell))).encode()
    value = int.from_bytes(hashlib.sha256(key).digest()[:8], "big") / ((1 << 64) - 1)
    return round(.94 + .12 * value, 5)


def _atlas_png():
    """A white multiplier atlas; pigment changes occur without an extra mesh."""
    w, h = 2048, 1024
    im = Image.new("RGB", (w, h), (255, 255, 255))
    ink = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 42)
        small = ImageFont.truetype("DejaVuSans-Bold.ttf", 23)
    except OSError:
        font = ImageFont.load_default()
        small = font

    def point(x, az):
        u = x / 54.
        v = ((az + 90.) % 360.) / 360.
        return (round(w * u), round(h * (1. - v)))

    for az in (0, 180):
        x, y = point(22.4, az)
        ink.text((x, y - 25), "WAYFARER", font=font, fill=(24, 29, 32))
        for station in (3.0, 15.9, 18.7, 33.7):
            bx, by = point(station, az)
            ink.rectangle((bx - 12, by - 19, bx + 12, by + 19),
                          fill=(219, 184, 86))
            for k in (-15, -3, 9):
                ink.line((bx - 10, by + k, bx + 10, by + k + 14),
                         fill=(24, 28, 30), width=5)

    for az in (0, 90, 180, 270):
        x, y = point(3.1, az)
        ink.text((x + 12, y + 12), "RCS", font=small, fill=(22, 26, 28))
        x, y = point(34.0, az)
        ink.text((x - 68, y + 20), "NO STEP", font=small, fill=(18, 21, 23))
    x, y = point(16.0, 270)
    ink.text((x - 32, y + 19), "DOCK", font=small, fill=(25, 29, 32))
    out = io.BytesIO()
    im.save(out, format="PNG")
    return out.getvalue()


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

    image_bytes = _atlas_png()
    image_view = view(image_bytes)
    image_id = len(data.setdefault("images", []))
    data["images"].append(dict(name="WAYFARER_NOSTROMO_PAINT_v2513",
                               mimeType="image/png", bufferView=image_view))
    sampler_id = len(data.setdefault("samplers", []))
    data["samplers"].append(dict(magFilter=9729, minFilter=9729,
                                 wrapS=33071, wrapT=33071))
    texture_id = len(data.setdefault("textures", []))
    data["textures"].append(dict(source=image_id, sampler=sampler_id,
                                 name="WAYFARER_NOSTROMO_DECAL_ATLAS"))

    material_cache = {}
    uv_cache = {}
    source_triangles = output_triangles = 0
    plated_meshes = 0
    paint_meshes = 0
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
            if name in PAINTED:
                paint_meshes += 1
                if pos_id not in uv_cache:
                    uv = []
                    for x, y, z in positions:
                        az = math.degrees(math.atan2(z, y)) % 360.
                        uv.extend((max(0., min(1., x / 54.)),
                                   ((az + 90.) % 360.) / 360.))
                    uv_view = view(struct.pack("<" + "f" * len(uv), *uv), 34962)
                    aid = len(data["accessors"])
                    data["accessors"].append(dict(bufferView=uv_view, byteOffset=0,
                                                  componentType=5126, count=len(positions),
                                                  type="VEC2"))
                    uv_cache[pos_id] = aid
            groups = defaultdict(list)
            for t in range(0, len(ids), 3):
                tri = ids[t:t + 3]
                centroid = tuple(sum(positions[k][axis] for k in tri) / 3.
                                 for axis in range(3))
                cell = _cell(name, centroid)
                groups[cell].extend(tri)
                node_cells.add(cell)
            source_triangles += len(ids) // 3
            if sum(map(len, groups.values())) != len(ids):
                raise RuntimeError("STOP export: NOSTROMO lost triangles")
            for cell in sorted(groups):
                tri_ids = groups[cell]
                tone = _tone(name, cell)
                tones.append(tone)
                source_mat_id = prim["material"]
                cache_key = (source_mat_id, name, cell)
                if cache_key not in material_cache:
                    src = data["materials"][source_mat_id]
                    mat = deepcopy(src)
                    pbr = mat["pbrMetallicRoughness"]
                    old = pbr["baseColorFactor"]
                    pbr["baseColorFactor"] = [_tone_linear(v, tone) for v in old[:3]] + old[3:]
                    if name in PAINTED:
                        pbr["baseColorTexture"] = dict(index=texture_id)
                    suffix = hashlib.sha256((SEED + name + str(cell)).encode()).hexdigest()[:10]
                    mat["name"] = "CANON_FINISH/" + role + "/PANEL_" + suffix
                    mat["extras"] = dict(panel_tone_srgb_factor=tone, panel_cell=list(cell),
                                         seed=SEED, print_decal_geometry=False)
                    material_cache[cache_key] = len(data["materials"])
                    data["materials"].append(mat)
                iview = view(struct.pack("<" + "I" * len(tri_ids), *tri_ids), 34963)
                index_id = len(data["accessors"])
                data["accessors"].append(dict(bufferView=iview, byteOffset=0,
                    componentType=5125, count=len(tri_ids), type="SCALAR",
                    min=[min(tri_ids)], max=[max(tri_ids)]))
                piece = dict(prim)
                piece["indices"] = index_id
                piece["attributes"] = dict(prim["attributes"])
                if name in PAINTED:
                    piece["attributes"]["TEXCOORD_0"] = uv_cache[pos_id]
                piece["material"] = material_cache[cache_key]
                replacements.append(piece)
                output_triangles += len(tri_ids) // 3
        mesh["primitives"] = replacements
        node.setdefault("extras", {}).update(
            nostromo_plate_count=len(node_cells), nostromo_paint_seed=SEED,
            nostromo_decal_atlas=(name in PAINTED), source_mass_rebooking_t=0)
        plated_meshes += 1
    if not plated_meshes or paint_meshes == 0:
        raise RuntimeError("STOP export: NOSTROMO no plated / painted surfaces")
    if source_triangles != output_triangles:
        raise RuntimeError("STOP export: NOSTROMO triangle conservation failure")
    if any(not (.94 <= t <= 1.06) for t in tones):
        raise RuntimeError("STOP export: NOSTROMO panel tone bound")
    while len(binary) % 4:
        binary.append(0)
    data["buffers"][0]["byteLength"] = len(binary)
    tail = struct.pack("<II", len(binary), 0x004e4942) + bytes(binary)
    data.setdefault("asset", {}).setdefault("extras", {})["nostromo_paint"] = SEED
    evidence = dict(seed=SEED, plated_meshes=plated_meshes,
        painted_mesh_primitives=paint_meshes,
        panel_materials_added=len(material_cache),
        panel_srgb_tone_min=min(tones), panel_srgb_tone_max=max(tones),
        panel_srgb_tone_bound=.06,
        source_triangles=source_triangles, output_triangles=output_triangles,
        original_vertex_positions_preserved=True,
        source_mass_rebooking_t=0, geometry_added=False, protrusions_added=False,
        decal_texture_embedded=True, registry_flanks=2,
        print_decal_artwork="wayfarer/render/decals/WAYFARER_NOSTROMO_DECALS_v2513.svg")
    return tail, evidence
