"""Corrective research: genuinely distinct support-station floorplan families.

The initial 500 search selected near-neighbour variations in one ring topology.
This deliberately authors five different functional topologies. Each family
has 100 small variants, checked by the *same* narrow 2D collision/path and
ideal forward rays. No claim that its proxies qualify full L1.
"""
import json,math,random,sys,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'command'))
import l1_crew_layout_iteration_20261029 as old
BASE=json.loads((ROOT/'command/l1_crew_layout_iteration_20261029_results.json').read_text())
R=random.Random(2226)
source=old.OLD
ids=['S1','S2','S3','S4']
# Angles are the actual seat centres about the +X body axis in the YZ plane.
# Each family changes WHO is near whom, not only ±20deg chair yaw.
FAMILIES=[
 dict(id='L1-A',name='Inboard panoramic ring',idea='Four seats around the inner shoulder, maximal crew visibility',
      angles=[45,135,225,315],radii=[2.92]*4,yaws=[-15]*4,stand=[.10,1.15],display=40,stand_style='compact'),
 dict(id='L1-B',name='Perimeter free core',idea='Four perimeter workstations leave the central floor open',
      angles=[45,135,225,315],radii=[3.38]*4,yaws=[-2]*4,stand=[.15,1.35],display=35,stand_style='round'),
 dict(id='L1-C',name='Paired mission pods',idea='Side-by-side work teams on upper and lower arcs, facing shared displays',
      angles=[65,115,245,295],radii=[3.05]*4,yaws=[-12,-12,12,12],stand=[0,1.05],display=37,stand_style='wide'),
 dict(id='L1-D',name='Staggered specialist stations',idea='Alternating inboard and outer stations for access and sensor work',
      angles=[35,145,215,325],radii=[2.78,3.37,2.78,3.37],yaws=[14,-12,14,-12],stand=[.0,1.17],display=37,stand_style='linear'),
 dict(id='L1-E',name='Command fan and mission wings',idea='Captain and mission near centre, sensors and engineer wide aft',
      angles=[56,124,236,304],radii=[2.79,3.33,3.33,2.79],yaws=[14,-18,18,-14],stand=[.08,1.32],display=37,stand_style='forward')
]
def transform_source(c,target_angle):
 v=math.atan2(c['eye'][2],c['eye'][1]);a=math.radians(target_angle)-v
 d=dict(c)
 for field in ['head','feet']:
  q=c[field];d[field]=old.rotate(q,math.degrees(a))
 q=c['eye'];out=old.rotate(q[1:],math.degrees(a));d['eye']=[q[0],out[0],out[1]]
 return d
def build(f,index):
 noise=.0 if index==0 else 1.
 yaw_noise=R.uniform(-4,4)*noise
 angles=[k+R.uniform(-4,4)*noise for k in f['angles']]
 radii=[k+R.uniform(-.09,.09)*noise for k in f['radii']]
 yaw=[k+yaw_noise+R.uniform(-4,4)*noise for k in f['yaws']]
 st=[f['stand'][0]+R.uniform(-.12,.12)*noise,f['stand'][1]+R.uniform(-.15,.15)*noise]
 seats=[old.seat(source[k]) for k in ('PILOT','NAV')]
 for k,ang,rad,yy in zip(ids,angles,radii,yaw):
  c=transform_source(source[k],ang)
  base_radius=old.norm(c['eye'][1:])
  ss=old.seat(c,radial=base_radius-rad,yaw=yy,base=0)
  seats.append(ss)
 return {'family':f['id'],'family_name':f['name'],'family_idea':f['idea'],
         'stand_style':f['stand_style'],
         'seats':seats,
         'stand':{'eye_xyz':[2.38,st[0],st[1]],'anchor_yz':st,'foot_restraints':True,'handholds':True,'low_g_only':True},
         'settings':{'radii_m':radii,'angles_deg':angles,'individual_yaws_deg':yaw,
            'display_angle_from_bow_deg':f['display'],'stand_y_m':st[0],'stand_z_m':st[1]}}
def score(x):
 seats=x['seats'];stand=x['stand']['anchor_yz']
 failure=old.fixed_collision(seats,stand)
 if failure:return None,failure
 path=old.sample_path(seats,stand,detail=True)
 if not path['both_ladders'] or path['reachable_support']<4:return None,'2d_paths'
 vis=old.ray_visibility(seats,detail=384)
 if min(vis[k]['forward_cone_60_fraction'] for k in ('PILOT','NAV'))<.9:return None,'pilot_nav_cone'
 cap=old.norm(old.sub(stand,seats[2]['center']))
 return {'path':path,'sightline':vis,
      'captain_stand_distance_m':round(cap,3),
      'mean_support_forward_fraction':round(sum(vis[k]['forward_hemisphere_geometric_fraction'] for k in ids)/4,4),
      'objective_proxy':round(path['route_cost_m']+.3*cap,4)},None
def choose_for(f):
 successes=[];failed=collections.Counter()
 for i in range(100):
  x=build(f,i);metrics,reason=score(x)
  if reason:failed[reason]+=1;continue
  successes.append((metrics['objective_proxy'],i,x,metrics))
 if not successes:
  return dict(family=f,valid=0,failures=dict(failed),chosen=None)
 # Family-specific representative, with preference to authored archetype (i=0)
 # within 0.8m equivalent geometric route cost of best tested one.
 best=min(c[0] for c in successes)
 shortlist=[c for c in successes if c[0]<=best+.8]
 chosen=next((q for q in shortlist if q[1]==0),min(shortlist))
 _,i,x,m=chosen
 screens=[old.display_for(s,f['display']) for s in x['seats']]
 # Extra wide local tandem displays only in paired-pods configuration
 if f['id']=='L1-C':
  for s in screens[2:]:s['half_width_m']=.29
 # Unit-oriented role screens with different design language, not identical monitors
 x['screens']=screens
 return dict(family=f,valid=len(successes),failures=dict(failed),
       chosen={'id':f['id'],'layout':x,'screens':screens,'metrics':m,'selected_sample':i,
           'geometry_proxy_only':True})
def main():
 results=[choose_for(f) for f in FAMILIES]
 for r in results:print(r['family']['id'],r['family']['name'],'VALID',r['valid'],'FAIL',r['failures'],
      'SELECTED',r.get('chosen',{}).get('selected_sample') if r.get('chosen') else None,
      'METRICS',r.get('chosen',{}).get('metrics') if r.get('chosen') else None,flush=True)
 out={'classification':'RESEARCH / NON-CANON / NON-RUNTIME / UNQUALIFIED',
      'why_redo':'Prior 500 candidate permutations were all the same support-ring architecture and visually indistinguishable. Five *topologically distinct* concept families, each perturbed 100 times, make honest, visible comparisons.',
      'source_sha':BASE['existing_geometry_sha256'],
      'prior_500_results':'L1_500_TO_1_INTERIOR_RESEARCH_RESULTS_20261029.md; retained only as a narrow single-family sweep',
      'families':results,'total_screened':500,
      'survivor_count':sum(x['valid'] for x in results),
      'fully_qualified_count':0,
      'hard_limits':['Actual 3D crew-seat swept volumes, viable 1.58m anthropometric fit, restrained 4g reach, load-rated mounts, measured view with sensors/screens, raised flight deck access and full human performance NOT qualified.',
       'All five layouts are research concepts, not winners from human-in-loop trials.',
       '2D circulation and ideal surface-only rays are screening proxies; no claim that the visible bridge or a moving crew actually clears every path.']}
 path=ROOT/'command/l1_distinct_layout_families_20261029_results.json'
 path.write_text(json.dumps(out,indent=2));print('WRITTEN',path)
if __name__=='__main__':main()