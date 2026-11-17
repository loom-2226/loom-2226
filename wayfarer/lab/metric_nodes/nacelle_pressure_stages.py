#!/usr/bin/env python3
"""#561 two-state #559 pressure recovery. Strict existing D9 criteria.

Two STEP states each get their own independent imported pressure BRep validity,
>=256 exact boundary samples BOTH ways, plus same 1um criterion.
Only reuse #559's *historical invalid Boolean* when canonical serialized
approved and candidate pressure BReps are byte-identical (SHA256). Otherwise
run current ordinary Boolean; never reuse a prior PASS or waive a failure.
Stages are independent GitHub Actions jobs with checkpoint artifacts.
"""
import argparse, gc, hashlib, json, math, pathlib, sys, time
from OCP.BRepTools import BRepTools

HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import nacelle_d9_pair as N
K,P=N.K,N.P
PV="dry:pressure_vessel"
OUT=N.OUT
OLD_BOOL=dict(common_volume_m3=-0.0028914016068082304,
              symmetric_difference_m3=22.719074845884716,
              previous_run_id=42452063347)
SOURCE_STEP_SHA="71e1d65a13872b01a7e656eccca16f6380e3074e947edb04febc4f118b97d31c"
def checkpoint_path(state):return OUT/state/"pressure_stages.json"
def get(state):
    G,G0,I,C,prior,sig=N.validate()
    p=checkpoint_path(state)
    x=N.read(p) if p.exists() else dict(state=state,geometry_sha=N.sha(N.GEO),
        candidate_step_sha=N.sha(N.CAND/f"candidate_{state}.step.gz"),
        source_step_sha=N.sha(N.SOURCE),original_fingerprint=sig,stages={})
    assert x["state"]==state and x["geometry_sha"]==N.sha(N.GEO)
    assert x["candidate_step_sha"]==N.sha(N.CAND/f"candidate_{state}.step.gz")
    assert x["source_step_sha"]==N.sha(N.SOURCE)==SOURCE_STEP_SHA
    assert x["original_fingerprint"]==sig
    assert C["D9"]["primary_brep_unchanged_bbox_tolerance_m"]==1e-6
    assert K.MIN_SURFACE_SAMPLES_EACH_WAY>=256
    return x,G,G0,C
def save(state,x):N.save(checkpoint_path(state),x)
def logged(state,stage,data):
    x,*_=get(state)
    x["stages"][stage]=data
    save(state,x)
    print("PRESSURE_CHECKPOINT",state,stage,json.dumps(data)[:2000],flush=True)
def imported(state,G0):
    shapes,factor=N.import_candidate(state,G0)
    assert factor==.001
    imp=shapes[PV]
    native=P.make(P.settled(N.BASE.catalogue(G0)[PV]["shape"]))
    return native,imp
def fingerprint(shape,tag):
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".brep",delete=False) as f:path=pathlib.Path(f.name)
    try:
        assert BRepTools.Write_s(shape.wrapped,str(path))
        raw=path.read_bytes()
        return dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
    finally:path.unlink(missing_ok=True)
def run(state,stage):
    start=time.monotonic()
    x,G,G0,C=get(state)
    t=C["D9"]["primary_brep_unchanged_bbox_tolerance_m"]
    print("PRESSURE_STAGE_START",state,stage,flush=True)
    if stage=="source_fingerprint":
        rows,shapes,installed,factor=N.D.imported(G0)
        assert factor==.001
        p=fingerprint(shapes[PV],"approved")
        p.update(reference="PR #559 source STEP",factor=factor)
        logged(state,stage,p)
        return 0
    if stage=="candidate_fingerprint":
        shapes,factor=N.import_candidate(state,G0)
        assert factor==.001
        p=fingerprint(shapes[PV],state)
        approved=x["stages"]["source_fingerprint"]
        p.update(reference="state candidate STEP",factor=factor,
                 byte_identical_to_approved=p["sha256"]==approved["sha256"])
        logged(state,stage,p)
        return 0
    if stage=="forward":
        native,imp=imported(state,G0)
        result=K._directed_distance(native,imp)
        assert result["samples"]>=256 and result["min_samples_each_way"]>=256
        result["duration_s"]=round(time.monotonic()-start,3)
        logged(state,stage,result)
        return 0
    if stage=="reverse":
        native,imp=imported(state,G0)
        result=K._directed_distance(imp,native)
        assert result["samples"]>=256 and result["min_samples_each_way"]>=256
        result["duration_s"]=round(time.monotonic()-start,3)
        logged(state,stage,result)
        return 0
    if stage=="validity":
        native,imp=imported(state,G0)
        v1,v2=float(native.volume),float(imp.volume)
        result=dict(native_volume_m3=v1,imported_volume_m3=v2,
                    volume_delta_m3=abs(v1-v2),
                    bbox_delta_m=max(abs(a-b) for a,b in zip(P.bounds(native),P.bounds(imp))),
                    diagnostics={})
        for label,shape in (("native",native),("imported",imp)):
            print("PRESSURE_BREPCHECK",state,label,flush=True)
            result["diagnostics"][label]=K._validity(shape)
        result["duration_s"]=round(time.monotonic()-start,3)
        logged(state,stage,result)
        return 0
    if stage=="boolean":
        same=x["stages"]["candidate_fingerprint"]["byte_identical_to_approved"]
        if same:
            result=dict(OLD_BOOL,not_rerun=True,
                        evidence="byte-identical pressure BRep (SHA256); #559 historical numerically invalid ordinary Boolean",
                        measured_against_sha256=x["stages"]["candidate_fingerprint"]["sha256"])
        else:
            native,imp=imported(state,G0)
            from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
            from OCP.GProp import GProp_GProps
            from OCP.BRepGProp import BRepGProp
            op=BRepAlgoAPI_Common(native.wrapped,imp.wrapped)
            op.Build()
            assert op.IsDone(),"ordinary BRep Common not done"
            props=GProp_GProps()
            BRepGProp.VolumeProperties_s(op.Shape(),props,True,False)
            cv=float(props.Mass())
            result=dict(common_volume_m3=cv,
                        symmetric_difference_m3=float(native.volume)+float(imp.volume)-2*cv,
                        not_rerun=False,evidence="new candidate BRep: ordinary Boolean recomputed")
        result["duration_s"]=round(time.monotonic()-start,3)
        logged(state,stage,result)
        return 0
    if stage!="finalize":raise ValueError(stage)
    names=("source_fingerprint","candidate_fingerprint","forward","reverse","validity","boolean")
    assert all(n in x["stages"] for n in names),[n for n in names if n not in x["stages"]]
    valid=x["stages"]["validity"];fwd=x["stages"]["forward"];rev=x["stages"]["reverse"]
    bo=x["stages"]["boolean"];a,b=valid["native_volume_m3"],valid["imported_volume_m3"]
    cv,sy=bo["common_volume_m3"],bo["symmetric_difference_m3"]
    invalid=(not math.isfinite(cv) or not math.isfinite(sy) or
             cv < -K.NUMERIC_VOLUME_MARGIN_M3 or
             cv > min(a,b)+K.NUMERIC_VOLUME_MARGIN_M3 or
             sy>a+b+K.NUMERIC_VOLUME_MARGIN_M3 or sy < -K.NUMERIC_VOLUME_MARGIN_M3)
    good_distance=max(fwd["max_deviation_m"],rev["max_deviation_m"])<=t
    enough=fwd["samples"]>=256 and rev["samples"]>=256
    diag=valid["diagnostics"]
    valid_sides=all(diag[k]["brepcheck_valid"] for k in ("native","imported"))
    no_shape_fix=not any("valid_after" in diag[k]["shapefix"] for k in ("native","imported"))
    orientations=(diag["native"]["face_orientation_counts"]==diag["imported"]["face_orientation_counts"]
        and diag["native"]["solid_orientation_counts"]==diag["imported"]["solid_orientation_counts"]
        and diag["native"]["signed_volume_m3"]>0 and diag["imported"]["signed_volume_m3"]>0)
    shape_ok=(valid["volume_delta_m3"]<=1e-5 and valid["bbox_delta_m"]<=t)
    ordinary=not invalid and sy<=C["D9"]["primary_brep_symmetric_difference_limit_m3"]
    surface=invalid and good_distance
    passed=bool(valid_sides and no_shape_fix and orientations and shape_ok and enough and good_distance and (ordinary or surface))
    integrity="ordinary_symmetric_difference" if ordinary else "two_way_BRep_surface_sample_distance" if surface else "FAIL"
    check=dict(name=PV,vol_native_m3=round(a,8),vol_approved_m3=round(b,8),
      volume_delta_m3=round(valid["volume_delta_m3"],9),
      bbox_delta_m=round(valid["bbox_delta_m"],9),diagnostics=diag,
      raw_boolean=bo,raw_boolean_numerically_invalid=invalid,
      surface_distance=dict(native_to_imported=fwd,imported_to_native=rev,
                            two_way_max_deviation_m=max(fwd["max_deviation_m"],rev["max_deviation_m"]),
                            bounded_sample_not_global_hausdorff=True,
                            tolerance_m=t,pass_distance=good_distance),
      integrity_method=integrity,pass_=passed,fallback_authority_applied=bool(surface),
      symmetric_difference_m3=round(sy,9))
    check["pass"]=check.pop("pass_")
    report=dict(state=state,mode="pressure",geometry_sha=x["geometry_sha"],
      candidate_step_sha=x["candidate_step_sha"],original_fingerprint=x["original_fingerprint"],
      source_step_sha=x["source_step_sha"],source_offset_m=[.03,-.26],unit_factor=.001,
      pressure_brep_sha256=x["stages"]["candidate_fingerprint"]["sha256"],
      approved_pressure_brep_sha256=x["stages"]["source_fingerprint"]["sha256"],
      byte_identical_to_approved=x["stages"]["candidate_fingerprint"]["byte_identical_to_approved"],
      check=check,pass_=passed)
    report["pass"]=report.pop("pass_")
    N.save(OUT/state/"pressure.json",report)
    print("PRESSURE_STAGE_FINAL",state,"PASS" if passed else "FAIL",
          "IDENTICAL",report["byte_identical_to_approved"],
          "MAX_DEVIATION",check["surface_distance"]["two_way_max_deviation_m"],flush=True)
    return 0 if passed else 1
def main():
    a=argparse.ArgumentParser()
    a.add_argument("stage",choices=("source_fingerprint","candidate_fingerprint","forward","reverse","validity","boolean","finalize"))
    a.add_argument("--state",choices=N.STATES,required=True)
    q=a.parse_args()
    raise SystemExit(run(q.state,q.stage))
if __name__=="__main__":main()
