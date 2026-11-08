#!/usr/bin/env python3
"""LOOM Wayfarer B-rep pilot. NON-GOVERNING, zero credit, pinned build123d==0.13.0.

Source grammar: loom-2226/loom-2226@ea50354 / wayfarer/lab/build_v05.py.
Geometry: sha256 274e94fb43cfe549a3d2087abbdff4d65499ce6f5055ad2d7ade790414fbaaf9.
Only seven declared kinds. No fabricated tank structure, geometry or pass assertions.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
import math
import sys
from pathlib import Path

from build123d import Axis, Color, Compound, Plane, Solid, Unit, export_step, export_gltf

HERE = Path(__file__).resolve().parent
SOURCE_HASH = "274e94fb43cfe549a3d2087abbdff4d65499ce6f5055ad2d7ade790414fbaaf9"
KINDS = ("sector", "cslot", "domecyl", "frustum", "box", "tube", "panel")
EPS = 1.0e-5
# No x,y,z inferred mass densities. All geometry in metres and B-rep volumes in m³.
def load_json(name):
    return json.loads((HERE / name).read_bytes())

def plane_x(x, y=0.0, z=0.0):
    return Plane(origin=(x,y,z), x_dir=(0,1,0), z_dir=(1,0,0))

def cyl(r, x0, x1, y=0.0, z=0.0, angle=360, rotate_deg=0):
    if r <= 0 or x1 <= x0: raise ValueError(f"degenerate cylinder {r} {x0} {x1}")
    out = Solid.make_cylinder(r, x1-x0, plane_x(x0,y,z), angle)
    if rotate_deg:
        out = out.rotate(Axis((0,y,z),(1,0,0)),rotate_deg)
    return out

def box(x0,x1,y0,y1,z0,z1):
    if min(x1-x0,y1-y0,z1-z0)<=0: raise ValueError("degenerate box")
    return Solid.make_box(x1-x0,y1-y0,z1-z0,Plane(origin=(x0,y0,z0)))

def sector(s):
    x0,x1,r0,r1,a0,a1=[s[k] for k in ("x0","x1","r0","r1","a0","a1")]
    span=min(360.0,a1-a0)
    if span<=0 or r1<=r0: raise ValueError("degenerate sector")
    out=cyl(r1,x0,x1,angle=span,rotate_deg=a0)
    if r0>0: out=out-cyl(r0,x0-EPS,x1+EPS)
    return out

def cslot(s):
    x0,x1,r0,r1,hw=[s[k] for k in ("x0","x1","r0","r1","hw")]
    out=cyl(r1,x0,x1)
    if r0>0: out=out-cyl(r0,x0-EPS,x1+EPS)
    # The source grammar removes |y|<hw in the +z half only.
    out=out-box(x0-EPS,x1+EPS,-hw,hw,0,r1+1)
    side=s.get("side",0)
    if side==1:out=out-box(x0-EPS,x1+EPS,-r1-1,0,-r1-1,r1+1)
    elif side==-1:out=out-box(x0-EPS,x1+EPS,0,r1+1,-r1-1,r1+1)
    elif side!=0:raise ValueError(f"unexpected side {side}")
    gd,gw=s.get("gd",0),s.get("gw",0)
    if gd>0 and gw>0:
        # The source removes tangential strips ONLY within the outer radial band.
        ring=cyl(r1+EPS,x0-EPS,x1+EPS)-cyl(r1-gd,x0-2*EPS,x1+2*EPS)
        for az in s.get("grooves",[]):
            strip=box(x0-2*EPS,x1+2*EPS,0,r1+1,-gw/2,gw/2).rotate(Axis.X,az)
            out=out-(ring & strip)
    for hy,hz,hr in s.get("holes",[]):
        out=out-cyl(hr,x0-EPS,x1+EPS,hy,hz)
    return out

def half_ellipsoid(xa,xb,xc,R):
    # A true B-rep half-ellipsoid: sphere latitudes [-90,0] about +X,
    # stretched in X about xb by the authored semi-axis length (xb-xa).
    if not (xa < xb and xc>xa and R>0):raise ValueError("bad dome")
    nose=Solid.make_sphere(R,plane_x(xb),angle1=-90,angle2=0)
    nose=nose.scale(((xb-xa)/R,1.0,1.0),about=(xb,0,0))
    if xc<xb-EPS:
        nose=nose & box(xa-1,xc+EPS,-R-1,R+1,-R-1,R+1)
        return nose
    if xc>xb+EPS:
        return nose.fuse(cyl(R,xb,xc))
    return nose

def domecyl(s):
    xa,xb,xc,R,t=[s[k] for k in ("xa","xb","xc","R","t")]
    out=half_ellipsoid(xa,xb,xc,R)
    if t>0:
        out=out-half_ellipsoid(xa+t,xb,xc,R-t)
    rin=s.get("rin",0)
    if rin>0:out=out-cyl(rin,xa-1,xc+1)
    for az,hw in s.get("gaps",[]):
        # Exact polar-wedge subtraction, not masked tessellation.
        out=out-cyl(R+1,xa-1,xc+1,angle=2*hw,rotate_deg=az-hw)
    if s.get("xs") is not None:
        out=out & box(s["xs"],xc+EPS,-R-1,R+1,-R-1,R+1)
    return out

def frustum(s):
    x0,x1,r0,r1,t=[s[k] for k in ("x0","x1","r0","r1","t")]
    out=Solid.make_cone(r0,r1,x1-x0,plane_x(x0))
    if t>0:out=out-Solid.make_cone(r0-t,r1-t,x1-x0+2*EPS,plane_x(x0-EPS))
    return out

def tube(s):
    p0,p1,r=s["p0"],s["p1"],s["r"]
    delta=tuple(b-a for a,b in zip(p0,p1))
    L=math.dist(p0,p1)
    if L<=0:raise ValueError("zero-length tube")
    guide=(1,0,0) if abs(delta[0]/L)<.8 else (0,1,0)
    return Solid.make_cylinder(r,L,Plane(origin=p0,x_dir=guide,z_dir=delta))

def panel(s):
    # x longitudinal, y radial, z tangential; rotate about ship x.
    x0,x1,a,r0,span,t=[s[k] for k in ("x0","x1","a","r0","span","t")]
    return box(x0,x1,r0,r0+span,-t/2,t/2).rotate(Axis.X,a)

def make(s):
    k=s["k"]
    if k=="sector":out=sector(s)
    elif k=="cslot":out=cslot(s)
    elif k=="domecyl":out=domecyl(s)
    elif k=="frustum":out=frustum(s)
    elif k=="box":out=box(*(s[n] for n in ("x0","x1","y0","y1","z0","z1")))
    elif k=="tube":out=tube(s)
    elif k=="panel":out=panel(s)
    else:raise ValueError(f"not a sourced shape kind: {k}")
    if s.get("offset_yz"):
        dy,dz=s["offset_yz"]
        out=out.translate((0,dy,dz))
    return out

def settled(s):
    if "settled_fraction" not in s:return s
    f=s["settled_fraction"]
    if not 0<f<=1:raise ValueError(f"invalid settled fraction {f}")
    out={k:v for k,v in s.items() if k!="settled_fraction"}
    out["x0"]=s["x1"]-f*(s["x1"]-s["x0"])
    return out

def bounds(s):
    b=s.bounding_box()
    return (b.min.X,b.max.X,b.min.Y,b.max.Y,b.min.Z,b.max.Z)

def bbox_intersection_upper(a,b):
    dims=(max(0.,min(a[1],b[1])-max(a[0],b[0])),
          max(0.,min(a[3],b[3])-max(a[2],b[2])),
          max(0.,min(a[5],b[5])-max(a[4],b[4])))
    return math.prod(dims)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def keyhash(obj):
    return sha(json.dumps(obj,sort_keys=True,separators=(",",":")).encode())

def make_g8(I,C,solid_lookup):
    S, Bay, X=I["shuttle"],I["bay"],C["G8"]
    rs=S["diameter_m"]/2
    cases=[]
    def record(n,v,th,kind):
        cases.append({"test":n,"measured_m":round(v,9),"threshold_m":th,"pass_source_proxy":v+1e-9>=th,"basis":kind})
    record("radial bore",Bay["bore_r_m"]-rs,X["radial_clearance_min_m"],"G8 source radial")
    record("forward axial",S["x_m"][0]-Bay["x_m"][0],X["axial_clearance_min_m"],"G8 source axial")
    record("aft axial",Bay["x_m"][1]-S["x_m"][1],X["axial_clearance_min_m"],"G8 source axial")
    obst=[("slot edge",Bay["slot_half_width_m"]),("open doors",Bay["slot_half_width_m"])]
    for it in I["longerons"]["items"]:
        if it["kind"]=="tube" and it["z_m"]>0:
            obst.append((f"sill longeron {it['name']}",abs(it["y_m"])-it["d_m"]/2))
    R=I["radiators"]
    g=I["tanks"]["groove"]
    for az in R["azimuths_deg"]:
        if math.sin(math.radians(az))<=0:continue
        ca,sa=math.cos(math.radians(az)),math.sin(math.radians(az))
        ys=[abs(along*ca-across*sa)
            for along in (R["root_r_m"]-g["depth_m"],R["root_r_m"],R["root_r_m"]+R["max_span_m"])
            for across in (-g["width_m"]/2,g["width_m"]/2)]
        obst.append((f"strake {az}",min(ys)))
    for name,y in obst:record("exit "+name,y-rs,X["path_clearance_min_m"],"G8 source swept +Z half-width")
    HF=I.get("hot_fins")
    if HF:
        worst=min(abs((HF["root_r_m"]+a)*math.cos(math.radians(az))
                      -sd*HF["stowed_stack_thickness_m"]/2*math.sin(math.radians(az)))
                  for az in HF["azimuths_deg"] if math.sin(math.radians(az))>0
                  for a in (0.,HF["pleat_m"],HF["pleat_m"]*HF["pleats"]) for sd in (-1,1))
        record("aft hot-fin corridor",worst-Bay["slot_half_width_m"],X["corridor_clearance_m"],"G8 source planar y-projection")
    # Distances between B-rep shuttle bounding envelope and actual authored near-bay dry solids.
    shuttle=cyl(rs,S["x_m"][0],S["x_m"][1])
    targets=["bay_liner","longeron_upper_starboard","longeron_upper_port",
             "door_starboard","door_port","strake_40","strake_140"]
    cad=[]
    for t in targets:
        if t in solid_lookup:
            try:
                gap=shuttle.distance_to(solid_lookup[t])
                cad.append({"shuttle_envelope_to":t,"BRep_gap_m":round(gap,9),
                            "note":"3D distance of cylindrical envelope in docked pose; NOT swept launch-path clearance"})
            except Exception as e:
                cad.append({"shuttle_envelope_to":t,"error":str(e)})
    return {"g8_source_criteria":X,"source_proxy_checks":cases,
            "min_source_proxy_margin_m":round(min(r["measured_m"]-r["threshold_m"] for r in cases),9),
            "all_source_proxy_checks_pass":all(r["pass_source_proxy"] for r in cases),
            "selected_3D_docked_BRep_gaps":cad,
            "qualification":"NOT full swept shuttle or integrated installed-fit qualification"}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True)
    parser.add_argument("--skip-exports",action="store_true")
    parser.add_argument("--clash-limit",type=int,default=0,help="debug only; zero=ALL pairs")
    args=parser.parse_args()
    out=Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    raw=(HERE/"geometry_base.json").read_bytes()
    actualsha=sha(raw)
    if actualsha!=SOURCE_HASH:
        raise RuntimeError(f"unpinned source hash {actualsha} != {SOURCE_HASH}")
    J=json.loads(raw)
    I,C=load_json("inputs_base.json"),load_json("criteria_base.json")
    dry,fluids=J["parts"],J["fluids_by_state"]["S1"]
    if len(dry)!=292:raise RuntimeError("expected 292 source dry parts")
    kinds=sorted(set(p["shape"]["k"] for p in dry))
    if kinds!=sorted(KINDS):raise RuntimeError(f"source kind coverage changed: {kinds}")
    print("SOURCE SHA",actualsha,"DRY",len(dry),"S1 fluids",len(fluids),flush=True)
    solids=[];by_id={};errors=[];source_volume_diffs=[]
    palette={"water":"#6ABAD7","structure":"#929CA5","habitat":"#6F8F9F",
             "equipment":"#D8B882","thermal":"#D57D55","power":"#C6C65D",
             "torch":"#DF5540"}
    def add(name,part,category):
        try:
            s=make(settled(part["shape"]))
            if not s.is_valid:
                raise ValueError("B-rep is invalid")
            v=float(s.volume)
            if not v>0:raise ValueError(f"nonpositive solid volume {v}")
            s.label=name
            color=palette.get(part.get("system",category),"#A6B1BC")
            s.color=Color(color)
            rec={"id":name,"source_id":part.get("id",name),"kind":part["shape"]["k"],
                 "group":category,"volume_m3":round(v,9),
                 "source_proxy_volume_m3":part.get("volume_m3")}
            rec["delta_vs_source_proxy_m3"]=(round(v-part["volume_m3"],9) if isinstance(part.get("volume_m3"),(float,int)) else None)
            solids.append((rec,s,bounds(s)))
            if category=="dry":by_id[part["id"]]=s
            source_volume_diffs.append(rec)
        except Exception as e:
            errors.append({"solid":name,"error":str(e)})
    for p in dry:add("dry:"+p["id"],p,"dry")
    for i,p in enumerate(fluids):add(f"S1:{p['id']}:{i:02d}",p,"S1_fluid")

    # Full-core cell boundaries are sourced as the four S1 fluid CSlot envelopes
    # BEFORE SettledWater fractions; no invented structural placement.
    cell_f=[p for p in fluids if p["id"].startswith("water_")]
    if len(cell_f)!=4:raise RuntimeError("four CSlot water cells missing")
    for p in cell_f:
        d={k:v for k,v in p.items()}
        d["shape"]=dict(p["shape"])
        d["shape"].pop("settled_fraction",None)
        # No source volume assertion is imported here: calculate from B-rep.
        d.pop("volume_m3",None)
        add("CORE_FULL:"+p["id"],d,"core_full_envelope")
    if errors:
        # Persist failures before raising, never silently omit any part.
        (out/"failure.json").write_text(json.dumps({"errors":errors,"solids_built":len(solids)},indent=2)+"\n")
        raise RuntimeError(f"{len(errors)} B-rep source part failures, see failure.json")
    if len(solids)!=292+len(fluids)+4:
        raise RuntimeError(f"incomplete solids: {len(solids)}")
    byname={r["id"]:s for r,s,_ in solids}
    cell_names=sorted(n for n in byname if n.startswith("CORE_FULL:"))
    gross=sum(float(byname[x].volume) for x in cell_names)
    structural_debit=J["tank_structure"]["displaced_m3"]
    net_capacity=gross-structural_debit
    source_net=J["tank_volume_m3"]
    print("CORE GROSS",gross,"DEBIT",structural_debit,"NET",net_capacity,flush=True)

    # Independent automatic B-rep intersection. All four cells tested, NOT a
    # constant, point sample, polygon or hand-coded known-overlap value.
    fuel=byname[next(n for n in byname if n.startswith("S1:house_fuel:"))]
    core_hits=[]
    for name in cell_names:
        intersection=fuel & byname[name]
        volume=float(intersection.volume) if intersection is not None else 0.
        core_hits.append({"cell":name,"intersected_BRep_m3":round(volume,9)})
    core_overlap=sum(h["intersected_BRep_m3"] for h in core_hits)
    print("AUTO CORE/FUEL OVERLAP",core_overlap,core_hits,flush=True)
    # Historical comparison is a reference only and is NOT used to calculate overlap.
    overlap_historical=64.386
    core_pass=abs(net_capacity-source_net)<=0.15
    fuel_pass=abs(core_overlap-overlap_historical)<=0.15
    g8=make_g8(I,C,by_id)

    # ALL solid pairs, with mathematically necessary AABB volume screening
    # before exact Open Cascade B-rep intersection. No special-case exclusions.
    hit=[];fail=[];tested=0;pairs=0;bounds_rejected=0
    count=len(solids)
    for i in range(count):
        ai,asi,abi=solids[i]
        for j in range(i+1,count):
            pairs+=1
            bj,bsj,bbj=solids[j]
            if bbox_intersection_upper(abi,bbj)<=0.01:
                bounds_rejected+=1;continue
            try:
                inter=asi & bsj
                volume=float(inter.volume) if inter is not None else 0.
                tested+=1
                if volume>0.01:
                    hit.append({"a":ai["id"],"b":bj["id"],"m3":round(volume,8)})
            except Exception as e:
                fail.append({"a":ai["id"],"b":bj["id"],"error":str(e)})
            if args.clash_limit>0 and tested>=args.clash_limit:
                break
        if args.clash_limit>0 and tested>=args.clash_limit:break
        if i%30==0:print("PAIR PROGRESS",i,"/",count,"TESTED",tested,"HITS",len(hit),flush=True)
    hit.sort(key=lambda x:(x["a"],x["b"]))
    scanned_all=(pairs==count*(count-1)//2 and not fail and args.clash_limit==0)
    success=bool(core_pass and fuel_pass and scanned_all and g8["all_source_proxy_checks_pass"])
    result={
        "header":"ALL bodies. ALL sponsors. 2026–2226.",
        "status":"NON-GOVERNING RESEARCH ONLY, NO CANON, NO QUALIFICATION, CREDIT ZERO",
        "source_geometry_sha256":actualsha,
        "input_hashes":{"inputs_base_sha256":sha((HERE/"inputs_base.json").read_bytes()),
                        "criteria_base_sha256":sha((HERE/"criteria_base.json").read_bytes())},
        "build123d_version":importlib.metadata.version("build123d"),
        "parts":{"source_dry":len(dry),"source_S1_fluids":len(fluids),
                 "full_core_envelopes_added_for_intersection":4,
                 "BRep_solid_count":len(solids),"kinds":kinds,
                 "note":"Features[] (window/node face markers) are not part solids; B-rep reproduces seven declared shape grammars, including cslot slot, groove, longeron holes and dome azimuth gaps."},
        "acceptance":{
            "A1_core_net":{"pass_numeric_source_reconciliation":core_pass,
                           "gross_four_BRep_cells_m3":round(gross,9),
                           "unlocated_source_internal_structure_displacement_m3":structural_debit,
                           "net_capacity_from_BRep_minus_source_structure_debit_m3":round(net_capacity,9),
                           "target_source_net_m3":source_net,
                           "tolerance_m3":0.15,
                           "physical_internal_structure_fit_qualified":False},
            "A2_automatic_fuel_overlap":{"pass":fuel_pass,
                "source_fuel_id":"S1:house_fuel",
                "computed_BRep_intersection_m3":round(core_overlap,9),
                "historical_reference_m3":overlap_historical,
                "tolerance_m3":0.15,
                "all_four_cell_intersections":core_hits,
                "formula":"sum BRep(fuel_proxy) COMMON BRep(full_core_cell_i) volumes; no constant used as result"},
            "A3_all_clashes":{"pass":scanned_all,"pairs_total":pairs,"pairs_expected":count*(count-1)//2,
                "aabb_rejected_pairs":bounds_rejected,"exact_BRep_intersection_pairs":tested,
                "hits_gt_0p01_m3":len(hit),"uncalculated_pairs":fail},
            "A4_G8":{"pass_source_criteria":g8["all_source_proxy_checks_pass"],
                "BRep_installed_fit_qualified":False},
            "all_requested_numeric_and_enumeration_checks_pass":success,
        },
        "g8":g8,
        "overlap_threshold_m3":0.01,
        "ALL_CLASH_HITS_GT_0p01_M3":hit,
        "source_vs_BRep_solid_volumes":source_volume_diffs,
        "known_limitations":[
            "Source net tank 321.620667 m3 deducts 5.870097m3 structural volume from gross CSlot; the original tank-structure record does not locate its web/baffle solids. Net is algebraic sourced debit, not a fabricated watertight installed structure.",
            "Fuel and water source shapes are mutually overlapping as-is; this detects clashes, does not repair source geometry.",
            "Source geometry parts are volume proxies, not pressure-joined engineered hardware. Features[] are source markers, not pre-cut window port/pressure closures; only holes defined in individual part shape specifications are physically cut.",
            "G8 scalar thresholds are checked on pinned source inputs and a small number of docked B-rep clearances, NOT an exhaustive dynamic shuttle swept-body clearance or material tolerance study.",
            "Each volume-intrusion hit is listed, even when intentional, such as a S1 fluid represented inside a corresponding dry container; no semantic excuses suppress collisions.",
            "No B-rep collisions can determine radiation/thermal/mass qualification, structural materials, dynamic motion, suitability for 2226 spacecraft or mass saving."
        ],
        "credit":{"mass_t":0,"dv_km_s":0,"G1_or_G8_qualified":False,
                  "source_main_changed":False,"frozen_152_153_155_changed":False}
    }
    report=out/"fit_report.json"
    report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("FULL CLASH SCAN",len(hit),"HITS /",tested,"BRep-tested/",pairs,"ALL PAIRS", "PASS",success,flush=True)
    if not args.skip_exports:
        output_solids=[(r,s) for r,s,b in solids if r["group"]!="core_full_envelope"]
        # Open Cascade XCAF color/presentation references can be generated in
        # non-repeatable order even when the geometry is identical. STEP is
        # engineering geometry: export without presentation colors, preserving
        # the original per-part shape names; restore colors only for viewer GLB.
        for r,s in output_solids:s.color=None
        print("EXPORT STEP (colorless geometry)",flush=True)
        export_step(Compound(children=[s for r,s in output_solids]),
                    out/"wayfarer.step",unit=Unit.M,timestamp="2026-11-07T00:00:00")
        for r,s in output_solids:
            s.color=Color(palette.get(
                next((p.get("system") for p in dry if p["id"]==r["source_id"]),r["group"]),
                "#A6B1BC"))
        print("EXPORT GLB (colored)",flush=True)
        export_gltf(Compound(children=[s for r,s in output_solids]),
                    out/"wayfarer.glb",unit=Unit.M,binary=True,
                    linear_deflection=0.025,angular_deflection=0.3)
    if not success:
        raise SystemExit("ACCEPTANCE FAIL / PARTIAL RESULTS (NO PASS CLAIM)")
    return 0

if __name__=="__main__":sys.exit(main())
