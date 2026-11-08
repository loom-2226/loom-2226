#!/usr/bin/env python3
"""#471 B pressure only: time-bounded execution stages of the existing K.audit.

Uses the SAME imported STEP transform, BRepCheck, VolumeProperties,
BRepAlgoAPI_Common, _fuzzy_common and _directed_distance as K.audit.
Stages persist results to permit partial evidence after a later timeout.
No changes to geometry, physical CAD operation, classification, or tolerance.
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
    names=("validity","booleans","forward","reverse")
    if not all(n in stages and stages[n].get("result")=="COMPLETE" for n in names):
        mark("final","incomplete","MISSING_STAGES "+str([n for n in names if
              n not in stages or stages[n].get("result")!="COMPLETE"]))
        return False
    validity=stages["validity"]["data"]
    bools=stages["booleans"]["data"]
    fwd=stages["forward"]["data"]
    rev=stages["reverse"]["data"]
    v1,v2=validity["native_volume_m3"],validity["imported_volume_m3"]
    vol_delta=validity["volume_delta_m3"]
    bbox_delta=validity["bbox_delta_m"]
    commonv=bools.get("common_volume_m3")
    sym=bools.get("symmetric_difference_m3")
    invalid=signed_invalid(commonv,sym,v1,v2)
    fuzzy=bools.get("fuzzy_boolean",{})
    fuzzy_valid=(fuzzy and not fuzzy.get("numerically_invalid",True)
                 and "symmetric_difference_m3" in fuzzy)
    tol=C["D9"]["primary_brep_symmetric_difference_limit_m3"]
    bbox_tol=C["D9"]["primary_brep_unchanged_bbox_tolerance_m"]
    ordinary_pass=bool(not invalid and sym is not None and sym<=tol)
    fuzzy_pass=bool(invalid and fuzzy_valid and fuzzy["symmetric_difference_m3"]<=tol)
    max_distance=max(fwd["max_deviation_m"],rev["max_deviation_m"])
    pass_distance=max_distance<=bbox_tol
    surface_pass=bool(invalid and pass_distance)
    diags=validity["diagnostics"]
    valid_sides=all(diags[k]["brepcheck_valid"] for k in ("native","imported"))
    any_fix=any("valid_after" in diags[k]["shapefix"] for k in ("native","imported"))
    geometry_pass=(vol_delta<=1e-5 and bbox_delta<=bbox_tol)
    accepted=bool(geometry_pass and valid_sides and not any_fix and
                  (ordinary_pass or fuzzy_pass or surface_pass) and pass_distance)
    check=dict(
        name="dry:pressure_vessel",
        vol_native_m3=round(v1,8),vol_approved_m3=round(v2,8),
        volume_delta_m3=round(vol_delta,9),bbox_delta_m=round(bbox_delta,9),
        diagnostics=diags,raw_boolean=bools["raw_boolean"],
        raw_boolean_numerically_invalid=invalid,
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
    if "fuzzy_boolean" in bools:
        check["fuzzy_boolean"]=fuzzy
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
    state=load(sha,step_sha)
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
        elif phase=="booleans":
            v1,v2=float(native.volume),float(imported.volume)
            mark(phase,"ordinary_COMMON","START")
            try:
                common=native & imported
                commonv=0. if common is None else float(common.volume)
                sym=v1+v2-2*commonv
                raw=dict(common_volume_m3=commonv,symmetric_difference_m3=sym)
            except Exception as exc:
                commonv=None;sym=None
                raw=dict(error=repr(exc))
            mark(phase,"ordinary_COMMON","COMPLETE "+json.dumps(raw))
            data=dict(raw_boolean=raw, common_volume_m3=commonv,
                      symmetric_difference_m3=sym)
            if signed_invalid(commonv,sym,v1,v2) or sym>C["D9"]["primary_brep_symmetric_difference_limit_m3"]:
                mark(phase,"OCCT_fuzzy_COMMON","START fuzzy_value_m="+str(K.FUZZY_M))
                try:
                    fuzzy=K._fuzzy_common(native,imported)
                    if fuzzy.get("is_done"):
                        fv=fuzzy["common_volume_m3"]
                        fs=v1+v2-2*fv
                        fuzzy["symmetric_difference_m3"]=fs
                        fuzzy["numerically_invalid"]=signed_invalid(fv,fs,v1,v2)
                except Exception as exc:
                    fuzzy=dict(fuzzy_value_m=K.FUZZY_M,error=str(exc),numerically_invalid=True)
                data["fuzzy_boolean"]=fuzzy
                mark(phase,"OCCT_fuzzy_COMMON","COMPLETE "+json.dumps(fuzzy))
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
    if phase=="reverse":
        finish(state,C,factor,started)
    return 0  # Preserve negative/incomplete diagnostic evidence. E must enforce PASS.


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("phase",choices=("validity","booleans","forward","reverse"))
    a=parser.parse_args()
    raise SystemExit(run(a.phase))
