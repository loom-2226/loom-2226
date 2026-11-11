#!/usr/bin/env python3
"""Wayfarer F3: retro-industrial exterior engraving, bounded by source BReps.

Every edited part is the ORIGINAL installed true solid MINUS blind pockets or
engraved lines. Zero added/raised solids, zero protrusion, zero rebooking.
This is visual/print-level engineering, not flight/sensor/thermal qualification.
Original six-state D9, containment, G8 and extras remain mandatory via the
#488 six-state integrator. No changes to crown panes or mass ledger.
"""
from __future__ import annotations
import json,math
from pathlib import Path
from collections import Counter
from build123d import Axis,Plane,Solid
from packing_phase1b import source_brep_pilot as P
from shuttle import shuttle_v1_fullship_integrate_20261110 as A
import hull_etch_finish_20261111 as E

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"render/out"
PREFIX="wayfarer_exterior_detail_88ce19fc"
MIN_PRINT_FEATURE_M=.10
records={}
samples={}
ALL_CLASSES=("rcs","sensor_turret","rf_tiles","laser_terminal",
    "star_tracker","bow_ring","docking_camera","grapple_fixture",
    "service_port","vent","docking_target","eva_rail","hold_door",
    "folded_fin","fin_root")

def group_of(name):
    k=name.removeprefix("dry:")
    if k.startswith("rcs_"):return "rcs"
    if k.startswith("ext_sensor_turret_"):return "sensor_turret"
    if k.startswith("ext_rf_array_"):return "rf_tiles"
    if k.startswith("ext_laser_terminal_"):return "laser_terminal"
    if k.startswith("ext_star_tracker_"):return "star_tracker"
    if k=="bow_sensors":return "bow_ring"
    if k.startswith("docking_camera_"):return "docking_camera"
    if k.startswith("ext_grapple_fixture_"):return "grapple_fixture"
    if k.startswith("ext_service_port_"):return "service_port"
    if k.startswith("ext_vent_"):return "vent"
    if k.startswith("ext_docking_target_"):return "docking_target"
    if k.startswith("ext_eva_rail_"):return "eva_rail"
    if k.startswith("hold_existing_door_"):return "hold_door"
    if k.startswith("hotfin_") and k.endswith(":folded_envelope"):return "folded_fin"
    if k.startswith("hotfin_root_") and k.endswith(":root"):return "fin_root"
    return None

def source_id(name,klass):
    n=name[4:].split(":")[0]
    if klass=="hold_door":return "courier_systems"
    return n

def bb(shape):
    b=shape.bounding_box()
    return (float(b.min.X),float(b.max.X),float(b.min.Y),float(b.max.Y),
            float(b.min.Z),float(b.max.Z))

def face(name,source,shape):
    """Outward-facing radial side, plus its tangent and source X span."""
    b=bb(shape);xc=(b[0]+b[1])/2
    cy=(b[2]+b[3])/2;cz=(b[4]+b[5])/2
    k=source["shape"].get("k")
    if name.startswith("dry:hold_existing_door_"):
        ny,nz=(1.,0.) if "starboard" in name else (-1.,0.)
        cy=b[3] if ny>0 else b[2]
    elif name.startswith("dry:rcs_"):
        side=name.split("rcs_",1)[1]
        if side.endswith("+Y"):ny,nz=1.,0.
        elif side.endswith("-Y"):ny,nz=-1.,0.
        elif side.endswith("+Z"):ny,nz=0.,1.
        else:ny,nz=0.,-1.
        cy=b[3] if ny>0 else b[2] if ny<0 else (b[2]+b[3])/2
        cz=b[5] if nz>0 else b[4] if nz<0 else (b[4]+b[5])/2
    elif name.startswith("dry:docking_camera_"):
        ny,nz=0.,-1.
        cz=b[4]
    elif k=="sector":
        q=source["shape"]
        a=math.radians((q["a0"]+q["a1"])/2)
        ny,nz=math.cos(a),math.sin(a)
        cy,cz=q["r1"]*ny,q["r1"]*nz
    else:
        raise ValueError("no exterior face direction "+name)
    ey,ez=nz,-ny    # y_dir of plane with world X as local x
    return (xc,cy,cz,ny,nz,ey,ez,b[0],b[1])

def round_engraving(F,x,offset_t,radius,depth):
    _,cy,cz,ny,nz,ey,ez,_,_=F
    origin=(x,cy+ey*offset_t-ny*depth,cz+ez*offset_t-nz*depth)
    return Solid.make_cylinder(radius,depth+.09,
        Plane(origin=origin,x_dir=(1,0,0),z_dir=(0,ny,nz)))

def panel_engraving(F,x_start,x_len,t_start,t_width,depth):
    _,cy,cz,ny,nz,ey,ez,_,_=F
    origin=(x_start,cy+ey*t_start-ny*depth,
            cz+ez*t_start-nz*depth)
    return Solid.make_box(x_len,t_width,depth+.09,
        Plane(origin=origin,x_dir=(1,0,0),z_dir=(0,ny,nz)))

def ring_engraving(F,x,offset_t,r_outer,r_inner,depth):
    if not 0<r_inner<r_outer:raise ValueError("bad annular engraving")
    return round_engraving(F,x,offset_t,r_outer,depth)-round_engraving(
        F,x,offset_t,r_inner,depth+.002)

def folded_stack_pleats(source):
    """Four compact 14-pleat source-stowed stacks, with visible engraved edges."""
    q=source["shape"]
    assert q["k"]=="panel"
    assert (q["x0"],q["x1"],q["r0"],q["span"],q["t"])==(34.3,53.3,4.75,2,.6)
    a=math.radians(q["a"])
    radial=(0,math.cos(a),math.sin(a))
    tangent=(0,-math.sin(a),math.cos(a))
    outer=q["r0"]+q["span"]
    cutters=[]
    for i in range(14):
        edge=-q["t"]/2+(i+.5)*q["t"]/14
        width=.012;depth=.030
        origin=(q["x0"]+.35,
                radial[1]*(outer-depth)+tangent[1]*(edge+width/2),
                radial[2]*(outer-depth)+tangent[2]*(edge+width/2))
        cutters.append(Solid.make_box(q["x1"]-q["x0"]-.70,width,depth+.010,
            Plane(origin=origin,x_dir=(1,0,0),z_dir=radial)))
    return cutters


def panel_pleats(source,root=False):
    if not root:
        return folded_stack_pleats(source)
    # Retain existing installed root-truss detail, unchanged.
    q=source["shape"]
    assert q["k"]=="panel"
    a=math.radians(q["a"])
    n=(0,math.cos(a),math.sin(a))
    t=(0,-math.sin(a),math.cos(a))
    start=q["x0"];stop=q["x1"]
    count=int((stop-start-1)/2.8)
    cutters=[]
    for i in range(count):
        x=start+1.2+i*2.8
        extent=45.0
        installed_t=q["t"]
        depth=min(.055,installed_t*.32)
        for side in (1,-1):
            direction=(0,side*t[1],side*t[2])
            offset_r=0.0 if side==1 else extent
            origin=(x,n[1]*offset_r+side*t[1]*(installed_t/2-depth),
                    n[2]*offset_r+side*t[2]*(installed_t/2-depth))
            cutters.append(Solid.make_box(.13,extent,depth+.012,
                Plane(origin=origin,x_dir=(1,0,0),z_dir=direction)))
    assert len(cutters)>=3
    return cutters

RCS_AFT_X=34.15
RCS_BELL_DIAMETER_M=.30   # 3mm at 1:100, above kT's 2mm floor

def source_bell_directions(azimuth_deg):
    """kT's source firing directions: one radial, two opposite tangential.
    The fourth axial bell retains the existing 10-degree outward cant.
    Directions are bell outward axes; torques use consistently signed
    equivalent thrust axes. Global sign does not change two-sided capacity.
    """
    a=math.radians(azimuth_deg)
    radial=(0.,round(math.cos(a),12),round(math.sin(a),12))
    tangent=(0.,-radial[2],radial[1])
    return [("RADIAL_OUT",radial),("TANGENT_PLUS",tangent),
            ("TANGENT_MINUS",(0.,-tangent[1],-tangent[2]))]


def rcs_authority_quick_screen():
    """Direction-based, zero-lateral-force paired-bell torque lower bound.

    The v2.5.6 scalar 3 x 25kN/cluster arm calculation did NOT represent
    the three distinct bell directions. This counts each real directional
    bell independently across both fore and aft rings, and demands
    balanced, oppositely directed fore/aft firing. Excludes the axial
    bell and gives no hardware/GNC/plume qualification.
    """
    g=json.loads((ROOT/"results/out/wayfarer_v05_geometry.json").read_text())
    inp=json.loads((ROOT/"config/wayfarer_v05_inputs.json").read_text())
    cfg=inp["rcs"]
    assert cfg["thruster_kn"]==25 and len(cfg["clusters"])==8
    assert all(c["thrusters"]==3 and c["axial"]["cant_out_deg"]==10
               for c in cfg["clusters"])
    assert 34.0<=RCS_AFT_X<34.3
    stations={}
    for c in cfg["clusters"]:
        cid=c["id"]
        az=c["theta_deg"]
        assert az in (0,90,180,270)
        assert c["x_m"]==(3 if cid.startswith("F") else 44)
        stations[cid]=dict(x=3. if cid.startswith("F") else RCS_AFT_X,
                           azimuth_deg=az,
                           bells=source_bell_directions(az))
    assert len([x for x in stations if x.startswith("F")])==4
    assert len([x for x in stations if x.startswith("A")])==4
    thrust=cfg["thruster_kn"]*1000.
    pitch_yaw_axes={"pitch":1,"yaw":2}
    def capacity(axis,sign,failed=None):
        fore=aft=0
        for cid,data in stations.items():
            if cid==failed:continue
            for _,vec in data["bells"]:
                component=vec[axis]
                if data["x"]==3 and component==-sign:
                    fore+=1
                elif data["x"]==RCS_AFT_X and component==sign:
                    aft+=1
        return min(fore,aft)*thrust*(RCS_AFT_X-3),fore,aft
    def worst(failed):
        cases={}
        for axis_name,index in pitch_yaw_axes.items():
            for sign in (-1,1):
                val,fore,aft=capacity(index,sign,failed)
                cases[axis_name+("_minus" if sign<0 else "_plus")]=dict(
                    torque_Nm=val,fore_bells=fore,aft_bells=aft)
        return cases
    nominal=worst(None)
    degraded={k:worst(k) for k in stations}
    nominal_min=min(x["torque_Nm"] for x in nominal.values())
    degraded_min=min(x["torque_Nm"] for c in degraded.values()
                     for x in c.values())
    ratio_nom=nominal_min/1_000_000
    ratio_out=degraded_min/750_000
    if min(ratio_nom,ratio_out)<1:
        raise RuntimeError("STOP kT: source-direction RCS pitch/yaw shortfall "+
                           str((ratio_nom,ratio_out)))
    return dict(aft_station_m=RCS_AFT_X,fore_station_m=3.,
        nominal_pitch_yaw_Nm=nominal_min,
        one_cluster_out_worst_Nm=degraded_min,
        nominal_required_Nm=1_000_000,degraded_required_Nm=750_000,
        nominal_ratio=ratio_nom,degraded_ratio=ratio_out,
        source_states_evaluated=len(g["states"]),
        radial_bells_per_cluster=1,tangential_bells_per_cluster=2,
        axial_bells_per_cluster=1,axial_cant_deg=10,
        source_direction_screen=True,zero_net_lateral_force=True,
        axial_bell_ignored_in_torque_screen=True,
        bell_direction_cases=nominal,
        one_cluster_out_cases=degraded,
        prior_v256_screen_did_not_use_source_directions=True,
        method="3 independently directed 25kN transverse bells per cluster; balanced fore/aft torque couple; no hardware/GNC/plume qualification")


def rcs_housing(name,old):
    """Same approved F1 housing and outer envelope; correct 3 bell axes."""
    side=name.split("rcs_",1)[1]
    aft=side.startswith("A")
    az={"+Y":0,"+Z":90,"-Y":180,"-Z":270}[side[-2:]]
    a=math.radians(az)
    ny,nz=math.cos(a),math.sin(a)
    ty,tz=-nz,ny
    station=RCS_AFT_X if aft else 3.0
    half_x=.14 if aft else .32
    housing=P.box(station-half_x,station+half_x,4.34,4.68,-.50,.50).rotate(Axis.X,az)
    nozzles=[]
    directions=source_bell_directions(az)
    # One outward radial bell; two opposite tangent bells are deliberately
    # planted on the outside face so their mouths remain visible.
    # Axial bell stays the v2.5.6 10-degree-out F1 geometry unchanged.
    specs=[(0.,(0.,ny,nz),.31),
           (-.10,(0.,-ty,-tz),.19),
           (+.10,(0.,ty,tz),.19)]
    for t,axis,length in specs:
        origin=(station,ny*(4.65 if t==0 else 4.72)+ty*t,
                nz*(4.65 if t==0 else 4.72)+tz*t)
        nozzles.append(Solid.make_cone(.105,RCS_BELL_DIAMETER_M/2,length,
            Plane(origin=origin,x_dir=(1,0,0),z_dir=axis)))
    sign=1 if aft else -1
    angle=math.radians(10)
    axial_axis=(sign*math.cos(angle),ny*math.sin(angle),nz*math.sin(angle))
    axial_base=(station+sign*.085,ny*4.48,nz*4.48)
    nozzles.append(Solid.make_cone(.105,RCS_BELL_DIAMETER_M/2,.33,
        Plane(origin=axial_base,x_dir=(0,ty,tz),z_dir=axial_axis)))
    detailed=housing.fuse(*nozzles)
    if detailed is None or not detailed.is_valid or detailed.volume<=0:
        raise RuntimeError("invalid source-direction F1 RCS solid "+name)
    detailed.label=name
    detailed.color=old.color
    spill=detailed-old
    extra=0 if spill is None else float(spill.volume)
    assert extra>0 and RCS_BELL_DIAMETER_M*10>=2
    return detailed,dict(source_volume_m3=float(old.volume),
        edited_volume_m3=float(detailed.volume),engraved_m3=0,
        external_added_m3=extra,same_source_envelope=False,
        F1_approved_housing_and_nozzles=True,
        bell_count=4,radial_bells=1,tangential_bells=2,
        axial_bells=1,axial_cant_deg=10,
        transverse_bell_axes=[dict(name=n,unit_axis=list(v))
                              for n,v in directions],
        bell_diameter_m=RCS_BELL_DIAMETER_M,
        print_bell_diameter_1_100_mm=RCS_BELL_DIAMETER_M*10,
        source_mass_rebooking_t=0,station_m=station,
        azimuth_deg=az,feature_tools=4)

def laser_source_cover(name,source):
    """Visible flush cover at exact source x33.3, no manifold/hull rework."""
    q=source["shape"]
    assert (q["x0"],q["x1"],q["r1"])==(33.05,33.55,4.515)
    spec=dict(q,r0=4.5005)
    shape=P.make(spec)
    assert shape is not None and shape.is_valid and shape.volume>0
    shape.label=name
    return shape

def cutters_for(name,klass,source,shape):
    if klass in ("folded_fin","fin_root"):
        return panel_pleats(source,root=(klass=="fin_root"))
    if klass=="bow_ring":
        # Existing source bow-sensor ring is internal to armour; four
        # small, blind face apertures never cut the pressure vessel.
        tools=[]
        for degrees in (0,90,180,270):
            a=math.radians(degrees);ny,nz=math.cos(a),math.sin(a)
            tools.append(Solid.make_cylinder(.075,.55,
                Plane(origin=(1.56,3.20*ny,3.20*nz),
                      x_dir=(1,0,0),z_dir=(0,ny,nz))))
        return tools
    F=face(name,source,shape)
    x=F[0];x0,x1=F[-2:]
    span=x1-x0
    k=source["shape"].get("k")
    radial_thick=source["shape"].get("r1",0)-source["shape"].get("r0",0) if k=="sector" else .8
    shallow=max(.002,min(.028,radial_thick*.27))
    tools=[]
    if klass=="rcs":
        raise RuntimeError("RCS F1 uses built true bells, not engraving cutters")
    elif klass=="sensor_turret":
        tools.extend((round_engraving(F,x,0,.135,.09),
                     ring_engraving(F,x,0,.26,.23,.012),
                     panel_engraving(F,x-.39,.18,-.32,.13,.012)))
    elif klass=="rf_tiles":
        # Flush, framed RF tiles; only engraved grid lines in 30mm source.
        for dx in (-.34,0.,.34):
            tools.append(panel_engraving(F,x+dx-.012,.024,-.34,.68,.007))
        for t in (-.18,.18):
            tools.append(panel_engraving(F,x-.56,1.12,t-.012,.024,.007))
    elif klass=="laser_terminal":
        # Recessed curved gimbal suggestion, not added dome outside
        # source exterior sector.
        tools.extend((round_engraving(F,x,0,.105,.004),
                     ring_engraving(F,x,0,.19,.166,.003)))
    elif klass=="star_tracker":
        # Baffle inside existing 0.08m-deep device, not a new tube.
        tools.extend((round_engraving(F,x,0,.056,.050),
                     ring_engraving(F,x,0,.087,.075,.009)))
    elif klass=="docking_camera":
        tools.extend((round_engraving(F,x,0,.053,.07),
                     ring_engraving(F,x,0,.080,.069,.015)))
    elif klass=="grapple_fixture":
        tools.extend((panel_engraving(F,x-.13,.26,-.115,.23,.011),
                     round_engraving(F,x,0,.060,.028)))
    elif klass=="service_port":
        tools.extend((round_engraving(F,x,0,.09,.012),
                     ring_engraving(F,x,0,.155,.14,.006)))
    elif klass=="vent":
        # A 0.12m part cannot carry a separate >=0.1m raised grille:
        # shallow below-threshold engraved slits only.
        for dx in (-.027,0.,.027):
            tools.append(panel_engraving(F,x+dx-.007,.014,-.023,.046,.005))
    elif klass=="docking_target":
        tools.extend((ring_engraving(F,x,0,.11,.09,.005),
                     round_engraving(F,x,0,.030,.005)))
    elif klass=="eva_rail":
        # Rail itself is <0.1m in transverse size; engrave bracket marks,
        # never invent raised 0.1m bolted supports outside its envelope.
        for xx in (x0+.36,x1-.36):
            tools.append(panel_engraving(F,xx-.052,.104,-.012,.024,.007))
    elif klass=="hold_door":
        # Existing 2.4x1.8m door is a 10mm sheet. Hatches/bolts are
        # ENGRAVINGS only, not 0.1m protruding hardware.
        tools.append(panel_engraving(F,x-.99,1.98,-.66,1.32,.003))
        for xx in (x-.86,x+.86):
            for t in (-.54,.54):
                tools.append(round_engraving(F,xx,t,.065,.004))
    else:
        raise ValueError("missing cutter style "+klass)
    assert tools
    return tools

def carve(old,tools,name):
    s=old
    before=float(old.volume)
    if not (old.is_valid and before>0):
        raise ValueError("invalid source BRep "+name)
    for cut in tools:
        s=s-cut
        if s is None or not s.is_valid or float(s.volume)<=0:
            raise RuntimeError("detail causes invalid/deleted part "+name)
    after=float(s.volume)
    removal=before-after
    if removal<=max(1e-10,before*1e-8):
        raise RuntimeError("detail did not engrave within source envelope "+name+
            " source_bbox="+str(bb(old))+
            " first_cut_bbox="+str(bb(tools[0])))
    a=bb(old);b=bb(s)
    if any(b[2*i]<a[2*i]-1e-6 or b[2*i+1]>a[2*i+1]+1e-6 for i in range(3)):
        raise RuntimeError("STOP kT F1: detail outside source bounding envelope "+name)
    # Difference from source is always an exact subset by construction.
    # A further OCC difference guards accidental BRep conversion defects.
    extra=s-old
    spill=0 if extra is None else float(extra.volume)
    if spill>1e-8:
        raise RuntimeError("STOP kT F1: added volume outside source "+name+" "+str(spill))
    s.label=name;s.color=old.color
    return s,dict(source_volume_m3=before,edited_volume_m3=after,
                  engraved_m3=removal,external_added_m3=spill,
                  same_source_envelope=True,feature_tools=len(tools))

def detail_ship(installed,rows,mode):
    updated=dict(installed)
    entries={};counts=Counter()
    for name in sorted(installed):
        klass=group_of(name)
        if klass is None:continue
        sid=source_id(name,klass)
        if sid not in rows:
            raise ValueError("detail without existing source booking "+name+" -> "+sid)
        original=installed[name]
        source=rows[sid]
        tools=None
        if klass=="rcs":
            detailed,evidence=rcs_housing(name,original)
        else:
            substrate=laser_source_cover(name,source) if klass=="laser_terminal" else original
            tools=cutters_for(name,klass,source,substrate)
            detailed,evidence=carve(substrate,tools,name)
            if klass=="laser_terminal":
                evidence["source_station_m"]=33.3
                evidence["source_flush_cover_only"]=True
        updated[name]=detailed
        entries[name]=dict(role=klass,source_allocation_id=sid,
                           booked_mass_t=source["mass_t"],**evidence)
        if klass=="folded_fin":
            assert len(tools)==14
            assert abs(evidence["source_volume_m3"]-22.8)<1e-7
            entries[name]["folded_stack"]=dict(pleats=14,folded_pleat_length_m=2,
                tangential_stack_thickness_m=.6,radial_root_m=4.75,
                radial_outer_m=6.75,x_range_m=[34.3,53.3],
                visible_edge_engravings=14)
        counts[klass]+=1
        if mode=="stowed" and name in (
            "dry:rcs_F+Y","dry:ext_sensor_turret_0",
            "dry:ext_rf_array_0","dry:hotfin_40:folded_envelope"):
            samples[name]=(original,detailed)
    # F1 permits housing recesses in the *unpressurised* mounting skin,
    # frame and manifold. Preserve the pressure vessel and source bookings.
    rcs_nodes=[updated[n] for n in sorted(entries) if entries[n]["role"]=="rcs"]
    host_recesses={}
    for host in ("dry:armor","dry:node_mount_allowance",
                 "dry:skin_aft","dry:frame_34","dry:manifold"):
        if host not in updated:continue
        h=updated[host]
        initial_volume=float(h.volume)
        for tool in rcs_nodes:
            cut=h & tool
            volume=0 if cut is None else float(cut.volume)
            if volume>1e-10:
                h=h-tool
                if h is None or not h.is_valid or h.volume<=0:
                    raise RuntimeError("invalid RCS housing recess "+host)
        if float(h.volume)<initial_volume-1e-9:
            h.label=host
            h.color=updated[host].color
            updated[host]=h
            host_recesses[host]=initial_volume-float(h.volume)
    # Source-derived hull/torch surface etch follows approved F1 RCS recesses.
    # Thin skins have 6mm blind display marks, never 30mm wall perforations.
    before_etch={n:updated[n] for n in (
        "dry:armor","dry:skin_service","dry:skin_aft",
        "dry:shield","dry:reactor","dry:nozzle") if n in updated}
    updated,etch_report=E.apply(updated,rows,mode)
    if mode=="stowed":
        for n,old in before_etch.items():
            samples[n]=(old,updated[n])
    expected=dict(rcs=8,sensor_turret=2,rf_tiles=4,laser_terminal=2,
        star_tracker=4,bow_ring=1,docking_camera=2,grapple_fixture=4,
        service_port=3,vent=4,docking_target=1,eva_rail=4,
        hold_door=2,folded_fin=0 if mode=="torch" else 4,fin_root=4)
    assert set(counts)=={k for k,v in expected.items() if v>0},(mode,dict(counts))
    assert all(counts[k]==v for k,v in expected.items()),(mode,dict(counts),expected)
    records[mode]=dict(edited_nodes=len(entries),by_role=dict(sorted(counts.items())),
        source_mass_rebooking_t=0,all_detail_subtractions=False,
        F1_approved_rcs_additions=8,
        RCS_recessed_host_volumes_m3=host_recesses,
        hull_and_torch_surface_etch=etch_report,
        source_envelope_violations=0,parts=entries)
    print("F3_EXTERIOR_DETAIL",mode,len(entries),json.dumps(dict(counts)),flush=True)
    return updated

def render_f3():
    """Source/modified BRep tessellation, orthographic paired CAD render."""
    import matplotlib
    matplotlib.use("Agg")
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    names=["dry:rcs_F+Y","dry:armor","dry:skin_service",
           "dry:skin_aft","dry:shield","dry:reactor","dry:nozzle",
           "dry:hotfin_40:folded_envelope"]
    assert all(n in samples for n in names),list(samples)
    fig=plt.figure(figsize=(15,24),facecolor="#141820")
    for row,name in enumerate(names):
        shapes=samples[name]
        bounds=[bb(v) for v in shapes]
        ext=[min(b[2*i] for b in bounds) for i in range(3)]
        top=[max(b[2*i+1] for b in bounds) for i in range(3)]
        mid=[(a+b)/2 for a,b in zip(ext,top)]
        radius=max((b-a)/2 for a,b in zip(ext,top)) * 1.3
        for col,obj in enumerate(shapes):
            ax=fig.add_subplot(len(names),2,row*2+col+1,projection="3d")
            vertices,faces=obj.tessellate(.035)
            verts=np.array([[v.X,v.Y,v.Z] for v in vertices])
            tris=np.array([[verts[k] for k in tri] for tri in faces])
            # Dense BRep tessellation; deliberately reduce display triangles
            # but never alter the exported CAD/GLB solids.
            if len(tris)>6000:tris=tris[::max(1,len(tris)//6000)]
            pc=Poly3DCollection(tris,linewidths=.04,
                    edgecolors="#4c5666",alpha=1)
            pc.set_facecolor("#81929b" if col==0 else "#adb6b3")
            ax.add_collection3d(pc)
            ax.set(xlim=(mid[0]-radius,mid[0]+radius),
                   ylim=(mid[1]-radius,mid[1]+radius),
                   zlim=(mid[2]-radius,mid[2]+radius))
            ax.view_init(elev=23,azim=-63)
            ax.set_proj_type("ortho")
            ax.set_axis_off()
            ax.set_title(name[4:]+("  SOURCE" if col==0 else "  ENGRAVED"),
                         color="white",size=10,pad=4)
    fig.suptitle("WAYFARER / SEAM + TORCH ETCH / SOURCE vs DRAWING DETAIL",
                 color="white",fontsize=17)
    fig.subplots_adjust(top=.96,bottom=.02,hspace=.08,wspace=.03)
    png=OUT/(PREFIX+"_F3_before_after.png")
    fig.savefig(png,dpi=160,facecolor=fig.get_facecolor())
    plt.close(fig)
    assert png.stat().st_size>5000
    return png.name

def main():
    A.PREFIX=PREFIX
    authority=rcs_authority_quick_screen()
    print("RCS_AUTHORITY_QUICK_SCREEN_PASS",json.dumps(authority),flush=True)
    # Viewer metadata only. Do not change source ledger, geometry, or
    # independently rebook the full 19.45037t courier allocation.
    retained=json.loads(A.LEDGER.read_text())
    held=retained["retained_hardware_split_t"]["hold_hardware_and_existing_door_interfaces"]
    assert held==2 and retained["retained_hardware_t"]==5
    door_display_share_t=held/2  # two equal nominal door/interface drawings
    base_metadata=A.metadata_for_mesh
    def f3_metadata(name,geom_rows,fluid_rows,radiator_mapping,system,subsystem):
        meta=base_metadata(name,geom_rows,fluid_rows,radiator_mapping,system,subsystem)
        if name.startswith("dry:docking_camera_"):
            assert meta["material"]=="rcs"
            meta["material"]="sensor"
            meta["material_override"]="viewer semantics only; source ledger unchanged"
        elif name.startswith("dry:shuttle_v1/belly_TPS_"):
            # Role only. Physical pigment/coating/PBR still requires kT approval.
            meta["surface_finish_role"]="shuttle_belly_heat_shield"
            meta["PBR_finish_status"]="OPEN"
        elif name.startswith("dry:shuttle_v1/hull_"):
            meta["surface_finish_role"]="shuttle_hull"
            meta["PBR_finish_status"]="OPEN"
        elif name.startswith("dry:hold_existing_door_"):
            assert meta["source_mass_owner_id"]=="courier_systems"
            assert abs(meta["mass"]-retained["source_courier_systems_allocation_t"])<1e-8
            meta["mass"]=door_display_share_t
            meta["mass_display_scope"]="equal display share of the existing 2t hold-hardware/door-interface allowance; not a separately measured physical door mass"
            meta["source_parent_booking_t"]=retained["source_courier_systems_allocation_t"]
            meta["mass_rebooking_t"]=0
        return meta
    A.metadata_for_mesh=f3_metadata
    def integrate(*args):
        A.evaluate(*args,detail_pass=detail_ship)
    A.build_canon_v253(on_model_ready=integrate)
    p=OUT/(PREFIX+"_report.json")
    rpt=json.loads(p.read_text())
    assert rpt["status"]=="FULL_SHUTTLE_HOLD_3X2_D9_CONTAINMENT_EXTRAS_HIERARCHY_PASS"
    assert rpt["all_six_state_D9_and_containment"]=="PASS"
    assert set(records)=={"stowed","metric_hard","torch"}
    f3=render_f3()
    rpt.update(status="F3_EXTERIOR_DETAIL_SIX_STATE_D9_CONTAINMENT_PASS",
        exterior_detail=dict(style="retro-industrial; kT F1 approved proud RCS bells + source-position lasers + engraved remainder",
         RCS_pitch_yaw_authority_quick_screen=authority,
         RCS_F1_approved=True,
         laser_terminals_source_station_m=33.3,
         shuttle_spine_groove=True,
         hull_surface_seam_scheme="hull_seam_scheme_2026_11_09",
         hull_seam_width_m=.05,visual_seam_depth_m=.03,
         thin_shell_actual_blind_mark_m=.006,
         PBR_finish_gate="CANON_FINISH kT 2026-11-11; material JSON in six GLBs",
         thermal_trade_dark_midship_over_water_tanks="Prefer low-visible-absorptance graphite; no new thermal credit",
         strake_1300K_glow_state="strakes Metric 2m and Torch 4m",
         hotfin_1750K_glow_state="hot fins Torch deployed only; root brightest",
         graphite_srgb_2026_11_11_v258="#3A3D42",
         hot_state_diffuse_linear_rgb=[.02,.02,.02],
         nozzle_coil_band_width_m=.15,nozzle_coil_band_depth_m=.03,
         nozzle_coil_band_finish="CANON_FINISH/nozzle_coil_bands",
         pressure_vessel_visible_finish="CANON_FINISH/interior_pressure_structure",
         service_shield_band_finish="CANON_FINISH/shadow_shield",
         bay_corner_finish="CANON_FINISH/external_fixtures",
         nozzle_coil_ring_boundary="unchanged v2.5.8 nozzle triangle classification; exact ring edges deferred to v2.5.10",
         all_rendered_nodes_require_CANON_FINISH=True,
         pale_accent_linear_rgb_scale=.8,
        print_minimum_modelled_feature_m=MIN_PRINT_FEATURE_M,
        smaller_marks="ENGRAVINGS not raised printable solids",
        no_hull_protrusion=False,no_crown_change=True,no_performance_claims=True,
         no_pressure_vessel_cuts=True,
        no_new_source_mass=True,
        source_canon="canon-v2.5.8",
        metadata_only_fixes=dict(docking_camera_material="sensor",
            hold_door_display_share_t=door_display_share_t,
            hold_hardware_and_door_interface_allowance_t=held,
            courier_parent_booking_unchanged_t=retained["source_courier_systems_allocation_t"],
            no_rebooking=True),
        modes=records),
        F3_before_after_png="render/out/"+f3,
        no_hull_cuts=False,
        shuttle_hull_spine_groove_cut=True)
    p.write_text(json.dumps(rpt,indent=2)+"\n")
    print("F3_EXTERIOR_SIX_STATE_PASS",f3,flush=True)

if __name__=="__main__":
    main()
