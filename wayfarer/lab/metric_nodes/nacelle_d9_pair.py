#!/usr/bin/env python3
"""Two-state Wayfarer D9: same pinned 194 installed solids, unchanged 43
protected primaries and the SAME predicate/classifier/0.01m3 threshold.
Only 20 new source solids vary by state. Full before+water-debit pairs each.
Outputs two actual candidate STEPs and one strict paired certificate.
"""
import argparse
import gzip
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path
from collections import Counter

HERE=Path(__file__).resolve().parent
LAB=HERE.parents[0]
sys.path.insert(0,str(LAB))
import d9_sharded as D
import d9_brep as BASE
from nacelle_source_brep import make as make_nacelle
from build123d import Compound, Unit, export_step, import_step

P,T,K=D.P,D.T,D.K
ROOT=LAB.parent
GEO=ROOT/"results/out/wayfarer_v05_geometry.json"
INPUT=ROOT/"config/wayfarer_v05_inputs.json"
CRITERIA=ROOT/"config/cert_criteria.json"
OLD=HERE/"nacelle_candidates/base_geometry.json"
SOURCE=LAB/"packing_phase1b/current_g3_3p8_forward.step.gz"
CAND=HERE/"nacelle_candidates"
OUT=ROOT/"results/out/nacelle_d9"
STATES=("torch","Metric")
NEW_NAMES=tuple(sorted(
    [f"dry:metric_nacelle_{a}" for a in (0,90,180,270)]+
    [f"dry:metric_link_{a}_{j}" for a in (0,90,180,270) for j in (0,1)]+
    [f"dry:metric_arm_{a}_{s}" for a in (0,90,180,270) for s in ("minus","plus")]
))

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,o):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")

def validate():
    G,G0,I,C=read(GEO),read(OLD),read(INPUT),read(CRITERIA)
    assert G["inputs_sha256"]==sha(INPUT)
    assert G["thrust_line_offset_m"]["y"]==.03 and G["thrust_line_offset_m"]["z"]==-.26
    assert G["dry_t"]==G0["dry_t"] or abs(G["dry_t"]-G0["dry_t"])<1e-8
    assert C["D9"]["min_intersection_m3"]==.01
    old={p["id"]:p for p in G0["parts"]}
    new={p["id"]:p for p in G["parts"]}
    assert len(G["fluids_by_state"]["S1"])==len(G0["fluids_by_state"]["S1"])
    for a,b in zip(G["fluids_by_state"]["S1"],G0["fluids_by_state"]["S1"]):
        assert (a["id"],a["shape"],a["mat"],a["tags"])==(b["id"],b["shape"],b["mat"],b["tags"])
    assert set(new)-set(old)=={x[4:] for x in NEW_NAMES}
    assert set(old)-set(new)=={"metric_nacelles_ring_unlocated"}
    for n in set(old)&set(new):
        a,b=old[n],new[n]
        assert (a["shape"],a["mat"],a["tags"])==(b["shape"],b["mat"],b["tags"]),n
    phys=sorted(((p["id"],p["shape"],p["mat"],p["tags"])
                 for p in G["parts"]+G["fluids_by_state"]["S1"] if "no_render" not in p["tags"] and
                 "metric_nacelle" not in p["tags"]), key=lambda x:x[0])
    sig=hashlib.sha256(json.dumps(phys,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    assert len(phys)==194 and sig==C["D9"]["approved_installed_source_shapes_sha256"]
    prior=read(CAND/"proven_d9/wayfarer/results/out/D9_BREP_CLASH_REPORT.json")
    assert prior["pass"] is True and prior["category_d_count"]==0
    assert prior["pair_count"]==18721 and prior["D8_primary_shape_unchanged"] is True
    assert len(prior["primary_shape_volume_checks"])==43
    assert prior["geometry_sha256"]==sha(OLD)
    assert prior["approved_source_step_gz_sha256"]==sha(SOURCE)
    assert read(LAB/"packing_phase1b/current_g3_rebuild_report.json")["candidate_pass"] is True
    for state in STATES:
        rows=G["metric_states"][state]["parts"]
        assert len(rows)==20 and {"dry:"+x["id"] for x in rows}==set(NEW_NAMES)
    return G,G0,I,C,prior,sig

def normalise(kids,original):
    raw={s.label:s for s in kids}
    names={BASE.RENAMES.get(n,n) for n in raw}
    assert len(names)==len(kids)
    trunk_native=P.make(P.settled(original["dry:core_trunk"]["shape"]))
    trunk=next(s for s in kids if s.label=="dry:core_trunk")
    ratio=(P.bounds(trunk)[1]-P.bounds(trunk)[0])/(P.bounds(trunk_native)[1]-P.bounds(trunk_native)[0])
    if abs(ratio-1000)<.01:factor=.001
    elif abs(ratio-1)<.001:factor=1.
    else:raise RuntimeError("STEP metre/mm mismatch "+str(ratio))
    shapes={}
    for s in kids:
        name=BASE.RENAMES.get(s.label,s.label)
        if factor!=1:
            pos=s.location.position
            prior=(float(pos.X),float(pos.Y),float(pos.Z))
            s=s.scale(factor)
            after=s.location.position
            delta=tuple(prior[i]*factor-float(v) for i,v in enumerate((after.X,after.Y,after.Z)))
            if any(abs(v)>1e-12 for v in delta):s=s.translate(delta)
        s.label=name
        shapes[name]=s
    return shapes,factor

def build():
    G,G0,_,_,_,sig=validate()
    old_rows=BASE.catalogue(G0)
    # Shared exact baseline importer, already checked against approved #559 A STEP.
    rows,original,installed,factor=D.imported(G0)
    assert len(original)==315 and len(installed)==194
    CAND.mkdir(parents=True,exist_ok=True)
    checks={}
    for state in STATES:
        new={}
        for row in G["metric_states"][state]["parts"]:
            name="dry:"+row["id"]
            s=make_nacelle(row["shape"])
            assert s is not None and s.is_valid and s.volume>0,name
            s.label=name
            new[name]=s
        assert set(new)==set(NEW_NAMES)
        assembly=Compound(children=list(original.values())+list(new.values()))
        dest=CAND/f"candidate_{state}.step"
        export_step(assembly,str(dest),unit=Unit.M)
        with dest.open("rb") as source,(CAND/f"candidate_{state}.step.gz").open("wb") as out:
            with gzip.GzipFile(fileobj=out,mode="wb",mtime=0,filename="") as z:
                shutil.copyfileobj(source,z)
        dest.unlink()
        checks[state]=dict(step_sha=sha(CAND/f"candidate_{state}.step.gz"),
                           count=335,added=20)
        print("CANDIDATE_STEP",state,checks[state],flush=True)
    save(CAND/"candidate_manifest.json",dict(
        source_sha=sha(GEO),original_sha=sha(OLD),protected_fingerprint=sig,
        approved_source_step=sha(SOURCE),states=checks))
    return 0

def import_candidate(state,G0):
    src=CAND/f"candidate_{state}.step.gz"
    tmp=Path("/tmp")/f"loom_nacelle_{state}.step"
    with gzip.open(src,"rb") as f,tmp.open("wb") as out:shutil.copyfileobj(f,out)
    st=import_step(str(tmp))
    kids=list(st.children)
    assert len(kids)==335 and len({k.label for k in kids})==335
    original=BASE.catalogue(G0)
    shapes,factor=normalise(kids,original)
    assert set(shapes)==set(original)-{"dry:d8_unlocated_doubler_allowance",
                                     "dry:metric_nacelles_ring_unlocated"}|set(NEW_NAMES)
    return shapes,factor

def run_primary(state,shard,shards):
    assert shards==4 and 0<=shard<shards
    t=time.monotonic()
    G,G0,_,C,prior,sig=validate()
    shapes,factor=import_candidate(state,G0)
    rows=BASE.catalogue(G0)
    names=D.primary_names(shapes)
    assert len(names)==43
    chosen=names[shard::shards]
    checks=[]
    pressure=None
    if shard==0:
        pressure=read(OUT/state/"pressure.json")
        assert pressure["state"]==state and pressure["mode"]=="pressure"
        assert pressure["geometry_sha"]==sha(GEO)
        assert pressure["candidate_step_sha"]==sha(CAND/f"candidate_{state}.step.gz")
        assert pressure["original_fingerprint"]==sig and pressure["unit_factor"]==factor
        assert pressure["pass"] is True and pressure["check"]["pass"] is True
        assert pressure["check"]["name"]=="dry:pressure_vessel"
        assert pressure["check"]["surface_distance"]["native_to_imported"]["samples"]>=256
        assert pressure["check"]["surface_distance"]["imported_to_native"]["samples"]>=256
        assert pressure["check"]["surface_distance"]["two_way_max_deviation_m"]<=C["D9"]["primary_brep_unchanged_bbox_tolerance_m"]
        assert pressure["check"]["diagnostics"]["native"]["brepcheck_valid"]
        assert pressure["check"]["diagnostics"]["imported"]["brepcheck_valid"]
    for name in chosen:
        print("PRIMARY_START",state,shard,name,flush=True)
        if name=="dry:pressure_vessel":
            assert pressure is not None
            result=dict(pressure["check"])
            result["staged_B_pressure_evidence"]=True
        else:
            try:
                result=D.single_primary(name,rows,shapes,C)
            except Exception as e:
                result=dict(name=name,pass_=False,error=repr(e))
                result["pass"]=result.pop("pass_")
        checks.append(result)
        print("PRIMARY_END",name,result.get("pass"),flush=True)
    report=dict(state=state,mode="primary",shard=shard,shards=shards,
                geometry_sha=sha(GEO),candidate_step_sha=sha(CAND/f"candidate_{state}.step.gz"),
                prior_brep_step_sha=sha(SOURCE),original_fingerprint=sig,
                checks=checks,total_primaries=43,unit_factor=factor,
                runtime_s=round(time.monotonic()-t,2),
                pass_=all(x.get("pass") is True for x in checks))
    report["pass"]=report.pop("pass_")
    save(OUT/state/f"primary-{shard}.json",report)
    return 0 if report["pass"] else 1

def run_pairs(state,shard,shards):
    assert shards==8 and 0<=shard<shards
    t=time.monotonic()
    G,G0,I,C,prior,sig=validate()
    shapes,factor=import_candidate(state,G0)
    names=sorted(n for n in shapes if n in set(
        "dry:"+p["id"] for p in G0["parts"] if "no_render" not in p["tags"]) or
        n in set("S1:"+p["id"]+f":{i:02d}" for i,p in enumerate(G0["fluids_by_state"]["S1"])
                 if "no_render" not in p["tags"]) or n in NEW_NAMES)
    assert len(names)==214
    total=len(names)*(len(names)-1)//2
    assert total==22791
    lo,hi=total*shard//shards,total*(shard+1)//shards
    before=D.pair_scan(shapes,names,lo,hi,C["D9"]["min_intersection_m3"])
    ref=read(LAB/"packing_phase1b/frozen_research_3p8_forward.json")
    ratio=I["states"]["S1"]["remass_t"]/ref["masses"]["core_R_t"]
    post=dict(shapes)
    water=[]
    for name in names:
        if name.startswith("S1:water_"):
            old=post[name]
            post[name]=BASE.trim_liquid_forward(old,ratio)
            water.append((name,float(old.volume),float(post[name].volume)))
    after=D.pair_scan(post,names,lo,hi,C["D9"]["min_intersection_m3"])
    ok=all(not x["collision_errors"] and x["category_d_count"]==0 for x in (before,after))
    result=dict(state=state,mode="pairs",shard=shard,shards=shards,
                geometry_sha=sha(GEO),candidate_step_sha=sha(CAND/f"candidate_{state}.step.gz"),
                original_fingerprint=sig,unit_factor=factor,
                threshold_m3=.01,names_sha=hashlib.sha256("\n".join(names).encode()).hexdigest(),
                water_debit=water,range=[lo,hi],total_pairs=total,before=before,after=after,
                runtime_s=round(time.monotonic()-t,2),pass_=ok)
    result["pass"]=result.pop("pass_")
    save(OUT/state/f"pairs-{shard}.json",result)
    print("PAIRS_RESULT",state,shard,dict(pass_=ok,d_before=before["category_d_count"],d_after=after["category_d_count"],
                                        errors=len(before["collision_errors"])+len(after["collision_errors"])),flush=True)
    return 0 if ok else 1

def merge():
    G,G0,I,C,prior,sig=validate()
    manifest=read(CAND/"candidate_manifest.json")
    assert manifest["source_sha"]==sha(GEO) and manifest["original_sha"]==sha(OLD)
    states={}
    for state in STATES:
        primary=[read(OUT/state/f"primary-{i}.json") for i in range(4)]
        pairs=[read(OUT/state/f"pairs-{i}.json") for i in range(8)]
        step=sha(CAND/f"candidate_{state}.step.gz")
        for x in primary+pairs:
            assert x["state"]==state and x["geometry_sha"]==sha(GEO)
            assert x["candidate_step_sha"]==step and x["original_fingerprint"]==sig
            assert x["unit_factor"]==primary[0]["unit_factor"]
        checks=[x for row in primary for x in row["checks"]]
        assert len(checks)==43 and len({x["name"] for x in checks})==43
        assert sum(x["name"]=="dry:pressure_vessel" for x in checks)==1
        pressure=read(OUT/state/"pressure.json")
        assert pressure["pass"] is True and pressure["state"]==state
        assert pressure["geometry_sha"]==sha(GEO)
        assert pressure["candidate_step_sha"]==step
        assert pressure["original_fingerprint"]==sig
        assert pressure["check"]["pass"] is True
        pcheck=next(x for x in checks if x["name"]=="dry:pressure_vessel")
        assert pcheck.get("staged_B_pressure_evidence") is True
        assert all(pcheck[k]==pressure["check"][k] for k in pressure["check"])
        pos=0
        for i,row in enumerate(pairs):
            assert row["range"]==[pos,22791*(i+1)//8] and row["total_pairs"]==22791
            pos=row["range"][1]
        assert pos==22791
        assert len({row["names_sha"] for row in pairs})==1
        for attr in ("before","after"):
            assert sum(x[attr]["pair_count"] for x in pairs)==22791
        failures=[x for x in checks if x.get("pass") is not True]
        ds=[hit for row in pairs for hit in row["after"]["category_d_conflicts"]]
        errors=[e for row in pairs for e in row["after"]["collision_errors"]+row["before"]["collision_errors"]]
        passed=not failures and not ds and not errors and all(x.get("pass") is True for x in pairs)
        states[state]=dict(pass_=passed,step_gz_sha256=step,
                           primary_count=43,primary_failures=failures,
                           installed_original=194,installed_new=20,modelled_solids=214,
                           pairs=22791,threshold_m3=.01,
                           category_d_conflicts=ds,errors=errors,
                           primary_checks=checks,
                           swing_envelope="OPEN; non-D9 lab sweep only")
        states[state]["pass"]=states[state].pop("pass_")
        print("STATE_CERT",state,states[state]["pass"],"D",len(ds),"PRIMARY_FAIL",len(failures),flush=True)
    total=all(v["pass"] for v in states.values())
    report=dict(authority="kT 2026-11-17 two-state installed source D9",
                geometry_sha256=sha(GEO),approved_base_sha256=sha(OLD),
                approved_installed_source_shapes_sha256=sig,
                unchanged_D9_threshold_m3=C["D9"]["min_intersection_m3"],
                original_194_protected_brep_authority="PR #559 genuine certified D9; both new candidate STEPs independently tested against source",
                both_required=True,states=states,
                swing_envelope="OPEN; no D9 clearance claimed for mid-stroke",
                pass_=total)
    report["pass"]=report.pop("pass_")
    save(ROOT/"results/out/D9_NACELLE_TWO_STATE_REPORT.json",report)
    return 0 if total else 1

def main():
    a=argparse.ArgumentParser()
    a.add_argument("mode",choices=("build","primary","pairs","merge"))
    a.add_argument("--state",choices=STATES)
    a.add_argument("--shard",type=int,default=0)
    a.add_argument("--shards",type=int,default=1)
    x=a.parse_args()
    if x.mode=="build":return build()
    if x.mode=="merge":return merge()
    assert x.state
    if x.mode=="primary":return run_primary(x.state,x.shard,x.shards)
    return run_pairs(x.state,x.shard,x.shards)

if __name__=="__main__":
    raise SystemExit(main())
