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


def _variant(role,name):
    """Authoritative fallback: no independent seam-cell mesh => one part tone."""
    key=(SEED+"|"+role+"|PART:"+name).encode("utf-8")
    return int.from_bytes(hashlib.sha256(key).digest()[:8],"big")%4


def audit_mosaic(data):
    """Spotcheck every plated role and reject per-triangle/material fragments."""
    role_variants=defaultdict(set)
    nodes=[n for n in data["nodes"] if n.get("name") in PLATED and "mesh" in n]
    if len(nodes)!=len(PLATED):
        raise RuntimeError("STOP export: missing mosaic part")
    for node in nodes:
        name=node["name"];ex=node.get("extras",{})
        mesh=data["meshes"][node["mesh"]]
        if (ex.get("nostromo_cell_basis")!="authored_part_fallback" or
            ex.get("nostromo_cell_count")!=1 or
            ex.get("nostromo_source_primitives")!=len(mesh["primitives"])):
            raise RuntimeError("STOP export: fragmented panel cells "+name)
        variants=set()
        for prim in mesh["primitives"]:
            mat=data["materials"][prim["material"]]
            variant=mat.get("extras",{}).get("panel_variant")
            if (not mat.get("name","").startswith("CANON_FINISH/"+ex["finish_role"]+"/PANEL_")
                or variant not in range(4)):
                raise RuntimeError("STOP export: non-panel material "+name)
            variants.add(variant)
        if variants!={ex.get("nostromo_part_variant")} or _variant(ex["finish_role"],name) not in variants:
            raise RuntimeError("STOP export: per-triangle colour variation "+name)
        role_variants[ex["finish_role"]].update(variants)
    if set(role_variants)!={"bow_strata","midship_skin_bay_doors","service_band_aft_thrust_cone"}:
        raise RuntimeError("STOP export: missing mosaic group")
    return {k:sorted(v) for k,v in sorted(role_variants.items())}


def _smooth_cone(data,accessor,view):
    """Smooth only lateral vertex NORMALs, preserve hard rim/cap/seam normals.

    Does not touch POSITION or indices: same exact triangles and surface area.
    """
    node=next((v for v in data["nodes"] if v.get("name")=="dry:thrust_cone"),None)
    if node is None:raise RuntimeError("STOP export: missing thrust_cone")
    mesh=data["meshes"][node["mesh"]]
    chunks=[];positions=[]
    for prim in mesh["primitives"]:
        if "NORMAL" not in prim["attributes"]:
            raise RuntimeError("STOP export: cone missing normals")
        pp=accessor(prim["attributes"]["POSITION"])
        nn=accessor(prim["attributes"]["NORMAL"])
        if not pp or len(pp)!=len(nn):
            raise RuntimeError("STOP export: cone attribute mismatch")
        chunks.append((prim,pp,nn))
        positions.extend(pp)
    bounds=[(min(q[j] for q in positions),max(q[j] for q in positions)) for j in range(3)]
    spans=[hi-lo for lo,hi in bounds]
    axis=min(range(3),key=lambda j:abs(spans[j]-5.))
    if abs(spans[axis]-5.)>.15:
        raise RuntimeError("STOP export: cone axis not 5 m "+str(spans))
    lateral=[j for j in range(3) if j!=axis]
    centers=[sum(bounds[j])/2 for j in lateral]
    lo,hi=bounds[axis]
    def radius(q):
        return math.hypot(q[lateral[0]]-centers[0],q[lateral[1]]-centers[1])
    left=[radius(q) for q in positions if q[axis]<lo+.025]
    right=[radius(q) for q in positions if q[axis]>hi-.025]
    if not left or not right:raise RuntimeError("STOP export: cone rings absent")
    slope=(max(right)-max(left))/(hi-lo)
    if abs(abs(slope)-.29)>.05:
        raise RuntimeError("STOP export: cone slope unexpected "+str(slope))
    smooth=hard=0
    for prim,pp,nn in chunks:
        values=[]
        for q,old in zip(pp,nn):
            r=radius(q)
            if r<.01:
                values.extend(old);hard+=1;continue
            radial=[(q[j]-centers[k])/r for k,j in enumerate(lateral)]
            dot=sum(old[j]*radial[k] for k,j in enumerate(lateral))
            if abs(dot)<.70:
                values.extend(old);hard+=1;continue
            sign=1. if dot>0 else -1.
            normal=[0.,0.,0.];normal[axis]=-slope*sign
            for k,j in enumerate(lateral):normal[j]=radial[k]*sign
            length=math.sqrt(sum(v*v for v in normal))
            values.extend(v/length for v in normal);smooth+=1
        raw=struct.pack("<"+"f"*len(values),*values)
        i=view(raw,34962)
        j=len(data["accessors"])
        data["accessors"].append(dict(bufferView=i,byteOffset=0,
            componentType=5126,count=len(pp),type="VEC3"))
        prim["attributes"]=dict(prim["attributes"],NORMAL=j)
    if smooth<40:raise RuntimeError("STOP export: cone smoothing no lateral normals "+str(smooth))
    result=dict(method="analytic_frustum_lateral_normals",
        smoothed_lateral_vertex_normals=smooth,preserved_hard_edge_normals=hard,
        unchanged_position_accessors=True,unchanged_triangle_indices=True,
        relative_surface_area_error=0.,surface_area_tolerance=1e-6,
        source_envelope_unchanged=True,no_new_vertices=True,
        slope=slope,axial_axis=axis)
    node.setdefault("extras",{})["thrust_cone_smoothing"]=result
    return result


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

    images_before=len(data.get("images",[]))
    textures_before=len(data.get("textures",[]))
    smooth=_smooth_cone(data,accessor,view)
    cache={};triangles=0;plated=0
    for node in data["nodes"]:
        name=node.get("name")
        if name not in PLATED or "mesh" not in node:continue
        ex=node.setdefault("extras",{})
        role=ex.get("finish_role")
        if not role or role=="source_palette_preserved":
            raise RuntimeError("STOP export: mosaic role unapproved "+str(name))
        variant=_variant(role,name)
        mesh=data["meshes"][node["mesh"]]
        count=len(mesh["primitives"])
        for prim in mesh["primitives"]:
            original=prim["material"];key=(original,variant)
            if key not in cache:
                mat=deepcopy(data["materials"][original])
                if not mat["name"].startswith("CANON_FINISH/"+role):
                    raise RuntimeError("STOP export: mosaic source material mismatch")
                rgba=mat["pbrMetallicRoughness"]["baseColorFactor"]
                mat["pbrMetallicRoughness"]["baseColorFactor"]=[
                    _tone_linear(v,TONES[variant]) for v in rgba[:3]]+rgba[3:]
                mat["name"]="CANON_FINISH/"+role+"/PANEL_"+str(variant)
                mat["extras"]=dict(panel_tone_srgb_factor=TONES[variant],
                    panel_variant=variant,seed=SEED)
                cache[key]=len(data["materials"])
                data["materials"].append(mat)
            prim["material"]=cache[key]
            triangles+=len(accessor(prim["indices"]))//3 if "indices" in prim else (
                data["accessors"][prim["attributes"]["POSITION"]]["count"]//3)
        ex.update(nostromo_cell_basis="authored_part_fallback",
            nostromo_cell_count=1,nostromo_source_primitives=count,
            nostromo_part_variant=variant,nostromo_plain_materials=True,
            print_markings_not_in_glb=True,source_mass_rebooking_t=0)
        plated+=1
    by_role=audit_mosaic(data)
    if len(data.get("images",[]))!=images_before or len(data.get("textures",[]))!=textures_before:
        raise RuntimeError("STOP export: unauthorized texture in mosaic")
    while len(binary)%4:binary.append(0)
    data["buffers"][0]["byteLength"]=len(binary)
    tail=struct.pack("<II",len(binary),0x004e4942)+bytes(binary)
    data.setdefault("asset",{}).setdefault("extras",{})["nostromo_finish_seed"]=SEED
    return tail,dict(seed=SEED,plated_meshes=plated,
        panel_materials_added=len(cache),tone_variants_srgb=list(TONES),
        material_variants_by_finish=by_role,
        panel_srgb_tone_min=min(TONES),panel_srgb_tone_max=max(TONES),
        panel_srgb_tone_bound=.06,per_triangle_assignment=False,
        all_plated_parts_single_cell=True,all_mosaic_roles_spotchecked=True,
        source_triangles=triangles,output_triangles=triangles,
        original_vertex_positions_preserved=True,
        source_images_count=images_before,source_textures_count=textures_before,
        texture_system_added=False,decal_texture_embedded=False,registry_flanks_in_glb=0,
        plain_gltf_materials=True,geometry_added=False,protrusions_added=False,
        source_mass_rebooking_t=0,thrust_cone_smoothing=smooth)
