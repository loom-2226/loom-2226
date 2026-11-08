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
from build123d import Axis, Color, Compound, Face, Solid, Wire, Unit, export_gltf, export_stl
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from packing_phase1b import source_brep_pilot as P
import d9_sharded as D
from glazing_geom_v251 import build_glazing

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

def make_crown_brow(crown):
    """Accepted Option C render brow as a separate closed solid, NOT the Osteon mount.

    Reproduce loomgl.js crownMeshes XO(r)-0.03 from r=3.40 to 3.75 m.
    Finite-volume thickness is render geometry only; no new mass booking.
    """
    opt=crown["shell_option_c"]
    outer=opt["outer_tile_layer"]["radii_m"][-1]
    assert outer == 3.5 and opt["fair_to_hull_at_r_m"] == 4.5
    assert opt["slope_deg"] == 50
    slope=math.tan(math.radians(opt["slope_deg"]))
    def xo(radius):
        if radius <= opt["flat_to_r_m"]:
            return -opt["nose_extension_forward_m"]
        cone=-opt["nose_extension_forward_m"]+(
            min(radius,opt["slope_to_r_m"])-opt["flat_to_r_m"])*slope
        if radius <= opt["slope_to_r_m"]:
            return cone
        u=max(0.0,min(1.0,(radius-opt["slope_to_r_m"])/(
             opt["fair_to_hull_at_r_m"]-opt["slope_to_r_m"])))
        return cone+(2.35-cone)*(u*u*(3-2*u))
    rs=[outer-.10+i*.35/24 for i in range(25)]
    # Front face exactly reproduces the accepted render profile. The rear
    # face extends 4mm past XO to meet pane ends and the armour shoulder.
    front=[(xo(r)-.03,r,0.) for r in rs]
    rear=[(xo(r)+.004,r,0.) for r in reversed(rs)]
    solid=Solid.revolve(Face(Wire.make_polygon(front+rear,close=True)),360,Axis.X)
    assert solid.is_valid and solid.volume>0
    bb=P.bounds(solid)
    assert abs(bb[3]-3.75)<.02 and abs(bb[5]-3.75)<.02
    assert abs(xo(rs[0])-.03-.43845502963189387)<1e-7
    assert abs(xo(rs[-1])-.03-.833000640627047)<1e-7
    return solid,dict(radial_span_m=[rs[0],rs[-1]],
                      front_axial_span_m=[xo(rs[0])-.03,xo(rs[-1])-.03],
                      back_at_shoulder_x_m=xo(rs[-1])+.004,
                      render_surface="wayfarer/render/loomgl.js:crownMeshes",
                      geometry_only=True,mass_rebooked_t=0)


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
      ("dry:crown_inner_pressure_dome",b,"#93C4CC"),
      ("dry:crown_aoi_cavity_envelope",gel,"#52B6B0"),
    ):
        sh.label=name;sh.color=Color(color);bodies[name]=sh
    # Canon brow dimensions: 1m radial width and 0.22m longitudinal height.
    # Position derives from the outer dome's r=3.5m seat; 0.12m offset means
    # the same ring reaches BOTH dome rims. No user-unapproved PV relocation.
    deep=crown["shell_option_c"]["deep_pressure_domes"]
    r=crown["r_m"]
    R=deep["parent_radius_m"]; base=deep["parent_base_x_m"]
    outer_rim=base-(base-deep["backup_apex_x_m"])*math.sqrt(1-(r/R)**2)
    inner_rim=base-(base-deep["primary_apex_x_m"])*math.sqrt(1-(r/R)**2)
    brow=crown["brow_ring"]
    seat=P.sector(dict(k="sector",x0=outer_rim,
                       x1=outer_rim+brow["height_m"],r0=r,
                       r1=r+brow["width_m"],a0=0,a1=360))
    assert outer_rim < inner_rim < outer_rim+brow["height_m"]
    seat.label="dry:crown_osteon_brow_seat"
    seat.color=Color("#9EAAB5")
    bodies[seat.label]=seat
    # Retain the dome mount. The distinct exterior transition covers the
    # gap between the r=3.5m panes and the r=3.75m armour shoulder.
    brow_solid,brow_profile=make_crown_brow(crown)
    brow_solid.label="dry:crown_brow"
    brow_solid.color=Color("#A2A3A0")
    bodies[brow_solid.label]=brow_solid
    assert len(bodies)==42
    glazing, glazing_cutters, glazing_report = build_glazing(g,cfg,make_pane)
    assert len(glazing)==137 and len(glazing_cutters)==26
    # Physical crown aperture and seat rebate cut only the two permitted hull
    # solids. INNER ceramic = the pressure vessel's bow closure, not a second
    # overlapping copy of the existing 30mm bow shell.
    source_parts={p["id"]:p for p in g["parts"]}
    original={k:P.make(source_parts[k]["shape"])
              for k in ("bow_sensors","pressure_vessel","armor")}
    aperture=P.cyl(r,-2.0,base+.001)
    targets=dict(original)
    for key in ("pressure_vessel","armor"):
        targets[key]=original[key]-aperture
        targets[key]=targets[key]-seat
        assert targets[key].is_valid and targets[key].volume>0
    # Remove all 21 round and five panoramic WWS-1 apertures from the same
    # cut source PV/armour BReps. No other source installed solid is altered.
    for key in ("pressure_vessel", "armor"):
        for cutter in glazing_cutters:
            targets[key] = targets[key] - cutter
        assert targets[key].is_valid and targets[key].volume>0
    mass_removal={}
    for key in ("pressure_vessel","armor"):
        pre=float(original[key].volume);post=float(targets[key].volume)
        booked=source_parts[key]["mass_t"]
        removed=pre-post
        assert removed>0
        mass_removal[key]=dict(original_m3=pre,after_cut_m3=post,
           removed_m3=removed,original_booked_t=booked,
           original_effective_density_t_m3=booked/pre,
           removed_mass_t_at_original_effective_density=removed*booked/pre,
           remaining_mass_t_at_original_effective_density=post*booked/pre)
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
    # Export existing installed D9 parts, substituting ONLY the cut PV/armour\n    # plus the 41 true crown solids. Source ledger is untouched in this screen.
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
    model["dry:pressure_vessel"]=targets["pressure_vessel"]
    model["dry:armor"]=targets["armor"]
    for name in ("dry:pressure_vessel","dry:armor"):
        model[name].label=name
    assert not set(model).intersection(bodies)
    model.update(bodies)
    assert not set(model).intersection(glazing)
    model.update(glazing)
    # Complete non-exempt D9 category-(d) scan for the 373 installed viewer
    # BReps, with the SAME original 0.01 m3 threshold and classifier.
    # This is the mandatory candidate screen, not a replacement of the source
    # authority's current 194-part certified D9 report.
    ordered=sorted(model)
    pairs_total=len(ordered)*(len(ordered)-1)//2
    assert len(ordered)==373 and pairs_total==69378
    full_scan=D.pair_scan(model,ordered,0,pairs_total,C["D9"]["min_intersection_m3"])
    assert full_scan["pair_count"]==pairs_total
    print("CROWN_AND_GLAZING_FULL_D9_SCAN",json.dumps(dict(
        solids=len(ordered),pairs=pairs_total,
        category_d=full_scan["category_d_count"],
        bool_errors=len(full_scan["collision_errors"]),
        conflicts=full_scan["category_d_conflicts"][:18])),flush=True)
    assert full_scan["category_d_count"] == 0 and not full_scan["collision_errors"], (
        "new crown+glazing has D9 category-d conflict or Boolean error")
    OUT.mkdir(parents=True,exist_ok=True)
    final=OUT/(PREFIX+".glb")
    export_gltf(Compound(children=list(model.values())),final,unit=Unit.M,
                binary=True,linear_deflection=.05,angular_deflection=.3)
    names=glb_names(final)
    assert len(names)==373 and len(set(names))==373 and set(names)==set(model)
    pane_out=OUT/"crown_print_tiles"
    pane_out.mkdir(parents=True,exist_ok=True)
    for name in sorted(n for n in bodies if n.startswith("dry:crown_pane_")):
        export_stl(bodies[name],pane_out/(name[4:]+".stl"))
    export_stl(brow_solid,pane_out/"crown_brow.stl")
    glazing_stls=OUT/"glazing_print_parts"
    glazing_stls.mkdir(parents=True,exist_ok=True)
    for name,part in sorted(glazing.items()):
        export_stl(part,glazing_stls/(name[4:]+".stl"))
    assert len(list(glazing_stls.glob("*.stl"))) == 137
    aoi=crown["adaptive_optogel"]
    alloc=3.023
    cavity_m3=gel.volume
    missing_dims=[
      "Per-pane retainer cross-sections and individual extraction paths are not source dimensioned",
      "Osteon internal ribs and section details remain OPEN; only source-sized seat ring is solid",
      "Sixteen tambour track sections / moving swept mechanisms remain OPEN",
      "Full physically closed 3.023m3 AOI fill vs modelled 2.489m3 cavity remains OPEN",
    ]
    mass={p["id"]:p["mass_t"] for p in g["parts"]}
    report=dict(status="HOLD_UNQUALIFIED_CROWN",source_tag="canon-v2.5",
      source_geometry_sha256=sha,geometry_source_unchanged=True,
      count_named_panes=37,per_part_GLTF_nodes=len(names),
      installed_source_nodes=194,replaced_no_render_proxy_nodes_in_export=[
       "crown_dome","crown_c_additional_strata_gore","crown_c_outward_retainers",
       "crown_backup_pressure_dome","crown_adaptive_optogel"],
      note="Existing no_render mass proxies remain in source G1; physical crown solids overlay is not yet a source-qualified replacement.",
      outer_pressure_dome_apex_m=-.42,inner_pressure_dome_apex_m=-.30,
      inner_dome_is_pressure_vessel_bow_closure=True,
      exterior_crown_brow=brow_profile,
      exterior_crown_brow_named_solid=True,
      osteon_dome_seat_preserved=True,
      seat_ring_source_dims=dict(r_m=r,width_m=brow["width_m"],
          height_m=brow["height_m"],x_m=[outer_rim,outer_rim+brow["height_m"]]),
      removed_mass_from_pv_and_armor=mass_removal,
      name_mapping="INNER and OUTER are independent pressure domes; their apex coordinates are unchanged",
      cavity_BRep_m3=cavity_m3,declared_AOI_fill_m3=alloc,
      AOI_volume_difference_m3=cavity_m3-alloc,
      AOI_mass_t_unchanged=aoi["mass_t"],
      source_mass_allocations_t={k:mass[k] for k in mass if k.startswith("crown_")},
      already_booked_crown_added_t=sum(v for k,v in mass.items() if k.startswith("crown_")),
      mass_budget_note="Crown proxy masses already exist in source; do not charge a second time. Inner dome replaces pressure-vessel bow material; removed tonnes are inferred from the former whole-shell effective density, not canon rebookings.",
      target_contacts=contacts,
      full_D9_candidate_scan=full_scan,
      full_D9_candidate_accepts=(full_scan["category_d_count"]==0 and not full_scan["collision_errors"]),
      prohibited_overlap_count=sum(q.get("exceeds_D9_0p01m3") is True for q in contacts),
      failed_boolean_count=sum("error" in q for q in contacts),
      missing_canon_dimensions=missing_dims,
      other_geometry_changed=False,
      print_tiles_count=38,brow_stl_count=1,glazing_stl_count=137,
      glazing_glb_nodes=137,glazing=glazing_report,
      canonical_source_mass_t_before_and_after=g["dry_t"],
      delta_v_ECON_km_s_unchanged=707.845,
      engineering_credit=0)
    report_path=OUT/(PREFIX+"_report.json")
    report_path.write_text(json.dumps(report,indent=2)+"\n")
    print("CROWN_BROW_RENDER_PROFILE",json.dumps(brow_profile),flush=True)
    print("CROWN_37_PANES_VALID",sum(n.startswith("dry:crown_pane_") for n in bodies),flush=True)
    print("CROWN_DOME_AND_GEL_VOLUME",a.volume,b.volume,cavity_m3,"target",alloc,flush=True)
    print("CROWN_BOW_CLASH_COUNT",report["prohibited_overlap_count"],"BOOLEAN_ERRORS",report["failed_boolean_count"],flush=True)
    print("CROWN_HULL_MASS_REMOVAL",json.dumps(mass_removal),flush=True)
    print("CROWN_PER_PART_GLB_NODES",len(names),"size",final.stat().st_size,flush=True)
    print("WWS1_21_WINDOWS_5_BANDS_7_SPARES",glazing_report["round_assemblies"],
          glazing_report["viewport_band_segments"],glazing_report["spare_true_solids"],
          flush=True)
    print("CROWN_HOLD",json.dumps({k:report[k] for k in ("prohibited_overlap_count","failed_boolean_count","AOI_volume_difference_m3","missing_canon_dimensions")}),flush=True)

if __name__=="__main__":
    main()
