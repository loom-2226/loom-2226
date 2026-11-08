#!/usr/bin/env python3
"""#471 kT surface-first pressure recovery, approved distance method only.

Uses unchanged source STEP transform, native/imported BRepCheck and the exact
K._directed_distance in BOTH directions before validity and final verdict.
Previously proven numerically invalid ordinary Boolean is reused only with
identical source geometry + compressed STEP hash. Fuzzy OCCT is not rerun.
No geometry or tolerance changes.
"""
import argparse
import hashlib
import json
import math
import time
from datetime import datetime, timezone

import d9_sharded as S

K, P = S.K, S.P
PATH = S.OUT / "pressure_stages.json"
FINAL = S.OUT / "pressure.json"

# Prior Actions job #128643535358, source hashes and ordinary Boolean
# independently recorded in its immutable log. This is NOT a new result.
PROVEN_RUN_ID = 42452063347
PROVEN_GEOMETRY_SHA = "88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
PROVEN_STEP_SHA = "71e1d65a13872b01a7e656eccca16f6380e3074e947edb04febc4f118b97d31c"
PROVEN_COMMON_M3 = -0.0028914016068082304
PROVEN_SYM_M3 = 22.719074845884716



def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def mark(stage, part, result):
    print("B_DIAG", stamp(), "stage="+stage, "part="+part,
          "result="+str(result), flush=True)


def signed_invalid(cv, sv, v1, v2):
    return (cv is None or sv is None or not math.isfinite(cv) or
            not math.isfinite(sv) or cv < -K.NUMERIC_VOLUME_MARGIN_M3 or
            cv > min(v1, v2)+K.NUMERIC_VOLUME_MARGIN_M3 or
            sv > v1+v2+K.NUMERIC_VOLUME_MARGIN_M3 or
            sv < -K.NUMERIC_VOLUME_MARGIN_M3)


def persist(state):
    S.OUT.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def load(sha, step_sha):
    if PATH.exists():
        state=json.loads(PATH.read_text())
        assert state["geometry_sha256"]==sha and state["step_sha256"]==step_sha
        return state
    return dict(geometry_sha256=sha,step_sha256=step_sha,
                stages={},name="dry:pressure_vessel",
                source_offset_m=[.03,-.26])


def finish(state, C, factor, started):
    stages=state["stages"]
    names=("forward","reverse","validity")
    if not all(n in stages and stages[n].get("result")=="COMPLETE" for n in names):
        mark("final","incomplete","MISSING_STAGES "+str([n for n in names if
              n not in stages or stages[n].get("result")!="COMPLETE"]))
        return False
    validity=stages["validity"]["data"]
    fwd=stages["forward"]["data"]
    rev=stages["reverse"]["data"]
    v1,v2=validity["native_volume_m3"],validity["imported_volume_m3"]
    vol_delta=validity["volume_delta_m3"]
    bbox_delta=validity["bbox_delta_m"]
    # Reuse *previously measured* impossible Boolean only for byte-identical
    # STEP and geometry; no OCCT Boolean is executed in this recovery run.
    commonv=PROVEN_COMMON_M3
    sym=PROVEN_SYM_M3
    invalid=signed_invalid(commonv,sym,v1,v2)
    assert invalid and sym>v1+v2, "previous Boolean must remain physically impossible"
    assert C["D9"]["primary_brep_symmetric_difference_limit_m3"]==1e-5
    bbox_tol=C["D9"]["primary_brep_unchanged_bbox_tolerance_m"]
    assert bbox_tol==1e-6
    ordinary_pass=False
    fuzzy_pass=False
    max_distance=max(fwd["max_deviation_m"],rev["max_deviation_m"])
    pass_distance=max_distance<=bbox_tol
    surface_pass=bool(invalid and pass_distance)
    diags=validity["diagnostics"]
    valid_sides=all(diags[k]["brepcheck_valid"] for k in ("native","imported"))
    any_fix=any("valid_after" in diags[k]["shapefix"] for k in ("native","imported"))
    geometry_pass=(vol_delta<=1e-5 and bbox_delta<=bbox_tol)
    orient_same=(diags["native"]["face_orientation_counts"]==diags["imported"]["face_orientation_counts"]
                 and diags["native"]["solid_orientation_counts"]==diags["imported"]["solid_orientation_counts"]
                 and diags["native"]["signed_volume_m3"]>0 and diags["imported"]["signed_volume_m3"]>0)
    enough_samples=(fwd["samples"]>=K.MIN_SURFACE_SAMPLES_EACH_WAY and
                    rev["samples"]>=K.MIN_SURFACE_SAMPLES_EACH_WAY)
    accepted=bool(geometry_pass and valid_sides and not any_fix and orient_same and
                  enough_samples and invalid and surface_pass)
    check=dict(
        name="dry:pressure_vessel",
        vol_native_m3=round(v1,8),vol_approved_m3=round(v2,8),
        volume_delta_m3=round(vol_delta,9),bbox_delta_m=round(bbox_delta,9),
        diagnostics=diags,raw_boolean=dict(common_volume_m3=commonv,
            symmetric_difference_m3=sym,previous_run_id=PROVEN_RUN_ID,
            not_rerun=True),
        raw_boolean_numerically_invalid=invalid,
        fuzzy_boolean=dict(skipped=True,reason="kT: prior ordinary Boolean numerically invalid; use approved surface method"),
        surface_distance=dict(
            native_to_imported=fwd,imported_to_native=rev,
            two_way_max_deviation_m=max_distance,
            bounded_sample_not_global_hausdorff=True,
            tolerance_m=bbox_tol,pass_distance=pass_distance),
        integrity_method=(
            "ordinary_symmetric_difference" if ordinary_pass else
            "OCCT_fuzzy_symmetric_difference" if fuzzy_pass else
            "two_way_BRep_surface_sample_distance" if surface_pass else "FAIL"),
        pass_=accepted,fallback_authority_applied=surface_pass,
        symmetric_difference_m3=round(sym,9) if sym is not None else None,
    )
    check["pass"]=check.pop("pass_")
    report=dict(mode="pressure",shard=0,shards=1,
                geometry_sha256=state["geometry_sha256"],
                step_sha256=state["step_sha256"],unit_factor=factor,
                source_offset_m=[.03,-.26],
                runtime_seconds=round(time.monotonic()-started,3),
                check=check,passed=accepted,pass_=accepted,
                stage_runtime_seconds={n:stages[n]["runtime_seconds"] for n in names})
    report["pass"]=report.pop("pass_")
    S.save("pressure.json",report)
    mark("final","pressure","PASS" if accepted else "FAIL")
    print("B_PRESSURE_MEASUREMENTS",json.dumps(check,sort_keys=True),flush=True)
    return accepted


def run(phase):
    started=time.monotonic()
    mark(phase,"stage","START")
    G,I,C,R,rebuilt,sha,step_sha=S.context()
    assert sha==PROVEN_GEOMETRY_SHA and step_sha==PROVEN_STEP_SHA, (
        "current geometry or STEP differs from proven ordinary Boolean source; must not reuse")
    state=load(sha,step_sha)
    if phase=="finalize":
        assert state["source_offset_m"]==[.03,-.26]
        verdict=finish(state,C,.001,started)
        mark(phase,"stage","COMPLETE PV_PASS="+str(verdict))
        return 0
    mark(phase,"STEP_import","START")
    rows,shapes,installed,factor=S.imported(G)
    native=P.make(P.settled(rows["dry:pressure_vessel"]["shape"]))
    imported=shapes["dry:pressure_vessel"]
    mark(phase,"STEP_import","COMPLETE factor="+str(factor))
    data={}
    try:
        if phase=="validity":
            v1,v2=float(native.volume),float(imported.volume)
            data=dict(native_volume_m3=v1, imported_volume_m3=v2,
                      volume_delta_m3=abs(v1-v2),
                      bbox_delta_m=max(abs(a-b) for a,b in zip(P.bounds(native),P.bounds(imported))),
                      diagnostics={})
            for name,shape in (("native",native),("imported",imported)):
                mark(phase,"BRepCheck_"+name,"START")
                data["diagnostics"][name]=K._validity(shape)
                mark(phase,"BRepCheck_"+name,"COMPLETE "+json.dumps(data["diagnostics"][name],sort_keys=True))
        elif phase=="forward":
            mark(phase,"native_to_imported","START")
            data=K._directed_distance(native,imported)
            mark(phase,"native_to_imported","COMPLETE samples="+str(data["samples"])+" max_m="+str(data["max_deviation_m"]))
        elif phase=="reverse":
            mark(phase,"imported_to_native","START")
            data=K._directed_distance(imported,native)
            mark(phase,"imported_to_native","COMPLETE samples="+str(data["samples"])+" max_m="+str(data["max_deviation_m"]))
        else:
            raise ValueError(phase)
        state["stages"][phase]=dict(result="COMPLETE",runtime_seconds=round(time.monotonic()-started,3),data=data)
    except Exception as exc:
        state["stages"][phase]=dict(result="ERROR",runtime_seconds=round(time.monotonic()-started,3),error=repr(exc))
        mark(phase,"stage","ERROR "+repr(exc))
    persist(state)
    mark(phase,"stage",state["stages"][phase]["result"]+" elapsed_s="+str(state["stages"][phase]["runtime_seconds"]))
    return 0  # Preserve negative/incomplete diagnostic evidence. E must enforce PASS.


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("phase",choices=("forward","reverse","validity","finalize"))
    a=parser.parse_args()
    raise SystemExit(run(a.phase))
