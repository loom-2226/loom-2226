#!/usr/bin/env python3
"""kT 2026-11-10: BRep gate before authoring internal-hold solids.

STOP on pod/hatch fit failure or real nearest strake distance <0.5m.
Only source geometry and kT approved dimensions; no thermal credit.
"""
from pathlib import Path
import json,math,hashlib,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from packing_phase1b import source_brep_pilot as P
from build123d import Solid,Color

EXPECTED="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
HATCH_AXIAL=(14.25,15.75)
HATCH_CLEAR_TANGENT_M=3.6
MIN_STRAKE_CLEARANCE_M=0.5
OUT=ROOT/"render/out/internal_hold_fit_v256.json"

def box(x0,x1,y0,y1,z0,z1):
    return P.make(dict(k="box",x0=x0,x1=x1,y0=y0,y1=y1,z0=z0,z1=z1))
def overlap(a,b):
    if P.bbox_intersection_upper(P.bounds(a),P.bounds(b))<=1e-8:return 0.
    c=a & b
    return 0. if c is None else float(c.volume)
def outside(a,b):
    c=a-b
    return 0. if c is None else float(c.volume)
def gap(a,b):
    if hasattr(a,"distance_to"):
        return float(a.distance_to(b))
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    tool=BRepExtrema_DistShapeShape(a.wrapped,b.wrapped);tool.Perform()
    assert tool.IsDone()
    return float(tool.Value())

raw=(ROOT/"results/out/wayfarer_v05_geometry.json").read_bytes()
assert hashlib.sha256(raw).hexdigest()==EXPECTED
geom=json.loads(raw)
cfg=json.loads((ROOT/"config/wayfarer_v05_inputs.json").read_text())
decision=json.loads((ROOT/"config/kt_decisions.json").read_text())
approved=decision["drone_crawler_internal_hold_approved_2026_11_10"]
assert approved["decision"]=="KT_APPROVED_INTERNAL_PAYLOAD_HOLD_TRUE_SOLID_IMPLEMENTATION"
rows={v["id"]:v for v in geom["parts"]}
hold_stbd=P.make(dict(k="sector",x0=14,x1=17,r0=2,r1=4.3,a0=-45,a1=45))
hold_port=P.make(dict(k="sector",x0=14,x1=17,r0=2,r1=4.3,a0=135,a1=225))
# At both azimuths the pod's 3.4m dimension is tangential.
# Mars stowed x14.35-15.45, r2.4-3.5; dense x15.65-16.55,r2.5-3.4.
parts={}
for side,sign,hold,mars,dense in (
    ("starboard",1,hold_stbd,0,2),("port",-1,hold_port,1,3)):
    yf=lambda lo,hi:(lo,hi) if sign==1 else (-hi,-lo)
    for k,xx,yy,tan in (
        (mars,(14.35,15.45),(2.4,3.5),3.4),
        (dense,(15.65,16.55),(2.5,3.4),2.9)):
        yl,yh=yf(*yy)
        parts[f"dry:internal_drone_{k}"]=box(*xx,yl,yh,-tan/2,tan/2)
    # Low-profile cradle under the inboard radial face, neither duplicating
    # nor intersecting the original drone's source booked mass.
    for k,xx,yy,tan in (
        (mars,(14.37,15.43),(2.33,2.39),3.30),
        (dense,(15.67,16.53),(2.43,2.49),2.80)):
        yl,yh=yf(*yy)
        parts[f"dry:internal_cradle_{k}"]=box(*xx,yl,yh,-tan/2,tan/2)
    crawler=([0] if side=="starboard" else [1,2])
    zcent=[0] if side=="starboard" else [-.88,.88]
    for k,zc in zip(crawler,zcent):
        yl,yh=yf(3.76,3.91)
        parts[f"dry:internal_crawler_{k}"]=box(16.17,16.97,yl,yh,zc-.3,zc+.3)
# Both hatches are circular-hull-following apertures, not incorrect
# constant-y boxes. Clear chord 3.6m at R4.5 => half-angle asin(1.8/4.5).
half=math.degrees(math.asin(HATCH_CLEAR_TANGENT_M/(2*4.5)))
hatches={}
for side,center in (("starboard",0),("port",180)):
    spec=dict(k="sector",x0=14.25,x1=15.75,r0=4.35,r1=4.60,
              a0=center-half,a1=center+half)
    hatches[side]=P.make(spec)
# Source strake solids are the certified installed 2m-wide folded footprints.
# Check both rails near either hold as installed source BReps.
strakes={str(a):P.make(rows[f"strake_{a}"]["shape"])
         for a in (40,140,220,320)}
strake_gaps={side:{name:round(gap(hatch,s),6) for name,s in strakes.items()}
             for side,hatch in hatches.items()}
pod_outside=[]
for n,s in parts.items():
    hold=hold_port if n.endswith(("_1","_3")) else hold_stbd
    v=outside(s,hold)
    if v>1e-5:pod_outside.append(dict(id=n,outside_m3=v))
frame_hits={}
for side,hatch in hatches.items():
    frame_hits[side]={frame:round(overlap(hatch,P.make(rows[frame]["shape"])),9)
                      for frame in ("frame_14","frame_16")}
all_gaps=[v for d in strake_gaps.values() for v in d.values()]
min_gap=min(all_gaps)
fit_pass=not pod_outside and all(v<=1e-7 for d in frame_hits.values() for v in d.values())
clearance_pass=min_gap>=MIN_STRAKE_CLEARANCE_M
report=dict(
    status="PASS" if (fit_pass and clearance_pass) else "HOLD_REQUIRED_BY_KT",
    source_sha256=EXPECTED,layout="2 existing holds; 2 Mars + 2 dense-air; 3 crawlers",
    pod_and_cradle_solids=len(parts),
    adopted_hatch_x_m=list(HATCH_AXIAL),
    adopted_hatch_chord_m=HATCH_CLEAR_TANGENT_M,
    actual_curved_shell_half_angle_deg=half,
    strake_clearance_m=strake_gaps,
    min_strake_clearance_m=min_gap,
    required_min_strake_clearance_m=MIN_STRAKE_CLEARANCE_M,
    real_strake_clearance_pass=clearance_pass,
    pod_and_cradle_hold_outside=pod_outside,
    frame_intersections_m3=frame_hits,
    pod_and_frame_fit_pass=fit_pass,
    no_source_or_mass_changes=True)
OUT.parent.mkdir(exist_ok=True,parents=True)
OUT.write_text(json.dumps(report,indent=2)+"\n")
print("INTERNAL_HOLD_BREP_GATE",json.dumps(report),flush=True)
if not fit_pass: raise SystemExit("STOP kT: pod/cradle or hatch frame fit FAILED")
if not clearance_pass: raise SystemExit("STOP kT: actual hatch-strake gap <0.5m")
