"""Bounded I4 constrained-fit screen against source L1 annulus and ladder holes.

No hull redesign, no optimization framework. Actual source geometry sourced
directly from geometry.json, 6 role seats retained. Plan-plane footprint
tests only; not 3D body sweeps/4g qualification or full operational access.
"""
import json,math
from pathlib import Path
R=Path(__file__).resolve().parent.parent
g={x['id']:x['shape'] for x in json.loads((R/'out/wayfarer_v05_geometry.json').read_text())['parts']}
b=json.loads((R/'command/L1_I4_COMMAND_COMMONS_GEOMETRY_20261029.json').read_text())['design']
T=1.58;W=.70
positions={
 'PILOT':(-.98,-2.00,1.91,-5),
 'NAV':(0,2.50,2.76,0),
 'S1':(.98,-2.00,1.91,5),
 'S2':(-2.85,-.70,3.31,-28),
 'S3':(2.85,-.70,3.31,28),
 'S4':(2.45,-2.00,3.31,22)
}
ladders=[(-1.4,0),(1.4,0)]
def rotate_box(y,z,L,W,a):
 a=math.radians(a);u=(math.sin(a),-math.cos(a));v=(-u[1],u[0])
 return [(y+s*u[0]+t*v[0],z+s*u[1]+t*v[1])
       for s,t in [(-L/2,-W/2),(-L/2,W/2),(L/2,W/2),(L/2,-W/2)]]
def dist_box(px,py,y,z,L,W,a):
 a=math.radians(a);u=(math.sin(a),-math.cos(a));v=(-u[1],u[0])
 dx=px-y;dy=py-z;du=max(0,abs(dx*u[0]+dy*u[1])-L/2);dv=max(0,abs(dx*v[0]+dy*v[1])-W/2)
 return math.hypot(du,dv)
r0=g['floor_L1']['r0'];r1=g['floor_L1']['r1']
rows=[]
for sid,(y,z,x,hdg) in positions.items():
 pts=rotate_box(y,z,T,W,hdg)
 mx=max(math.hypot(*q) for q in pts)
 mn=dist_box(0,0,y,z,T,W,hdg)
 dl=min(dist_box(*q,y,z,T,W,hdg) for q in ladders)
 # Ladder shafts .4 radius, conservative .12m margin at this stage
 hard={'inside_outer_floor':mx<=r1,
       'outside_centre_hole':mn>=r0,
       'clear_source_ladder_shafts_plus_0p12m':dl>=.52}
 rows.append({'id':sid,'position_y_z_x_deg':[y,z,x,hdg],
   'max_corner_radius_m':round(mx,3),'min_body_footprint_radius_m':round(mn,3),
   'min_edge_to_ladder_centre_m':round(dl,3),'coarse_gates':hard})
# proposed room elements have explicit plan-footprint constraints
furniture=[
 ('mission_table',.40,-3.45,1.10,.63),
 ('workbench',-2.45,-2.18,1.38,.54),
 ('command_stand',-1.35,-3.55,.40,.36),
 ('engineering_cabinet',-3.45,1.10,.35,.70),
 ('sensors_cabinet',3.45,1.10,.35,.70),

]
for name,y,z,w,h in furniture:
 pts=rotate_box(y,z,w,h,0)
 # Rectangular furniture interior might have small trim at source circle
 rows.append({'id':name,'position_y_z_w_h':[y,z,w,h],
  'max_corner_radius_m':round(max(math.hypot(*q) for q in pts),3),
  'min_to_hole_m':round(dist_box(0,0,y,z,h,w,0),3),
  'min_to_ladder_centre_m':round(min(dist_box(*q,y,z,h,w,0) for q in ladders),3),
  'coarse_gates':{'inside_outer_floor':all(math.hypot(*q)<r1+1e-9 for q in pts),
       'outside_centre_hole':dist_box(0,0,y,z,h,w,0)>r0,
       'clear_source_ladder_shafts_plus_0p12m':min(dist_box(*q,y,z,h,w,0) for q in ladders)>=.52}})
# source original annular floor generated, not overlaid with I4 rectangle.
# Loft/terrace elevated: at (Y0,Z-1.96),3.40Yx2.10Z; lower NAV platform
# at (Y0,Z2.54),2.65Yx2.20Z. Both need footprint clipping to same ring.
r_terrace=[[-1.70,-3.01],[1.70,-3.01],[1.70,-.91],[-1.70,-.91]]
r_nav=[[-1.33,1.45],[1.33,1.45],[1.33,3.65],[-1.33,3.65]]
plates=[]
for name,poly,h in [('command_terrace',r_terrace,2.09),('nav_platform',r_nav,1.24)]:
 plates.append({'id':name,'corners':poly,'height_m':h,
   'max_corner_radius_m':max(math.hypot(*q) for q in poly),
   'coarse_hull_fit':all(math.hypot(*q)<=r1 for q in poly),
   'hole_conflict':'trim to source annulus r>=0.9' if min(math.hypot(*q) for q in poly)<r0 else 'no corner conflict'})
src=json.loads((R/'command/L1_I4_SOURCE_STRUCTURAL_CONTEXT_20261029.json').read_text())
out={'classification':'RESEARCH NON-CANON / PLAN-PLANE TEST ONLY',
 'source_geometry':{'pressure_vessel_radius_m':g['pressure_vessel']['R'],
       'floor_outer_radius_m':r1,'floor_central_opening_radius_m':r0,
       'original_ladder_positions_yz':ladders,'ladder_radius_m':.4},
 'seats':rows,'platforms':plates,
 'gates_pass_all':all(all(j['coarse_gates'].values()) for j in rows),
 'physical_open_issues':['No aisle clearance / full occupied 3D collision or ramps assessed',
  'Original L1 underfloor ladder/axial access remains to be checked in 3D',
  'I4 freeform Z-forward was transverse; true ship bow axis is source -X (viewer +H)',
  'Seat/support/thrust alignment, 4g physiology, loading and mounts not qualified',
  'Visual 37 pane and clear dome geometry is speculative; pane mounting and ballistic pressure behaviour unknown'],
 'previous_I4_floor_rectangular_overhang_m2':src['conflicts']['main_deck_area_outside_source_L1_floor_outer_radius_m2'],
 'previous_I4_central_hole_covered_m2':src['conflicts']['main_deck_area_over_source_central_opening_m2'],
 'floor_fix':'Replace, do not overlay, former rectangular 8.15x8.05m floor by source L1 r0=0.9..r1=4.15 annulus, remove both 0.8m diameter original ladder shafts from that annulus.',
 'next':'Render true source floor, seat/furniture candidates and all 37 full outer tile patches with separate window/hull/structure controls.'}
(R/'command/L1_I4_CONSTRAINED_FIT_SCREEN_20261029.json').write_text(json.dumps(out,indent=2))
for q in rows:print(q['id'],q['coarse_gates'],q.get('max_corner_radius_m'),flush=True)
print('PASS',out['gates_pass_all'])
if not out['gates_pass_all']:raise SystemExit(2)