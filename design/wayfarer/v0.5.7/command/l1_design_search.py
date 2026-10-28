"""Parametric Wayfarer L1/nose experiment, NON-CANON, NOT QUALIFIED.
Read-only source geometry; writes only command/l1_design_search_results.json.
Uses Rev 7 real couch, room, sensor and walkway geometry. Makes NO claim that
new pressure apertures, sensor relocation or armour shutters are qualified.
Run: python3 command/l1_design_search.py
"""
import itertools, json, math, hashlib, sys
from pathlib import Path
from collections import Counter
import numpy as np

ROOT=Path(__file__).resolve().parent.parent
sys.path[:0]=[str(ROOT),str(ROOT/'command')]
import l1_study as L
import l1_options as O

INPUTS=json.loads((ROOT/'inputs/wayfarer_v05_inputs.json').read_text())
GEO=json.loads((ROOT/'out/wayfarer_v05_geometry.json').read_text())
H=INPUTS['hull']; CL=INPUTS['habitat']['decks'][0]['command_layout']
BASE=L.built_option(); SC=BASE['scene']
RUSABLE=O.RU; RP=H['pressure_r_m']; RO=H['outer_r_m']
HD=H['pressure_head_depth_m']; XB=H['pressure_vessel_x_m'][0]+HD
EXTENSIONS=(0,.4,.8,1.2,1.6,2)
FACES=(1.2,1.6,2)
ANGLES=(35,42.5,50,57.5,65)
CROWNS=(2.8,3,3.2,3.5)
WINDOWS=('current','radial','segmented','targeted')
SENSORS=('ring','partial','distributed')
STATION_RADII=(-.2,0,.2)
STATION_ROTS=(-15,0,15)
DECK_SHIFTS=(-.2,0,.2)
SHUTTERS=('radial_tambour','segmented_retractable')
IDS=[c['id'] for c in SC.couches]
EYES=np.array([c['eye'] for c in SC.couches])
GOLDEN=np.pi*(3-np.sqrt(5))
FRAMES_W=.08

def out_x(r):
    return 2.35*(1-np.sqrt(np.maximum(0,1-(np.asarray(r)/RO)**2)))
def pressure_x(r):
    return XB-HD*np.sqrt(np.maximum(0,1-(np.asarray(r)/RP)**2))
def facet_x(r,ext,face,ang):
    return -ext+np.maximum(0,np.asarray(r)-face)*np.tan(np.deg2rad(ang))
def profile_screen():
    rr=np.linspace(0,RO,1801)
    pp=np.linspace(0,RP,1721)
    r=[]
    for e,f,a in itertools.product(EXTENSIONS,FACES,ANGLES):
        original=np.min(out_x(rr)-facet_x(rr,e,f,a))
        pressure=np.min(pressure_x(pp)-facet_x(pp,e,f,a))
        if original>=-1e-9 and pressure>=-1e-9:
            r.append((e,f,a,round(float(original),5),round(float(pressure),5)))
    return r

# Vectorized deterministic, equal-solid-angle samples; directions face the original bow.
def directions(n=256,cone=None):
    maximum=1 if cone is None else 1-np.cos(np.deg2rad(cone/2))
    u=1-maximum*(np.arange(n)+.5)/n
    v=np.sqrt(1-u*u); ph=np.arange(n)*GOLDEN
    return np.stack((-u,v*np.cos(ph),v*np.sin(ph)),axis=-1)

RAYS=directions(256)
CONE=directions(224,60)

def ellipse_hit(eye,ds,r):
    # Front ellipsoidal cap. Only x<=XB solutions count, not aft half of ellipsoid.
    ex,ey,ez=eye
    A=(ds[:,0]/HD)**2+(ds[:,1]**2+ds[:,2]**2)/r**2
    B=2*((ex-XB)*ds[:,0]/HD**2+(ey*ds[:,1]+ez*ds[:,2])/r**2)
    C=((ex-XB)/HD)**2+(ey**2+ez**2)/r**2-1
    disc=B*B-4*A*C
    sd=np.sqrt(np.maximum(0,disc))
    t1=(-B-sd)/(2*A);t2=(-B+sd)/(2*A)
    q1=(t1>1e-8)&(ex+t1*ds[:,0]<=XB+1e-7)&(disc>=0)
    q2=(t2>1e-8)&(ex+t2*ds[:,0]<=XB+1e-7)&(disc>=0)
    return np.where(q1,t1,np.where(q2,t2,np.nan))

def outer_hit(eye,ds,ext,face,angle):
    k=np.tan(np.deg2rad(angle))
    ex,ey,ez=eye; x0=ex+ext+k*face
    # x+ext+k*face = k*sqrt(y^2+z^2)
    A=ds[:,0]**2-k*k*(ds[:,1]**2+ds[:,2]**2)
    B=2*(x0*ds[:,0]-k*k*(ey*ds[:,1]+ez*ds[:,2]))
    C=x0*x0-k*k*(ey*ey+ez*ez)
    disc=B*B-4*A*C
    sd=np.sqrt(np.maximum(0,disc))
    safe=np.where(np.abs(A)>1e-10,2*A,np.nan)
    t1=(-B-sd)/safe;t2=(-B+sd)/safe
    def valid(t):
        y=ey+t*ds[:,1];z=ez+t*ds[:,2]
        r=np.hypot(y,z)
        return (disc>=0)&(t>0)&(r>=face-1e-7)&(r<=RO+1e-7)&(x0+ds[:,0]*t>=0)
    a=np.where(valid(t1),t1,np.nan);b=np.where(valid(t2),t2,np.nan)
    tc=np.where(np.isnan(a),b,np.where(np.isnan(b),a,np.minimum(a,b)))
    tf=(-ext-ex)/ds[:,0]
    rf=np.hypot(ey+tf*ds[:,1],ez+tf*ds[:,2])
    tf=np.where((tf>0)&(rf<=face+1e-7),tf,np.nan)
    return np.where(np.isnan(tc),tf,np.where(np.isnan(tf),tc,np.minimum(tc,tf)))

def polar(pts):
    return np.hypot(pts[:,1],pts[:,2]),np.mod(np.degrees(np.arctan2(pts[:,2],pts[:,1])),360)
def angdiff(phi,theta):
    return (phi-theta+180)%360-180

def aperture(radius,phi,crown,pattern):
    if pattern=='current':
        return radius<=2.8
    if pattern=='radial':
        return radius<=crown
    if pattern=='segmented':
        sectors=np.minimum.reduce([np.abs(angdiff(phi,t)) for t in range(0,360,45)])
        return (radius<=1.15)|((radius<=crown)&(sectors<=14))
    sectors=np.minimum.reduce([np.abs(angdiff(phi,t)) for t in (45,135,225,315)])
    return (radius<=2.0)|((radius<=crown)&(sectors<=24))

def frame_hit(radius,phi,crown,pattern):
    # Single retained/integrated pressure frame; mesh frame double-layer is sensitivity.
    edge=np.abs(radius-(2.8 if pattern=='current' else crown))<FRAMES_W/2
    if pattern in ('radial','current'):
        ring=np.abs(radius-1.15)<FRAMES_W/2
        mer=np.minimum.reduce([np.abs(angdiff(phi,t)) for t in range(0,360,45)])
        mer=mer*np.pi/180*radius<FRAMES_W/2
        return edge|ring|((radius>1.15)&mer)
    if pattern=='segmented':
        ring=np.abs(radius-1.15)<FRAMES_W/2
        bounds=np.minimum.reduce([np.abs(angdiff(phi,t)) for t in range(0,360,45)])
        return edge|ring|((radius>1.15)&(np.abs(bounds-14)*np.pi/180*radius<FRAMES_W/2))
    ring=np.abs(radius-2.0)<FRAMES_W/2
    bounds=np.minimum.reduce([np.abs(angdiff(phi,t)) for t in (45,135,225,315)])
    return edge|ring|((radius>2.0)&(np.abs(bounds-24)*np.pi/180*radius<FRAMES_W/2))

def ray_sensor_mask(eye,ds,ti):
    # The actual current Rev7 sensor occupied ring: inside usable dome, x<=2,
    # r>=2.9, except azimuth gap +/-14deg at 45/135/225/315.
    # A sampled occupancy approximation used in coarse screen.
    v=np.zeros(len(ds),dtype=bool)
    tt=np.nan_to_num(ti,nan=0.0)
    for u in np.linspace(.03,.97,20):
        p=eye+ds*(tt*u)[:,None]
        rr,ph=polar(p)
        gap=np.minimum.reduce([np.abs(angdiff(ph,t)) for t in (45,135,225,315)])<=14
        ix=XB-HD*np.sqrt(np.maximum(0,1-(rr/RUSABLE)**2))
        v|=(rr>=2.9)&(rr<=RUSABLE)&(p[:,0]<=2)&(p[:,0]>=ix)&(~gap)&np.isfinite(ti)
    return v

def visibility_one(eye,shape,crown,pattern,sensor,n=256,cone=False,double_frame=False,return_mask=False):
    ds=CONE if cone else RAYS
    e,f,a=shape
    ti=ellipse_hit(eye,ds,RUSABLE)
    tp=ellipse_hit(eye,ds,RP)
    to=outer_hit(eye,ds,e,f,a)
    ip=eye+ds*np.nan_to_num(tp,nan=0)[:,None]
    op=eye+ds*np.nan_to_num(to,nan=0)[:,None]
    pi,ai=polar(ip);po,ao=polar(op)
    check=np.isfinite(ti)&np.isfinite(tp)&np.isfinite(to)&(tp>=ti-1e-5)&(to>=tp+1e-5)
    check &= aperture(pi,ai,crown,pattern)&aperture(po,ao,crown,pattern)
    check &=~frame_hit(pi,ai,crown,pattern)
    if double_frame:
        check&=~frame_hit(po,ao,crown,pattern)
    if sensor=='ring':
        check &=~ray_sensor_mask(eye,ds,ti)
    # 'partial'/'distributed' are visibility upper bounds only, NOT packaged.
    return check if return_mask else round(float(check.mean()),4)

def eye_variation(radius_shift,rot_shift,deck_shift):
    # Shift and rotate actual 4 rim couch axes; preserve L and base.
    eyes=EYES.copy()
    if deck_shift:
        eyes[:2,0]+=deck_shift
    for j in range(2,6):
        cc=SC.couches[j]
        theta=np.deg2rad(rot_shift)
        cc0=np.array(cc['head']);ff0=np.array(cc['feet'])
        vec=ff0-cc0
        head=cc0*(1+radius_shift/max(np.linalg.norm(cc0),1e-6))
        feet=head+np.array([np.cos(theta)*vec[0]-np.sin(theta)*vec[1],
                             np.sin(theta)*vec[0]+np.cos(theta)*vec[1]])
        eyes[j]=O.couch(IDS[j],tuple(head),tuple(feet),O.FLOOR,cc['L'])['eye']
    return eyes

def area_m2(crown,pattern):
    # Transparent *pressure* area, ellipsoidal surface; shutter area can differ.
    rr=np.linspace(.002,2.8 if pattern=='current' else crown,600)
    derivative=HD*rr/(RP*RP*np.sqrt(np.maximum(1e-6,1-(rr/RP)**2)))
    if pattern in ('current','radial'):frac=np.ones_like(rr)
    elif pattern=='segmented':frac=np.where(rr<=1.15,1,8*28/360)
    else:frac=np.where(rr<=2,1,4*48/360)
    return round(float(np.trapz(2*np.pi*rr*np.sqrt(1+derivative**2)*frac,rr)),2)

def exterior_aperture_area_m2(shape,crown,pattern):
    # Idealised exterior-panel surface area: flat central face then conical facets.
    # Differs from pressure-pane area. 72-sector triangulations vary slightly.
    ext,face,angle=shape
    limit=2.8 if pattern=='current' else crown
    rr=np.linspace(.0005,limit,2001)
    slope=np.where(rr<=face,1.0,1/np.cos(np.deg2rad(angle)))
    if pattern in ('current','radial'):
        fraction=np.ones_like(rr)
    elif pattern=='segmented':
        fraction=np.where(rr<=1.15,1,8*28/360)
    else:
        fraction=np.where(rr<=2,1,4*48/360)
    return round(float(np.trapz(2*np.pi*rr*slope*fraction,rr)),2)

def screen():
    shapes=profile_screen()
    assert len(shapes)==28, len(shapes)
    # 28*4*4*3 = 1344 unperturbed candidates; 656 deterministic variations.
    base=[(s[:3],c,w,se,0,0,0,sh)
          for s,c,w,se,sh in itertools.product(shapes,CROWNS,WINDOWS,SENSORS,('radial_tambour',))]
    # Add diverse perturbations, using pre-chosen evenly spaced indices.
    pool=[(s[:3],c,w,se,dr,rot,dx,sh)
          for s,c,w,se,dr,rot,dx,sh in itertools.product(
              shapes,CROWNS,WINDOWS,SENSORS,STATION_RADII,STATION_ROTS,DECK_SHIFTS,SHUTTERS)
          if (dr,rot,dx,sh)!=(0,0,0,'radial_tambour')]
    idx=np.linspace(0,len(pool)-1,656,dtype=int)
    selected=base+[pool[int(i)] for i in idx]
    assert len(selected)==2000,len(selected)
    ecache={}
    results=[]
    for shape,c,w,se,dr,rot,dx,sh in selected:
        key=(dr,rot,dx)
        if key not in ecache:ecache[key]=eye_variation(dr,rot,dx)
        eyes=ecache[key]
        vis=[visibility_one(eye,shape,c,w,se) for eye in eyes]
        cone=[visibility_one(eye,shape,c,w,se,cone=True) for eye in eyes[:2]]
        # Window area is geometric pressure-area estimate, NOT structural pane qualification.
        area=area_m2(c,w)
        outer_area=exterior_aperture_area_m2(shape,c,w)
        record=dict(shape=list(shape),crown=c,windows=w,sensors=se,
                    shift=[dr,rot,dx],shutter=sh,area_m2=area,exterior_window_m2=outer_area,
                    pilot_min=min(vis[:2]),support_min=min(vis[2:]),
                    crew_min=min(vis),pilot_cone_min=min(cone),
                    forward=vis,
                    shutter_armor_t=round(outer_area*.27,2),
                    shutter_material_m3=round(outer_area*.27/1.375,2),
                    packaging='existing_ring' if se=='ring' else 'UNVERIFIED_RELOCATION',
                    pressure_openings='UNQUALIFIED',
                    shutter_stowage='UNVERIFIED')
        results.append(record)
    # Maintain multiple objectives: performance + area + extension, no arbitrary scalar.
    feasible=[r for r in results if r['pilot_cone_min']>=.90 and r['sensors']=='ring']
    # Thin set for detailed tests: prioritize improvement and low glass area; preserve diversity.
    ranking=sorted(feasible,key=lambda x:(-x['support_min'],-x['pilot_min'],x['area_m2'],x['shape'][0]))
    shortlist=[]
    seen=set()
    for r in ranking:
        k=(tuple(r['shape']),r['windows'],r['crown'],tuple(r['shift']))
        if k not in seen:
            shortlist.append(r);seen.add(k)
        if len(shortlist)==100:break
    return shapes,results,shortlist

def true_layout(record):
    # Read real model and re-score its 0.8m-connected floor pathways.
    dr,rot,dx=record['shift']
    if (dr,rot,dx)==(0,0,0):return json.loads((ROOT/'command/l1_study_results.json').read_text())['paths']
    o=L.built_option()
    sc=o['scene']
    for i,c in enumerate(sc.couches):
        if i<2:
            if dx:
                c['eye']=(c['eye'][0]+dx,*c['eye'][1:])
                c['base_x']+=dx
                b=c['box']; c['box']=((b[0][0]+dx,b[0][1]+dx),*b[1:])
        else:
            th=np.deg2rad(rot)
            hd=np.array(c['head']);v=np.array(c['feet'])-hd
            hd*=1+dr/np.linalg.norm(hd)
            ft=hd+np.array([np.cos(th)*v[0]-np.sin(th)*v[1],np.sin(th)*v[0]+np.cos(th)*v[1]])
            sc.couches[i]=O.couch(c['id'],tuple(hd),tuple(ft),O.FLOOR,c['L'])
    return O.floor_paths(o)

def detailed(r):
    # Per-ray joint physical visibility, same direction through usable dome,
    # real Rev7 furniture, pressure aperture and exterior aperture.
    o=L.built_option(); sc=o['scene']
    eyes=eye_variation(*r['shift'])
    score={}
    for k,eye in enumerate(eyes):
        ds=CONE if k<2 else RAYS
        results={}
        for mode in ('integrated','dual'):
            geom=visibility_one(eye,tuple(r['shape']),r['crown'],r['windows'],r['sensors'],
                         cone=(k<2),double_frame=(mode=='dual'),return_mask=True)
            seen=0
            for j in np.flatnonzero(geom):
                hit,kind=O.dome_hit(sc,tuple(eye),tuple(ds[j]))
                if hit and not O.blocked(sc,tuple(eye),hit,IDS[k]):seen+=1
            results[mode]=round(seen/len(ds),4)
        score[IDS[k]]=results
    paths=true_layout(r)
    return score,paths

def main():
    shapes,results,shortlist=screen()
    # Detailed 20, including one each lowest glass area among those meeting screens.
    final_pool=shortlist[:20]
    detail=[]
    for r in final_pool:
        s,path=detailed(r)
        detail.append({**r,'detail':s,'paths':path})
    # Pareto among unperturbed/packed conservative candidates:
    rr=[r for r in results if r['sensors']=='ring' and r['pilot_cone_min']>=.9]
    nd=[]
    for r in sorted(rr,key=lambda q:(-q['support_min'],q['area_m2'])):
        if not any(q['support_min']>=r['support_min'] and q['pilot_min']>=r['pilot_min'] and
                   q['area_m2']<=r['area_m2'] and q['shape'][0]<=r['shape'][0] and
                   (q['support_min']>r['support_min'] or q['pilot_min']>r['pilot_min'] or q['area_m2']<r['area_m2'] or q['shape'][0]<r['shape'][0])
                   for q in rr):nd.append(r)
    base=json.loads((ROOT/'command/l1_study_results.json').read_text())
    out={'status':'NON-CANON | RESEARCH | NOT QUALIFIED',
         'source_sha': '3485830a56dfead79b2ef8bba031a595b536fbb5',
         'geometry_sha256':hashlib.sha256((ROOT/'out/wayfarer_v05_geometry.json').read_bytes()).hexdigest(),
         'envelope':{'tested':90,'passed':len(shapes),'by_extension':dict(Counter(str(s[0]) for s in shapes)),'shapes':shapes},
         'search':{'tested':len(results),'original_grid_total':233280,'after_envelope':72576,
                   'sensor_ring_pilot_cone_ge90':len(rr),'detailed':len(detail)},
         'baseline':{'stations':base['stations'],'paths':base['paths']},
         'pareto':nd,'shortlist':shortlist,'detail':detail,
         'warnings':['Approximate analytic cone exterior; actual plane-facet intersections not yet tested',
                     'Pressure openings are hypothetical, not structural qualifications',
                     'Sensor-relocation variants are visibility upper bounds only',
                     'Shutter areal mass does NOT demonstrate swept-volume stowage',
                     '100 preliminary shortlisted, 20 furniture/dual-frame screens',
                     'Detailed stage jointly measures pressure/exterior glazing and existing room obstructions']}
    (ROOT/'command/l1_design_search_results.json').write_text(json.dumps(out,indent=2))
    print('ENVELOPE',len(shapes),'BY EXT',out['envelope']['by_extension'])
    print('SEARCH',out['search'])
    print('BASELINE',[(k,v.get('field_of_regard',v.get('forward_hemisphere_visible'))) for k,v in base['stations'].items()])
    for r in shortlist[:12]:
        print('SHORT',r['shape'],r['crown'],r['windows'],r['sensors'],r['shift'],
              'forward',r['forward'],'cone',r['pilot_cone_min'],'area',r['area_m2'])
    for d in detail[:8]:
        print('DETAIL',d['shape'],d['crown'],d['windows'],'path',d['paths']['all_reachable_with_0.8m_path'],
              'measured_integrated',[(k,x['integrated']) for k,x in d['detail'].items()])
    print('PARETO',len(nd))

if __name__=='__main__':main()
