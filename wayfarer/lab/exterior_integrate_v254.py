#!/usr/bin/env python3
"""Full-ship radiator states on fixed canon-v2.5.3 BReps.

One radiator configuration at a time, each with either crown-gore pose.
Source radiator solids are REPLACED, never added over identical booked
solids; source mass, CG, thermal/certification inputs stay untouched.
Every exported mesh node receives glTF extras, referring to source
allocations without counting a shared allocation once per pleat.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path
from build123d import Compound, Unit, export_gltf

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from crown_geom_v253 import main as build_canon_v253
from crown_geom_v253 import inside_pressure_hull_check
from v253_extra import check_added_interior
from exterior_radiator_states_v254 import build as radiator_state, STATES, ANGLES
import d9_sharded as D

OUT=ROOT/"render/out"
PREFIX="wayfarer_full_radiator_states_88ce19fc"
EXPECTED="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"

def provenance(name,rows,fluids,radiators):
    allocation=None
    if name in radiators:
        allocation=radiators[name]
    elif name.startswith("dry:"):
        candidate=name[4:]
        if candidate in rows:
            allocation=candidate
        elif candidate.startswith("service_shield_band_"):
            allocation="service_shield_band"
        elif candidate.startswith("crown_gore_"):
            allocation="crown_c_additional_strata_gore"
    elif name.startswith("S1:"):
        candidate=name.split(":")[1]
        if candidate in fluids:
            allocation=candidate
    src=rows.get(allocation) or fluids.get(allocation)
    return dict(
        source_allocation_id=allocation,
        source_allocation_total_t=None if src is None else src["mass_t"],
        source_allocation_reused_by_multiple_geometry_nodes=True,
        node_mass_rebooking_t=0,
        epistemic_status="full-size representation of booked hardware; hardware qualification unchanged"
    )

def glb_extras(path,expected):
    raw=path.read_bytes()
    assert len(raw)>=20 and raw[:4]==b"glTF"
    magic,version,total=struct.unpack_from("<III",raw)
    assert version==2 and total==len(raw)
    jlen,jkind=struct.unpack_from("<II",raw,12)
    assert jkind==0x4e4f534a
    data=json.loads(raw[20:20+jlen])
    tail=raw[20+jlen:]
    mesh_nodes=set()
    for index,node in enumerate(data["nodes"]):
        name=node.get("name","")
        if "mesh" in node:
            assert name in expected,("missing node provenance",index,name)
            assert name not in mesh_nodes,("duplicate mesh name",name)
            mesh_nodes.add(name)
            node["extras"]=expected[name]
        else:
            node["extras"]=dict(
                node_id=name or f"container_{index}",
                kind="scene_transform",
                canon_tag="canon-v2.5.3",
                source_mass_rebooking_t=0)
    assert mesh_nodes==set(expected),(len(mesh_nodes),len(expected),
                                      list(set(expected)-mesh_nodes)[:10])
    packed=json.dumps(data,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    packed+=b" " *((-len(packed))%4)
    result=(struct.pack("<III",magic,2,12+8+len(packed)+len(tail))+
            struct.pack("<II",len(packed),jkind)+packed+tail)
    assert len(result)%4==0
    path.write_bytes(result)
    check=path.read_bytes()
    assert struct.unpack_from("<I",check,8)[0]==len(check)
    return dict(mesh_nodes_with_extras=len(mesh_nodes),
                all_scene_nodes_with_extras=len(data["nodes"]),
                raw_glb_sha256=hashlib.sha256(check).hexdigest(),
                bytes=len(check))

def integrate(model,poses,g,cfg,criteria,original_containment,
              original_added_inside,new_parts,source_sha):
    assert source_sha==EXPECTED
    assert original_containment["pass_containment"]
    assert original_added_inside["pass_containment"]
    rows={r["id"]:r for r in g["parts"]}
    fluids={r["id"]:r for r in g["fluids_by_state"]["S1"]}
    replace_ids=set()
    for a in ANGLES:
        replace_ids|={f"dry:strake_{a}",f"dry:hotfin_{a}",f"dry:hotfin_root_{a}"}
    assert replace_ids<=set(model)
    # Original 12 solids are only omitted in the state overlays.
    base={name:shape for name,shape in model.items() if name not in replace_ids}
    assert len(model)==441 and len(base)==429,(len(model),len(base))
    OUT.mkdir(parents=True,exist_ok=True)
    result=dict(status="EXTERIOR_STEP1_INTEGRATED_D9_AND_CONTAINMENT",
        governing_canon_tag="canon-v2.5.3",
        governing_merge_commit="03479ea035a9207e3f7b91402ec387237b5c66e6",
        source_geometry_sha256=source_sha,
        v253_base_solids_before_replacement=len(model),
        replaced_source_radiator_ids=sorted(replace_ids),
        source_mass_ledger_changed_t=0,
        source_dry_mass_t=g["dry_t"],
        econ_dv_km_s=707.845,
        each_mode_mutually_exclusive=True,
        each_crown_pose_mutually_exclusive=True,
        no_print_only_edits=True,
        classifier="unmodified source_brep_triage.classify via d9_sharded.pair_scan",
        threshold_m3=criteria["D9"]["min_intersection_m3"],
        new_hardware_qualification="NONE; hinge/mast/fatigue/unresolved hardware OPEN",
        modes={})
    for mode in STATES:
        radiators,mapping=radiator_state(g,cfg,mode)
        # The standalone component BReps use raw source envelopes for
        # stowed stacks, folded fins and roots. The v2.5.3 installed-ship
        # BReps are already FITTED around service water, mounts and nozzle.
        # Reuse those exact installed solids rather than reopening D8
        # intersections or altering mass/position. Only new extended
        # pleats are constructed from the state drawings.
        fitted_originals=[]
        for name in sorted(radiators):
            if name.endswith((":stowed_stack",":folded_envelope",":root")):
                original_id="dry:"+mapping[name]
                assert original_id in replace_ids and original_id in model
                radiators[name]=model[original_id]
                radiators[name].label=name
                fitted_originals.append(dict(export_node=name,
                                             reused_v253_installed=original_id,
                                             unchanged_volume_m3=float(model[original_id].volume)))
        assert len(fitted_originals)==12 if mode=="stowed" else len(fitted_originals)==8
        assert not(set(base)&set(radiators))
        added={**base,**radiators}
        assert len(added)==429+len(radiators)
        # Per radiator state, re-run both relevant unary containment checks.
        cont=inside_pressure_hull_check(added,rows)
        extra=check_added_interior(added,g,new_parts)
        assert cont["pass_containment"] and extra["pass_containment"]
        mode_out=dict(radiator_components=len(radiators),
                      radiator_source_ids=sorted(set(mapping.values())),
                      replacing_exactly_12_original_solids=True,
                      reused_v253_installed_radiator_BReps=fitted_originals,
                      mass_credit_t=0,
                      containment=dict(physical_interior_count=cont["checked_physical_interior_count"],
                          escaped_physical_count=len(cont["escaped_parts"]),
                          new_habitat_interior_count=extra["checked_new_pressure_interior_count"],
                          new_habitat_outside_count=len(extra["escaped_new_pressure_interior"]),
                          band_pieces_within_service_hull=extra["checked_service_hull_count"],
                          band_escaped_m3=extra["service_hull_escaped_m3"],
                          pass_containment=True),
                      gores={})
        for gore_pose in ("stowed","closed"):
            ship={**added,**poses[gore_pose]}
            names=sorted(ship)
            n=len(names)
            n_pairs=n*(n-1)//2
            check=D.pair_scan(ship,names,0,n_pairs,criteria["D9"]["min_intersection_m3"])
            print("FULL_SHIP_D9",mode,gore_pose,json.dumps(dict(
                solids=n,pairs=n_pairs,d=check["category_d_count"],
                bool_errors=len(check["collision_errors"]),
                conflicts=check["category_d_conflicts"][:15])),flush=True)
            if check["category_d_count"] or check["collision_errors"]:
                # Reproducible blocker before ANY unqualified geometry export.
                failpath=OUT/(PREFIX+"_blocker.json")
                failpath.write_text(json.dumps(dict(
                    mode=mode,gore_pose=gore_pose,scan=check,
                    no_source_mass_or_position_changes=True),indent=2)+"\n")
                raise RuntimeError(f"full ship D9 HOLD {mode} {gore_pose}")
            path=OUT/(PREFIX+"_"+mode+"_"+gore_pose+".glb")
            export_gltf(Compound(children=list(ship.values())),path,unit=Unit.M,
                binary=True,linear_deflection=.05,angular_deflection=.3)
            metadata={}
            for name in names:
                e=provenance(name,rows,fluids,mapping)
                metadata[name]=dict(canon_tag="canon-v2.5.3",
                    geometry_revision="step1 radiator states",
                    node_id=name,radiator_mode=mode,crown_gore_pose=gore_pose,
                    **e)
            extras=glb_extras(path,metadata)
            mode_out["gores"][gore_pose]=dict(
                part_count=n,pair_count=n_pairs,
                category_d_count=check["category_d_count"],
                boolean_errors=len(check["collision_errors"]),
                category_counts=check["category_counts"],
                category_d_conflicts=check["category_d_conflicts"],
                containment_pass=True,
                glb=str(path.relative_to(ROOT)),
                gltf_extras=extras)
        result["modes"][mode]=mode_out
    assert set(result["modes"])==set(STATES)
    path=OUT/(PREFIX+"_report.json")
    path.write_text(json.dumps(result,indent=2)+"\n")
    print("FULL_SHIP_RADIATOR_3X2_D9_AND_CONTAINMENT_PASS",path,flush=True)

if __name__=="__main__":
    build_canon_v253(on_model_ready=integrate)
