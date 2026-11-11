#!/usr/bin/env python3
"""Wayfarer canon-v2.5.13: approved PBR and strict plane-split nozzle groove faces.

No geometry, physics, density, mass, IR emissivity, or source material changes.
Rewrites only the JSON chunk of the existing GLB: node materials/extras.
Colour is an sRGB viewer paint approximation, NOT a measured spectrum.
"""
from __future__ import annotations
import hashlib,json,math,re,struct
from pathlib import Path
from nozzle_band_faces_v259 import split_nozzle_rings
import nostromo_paint_v2513 as N

ROOT=Path(__file__).resolve().parents[1]
FINISH=ROOT/"config/kt_decisions.json"

def _rgb(hexcode):
    rgb=[int(hexcode[i:i+2],16)/255 for i in (1,3,5)]
    # glTF baseColorFactor is linear, unlike canonical human sRGB swatches.
    return [((v+.055)/1.055)**2.4 if v>.04045 else v/12.92 for v in rgb]

def _entry(f,role):
    e=f["rows"][role]
    assert e["status"]=="CANON_FINISH"
    return e

def role_for(name,meta,mode):
    """Use semantic node ID, not source material alone, to retain distinct skins."""
    n=name.removeprefix("dry:")
    if n=="pressure_vessel":return "interior_pressure_structure"
    if n.startswith(("room_","floor_","outfit_","i4_","deck_","core_")):
        return "interior_pressure_structure"
    if n.startswith(("docking_collar","service_arm","manifold")):
        return "external_fixtures"
    if n.startswith("service_shield_band_"):return "shadow_shield"
    if n.startswith("bay_corner_"):return "external_fixtures"
    if n.startswith("shuttle_v1/"):
        part=n.split("/",1)[1]
        if part.startswith("belly_TPS_"):return "shuttle_belly_tps"
        if part.startswith(("hull_","gullwing_","tail_","pod_","rotor_blade_")):return "shuttle_main_hull"
        if part.startswith(("torch_","magnetic_nozzle_ring")):return "magnetic_nozzle_bronze"
        return "external_fixtures"
    if n in ("armor", "crown_c_additional_strata_gore") or n.startswith(("crown_gore_","wws1_shutter_")):
        return "bow_strata" if n=="armor" else "strata_gores_shutters"
    if n.startswith(("window_","viewport_band_")):
        return "side_glazing"
    if n.startswith(("crown_outer_pressure_dome","crown_inner_pressure_dome")):
        return "crown_pressure_ceramic"
    if n.startswith(("crown_pane_","crown_spare_")):
        return "crown_outer_ceramic"
    if n.startswith(("crown_aoi_","crown_adaptive_")):
        return "aoi_optogel"
    if n.startswith(("crown_osteon_","crown_brow","crown_c_outward_")):
        return "crown_titanium"
    if n in ("skin_midship","door_port","door_starboard"):
        return "midship_skin_bay_doors"
    if n in ("skin_service","skin_aft","thrust_cone"):
        return "service_band_aft_thrust_cone"
    if n=="tank_shell_out":return "midship_skin_bay_doors"
    if n=="tank_shell_in":return "tank_shell"
    if n=="shield":return "shadow_shield"
    if n=="reactor":return "torch_reactor"
    if n=="nozzle":return "magnetic_nozzle_bronze"
    if n.startswith("strake_"):return "radiator_strakes"
    if n.startswith("hotfin_") or n.startswith("hotfin_root_"):
        return "hotfin_torch_1750K" if mode=="torch" and ":pleat_" in name else "hotfin_cold"
    if n.startswith("rcs_"):return "rcs_housings_bells"
    if n.startswith(("ext_sensor_","ext_rf_","ext_laser_","ext_star_","docking_camera","bow_sensors")):
        return "sensors_optics"
    if n.startswith(("ext_","hold_existing_door","frame_","longeron_")):
        return "external_fixtures"
    # Remaining booked internal parts are visible through sectioned glazing.
    # Unclassified/source palette material is not an approved finish.
    return "interior_pressure_structure"

def _hot_state(name,mode):
    if mode=="metric_hard" and name.startswith("dry:strake_"):
        return ("STRAKE_1300K_2M",[.64,.065,.008],.70)
    if mode=="torch" and name.startswith("dry:strake_"):
        return ("STRAKE_1300K_4M",[.64,.065,.008],.70)
    if mode=="torch" and name.startswith("dry:hotfin_") and ":pleat_" in name:
        mt=re.search(r":pleat_(\d+)",name)
        idx=int(mt.group(1)) if mt else 0
        strength=max(.45,1.25-(idx*.80/13))
        return ("HOTFIN_1750K_ROOT_GRADED",[1.,.20,.015],strength)
    return (None,[0,0,0],0)

def assign_pbr(path,source_mesh_extras,mode):
    f=json.loads(FINISH.read_text())["canon_finish_2026_11_11"]
    assert f["status"]=="CANON_FINISH" and f["decision"]=="kT APPROVED"
    assert len(f["rows"])==24
    assert f["colour_conversion_audit"]["expected_declared_roles"]==23
    assert f["rows"]["interior_pressure_structure"]["status"]=="CANON_FINISH"
    assert f["rows"]["service_band_aft_thrust_cone"]["linear_base_scale"]==0.57
    assert all(v["status"]=="CANON_FINISH" for v in f["rows"].values())
    converted={role:_rgb(v["base_srgb_hex"]) for role,v in f["rows"].items()}
    assert len(converted)==24
    expected_graphite=_rgb("#3A3D42")
    assert all(f["rows"][role]["base_srgb_hex"]=="#3A3D42"
               and all(abs(x-y)<1e-10 for x,y in zip(converted[role],expected_graphite))
               for role in f["graphite_roles"])
    raw=path.read_bytes()
    if raw[:4]!=b"glTF":raise ValueError("not GLB")
    magic,version,total=struct.unpack_from("<III",raw)
    assert version==2 and total==len(raw)
    length,kind=struct.unpack_from("<II",raw,12)
    assert kind==0x4e4f534a
    data=json.loads(raw[20:20+length])
    tail=raw[20+length:]
    mats=data.setdefault("materials",[])
    cache={}
    changed=0
    emissive=0
    by_role={}
    nozzle_node=None
    for node in data["nodes"]:
        if "mesh" not in node:continue
        name=node["name"]
        assert name in source_mesh_extras
        if name=="dry:nozzle":
            assert nozzle_node is None
            nozzle_node=node
        role=role_for(name,source_mesh_extras[name],mode)
        mesh=data["meshes"][node["mesh"]]
        if role=="source_palette_preserved" or role not in f["rows"]:
            raise RuntimeError("STOP export: unapproved finish role "+role+" on "+name)
        row=_entry(f,role)
        kind_hot,color_hot,strength=_hot_state(name,mode)
        material_key=(role,kind_hot,strength)
        if material_key not in cache:
            # Hot diffuse stays 0.02 linear; all thermal colour is emissive.
            scale=float(row.get("linear_base_scale",1.0))
            base=([.02,.02,.02] if kind_hot else
                  [c*scale for c in converted[role]]) + [1.]
            if role in ("side_glazing","crown_pressure_ceramic","crown_outer_ceramic","aoi_optogel"):
                base[3]=.24 if role=="aoi_optogel" else .38
            pbr=dict(baseColorFactor=base,
                metallicFactor=float(row["metallic_factor"]),
                roughnessFactor=float(row["roughness_factor"]))
            mat=dict(name="CANON_FINISH/"+role+
                     ("/"+kind_hot if kind_hot else ""),
                     pbrMetallicRoughness=pbr,
                     doubleSided=(role in ("hotfin_torch_1750K","radiator_strakes")))
            if base[3]<1:
                mat["alphaMode"]="BLEND"
            if kind_hot:
                mat["emissiveFactor"]=color_hot
                mat["extensions"]={"KHR_materials_emissive_strength":
                                    {"emissiveStrength":strength}}
            else:mat["emissiveFactor"]=[0.,0.,0.]
            cache[material_key]=len(mats)
            mats.append(mat)
        mi=cache[material_key]
        mesh=data["meshes"][node["mesh"]]
        for prim in mesh["primitives"]:
            prim["material"]=mi
        ex=node.setdefault("extras",{})
        ex["finish_role"]=role
        if name=="dry:tank_shell_out":
            assert role=="midship_skin_bay_doors"
        if name=="dry:tank_shell_in":
            assert role=="tank_shell"
        ex["finish_status"]="CANON_FINISH"
        ex["pbr_material_index"]=mi
        ex["source_spectral_performance_unchanged"]=True
        if kind_hot:
            ex["thermal_emissive_state"]=kind_hot
            emissive+=1
        by_role[role]=by_role.get(role,0)+1
        changed+=1
    # Check every rendered finish material uses the source sRGB to linear
    # conversion; hot states deliberately use the neutral near-black base.
    verified_materials=0
    for mat in mats:
        label=mat.get("name","")
        if not label.startswith("CANON_FINISH/"):continue
        role=label.split("/")[1]
        if role=="source_palette_preserved":
            raise RuntimeError("STOP export: source_palette_preserved is not a finish")
        assert role in converted
        hot=any(v>0 for v in mat.get("emissiveFactor",[0,0,0]))
        expected=([.02,.02,.02] if hot else
                  [c*float(f["rows"][role].get("linear_base_scale",1.))
                   for c in converted[role]])
        actual=mat["pbrMetallicRoughness"]["baseColorFactor"][:3]
        if any(abs(x-y)>1e-7 for x,y in zip(actual,expected)):
            raise RuntimeError("STOP export: sRGB-to-linear check failed "+str((label,actual,expected)))
        verified_materials+=1
    assert nozzle_node is not None
    coil=_entry(f,"nozzle_coil_bands")
    coil_index=len(mats)
    mats.append(dict(name="CANON_FINISH/nozzle_coil_bands",
        pbrMetallicRoughness=dict(baseColorFactor=converted["nozzle_coil_bands"]+[1.],
            metallicFactor=float(coil["metallic_factor"]),
            roughnessFactor=float(coil["roughness_factor"])),
        emissiveFactor=[0.,0.,0.]))
    tail,coils=split_nozzle_rings(data,tail,nozzle_node,coil_index,
        f["nozzle_coil_band"]["stations_x_m"])
    tail,paint=N.apply(data,tail)
    verified_materials+=1+paint["panel_materials_added"]
    for mat in mats:
        ex=mat.get("extras",{})
        if "panel_tone_srgb_factor" not in ex:continue
        role=mat["name"].split("/")[1]
        tone=float(ex["panel_tone_srgb_factor"])
        if not .94<=tone<=1.06 or role not in f["rows"]:
            raise RuntimeError("STOP export: invalid NOSTROMO plate material")
        scale=float(f["rows"][role].get("linear_base_scale",1.0))
        expected=[N._tone_linear(c*scale,tone) for c in converted[role]]
        actual=mat["pbrMetallicRoughness"]["baseColorFactor"][:3]
        if any(abs(a-b)>1e-7 for a,b in zip(actual,expected)):
            raise RuntimeError("STOP export: NOSTROMO panel tone mismatch")
    assert verified_materials==sum(
        1 for mat in mats if mat.get("name","").startswith("CANON_FINISH/"))
    # Any mesh can be exposed by sectioning. No exported mesh node may rely
    # on default white or on an unnamed glTF material, including interior.
    mesh_nodes=[n for n in data["nodes"] if "mesh" in n]
    missing=[]
    for node in mesh_nodes:
        if (node.get("extras",{}).get("finish_status")!="CANON_FINISH"
                or node.get("extras",{}).get("finish_role") not in f["rows"]):
            missing.append(node.get("name"))
            continue
        for prim in data["meshes"][node["mesh"]]["primitives"]:
            idx=prim.get("material")
            if idx is None or not mats[idx].get("name","").startswith("CANON_FINISH/"):
                missing.append(node.get("name"))
                break
    if missing:
        raise RuntimeError("STOP export: visible mesh lacks CANON_FINISH material "+
                           str(missing[:20]))
    assert changed==len(mesh_nodes)
    if emissive:
        used=data.setdefault("extensionsUsed",[])
        if "KHR_materials_emissive_strength" not in used:
            used.append("KHR_materials_emissive_strength")
    output=json.dumps(data,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    output+=b" " *((-len(output))%4)
    binary=(struct.pack("<III",magic,2,12+8+len(output)+len(tail))+
            struct.pack("<II",len(output),kind)+output+tail)
    assert len(binary)%4==0
    path.write_bytes(binary)
    assert struct.unpack_from("<I",binary,8)[0]==len(binary)
    if mode=="stowed":assert emissive==0
    if mode=="metric_hard":assert emissive and all(
        not ("hotfin" in node["name"] and node.get("extras",{}).get("thermal_emissive_state"))
        for node in data["nodes"])
    if mode=="torch":assert emissive>0
    return dict(canon_finish="CANON_FINISH",
                exterior_pbr_meshes=changed,
                exterior_pbr_variants=len(cache),
                thermal_emissive_meshes=emissive,
                hot_fin_1300K_preview_removed=True,
                thermal_source_no_credit=True,
                by_finish_role=dict(sorted(by_role.items())),
                all_visible_meshes_CANON_FINISH=True,
                rendered_meshes_total=len(mesh_nodes),
                missing_visible_finish_meshes=missing,
                source_palette_preserved_meshes=0,
                explicit_finish_meshes=changed,
                pressure_vessel_finish="interior_pressure_structure",
                service_shield_finish="shadow_shield",
                bay_corner_finish="external_fixtures",
                pale_accent_linear_scale=.57,
                srgb_to_linear_declared_roles=len(converted),
                verified_linear_pbr_materials=verified_materials,
                graphite_linear_base_rgb=expected_graphite,
                thermal_glow_diffuse_base_linear_rgb=[.02,.02,.02],
                nozzle_coil_band_faces=coils,
                nostromo_paint=paint,
                raw_glb_sha256=hashlib.sha256(binary).hexdigest(),
                bytes=len(binary))
