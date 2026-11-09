#!/usr/bin/env python3
"""kT DOCKED shuttle v1: first-source REAL BRep G8 stop gate.

This is the earliest independently sufficient blocker, not a substitute for
full G8. In docked config the distinct magnetic-nozzle ring is always
installed and visible; stop immediately if its true torus BRep breaks aft G8.
The single kT-authorised visual nozzle-ring station change 12.72→12.70 is allowed. Never resize, move, hide, clip, or waive another source v1 component to get PASS.
"""
from __future__ import annotations
import hashlib,json,math,re,sys
from pathlib import Path
from build123d import Solid,Plane

ROOT=Path(__file__).resolve().parents[2]
VIEWER=ROOT/"render/shuttle/wayfarer_shuttle_v1_viewer.html"
GEOM=ROOT/"results/out/wayfarer_v05_geometry.json"
INPUT=ROOT/"config/wayfarer_v05_inputs.json"
RESULT=ROOT/"render/out/wayfarer_shuttle_v1_docked_real_G8_gate.json"
EXPECTED="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"

source=VIEWER.read_text()
gbytes=GEOM.read_bytes()
assert hashlib.sha256(gbytes).hexdigest()==EXPECTED
G=json.loads(gbytes)
I=json.loads(INPUT.read_text())
# Verify exact source expressions, never unconstrained/ad-hoc positions.
assert "const X=s=>6.4-s;" in source
assert "const ring=new THREE.Mesh(new THREE.TorusGeometry(.78,.1,14,48)" in source
assert "ring.rotation.y=Math.PI/2;ring.position.x=X(12.70);ship.add(ring);" in source
assert "const POD0=new THREE.Vector3(X(5.45),.08,0)" in source
assert I["shuttle"]["length_m"]==12.8
assert I["shuttle"]["x_m"]==[18.75,31.55]
assert I["bay"]["x_m"]==[18.25,32.05]
assert abs(G["dry_t"]-868.1922552640087)<1e-9
shuttle_source=next(q for q in G["parts"] if q["id"]=="shuttle")
assert abs(shuttle_source["mass_t"]-30.732248081255836)<1e-7
# JS local X = 6.4-s, nose toward positive local X; in DOCKED ship
# the nose is x18.75. Thus world x=18.75+s. Torus normal is
# ship x because viewer rotates the default torus by Pi/2 about Y.
s=12.70
major=.78
minor=.1
world_x=I["shuttle"]["x_m"][0]+s
ring=Solid.make_torus(major,minor,plane=Plane(origin=(world_x,0,0),
                                      x_dir=(0,1,0),z_dir=(1,0,0)))
assert ring is not None and ring.is_valid and float(ring.volume)>0
bb=ring.bounding_box()
x_max=float(bb.max.X)
aft_clearance_m=I["bay"]["x_m"][1]-x_max
min_aft=I["shuttle"]["x_m"][1]-I["shuttle"]["x_m"][0] # 12.8
min_required=0.5
# The booked source hull itself ends at 31.55, which just meets 0.5m.
# The ring MAY NOT be ignored because it is a true installed docked
# shuttle component, regardless of same 30.7322t allocation.
result={
 "status":"G8_STOP_SHUTTLE_PART" if aft_clearance_m<min_required-1e-6 else "G8_PART_PASS_CONTINUE_FULL_SCREEN",
 "part":"shuttle_v1/magnetic_nozzle_ring",
 "source_file":"wayfarer/render/shuttle/wayfarer_shuttle_v1_viewer.html",
 "source_threejs":"TorusGeometry(.78,.1,14,48), rotation.y=Pi/2, ring.position.x=X(12.70), X(s)=6.4-s",
 "source_geometry_sha256":EXPECTED,
 "source_shuttle_mass_t":shuttle_source["mass_t"],
 "mass_rebooking_t":0,
 "configuration":"DOCKED, no Venus kit geometry outside source mass",
 "real_BRep":"OCC torus, major radius 0.78m, minor radius 0.10m, normal x",
 "ring_center_world_x_m":world_x,
 "real_BRep_max_world_x_m":x_max,
 "bay_aft_end_x_m":I["bay"]["x_m"][1],
 "measured_G8_aft_axial_clearance_m":aft_clearance_m,
 "required_G8_aft_axial_clearance_m":min_required,
 "shortfall_m":max(0,min_required-aft_clearance_m),
 "ship_source_aft_clearance_m":I["bay"]["x_m"][1]-I["shuttle"]["x_m"][1],
 "uncut_hull_and_existing_doors":True,
 "geometry_adjustment_allowed":"Only kT-approved nozzle-ring station 12.72→12.70; other parts unchanged",
 "further_geometry_export_authorised":aft_clearance_m>=min_required-1e-6,
}
RESULT.parent.mkdir(parents=True,exist_ok=True)
RESULT.write_text(json.dumps(result,indent=2)+"\n")
print("SHUTTLE_V1_REAL_BREP_G8",json.dumps(result),flush=True)
if result["status"]=="G8_STOP_SHUTTLE_PART":
    raise SystemExit("STOP kT: DOCKED shuttle magnetic-nozzle ring fails G8 aft clearance; do not fix")
