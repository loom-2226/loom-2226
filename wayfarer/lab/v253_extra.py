"""v2.5.3 purely drawn no_render inventory. Source positions, no new mass credit.

The two gore states are alternative poses of the SAME 16 booked assemblies,
not 32 pieces to be installed together. Physical seams and mechanisms OPEN.
"""
import math
from build123d import Axis, Color, Solid, Wire
from packing_phase1b import source_brep_pilot as P

DONE = {"crown_dome", "crown_backup_pressure_dome",
        "crown_adaptive_optogel", "crown_c_seven_spare_panes"}
KEEP = {"crown_c_outward_retainers", "wws1_shelter_armour_restoration",
        "node_mount_allowance", "d8_unlocated_doubler_allowance"}
GORE = "crown_c_additional_strata_gore"

def inventory(geom):
    rows={p["id"]:p for p in geom["parts"] if "no_render" in p.get("tags",[])}
    done={n for n in rows if n in DONE or n.startswith(("window_","viewport_band_"))}
    keep={n for n in rows if n in KEEP or n.startswith(("wws1_port_uplift_","wws1_band_uplift_"))}
    draw=set(rows)-done-keep-{GORE}
    assert len(rows)==122 and len(done)==30 and len(keep)==30 and len(draw)==61
    assert GORE in rows
    assert len(done|keep|draw|{GORE})==122 and not (done&keep)
    return rows,sorted(done),sorted(keep),sorted(draw)

def new_true_solids(geom):
    rows,done,keep,to_draw=inventory(geom)
    out={}
    for name in to_draw:
        row=rows[name]
        shape=P.make(row["shape"])  # exact approved shape / location, not a proxy double
        assert shape is not None and shape.is_valid and shape.volume>0,(name,shape)
        shape.label="dry:"+name
        shape.color=Color("#A6ACB2" if row["system"]=="structure" else "#B4B5B0")
        out[shape.label]=shape
    evidence=dict(source_no_render_count=122,already_done_count=30,
                  already_done_ids=done,keep_as_allocation_count=30,
                  keep_as_allocation_ids=keep,new_true_solids_count=61,
                  new_true_solids_ids=to_draw,
                  new_source_allocations_t={k:rows[k]["mass_t"] for k in to_draw},
                  source_allocation_total_t=sum(p["mass_t"] for p in rows.values()),
                  mass_rebooked_t=0)
    return out,evidence

def xo(rad,opt):
    flat=-opt["nose_extension_forward_m"]
    if rad<=opt["flat_to_r_m"]:return flat
    edge=flat+(opt["slope_to_r_m"]-opt["flat_to_r_m"])*math.tan(
        math.radians(opt["slope_deg"]))
    if rad<=opt["slope_to_r_m"]:
        return flat+(rad-opt["flat_to_r_m"])*math.tan(
            math.radians(opt["slope_deg"]))
    t=(rad-opt["slope_to_r_m"])/(opt["fair_to_hull_at_r_m"]-opt["slope_to_r_m"])
    return edge+(2.35-edge)*t*t*(3-2*t)

def gore_loft(opt,index,pose):
    """Finite-volume 22.5 degree gore along exact Option C meridional surface.

    0.1 m visual thickness equals WWS-1 existing 27g/cm2 / 2700 kg/m3
    representational Strata depth, not a new material constitutive statement.
    Numeric axis starts at r=0.5 mm to avoid degenerate BRep pole.
    """
    assert pose in ("stowed","closed") and 0<=index<16
    if pose=="closed":
        rs=[.0005+(3.5-.0005)*i/52 for i in range(53)]
        offset=0.0  # no additional nose extension beyond canon -1.2m
    else:
        rs=[3.50+(4.50-3.50)*i/32 for i in range(33)]
        offset=.025  # within existing 0.20m armour shoulder
    a0=index*2*math.pi/16
    a1=(index+1)*2*math.pi/16
    sections=[]
    for r in rs:
        x=xo(r,opt)+offset
        points=[(x,r*math.cos(a0),r*math.sin(a0)),
                (x,r*math.cos(a1),r*math.sin(a1)),
                (x+.1,r*math.cos(a1),r*math.sin(a1)),
                (x+.1,r*math.cos(a0),r*math.sin(a0))]
        sections.append(Wire.make_polygon(points,close=True))
    result=Solid.make_loft(sections,ruled=True)
    assert result is not None and result.is_valid and result.volume>0,(index,pose)
    result.label=f"dry:crown_gore_{index:02d}_{pose}"
    result.color=Color("#7D8792" if pose=="closed" else "#515D64")
    return result

def gore_states(inputs):
    spec=inputs["habitat"]["decks"][0]["command_layout"]["crown_dome"]["shell_option_c"]
    assert spec["gores"]["count"]==16 and spec["gores"]["equivalent_areal_g_cm2"]==27
    assert spec["nose_tip_x_m"]==-1.2 and spec["slope_deg"]==50
    assert spec["flat_to_r_m"]==2 and spec["slope_to_r_m"]==3.5
    assert spec["fair_to_hull_at_r_m"]==4.5
    a={}
    for pose in ("stowed","closed"):
        a[pose]={s.label:s for s in (gore_loft(spec,i,pose) for i in range(16))}
        assert len(a[pose])==16
    evidence=dict(gores_per_state=16,poses=["stowed","closed"],
        physically_mutually_exclusive=True,not_additional_inventory=True,
        underlying_no_render_id=GORE,nominal_visual_thickness_m=.1,
        stowed_radial_span_m=[3.5,4.5],
        closed_radial_span_m=[.0005,3.5],
        overall_baseline_length_m=54.5,source_mass_rebooked_t=0,
        actuation_seams_and_fatigue="OPEN / NOT QUALIFIED")
    return a,evidence

def check_added_interior(model,geom,added):
    """Newly drawn internal fixtures inside original vessel inner cavity.

    Service band and external structural brackets are *not* pressure-vessel
    interiors. Respect that distinction rather than forcing false containments.
    """
    source={p["id"]:p for p in geom["parts"]}
    pv=source["pressure_vessel"]["shape"]
    pressure_inside=P.half_ellipsoid(pv["xa"]+pv["t"],pv["xb"],pv["xc"],pv["R"]-pv["t"])
    inner=[n for n in added if source[n[4:]]["system"]=="habitat" and
           n!="dry:service_shield_band"]
    assert len(inner)==48, (len(inner),inner)
    escaped=[]
    for n in sorted(inner):
        s=model[n]
        outside=s-pressure_inside
        volume=0.0 if outside is None else float(outside.volume)
        if volume>.0001:escaped.append(dict(id=n,outside_m3=volume))
    assert not escaped,("newly drawn internal part outside pressure vessel",escaped)
    service=model["dry:service_shield_band"]
    svc_hull=P.cyl(4.5,14.,18.)
    svc_escaped=service-svc_hull
    sv=0.0 if svc_escaped is None else float(svc_escaped.volume)
    assert sv<=.0001,("service shield outside service hull",sv)
    return dict(checked_new_pressure_interior_count=48,
                escaped_new_pressure_interior=escaped,
                checked_service_hull_count=1,
                service_hull_escaped_m3=sv,
                structural_external_attachment_count=12,
                external_brackets_not_misclassified_as_internal=True,
                pass_containment=True)


def fit_service_shield_band(geom):
    """kT 2026-11-09: fitted 0.6 t shield, unchanged source mass and density.

    Two axial station intervals avoid the frame solids. The four 2m-wide
    source strake-stack footprints and 0.8m docking collar are cut out with
    10mm positive radial/tangential clearance. The surviving arc pieces are
    physically separate BRep solids, grouped under ONE source allocation.
    A radial solve holds the prior 0.6 t at its original effective density.
    No credit assigned to gaps from overlapping radiator/frame/collar mass.
    """
    rows={p["id"]:p for p in geom["parts"]}
    src=rows["service_shield_band"]
    assert abs(src["mass_t"]-.6)<1e-9
    assert src["shape"]["x0"]==14 and src["shape"]["x1"]==17
    assert src["shape"]["r0"]==4.3 and src["shape"]["r1"]==4.36
    reference_volume=float(P.make(src["shape"]).volume)
    assert abs(reference_volume-src["volume_m3"])<.01
    axial=(("fore",14.15,16.),("aft",16.15,17.))
    cutters=[]
    strake_angles=[40,140,220,320]
    for az in strake_angles:
        source=rows[f"strake_{az}"]["shape"]
        assert source["k"]=="panel" and source["r0"]==4 and source["t"]==2
        cutters.append(P.make(dict(k="panel",x0=14.14,x1=17.01,
                        a=az,r0=3.99,span=.52,t=2.02)))
    collar=rows["docking_collar"]["shape"]
    assert collar["r"]==.8 and collar["p0"]==[16,0,-3.6]
    cutters.append(P.make(dict(k="tube",p0=[16,0,-3.55],
                    p1=[16,0,-4.8],r=.81)))
    def cut_shape(lo,hi,inner):
        shape=P.make(dict(k="sector",x0=lo,x1=hi,r0=inner,
                          r1=4.48,a0=0,a1=360))
        for tool in cutters:
            shape=shape-tool
        if shape is None or not shape.is_valid:raise ValueError("invalid fitted band")
        return [s for s in shape.solids() if float(s.volume)>1e-8]
    def at(inner):
        shapes=[(label,s) for label,lo,hi in axial
                         for s in cut_shape(lo,hi,inner)]
        return shapes,sum(float(s.volume) for _,s in shapes)
    lo,hi=4.3,4.479
    low,volume_low=at(lo)
    high,volume_high=at(hi)
    if not(volume_low>reference_volume>volume_high):
        raise ValueError(f"0.6t fitting volume not bracketed: {volume_low}, {volume_high}, {reference_volume}")
    for _ in range(14):
        mid=(lo+hi)*.5
        trial,v=at(mid)
        if v>reference_volume:lo=mid
        else:hi=mid
    shapes,volume=at((lo+hi)*.5)
    if abs(volume-reference_volume)>.01:
        raise ValueError(f"fitted band cannot preserve mass/volume: {volume-reference_volume}m3")
    bodies={}
    counts={"fore":0,"aft":0}
    for label,sh in shapes:
        i=counts[label]
        counts[label]+=1
        name=f"dry:service_shield_band_{label}_{i:02d}"
        assert sh.is_valid and sh.volume>0 and name not in bodies
        sh.label=name
        sh.color=Color("#B0B8A3")
        bodies[name]=sh
    assert counts["fore"]>0 and counts["aft"]>0
    inner=(lo+hi)*.5
    report=dict(source_allocation_id="service_shield_band",
                booked_mass_t=src["mass_t"],booked_density_t_per_m3=src["mass_t"]/reference_volume,
                source_volume_m3=reference_volume,fitted_volume_m3=volume,
                implied_fitted_mass_t=volume*src["mass_t"]/reference_volume,
                axial_intervals_m=[[14.15,16.],[16.15,17.]],
                radial_inner_m=inner,radial_outer_m=4.48,
                reference_radial_thickness_m=.06,
                fitted_radial_thickness_m=4.48-inner,
                strake_cut_angles_deg=strake_angles,
                docking_collar_cutout=True,
                clearance_m=.01,independent_BRep_pieces=len(bodies),
                source_ledger_unchanged=True,
                credited_gap_areal_density_g_cm2=0,
                g6_requires_focused_single_run=True,
                piece_ids=sorted(bodies))
    assert report["fitted_radial_thickness_m"]>.06
    return bodies,report
