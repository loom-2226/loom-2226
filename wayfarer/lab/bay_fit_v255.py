#!/usr/bin/env python3
"""kT 2026-11-10 drone-crawler bay: source-pinned BRep fit, no mass rebooking.

Screen primary tangential+radial exit first. Screen kT's aft-door fallback
ONLY if primary does not fit. Build source allocation geometry in candidate
memory, never mutate the governing inputs or the v2.5.3 release.
"""
from __future__ import annotations
import hashlib, json, math, sys
from itertools import combinations
from pathlib import Path
from build123d import Color
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from packing_phase1b import source_brep_pilot as P

GEO=ROOT/"results/out/wayfarer_v05_geometry.json"
INPUT=ROOT/"config/wayfarer_v05_inputs.json"
DEC=ROOT/"config/kt_decisions.json"
EXPECTED="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
THRESH=.01
COURIER_PARTS=("courier_systems","drone_0","drone_1","drone_2","drone_3",
               "ext_crawler_dock_0","ext_crawler_dock_1","ext_crawler_dock_2")
WINGS=(("port",0,2,1),("starboard",1,3,-1))
MASS_SPLIT={"bay_shell":4.5,"bay_doors":2,"drone_cradles":3,
            "crawler_egress":1,"charging_thermal":1.5,
            "existing_sensor_turrets":1,
            "courier_systems_unallocated":6.450370894400045}

def volume(s):
    return 0.0 if s is None else float(s.volume)

def overlap(a,b):
    if P.bbox_intersection_upper(P.bounds(a),P.bounds(b))<=1e-8:
        return 0.0
    return volume(a & b)

def part(name,shape,colour="#8797AA"):
    s=P.make(shape)
    assert s is not None and s.is_valid and volume(s)>0,name
    s.label=name;s.color=Color(colour)
    return s

def panel(x0,x1,az,r0,span,t):
    return dict(k="panel",x0=x0,x1=x1,a=az,r0=r0,span=span,t=t)

def sector(x0,x1,r0,r1,a0,a1):
    return dict(k="sector",x0=x0,x1=x1,r0=r0,r1=r1,a0=a0,a1=a1)

def inputs():
    assert hashlib.sha256(GEO.read_bytes()).hexdigest()==EXPECTED
    g=json.loads(GEO.read_text());i=json.loads(INPUT.read_text())
    dec=json.loads(DEC.read_text())["drone_crawler_bay_layout_2026_11_10"]
    assert dec["decision"]=="ACCEPTED_LAYOUT_WITH_CHANGES_BREP_GATE"
    assert dec["spares"]["keep_approved_screened_rack_x_m"]==[20,22.6]
    src={v["id"]:v for v in g["parts"]}
    assert abs(sum(MASS_SPLIT.values())-src["courier_systems"]["mass_t"])<1e-9
    assert abs(sum(src[f"drone_{j}"]["mass_t"] for j in range(4))-1.2263970700784872)<1e-9
    assert all(src[f"ext_crawler_dock_{j}"]["mass_t"]==.2 for j in range(3))
    return g,i,src,dec

def candidate(mode,src):
    assert mode in ("tangential_radial","axial_aft_fallback")
    shapes={};allocation={};booked={}
    def add(n,spec,source,mass=None,col="#8097AF"):
        assert n not in shapes
        shapes[n]=part(n,spec,col)
        allocation[n]=source
        if mass is not None:booked[n]=mass
    for name,j,k,sign in WINGS:
        if mode=="tangential_radial":
            # Axial width from source; 3.4m / 2.9m tangential as approved.
            a=255 if sign==1 else 285
            mars=panel(14.05,15.15,a,4.76,1.02,3.4)
            dense=panel(16.45,17.35,a,4.95,.87,2.9)
        else:
            # Source 3.4m / 2.9m longitudinal; narrow azimuth wings.
            a=241.5 if sign==1 else 298.5
            b=254 if sign==1 else 286
            mars=panel(14.04,17.44,a,4.85,1.02,1.1)
            dense=panel(14.18,17.08,b,5.0,.87,.9)
        for idx,spec in ((j,mars),(k,dense)):
            source=f"drone_{idx}"
            add(f"dry:bay_{source}",spec,source,src[source]["mass_t"],"#86A8C6")
            # Thin physically separate radial support under pod.
            cradle=dict(spec,r0=spec["r0"]-.03,span=.025,
                         t=spec["t"]*.92,
                         x0=spec["x0"]+.015,x1=spec["x1"]-.015)
            add(f"dry:bay_cradle_{source}",cradle,"courier_systems",.75,"#687B8B")
    for j,az in enumerate((248,270,292)):
        n=f"ext_crawler_dock_{j}"
        add(f"dry:bay_{n}",panel(14.08,14.88,az,5.94,.15,.6),
            n,src[n]["mass_t"],"#B49B6B")
        add(f"dry:bay_crawler_guide_{j}",panel(14.90,15.48,az,5.94,.10,.055),
            "courier_systems",1/3,"#B49B6B")
    # Two charging and thermal subpanels, clear of centerline corridor.
    for idx,az in enumerate((266,274)):
        add(f"dry:bay_charge_{idx}",panel(16.96,17.32,az,5.94,.10,.32),
            "courier_systems",.75,"#C2A975")
    # Closed debris/thermal shell segments leave a genuine central collar
    # aperture. Fore shell is split around three crawler hatches.
    shell_defs=[
        sector(14.00,14.04,6.06,6.10,235,305),
        sector(14.04,14.91,6.06,6.10,235,244),
        sector(14.04,14.91,6.06,6.10,254,263),
        sector(14.04,14.91,6.06,6.10,277,286),
        sector(14.04,14.91,6.06,6.10,296,305),
        sector(14.92,17.42,6.06,6.10,235,260),
        sector(14.92,17.42,6.06,6.10,280,305)
    ]
    for idx,spec in enumerate(shell_defs):
        add(f"dry:bay_shell_{idx:02d}",spec,"courier_systems",4.5/len(shell_defs),"#6C7D88")
    door_closed={};door_sweep={}
    for side,k,(aa,bb) in ((0,"port",(235,264)),(1,"starboard",(276,305))):
        if mode=="tangential_radial":
            # One radial opening per wing, front face slides outwards; sweep
            # occupies r6.10..7.10. All pods must fit the angular exit.
            closed=sector(14.05,17.40,6.02,6.06,aa,bb)
            swept=sector(14.05,17.40,6.10,7.10,aa,bb)
        else:
            # Aft clamshell at x17.47..17.50; opened path extends aft,
            # before reaching the adjacent midship structural equipment.
            closed=sector(17.47,17.50,4.64,6.05,aa,bb)
            swept=sector(17.50,18.22,4.64,6.05,aa,bb)
        key=f"dry:bay_door_{k}"
        add(key,closed,"courier_systems",1.0,"#8DABBA")
        door_closed[key]=shapes[key]
        door_sweep[key]=part("sweep:"+key,swept,"#DAA36E")
    assert len(shapes)>20
    assert abs(sum(v for n,v in booked.items() if allocation[n]=="courier_systems")-12)<1e-7, (
        "mass is split into 4.5+2+3+1+1.5=12t physically represented; "
        "1t prebooked turret allocation and 6.450371t remain undrawn")
    return shapes,allocation,booked,door_closed,door_sweep

def local_fit(mode,src,shapes,door_closed,door_sweep):
    issues=[];stats=[]
    def fail(kind,a,b,v,extra=None):
        issues.append(dict(kind=kind,a=a,b=b,overlap_m3=round(v,7),detail=extra))
    bound=P.make(src["courier_systems"]["shape"])
    for n,s in shapes.items():
        v=volume(s-bound)
        if v>THRESH:fail("outside_accepted_bay",n,"courier_envelope",v)
    # Keep-out more conservative than the existing 0.8m collar:
    # 0.88m swept axial/tangential radius, full radial approach to r7.2.
    collar=part("keepout:collar_radial_approach",dict(
        k="tube",p0=[16,0,-4.10],p1=[16,0,-7.20],r=.88))
    local={
        "collar":part("keepout:docking_collar",src["docking_collar"]["shape"]),
        "service_arm":part("keepout:service_arm",src["service_arm"]["shape"]),
        **{n:part("keepout:"+n,src[n]["shape"]) for n in ("tunnel_0","tunnel_1","tunnel_2")},
        "collar_approach":collar
    }
    for n,s in shapes.items():
        for key,obj in local.items():
            v=overlap(s,obj)
            if v>THRESH:fail("protected_equipment_or_corridor",n,key,v)
    # A true self-clash is a blocker, not an 'allowed cradle' exception.
    for a,b in combinations(sorted(shapes),2):
        v=overlap(shapes[a],shapes[b])
        if v>THRESH:fail("new_part_self_intersection",a,b,v)
    # Model the canopy door's OPEN swept volume independently of the CLOSED
    # door. A volume may contact its own frame, not independently mass-booked
    # installed hardware. A pod cannot be under a moving door.
    for door,sweep in door_sweep.items():
        for key,obj in local.items():
            v=overlap(sweep,obj)
            if v>THRESH:fail("door_open_sweep_blocks_existing",door,key,v)
        for n,s in shapes.items():
            if n==door or n.startswith("dry:bay_shell_"):continue
            v=overlap(sweep,s)
            if v>THRESH:fail("door_open_sweep_blocks_new",door,n,v)
    # Radial launch path must pass its own opened wing door, without touching
    # independent pods or collar corridor. Aft alternative slides longitudinally.
    for n,s in shapes.items():
        if not n.startswith("dry:bay_drone_"):continue
        # Internal allowed pod volume is subtracted from its swept path; no
        # exemption for interaction with any OTHER pod or corridor.
        bb=P.bounds(s)
        if mode=="tangential_radial":
            # Exact swept BRep translated outwards in .3m increments. Door
            # openings must cover every cross section near r6.1.
            import build123d as B
            az=255 if n.endswith(("_0","_2")) else 285
            radial=B.Vector(0,math.cos(math.radians(az)),math.sin(math.radians(az)))
            moved=s.translate(radial*1.55)
            v=overlap(moved,collar)
            if v>THRESH:fail("pod_radial_exit_hits_collar_corridor",n,"collar_approach",v)
            for other,ob in shapes.items():
                if other==n or other.startswith(("dry:bay_cradle_","dry:bay_charge_","dry:bay_shell_")):continue
                if other.startswith("dry:bay_drone_") and other!=n:
                    v=overlap(moved,ob)
                    if v>THRESH:fail("pod_radial_exit_hits_other_pod",n,other,v)
            # A pod requires full tangential width through its open door.
            if n.endswith(("_0","_2")):
                dangles=(235,264)
            else:dangles=(276,305)
            opening=part("opening",sector(14.0,17.5,6.0,7.4,*dangles))
            v=volume(moved-opening)
            if v>THRESH:fail("pod_exits_outside_radial_door_aperture",n,str(dangles),v)
        else:
            import build123d as B
            moved=s.translate(B.Vector(1.6,0,0))
            for key,obj in local.items():
                v=overlap(moved,obj)
                if v>THRESH:fail("pod_aft_exit_hits_existing",n,key,v)
    # Strake clearance against both installed stack AND the two deployed
    # two-metre pleats, source 1300 K. No thermal 'PASS' claimed from D9.
    for a in (220,320):
        for k,spec in (("stack",src[f"strake_{a}"]["shape"]),
                       ("pleat0",panel(14,17.5,a,4.5,2,.06)),
                       ("pleat1",panel(14,17.5,a,6.5,2,.06))):
            fin=part("strake",spec)
            for n,s in shapes.items():
                v=overlap(s,fin)
                if v>THRESH:fail("strake_mode_intersection",n,f"strake_{a}:{k}",v)
            for n,s in door_sweep.items():
                v=overlap(s,fin)
                if v>THRESH:fail("strake_mode_door_sweep",n,f"strake_{a}:{k}",v)
    stats=dict(parts=len(shapes),issues=len(issues),issue_types=sorted({x["kind"] for x in issues}),
               inside_bay_verified=not any(x["kind"]=="outside_accepted_bay" for x in issues),
               protected_collar_access_clear=not any("collar" in x["b"] for x in issues),
               open_door_sweep_clear=not any(x["kind"].startswith("door_open") for x in issues))
    return issues,stats

def view_factor_screen():
    """Conservative unshadowed differential Lambertian panel view-factor.

    Hot surfaces: x14..17.5/r4.5..6.5 at az220 and320, 1300K, e=.9.
    Receiving faces: bay lateral edges at az235 and305, x14..17.5,
    r4.6..6.1, facing the corresponding hot strake. Four-by-four
    midpoint quadrature over source and receiving faces. Ignore baffles.
    This is a heat-flux *exposure*, NOT installed thermal closure.
    """
    sigma=5.670374419e-8; temp=1300; eps=.9
    flux=eps*sigma*temp**4
    result={}
    for side,hot,edge,sgn in (("port",220,235,1),("starboard",320,305,-1)):
        ah=math.radians(hot);ae=math.radians(edge)
        hn=(0,-math.sin(ah)*sgn,math.cos(ah)*sgn)
        rn=(0,math.sin(ae)*sgn,-math.cos(ae)*sgn)
        total=0.;samples=0
        # receiver 4x4 surface patches, integrate apparent hot area by 12x12
        for ir in range(4):
            rr=4.6+(ir+.5)*1.5/4
            for ix in range(4):
                rx=14+(ix+.5)*3.5/4
                rv=(rx,rr*math.cos(ae),rr*math.sin(ae))
                F=0.
                for hr in range(12):
                    rh=4.5+(hr+.5)*2/12
                    for hx in range(12):
                        xh=14+(hx+.5)*3.5/12
                        hv=(xh,rh*math.cos(ah),rh*math.sin(ah))
                        diff=tuple(hv[q]-rv[q] for q in range(3))
                        r2=sum(z*z for z in diff)
                        if r2<=1e-6:continue
                        mag=math.sqrt(r2)
                        # receiver points toward emitter, emitter points
                        # toward receiver: directional factors must face.
                        ci=max(0,sum(rn[q]*diff[q] for q in range(3))/mag)
                        co=max(0,-sum(hn[q]*diff[q] for q in range(3))/mag)
                        F+=ci*co/(math.pi*r2)*(3.5/12)*(2/12)
                total+=F;samples+=1
        average=min(1,total/samples)
        result[side]=dict(unshadowed_geometric_view_factor=round(average,6),
                           hot_strake_temperature_K=1300,
                           emissivity=.9,
                           unshadowed_incident_kW_m2=round(flux*average/1000,4),
                           passive_shielding_credit_kW_m2=0,
                           thermal_qualification="OPEN: flux proxy without baffle shadowing, reflectance or response")
    return result

def screen():
    g,cfg,src,dec=inputs()
    selection=None;results={}
    for mode in ("tangential_radial","axial_aft_fallback"):
        parts,mapping,masses,doors,sweeps=candidate(mode,src)
        fails,stats=local_fit(mode,src,parts,doors,sweeps)
        results[mode]=dict(pass_BRep_fit=not fails,stats=stats,
                            conflicts=fails[:80],all_conflicts_count=len(fails),
                            future_courier_mass_allocation=MASS_SPLIT)
        print("BAY_BREP_FIT",mode,json.dumps({**stats,"first_conflicts":fails[:7]}),flush=True)
        if not fails:
            selection=(mode,parts,mapping,masses,doors,sweeps)
            break
    therm=view_factor_screen()
    report=dict(status="BAY_SOURCE_BREP_FIT_SCREEN",source_geometry_sha256=EXPECTED,
        kT_decision="2026-11-10 tangential primary / aft fallback",
        source_spare_panes_remain_screened_at_x_m=[20,22.6],
        courier_total_booked_t=src["courier_systems"]["mass_t"],
        courier_remains_named_t=MASS_SPLIT["courier_systems_unallocated"],
        original_vehicle_and_dock_mass_untouched=True,
        ship_mass_unchanged_t=g["dry_t"],
        no_new_canon_geometry=True,
        variants=results,strake_view_factor_screen=therm,
        chosen=None if selection is None else selection[0])
    OUT=ROOT/"render/out"
    OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/"wayfarer_drone_bay_fit_20261110.json"
    path.write_text(json.dumps(report,indent=2)+"\n")
    print("BAY_SCREEN_DISPOSITION",report["chosen"],json.dumps(therm),flush=True)
    if selection is None:
        raise RuntimeError("Both kT-approved bay layouts fail the BRep fit")
    return selection,report

if __name__=="__main__":
    screen()
