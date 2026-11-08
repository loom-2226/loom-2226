#!/usr/bin/env python3
"""kT 2026-11-08 crown decision: source-dimension BRep feasibility, never a canon promotion.

Source geometry and masses are read-only. Existing crown no_render allocations
are replaced IN THE EXPORTED CAD/VIEWER ASSET, not silently rebooked in G1.
Failure to close a physical detail or an intersection is an explicit HOLD.
"""
import hashlib
import json
import math
import struct
import sys
from pathlib import Path
from build123d import Color, Compound, Solid, Wire, Unit, export_gltf, export_stl
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from packing_phase1b import source_brep_pilot as P
import d9_sharded as D

EXPECTED = "88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
GEO = ROOT / "results/out/wayfarer_v05_geometry.json"
INPUT = ROOT / "config/wayfarer_v05_inputs.json"
OUT = ROOT / "render/out"
PREFIX = "wayfarer_crown_parts_88ce19fc"

def make_pane(r0, r1, theta0, theta1, thick, slope, center=False):
    """Closed, separately removable solid, external surface dimension from Option C."""
    def x_at(r):
        return -1.2 + max(0, r-2.0)*slope
    if center:
        outer = [(x_at(.75), .75*math.cos(2*math.pi*i/12),
                  .75*math.sin(2*math.pi*i/12)) for i in range(12)]
        inner = [(x+thick,y,z) for x,y,z in outer]
    else:
        a0,a1=math.radians(theta0),math.radians(theta1)
        outer=[(x_at(r0),r0*math.cos(a0),r0*math.sin(a0)),
               (x_at(r1),r1*math.cos(a0),r1*math.sin(a0)),
               (x_at(r1),r1*math.cos(a1),r1*math.sin(a1)),
               (x_at(r0),r0*math.cos(a1),r0*math.sin(a1))]
        beta=slope if r0>=2-1e-8 else 0.
        a=(a0+a1)/2
        norm=math.sqrt(1+beta*beta)
        shift=(thick/norm,-thick*beta*math.cos(a)/norm,
               -thick*beta*math.sin(a)/norm)
        inner=[tuple(p[i]+shift[i] for i in range(3)) for p in outer]
    sh=Solid.make_loft([Wire.make_polygon(outer, close=True),
                        Wire.make_polygon(inner, close=True)], ruled=True)
    assert sh.is_valid and sh.volume>0
    return sh

def domes_and_aoi(c):
    opt=c["shell_option_c"]["deep_pressure_domes"]
    ao=c["adaptive_optogel"]
    base=opt["parent_base_x_m"]
    R=opt["parent_radius_m"]
    rad=c["r_m"]
    thick=ao["primary_dome_thickness_m"]
    assert abs(thick-.028)<1e-10 and abs(ao["backup_dome_thickness_m"]-thick)<1e-10
    assert abs(opt["backup_apex_x_m"]+0.42)<1e-8 and abs(opt["primary_apex_x_m"]+.30)<1e-8
    # Geometry positions remain CANON. kT's outside-in terminology is used in viewer:
    # x=-0.42 is physically OUTER, originally labelled backup in v2.5;
    # x=-0.30 is physically INNER, originally labelled primary in v2.5.
    lim=P.cyl(rad,-1.5,base+0.5)
    def shell(apex):
        return P.domecyl(dict(k="domecyl",xa=apex,xb=base,xc=base,R=R,t=thick)) & lim
    outer=shell(opt["backup_apex_x_m"])
    inner=shell(opt["primary_apex_x_m"])
    # A physically bounded gel CAVITY envelope, not proof the authored 3.023m3
    # fill volume is independently closed. Check against actual source allocation.
    cavity=(P.half_ellipsoid(opt["backup_apex_x_m"]+thick,base,base,R-thick) -
            P.half_ellipsoid(opt["primary_apex_x_m"],base,base,R)) & lim
    for s in (outer,inner,cavity):
        assert s is not None and s.is_valid and s.volume>0
    return outer,inner,cavity

def glb_names(path):
    data=path.read_bytes()
    magic,version,total=struct.unpack_from("<III",data)
    assert magic==0x46546c67 and version==2 and total==len(data)
    n,kind=struct.unpack_from("<II",data,12)
    assert kind==0x4e4f534a
    doc=json.loads(data[20:20+n])
    return [v.get("name","") for v in doc["nodes"] if "mesh" in v]

def main():
    raw=GEO.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    assert sha==EXPECTED
    g=json.loads(raw)
    cfg=json.loads(INPUT.read_text())
    crown=cfg["habitat"]["decks"][0]["command_layout"]["crown_dome"]
    spec=crown["shell_option_c"]
    tile=spec["outer_tile_layer"]
    assert tile["type_counts"]==[1,12,12,12] and tile["radii_m"]==[0,.75,2,2.75,3.5]
    assert tile["thickness_m"]==.01 and spec["slope_deg"]==50
    assert abs(spec["nose_tip_x_m"]+1.2)<1e-12
    bodies={}
    radius=tile["radii_m"]
    step=360/12
    for j in range(37):
        name=f"dry:crown_pane_{j+1:02d}"
        if j==0:
            sh=make_pane(0,radius[1],0,360,.01,math.tan(math.radians(50)),center=True)
        else:
            k=j-1
            band=1+k//12
            az=k%12
            stagger=math.degrees(tile["stagger_last_band_rad"]) if band==3 else 0
            sh=make_pane(radius[band],radius[band+1],
                         az*step+stagger,(az+1)*step+stagger,
                         tile["thickness_m"],math.tan(math.radians(50)))
        sh.label=name
        sh.color=Color("#B6D8D9")
        bodies[name]=sh
    a,b,gel=domes_and_aoi(crown)
    for name,sh,color in (
      ("dry:crown_outer_pressure_dome",a,"#88AFB8"),
      ("dry:crown_inner_backup_pressure_dome",b,"#93C4CC"),
      ("dry:crown_aoi_cavity_envelope",gel,"#52B6B0"),
    ):
        sh.label=name;sh.color=Color(color);bodies[name]=sh
    assert len(bodies)==40
    # Clash screen against the existing source solids WITHOUT cutting them.
    targets={k:P.make(next(p["shape"] for p in g["parts"] if p["id"]==k))
             for k in ("bow_sensors","pressure_vessel","armor")}
    contacts=[]
    for name,part in bodies.items():
        b0=P.bounds(part)
        for t,ob in targets.items():
            b1=P.bounds(ob)
            upper=math.prod(max(0,min(b0[2*i+1],b1[2*i+1])-max(b0[2*i],b1[2*i])) for i in range(3))
            if upper<=0:continue
            try:
                common=part & ob
                vol=0 if common is None else float(common.volume)
                contacts.append(dict(part=name,against="dry:"+t,common_m3=vol,
                                     exceeds_D9_0p01m3=vol>.01))
            except Exception as exc:
                contacts.append(dict(part=name,against="dry:"+t,error=repr(exc),
                                     exceeds_D9_0p01m3=None))
    # Export existing 194 installed solids untouched plus the 40 true crown solids.
    G,I,C,R,rebuilt,gsha,step_sha=D.context()
    rows,shapes,installed,factor=D.imported(G)
    assert len(installed)==194 and len(set(rows)-set(installed))==122
    water_ratio=I["states"]["S1"]["remass_t"]/R["masses"]["core_R_t"]
    model={}
    for name in installed:
        part=shapes[name]
        if name.startswith("S1:water_"):
            part=D.D.trim_liquid_forward(part,water_ratio)
        part.label=name
        part.color=Color("#7E9BAF" if name.startswith("S1:") else "#A8A8A8")
        model[name]=part
    assert not set(model).intersection(bodies)
    model.update(bodies)
    OUT.mkdir(parents=True,exist_ok=True)
    final=OUT/(PREFIX+".glb")
    export_gltf(Compound(children=list(model.values())),final,unit=Unit.M,
                binary=True,linear_deflection=.05,angular_deflection=.3)
    names=glb_names(final)
    assert len(names)==234 and len(set(names))==234 and set(names)==set(model)
    pane_out=OUT/"crown_print_tiles"
    pane_out.mkdir(parents=True,exist_ok=True)
    for name in sorted(n for n in bodies if n.startswith("dry:crown_pane_")):
        export_stl(bodies[name],pane_out/(name[4:]+".stl"))
    aoi=crown["adaptive_optogel"]
    alloc=3.023
    cavity_m3=gel.volume
    missing_dims=[
      "Pane retainer cross-sections / positions (only 0.12t allowance and removal doctrine supplied)",
      "Osteon frame rib section and joints (only 1.8t mass; root/fork counts)",
      "Tambour gore track cross-section and swept path (16 tracks and 50deg break only)",
      "Brow ring axial datum (width 1m, height .22m, but no fully constrained placement)",
      "Cavity fill geometry: declared 3.023m3 need not equal full two-dome interspace",
    ]
    mass={p["id"]:p["mass_t"] for p in g["parts"]}
    report=dict(status="HOLD_UNQUALIFIED_CROWN",source_tag="canon-v2.5",
      source_geometry_sha256=sha,geometry_source_unchanged=True,
      count_named_panes=37,per_part_GLTF_nodes=len(names),
      installed_source_nodes=194,replaced_no_render_proxy_nodes_in_export=[
       "crown_dome","crown_c_additional_strata_gore","crown_c_outward_retainers",
       "crown_backup_pressure_dome","crown_adaptive_optogel"],
      note="Existing no_render mass proxies remain in source G1; physical crown solids overlay is not yet a source-qualified replacement.",
      outer_pressure_dome_apex_m=-.42,inner_backup_pressure_dome_apex_m=-.30,
      name_mapping="kT inner-backup order reverses v2.5 primary/backup labels, NOT coordinates",
      cavity_BRep_m3=cavity_m3,declared_AOI_fill_m3=alloc,
      AOI_volume_difference_m3=cavity_m3-alloc,
      AOI_mass_t_unchanged=aoi["mass_t"],
      source_mass_allocations_t={k:mass[k] for k in mass if k.startswith("crown_")},
      target_contacts=contacts,
      prohibited_overlap_count=sum(q.get("exceeds_D9_0p01m3") is True for q in contacts),
      failed_boolean_count=sum("error" in q for q in contacts),
      missing_canon_dimensions=missing_dims,
      other_geometry_changed=False,
      print_tiles_count=37,engineering_credit=0)
    report_path=OUT/(PREFIX+"_report.json")
    report_path.write_text(json.dumps(report,indent=2)+"\n")
    print("CROWN_37_PANES_VALID",len(bodies)-3,flush=True)
    print("CROWN_DOME_AND_GEL_VOLUME",a.volume,b.volume,cavity_m3,"target",alloc,flush=True)
    print("CROWN_BOW_CLASH_COUNT",report["prohibited_overlap_count"],"BOOLEAN_ERRORS",report["failed_boolean_count"],flush=True)
    print("CROWN_PER_PART_GLB_NODES",len(names),"size",final.stat().st_size,flush=True)
    print("CROWN_HOLD",json.dumps({k:report[k] for k in ("prohibited_overlap_count","failed_boolean_count","AOI_volume_difference_m3","missing_canon_dimensions")}),flush=True)

if __name__=="__main__":
    main()
