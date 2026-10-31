"""Wayfarer I4 source-frame human-factors screening, non-governing Step 1b.
Reads the exact current hashed geometry; does not mutate it.
Conservative 0.8m floor clearance, upper-bound crown sightlines; dimensional caveats explicit."""
import hashlib,json,math
from collections import deque
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
I=json.loads((ROOT.parent/'config/wayfarer_v05_inputs.json').read_text())
GP=ROOT.parent/'results/out/wayfarer_v05_geometry.json'
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
        'contoured_couch_length_1p58m':round(math.dist(s['head'],s['feet']),4)>=1.58-1e-5,
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
# Real 3-axis overlap test of command-terrace slab against all source-annulus
# floor couch bounding envelopes. Intentionally conservative axis-aligned (AABB),
# NOT a 3D body envelope or 4g suited occupant swept-volume certificate.
def couch_aabb(st):
    hy,hz=st['head'];fy,fz=st['feet']
    return {'x_m':[st['base_x']-.45,st['base_x']],
            'y_m':[min(hy,fy)-.35,max(hy,fy)+.35],
            'z_m':[min(hz,fz)-.35,max(hz,fz)+.35]}
def aabb_overlap(a,b):
    axis={k:max(0,min(a[k][1],b[k][1])-max(a[k][0],b[k][0])) for k in ('x_m','y_m','z_m')}
    return axis,all(x>1e-9 for x in axis.values())
floor_clashes={}
for st in seats:
    if st['base_x']<=deck['x_m'][0] or st['id'] not in ('S2','S3','S4'):continue
    a=couch_aabb(st);ov,hit=aabb_overlap(a,deck)
    floor_clashes[st['id']]={'couch_aabb':a,'terrace_aabb':deck,'overlap_m_by_axis':ov,
       'solid_intersection':hit,'min_y_separation_m':round(max(0,a['y_m'][0]-deck['y_m'][1],deck['y_m'][0]-a['y_m'][1]),4),
       'minimum_clearance_m':round(max(max(0,a[k][0]-deck[k][1],deck[k][0]-a[k][1]) for k in ('x_m','y_m','z_m')),4)}
# I4 candidate carry-over: 3D AABB against every occupied couch and source ladder
# well, plus a separate floor-walkway connectivity screen. Contact with the
# already-modelled NAV support platform is intentional, not a new furniture item.
def object_boxes(q):
    if q['kind']=='box':
        return [[[v-h/2,v+h/2] for v,h in zip(q['xyz'],q['size'])]]
    if q['kind']=='tube':
        return [[[min(a,b)-q['radius_m'],max(a,b)+q['radius_m']] for a,b in zip(q['a'],q['b'])]]
    if q['kind']=='arc':
        a0,a1=q['angles_rad'];r=q['radius_m'];x=q['x_m'];t=q['tube_radius_m']
        boxes=[]
        for j in range(18):
            a=a0+(a1-a0)*j/18;b=a0+(a1-a0)*(j+1)/18
            ys=[r*math.cos(a),r*math.cos(b)];zs=[r*math.sin(a),r*math.sin(b)]
            boxes.append([[x-t,x+t],[min(ys)-t,max(ys)+t],[min(zs)-t,max(zs)+t]])
        return boxes
    raise ValueError(q['kind'])
def overlap_volume(a,b):
    return math.prod(max(0,min(a[i][1],b[i][1])-max(a[i][0],b[i][0])) for i in range(3))
seat_boxes={s['id']:[[s['base_x']-.45,s['base_x']],
    [min(s['head'][0],s['feet'][0])-.35,max(s['head'][0],s['feet'][0])+.35],
    [min(s['head'][1],s['feet'][1])-.35,max(s['head'][1],s['feet'][1])+.35]] for s in seats}
ladder_boxes=[[[1.8,3.4],[y-.4,y+.4],[-.4,.4]] for y in (-1.4,1.4)]
item_details={}
blocked_by_objects=set()
for q in I.get('i4_carryover',{}).get('items',[]):
    boxes=object_boxes(q)
    overlaps=[name for name,b in seat_boxes.items() if any(overlap_volume(a,b)>1e-9 for a in boxes)]
    ladders=[j for j,b in enumerate(ladder_boxes) if any(overlap_volume(a,b)>1e-9 for a in boxes)]
    if q.get('collision')=='intentional_table_contact': # still check couches and ladders
        pass
    for iy,iz in walkable:
        y=origin+iy*step;z=origin+iz*step
        if any(a[0][0]<3.31 and a[0][1]>3.0 and a[1][0]-.4<=y<=a[1][1]+.4 and a[2][0]-.4<=z<=a[2][1]+.4 for a in boxes):
            blocked_by_objects.add((iy,iz))
    item_details[q['id']]={'boxes_3D':len(boxes),'couch_intersections':overlaps,'ladder_intersections':ladders,
         'clear':not (overlaps or ladders)}
# Re-evaluate actual connected walkable floor AFTER subtracting carry-over
# obstacles; never rely on the pre-furniture BFS to certify a route.
floor_free=walkable-blocked_by_objects
floor_start=[min(floor_free,key=lambda pt:(origin+pt[0]*step-y)**2+
                             (origin+pt[1]*step)**2) for y in (1.4,-1.4)] if floor_free else []
floor_reach=set(floor_start);floor_todo=deque(floor_start)
while floor_todo:
    iy,iz=floor_todo.popleft()
    for nxt in ((iy+1,iz),(iy-1,iz),(iy,iz+1),(iy,iz-1)):
        if nxt in floor_free and nxt not in floor_reach:
            floor_reach.add(nxt);floor_todo.append(nxt)
floor_seat_reach={st['id']:any(seat_dist(origin+iy*step,origin+iz*step,st)<1.10 for iy,iz in floor_reach)
                  for st in seats if st['id'] in ('S2','S3','S4')}
floor_transfer_reach={}
for q in I.get('i4_carryover',{}).get('items',[]):
    if q['id'].startswith('transfer_'):
        a=q['a'];floor_transfer_reach[q['id']]=any(math.hypot(origin+iy*step-a[1],origin+iz*step-a[2])<1.2
                                                      for iy,iz in floor_reach)
checks={
'six_role_seats_present':len(seats)==6 and len(set(s['id'] for s in seats))==6,
'contoured_couch_nominal_length_1p58m':all(x['contoured_couch_length_1p58m'] for x in couch),
'plan_seat_envelope_inside_annulus':all(x['within_4p15m_plan'] for x in couch),
'pilot_captain_crown_60deg_upper_bound_ge_0p90':all(x['sightline']['visible_upper_bound']>=.9 for x in couch if x['id'] in ('PILOT','S1')),
'0p8m_walkway_to_floor_seats':all(reach[k]['reachable_with_0p8m_route_to_seat_edge'] for k in ('S2','S3','S4')),
'both_ladders_landings_clear':landings['none_overlapped_by_terrace_or_nav'] and landings['both_ladders_in_same_connected_walk_region'],
'terrace_worst_corner_1p2m_crawl_clearance':raw>=1.2,
'floor_couches_vs_terrace_3D_AABB_nonintersection':len(floor_clashes)==3 and not any(v['solid_intersection'] for v in floor_clashes.values()),
'i4_carryover_all_items_3D_no_couch_or_ladder_collision':len(item_details)==len(I.get('i4_carryover',{}).get('items',[])) and all(v['clear'] for v in item_details.values()),
'i4_carryover_floor_walkway_not_severed': bool(floor_free) and all(floor_seat_reach.values()) and all(floor_transfer_reach.values()),


}
out={'geometry_sha256':H,'status':'kT 2026-10-31 bounded I4 couch+crawl 1.2m rule; does NOT qualify physical occupant fit/egress',
'couches':couch,'walkways':{'grid_step_m':step,'path_half_width_m':.4,'walkable_cells':len(walkable),'connected_cells':len(seen),'to_seats':reach},
'ladders':{'holes':ladder_holes,'checks':landings},
'headroom':{'terrace_center_m':round(front-dome(1.96),3),'worst_corner_m':round(raw,3),
           'chamfer_OPTION_not_geometry':{'cut_m':cut,'worst_corner_m':round(ch,3),'gain_m':round(ch-raw,3),
                                        'note':'trim two symmetric outer-forward plan corners; theoretical shell envelope only; reduces usable deck area, no recomputed mass/CG/inertia'}},
'couch_terrace_3D_AABB':floor_clashes,'i4_carryover_objects_3D':item_details,'walkway_cells_blocked_by_carryover':len(blocked_by_objects),'walkway_connected_after_carryover':len(floor_reach),'floor_seat_reach_after_carryover':floor_seat_reach,'floor_transfer_reach_after_carryover':floor_transfer_reach,'checks':checks,'known_HOLD':['1.58m I4 contoured seat accepted as couch for plan screen, but knees-up occupant clearance and 4g hard-point fit HOLD',
 'sightlines optimistic: Osteon ribs/sensors/pane shutter and other obstacles unmodelled',
 'walkway 2D floor only, not raised-terrrace egress and ladder handholds',
 'bare shell clearance against 1.2m crawl threshold is an optimistic upper bound, not certified access','platform loads beyond isolated 4-column beam check unqualified']}
outpath=ROOT/'command/l1_i4_results.json'
outpath.write_text(json.dumps(out,indent=2))
print(json.dumps({'geometry_sha256':H,'checks':checks,'headroom':out['headroom'],'crown_upper_bound':{x['id']:x['sightline']['visible_upper_bound'] for x in couch},'paths':reach},indent=2))
