"""Wayfarer I4 source-frame human-factors screening, non-governing Step 1b.
Reads existing hashed 9290... geometry, does NOT alter geometry, render or production.
Conservative 0.8m floor clearance, upper-bound crown sightlines; dimensional caveats explicit."""
import hashlib,json,math
from collections import deque
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
I=json.loads((ROOT/'inputs/wayfarer_v05_inputs.json').read_text())
GP=ROOT/'out/wayfarer_v05_geometry.json'
G=json.loads(GP.read_text())
H=hashlib.sha256(GP.read_bytes()).hexdigest()
i4=I['habitat']['decks'][0]['command_layout']['i4_lock']
seats=i4['stations']
hull=I['hull']; pressure=next(p['shape'] for p in G['parts'] if p['id']=='pressure_vessel')
xa,xb,R=pressure['xa'],pressure['xb'],pressure['R']
def dome(r):
    return xb-(xb-xa)*math.sqrt(max(0,1-(min(r,R)/R)**2))
def d2(pt,seg):
    (x,y),(u,v)=pt,seg[0];p,q=seg[1]
    dx,dy=p-u,q-v
    t=max(0,min(1,((x-u)*dx+(y-v)*dy)/max(1e-10,dx*dx+dy*dy)))
    return math.hypot(x-(u+t*dx),y-(v+t*dy))
def inside_rect(y,z,b):
    return b['y_m'][0]<=y<=b['y_m'][1] and b['z_m'][0]<=z<=b['z_m'][1]
# A couch footprint based on the actual 1.58m I4 geometry and width 0.7m.
def seat_dist(y,z,s):
    return d2((y,z),(s['head'],s['feet']))
def sep(s,t):
    return min(d2(p,(t['head'],t['feet'])) for p in [s['head'],s['feet']])
def ray_fraction(st,n=360):
    r=math.hypot(st['eye'][1],st['eye'][2])
    eye=(st['base_x']-0.45,st['eye'][1],st['eye'][2])
    if eye[0]<dome(r): return {'visible_upper_bound':0,'eye_inside_shell':False}
    hit=0
    for i in range(n):
        mu=1-(1-math.cos(math.pi/6))*(i+.5)/n
        sn=math.sqrt(1-mu*mu);phi=i*math.pi*(3-math.sqrt(5))
        d=(-mu,sn*math.cos(phi),sn*math.sin(phi))
        # Binary search intersection of shell, assuming forward-ray segment in dome.
        t0=0; t1=8
        for _ in range(24):
            t=(t0+t1)*.5
            x=eye[0]+t*d[0]; y=eye[1]+t*d[1];z=eye[2]+t*d[2]
            if x>=dome(math.hypot(y,z)):t0=t
            else:t1=t
        y=eye[1]+t1*d[1];z=eye[2]+t1*d[2];rad=math.hypot(y,z)
        # Optimistic pane check: do not count obstructed by the pane radius; the
        # Osteon blades, sensors, other occupied seats and displays can only reduce.
        if rad<=I['habitat']['decks'][0]['command_layout']['crown_dome']['r_m']:hit+=1
    return {'visible_upper_bound':round(hit/n,3),'eye_inside_shell':True,
            'model':'upper bound ONLY; panes open, no Osteon/sensor/other occupant blocking'}
deck=i4['platforms']['command_terrace']
corners=[(y,z) for y in deck['y_m'] for z in deck['z_m']]
front=deck['x_m'][0]
raw=min(front-dome(math.hypot(y,z)) for y,z in corners)
# Optional symmetric 0.5m chamfer at both outboard aft corners (one corner per ±Y)
cut=.5
verts=[(deck['y_m'][0]+cut,deck['z_m'][0]),(deck['y_m'][1]-cut,deck['z_m'][0]),
       (deck['y_m'][0],deck['z_m'][0]+cut),(deck['y_m'][1],deck['z_m'][0]+cut),
       (deck['y_m'][0],deck['z_m'][1]),(deck['y_m'][1],deck['z_m'][1])]
ch=min(front-dome(math.hypot(y,z)) for y,z in verts)
couch=[{'id':s['id'],'length_m':round(math.dist(s['head'],s['feet']),4),
        'min_2p10_m':round(math.dist(s['head'],s['feet']),4)>=2.10-1e-5,
        'radius_head_m':round(math.hypot(*s['head']),3),'radius_feet_m':round(math.hypot(*s['feet']),3),
        'within_4p15m_plan':max(math.hypot(*s['head']),math.hypot(*s['feet']))+.35<=4.15,
        'eye_x_m':round(s['base_x']-.45,3),'sightline':ray_fraction(s)}
        for s in seats]
# Grid-based conservative clearance in L1 floor; does NOT qualify vertical transitions.
step=.1; n=88; origin=-4.35
blocked=set();walkable=set()
for iy in range(n):
    y=origin+iy*step
    for iz in range(n):
        z=origin+iz*step;r=math.hypot(y,z)
        if r<1.30 or r>3.75:continue
        if any(inside_rect(y,z,b) or (b['y_m'][0]-.4<=y<=b['y_m'][1]+.4 and b['z_m'][0]-.4<=z<=b['z_m'][1]+.4)
               for b in i4['platforms'].values()):continue
        if any(seat_dist(y,z,s)<.75 for s in seats if s['id'] not in ('PILOT','NAV','S1')):continue
        walkable.add((iy,iz))
def closest(y,z):
    return min(walkable,key=lambda pt:(origin+pt[0]*step-y)**2+(origin+pt[1]*step-z)**2)
start=[closest(1.4,0.0),closest(-1.4,0.0)] if walkable else []
seen=set(start);todo=deque(start)
while todo:
    iy,iz=todo.popleft()
    for nxt in ((iy+1,iz),(iy-1,iz),(iy,iz+1),(iy,iz-1)):
        if nxt in walkable and nxt not in seen:seen.add(nxt);todo.append(nxt)
reach={}
for st in seats:
    d=min((seat_dist(origin+iy*step,origin+iz*step,st) for iy,iz in seen),default=1e9)
    reach[st['id']]={'reachable_floor_clearance_to_seat_edge_m':round(d-.35,3),
                     'reachable_with_0p8m_route_to_seat_edge':d<=.85,
                     'requires_vertical_transfer':st['id'] in ('PILOT','NAV','S1')}
ladder_holes=[{'y_m':math.cos(math.radians(x['theta_deg']))*x['r_m'],
               'z_m':math.sin(math.radians(x['theta_deg']))*x['r_m'],
               'diameter_m':x['size_m']} for x in I['habitat']['ladderways']]
landings={'none_overlapped_by_terrace_or_nav':all(not inside_rect(x['y_m'],x['z_m'],b) for x in ladder_holes for b in i4['platforms'].values()),
          'both_ladders_in_same_connected_walk_region':all(x in seen for x in start)}
checks={
'six_role_seats_present':len(seats)==6 and len(set(s['id'] for s in seats))==6,
'2p10m_99pct_couch_envelope':all(x['min_2p10_m'] for x in couch),
'plan_seat_envelope_inside_annulus':all(x['within_4p15m_plan'] for x in couch),
'pilot_captain_crown_60deg_upper_bound_ge_0p90':all(x['sightline']['visible_upper_bound']>=.9 for x in couch if x['id'] in ('PILOT','S1')),
'0p8m_walkway_to_floor_seats':all(reach[k]['reachable_with_0p8m_route_to_seat_edge'] for k in ('S2','S3','S4')),
'both_ladders_landings_clear':landings['none_overlapped_by_terrace_or_nav'] and landings['both_ladders_in_same_connected_walk_region'],
'terrace_worst_corner_2p10m_standing_headroom':raw>=2.1,
}
out={'geometry_sha256':H,'status':'Step1b I4 bounded structural plan/sightline upper-bound screening; DOES NOT qualify physical station occupancy',
'couches':couch,'walkways':{'grid_step_m':step,'path_half_width_m':.4,'walkable_cells':len(walkable),'connected_cells':len(seen),'to_seats':reach},
'ladders':{'holes':ladder_holes,'checks':landings},
'headroom':{'terrace_center_m':round(front-dome(1.96),3),'worst_corner_m':round(raw,3),
           'chamfer_OPTION_not_geometry':{'cut_m':cut,'worst_corner_m':round(ch,3),'gain_m':round(ch-raw,3),
                                        'note':'trim two symmetric outer-forward plan corners; theoretical shell envelope only; reduces usable deck area, no recomputed mass/CG/inertia'}},
'checks':checks,'known_HOLD':['nominal I4 seat 1.58m envelope below 2.10m criterion',
 'sightlines optimistic: Osteon ribs/sensors/pane shutter and other obstacles unmodelled',
 'walkway 2D floor only, not raised-terrrace egress and ladder handholds',
 'bare shell clearance not occupant headroom','platform loads beyond isolated 4-column beam check unqualified']}
outpath=ROOT/'command/l1_i4_results.json'
outpath.write_text(json.dumps(out,indent=2))
print(json.dumps({'geometry_sha256':H,'checks':checks,'headroom':out['headroom'],'crown_upper_bound':{x['id']:x['sightline']['visible_upper_bound'] for x in couch},'paths':reach},indent=2))
