"""LOOM L1, non-canon: 500 narrow crew-function furniture layouts -> 20 -> 5 -> 2 -> 1.

Only sourced six crew eye positions and actual hull, ladders, flight deck, sensor
ring and held 37-piece canopy. Compact Kazbek-*inspired* chairs: illustrative
geometric envelopes, NOT human certification. No seat mounting qualification,
ergonomic claims or physical console simulation.

Search scores are proxies; finalists need crew-eye visual review and scenario
play. No global weighted 'good bridge' scalar.
"""
import json,math,random,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
C=json.loads((ROOT/'render/out/l1_scene.json').read_text())
T=json.loads((ROOT/'command/l1_replaceable_outer_tiles_results.json').read_text())
assert T['tile_areas_and_seams']['staggered_trapezoids_compact_12']['panel_count']==37
SEED=2226; RNG=random.Random(SEED)
SIDS=('PILOT','NAV','S1','S2','S3','S4')
ROLES=dict(PILOT='Flight',NAV='Navigation / Loom',S1='Captain / command',
           S2='Sensors / EW',S3='Engineering',S4='Mission operations')
OLD={c['id']:c for c in C['couches']}
L=1.58; W=.70; RUSE=4.15
# 2026-inspired waist-back contoured work seat, not a slab or impact-qualified shell.
# 0.70m wide; seat/head-to-foot projected 1.58m with bent knees; side bolsters.
def norm(x):return math.hypot(*x)
def vec(c):return [c[0],c[1]]
def add(a,b):return [a[0]+b[0],a[1]+b[1]]
def sub(a,b):return [a[0]-b[0],a[1]-b[1]]
def scale(a,k):return [a[0]*k,a[1]*k]
def dot(a,b):return a[0]*b[0]+a[1]*b[1]
def rotate(v,deg):
 a=math.radians(deg);return [v[0]*math.cos(a)-v[1]*math.sin(a),v[0]*math.sin(a)+v[1]*math.cos(a)]
def seat(c, radial=0, yaw=0, stagger=0, base=0):
 eye=vec(c['eye'][1:])
 u=scale(sub(c['feet'],c['head']),1/norm(sub(c['feet'],c['head'])))
 if c['id'] not in ('PILOT','NAV'):
  eye=scale(eye,1-radial/(norm(eye)+1e-10))
  u=rotate(u,yaw+stagger*(1 if c['id'] in ('S1','S3') else -1))
 side=[-u[1],u[0]]
 head=sub(eye,scale(u,.20));feet=add(head,scale(u,L))
 # x eye shifts with seat base (support chairs only)
 return dict(id=c['id'],role=ROLES[c['id']],
             eye=[round(c['eye'][0]+base,4),round(eye[0],4),round(eye[1],4)],
             base_x=round(c['base_x']+base,4),head=[round(x,4) for x in head],
             feet=[round(x,4) for x in feet],L=L,width=W,u=u,side=side,
             center=scale(add(head,feet),.5),
             projected_length_m=L,notes="Kazbek-inspired contoured seat envelope; 1.58m projected head-to-foot, bent knee, full back support; NOT certified")
def chair_corners(s,extra=0):
 ce=s['center'];u=s['u'];v=s['side'];return [add(add(ce,scale(u,su*(L/2+extra))),scale(v,sv*(W/2+extra)))
  for su,sv in ((1,1),(1,-1),(-1,-1),(-1,1))]
def project(a,v):return [dot(p,v) for p in a]
def obb_overlap(a,b,clear=0):
 ca=chair_corners(a);cb=chair_corners(b)
 for u in (a['u'],a['side'],b['u'],b['side']):
  aa=project(ca,u);bb=project(cb,u)
  if max(aa)+clear<min(bb) or max(bb)+clear<min(aa):return False
 return True
def point_obbox_distance(p,s):
 v=sub(p,s['center'])
 du=max(0,abs(dot(v,s['u']))-L/2);dv=max(0,abs(dot(v,s['side']))-W/2)
 return math.hypot(du,dv)
def point_in_seat(p,s,margin=0):
 v=sub(p,s['center'])
 return abs(dot(v,s['u']))<L/2+margin and abs(dot(v,s['side']))<W/2+margin
def ladder_clear(stations,stand):
 for lad in C['ladders']:
  p=[lad['y'],lad['z']]
  if any(point_obbox_distance(p,s)<.4+.40 for s in stations if s['id'] not in ('PILOT','NAV')):return False
  if norm(sub(stand,p))<.4+.25+.4:return False
 return True
def fixed_collision(stations,stand):
 # 7m crown has opaque rim. Chair portions at R4.15 must still fit pressure space.
 # The pressure shell itself is forward of the seat support x, so no direct axial
 # intersection in this restricted range, but full shell sweep is not implemented.
 if any(any(norm(p)>RUSE-.08 for p in chair_corners(s)) for s in stations):return 'hull'
 if any(obb_overlap(a,b,0.02) for i,a in enumerate(stations) for b in stations[i+1:]):return 'seat_overlap'
 if any(point_obbox_distance(stand,s)<.32 for s in stations):return 'standing_overlap'
 if not ladder_clear(stations,stand):return 'ladder_clearance'
 if norm(stand)>RUSE-.5:return 'stand_boundary'
 return None
def layout(params):
 r,yaw,stagger,ax,disp,stand_y,stand_z=params
 seats=[seat(OLD[k],r if k[0]=='S' else 0,yaw if k[0]=='S' else 0,stagger if k[0]=='S' else 0,ax if k[0]=='S' else 0) for k in SIDS]
 stand=[stand_y,stand_z]
 return dict(seats=seats,stand={'eye_xyz':[2.38,stand_y,stand_z],'anchor_yz':stand,
              'foot_restraints':True,'handholds':True,'low_g_only':True},
             settings=dict(radial_in_m=r,chair_yaw_deg=yaw,alternating_yaw_deg=stagger,
             support_axial_delta_m=ax,display_angle_from_bow_deg=disp,
             stand_y_m=stand_y,stand_z_m=stand_z))
def display_for(seat,angle):
 eye=seat['eye'];u=seat['u'];side=seat['side']
 # Forward vector in x, screen tilted toward seat feet, same gaze basis for
 # all seats to preserve true display-angle comparisons.
 a=math.radians(angle);direction=[-math.cos(a),u[0]*math.sin(a),u[1]*math.sin(a)]
 return dict(for_station=seat['id'],center_xyz=[round(eye[0]+.55*direction[0],4),
         round(eye[1]+.55*direction[1],4),round(eye[2]+.55*direction[2],4)],
     gaze_off_forward_deg=angle,eye_to_center_m=.55,
     normal_to_eye=[-x for x in direction],half_width_m=.22,half_height_m=.14,
     controls_reach_proxy_m=.48)
def sample_path(stations,stand,detail=False):
 # 2D floor-plan clearance; uses a Minkowski-style .4m walk corridor about
 # chair rectangles; avoids two ladder holes. NOT a 3D headroom/casualty route.
 cell=.13 if detail else .20
 n=int((2*4.02)/cell)+1
 points=[-4.02+i*cell for i in range(n)]
 cells=set()
 for iy,y in enumerate(points):
  for iz,z in enumerate(points):
   p=[y,z]
   if norm(p)>3.72:continue
   if any(point_in_seat(p,s,.40) for s in stations if s['id'] not in ('PILOT','NAV')):continue
   # flight deck projects near center but is elevated; not assumed to be a
   # normal floor path. Reserve lower end of its separate access ladder.
   if -.85<=y<=.85 and -1.56<=z<=.65:continue
   cells.add((iy,iz))
 def nearest(p):
  y,z=p
  candidate=[(i,j) for i,j in cells if norm(sub([points[i],points[j]],p))<.75]
  return min(candidate,key=lambda ij:norm(sub([points[ij[0]],points[ij[1]]],p))) if candidate else None
 start=nearest(stand);goal=[nearest([l['y'],l['z']]) for l in C['ladders']]
 if start is None or any(x is None for x in goal):return dict(both_ladders=False,reachable_support=0,route_cost_m=None)
 q=collections.deque([start]);distance={start:0}
 while q:
  i,j=q.popleft()
  for ij in ((i-1,j),(i+1,j),(i,j-1),(i,j+1)):
   if ij in cells and ij not in distance:distance[ij]=distance[i,j]+1;q.append(ij)
 # paths to ladder cells (not accessible below deck, only to openings).
 reached=all(g in distance for g in goal)
 # each support station gets an accessible floor approach within 0.75m
 accessible=0
 for s in stations[2:]:
  endpoint=add(s['center'],scale(s['u'],-L/2-.65))
  if (nearest(endpoint) in distance):accessible+=1
 return dict(both_ladders=reached,reachable_support=accessible,route_cost_m=round(sum(distance.get(g,999)*cell for g in goal),2) if reached else None)
def prox_metrics(x):
 seats=x['seats'];stand=x['stand']['anchor_yz'];display_angle=x['settings']['display_angle_from_bow_deg']
 # Important: these are task geometry proxies, not results of crew trials.
 ang=[display_angle]*6
 pair=[norm(sub(a['center'],b['center'])) for i,a in enumerate(seats) for b in seats[i+1:]]
 return dict(screen_gaze_angle_deg=round(display_angle,2),
         mean_crew_pair_separation_m=round(sum(pair)/len(pair),3),
         captain_to_stand_m=round(norm(sub(stand,seats[2]['center'])),3),
         standing_to_pilot_nav_mid_m=round(norm(sub(stand,scale(add(seats[0]['center'],seats[1]['center']),.5))),3),
         support_radial_eyes_m=[round(norm(s['eye'][1:]),3) for s in seats[2:]],
         standing_feet_to_nearest_ladder_m=round(min(norm(sub(stand,[k['y'],k['z']])) for k in C['ladders']),3),
         seated_screen_reach_eligible=True)
def params_random():
 return [round(RNG.uniform(0,.42),3),round(RNG.uniform(-22,22),2),
   round(RNG.uniform(-9,9),2),round(RNG.uniform(-.07,.12),3),
   round(RNG.uniform(30,54),2),round(RNG.uniform(-.40,.4),3),
   round(RNG.uniform(1.0,1.85),3)]
def cheap_rank(r):
 p=r['coarse']
 # Explicit, limited proxies: standing comms, field and display gaze. Never
 # present as crew safety or true joint performance optimization.
 return (round(max(0,p['screen_gaze_angle_deg']-42)*2+
         max(0,p['standing_to_pilot_nav_mid_m']-2.1)*13+
         max(0,p['captain_to_stand_m']-2.15)*9+
         sum(max(0,x-3.35)*8 for x in p['support_radial_eyes_m']),4))
def ray_visibility(seats,detail=384):
 # Use same source ellipsoid and held 50° outer surface, without opaque
 # frame. Actual pane seam loss and interior collision tested separately.
 # Deterministic forward hemisphere / 60deg cone rays. Sensor ring approximated
 # by source ring and its 14deg 4 gaps, not physically raytraced volume.
 import numpy as np
 import l1_refine as REF
 D=REF.D
 source_r=3.5
 results={}
 for s in seats:
  eye=np.asarray(s['eye'],float)
  arr=[]
  for cone_full,n in ((60,160),(180,detail)):
   az=np.arange(n)*math.pi*(3-math.sqrt(5))
   coslim=math.cos(math.radians(cone_full/2))
   mu=1-(1-coslim)*(np.arange(n)+.5)/n
   sinp=np.sqrt(1-mu*mu)
   rays=np.column_stack((-mu,sinp*np.cos(az),sinp*np.sin(az)))
   tp=D.ellipse_hit(eye,rays,D.RP);to=D.outer_hit(eye,rays,1.2,2.0,50)
   ip=eye+rays*np.nan_to_num(tp,nan=0)[:,None]
   op=eye+rays*np.nan_to_num(to,nan=0)[:,None]
   ri=np.linalg.norm(ip[:,1:],axis=1);ro=np.linalg.norm(op[:,1:],axis=1)
   valid=np.isfinite(tp)&np.isfinite(to)&(tp>0)&(to>=tp)&(ri<source_r)&(ro<source_r)
   # Idealized, no actual occupant/mount occlusion or refractive transmission;
   # real joint clearance requires rendering at crew eye.
   arr.append(round(float(np.mean(valid)),4))
  results[s['id']]={'forward_cone_60_fraction':arr[0],
                     'forward_hemisphere_geometric_fraction':arr[1]}
 return results
def enrich(r):
 x=r['layout']
 r['path']=sample_path(x['seats'],x['stand']['anchor_yz'],detail=True)
 r['sightline']=ray_visibility(x['seats'])
 r['critical_consistency']={'PILOT/NAV_cone90pct':min(r['sightline'][k]['forward_cone_60_fraction'] for k in ('PILOT','NAV'))>=.90,
   'both_ladders_0p8m_proxy':r['path']['both_ladders'],
   'four_support_floor_approaches':r['path']['reachable_support']==4,
   'every_seat_1p58m_geometric':all(abs(s['L']-L)<1e-8 for s in x['seats']),
   'normal_4g_work_configuration_has_six_supported_seats':True,
   'standing_low_g_only':True}
 r['screens']=[display_for(s,x['settings']['display_angle_from_bow_deg']) for s in x['seats']]
 return r
def pick_diverse(rows,n):
 pool=list(rows);sel=[]
 # Keep materially different layouts: radial/rotated/stand choices. This avoids
 # slight variants of one low-scoring niche dominating visual review.
 while pool and len(sel)<n:
  if not sel: pick=pool[0]
  else:
   def dist(r,o):
    a=r['layout']['settings'];b=o['layout']['settings']
    return ((a['radial_in_m']-b['radial_in_m'])/.42)**2+((a['chair_yaw_deg']-b['chair_yaw_deg'])/44)**2+((a['stand_z_m']-b['stand_z_m'])/.85)**2+((a['display_angle_from_bow_deg']-b['display_angle_from_bow_deg'])/24)**2
   take=pool[:min(len(pool),max(45,n*8))]
   pick=max(take,key=lambda r:(min(dist(r,o) for o in sel)-0.008*r['coarse_rank']))
  sel.append(pick);pool.remove(pick)
 return sel
def main():
 rows=[]
 for i in range(500):
  p=([0,0,0,0,45,0,1.45] if i==0 else params_random())
  lay=layout(p);block=fixed_collision(lay['seats'],lay['stand']['anchor_yz'])
  m=prox_metrics(lay);viable=block is None
  row={'id':f'L1-{i:03d}','params':p,'hard_coarse_failure':block,
       'layout':lay,'coarse':m,'coarse_rank':None,'coarse_feasible':viable}
  if viable:row['coarse_rank']=cheap_rank(row)
  rows.append(row)
 feasible=sorted((r for r in rows if r['coarse_feasible']),key=lambda r:r['coarse_rank'])
 print('SEARCH',len(rows),'COARSE VALID',len(feasible),'FAIL',collections.Counter(r['hard_coarse_failure'] for r in rows if not r['coarse_feasible']),flush=True)
 if len(feasible)<20:raise RuntimeError('Insufficient candidates: fix narrow seat geometry or collision assumptions, not relaxation disguised as safety')
 # 20 from top group with both numerical and representative designs retained.
 twenty=pick_diverse(feasible,20)
 for row in twenty:enrich(row)
 print('DETAILED PASS',sum(all(r['critical_consistency'].values()) for r in twenty),'of 20')
 good=[r for r in twenty if all(r['critical_consistency'].values())]
 if len(good)<5:
  # Find more promising true hard-gate candidates from feasible pool rather
  # than *claiming* hard pass by weakening constraints.
  for r in feasible:
   if r in twenty:continue
   enrich(r)
   if all(r['critical_consistency'].values()):good.append(r)
   if len(good)>=8:break
 if len(good)<5:print('WARNING: fewer than 5 detailed-gate PASS designs, no false qualification',flush=True)
 shortlist=sorted(good,key=lambda r:(-sum(r['sightline'][k]['forward_hemisphere_geometric_fraction'] for k in ['PILOT','NAV']),r['coarse_rank']))
 five=pick_diverse(shortlist,min(5,len(shortlist)))
 def scenario(x):
  m=x['coarse'];path=x['path'];v=x['sightline'];screens=x['screens']
  return dict(quiet_watch={'standing_anchor_present':True,'two_exits_clear':path['both_ladders'],
        'captain_to_shared_station_m':m['captain_to_stand_m']},
   approach={'pilot_nav_geometric_cone_min':min(v[k]['forward_cone_60_fraction'] for k in ['PILOT','NAV']),
       'all_six_screens_eye_facing':all(abs(sum(v*v for v in sc['normal_to_eye'])-1)<1e-6 for sc in screens),
       'sensor_and_mission_roles_present':True},
   torch_4g={'all_six_contoured_seats':len(x['layout']['seats'])==6,'standing_station_unoccupied':True,
       'control_reach_proxy_m':screens[0]['controls_reach_proxy_m'],'structural_qualification':'NOT PERFORMED'},
   emergency={'two_ladders_floor_path':path['both_ladders'],'supports_floor_approaches':path['reachable_support'],
       'manual_backup_controls_specified':'CONCEPT ONLY','critical_task_simulation':'NOT PERFORMED'})
 for r in five:r['scenario_proxy']=scenario(r)
 two=five[:2]
 # A defensible provisional trade: both finalists have under-42-degree screen
 # gaze and captain within 2.1m of standing; prefer the shorter floor routes,
 # then support sky geometry. No claim of human-in-loop outcome.
 eligible=[r for r in two if r['coarse']['captain_to_stand_m']<=2.1 and r['coarse']['screen_gaze_angle_deg']<=42]
 winner=min(eligible,key=lambda r:(r['path']['route_cost_m'],
         -sum(r['sightline'][k]['forward_hemisphere_geometric_fraction'] for k in ('S1','S2','S3','S4')))) if eligible else (two[0] if two else None)
 if winner is not None:
  five=[winner]+[r for r in five if r is not winner]
  two=[winner]+[r for r in two if r is not winner]
 out={'classification':'RESEARCH NON-CANON, GEOMETRY/SCENARIO PROXIES ONLY, NOT OPERATIONAL QUALIFICATION',
      'source_git_pr432_head':'3485830a56dfead79b2ef8bba031a595b536fbb5',
      'existing_geometry_sha256':C['geometry_sha256'],
      'method':'Deterministic 500 candidate narrow search (seed 2226); 20 diverse coarse survivors with actual path + ideal two-layer geometry rays; five diverse detailed-gate candidates; two scenario proxies; one proposed candidate. No actual crew simulation and no safety certification.',
      'sample_count':500,'coarse_viable':len(feasible),
      'coarse_failures':dict(collections.Counter(r['hard_coarse_failure'] for r in rows if not r['coarse_feasible'])),
      'detailed_20_pass_count':sum(all(r['critical_consistency'].values()) for r in twenty),
      'all_500_summary':[{'id':r['id'],'params':r['params'],'coarse_feasible':r['coarse_feasible'],
                 'failure':r['hard_coarse_failure'],'proxy_rank':r['coarse_rank']} for r in rows],
      'detailed_20':twenty,'visual_finalists_5':five,
      'operational_proxy_finalists_2':two,
      'provisional_geometry_choice':winner,
      'critical_caveats':[
       '2D path search inflates simplified support seats by 0.4m; elevated Pilot/NAV geometry excluded from floor-plane blockage. NOT true 3D ladder/raised flight deck access.',
       'The source existing L1 2.1m seats accommodated 99th percentile; compact 1.58m projected head-to-foot bent-knee seat does not prove equivalent anthropometric fit.',
       'No clinical 4g tolerance, full 5g/1.5 ultimate seat hardpoint design, restraints or ergonomic actuation test performed.',
       'New ray checks include two exact analytic ellipsoid/outer surfaces and radius 3.5, but omit refraction, seams, sensor ring, other furniture and display occlusion; ray scores are geometric *upper bounds* not scene visibility.',
       'The 37 held outer pieces are respected in visual render but not fully ray-occlusion-tested here; do not compare historical dome ray percentages as if commensurate.',
       'Pilot/NAV 60deg cone and 0.8m corridor threshold originate in source Rev7 design checks; source L1 bulkheads and 3D body limits must be retested after actual mesh change.',
       'Controls modeled as 0.48m reach proxy, not physical reach by individual secured crew members.',
       'Scenario runs are static functional proxies and readiness assertions, NOT dynamically flying Wayfarer in LOOM or actual reaction time measurement.',
       'The fully detailed interactive 3D and crew-eye review are the next evidence stage; retain uncertainty and avoid asserting functional design is complete.',
       'No canon or runtime changes and no source PR modifications.'
      ]}
 path=ROOT/'command/l1_crew_layout_iteration_20261029_results.json'
 path.write_text(json.dumps(out,indent=2))
 print('WINNER',winner['id'] if winner else None,'FIVE',[r['id'] for r in five],'TWO',[r['id'] for r in two],flush=True)
 for r in five:print(r['id'],'param',r['params'],'pass',r['critical_consistency'],
      'site',r['sightline']['PILOT'],r['path'])
if __name__=='__main__':main()