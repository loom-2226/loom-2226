#!/usr/bin/env python3
"""#471 finish C0 with B's approved PV surface result and unchanged K.audit for others."""
import json
import time
import d9_sharded as S

PRESSURE="dry:pressure_vessel"

def main():
    start=time.monotonic()
    G,I,C,R,rebuilt,geo_sha,step_sha=S.context()
    p=json.loads((S.OUT/"pressure.json").read_text())
    assert p["mode"]=="pressure" and p["check"]["name"]==PRESSURE
    assert p["geometry_sha256"]==geo_sha and p["step_sha256"]==step_sha
    assert p["unit_factor"]==.001 and p["source_offset_m"]==[.03,-.26]
    assert p["check"]["integrity_method"]=="two_way_BRep_surface_sample_distance"
    assert p["check"]["raw_boolean_numerically_invalid"] is True
    assert p["check"]["surface_distance"]["two_way_max_deviation_m"]<=C["D9"]["primary_brep_unchanged_bbox_tolerance_m"] or p["pass"] is False
    assert p["check"]["surface_distance"]["native_to_imported"]["samples"]>=S.K.MIN_SURFACE_SAMPLES_EACH_WAY
    assert p["check"]["surface_distance"]["imported_to_native"]["samples"]>=S.K.MIN_SURFACE_SAMPLES_EACH_WAY
    rows,shapes,installed,factor=S.imported(G)
    names=S.primary_names(shapes)
    assert len(names)==43
    chosen=names[0::4]
    assert len(chosen)==11 and PRESSURE in chosen
    checks=[]
    for name in chosen:
        print("C0_PRIMARY_START",name,flush=True)
        if name==PRESSURE:
            check=dict(p["check"])
            check["reused_same_source_B_surface_result"]=True
        else:
            try:check=S.single_primary(name,rows,shapes,C)
            except Exception as exc:check=dict(name=name,diagnostic_error=repr(exc),pass_=False)
            if "pass_" in check:check["pass"]=check.pop("pass_")
        checks.append(check)
        print("C0_PRIMARY_DONE",name,"pass",check.get("pass"),flush=True)
    result=dict(mode="primary",shard=0,shards=4,
                geometry_sha256=geo_sha,step_sha256=step_sha,
                source_offset_m=[.03,-.26],unit_factor=factor,
                total_primaries=43,names=chosen,checks=checks,
                runtime_seconds=round(time.monotonic()-start,3),
                pass_=all(x.get("pass") is True for x in checks))
    result["pass"]=result.pop("pass_")
    S.save("primary-0.json",result)
    print("C0_SHARD_RESULT",json.dumps(dict(pass_=result["pass"],
         count=len(checks),runtime_seconds=result["runtime_seconds"])),flush=True)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
