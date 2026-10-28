"""Real-coordinate swept-petal experiment: one rigid 1/16 gore, two rotation signs.

Samples three layers through the 27 g/cm2 equivalent thickness, along a
curved/faceted exterior panel. A tangential hinge is placed at the outer
rim of a single azimuthal sector. Does not invent a flexible fold.
Checks pressure, fixed armor outside aperture, original bow-sensor solid,
and original ring-zero 0.35m Metric node face locations.
Non-governing; sample-based collision screen, NOT CAD closure.
"""
import json,math
from pathlib import Path
import numpy as np
import l1_fair_shutter_comparison as F
import l1_design_search as S

ROOT=Path(__file__).resolve().parent.parent
G=json.loads((ROOT/'out/wayfarer_v05_geometry.json').read_text())
SENSOR=next(p for p in G['parts'] if p['id']=='bow_sensors')['shape']
NODES=np.array([f['pos'] for f in G['features'] if f.get('kind')=='node_face' and f.get('ring')==0],dtype=float)
T=F.T
HALF=math.radians(360/16/2)

def profile_x(r,shape):
    if shape is None:return F.base_x(r)
    return float(S.facet_x(r,*shape))
def slope(r,shape):
    if shape is None:return F.base_dx(r)
    return 0 if r<=shape[1] else math.tan(math.radians(shape[2]))

def sample_panel(shape,crown,nr=48,na=9,ns=3):
    # Full aperture includes central closure, no artificial central hole
    radii=np.linspace(.015,crown,nr)
    phis=np.linspace(-HALF,HALF,na)
    depth=np.linspace(0,T,ns)
    verts=[]
    for r in radii:
        x=profile_x(float(r),shape)
        k=slope(float(r),shape)
        normalizer=math.sqrt(1+k*k)
        for phi in phis:
            y=r*math.cos(phi);z=r*math.sin(phi)
            nx,ny,nz=1/normalizer,-k*math.cos(phi)/normalizer,-k*math.sin(phi)/normalizer
            for t in depth:verts.append([x+nx*t,y+ny*t,z+nz*t])
    return np.array(verts)

def pivot(shape,crown,shift=0):
    r=crown
    k=slope(r,shape)
    n=math.sqrt(1+k*k)
    return np.array([profile_x(r,shape)-shift/n,r+shift*k/n,0.]) # standoff outward normal

def rotate_panel(points,pivot,deg):
    a=math.radians(deg);co,si=math.cos(a),math.sin(a)
    v=points-pivot
    x=pivot[0]+v[:,0]*co-v[:,1]*si
    y=pivot[1]+v[:,0]*si+v[:,1]*co
    return np.column_stack((x,y,points[:,2]))

def ring_contains(points):
    x,y,z=points.T
    r=np.hypot(y,z)
    rad=np.where(x<SENSOR['xa'],-1.,
       np.where(x>SENSOR['xc'],-1.,
       np.where(x>=SENSOR['xb'],SENSOR['R'],
        SENSOR['R']*np.sqrt(np.maximum(0,1-((SENSOR['xb']-x)/(SENSOR['xb']-SENSOR['xa']))**2)))))
    ang=np.mod(np.degrees(np.arctan2(z,y)),360)
    gap=np.zeros(len(points),dtype=bool)
    for g,hw in SENSOR['gaps']:
        gap|=np.abs((ang-g+180)%360-180)<=hw
    return (rad>=r)&(r>=SENSOR['rin'])&~gap

def masks(points,shape,crown):
    x,y,z=points.T
    r=np.hypot(y,z)
    pp=S.pressure_x(np.minimum(r,F.R_P))
    pressure=(r<=F.R_P)&(x>=pp+1e-4)&(x<=14.)
    if shape is None:
        outer=S.out_x(np.minimum(r,F.R_OUT))
    else:
        outer=S.facet_x(np.minimum(r,F.R_OUT),*shape)
    # Fixed shield is present only beyond aperture; intersection in shell layer.
    shield=(r>=crown+.002)&(r<=F.R_OUT)&(x>=outer+1e-4)&((x<pp-1e-4)|(r>F.R_P))
    sensor=ring_contains(points)
    distance=np.linalg.norm(points[:,None,:]-NODES[None,:,:],axis=2)
    node=np.any(distance<=.175,axis=1)
    return {'pressure':pressure,'fixed_armor':shield,'bow_sensor':sensor,'metric_node_face':node}

def simulate(shape,crown,sign=1,angles=range(0,181,5),shift=0):
    p=sample_panel(shape,crown)
    h=pivot(shape,crown,shift)
    samples=[]
    for ang in angles:
        q=rotate_panel(p,h,sign*ang)
        masks_at=masks(q,shape,crown)
        counts={k:int(v.sum()) for k,v in masks_at.items()}
        rad=np.hypot(q[:,1],q[:,2])
        samples.append({'angle_deg':sign*ang,'counts':counts,
                        'min_x_m':round(float(q[:,0].min()),3),
                        'max_x_m':round(float(q[:,0].max()),3),
                        'max_radial_m':round(float(rad.max()),3)})
    first={k:next((s['angle_deg'] for s in samples if s['counts'][k]>0),None) for k in samples[0]['counts']}
    return {'direction':'aft_fold_positive' if sign==1 else 'forward_flower_negative',
            'crown_m':crown,'shape':shape,'hinge_pivot_m':np.round(h,4).tolist(),
            'full_travel_clear':all(sum(s['counts'].values())==0 for s in samples),
            'first_collision_angle_deg':first,
            'max_radial_m':max(s['max_radial_m'] for s in samples),
            'most_forward_x_m':min(s['min_x_m'] for s in samples),
            'sample_count_per_angle':len(p),'angles':samples}

def main():
    result={'classification':'RESEARCH NON-GOVERNING; point-cloud sweep not CAD',
      'assumptions':{'sectors':16,'per_sector_half_angle_deg':11.25,
                     'normal_layer_equivalent_m':round(T,4),
                     'hinge':'outer perimeter, tangent to crown ring at sector centre, no stand-off',
                     'angular_step_deg':5,
                     'radial_samples':48,'azimuth_samples':9,'material_depth_samples':3,
                     'physical_meaning':'constant-thickness rigid curved or faceted 22.5-degree segment'},
      'mechanisms':[]}
    for name,shape,crown in [
        ('Rev7',None,2.8),
        ('angular_compact',(.8,1.2,35),3.2),
        ('angular_panorama',(1.2,2.,50),3.5)]:
        rec={'design':name,'tests':[]}
        for sign in (1,-1):
            s=simulate(shape,crown,sign)
            rec['tests'].append(s)
            print(name,s['direction'],'clear:',s['full_travel_clear'],
                  'first',s['first_collision_angle_deg'],'rmax',s['max_radial_m'],'x_min',s['most_forward_x_m'])
        result['mechanisms'].append(rec)
    result['limitations']=[
       'Single rigid panel only; no servo torque, hinge bracket, 16-sector self-collision, door/frame seals, impact response, folding slats or quantified rail bodies',
       'Section hinge taken tangent at sector centre, not a curved ring linkage; edge-seal mismatch is untested',
       'Sample-based swept intersections; a zero count is not a continuous-mesh guarantee',
       'Bow sensor and original Metric ring reused in place, no newly invented rearrangement',
       'Closed panel replaces existing fixed crown armor; exterior shield check begins outside crown ring']
    (ROOT/'command/l1_single_gore_sweep_results.json').write_text(json.dumps(result,indent=2))
if __name__=='__main__':main()
