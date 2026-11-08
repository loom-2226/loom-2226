"""D9 Phase 1b shared installed-part B-rep check, researched solids as source.

The #157 named, cut STEP is the authority for *installed CAD*. The upstream
analytic geometry supplies state/mass, source part IDs, and no_render flags.
Both the reference and upstream checks below use the SAME installed part
set, category function and 0.01m3 threshold. No auto-notch or primary move.
"""
import argparse
import gzip
import hashlib
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE/"packing_phase1b"))
from build123d import import_step, Compound, Color, Unit, export_step, export_gltf
import source_brep_pilot as P
import source_brep_triage as T

GEO=ROOT/"results/out/wayfarer_v05_geometry.json"
INPUT=ROOT/"config/wayfarer_v05_inputs.json"
CRITERIA=ROOT/"config/cert_criteria.json"
SOURCE=HERE/"packing_phase1b/frozen_research_3p8_forward.step.gz"
REF=HERE/"packing_phase1b/frozen_research_3p8_forward.json"
REPORT=ROOT/"results/out/D9_BREP_CLASH_REPORT.json"

CELL_NAMES=("starboard_fore","starboard_aft","port_fore","port_aft")
RENAMES={
    **{f"dry:house_fuel_tank_cap_{i}":f"dry:house_fuel_tank_cap_{name}" for i,name in enumerate(CELL_NAMES)},
    **{f"S1:house_fuel_lobe_{i}:15":f"S1:house_fuel_lobe_{name}:{15+i}" for i,name in enumerate(CELL_NAMES)},
    "S1:c_lite_monoprop:16":"S1:c_lite_monoprop:19",
    **{f"dry:bay_corner_32_3_{side}":f"dry:bay_corner_32.3_{side}" for side in ("p","s")},
    **{f"dry:longeron_end_fitting_34_3_{pos}":f"dry:longeron_end_fitting_34.3_{pos}"
        for pos in ("lower_port","lower_starboard","upper_port","upper_starboard")},
}

def catalogue(G):
    rows={"dry:"+p["id"]:p for p in G["parts"]}
    rows.update({f"S1:{p['id']}:{i:02d}":p for i,p in enumerate(G["fluids_by_state"]["S1"])})
    return rows

def common_scan(installed,threshold):
    names=sorted(installed)
    bounds={n:P.bounds(installed[n]) for n in names}
    hits=[]
    errors=[]
    c=Counter()
    pairs=0
    for i,a in enumerate(names):
        for b in names[i+1:]:
            pairs+=1
            if P.bbox_intersection_upper(bounds[a],bounds[b])<=threshold:continue
            try:
                common=installed[a] & installed[b]
                if common is None:continue
                v=float(common.volume)
                if v<=threshold:continue
                cat,why=T.classify({"a":a,"b":b})
                assert cat in "abcd",(a,b,cat)
                hits.append(dict(a=a,b=b,m3=round(v,9),category=cat,why=why))
                c[cat]+=1
            except Exception as e:
                errors.append(dict(a=a,b=b,error=str(e)))
    return dict(part_count=len(names),pair_count=pairs,expected_pairs=len(names)*(len(names)-1)//2,
                category_counts=dict(c),
                category_d_count=sum(x["category"]=="d" for x in hits),
                category_d_conflicts=sorted([x for x in hits if x["category"]=="d"],key=lambda r:-r["m3"]),
                collision_errors=errors,intersection_hits=hits)

def trim_liquid_forward(shape,ratio):
    """Debit water volume ONLY, never fuel/steel: keep aft settled boundary."""
    if ratio>=1:return shape
    x0,x1,y0,y1,z0,z1=P.bounds(shape)
    target=float(shape.volume)*ratio
    lo,hi=x0,x1
    result=None
    # Search the fore-face clip plane; the remaining aft water is settled.
    for _ in range(20):
        cut=(lo+hi)*.5
        trial=shape & P.box(cut,x1+1.,y0-1.,y1+1.,z0-1.,z1+1.)
        v=0. if trial is None else float(trial.volume)
        if v>=target:
            lo=cut
        else:
            hi=cut
        result=trial
    cut=(lo+hi)*.5
    result=shape & P.box(cut,x1+1.,y0-1.,y1+1.,z0-1.,z1+1.)
    if result is None or abs(float(result.volume)-target)>.00004:
        raise RuntimeError(f"water BRep debit did not converge {float(shape.volume)} -> {target}")
    return result

def run(export=False):
    G=json.loads(GEO.read_text())
    I=json.loads(INPUT.read_text())
    C=json.loads(CRITERIA.read_text())
    R=json.loads(REF.read_text())
    geo_sha=hashlib.sha256(GEO.read_bytes()).hexdigest()
    source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    threshold=C["D9"]["min_intersection_m3"]
    assert abs(threshold-.01)<1e-12
    if geo_sha!=C["D9"]["approved_source_geometry_sha256"]:
        raise RuntimeError("D9 frozen CAD authority stale for changed upstream source geometry; REBUILD BRep, never inherit old PASS")
    rows=catalogue(G)
    installed_names={n for n,row in rows.items() if "no_render" not in row.get("tags",[])}
    excluded_names=set(rows)-installed_names
    with gzip.open(SOURCE,"rb") as rd,open("/tmp/loom_d9_approved_base.step","wb") as out:
        shutil.copyfileobj(rd,out)
    step=import_step("/tmp/loom_d9_approved_base.step")
    kids=list(step.children)
    raw_names=[k.label for k in kids]
    assert len(kids)==315 and len(set(raw_names))==315
    # #157 exported STEP with Unit.M. OCC importer returns numeric coordinates
    # in MM, while source build_v05 P.make() uses metre-valued coordinates.
    # Compare UNMOVED primary trunk longitudinal bounds and scale once.
    # Failing to do this makes mm3 intersections appear as m3.
    native_trunk=P.make(P.settled(rows["dry:core_trunk"]["shape"]))
    raw_trunk=next(k for k in kids if k.label=="dry:core_trunk")
    source_span=P.bounds(native_trunk)[1]-P.bounds(native_trunk)[0]
    imported_span=P.bounds(raw_trunk)[1]-P.bounds(raw_trunk)[0]
    unit_ratio=imported_span/source_span
    if abs(unit_ratio-1000)<.01: unit_factor=.001
    elif abs(unit_ratio-1)<.001: unit_factor=1.
    else:raise RuntimeError(f"STEP units mismatch: source/STEP core_trunk spans ratio {unit_ratio}")
    candidate={}
    for shape in kids:
        name=RENAMES.get(shape.label,shape.label)
        assert name not in candidate,name
        shape=shape.scale(unit_factor) if unit_factor!=1 else shape
        shape.label=name
        candidate[name]=shape
    # The only extra upstream part is D8's *unlocated* 0.660802t
    # allowance, not a physical installed solid.
    assert set(candidate)==set(rows)-{"dry:d8_unlocated_doubler_allowance"},dict(
        research_only=sorted(set(candidate)-set(rows)),
        upstream_only=sorted(set(rows)-set(candidate)))
    assert installed_names<=set(candidate)
    assert len(installed_names)==194 and len(excluded_names)==122

    original={name:candidate[name] for name in installed_names}
    before=common_scan(original,threshold)
    if before["category_d_count"] or before["collision_errors"]:
        print("RESEARCH_STEP_ROUNDTRIP_D9",json.dumps({
            "category_counts":before["category_counts"],
            "d":before["category_d_count"],
            "first_d":before["category_d_conflicts"][:35],
            "cad_errors":before["collision_errors"][:10],
            "modelled":before["part_count"],
            "pairs":before["pair_count"]
        }),flush=True)
        raise RuntimeError("research reference unexpectedly conflicts on shared 194-part D9 checker")

    # Preserve all original source primary structures exactly.
    primary_checks=[]
    for name in sorted(candidate):
        # Include primary tagged no_render end fittings and corners in the
        # NEVER MOVE check even though no_render never earns installed fit credit.
        if not name.startswith("dry:") or not (name[4:].startswith(("frame_","longeron_","bay_corner_")) or
                name[4:] in ("armor","pressure_vessel","aft_bulkhead","thrust_cone","core_trunk",
                              "docking_collar","shield","nozzle") or name[4:].startswith("tunnel_")):
            continue
        native=P.make(P.settled(rows[name]["shape"]))
        actual=candidate[name]
        delta=abs(float(native.volume)-float(actual.volume))
        bb_delta=max(abs(a-b) for a,b in zip(P.bounds(native),P.bounds(actual)))
        common=native & actual
        commonv=0. if common is None else float(common.volume)
        sym=max(0.,float(native.volume)+float(actual.volume)-2*commonv)
        primary_checks.append(dict(name=name,vol_native_m3=round(float(native.volume),8),
                                   vol_approved_m3=round(float(actual.volume),8),
                                   volume_delta_m3=round(delta,9),
                                   bbox_delta_m=round(bb_delta,9),
                                   symmetric_difference_m3=round(sym,9)))
        if (delta>1e-5 or
            bb_delta>C["D9"]["primary_brep_unchanged_bbox_tolerance_m"] or
            sym>C["D9"]["primary_brep_symmetric_difference_limit_m3"]):
            # STOP immediately, but write a current-source machine FAIL
            # so certify.py can NEVER inherit the prior volume-only pass.
            failure=dict(
                authority="kT D8 STOP: primary STEP import geometry mismatch",
                geometry_sha256=geo_sha,
                approved_source_step_gz_sha256=source_sha,
                imported_step_source_numeric_unit=("mm" if unit_factor==.001 else "m"),
                explicit_step_to_source_linear_scale=unit_factor,
                modelled_solids=len(installed_names),
                pair_count=before["pair_count"],
                expected_pairs=before["expected_pairs"],
                threshold_m3=threshold,
                category_d_count=before["category_d_count"],
                category_d_conflicts=before["category_d_conflicts"],
                lab_same_checker=before,
                same_lab_and_upstream_installed_part_set=True,
                source_dry_count=len(G["parts"]),
                source_S1_fluid_count=len(G["fluids_by_state"]["S1"]),
                excluded_source_no_render_proxy_count=len(excluded_names),
                D8_primary_shape_unchanged=False,
                primary_invariant_failures=[primary_checks[-1]],
                primary_shape_volume_checks=primary_checks,
                geometry_conversion_or_boolean_errors=[],
                pass_=False,
                STOP="Primary nozzle or another G5 member does not match its original BRep, even though the research/reference pairwise D9 collisions count is zero. Geometry NOT promoted.")
            failure["pass"]=failure.pop("pass_")
            REPORT.write_text(json.dumps(failure,indent=2)+"\n")
            print("D9_PRIMARY_STOP",json.dumps(primary_checks[-1]),flush=True)
            return 1

    prior_water=R["masses"]["core_R_t"]
    actual_water=I["states"]["S1"]["remass_t"]
    assert 0<actual_water<prior_water and abs(actual_water-245.39043171108221)<1e-7
    ratio=actual_water/prior_water
    migrated={}
    water_debits=[]
    for name,shape in candidate.items():
        if name.startswith("S1:water_"):
            pre=float(shape.volume)
            shape=trim_liquid_forward(shape,ratio)
            water_debits.append(dict(id=name,before_BRep_m3=pre,after_BRep_m3=float(shape.volume)))
        shape.label=name
        migrated[name]=shape

    installed={n:migrated[n] for n in installed_names}
    after=common_scan(installed,threshold)
    aligned=sorted(installed_names)==sorted(original)
    passed=(aligned and not after["category_d_count"] and not after["collision_errors"] and
            not before["category_d_count"] and len(primary_checks)>0)
    result=dict(authority="kT Phase1b approved installed geometry #157 STEP, same lab/upstream D9 classifier",
        geometry_sha256=geo_sha,
        approved_source_step_gz_sha256=source_sha,
        approved_source_brep_origin="loom-2226/loom-research-lab PR #157 approved 3.8t forward courier",
        original_D8_notch_ops=len(R["notches"]),
        D8_primary_shape_unchanged=True,
        primary_shape_volume_checks=primary_checks,
        source_dry_count=len(G["parts"]),source_S1_fluid_count=len(G["fluids_by_state"]["S1"]),
        imported_reference_names=len(candidate),
        source_brep_label_remaps=RENAMES,
        imported_step_source_numeric_unit="mm" if unit_factor==.001 else "m",
        source_geometry_numeric_unit="m",
        explicit_step_to_source_linear_scale=unit_factor,
        no_render_excluded=sorted(excluded_names),
        no_render_excluded_count=len(excluded_names),
        same_lab_and_upstream_installed_part_set=aligned,
        part_set=sorted(installed_names),
        threshold_m3=threshold,classification="source_brep_triage.classify pinned #156 shared single checker",
        lab_same_checker=before,
        upstream_same_checker=after,
        source_water_R_before_t=prior_water,source_water_R_current_t=actual_water,
        water_BRep_forward_debits=water_debits,
        category_d_count=after["category_d_count"],category_d_conflicts=after["category_d_conflicts"],
        geometry_conversion_or_boolean_errors=after["collision_errors"],pair_count=after["pair_count"],
        expected_pairs=after["expected_pairs"],modelled_solids=len(installed),
        pass_=passed,
        unresolved="Fitted D8 doubler, unlocated tank webs, cryogenic walls, no_render allocations and dynamic swept clearances remain OPEN."
    )
    result["pass"]=result.pop("pass_")
    REPORT.write_text(json.dumps(result,indent=1)+"\n")
    if export:
        dst=HERE/"packing_phase1b/approved_current_3p8_installed.step"
        export_step(Compound(children=[migrated[n] for n in sorted(migrated)]),dst,unit=Unit.M,timestamp="2026-11-08T00:00:00")
        with open(dst,"rb") as r,gzip.GzipFile(str(dst)+".gz","wb",mtime=0) as w:
            shutil.copyfileobj(r,w)
        dst.unlink()
        shapes=[]
        for n in sorted(installed):
            s=installed[n]
            s.color=Color("#78B7D2" if n.startswith("S1:") else "#9BA4AE")
            shapes.append(s)
        export_gltf(Compound(children=shapes),
            HERE/"packing_phase1b/approved_current_3p8_installed.glb",
            unit=Unit.M,binary=True,linear_deflection=.05,angular_deflection=.3)
    print("D9_SHARED",json.dumps(dict(sha=geo_sha,original_parts=len(candidate),
        installed_parts=len(installed),excluded=len(excluded_names),
        lab_d=before["category_d_count"],upstream_d=after["category_d_count"],
        errors=len(after["collision_errors"]),primary_count=len(primary_checks),
        pass_=passed)),flush=True)
    if after["category_d_count"]:
        print("D9_REMAINING",json.dumps(after["category_d_conflicts"][:15]),flush=True)
    return 0 if passed else 1

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--export",action="store_true")
    a=p.parse_args()
    raise SystemExit(run(export=a.export))
