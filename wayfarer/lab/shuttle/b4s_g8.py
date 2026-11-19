#!/usr/bin/env python3
"""Actual authored mesh check for rolled B4-S stowage. Existing G8 criteria."""
import json,sys,math,hashlib
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
sys.path.insert(0,str(HERE/"v2_lifting_body"))
import build_b4s as B
I=json.load(open(ROOT/"config/wayfarer_v05_inputs.json"))
C=json.load(open(ROOT/"config/cert_criteria.json"))["G8"]
G=json.load(open(ROOT/"results/out/wayfarer_v05_geometry.json"))
S=I["shuttle"];Bay=I["bay"]
h=json.load(open(HERE/"v2_lifting_body/b4s_source_hull.json"))
sha=hashlib.sha256((HERE/"v2_lifting_body/viewer/glb/b4s_flight.glb").read_bytes()).hexdigest()
assert h["exact_visual_glb_sha256"]==sha
assert h["roll_deg"]==S["b4s_roll_deg"]==90
assert G["dry_t"]==868.1922552640087
sh=next(p for p in G["parts"] if p["id"]=="shuttle")
assert sh["shape"]["k"]=="polyhull" and sh["shape"]["source_hash"]==sha
assert abs(sh["mass_t"]-36.48)<1e-8
assert S["docked_dry_limit_t"]==37.0
assert S["x_m"]==[18.75,31.55]
assert I["service"]["tunnel"]["segments"][-1]["to"]==[18.75,0,0]
min_sill=min(abs(it["y_m"])-it["d_m"]/2 for it in I["longerons"]["items"] if it["kind"]=="tube" and it["z_m"]>0)
results={}
for state in ("flight","venus"):
 model=B.shuttle(state)
 V=np.vstack([p[0] for p in model.values()])
 y_rolled=-V[:,2];z_rolled=V[:,1]
 hw=float(np.max(np.abs(y_rolled)))
 r=float(np.max(np.hypot(y_rolled,z_rolled)))
 cl=Bay["slot_half_width_m"]-hw
 lon=min_sill-hw
 fwd=min(V[:,0])+S["x_m"][0]-Bay["x_m"][0]
 aft=Bay["x_m"][1]-(max(V[:,0])+S["x_m"][0])
 radial=Bay["bore_r_m"]-r
 results[state]=dict(parts=len(model),stowed_halfwidth_m=hw,radius_m=r,
                     slot_clearance_m=cl,longeron_clearance_m=lon,
                     bay_bore_clearance_m=radial,forward_axial_m=fwd,aft_axial_m=aft,
                     PASS=bool(cl>=C["path_clearance_min_m"] and lon>=C["path_clearance_min_m"] and
                           radial>=C["radial_clearance_min_m"] and fwd>=C["axial_clearance_min_m"] and
                           aft>=C["axial_clearance_min_m"]-1e-9))
 assert results[state]["PASS"],(state,results[state])
 assert abs(hw-S["b4s_"+("stowed" if state=="flight" else "venus")+"_halfwidth_m"])<1e-4
assert abs(results["flight"]["radius_m"]-h["stowed_radius_m"])<1e-9
assert C["path_clearance_min_m"]==.5 and C["radial_clearance_min_m"]==.25
berth=S["b4s_berth"]
load=37e3*berth["ultimate_g"]*9.80665/1e6
cap=berth["cradle_count"]*berth["latch_allow_tension_mn_each"]
stress=(load/berth["cradle_count"])/berth["effective_shear_area_m2_each"]
assert cap>=load and stress<=berth["allowable_shear_mpa"]
report=dict(source_geometry_sha256=hashlib.sha256((ROOT/"results/out/wayfarer_v05_geometry.json").read_bytes()).hexdigest(),
            states=results,berth_load_mn=load,berth_latch_capacity_mn=cap,
            berth_ultimate_shear_mpa=stress,berth_allowable_shear_mpa=berth["allowable_shear_mpa"],
            sh_standard_dry_t=36.48,venus_kit_payload_mid_t=15.17,
            unchanged_G8_criteria=C,pass_=True)
report["pass"]=report.pop("pass_")
out=ROOT/"results/out/B4S_ROLLED_DOCKED_REAL_G8.json"
out.write_text(json.dumps(report,indent=2)+"\n")
print("B4S_ROLLED_REAL_G8",json.dumps(report),flush=True)
