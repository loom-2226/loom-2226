"""Physical sampled sweep of compact angular crown covers, not production CAD.

Two central semicircles translate laterally ±y toward shoulders and rotate by
35deg to conform to the faceted hull. Four 40deg annular shutters slide in
azimuth to opaque angular intervals. Keep true effective 0.1963m thickness.

The central paths are best-possible externally offset for pressure/armour
clearance; this is a necessary geometric test, not a proven drive or track.
"""
import json,math
from pathlib import Path
import numpy as np
import l1_fair_shutter_comparison as F

ROOT=Path(__file__).resolve().parent.parent
SHAPE=(.8,1.2,35)
CENTER_R=1.45
OUTER_R=3.2
THICK=F.T
NODES=np.array([f['pos'] for f in F.G['features'] if f.get('kind')=='node_face' and f.get('ring')==0],float)
SENSOR=next(p['shape'] for p in F.G['parts'] if p['id']=='bow_sensors')

def surf(r):
    return np.asarray(F.S.facet_x(r,*SHAPE))
def layer(r,phi,u):
    k=np.where(np.asarray(r)<=SHAPE[1],0.0,math.tan(math.radians(SHAPE[2])))
    nx=1/np.sqrt(1+k*k);nr=-k*nx
    return np.stack((surf(r)+u*nx,(r+u*nr)*np.cos(phi),(r+u*nr)*np.sin(phi)),axis=-1)

def central(side,rad=14,ang=14):
    coords=[]
    for r in np.linspace(.055,CENTER_R-.045,rad):
        for phi in np.linspace(-math.pi/2+.03,math.pi/2-.03,ang):
            p=phi+(0 if side==1 else math.pi)
            for u in (0,THICK):
                coords.append(layer(r,p,u))
    return np.array(coords)

def ring(which,rad=12,ang=7):
    theta=math.radians([45,135,225,315][which])
    coords=[]
    for r in np.linspace(CENTER_R+.055,OUTER_R-.055,rad):
        for d in np.linspace(math.radians(-20+.7),math.radians(20-.7),ang):
            for u in (0,THICK):coords.append(layer(r,theta+d,u))
    return np.array(coords)

def cap_pose(src,side,t):
    # First lift entire panel out beyond own closed surface.
    if t<=.2: return src-np.array([(.04+THICK)*t/.2,0,0])
    u=(t-.2)/.8
    a=-side*math.radians(35)*u;co,si=math.cos(a),math.sin(a)
    v=src.copy()
    v[:,0]=co*src[:,0]-si*src[:,1]
    v[:,1]=si*src[:,0]+co*src[:,1]+side*2.8*u
    rr=np.hypot(v[:,1],v[:,2])
    # Max x (aft) that keeps all panel sampled points in FRONT of skin.
    v[:,0]+=float(np.min(surf(rr)-v[:,0]))-.04
    return v

def ring_pose(src,t):
    if t<=.2:return src-np.array([(.06+THICK)*t/.2,0,0])
    u=(t-.2)/.8;ang=-math.radians(45)*u
    out=src.copy()
    y,z=src[:,1],src[:,2]
    out[:,1]=np.cos(ang)*y-np.sin(ang)*z
    out[:,2]=np.sin(ang)*y+np.cos(ang)*z
    out[:,0]-=(THICK+.06)
    return out

def min_pair(A,B):
    # Coarse 3D pairwise sampled minimum distance. Not a triangle/continuous collision.
    d=100
    for a in np.array_split(A,12):
        m=np.sqrt(((a[:,None,:]-B[None,:,:])**2).sum(axis=2)).min()
        d=min(d,float(m))
    return d

def nearest_node(verts):
    dist=1e9
    for n in NODES:dist=min(dist,float(np.sqrt(((verts-n)**2).sum(axis=1)).min()))
    return dist

def check_surface(verts):
    r=np.hypot(verts[:,1],verts[:,2]);x=verts[:,0]
    return {'max_radius_m':float(r.max()),'min_radius_m':float(r.min()),
            'min_outside_gap_x_m':float(np.min(surf(r)-x)),
            'max_outside_gap_x_m':float(np.max(surf(r)-x)),
            'closest_node_center_m':nearest_node(verts)}

def main():
    A=[central(1),central(-1)]
    B=[ring(i) for i in range(4)]
    steps=np.linspace(0,1,11)
    outcomes=[]
    for sequence in ('central_first','ring_first','simultaneous'):
        rec={'sequence':sequence,'frames':[]}
        for t in steps:
            if sequence=='central_first':
                tc=min(1,t*2);tr=max(0,min(1,2*t-1))
            elif sequence=='ring_first':
                tr=min(1,t*2);tc=max(0,min(1,2*t-1))
            else:tc=tr=t
            caps=[cap_pose(A[0],1,tc),cap_pose(A[1],-1,tc)]
            rings=[ring_pose(b,tr) for b in B]
            moving=caps+rings
            # Ignore panel shared seams during closed pose. Distance < 0.1 implies
            # suspected material interference, but near-surface contact can false-positive.
            distances=[min_pair(c,r) for c in caps for r in rings]
            stats=[check_surface(p) for p in moving]
            rec['frames'].append({'t':round(float(t),3),'central_t':round(float(tc),3),'ring_t':round(float(tr),3),
                'minimum_central_to_ring_sample_distance_m':round(min(distances),4),
                'max_radius_m':round(max(v['max_radius_m'] for v in stats),4),
                'minimum_node_face_surface_clearance_m':round(min(v['closest_node_center_m'] for v in stats)-.175,4),
                'max_central_gap_outward_m':round(max(v['max_outside_gap_x_m'] for v in stats[:2]),3),
                'minimum_external_skin_gap_m':round(min(v['min_outside_gap_x_m'] for v in stats),4),
                })
        outcomes.append(rec)
        print(sequence)
        for f in rec['frames']:print(' ',f,flush=True)
    data={'classification':'RESEARCH / NON-GOVERNING; sampled path check not full swept-solid CAD',
      'shape':SHAPE,'central_r_m':CENTER_R,'outer_glazing_r_m':OUTER_R,
      'ring_window_centres_deg':[45,135,225,315],'ring_window_width_deg':40,
      'ring_opaque_storage_centres_deg':[0,90,180,270],
      'central_park_drifts_y_m':[-2.8,2.8],
      'effective_armour_thickness_m':THICK,'source':'PR432 unchanged geometry',
      'sequences':outcomes,'limitations':[
        'Two rigid central halves are taken from the original faceted central patch, each with fixed curvature and thickness',
        'For central translation, exterior x offset is optimistically adjusted continuously to avoid the outer skin; a real track path with required actuators is not drawn',
        '0.1m sample point distance does not certify triangle mesh intersections; optical seals and overlap not considered',
        'Fixed armour and pressure collisions are screened by exterior signed x gap only; no complete hull mesh',
        'Crown and pane structural closure, shutters impact response, rail clearance, actuator mass and power are unresolved',
        'Metric nodes screened as small face spheres, not their mounts/field requirements',
        'The central panels remain externally proud at parked pose; do not call this flush or concealed']}
    (ROOT/'command/l1_lateral_slide_sweep_results.json').write_text(json.dumps(data,indent=2))
if __name__=='__main__':main()
