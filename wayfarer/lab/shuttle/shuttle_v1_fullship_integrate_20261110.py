#!/usr/bin/env python3
"""kT #486 successor: docked shuttle + existing hold doors; 3x2 Wayfarer.

Source-pinned canon-v2.5.3 installed OCC solids. Replaces dry:shuttle with
individual viewer-derived OCC solids, with no extra shuttle mass. Removes
withdrawn #483 exterior courier geometry, keeps existing internal drone
parts and moves three source-booked crawler stowage representations into
the accepted holds. Uses only existing 2.4x1.8m hold doors, no hull cuts.
D9 + containment before exporting six GLBs with every-mesh extras and
semantic parent hierarchy. No canon, hardware or flight qualification.
"""
from __future__ import annotations
import hashlib,json,math,struct,sys
from pathlib import Path
from collections import Counter
from build123d import Color,Compound,Unit,export_gltf

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"lab"))
from shuttle.shuttle_v1_full_docked_G8 import (parts as shuttle_parts,
    source as check_shuttle_source, P)
from crown_geom_v253 import (main as build_canon_v253,inside_pressure_hull_check)
from v253_extra import check_added_interior
from exterior_radiator_states_v254 import build as radiator_state,STATES,ANGLES
from exterior_integrate_v254 import provenance,glb_extras
from pbr_finish_v257 import assign_pbr
import d9_sharded as D

OUT=ROOT/"render/out"
PREFIX="wayfarer_shuttle_hold_fullship_88ce19fc"
LEDGER=ROOT/"config/courier_option_c_ledger_20261110.json"
EXPECTED="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
THRESH=.01

def ledger_read(g):
    a=json.loads(LEDGER.read_text())
    assert a["source_geometry_sha256"]==EXPECTED
    assert abs(a["source_courier_systems_allocation_t"]-
               next(p["mass_t"] for p in g["parts"] if p["id"]=="courier_systems"))<1e-8
    assert a["retained_hardware_t"]==5
    assert abs(sum(a["retained_hardware_split_t"].values())-5)<1e-10
    assert abs(a["returned_to_engineering_reserve_t"]-
               (a["source_courier_systems_allocation_t"]-5))<1e-8
    assert abs(a["effective_engineering_reserve_t"]-
               (a["source_engineering_reserve_t"]+
                a["returned_to_engineering_reserve_t"]))<1e-8
    assert abs(a["dry_t"]-g["dry_t"])<1e-8
    assert abs(a["source_booked_shuttle_t"]-
               next(p["mass_t"] for p in g["parts"] if p["id"]=="shuttle"))<1e-8
    return a

def hold_doors():
    # The accepted existing 2.4x1.8m az0/180 doors, face entirely
    # within current outer hull r<=4.5. CAD locations are illustrative:
    # no new hatch, aperture cutter, hull removal or mechanical fit claim.
    # 2t already included in retained Courier Option C allocation.
    d={}
    x0,x1=14.3,16.7
    for side,y0,y1 in (("starboard",4.29,4.30),
                       ("port",-4.30,-4.29)):
        name="dry:hold_existing_door_"+side
        s=P.box(x0,x1,y0,y1,-.9,.9)
        assert s.is_valid and s.volume>0
        s.label=name;s.color=Color("#A8AFB4")
        d[name]=s
    return d

def internal_crawler_stowage(model):
    # Source book: each ext_crawler_dock_i = 0.2t, previously drawn
    # outside hull. Place one stowed in starboard existing hold and two
    # in port hold. Preserve nominal source envelope dimensions
    # x=.8, radial thickness=.15, tangential width ~=.6m. These are
    # *stowed crawler/dock representations*, not launch mechanisms.
    places=((0,16.1,3.75,3.90),
            (1,14.0,-3.90,-3.75),
            (2,16.1,-3.90,-3.75))
    out={}
    for i,x,y0,y1 in places:
        name=f"dry:ext_crawler_dock_{i}"
        assert name in model
        st=P.box(x,x+.8,y0,y1,-.30,.30)
        assert st.is_valid and st.volume>0
        st.label=name;st.color=Color("#929AA2")
        out[name]=st
    return out

def special_source(name):
    if name.startswith("dry:shuttle_v1/"):
        return "shuttle"
    if name.startswith("dry:hold_existing_door_"):
        return "courier_systems"
    return None

def classify_booking_integrity(scan):
    # D9's original generic classifier cannot know that 41 individual
    # shuttle shapes share one already-booked dry:shuttle mass. Preserve
    # every intersection, reclassify ONLY within that exact allocation
    # from independent-mass conflict (d) to same-assembly overlap (c).
    # Other D9 classifications remain untouched; no volume waived.
    counts=Counter()
    for hit in scan["intersection_hits"]:
        a,b=hit["a"],hit["b"]
        sa,sb=special_source(a),special_source(b)
        if sa is not None and sa==sb:
            hit["original_classifier_category"]=hit["category"]
            hit["category"]="c"
            hit["why"]="identical physical mass booking "+sa+"; component internal intersections (reported)"
        counts[hit["category"]]+=1
    scan["category_counts"]=dict(counts)
    scan["category_d_count"]=counts["d"]
    scan["category_d_conflicts"]=sorted(
        (h for h in scan["intersection_hits"] if h["category"]=="d"),
        key=lambda h:-h["m3"])
    scan["source_booking_refinement"]="intra-shuttle intersection only; no other category-d suppressed"
    return scan

def hierarchy(name, systems):
    """Use the source mass ledger system, with explicit physical-role overrides.

    These are *scene parents*, not separate masses. Every dry mesh must resolve
    to an existing booked source ID or an explicitly named derived piece.
    """
    if name.startswith("dry:shuttle_v1/"):
        n=name.split("/",1)[1]
        if n.startswith(("pod_","pod")):return ("SHUTTLE","pod")
        if n.startswith(("kit_","rotor_")):return ("SHUTTLE","kit_and_rotor")
        if n.startswith(("magnetic_","torch_","water_")):return ("SHUTTLE","propulsion_and_water")
        return ("SHUTTLE","hull_and_interfaces")
    if name.startswith("dry:hold_") or name.startswith("dry:drone_") or name.startswith("dry:ext_crawler_dock"):
        return ("SERVICE","internal_holds")
    if name.startswith("dry:crown_") or name.startswith("dry:wws1_") or name.startswith("dry:window_") or name.startswith("dry:viewport_band"):
        return ("HABITAT","glazing_and_crown")
    if name.startswith(("dry:strake_","dry:hotfin_")):
        return ("EXTERIOR","radiators")
    if name.startswith("S1:"):return ("FLUIDS","loaded")
    if not name.startswith("dry:"):
        raise ValueError("unmapped scene node "+name)

    n=name[4:]
    booked="service_shield_band" if n.startswith("service_shield_band_") else n
    system=systems.get(booked)
    if system is None:
        raise ValueError("no mass-ledger system for dry mesh "+name)

    # Explicit physical role overrides where the ledger's accounting
    # system is broader than the scene category. Never alter its booking.
    if n=="armor" or booked=="service_shield_band":
        assert system=="habitat"
        return ("STRUCTURE","hull_armour")
    if n.startswith("floor_L"):
        assert system=="structure"
        return ("HABITAT",n.split("_",1)[1])
    if n=="node_mount_allowance":
        assert system=="structure"
        return ("EXTERIOR","nodes_crawler_points")

    if system=="structure":
        if n.startswith(("pressure_vessel","skin_","tank_shell_","bay_liner")):
            return ("STRUCTURE","hull_armour")
        if n.startswith(("frame_","longeron_","bay_corner_")):
            return ("STRUCTURE","frames_longerons")
        if n in ("aft_bulkhead","door_starboard","door_port","thrust_cone","d8_unlocated_doubler_allowance"):
            return ("STRUCTURE","bulkheads_interfaces")
    elif system=="propulsion":
        if n=="shield":return ("PROPULSION","shield")
        if n=="reactor":return ("PROPULSION","torch_reactor")
        if n=="nozzle":return ("PROPULSION","nozzle")
    elif system=="plant":
        return ("POWER","plant")
    elif system=="electrical":
        if n.startswith("house_reactor_"):return ("POWER","reactors")
        if n.startswith(("house_peak_store","house_energy_battery")):
            return ("POWER","energy_storage")
        if n.startswith(("house_fuel_tank_cap_","c_lite_dry")):
            return ("POWER","fuel_support")
        if n.startswith("electrical"):return ("POWER","electrical_distribution")
    elif system=="thermal":
        if n=="manifold":return ("POWER","thermal_management")
    elif system=="avionics":
        if n=="bow_sensors":return ("EXTERIOR","sensors_comms")
        if n=="core_racks":return ("POWER","avionics")
    elif system=="habitat":
        if n in ("command_terrace","navigator_platform") or n.startswith("i4_"):
            return ("HABITAT","L1")
        if n.startswith(("outfit_L","room_L")):
            deck=n.split("_",1)[1].split("-",1)[0]
            assert deck in ("L1","L2","L3","L4","L5")
            return ("HABITAT",deck)
        if n.startswith("hatch_L1L2"):return ("HABITAT","L1")
        if n.startswith(("hatch_L4L5","trunk_plug_L4L5","doors_L4-")) or n in ("shelter_backup","rescue_kit"):
            return ("HABITAT","L4")
        if n=="core_trunk":return ("HABITAT","shared_access")
    elif system=="rcs":
        return ("EXTERIOR","rcs")
    elif system=="external":
        if n.startswith(("ext_sensor_turret_","ext_rf_array_","ext_laser_terminal_","ext_star_tracker_","ext_docking_target_")):
            return ("EXTERIOR","sensors_comms")
        if n.startswith(("ext_crawler_point_","ext_grapple_fixture_","ext_eva_rail_")):
            return ("EXTERIOR","nodes_crawler_points")
        if n.startswith(("ext_service_port_","ext_vent_")):
            return ("EXTERIOR","service_interfaces")
    elif system=="service":
        if n.startswith("docking_camera_"):return ("EXTERIOR","sensors_comms")
        if n=="service_arm":return ("EXTERIOR","service_interfaces")
        if n=="docking_collar":return ("STRUCTURE","bulkheads_interfaces")
        if n.startswith("tunnel_"):return ("HABITAT","shared_access")
        if n=="crown_c_seven_spare_panes":return ("HABITAT","glazing_and_crown")
    raise ValueError("unmapped ledger system/part "+system+"/"+n)


def hierarchical_compound(ship, systems):
    groups={}
    for n,obj in ship.items():
        assert obj.label==n,(n,obj.label)
        groups.setdefault(hierarchy(n,systems),[]).append(obj)
    parents={}
    for (system,sub),parts in sorted(groups.items()):
        node=Compound(children=parts,label="subsystem:"+system+"/"+sub)
        parents.setdefault(system,[]).append(node)
    containers=[Compound(children=parts,label="system:"+sysname)
        for sysname,parts in sorted(parents.items())]
    assert not any(sysname in ("WAYFARER","OTHER") for sysname in parents)
    assert {"STRUCTURE","PROPULSION","POWER","HABITAT","EXTERIOR","SHUTTLE"} <= set(parents)
    assert len(parents.get("SHUTTLE",[]))==4
    return Compound(children=containers,label="LOOM_WAYFARER_v2_5_3")

def verify_hierarchy(path,metadata):
    raw=path.read_bytes()
    n,kind=struct.unpack_from("<II",raw,12)
    assert kind==0x4e4f534a
    doc=json.loads(raw[20:20+n])
    nodes=doc["nodes"]
    assert all("extras" in n for n in nodes)
    names={v.get("name") for v in nodes}
    assert any(n and n.startswith("system:") for n in names),sorted(names)[:40]
    assert any(n and n.startswith("subsystem:") for n in names)
    # Walk parent map, no cycles, for actual encoded GLB hierarchy.
    parent={}
    for i,node in enumerate(nodes):
        for ch in node.get("children",[]):
            assert ch not in parent,("multiple parents",ch)
            parent[ch]=i
    mesh_nodes=[(i,n) for i,n in enumerate(nodes) if "mesh" in n]
    assert len(mesh_nodes)==len(metadata)
    for i,n in mesh_nodes:
        chain=[]
        cursor=i
        while cursor in parent:
            cursor=parent[cursor]
            chain.append(nodes[cursor].get("name",""))
            assert len(chain)<20,(i,chain)
        for field in ("zone","deck","material","print_group","mass"):
            assert field in n["extras"] and n["extras"][field] is not None,(n["name"],field)
        assert n["extras"]["mass_basis"]=="source_booking_reference_nonadditive"
        assert n["extras"]["print_group"]==(n["extras"]["semantic_system"]+"/"+n["extras"]["semantic_subsystem"])
        group=n["extras"]["semantic_system"]
        sub=n["extras"]["semantic_subsystem"]
        assert (group,sub)==(metadata[n["name"]]["semantic_system"],
                             metadata[n["name"]]["semantic_subsystem"])
        assert "system:"+group in chain,(n["name"],chain)
        assert "subsystem:"+group+"/"+sub in chain,(n["name"],chain)
    assert set(n["name"] for _,n in mesh_nodes)==set(metadata)
    from collections import Counter
    by_system=dict(sorted(Counter(n["extras"]["semantic_system"] for _,n in mesh_nodes).items()))
    assert not any(n["extras"]["semantic_system"]=="WAYFARER" for _,n in mesh_nodes)
    return dict(meshes=len(mesh_nodes),
                dry_system_breakdown=by_system,
                semantic_systems=sum(v.startswith("system:") for v in names if v),
                semantic_subsystems=sum(v.startswith("subsystem:") for v in names if v),
                hierarchy_valid=True)


def metadata_for_mesh(name, geom_rows, fluid_rows, radiator_mapping, system, subsystem):
    """View/print discovery fields, never independently rebooked node mass.

    "mass" deliberately references the SOURCE allocation and is not additive
    across split solids. node_mass_rebooking_t remains zero on every mesh.
    """
    physical=name[4:] if name.startswith("dry:") else None
    allocation=radiator_mapping.get(name)
    if name.startswith("S1:"):
        allocation=name.split(":")[1]
    elif name.startswith("dry:shuttle_v1/"):
        allocation="shuttle"
    elif name.startswith("dry:hold_existing_door_"):
        allocation="courier_systems"
    elif physical is not None and physical in geom_rows:
        allocation=physical
    elif physical is not None:
        if physical.startswith(("window_","viewport_band_")) and "__" in physical:
            allocation=physical.split("__",1)[0]
        elif physical.startswith("service_shield_band_"):
            allocation="service_shield_band"
        elif physical.startswith("crown_spare_"):
            allocation="crown_c_seven_spare_panes"
        elif physical.startswith("crown_pane_"):
            allocation="crown_dome"
        elif physical=="crown_outer_pressure_dome":
            allocation="crown_dome"
        elif physical=="crown_inner_pressure_dome":
            allocation="crown_backup_pressure_dome"
        elif physical=="crown_aoi_cavity_envelope":
            allocation="crown_adaptive_optogel"
        elif physical in ("crown_osteon_brow_seat","crown_brow"):
            allocation="crown_c_outward_retainers"
        elif physical.startswith("crown_gore_"):
            allocation="crown_c_additional_strata_gore"
    src=geom_rows.get(allocation) or fluid_rows.get(allocation)
    if not src or not src.get("mat") or "mass_t" not in src:
        raise ValueError("source mass/material not resolvable for "+name+" => "+str(allocation))
    mass=float(src["mass_t"])
    if not math.isfinite(mass) or mass<0:
        raise ValueError("invalid source-booked mass for "+name)
    # Zone is the source allocation CENTROID bucket; not a claim that a
    # physically long part is wholly contained inside the bucket.
    x=float(src["centroid_m"][0])
    zone=("FORE" if x<14 else "MIDSHIP" if x<34.3 else "AFT")
    if system=="SHUTTLE":
        zone="DOCKED_SHUTTLE"
    if name.startswith("dry:hold_existing_door_"):
        zone="EXISTING_HOLD"
    import re
    deck="NON_DECK"
    match=re.search(r"(?:^|[_:/-])(L[1-5])(?:[_:/-]|$)",name)
    if match:
        deck=match.group(1)
    elif physical is not None and physical.startswith("i4_"):
        deck="L1"
    elif subsystem in ("L1","L2","L3","L4","L5"):
        deck=subsystem
    print_group=system+"/"+subsystem
    if not zone or not deck or not print_group:
        raise ValueError("incomplete zone/deck/print group "+name)
    return dict(zone=zone,deck=deck,material=src["mat"],
        print_group=print_group,mass=mass,
        mass_unit="t",mass_basis="source_booking_reference_nonadditive",
        source_mass_owner_id=allocation)


def evaluate(model,poses,g,cfg,criteria,original_containment,
             original_added_inside,new_parts,source_sha,detail_pass=None):
    assert source_sha==EXPECTED and len(model)==441
    assert original_containment["pass_containment"]
    assert original_added_inside["pass_containment"]
    _,gcheck,inp,g8,booked=check_shuttle_source()
    assert abs(gcheck["dry_t"]-g["dry_t"])<1e-9
    ledger=ledger_read(g)
    rows={q["id"]:q for q in g["parts"]}
    # Ledger's system field is the authority for hierarchy parent ownership.
    basis=json.loads((ROOT/"config/mass_basis.json").read_text())
    assert basis["geometry_sha256"]==EXPECTED
    systems={p["id"]:p["system"] for p in basis["parts"]}
    assert set(systems)==set(rows)
    assert all(systems[k]==v["system"] for k,v in rows.items())
    fluids={v["id"]:v for v in g["fluids_by_state"]["S1"]}
    shuttle=shuttle_parts()
    assert len(shuttle)==41 and "magnetic_nozzle_ring" in shuttle
    docked={}
    for name,shape in shuttle.items():
        label="dry:shuttle_v1/"+name
        shape.label=label;shape.color=Color("#8FA4B4")
        docked[label]=shape
    # Real source-geometry G8 checked for *every* ported OCC subpart.
    # Deliberately do not convert missing flight hardware into PASS.
    radial_limit=inp["bay"]["bore_r_m"]-g8["radial_clearance_min_m"]
    fore=inp["bay"]["x_m"][0]+g8["axial_clearance_min_m"]
    aft=inp["bay"]["x_m"][1]-g8["axial_clearance_min_m"]
    bore=P.cyl(radial_limit,17,33)
    G8=[]
    for n,s in docked.items():
        b=s.bounding_box()
        escaped=s-bore
        vol=0 if escaped is None else float(escaped.volume)
        if float(b.min.X)<fore-1e-6 or float(b.max.X)>aft+1e-6 or vol>1e-9:
            G8.append(dict(part=n,fore_x=float(b.min.X),aft_x=float(b.max.X),radial_escape_m3=vol))
    if G8:
        block=dict(status="G8_STOP_NEW_PART",new_failed_parts=G8)
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/(PREFIX+"_G8_blocker.json")).write_text(json.dumps(block,indent=2)+"\n")
        raise RuntimeError("STOP kT: new DOCKED G8 failure "+str(G8))
    assert "dry:shuttle" in model
    assert "dry:courier_systems" in model
    moved=internal_crawler_stowage(model)
    doors=hold_doors()
    replace_radiator={f"dry:{prefix}_{a}" for prefix in ("strake","hotfin","hotfin_root")
                      for a in ANGLES}
    replace_crawlers={f"dry:ext_crawler_dock_{i}" for i in range(3)}
    assert replace_radiator|replace_crawlers|{"dry:shuttle","dry:courier_systems"}<=set(model)
    # courier_systems is a source *allocation* sector, not an exterior solid,
    # per kT F2. Do not copy #483 bay_parts. No dry mass removed or added.
    gone=replace_radiator|replace_crawlers|{"dry:shuttle","dry:courier_systems"}
    base={n:s for n,s in model.items() if n not in gone}
    assert len(base)==441-len(gone)
    base.update(moved)
    base.update(doors)
    base.update(docked)
    assert all(f"dry:crown_spare_{j:02d}" in base for j in range(1,8))
    assert all(f"dry:drone_{j}" in base for j in range(4))
    assert not any(n.startswith("dry:bay_") and n not in model for n in base)
    print("SHUTTLE_41_SOURCE_SOLIDS_G8_PASS_COURIER_OPTION_C_APPLIED",len(base),flush=True)
    report=dict(status="SIX_STATE_D9_PENDING",
        canon_tag=("canon-v2.5.9" if detail_pass is not None else "canon-v2.5.3"),
        source_geometry_sha256=source_sha,
        source_dry_t=g["dry_t"],ECON_dv_km_s=ledger["econ_delta_v_km_s"],
        original_source_shuttle_t=booked,
        shuttle_true_solids_count=len(shuttle),
        exact_shuttle_ring_station_m=12.70,
        docked_radial_and_axial_G8="PASS actual OCC solids",
        swept_shuttle_egress_G8="OPEN; source no swept geometry hardware qualification",
        crew_and_vehicle_mission_G8="OPEN (hardware and door clearance)",
        courier_option_c_applied_ledger="wayfarer/config/courier_option_c_ledger_20261110.json",
        courier_retained_t=ledger["retained_hardware_t"],
        courier_returned_to_reserve_t=ledger["returned_to_engineering_reserve_t"],
        engineering_reserve_effective_t=ledger["effective_engineering_reserve_t"],
        dry_mass_change_t=ledger["dry_mass_delta_t"],
        no_extra_reserve_geometry=True,
        withdrawn_bay_483_not_drawn=True,
        existing_hold_door_aperture_m=[2.4,1.8],
        no_hull_cuts=True,
        crawler_stowage_by_hold={"starboard":[0],"port":[1,2]},
        drone_stowage_by_hold={"starboard":[0,2],"port":[1,3]},
        mars_drone_egress="OPEN",
        spare_panes_unchanged=True,
        all_six_state_D9_and_containment="PENDING",
        six_states={})
    OUT.mkdir(parents=True,exist_ok=True)
    any_d9=False
    for mode in STATES:
        radiator,mapping=radiator_state(g,cfg,mode)
        for name in sorted(radiator):
            if name.endswith(":folded_envelope"):
                # Source stowed stack; do not substitute the v2.5.3
                # installed hotfin's fully deployed membrane.
                assert mode in ("stowed","metric_hard")
                q=rows[mapping[name]]["shape"]
                assert (q["x0"],q["x1"],q["r0"],q["span"],q["t"])==(
                    34.3,53.3,4.75,2,.6)
                assert abs(float(radiator[name].volume)-22.8)<1e-7
            elif name.endswith((":stowed_stack",":root")):
                old="dry:"+mapping[name]
                assert old in replace_radiator
                radiator[name]=model[old]
            radiator[name].label=name
        if mode!="torch":
            for az in ANGLES:
                stack=radiator[f"dry:hotfin_{az}:folded_envelope"]
                for other in sorted(radiator):
                    if other.startswith(("dry:hotfin_root_","dry:strake_")):
                        cut=stack & radiator[other]
                        overlap=0 if cut is None else float(cut.volume)
                        if overlap>1e-8:
                            raise RuntimeError("STOP kT: folded stack intersects root/strake "+
                                str((mode,az,other,overlap)))
        assert not(set(radiator)&set(base))
        installed={**base,**radiator}
        if detail_pass is not None:
            installed=detail_pass(installed,rows,mode)
        cont=inside_pressure_hull_check(installed,rows)
        extra=check_added_interior(installed,g,new_parts)
        assert cont["pass_containment"] and extra["pass_containment"]
        mode_r={}
        for pose in ("stowed","closed"):
            ship={**installed,**poses[pose]}
            names=sorted(ship)
            n=len(names);np=n*(n-1)//2
            hit=classify_booking_integrity(D.pair_scan(ship,names,0,np,THRESH))
            dcount=hit["category_d_count"]
            ecount=len(hit["collision_errors"])
            any_d9|=bool(dcount or ecount)
            print("WAYFARER_SHUTTLE_HOLD_FULL_D9",mode,pose,
                json.dumps(dict(parts=n,pairs=np,category_d=dcount,
                boolean_errors=ecount,conflicts=hit["category_d_conflicts"][:8])),flush=True)
            mode_r[pose]=dict(part_count=n,pair_count=np,
                category_d_count=dcount,boolean_errors=ecount,
                category_counts=hit["category_counts"],
                category_d_conflicts=hit["category_d_conflicts"],
                collision_errors=hit["collision_errors"],
                pressure_containment_pass=cont["pass_containment"] and extra["pass_containment"],
                source_dry_mass_t=g["dry_t"],
                glb=None)
            if dcount or ecount:
                continue
            path=OUT/(PREFIX+"_"+mode+"_"+pose+".glb")
            export_gltf(hierarchical_compound(ship,systems),path,unit=Unit.M,
                        binary=True,linear_deflection=.05,angular_deflection=.3)
            meta={}
            for name in names:
                if name.startswith("dry:shuttle_v1/"):
                    e=dict(source_allocation_id="shuttle",
                        source_allocation_total_t=booked,
                        source_allocation_reused_by_multiple_geometry_nodes=True,
                        node_mass_rebooking_t=0,
                        epistemic_status="source-viewer DOCKED representative OCC solids, hardware OPEN")
                elif name.startswith("dry:hold_existing_door_"):
                    e=dict(source_allocation_id="courier_systems",
                        source_allocation_total_t=ledger["source_courier_systems_allocation_t"],
                        node_booked_suballocation_t=None,
                        node_mass_rebooking_t=0,
                        epistemic_status="existing 2.4x1.8m approved hold doors, no new cuts; door interface 2t allocation shared")
                elif name.startswith("dry:ext_crawler_dock_"):
                    e=provenance(name,rows,fluids,mapping)
                    e["source_allocation_repositioned"]="inside approved hold; source mass unchanged"
                else:
                    e=provenance(name,rows,fluids,mapping)
                if name.startswith("dry:crown_spare_"):
                    e["preserved_rack_x_m"]=[20,22.6]
                gp,sub=hierarchy(name,systems)
                required=metadata_for_mesh(name,rows,fluids,mapping,gp,sub)
                assert all(required.get(field) is not None for field in
                    ("zone","deck","material","print_group","mass")),(name,required)
                meta[name]=dict(canon_tag=("canon-v2.5.9" if detail_pass is not None else "canon-v2.5.3"),
                    geometry_revision=("kT exterior detail F3" if detail_pass is not None
                                       else "kT #486 shuttle/holds successor"),
                    node_id=name,semantic_system=gp,
                    semantic_subsystem=sub,
                    radiator_mode=mode,crown_gore_pose=pose,**e,**required)
            extras=glb_extras(path,meta)
            if detail_pass is not None:
                # kT CANON_FINISH: colour/roughness/metal/emissive are
                # GLB JSON-only edits after final six-state D9/containment.
                extras.update(assign_pbr(path,meta,mode))
            semantic=verify_hierarchy(path,meta)
            mode_r[pose].update(glb=str(path.relative_to(ROOT)),
                gltf_extras=extras,semantic_hierarchy=semantic)
        report["six_states"][mode]=mode_r
    report["all_six_state_D9_and_containment"]=(
        "PASS" if not any_d9 else "FAIL_RETAIN_EXISTING_RELEASE")
    report["status"]=("FULL_SHUTTLE_HOLD_3X2_D9_CONTAINMENT_EXTRAS_HIERARCHY_PASS"
                      if not any_d9 else "D9_FAIL_NO_RELEASE")
    (OUT/(PREFIX+"_report.json")).write_text(json.dumps(report,indent=2)+"\n")
    if any_d9:
        raise RuntimeError("D9 collision(s) remain; no old assets deleted, all scans recorded")
    assert len(report["six_states"])==3
    assert all(len(x)==2 for x in report["six_states"].values())
    print("WAYFARER_FULL_SHUTTLE_HOLD_SIX_STATE_RELEASE_CANDIDATE_PASS",flush=True)

if __name__=="__main__":
    build_canon_v253(on_model_ready=evaluate)
