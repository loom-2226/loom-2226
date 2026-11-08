#!/usr/bin/env python3
"""Two bounded, collision-checked options for all seven rigid crown spare panes.

Each 2.6×1.9×0.0186m bay-wall envelope must wholly contain the selected
pre-existing 10mm pane geometry when rotated into the rack. The rack is a
clearance SCREEN only, not a newly massed piece of hardware.
"""
import hashlib,json,math,sys
from pathlib import Path
from build123d import Solid
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"lab"))
import d9_sharded as D
from crown_geom_v25 import make_pane
P=D.P
OUT=ROOT/"results/out/crown_seven_spares_bay_options.json"
G,I,C,R,rebuilt,sha,step_sha=D.context()
assert sha=="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
geo,shapes,installed,_=D.imported(G)
assert len(installed)==194
spare=next(x for x in G["parts"] if x["id"]=="crown_c_seven_spare_panes")
k=math.tan(math.radians(50))
p=I["habitat"]["decks"][0]["command_layout"]["crown_dome"]["shell_option_c"]["outer_tile_layer"]
types=[
 ("central",make_pane(0,.75,0,360,.01,k,center=True),1),
 ("flat_ring",make_pane(.75,2,0,30,.01,k),2),
 ("slope_inner",make_pane(2,2.75,0,30,.01,k),2),
 ("slope_outer",make_pane(2.75,3.5,15,45,.01,k),2)
]
rho=3.75
weights=[round(obj.volume*rho,12) for _,obj,n in types for _ in range(n)]
assert len(weights)==7
# Derived source bounds: max rigid longitudinal/chord, lateral/meridian,
# and local plate thickness. The axis-aligned racks exceed those maxima.
max_chord=max(1.5,2*3.5*math.sin(math.pi/12))
max_meridian=max(1.5,1.25,0.75/math.cos(math.radians(50)))
assert max_chord<2.6 and max_meridian<1.9
# Radial gap: shuttle reaches r1.9; liner starts r2.4.
# z<0 means against the actual closed lower bay wall, not its +z open slot.
x_ranges=((20.00,22.60),(27.00,29.60))
options=[]
for j,(xa,xb) in enumerate(x_ranges):
  stack=[]
  for i,m in enumerate(weights):
    low=-2.16+i*.0186
    high=low+.0186
    body=P.box(xa,xb,-.95,.95,low,high)
    assert body.is_valid
    assert min(math.hypot(-.95,low),math.hypot(.95,low))<=2.4
    # Entire rectangular volume is within the free bay bore:
    assert math.sqrt(.95**2+max(abs(low),abs(high))**2)<2.4
    assert min(abs(low),abs(high))>1.9
    conflicts=[]
    bb=P.bounds(body)
    for name in installed:
      if P.bbox_intersection_upper(bb,P.bounds(shapes[name]))<=0:continue
      common=body & shapes[name]
      if common and common.volume>1e-8:
        conflicts.append(dict(id=name,overlap_m3=float(common.volume)))
    stack.append(dict(id=f"crown_spare_{i+1:02d}",envelope_bounds_m=list(bb),
      mass_t=m,clashes=conflicts,centroid_m=[(xa+xb)/2,0,(low+high)/2]))
  assert all(not t["clashes"] for t in stack)
  mass=sum(weights)
  oldMass=spare["mass_t"]
  # Full replacement: retire booked spare allocation and charge actual pane
  # physical volume×ceramic density; effect excludes ship's other crown changes.
  baseMass=G["dry_t"]
  baseMoment=[sum(x["mass_t"]*x["centroid_m"][k] for x in G["parts"]) for k in range(3)]
  adjusted=baseMass-oldMass+mass
  newMom=[baseMoment[k]-oldMass*spare["centroid_m"][k]+
     sum(t["mass_t"]*t["centroid_m"][k] for t in stack) for k in range(3)]
  cgOld=[v/baseMass for v in baseMoment]
  cgNew=[v/adjusted for v in newMom]
  options.append(dict(label=("A: lower bay wall forward" if j==0 else
                               "B: lower bay wall aft"),x_m=[xa,xb],
     y_m=[-.95,.95],z_m=[-2.16,-2.03],
     candidate_spare_count=7,total_physical_mass_t=mass,
     retired_old_spare_allocation_t=oldMass,net_dry_mass_delta_t=mass-oldMass,
     dry_cg_before_m=cgOld,dry_cg_after_spares_only_m=cgNew,
     dry_cg_delta_spares_only_m=[cgNew[k]-cgOld[k] for k in range(3)],
     zero_clashes=all(not x["clashes"] for x in stack),
     permitted_source_exemptions=[],
     pane_envelopes=stack,
     packing_assumption="Rigid panes oriented longest chord along x, meridian span tangential, plate normals radial; each separately sleeved in a 18.6mm layer. Actual attachment hardware NOT modelled."
  ))
report=dict(source_sha256=sha,step_sha256=step_sha,
 density_t_m3=rho,max_hoop_chord_m=max_chord,max_meridian_span_m=max_meridian,
 using_installed_D9_solids=len(installed),
 old_hold_bbox=spare["shape"],options=options,
 qualification="SCREEN_ONLY: conservative full-box clearance; print fixtures and mounts NOT modelled",
 all_options_zero_clash=all(x["zero_clashes"] for x in options))
OUT.write_text(json.dumps(report,indent=2)+"\n")
for o in options:
  print("SEVEN_SPARES_OPTION",json.dumps({k:o[k] for k in
    ("label","total_physical_mass_t","net_dry_mass_delta_t","dry_cg_delta_spares_only_m","zero_clashes")}),flush=True)
assert report["all_options_zero_clash"]
