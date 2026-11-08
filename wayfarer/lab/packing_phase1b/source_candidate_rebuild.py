#!/usr/bin/env python3
"""#471 engineering port of research #157 D8 candidate.py at 2e7c374; no lab mutation.

Uses actual #156 OpenCascade/build123d make() and category(), pinned input SHA.
Never subtracts ANY primary G5 load path. Auto-resolution of independent
nonprimary solid intersections is provisional: volumes, mass, double-counts,
G6 and reach must be reported, not waved away as qualified hardware.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
from collections import defaultdict
from build123d import CenterOf, Compound, Color, Unit, export_step, export_gltf

def is_primary(name):
    if not name.startswith("dry:"):return False
    x=name[4:]
    return (x.startswith(("frame_","longeron_","bay_corner_")) or
            x in ("aft_bulkhead","thrust_cone","pressure_vessel","armor","core_trunk",
                  "shield","reactor","nozzle","docking_collar") or x.startswith("rcs_A") or
            x.startswith("tunnel_"))
def is_secondary(name):
    x=name.split(":")[1]
    return (x.startswith(("floor_","core_racks","bay_liner","door_",
                          "hotfin_root_","bracket_","trunk_plug_","service_shield_band")))
def is_view_proxy(name):
    x=name.split(":")[1]
    return x.startswith(("room_","outfit_","i4_","window_","wws1_",
                         "crown_","viewport_","node_mount_allowance"))
def rank(name):
    """Keep designed primary, remass/fuel, thermal radiating surfaces, then equipment."""
    if is_primary(name):return 100
    if name.startswith("S1:water_"):return 90
    if name.startswith("S1:house_fuel"):return 88
    if name.startswith("S1:pw_service"):return 85
    if name.startswith("S1:jacket_"):return 80
    if name.startswith("dry:house_fuel_tank"):return 79
    if name.startswith("dry:hotfin_") and "root_" not in name:return 77
    if name.startswith("dry:strake_"):return 75
    if name.startswith("dry:manifold"):return 73
    if name.startswith("dry:house_reactor"):return 70
    if name.startswith("dry:house_energy_battery"):return 68
    if name.startswith("dry:electrical_fwd"):return 40
    if name.startswith("dry:electrical"):return 38
    if is_secondary(name):return 32
    if is_view_proxy(name):return 1
    return 50

def centroid(s):
    v=s.center(CenterOf.MASS)
    return [float(v.X),float(v.Y),float(v.Z)]

def vol(s):
    try:return float(s.volume)
    except:return 0.
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True,
                    help="unmodified #156 project directory (pinned exact original)")
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--export",action="store_true")
    ap.add_argument("--courier-forward",action="store_true",help="kT D1 follow-up #4: choose screened forward external service-section courier; retains aft default for old checks")
    ap.add_argument("--fuel-t",type=float,default=4.,help="D1 D-He3 total t, default 4.0 legacy Phase1a")
    ap.add_argument("--g1-liquid-ullage",action="store_true",help="G1 SOURCE: 5pct liquid volume (300t x 1.05 = 315m3); else old tank fraction replay")
    ap.add_argument("--house-reserve-t",type=float,default=.10,help="D1 screening house fuel reserve above torch full-ECON fuel; 0.10t provisional, NOT source mission requirement")
    args=ap.parse_args()
    assert 3.0<=args.fuel_t<=5.0
    assert args.house_reserve_t>=0
    sys.path.insert(0,str(args.source.resolve()))
    import pilot as P
    import triage as T
    src=args.source
    raw=(src/"geometry_base.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==P.SOURCE_HASH
    J=json.loads(raw);I=P.load_json("inputs_base.json");C=P.load_json("criteria_base.json")

    # kT-approved G3 authority: only the 7 offset_yz parts differ from #156.
    # Replay the complete original research D1-D8 machinery on the 2026-11-08
    # current source-derived -0.26m propulsion chain. No new tuning rules.
    upstream=Path(__file__).resolve().parents[2]
    current_bytes=(upstream/"results/out/wayfarer_v05_geometry.json").read_bytes()
    current=json.loads(current_bytes)
    criteria=json.loads((upstream/"config/cert_criteria.json").read_text())
    current_sha=hashlib.sha256(current_bytes).hexdigest()
    assert current_sha==criteria["D9"]["approved_source_geometry_sha256"]
    assert abs(current["thrust_line_offset_m"]["y"]-.03)<1e-9
    assert abs(current["thrust_line_offset_m"]["z"]+.26)<1e-9
    names={"nozzle","reactor","shield","rcs_A+Y","rcs_A+Z","rcs_A-Y","rcs_A-Z"}
    source_parts={p["id"]:p for p in J["parts"]}
    current_parts={p["id"]:p for p in current["parts"]}
    old_nonzero={p["id"] for p in J["parts"] if any(p["shape"].get("offset_yz",[0,0]))}
    new_nonzero={p["id"] for p in current["parts"] if any(p["shape"].get("offset_yz",[0,0]))}
    assert old_nonzero==new_nonzero==names,(old_nonzero,new_nonzero)
    for name in sorted(names):
        old=source_parts[name]["shape"]
        new=current_parts[name]["shape"]
        assert all(abs(a-b)<1e-9 for a,b in zip(old["offset_yz"],[.03,-.23])),(name,old)
        assert all(abs(a-b)<1e-9 for a,b in zip(new["offset_yz"],[.03,-.26])),(name,new)
        assert {k:v for k,v in old.items() if k!="offset_yz"}=={k:v for k,v in new.items() if k!="offset_yz"},name
        old["offset_yz"]=list(new["offset_yz"])
    print("G3_AUTHORITY",json.dumps(dict(geometry_sha256=current_sha,
        thrust=current["thrust_line_offset_m"],S1_CG_m=current["states"]["S1"]["cg_m"],
        rebased_parts=sorted(names),frozen_offset_m=[.03,-.23],
        authoritative_offset_m=[.03,-.26])),flush=True)

    original_d=json.loads((src/"results"/"clash_triage.json").read_bytes())
    assert len(original_d["conflicts_d"])==150
    out=args.out;out.mkdir(parents=True,exist_ok=True)
    all_s={};base={};book_mass={};kind={};history=defaultdict(list)
    for part in J["parts"]:
        name="dry:"+part["id"]
        s=P.make(P.settled(part["shape"]))
        all_s[name]=s;base[name]=vol(s)
        book_mass[name]=part["mass_t"];kind[name]="dry"
    for i,p in enumerate(J["fluids_by_state"]["S1"]):
        name=f"S1:{p['id']}:{i:02d}"
        s=P.make(P.settled(p["shape"]))
        all_s[name]=s;base[name]=vol(s)
        book_mass[name]=p["mass_t"];kind[name]="water" if p["id"].startswith(("jacket_","water_","pw_service")) else "other_fluid"
    assert len(all_s)==309
    old_parts=dict(all_s)
    old_mass=dict(book_mass)
    movement=[];notches=[];violations=[]

    def replace(name,new,decision,remark):
        old=all_s[name]
        v=vol(new)
        if v<=0:raise ValueError("candidate destroyed "+name)
        all_s[name]=new
        movement.append(dict(part=name,decision=decision,old_m3=round(vol(old),8),
                             new_m3=round(v,8),message=remark,
                             source_mass_t=book_mass[name]))
    def cut(name,cutter,reason):
        prev=all_s[name]
        before=vol(prev)
        try:
            aftershape=prev.cut(cutter)
            after=vol(aftershape)
            lost=max(0.,before-after)
        except Exception as ex:
            violations.append(dict(part=name,reason=reason,error=str(ex)))
            return False
        if lost<=.000001:return True
        if after<=1e-7:
            violations.append(dict(part=name,reason=reason,blocked="entire solid removed",
                                   before_m3=before,lost_m3=lost))
            return False
        if is_primary(name):
            raise RuntimeError("FATAL D8: primary member cut attempted "+name)
        all_s[name]=aftershape
        original=base.get(name,before)
        flag=100*lost/original>5
        notches.append(dict(part=name,cut_reason=reason,removed_m3=round(lost,9),
                            original_m3=round(original,9),
                            pct_source_envelope=round(100*lost/original,4),
                            over_5pct=flag,
                            original_density_t_m3=(book_mass[name]/original if original>0 else None),
                            secondary=is_secondary(name)))
        return True
    def new(name,s,mass,material,why):
        assert name not in all_s
        all_s[name]=s;base[name]=vol(s);book_mass[name]=mass;kind[name]=material
        movement.append(dict(part=name,decision=why,new_m3=round(vol(s),9),
                             source_mass_t=mass))
    # D2 kT decision: RELOCATE the courier, restore BOTH useful envelopes.
    # The full service-arm sector remains near its existing collar/tunnel;
    # extend aft 0.5m to recover its volume after primary-path notches.
    # Courier has a separate aft/outer cone-adjacent carrier envelope,
    # outside 2.75m shadow-shield radius and inside fin-root radius;
    # no hold/payload reservation is taken. Structural support and thermal
    # exposure of this carrier location remain unqualified.
    service_p=next(p for p in J["parts"] if p["id"]=="service_arm")
    replace("dry:service_arm",
            P.make(dict(service_p["shape"],x1=17.5)),
            "D2","service arm retained at original azimuth 225-315; +0.5m aft volume for primary collar/tunnel notches")
    courier_p=next(p for p in J["parts"] if p["id"]=="courier_systems")
    if args.courier_forward:
        # kT D1 follow-up #4: aft x35-39m is outside the direct
        # neutron shadow and within ~0.6m of 1750K deployed hot fins.
        # Exterior forward service bay between strakes 220/320:
        # 70deg sector gives >95% original volume with 19.450t unchanged.
        courier_new=dict(courier_p["shape"],x0=14.0,x1=17.5,
                         r0=4.6,r1=6.1,a0=235,a1=305)
        courier_message=("COURIER moved FORWARD to exterior service-section gap between strakes, "
             "shadow-shield LOS blocked (analytic), x14-17.5/r4.6-6.1/az235-305; "
             "external mounting, 1300K strake radiative view factors and access remain UNQUALIFIED")
    else:
        courier_new=dict(courier_p["shape"],x0=35.0,x1=39.0,
                         r0=2.8,r1=4.5,a0=225,a1=315)
        courier_message=("COURIER aft near conical thrust shroud; "
             "neutron/1750K-fin hazard now screened UNACCEPTABLE as unshielded default")
    replace("dry:courier_systems",P.make(courier_new),
            "D2",courier_message)
    # D3. Keep central trunk primary uncut; remap 11.670t racks to surrounding annulus.
    pr=next(p for p in J["parts"] if p["id"]=="core_racks")
    r0=.95
    r1=math.sqrt(r0*r0+.81*.81)
    replace("dry:core_racks",P.make(dict(pr["shape"],r0=r0,r1=r1)),
            "D3","racks outside uncut 0.9m radius trunk; volume preserved before other notches")
    # D4. Dedicated monoprop tank in otherwise unassigned aft sector of forward ring.
    cl=dict(k="sector",x0=17,x1=18,r0=2.0,r1=2.8,a0=182,a1=202)
    for n in ("dry:c_lite_dry",next(n for n in all_s if n.startswith("S1:c_lite_monoprop:"))):
        replace(n,P.make(cl),"D4","separate C-lite store in electrical ring away from reactor and battery angles; contents share tank envelope")
    # D5. Booked jacket water is the sum of overlapping parts. Remove overlap
    # from later segments, and move its 1.931109t to the existing service reservoir.
    jnames=[n for n in all_s if n.startswith("S1:jacket_")]
    for k,n in enumerate(jnames):
        for previous in jnames[:k]:
            if not cut(n,all_s[previous],"D5 unique jacket water; transferred to service"):
                break
    jbook=sum(book_mass[n] for n in jnames)
    junique=sum(vol(all_s[n]) for n in jnames)
    jlost=jbook-junique
    assert abs(jlost-1.9311090369478805)<0.002,(jbook,junique,jlost)
    for n in jnames: book_mass[n]=vol(all_s[n])  # water at 1 t/m³
    service=next(n for n in all_s if n.startswith("S1:pw_service:"))
    srcS=next(p for p in J["fluids_by_state"]["S1"] if p["id"]=="pw_service")
    f_old=srcS["shape"]["settled_fraction"]
    geom_full=srcS["mass_t"]/f_old
    f_new=(srcS["mass_t"]+jlost)/geom_full
    assert f_new<1.
    replace(service,P.make(P.settled(dict(srcS["shape"],settled_fraction=f_new))),
            "D5","service fill +1.931t, source ullage still positive")
    book_mass[service]=srcS["mass_t"]+jlost
    # D1. Source 5t D-He3 / 83.7758 m³ proxy density. One four-lobe
    # conformal 4t store in the unfilled forward portion of source CSlot
    # cell geometries. The dry 0.5t source tank envelope is rebuilt as four
    # narrow closure cap solid proxies (6mm) immediately aft of each lobe.
    fuel=next(n for n in all_s if n.startswith("S1:house_fuel:"))
    drytank="dry:house_fuel_tank"
    oldfuel=J["fluids_by_state"]["S1"][-2]
    assert oldfuel["id"]=="house_fuel"
    fuel_target=args.fuel_t/5*oldfuel["volume_m3"]
    cells=[p for p in J["fluids_by_state"]["S1"] if p["id"].startswith("water_")]
    assert len(cells)==4
    waterloss=0.
    oldwater=sum(book_mass[n] for n in all_s if n.startswith("S1:water_"))
    all_s.pop(fuel);all_s.pop(drytank)
    book_mass.pop(fuel);book_mass.pop(drytank)
    per=fuel_target/4.
    capthick=0.006
    shell_volume=0.
    for k,p in enumerate(cells):
        b=dict(p["shape"]);b.pop("settled_fraction")
        area=vol(P.make(b))/(b["x1"]-b["x0"])
        xfuelend=b["x0"]+per/area
        xwaterstart=b["x1"]-p["shape"]["settled_fraction"]*(b["x1"]-b["x0"])
        assert xfuelend+capthick<xwaterstart,(p["id"],xfuelend,xwaterstart)
        s=P.make(dict(b,x1=xfuelend))
        new(f"S1:house_fuel_lobe_{k}:15",s,args.fuel_t/4,"other_fluid","D1")
        cap=P.make(dict(b,x0=xfuelend,x1=xfuelend+capthick))
        shell_volume+=vol(cap)
        new(f"dry:house_fuel_tank_cap_{k}",cap,.125,"dry","D1")
    fuel_actual=sum(vol(s) for n,s in all_s.items() if n.startswith("S1:house_fuel_lobe_"))
    assert abs(fuel_actual-fuel_target)<0.03,(fuel_actual,fuel_target)
    core_gross=sum(vol(P.make({k:v for k,v in p["shape"].items() if k!="settled_fraction"})) for p in cells)
    core_net=core_gross-J["tank_structure"]["displaced_m3"]
    sum_water_rendered=sum(vol(all_s[n]) for n in all_s if n.startswith("S1:water_"))
    # Keep real source 5.870m3 unlocated web/baffle displacement in capacity
    # budget, despite source not providing physical installed shapes for it.
    # When using source G1 LIQUID basis, do not treat the B-rep's 1.8%
    # virtual water volume (unlocated tank internals already charged in
    # core_net) as physical water or double-charge the structure debit.
    # Source 250t = 254.633m3 of water envelope by representation.
    # Net liquid mass/t is still 1 t/m3, EXACTLY source G1.
    deficit=(0. if args.g1_liquid_ullage else
             max(0.,sum_water_rendered+fuel_actual+shell_volume-core_net))
    # only exact required water displacement, no performance tuning
    for k,p in enumerate(cells):
        n=next(n for n in all_s if n.startswith(f"S1:{p['id']}:"))
        b=p["shape"];L=b["x1"]-b["x0"]
        frac=b["settled_fraction"]
        area=vol(P.make({k:v for k,v in b.items() if k!="settled_fraction"}))/L
        sh=P.make(P.settled(dict(b,settled_fraction=frac-deficit/4/area/L)))
        before=vol(all_s[n]);after=vol(sh)
        replace(n,sh,"D1","retract filled water slightly to preserve source unlocated 5.870m3 internal baffle/web volume")
        book_mass[n]*=after/before
        waterloss+=before-after
    # D7. Each fin has a 28m operating BRep panel (folded source model remains
    # well documented by #156). Thin sheet is an exploratory 5mm dry panel,
    # not a qualified material assumption: mass is unchanged 17.024t.
    for name in [n for n in all_s if n.startswith("dry:hotfin_") and "root" not in n]:
        p=next(p for p in J["parts"] if p["id"]==name[4:])
        sh=dict(p["shape"],span=28.,t=.005)
        replace(name,P.make(sh),"D7","four deployed 28m membranes; illustrative 5mm sheet; 4kg/m² per face source mass retained")
    # D2/D7 exterior equipment relocation: avoid destroying 62-71% of
    # terminals/dock by shaving them against the 90t manifold allocation.
    for name in ("ext_laser_terminal_0","ext_laser_terminal_1","ext_crawler_dock_2"):
        p=next(p for p in J["parts"] if p["id"]==name)
        sh=dict(p["shape"])
        delta=1.55 if name.startswith("ext_laser") else 1.2
        sh["x0"]+=delta;sh["x1"]+=delta
        replace("dry:"+name,P.make(sh),"D7",
                "move external accessory just aft of 90t manifold; do not cut 62-71% of its working envelope")
    # D8 & remaining D1-D7: remove ONLY nonprimary independent B-rep
    # overlap. Preserve actual primary load path volumes bit-for-bit.
    # No conflict is auto excused by blanket D8; every eligible pair tested.
    initial_primary={n:(vol(s),hashlib.sha256(str(P.bounds(s)).encode()).hexdigest())
                     for n,s in all_s.items() if is_primary(n)}
    unresolved=[]
    for iteration in range(4):
        clashes=[]
        names=list(all_s)
        for i,a in enumerate(names):
            sa=all_s[a]
            ba=P.bounds(sa)
            for b in names[i+1:]:
                sb=all_s[b]
                if P.bbox_intersection_upper(ba,P.bounds(sb))<=.01:continue
                cat,reason=T.classify({"a":a,"b":b})
                if cat!="d":continue
                common=sa & sb
                overlap=vol(common)
                if overlap>.01:clashes.append((a,b,round(overlap,9),reason))
        print("CANDIDATE CLASH ITER",iteration,"d",len(clashes),flush=True)
        if not clashes:break
        for a,b,v,why in clashes:
            if a not in all_s or b not in all_s:continue
            # stale list: current BRep may already have been trimmed
            if P.bbox_intersection_upper(P.bounds(all_s[a]),P.bounds(all_s[b]))<=.01:continue
            inter=vol(all_s[a] & all_s[b])
            if inter<=.01:continue
            if is_primary(a) and is_primary(b):
                violations.append(dict(a=a,b=b,m3=inter,
                                       blocked="D8 primary-primary conflict; no relocation allowed"))
                continue
            if rank(a)>rank(b):winner,loser=a,b
            elif rank(b)>rank(a):winner,loser=b,a
            else:winner,loser=sorted((a,b))
            if not cut(loser,all_s[winner],f"candidate {winner} protected over {loser}; {why}"):
                continue
    # final exhaustive BRep clash scan: only physically installed solids,
    # never four CORE_FULL analytical duplicates.
    names=list(all_s);allhits=[];d=[];n=0
    for i,a in enumerate(names):
        sa=all_s[a];ba=P.bounds(sa)
        for b in names[i+1:]:
            sb=all_s[b];n+=1
            if P.bbox_intersection_upper(ba,P.bounds(sb))<=.01:continue
            intr=vol(sa & sb)
            if intr>.01:
                cat,why=T.classify({"a":a,"b":b})
                row=dict(a=a,b=b,m3=round(intr,8),category=cat,why=why)
                allhits.append(row)
                if cat=="d":d.append(row)
    for pn,stat in initial_primary.items():
        if abs(vol(all_s[pn])-stat[0])>1e-8:
            raise RuntimeError("PRIMARY STRUCTURE CHANGED "+pn)
    # Strict physical water audit: cuts into primary structure displace fluid.
    # Only the approved 1.931t D5 transfer is automatically booked. Additional
    # displaced protected volume must be flagged; no silently added water.
    jacket_end=sum(vol(all_s[n]) for n in jnames)
    service_end=vol(all_s[service])
    protected_end=jacket_end+service_end+J["protected_water"]["c_tank_t"]
    protected_deficit=50-protected_end
    if protected_deficit>0.000001:
        # Keep 50 t *physically* allocated: resolve frame/longeron cuts
        # to source service-water capacity within existing D5 reservoir.
        # This is water placement, not a new physical subsystem.
        target=50-jacket_end-J["protected_water"]["c_tank_t"]
        fmax=J["protected_water"]["service_tank_capacity_t"]/geom_full
        prim=[(n,s) for n,s in all_s.items() if is_primary(n)]
        def candidate_service(ff):
            sh=P.make(P.settled(dict(srcS["shape"],settled_fraction=ff)))
            for n,ob in prim:
                if P.bbox_intersection_upper(P.bounds(sh),P.bounds(ob))>.0000001:
                    sh=sh.cut(ob)
            return sh
        upper=candidate_service(fmax)
        if vol(upper)+1e-7<target:
            violations.append(dict(blocked="D5 service reservoir insufficient AFTER primary notches",
                                   needed_t=target,capacity_unique_t=vol(upper)))
        else:
            low=f_new;high=fmax
            for _ in range(38):
                mid=(low+high)/2
                if vol(candidate_service(mid))<target:low=mid
                else:high=mid
            fitted=candidate_service(high)
            replace(service,fitted,"D5",
                    "top up service fill around IMMUTABLE primary collar/frame and longerons; 50t unique total")
            book_mass[service]=vol(fitted)
            service_end=vol(fitted)
            protected_end=jacket_end+service_end+J["protected_water"]["c_tank_t"]
            protected_deficit=50-protected_end
            if abs(protected_deficit)>1e-5:
                violations.append(dict(blocked="D5 water union didn't close",
                                       remaining_t=protected_deficit))
    for wn in jnames: book_mass[wn]=vol(all_s[wn])  # exact after D8 primary cuts, no phantom jacket water
    # G1: 300t water at 1t/m3; ullage 5% of PHYSICAL water liquid.
    # The source B-rep water proxy has an unlocated web/baffle inflation:
    # 250t booked -> 254.633m3 nominal B-rep solid. Preserve that
    # original proxy scale only for spatial collision/ray testing, never
    # interpret it as water density, true liquid mass or usable volume.
    f_ullage=I["tanks"]["ullage_fraction"]
    water_envelope_per_physical_t=sum_water_rendered/oldwater
    if args.g1_liquid_ullage:
        water_capacity_physical_m3=(core_net-fuel_actual-shell_volume)/(1+f_ullage)
        max_core_water_m3=min(float(I["canon"]["remass_t"]),water_capacity_physical_m3)
        required_ullage=f_ullage*max_core_water_m3
        target_water_BRep_m3=max_core_water_m3*water_envelope_per_physical_t
    else:
        required_ullage=f_ullage*core_net
        max_core_water_m3=core_net-fuel_actual-shell_volume-required_ullage
        target_water_BRep_m3=max_core_water_m3
    current_water_m3=sum(vol(all_s[n]) for n in all_s if n.startswith("S1:water_"))
    # Symmetric 4-cell change, exact full collision check follows.
    if abs(current_water_m3-target_water_BRep_m3)>1.e-8:
        for p in cells:
            wn=next(n for n in all_s if n.startswith(f"S1:{p['id']}:"))
            oldv=vol(all_s[wn])
            targetv=oldv+(target_water_BRep_m3-current_water_m3)/len(cells)
            b=p["shape"]
            full=P.make({k:v for k,v in b.items() if k!="settled_fraction"})
            totalvol=vol(full)
            ff=targetv/totalvol
            assert 0<ff<=b["settled_fraction"]+1.e-8,(wn,ff,b["settled_fraction"])
            newwater=P.make(P.settled(dict(b,settled_fraction=ff)))
            replace(wn,newwater,"D1-G1-ULLAGE",
                    "5% of physical water liquid; B-rep envelope scaled from pinned source source mass/shape ratio")
            book_mass[wn]*=vol(newwater)/oldv
    final_core_water_m3=sum(vol(all_s[n]) for n in all_s if n.startswith("S1:water_"))
    physical_water_t=sum(book_mass[n] for n in all_s if n.startswith("S1:water_"))
    actual_ullage_m3=(core_net-fuel_actual-shell_volume-
                       (physical_water_t if args.g1_liquid_ullage else final_core_water_m3))
    if actual_ullage_m3+1.e-6<required_ullage:
        violations.append(dict(blocked="core G1 5pct liquid-source ullage missing",
                               required=required_ullage,actual=actual_ullage_m3))
    if args.g1_liquid_ullage and abs(physical_water_t-max_core_water_m3)>.002:
        violations.append(dict(blocked="source 1t/m3 G1 physical water ledger vs source BRep proxy discrepancy",
                               expected_physical_t=max_core_water_m3,actual_physical_t=physical_water_t))
    waterloss=sum_water_rendered-final_core_water_m3
    d2_envelopes={}
    for d2name in ("dry:courier_systems","dry:service_arm"):
        v=vol(all_s[d2name]);v0=base[d2name]
        d2_envelopes[d2name]=dict(source_m3=round(v0,8),
            candidate_installed_m3=round(v,8),
            percentage_restored=round(100*v/v0,5),
            meets_95_percent=v>=.95*v0)
        if v<.95*v0:
            violations.append(dict(blocked="D2 restore >=95% original useful envelope",
                                   item=d2name,source_volume_m3=v0,remaining_volume_m3=v))
    # Report per-item total notch volume, not just individual pair cuts.
    per_notch={}
    for row in notches:
        name=row["part"]
        if name not in base:continue
        lost=max(0.,base[name]-vol(all_s[name]))
        if lost<1.e-6:continue
        per_notch[name]=dict(
            part=name,source_BRep_m3=round(base[name],9),
            remaining_BRep_m3=round(vol(all_s[name]),9),
            lost_m3=round(lost,9),
            lost_percent_of_source=round(100*lost/base[name],5),
            FLAG_over5=100*lost/base[name]>5,
            protected_primary_untouched=is_primary(name),
            secondary_doubler_requirement_t=(
                round(1.5*lost/base[name]*book_mass[name],9)
                if is_secondary(name) else 0.))
    # Bow "box" in the GLB is NOT an installed box: all overlapping
    # crown_* 7x7m B-rep allocations carry source tag no_render.
    # Identify each mass and geometric incursions; exclude them from GLB
    # presentation ONLY, preserving masses and B-rep accounting.
    crown=[]
    armor=all_s["dry:armor"];vessel=all_s["dry:pressure_vessel"]
    for p in J["parts"]:
        if p["id"].startswith("crown_") and p["shape"]["k"]=="box" and p["shape"]["x0"]<1:
            n="dry:"+p["id"];shape=all_s[n]
            bb=P.bounds(shape)
            crown.append(dict(part=n,mass_t=p["mass_t"],source_tags=p["tags"],
                envelope_m3=round(vol(shape),6),
                axial_range_m=[round(bb[0],3),round(bb[1],3)],
                side_extent_m=[round(bb[2],3),round(bb[3],3)],
                vertical_extent_m=[round(bb[4],3),round(bb[5],3)],
                forward_of_armor_front_m=max(0,round(-bb[0],4)),
                forward_of_pressure_vessel_front_m=max(0,round(-.3-bb[0],4)),
                overlap_armor_m3=round(vol(shape & armor),6),
                overlap_pressure_vessel_m3=round(vol(shape & vessel),6)))
    # Source masses are retained on equipment; secondary reinforcement
    # adds 1.5x mass notionally displaced from original distributed proxy.
    doublers=0.
    for n in set(row["part"] for row in notches):
        if not is_secondary(n):continue
        orig=base[n]
        rem=max(0.,orig-vol(all_s[n]))
        if rem>0:doublers+=1.5*rem/orig*book_mass[n]
    core_original=sum(p["mass_t"] for p in cells)
    core_after=sum(book_mass[n] for n in all_s if n.startswith("S1:water_"))
    core_lost=core_original-core_after
    source_S1=J["states"]["S1"]["mass_t"]
    mass=source_S1-(5.0-args.fuel_t)-core_lost+doublers
    # Full-ECON fuel energy ledger, source S4 12.640766441867TW
    # fusion per 11.361TW jet, source 353TJ/kg D-He3 energy.
    # House reserve is an explicit PROVISIONAL scenario decision,
    # not a sourced Wayfarer mission duration/qualification.
    heat=json.loads((Path(__file__).parent/"pinned_main_lab"/"torch_heat_results.json").read_bytes())
    s4=next(q for q in heat["steps"] if q["id"]=="S4")
    jet_tw=11.361
    fusion_to_jet=s4["fusion_tw"]/jet_tw
    energy_per_kg_remass=.5*(I["canon"]["torch_ve_km_s"]["ECON"]*1000.)**2
    specific_fuel_energy=I["ship_power"]["fuel_specific_fusion_j_kg"]
    full_econ_DHe3_t=core_after*1000*energy_per_kg_remass*fusion_to_jet/specific_fuel_energy/1000
    unused_house_DHe3_t=args.fuel_t-full_econ_DHe3_t
    fuel_covers_full_econ_and_house=(unused_house_DHe3_t+1.e-10>=args.house_reserve_t)
    if core_after>250.+1.e-5:
        violations.append(dict(blocked="source 250t remass exceeded",actual=core_after))
    econ=3000*math.log(mass/(mass-core_after))
    # G3 source S1 bookkeeping, recomputed from each actual BRep solid's
    # centroid and retained mass. This is a point-mass CG/trim screen, not
    # a full seven-state inertia or validated 5g structural analysis.
    srcCG=J["states"]["S1"]["cg_m"]
    pmom=[source_S1*x for x in srcCG]
    summed_mass=source_S1
    for key,shape in old_parts.items():
        m=old_mass[key]
        co=centroid(shape)
        pmom=[pmom[i]-m*co[i] for i in range(3)]
        summed_mass-=m
    for key,shape in all_s.items():
        m=book_mass[key]
        co=centroid(shape)
        pmom=[pmom[i]+m*co[i] for i in range(3)]
        summed_mass+=m
    # Doubler mass from physically removed secondary material, retained
    # source structural mass plus 1.5x added support; centroid provisionally
    # at the parent part. Placement solids remain OPEN until fitted.
    for key in set(row["part"] for row in notches):
        if not is_secondary(key):continue
        dmass=1.5*max(0.,base[key]-vol(all_s[key]))/base[key]*book_mass[key]
        co=centroid(all_s[key])
        pmom=[pmom[i]+dmass*co[i] for i in range(3)]
        summed_mass+=dmass
    if abs(summed_mass-mass)>0.002:
        violations.append(dict(blocked="source mass and BRep changed-part accounting disagree",
                               ledger_mass_t=mass,centroid_mass_t=summed_mass))
    newcg=[v/summed_mass for v in pmom]
    off=J["thrust_line_offset_m"]
    lateral=math.hypot(newcg[1]-off["y"],newcg[2]-off["z"])
    trim=math.degrees(math.atan2(lateral,I["torch"]["thrust_point_x_m"]-newcg[0]))
    G3screen=dict(S1_CG_m=[round(v,9) for v in newcg],
                  shift_vs_source_CG_m=[round(newcg[i]-srcCG[i],9) for i in range(3)],
                  S1_trim_deg=round(trim,8),
                  source_trim_S1_deg=J["states"]["S1"]["trim_deg"],
                  source_G3_max_deg=C["G3"]["trim_max_deg"],
                  pass_S1_point_mass_trim=trim<=C["G3"]["trim_max_deg"],
                  seven_state_inertia_slew_qualified=False,
                  doubler_centroids_approximate=True)
    # Exact authoritative ea50354 standard-library ray kernel, pinned
    # byte-for-byte in this research-only project. The baseline is SOURCE
    # analytic; each changed physical solid is the actual new #156 BRep.
    # No source main edits, no dose qualification or displaced mass credit.
    sys.path.insert(0,str((Path(__file__).parent/"pinned_main_lab").resolve()))
    import build_v05 as BM
    import certify as CC
    class CandidateRayShape:
        def __init__(self,shape):
            self.s=shape
            b=P.bounds(shape)
            self.b=((b[0],b[1]),(b[2],b[3]),(b[4],b[5]))
        def contains(self,x,y,z):
            return bool(self.s.is_inside((x,y,z),1e-7))
        def bbox(self):return self.b
    origitems=[];newitems=[]
    changes={x["part"] for x in movement+notches}
    spread_fraction=CC.committed_shield_fraction(I,J)
    for scope,parts in (("dry",J["parts"]),("S5",J["fluids_by_state"]["S5"])):
        for idx,p in enumerate(parts):
            if "shuttle" in p["tags"] and I["states"]["S5"]["shuttle"]=="absent":continue
            if p["volume_m3"]<=0:continue
            m=CC.committed_shield_mass(p,spread_fraction)
            if m<=0:continue
            orig=BM.shape_from_spec(p["shape"])
            baseline_density=m/p["volume_m3"]
            origitems.append((orig,baseline_density,orig.bbox()))
            name="dry:"+p["id"] if scope=="dry" else f"S1:{p['id']}:{idx:02d}"
            if name not in all_s:continue
            if name in changes:
                updated=CandidateRayShape(all_s[name])
                density=(1.0 if scope=="S5" and p["id"].startswith(("jacket_","pw_service"))
                         else baseline_density)
                newitems.append((updated,density,updated.bbox()))
            else:newitems.append((orig,baseline_density,orig.bbox()))
    shelter=next(r for r in J["rooms"] if r["kind"]=="shelter")
    ssh=shelter["shape"]
    rm=(ssh["r0"]+ssh["r1"])/2;am=math.radians((ssh["a0"]+ssh["a1"])/2)
    origins=[
      ((ssh["x0"]+ssh["x1"])/2,rm*math.cos(am),rm*math.sin(am)),
      (ssh["x0"]+0.3,(ssh["r1"]-0.3)*math.cos(am),(ssh["r1"]-0.3)*math.sin(am)),
      (ssh["x1"]-0.3,(ssh["r0"]+0.3)*math.cos(math.radians(ssh["a0"]+10)),
       (ssh["r0"]+0.3)*math.sin(math.radians(ssh["a0"]+10)))]
    N=C["G6"]["rays"];step=C["G6"]["ray_step_m"];tmax=C["G6"]["ray_max_m"]
    oldmin=float("inf");newmin=float("inf");points=[]
    for oi,o in enumerate(origins):
        om=float("inf");nm=float("inf")
        for i in range(N):
            z=1-2*(i+.5)/N
            rr=math.sqrt(1-z*z)
            ph=i*math.pi*(3-math.sqrt(5))
            dd=(z,rr*math.cos(ph),rr*math.sin(ph))
            vo=CC.ray_density(o,dd,origitems,step,tmax)
            vn=CC.ray_density(o,dd,newitems,step,tmax)
            om=min(om,vo);nm=min(nm,vn)
        oldmin=min(oldmin,om);newmin=min(newmin,nm)
        points.append(dict(origin_index=oi,source_min_g_cm2=round(om,8),
                           candidate_min_g_cm2=round(nm,8)))
        print("G6 AUTHORITATIVE RAY",oi,om,nm,flush=True)
    if abs(oldmin-53.39034860482293)>.01:
        violations.append(dict(blocked="pinned source G6 baseline mismatch",oldmin=oldmin))
    if newmin<C["G6"]["shelter_min_g_cm2"]:
        violations.append(dict(blocked="candidate G6 below source 40g/cm2 screen",newmin=newmin))
    g6screen=dict(source_original_g_cm2=round(oldmin,8),
                  candidate_changed_BRep_g_cm2=round(newmin,8),
                  source_threshold_g_cm2=C["G6"]["shelter_min_g_cm2"],
                  source_kernel="exact copied pinned ea50354 build_v05.py and certify.py",
                  sample="S5 shelter; 3 origins x 600 directions; 2cm",
                  scenario_minima=points,
                  numeric_shelter_screen_pass=newmin>=C["G6"]["shelter_min_g_cm2"],
                  unlocated_secondary_doublers_shield_credit_zero=True,
                  radiation_transport_qualification=False)
    # conservative: source 4t decrease; jacket net unchanged, only fluid
    # normalization; CG unknown for additional notch material reinforcements.
    g8=P.make_g8(I,C,{k[4:]:s for k,s in all_s.items() if k.startswith("dry:")})
    report=dict(status="PHASE1A LAB CANDIDATE; NO QUALIFICATION; CREDIT ZERO",
        source_geometry_sha256=P.SOURCE_HASH,
        input_sha256=hashlib.sha256((src/"inputs_base.json").read_bytes()).hexdigest(),
        D8_primary_untouched=True,
        source_original_D_hits=150,
        final_all_installed_pair_intersections_over_0p01_m3=len(allhits),
        final_category_d_hits=len(d),final_category_d=d,
        pair_count=len(all_s)*(len(all_s)-1)//2,all_intersections=allhits,
        candidate_moves=movement,
        notches=notches,
        aggregate_notch_losses=list(per_notch.values()),
        flagged_over5pct=[x for x in per_notch.values() if x["FLAG_over5"]],
        blockers=violations,
        D1=dict(original_source5t_fuel_proxy_m3=oldfuel["volume_m3"],
                requested_DHe3_t=args.fuel_t,
                four_lobes_target_m3=fuel_target,
                four_t_target_m3=fuel_target,real_four_lobe_BRep_m3=fuel_actual,
                dry_tank_caps_m3=shell_volume,
                core_full_gross_BRep_m3=core_gross,
                source_unlocated_internal_structure_m3=J["tank_structure"]["displaced_m3"],
                core_net_BRep_after_debit_m3=core_net,
                original_core_water_rendered_m3=sum_water_rendered,
                displaced_core_water_BRep_m3=waterloss,
                source_required_ullage_fraction=I["tanks"]["ullage_fraction"],
                ullage_basis=("G1 5 percent of WATER LIQUID volume" if args.g1_liquid_ullage else "OLD 5 percent of net core volume historical replay"),
                required_ullage_fraction_of_liquid=(required_ullage/max_core_water_m3),
                physical_core_water_liquid_m3=physical_water_t,
                required_core_ullage_m3=required_ullage,
                actual_core_ullage_m3=actual_ullage_m3,
                max_core_water_m3=max_core_water_m3,
                BRep_proxy_water_envelope_per_actual_t=water_envelope_per_physical_t,
                source_water_liquid_density_t_m3=1.0,
                candidate_core_water_occupied_m3=final_core_water_m3,
                source_core_water_ullage_in_previous_candidate_m3=core_net-fuel_actual-shell_volume-(sum_water_rendered-deficit),

                core_remass_after_t=core_after,core_remass_lost_t=core_lost,
                note="G1 source physical water density 1t/m3; B-rep water shape has 1.0185m3 per booked t due to unlocated web/baffle proxy. Net core cap separately debits 5.870m3 structural volume; no double charge."),
        D2=dict(envelopes=d2_envelopes,
                courier_forward_hazard_pivot=bool(args.courier_forward),
                location=("courier EXTERNAL FORWARD x14-17.5m/r4.6-6.1m/az235-305; "
                          "service arm x14-17.5m/r2-4.3m/az225-315"
                          if args.courier_forward else
                          "courier AFT x35-39m/r2.8-4.5m/az225-315; service arm x14-17.5m/r2-4.3m/az225-315"),
                no_payload_hold_displaced=True,
                aft_carrier_attachment_and_thermal_fit_qualified=False,
                new_external_mount_and_view_factor_qualification=False),
        bow_no_render_proxy_boxes=crown,
        bow_viewer_excludes_source_no_render_tags=True,
        D5=dict(source_booked_protected_t=50,jacket_original_booked_t=jbook,
                jacket_unique_BRep_t=junique,service_booked_t=book_mass[service],
                jacket_to_service_moved_t=jlost,
                unique_protected_after_primary_cut_t=protected_end,
                protected_water_shortfall_after_cut_t=protected_deficit),
        house_fuel_ledger=dict(
            source_fusion_to_jet_ratio=fusion_to_jet,
            source_DHe3_specific_energy_J_kg=specific_fuel_energy,
            full_ECON_core_remass_t=core_after,
            full_ECON_DHe3_required_t=full_econ_DHe3_t,
            house_DHe3_reserve_t=args.house_reserve_t,
            house_DHe3_remaining_after_full_ECON_t=unused_house_DHe3_t,
            meets_full_ECON_plus_house=fuel_covers_full_econ_and_house,
            house_reserve_is_provisional_not_canon=True,
            reason="0.10t declared lab reserve, not a source-mandated mission duration"),
        masses=dict(source_S1_t=source_S1,source_dry_t=J["dry_t"],
                    source_mass_change_t=mass-source_S1,
                    secondary_doubler_added_t=doublers,
                    candidate_S1_t=mass,
                    source_R_t=250,core_R_t=core_after,
                    ideal_ECON_km_s=econ,
                    passes_kT_700_floor=econ>=700,
                    passes_G2_692p55_floor=econ>=692.55,
                    delta_vs_700_km_s=econ-700.,
                    delta_vs_G2_692p55_km_s=econ-692.55,
                    kT_700_floor_shortfall_km_s=max(0.,700-econ),
                    remaining_mass_headroom_t=core_after*math.exp(700/3000)/(math.exp(700/3000)-1)-mass),
        G8=g8,
        G6=g6screen,
        G3=G3screen,
        credit=dict(mass_t=0,dv_km_s=0,shielding=0,canon=False),
        candidate_pass=not d and not violations and econ>=700 and fuel_covers_full_econ_and_house)
    (out/"candidate_report.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("FINAL d",len(d),"VIOLATIONS",len(violations),
          "FLAG OVER5",len(report["flagged_over5pct"]),
          "R LOST",core_lost,"ECON",econ,"Doubler t",doublers,flush=True)
    if args.export:
        # Export editable solids, which are a candidate only; never imply
        # their source proxy's density or structural notch is qualified.
        for n,s in all_s.items():s.label=n;s.color=None
        export_step(Compound(children=list(all_s.values())),
                    out/"candidate.step",unit=Unit.M,timestamp="2026-11-08T00:00:00")
        # The source marks crown_* 7m boxes and other allocation placeholders
        # no_render; they must NOT be mistakenly visualized as bow hardware.
        view_shapes=[]
        dry_by_id={p["id"]:p for p in J["parts"]}
        for n,shape in all_s.items():
            if n.startswith("dry:") and "no_render" in dry_by_id.get(n[4:],{}).get("tags",[]):
                continue
            shape.color=Color("#7E9BAF" if n.startswith("S1") else "#A8A8A8")
            view_shapes.append(shape)
        export_gltf(Compound(children=view_shapes),
                    out/"candidate.glb",unit=Unit.M,binary=True,
                    linear_deflection=.05,angular_deflection=.3)
    # Fails candidate PASS without deleting evidence; blocker causes STOP.
    if not report["candidate_pass"]:
        raise SystemExit("LAB CANDIDATE HOLD: no zero-conflict certified packing claim")
if __name__=="__main__":main()
