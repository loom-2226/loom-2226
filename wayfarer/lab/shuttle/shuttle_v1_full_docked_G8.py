#!/usr/bin/env python3
"""Shuttle v1 DOCKED viewer: individual OpenCascade solids and G8 fit.

Faithfully keeps the source viewer component positions and orientations.
The viewer provides zero-thickness hull/TPS surfaces: these are represented
by 0.1mm OCC *display* skins solely to make closed BReps. This does NOT
invent hardware thickness, structure, material or mass. No shape may be
shrunken, moved or omitted to make G8 pass (except already-approved nozzle
centre station 12.72 -> 12.70). Dormant/hidden animation-only exhaust,
ground plane, raised gear and opened ramp are not installed DOCKED shapes.
Full ship G8 swept egress and D9 are separately gated, NOT claimed here.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
from build123d import Axis, Plane, Solid, Wire
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"lab"))
from packing_phase1b import source_brep_pilot as P

VIEWER=ROOT/"render/shuttle/wayfarer_shuttle_v1_viewer.html"
GEOM=ROOT/"results/out/wayfarer_v05_geometry.json"
INPUT=ROOT/"config/wayfarer_v05_inputs.json"
CRITERIA=ROOT/"config/cert_criteria.json"
OUT=ROOT/"render/out/wayfarer_shuttle_v1_full_docked_G8.json"
EXPECTED="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
SKIN=0.0001 # numerical display skin only, not a hardware thickness

def source():
    text=VIEWER.read_text()
    required=[
        "const X=s=>6.4-s;",
        "const POD0=new THREE.Vector3(X(5.45),.08,0)",
        "ring.rotation.y=Math.PI/2;ring.position.x=X(12.70);ship.add(ring);",
        "new THREE.TorusGeometry(.78,.1,14,48)",
        "const STOW=[{yaw:Math.PI,z:.23,y:0},{yaw:Math.PI,z:-.23,y:0},{yaw:Math.PI,z:.23,y:-.09},{yaw:Math.PI,z:-.23,y:-.09}]",
        "const hullM=clipM(",
        "new THREE.BoxGeometry(5.6,.07,.42)",
        "const wheelG=new THREE.CylinderGeometry(.26,.26,.24,20);wheelG.rotateZ(Math.PI/2);",
        "const st={cut:false,kit:true,lbl:true,fig:false};",
    ]
    for snippet in required:
        assert snippet in text,("unreviewed viewer source change",snippet)
    raw=GEOM.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==EXPECTED
    g=json.loads(raw)
    inp=json.loads(INPUT.read_text())
    crit=json.loads(CRITERIA.read_text())["G8"]
    assert inp["bay"]["x_m"]==[18.25,32.05]
    assert inp["shuttle"]["x_m"]==[18.75,31.55]
    assert inp["shuttle"]["length_m"]==12.8
    assert abs(g["dry_t"]-868.1922552640087)<1e-8
    part=next(p for p in g["parts"] if p["id"]=="shuttle")
    assert abs(part["mass_t"]-30.732248081255836)<1e-8
    return text,g,inp,crit,part["mass_t"]

def bx(x0,x1,y0,y1,z0,z1):
    return P.box(x0,x1,y0,y1,z0,z1)
def cy(radius,s0,s1,y=0,z=0):
    return P.cyl(radius,18.75+s0,18.75+s1,y,z)
def cone_skin(s0,s1,r0,r1):
    plane=P.plane_x(18.75+s0)
    outer=Solid.make_cone(r0,r1,s1-s0,plane)
    inner=Solid.make_cone(max(0,r0-SKIN),max(0,r1-SKIN),s1-s0,plane)
    return outer-inner
def cyl_skin(s0,s1,r):
    outer=cy(r,s0,s1)
    inner=cy(r-SKIN,s0-0.00001,s1+0.00001)
    return outer-inner
def sector(s0,s1,r0,r1,a0,a1):
    return P.make(dict(k="sector",x0=18.75+s0,x1=18.75+s1,
                       r0=r0,r1=r1,a0=a0,a1=a1))
def cyl_y(r,y0,y1,x,z=0):
    return Solid.make_cylinder(r,y1-y0,Plane(origin=(x,y0,z),
        x_dir=(1,0,0),z_dir=(0,1,0)))
def cone_y(r0,r1,y0,y1,x,z=0):
    return Solid.make_cone(r0,r1,y1-y0,Plane(origin=(x,y0,z),
        x_dir=(1,0,0),z_dir=(0,1,0)))
def sphere(r,x,y,z):
    return Solid.make_sphere(r,Plane(origin=(x,y,z)))
def torus(r_major,r_minor,x,y,z,axis):
    if axis=="x":
        plane=P.plane_x(x,y,z)
    elif axis=="z":
        plane=Plane(origin=(x,y,z))
    else:raise ValueError(axis)
    return Solid.make_torus(r_major,r_minor,plane=plane)

def blade_airfoil(x0,x1,y,z):
    """Source 5.6m blade with real thin faceted section, same 0.07x0.42m limits."""
    assert abs((x1-x0)-5.6)<1e-9
    def section(x):
        yz=((y,z-.21),(y+.025,z-.13),(y+.035,z+.05),
            (y+.008,z+.21),(y-.028,z+.10),(y-.035,z-.08))
        return Wire.make_polygon([(x,yy,zz) for yy,zz in yz],close=True)
    shape=Solid.make_loft([section(x0),section(x1)],ruled=True)
    assert shape is not None and shape.is_valid and shape.volume>0
    return shape

def thin_skin_seam(shape,s,r,depth=None):
    """Optional face-only engraving inside the 0.1mm numerical display skin."""
    d=SKIN*.35 if depth is None else depth
    assert 0<d<SKIN and 0<s<12.8
    x=18.75+s
    outer=cy(r+.035,s-.020,s+.020)
    inner=cy(r-d,s-.025,s+.025)
    cutter=outer-inner
    cut=shape-cutter
    if cut is None or not cut.is_valid or float(cut.volume)<=0:
        raise RuntimeError("shuttle surface seam invalid "+str(s))
    return cut


def shuttle_surface_etch(name,original):
    """No silhouette change, only blind etch into the viewer's skin solids."""
    sh=original
    if name=="hull_mid_open_side":
        for s in (4.35,6.50):
            sh=thin_skin_seam(sh,s,1.9)
    elif name=="gullwing_door_closed":
        for s in (4.08,6.82):
            sh=thin_skin_seam(sh,s,1.9)
        # The existing independent door sector carries both side outlines.
        # Etch narrow adjacent angular border lines, without adding hardware.
        a0=math.degrees(math.pi/2-(-.75+1.62))
        a1=math.degrees(math.pi/2-(-.75))
        for az0,az1 in ((a0+.2,a0+1.0),(a1-1.0,a1-.2)):
            edge=sector(4.12,6.78,1.9-SKIN*.35,1.94,az0,az1)
            sh=sh-edge
            if sh is None or not sh.is_valid or sh.volume<=0:
                raise RuntimeError("shuttle door outline invalid")
    elif name=="hull_aft":
        for s in (7.8,9.6,11.4):
            sh=thin_skin_seam(sh,s,1.9)
    elif name=="belly_TPS_aft":
        # Separate, already-source-authored heat-shield skin; finish role
        # stays separate from hull via mesh metadata, PBR unapproved.
        for s in (5.0,7.2,9.5,11.6):
            sh=thin_skin_seam(sh,s,1.9-SKIN)
    elif name=="magnetic_nozzle_ring":
        # One circumferential coil/torus accent; only a blind cut.
        x=18.75+12.70
        outside=cy(.92,12.70-.014,12.70+.014)
        inside=cy(.865,12.70-.022,12.70+.022)
        tool=outside-inside
        sh=sh-tool
        if sh is None or not sh.is_valid or sh.volume<=0:
            raise RuntimeError("shuttle nozzle-ring band invalid")
    if sh is not original:
        a=original.bounding_box();b=sh.bounding_box()
        if any(abs(float(u)-float(v))>.05 for u,v in zip(
            (a.min.X,a.min.Y,a.min.Z,a.max.X,a.max.Y,a.max.Z),
            (b.min.X,b.min.Y,b.min.Z,b.max.X,b.max.Y,b.max.Z))):
            raise RuntimeError("STOP: shuttle engraving changed outer envelope "+name)
    return sh


def parts():
    d={}
    def add(name,obj):
        assert name not in d,name
        assert obj is not None and obj.is_valid and float(obj.volume)>0,(name,obj)
        obj=shuttle_surface_etch(name,obj)
        obj.label="shuttle_v1/"+name
        d[name]=obj
    # Profile source: LatheGeometry V2 radius/s from nose. Four exact
    # frustum spans; the visible TPS underside is a separate display skin.
    profile=[(0,0),(.05,.33),(.28,.55),(1.5,1.12),(4.0,1.9)]
    for i,((s0,r0),(s1,r1)) in enumerate(zip(profile,profile[1:])):
        hull=cone_skin(s0,s1,r0,r1)
        add("hull_nose_%02d"%i,hull)
        # Optional source TPS arc only, numerical skin enclosed in hull skin.
        if i:
            tps=cone_skin(s0,s1,max(0,r0-SKIN),max(0,r1-SKIN))
            tps=tps & sector(s0,s1,0,2.0,137.0,223.0)
            if tps is not None and tps.is_valid and tps.volume>0:
                add("belly_TPS_nose_%02d"%i,tps)
    # The circular 2.9m shell is open on one side; closed gull-wing door
    # occupies the exact missing angular sector (from authored DT0/DTL).
    DT0=-.75; DTL=1.62
    a0=math.degrees(math.pi/2-(DT0+DTL))
    a1=math.degrees(math.pi/2-DT0)
    add("hull_mid_open_side",sector(4.0,6.9,1.9-SKIN,1.9,a1,a0+360))
    add("gullwing_door_closed",sector(4.0,6.9,1.9-SKIN,1.9,a0,a1))
    # Source 5.6m stowed rotor blades occupy a recessed upper spine.
    # Remove only the numerical shuttle hull display skin above them,
    # not Wayfarer's pressure hull or booked spacecraft structure.
    aft_hull=cyl_skin(6.9,12.4,1.9)
    groove=P.box(18.75+7.2,18.75+12.4,1.64,2.2,-.55,.55)
    aft_hull=aft_hull-groove
    assert aft_hull is not None and aft_hull.is_valid and aft_hull.volume>0
    add("hull_aft",aft_hull)
    add("hull_tail",cone_skin(12.4,12.8,1.9,1.72))
    add("tail_cap",cy(1.72,12.8-SKIN,12.8))
    # TPS over the underside, source arc 1.5rad; no material/thermal credit.
    belly=sector(4.0,12.4,1.9-2*SKIN,1.9-SKIN,137.0,223.0)
    add("belly_TPS_aft",belly)
    # Fixed tank + tapered core torch (source THREE axial cylinder).
    add("water_tank",cy(1.55,7.1,10.2))
    add("torch_reactor",Solid.make_cone(1.0,.95,2.15,P.plane_x(18.75+10.3)))
    add("magnetic_nozzle_ring",torus(.78,.1,18.75+12.70,0,0,"x"))
    # DOCKED Venus kit source mesh visible; it has no independent
    # reassigned mass here. x is world positive aft from original nose.
    add("kit_reactor",bx(18.75+2.2,18.75+3.7,-.375,.675,-.55,.55))
    add("kit_exchanger",bx(18.75+2.475,18.75+3.625,.81,1.19,-.4,.4))
    duct=[(3.6,1.1,0),(4.6,1.52,0),(5.9,1.6,0),(6.8,1.6,0)]
    for i,(p0,p1) in enumerate(zip(duct,duct[1:])):
        add("kit_duct_%02d"%i,P.tube(dict(p0=(18.75+p0[0],p0[1],p0[2]),
                     p1=(18.75+p1[0],p1[1],p1[2]),r=.1)))
    add("kit_intake",bx(18.75+5.65,18.75+6.45,1.74,1.86,-.275,.275))
    # Mast is y-compressed only in docked renderer; radius is unchanged.
    add("kit_mast_stowed",cone_y(.18,.16,1.6,1.72,18.75+6.8))
    add("rotor_hub_stowed",cyl_y(.3,1.59,1.85,18.75+6.8))
    for i,(z,dy) in enumerate(((.23,0),(-.23,0),(.23,-.09),(-.23,-.09))):
        # Source: 5.6m x .07m x .42m blade, x-centre 3.2m, yaw Pi;
        # transforms to s = hub 6.8 + [.4,6.0].
        add("rotor_blade_stowed_%d"%i,blade_airfoil(
            18.75+7.2,18.75+12.8,1.72+dy,z))
        add("rotor_tip_hidden_%d"%i,sphere(.16,18.75+12.64,1.72+dy,z))
    # Source tips.visible=false in docked state; remove tips from the
    # assembled installed renderer model, retaining their geometry as
    # source-only accounting check. Their tips end flush at station 12.8.
    for i in range(4):d.pop("rotor_tip_hidden_%d"%i)
    # Pressurised rover pod and its physical attachments. Parent POD0 has
    # +0.08m y offset, INCLUDING wheels/chassis. Do not miss transform.
    x=18.75+5.45
    add("pod_pressure_sphere",sphere(1.25,x,.08,0))
    add("pod_window_disc",Solid.make_cylinder(.42,.001,
        Plane(origin=(x,.38,1.219),z_dir=(0,0,1),x_dir=(1,0,0))))
    add("pod_hatch_ring",torus(.48,.05,x,.38,1.22,"z"))
    add("pod_chassis",bx(x-.8,x+.8,-1.33,-1.17,-1.2,1.2))
    for i,wx in enumerate((-.7,.7)):
        for j,wz in enumerate((-.6,.6)):
            add("pod_wheel_%d_%d"%(i,j),cy(.26,5.45+wx-.12,5.45+wx+.12,
                                                -1.45,wz))
    add("pod_custody_capsule",bx(x-.19,x+.19,-1.16,-.84,.78,1.22))
    # Belly thrusters are visible in docked view. Bell exhaust plumes,
    # extended landing legs and ramp are animation/ground-only and hidden.
    for i,s in enumerate((3.4,10.0)):
        for j,z in enumerate((-.45,.45)):
            add("belly_nozzle_%d_%d"%(i,j),
                cone_y(.16,.10,-1.75,-1.65,18.75+s,z))
    return d

def main():
    _,g,inp,crit,shuttle_t=source()
    d=parts()
    bay=inp["bay"]
    s=inp["shuttle"]
    radial_limit=bay["bore_r_m"]-crit["radial_clearance_min_m"]
    allowed_aft=bay["x_m"][1]-crit["axial_clearance_min_m"]
    allowed_fore=bay["x_m"][0]+crit["axial_clearance_min_m"]
    assert abs(allowed_aft-s["x_m"][1])<1e-10
    assert abs(allowed_fore-s["x_m"][0])<1e-10
    # Exact OCC boolean radial envelope, not an AABB diagonal or polygon sample.
    bore=P.cyl(radial_limit,17.0,33.0)
    rows=[]
    fails=[]
    for name,shape in sorted(d.items()):
        b=shape.bounding_box()
        radial_escape=shape-bore
        v=float(radial_escape.volume) if radial_escape is not None else 0.0
        aft=float(b.max.X);fore=float(b.min.X)
        row=dict(part="shuttle_v1/"+name,
                 bbox_fore_x_m=round(fore,8),
                 bbox_aft_x_m=round(aft,8),
                 radial_limit_m=radial_limit,
                 radial_escape_BRep_volume_m3=round(v,10),
                 fore_clearance_m=round(fore-bay["x_m"][0],8),
                 aft_clearance_m=round(bay["x_m"][1]-aft,8),
                 pass_G8=(v<1e-9 and fore>=allowed_fore-1e-6
                         and aft<=allowed_aft+1e-6))
        rows.append(row)
        if not row["pass_G8"]:fails.append(row)
    result=dict(status="NEW_NON_RING_G8_STOP" if any(
        q["part"]!="shuttle_v1/magnetic_nozzle_ring" for q in fails)
        else ("RING_G8_STOP" if fails else "ASSEMBLED_DOCKED_ENVELOPE_G8_PASS"),
        scope="actual individual OCC BReps, installed DOCKED viewer envelope radial/axial only",
        docked_parts_count=len(d),
        source_viewer="wayfarer/render/shuttle/wayfarer_shuttle_v1_viewer.html",
        source_geometry_sha256=EXPECTED,
        booked_shuttle_mass_t=shuttle_t,
        source_dry_mass_t=g["dry_t"],source_mass_rebooking_t=0,
        permitted_nozzle_station=12.70,
        no_other_part_correction_allowed=True,
        G8_source_criteria=crit,
        failures=fails,parts=rows,
        G8_swept_lateral_exit="OPEN, not asserted by radial/axial envelope",
        docked_gear="source hidden at zero animated extension; physical stowed gear fit unqualified",
        visor_skin_thickness_m="0.0001 visualization BRep skin only, ZERO mass or hardware qualification",
        venus_kit="source viewer DOCKED kit visible; no additional mass credit",
        radiator_and_crown_states="not addressed by this isolated G8",
        whole_ship_D9="NOT RUN",
        full_ship_containment="NOT RUN")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2)+"\n")
    print("SHUTTLE_V1_FULL_DOCKED_OCC_G8",json.dumps(dict(status=result["status"],
        solids=len(d),failures=fails)),flush=True)
    if fails:
        raise SystemExit("STOP kT: real DOCKED shuttle G8 part failure(s) "+
            ", ".join(q["part"] for q in fails))
if __name__=="__main__":
    main()
