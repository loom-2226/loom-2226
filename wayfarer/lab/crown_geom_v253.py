#!/usr/bin/env python3
"""kT 2026-11-09 v2.5.3 drawing-only overlay of source-booked fixtures and shutters.

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
from v253_extra import new_true_solids, gore_states, check_added_interior

EXPECTED = "88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
GEO = ROOT / "results/out/wayfarer_v05_geometry.json"
INPUT = ROOT / "config/wayfarer_v05_inputs.json"
OUT = ROOT / "render/out"
PREFIX = "wayfarer_parts_v253_88ce19fc"

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


def make_option_c_fairing(spec):
    """Replace old armour nose r3.5..4.5 with kT's accepted C0 Option C fair.

    x(r) is exactly crownMeshes/XO from loomgl.js. The solid 0.2m
    rear offset is a BRep display thickness, not new mass booking.
    """
    assert spec["nose_tip_x_m"] == -1.2
    assert spec["flat_to_r_m"] == 2
    assert spec["slope_deg"] == 50
    assert spec["slope_to_r_m"] == 3.5
    assert spec["fair_to_hull_at_r_m"] == 4.5
    slope=math.tan(math.radians(spec["slope_deg"]))
    edge=-spec["nose_extension_forward_m"]+1.5*slope
    def at_radius(rad):
        if rad <= spec["slope_to_r_m"]:
            return -spec["nose_extension_forward_m"]+max(
                0,rad-spec["flat_to_r_m"])*slope
        u=(rad-spec["slope_to_r_m"])/(
            spec["fair_to_hull_at_r_m"]-spec["slope_to_r_m"])
        return edge+(2.35-edge)*(u*u*(3-2*u))
    radii=[3.5+i/48 for i in range(49)]
    front=[(at_radius(r),r,0.) for r in radii]
    aft=[(at_radius(r)+.20,r,0.) for r in reversed(radii)]
    fair=Solid.revolve(Face(Wire.make_polygon(front+aft,close=True)),360,Axis.X)
    assert fair.is_valid and fair.volume>0
    assert abs(front[0][0]-edge)<1e-10 and abs(front[-1][0]-2.35)<1e-10
    assert all(a[0]<=b[0] for a,b in zip(front,front[1:]))
    assert spec["gores"]["count"]==16
    return fair,dict(r_m=[3.5,4.5],front_x_m=[front[0][0],front[-1][0]],
        pane_edge_x_m=edge,hull_shoulder_x_m=2.35,
        seam_step_at_pane_m=front[0][0]-edge,
        seam_step_at_cylinder_m=front[-1][0]-2.35,
        source_renderer="wayfarer/render/loomgl.js:crownMeshes/XO",
        authored_gore_count=16,physical_gore_mechanism_qualified=False,
        fairing_brep_volume_m3=float(fair.volume),source_armour_mass_rebooked_t=0)


def relocate_outfit_L1(source,pressure_shape):
    """Conform the L1 distributed-outfit annulus inside the domed PV."""
    assert source["k"]=="sector" and abs(source["x0"]-.2)<1e-9
    assert abs(source["x1"]-3)<1e-9 and source["a1"]-source["a0"]==360
    s=pressure_shape
    xa=s["xa"]+s["t"]; xb=s["xb"]; R=s["R"]-s["t"]
    assert xa < source["x0"] < source["x1"] < xb
    xx=[source["x0"]+(source["x1"]-source["x0"])*i/40 for i in range(41)]
    rr=[R*math.sqrt(1-((xb-x)/(xb-xa))**2)-.08 for x in xx]
    thick=source["r1"]-source["r0"]
    assert abs(thick-.10)<1e-8 and min(rr)>thick
    outer=[(x,r,0.) for x,r in zip(xx,rr)]
    inner=[(x,r-thick,0.) for x,r in zip(reversed(xx),reversed(rr))]
    moved=Solid.revolve(Face(Wire.make_polygon(outer+inner,close=True)),360,Axis.X)
    assert moved.is_valid and moved.volume>0
    evidence=dict(source_shape=source,corrected_axial_range_m=[xx[0],xx[-1]],
        corrected_inner_radius_range_m=[min(rr)-thick,max(rr)-thick],
        corrected_outer_radius_range_m=[min(rr),max(rr)],
        nominal_clearance_to_inner_pressure_wall_m=.08,
        shape_volume_m3=float(moved.volume),mass_rebooked_t=0)
    return moved,evidence


def inside_pressure_hull_check(model,source_parts):
    """Independent unary containment; D9 tests intersections, not this."""
    vessel=source_parts["pressure_vessel"]["shape"]
    interior=P.half_ellipsoid(vessel["xa"]+vessel["t"],
                             vessel["xb"],vessel["xc"],
                             vessel["R"]-vessel["t"])
    # Every material habitat fixture, and structural deck floors.
    # room_* denote EMPTY SPACE volumes, not physically installed materials.
    physical=sorted("dry:"+name for name,p in source_parts.items()
            if "no_render" not in p.get("tags",[]) and (
                (p["system"]=="habitat" and name!="armor" and
                 not name.startswith("room_")) or name.startswith("floor_")))
    missing=[name for name in physical if name not in model]
    assert not missing,("unexamined physical habitat interiors",missing)
    results=[]
    tol=.0001 # Numerical 0.1L, not a clearance exemption.
    for name in physical:
        part=model[name]
        try:
            escaped=part-interior
            v=0 if escaped is None else float(escaped.volume)
            assert math.isfinite(v)
        except Exception as exc:
            raise RuntimeError(f"containment Boolean failed for {name}: {exc}")
        results.append(dict(part=name,volume_m3=round(float(part.volume),9),
                            outside_pressure_interior_m3=round(v,9),
                            pass_containment=v<=tol))
    failures=[x for x in results if not x["pass_containment"]]
    report=dict(checked_physical_interior_count=len(physical),
        checked_parts=results,escaped_parts=failures,pass_containment=not failures,
        outside_tolerance_m3=tol,
        excluded_no_render_allocation_count=sum("no_render" in p.get("tags",[]) for p in source_parts.values()),
        excluded_semantic_volume_proxies=sorted(
            "dry:"+name for name in source_parts if name.startswith("room_")),
        excluded_exterior_and_boundary="Armor, vessel, crown, windows, exterior equipment, tanks and propulsion are not internal habitat fixtures",
        why_D9_missed="D9 evaluates only solid overlaps >0.01m3, not unary hull containment; outfit_* collision pairs are category-c authored display representations, not category-d.")
    assert not failures,("installed interior outside pressure vessel",failures)
    return report


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

def main(on_model_ready=None, medical_port_visual_overlay=False):
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
    assert g["overall_length_m"] == cfg["hull"]["overall_length_m"] == 54.5
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
    # kT 2026-11-13: approved NON-CANON WWS-1 positional overlay.
    # Copy only the three feature positions used for the 21 real window
    # solids and their cutters. Keep the pinned geometry JSON, actual source
    # allocations, original source mass, and all other features unchanged.
    glazing_source=g
    if medical_port_visual_overlay:
        approved=json.loads((ROOT/"config/kt_decisions.json").read_text())[
            "exterior_surface_2026_11_13"]
        assert approved["canon_change"] is False
        assert "9.30" in approved["medical_ports"]
        new_features=[];moved=[]
        for feat in g["features"]:
            if feat["kind"]=="window" and feat["room"]=="L4-medical":
                assert abs(feat["pos"][0]-9.10)<1e-8
                assert abs(feat["d_m"]-1.55)<1e-8
                theta=(math.degrees(math.atan2(feat["pos"][2],feat["pos"][1]))+360)%360
                assert any(abs(theta-k)<1e-7 for k in (180,210,240)),theta
                changed={**feat,"pos":[9.30,*feat["pos"][1:]]}
                new_features.append(changed)
                moved.append(dict(azimuth_deg=theta,source_x_m=9.10,
                                  model_x_m=9.30,diameter_m=feat["d_m"]))
            else:
                new_features.append(feat)
        assert len(moved)==3
        glazing_source={**g,"features":new_features}
    glazing, glazing_cutters, glazing_report = build_glazing(glazing_source,cfg,make_pane)
    if medical_port_visual_overlay:
        assert [q["centre"][0] for q in glazing_report["individual_windows"]
                if q["id"].startswith("window_L4-medical_")] == [9.30]*3
        glazing_report["medical_visual_overlay"]=dict(
            status="NON_CANON_POSITION",moved=moved,source_mass_delta_t=0,
            cutters_are_BRep=True,exterior_source_json_unchanged=True,
            source_WWS1_qualification="NOT CLAIMED",
            pressure_or_shielding_qualification="NOT CLAIMED")
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
    # Replace just the old nose shoulder, leaving the x>=2.35 cylinder.
    fairing,fairing_report=make_option_c_fairing(spec)
    obsolete=P.sector(dict(k="sector",x0=-2.,x1=2.35,
        r0=3.5,r1=4.51,a0=0,a1=360))
    targets["armor"]=(targets["armor"]-obsolete).fuse(fairing)
    assert targets["armor"].is_valid and targets["armor"].volume>0
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
    outfit,outfit_report=relocate_outfit_L1(
        source_parts["outfit_L1"]["shape"],source_parts["pressure_vessel"]["shape"])
    outfit.label="dry:outfit_L1"
    outfit.color=Color("#B5A59D")
    model[outfit.label]=outfit
    model["dry:pressure_vessel"]=targets["pressure_vessel"]
    model["dry:armor"]=targets["armor"]
    for name in ("dry:pressure_vessel","dry:armor"):
        model[name].label=name
    assert not set(model).intersection(bodies)
    model.update(bodies)
    assert not set(model).intersection(glazing)
    model.update(glazing)
    containment=inside_pressure_hull_check(model,source_parts)
    print("WAYFARER_ALL_INTERNAL_INSIDE_HULL",json.dumps({
        "physical_parts":containment["checked_physical_interior_count"],
        "escaped_parts":containment["escaped_parts"],
        "pass":containment["pass_containment"]}),flush=True)
    # 30 already drawn originals remain exactly as v2.5.2; 30 extra
    # accounting allocations stay hidden. New 61 are P.make source solids.
    new_parts,inventory_report=new_true_solids(g)
    assert len(model)==373
    assert inventory_report["new_source_allocations_count"]==61
    assert len(new_parts)==inventory_report["new_true_solids_count"]
    g6_rebuild=json.loads((ROOT/"lab/packing_phase1b/current_g3_rebuild_report.json").read_text())
    band_g6=g6_rebuild["G6"]
    assert band_g6["g6_runs_for_v253"]==1
    assert band_g6["kT_v253_min_53p39_with_0p1_tolerance_pass"]
    assert abs(band_g6["source_original_g_cm2"]-53.39034860482293)<.01
    assert abs(band_g6["v253_band_fit"]["fitted_volume_m3"]-
               inventory_report["service_shield_band_fitting"]["fitted_volume_m3"])<.005
    print("WAYFARER_V253_SINGLE_G6_PASS",json.dumps(dict(
        source=band_g6["source_original_g_cm2"],
        fitted=band_g6["candidate_changed_BRep_g_cm2"],
        minimum=53.39034860482293-.1)),flush=True)
    assert not set(model).intersection(new_parts)
    model.update(new_parts)
    added_inside=check_added_interior(model,g,new_parts)
    poses,gore_report=gore_states(cfg)
    assert len(model)==373+len(new_parts)
    if on_model_ready is not None:
        # Exterior Step 1 hook: reusable v2.5.3 BReps, without re-exporting
        # or changing v2.5.3 canon. Full-ship radiator states are checked
        # separately in the calling script.
        on_model_ready(model,poses,g,cfg,C,containment,added_inside,new_parts,sha)
        return
    scans={}
    exports={}
    OUT.mkdir(parents=True,exist_ok=True)
    for pose in ("stowed","closed"):
        state={**model,**poses[pose]}
        ordered=sorted(state)
        pairs_total=len(ordered)*(len(ordered)-1)//2
        assert len(ordered)==len(model)+16 and pairs_total==len(ordered)*(len(ordered)-1)//2
        scan=D.pair_scan(state,ordered,0,pairs_total,C["D9"]["min_intersection_m3"])
        scans[pose]=scan
        print("WAYFARER_V253_D9_"+pose.upper(),json.dumps(dict(
            solids=len(ordered),pairs=pairs_total,
            category_d=scan["category_d_count"],
            bool_errors=len(scan["collision_errors"]),
            conflicts=scan["category_d_conflicts"][:25])),flush=True)
        assert scan["category_d_count"]==0 and not scan["collision_errors"], (
            "v2.5.3 "+pose+" D9 collision or Boolean error")
        path=OUT/(PREFIX+"_"+pose+".glb")
        export_gltf(Compound(children=list(state.values())),path,unit=Unit.M,
                    binary=True,linear_deflection=.05,angular_deflection=.3)
        state_names=glb_names(path)
        assert len(state_names)==len(state) and set(state_names)==set(state)
        exports[pose]=str(path.relative_to(ROOT))
    # Combined parts catalogue has both named poses for viewer selection.
    # They are NOT 32 simultaneous pieces of material.
    final=OUT/(PREFIX+".glb")
    both={**model,**poses["stowed"],**poses["closed"]}
    export_gltf(Compound(children=list(both.values())),final,unit=Unit.M,
                binary=True,linear_deflection=.05,angular_deflection=.3)
    names=glb_names(final)
    assert len(names)==len(both) and len(set(names))==len(both) and set(names)==set(both)
    full_scan=scans["stowed"]
    print("WAYFARER_V253_EXPORT",json.dumps(dict(all_states_nodes=len(names),
        poses=exports,new_solids=len(new_parts),source_allocations=61,
        booked_mass_recharged_t=0)),flush=True)
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
    report=dict(status="D9_CONTAINMENT_PASS_HARDWARE_OPEN",
      drawing_revision="canon-v2.5.3",source_tag="canon-v2.5",
      source_geometry_sha256=sha,geometry_source_unchanged=True,
      count_named_panes=37,per_part_GLTF_nodes=len(names),
      original_v252_nodes_preserved=373,
      approved_no_render_inventory=inventory_report,
      new_true_solids_count=len(new_parts),
      fitted_service_shield_band=inventory_report["service_shield_band_fitting"],
      single_focused_shelter_G6=band_g6,
      new_interior_containment_check=added_inside,
      gore_state_geometry=gore_report,
      gore_states_D9_scans=scans,
      mutually_exclusive_gore_state_GLBS=exports,
      combined_GLTF_is_selectable_catalogue_not_simultaneous_pose=True,
      installed_source_nodes=194,replaced_no_render_proxy_nodes_in_export=[
       "crown_dome","crown_c_additional_strata_gore","crown_c_outward_retainers",
       "crown_backup_pressure_dome","crown_adaptive_optogel"],
      note="Existing no_render mass proxies remain in source G1; physical crown solids overlay is not yet a source-qualified replacement.",
      outer_pressure_dome_apex_m=-.42,inner_pressure_dome_apex_m=-.30,
      inner_dome_is_pressure_vessel_bow_closure=True,
      option_c_armour_shoulder_fairing=fairing_report,
      outfit_L1_relocation=outfit_report,
      all_internal_parts_inside_pressure_hull=containment,
      overall_length_m_unchanged=g["overall_length_m"],
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
      full_D9_candidate_accepts=all(x["category_d_count"]==0 and not x["collision_errors"] for x in scans.values()),
      prohibited_overlap_count=max(s["category_d_count"] for s in scans.values()),
      legacy_target_contact_overlap_count=sum(q.get("exceeds_D9_0p01m3") is True for q in contacts),
      target_contacts_basis="pre-substitution brow/seat vs armour diagnostics; not D9 installed-state clashes",
      failed_boolean_count=sum("error" in q for q in contacts),
      missing_canon_dimensions=missing_dims,
      other_geometry_changed=["service_shield_band_fitted_at_unchanged_0p6t"],
      unchanged_source_geometry=True,
      print_tiles_count=38,brow_stl_count=1,glazing_stl_count=137,
      glazing_glb_nodes=137,glazing=glazing_report,
      canonical_source_mass_t_before_and_after=g["dry_t"],
      delta_v_ECON_km_s_unchanged=707.845,
      engineering_credit=0)
    report_path=OUT/(PREFIX+"_report.json")
    report_path.write_text(json.dumps(report,indent=2)+"\n")
    print("OPTION_C_SHOULDER_FAIRING",json.dumps(fairing_report),flush=True)
    print("CROWN_BROW_RENDER_PROFILE",json.dumps(brow_profile),flush=True)
    print("CROWN_37_PANES_VALID",sum(n.startswith("dry:crown_pane_") for n in bodies),flush=True)
    print("CROWN_DOME_AND_GEL_VOLUME",a.volume,b.volume,cavity_m3,"target",alloc,flush=True)
    print("CROWN_BOW_CLASH_COUNT",report["prohibited_overlap_count"],"BOOLEAN_ERRORS",report["failed_boolean_count"],flush=True)
    print("CROWN_HULL_MASS_REMOVAL",json.dumps(mass_removal),flush=True)
    print("CROWN_PER_PART_GLB_NODES",len(names),"size",final.stat().st_size,flush=True)
    print("WWS1_21_WINDOWS_5_BANDS_7_SPARES",glazing_report["round_assemblies"],
          glazing_report["viewport_band_segments"],glazing_report["spare_true_solids"],
          flush=True)
    print("CROWN_HARDWARE_OPEN",json.dumps({k:report[k] for k in ("prohibited_overlap_count","failed_boolean_count","AOI_volume_difference_m3","missing_canon_dimensions")}),flush=True)

if __name__=="__main__":
    main()
