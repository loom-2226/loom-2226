"""Iris armour feasibility on Wayfarer Rev7 pressure head and two angular noses.

A deliberately narrow 16-leaf, 2-tier rigid wedge iris. Arc polygons move by
rotation about off-axis pivots. Tests true closed angular union by construction,
same-tier leaf collisions with convex SAT, centred open-disc clearance, annular
stow extent, and actual x-profile pressure/outer armour slot for two thick layers.

RESEARCH / NON-GOVERNING. An iris with a real manufactured full seal at x=0,
pivot hardware, bearings and actual crash-impact armour remains unqualified.
"""
import json,math
from pathlib import Path
import numpy as np
import l1_fair_shutter_comparison as F
import l1_refine as REF

ROOT=Path(__file__).resolve().parent.parent
D=REF.D
N=16
PIVOT_RADIAL_EXTRA_M=.07
PIVOT_ANGLE_DEG=22.0
ANGLE_SPAN=2*math.pi/N
OVER_DEG=1.0
T=F.T
GAP=.020
TWO_TIER=2*T+GAP
FRONT_MARGIN=.02
BACK_MARGIN=.02

def sector(R):
    tt=np.linspace(-math.pi/N-math.radians(OVER_DEG),math.pi/N+math.radians(OVER_DEG),25)
    return np.array([[0.,0.]]+[[R*math.cos(t),R*math.sin(t)] for t in tt])

def move(poly,R,piv_delta,deg):
    pivot=(R+PIVOT_RADIAL_EXTRA_M)*np.array([math.cos(math.radians(PIVOT_ANGLE_DEG)),math.sin(math.radians(PIVOT_ANGLE_DEG))])
    a=math.radians(deg);c,s=math.cos(a),math.sin(a)
    rot=np.array([[c,-s],[s,c]])
    return (poly-pivot)@rot.T+pivot

def rotate(poly,deg):
    a=math.radians(deg);c,s=math.cos(a),math.sin(a)
    return poly@np.array([[c,s],[-s,c]])

def radial(poly):
    edge=np.roll(poly,-1,axis=0)-poly
    v=np.clip(-np.einsum('ij,ij->i',poly,edge)/(np.einsum('ij,ij->i',edge,edge)+1e-30),0.,1.)
    foot=poly+v[:,None]*edge
    return float(np.min(np.linalg.norm(foot,axis=1))),float(np.max(np.linalg.norm(poly,axis=1)))

def collide(A,B):
    # Separating axis for 2D convex leaf polygon, excludes mere edge contact.
    for P in (A,B):
        v=np.roll(P,-1,axis=0)-P
        norm=np.column_stack((-v[:,1],v[:,0]))
        for axis in norm:
            if np.max(A@axis)<=np.min(B@axis)+1e-9 or np.max(B@axis)<=np.min(A@axis)+1e-9:
                return False
    return True

def pressure(r):
    return np.asarray(D.pressure_x(np.minimum(r,F.R_P)))

def exterior(r,shape):
    return np.asarray(D.facet_x(r,*shape))

def detailed_sheet(R,shape):
    # Dense actual radial and angular material samples for 3D pressure slot.
    rr=np.linspace(.01,R,50)
    aa=np.linspace(-math.pi/N-math.radians(OVER_DEG),math.pi/N+math.radians(OVER_DEG),15)
    xy=np.array([[r*math.cos(a),r*math.sin(a)] for r in rr for a in aa])
    x=exterior(np.linalg.norm(xy,axis=1),shape)
    return xy,x

def slot(shape,R,deg):
    xy,x=detailed_sheet(R,shape)
    c=move(xy,R,None,deg)
    r=np.linalg.norm(c,axis=1)
    # Original panel outer surface x(r) rotates rigidly around x-axis; an
    # independent longitudinal translation is permitted.
    outside=r>R+.005
    # For opaque storage lip, original hull boundary is still present.
    if np.any(outside):
        low=float(np.max(exterior(r[outside],shape)-x[outside]+FRONT_MARGIN))
    else:low=-float('inf')
    if np.any(r>F.R_P):up=-float('inf')
    else:up=float(np.min(pressure(r)-x-TWO_TIER-BACK_MARGIN))
    return {'low_x_shift_m':round(low,4) if np.isfinite(low) else None,
            'high_x_shift_m':round(up,4) if np.isfinite(up) else None,
            'axial_shift_slot_m':round(up-low,4) if np.isfinite(low) else None,
            'two_tier_press_clear_possible':(not np.isfinite(low)) or low<=up,
            'min_radius_m':round(float(r.min()),4),
            'max_radius_m':round(float(r.max()),4)}

def simulate(name,shape,R):
    P=sector(R)
    frames=[]
    for theta in range(0,91,1):
        q=move(P,R,None,theta)
        rmin,rmax=radial(q)
        overlap=any(collide(q,rotate(q,360*k/N)) for k in (2,4,6,8,10,12,14))
        ss=slot(shape,R,theta)
        frames.append({'angle_deg':theta,
            'center_clear_radius_m':round(rmin,4),
            'max_leaf_radial_m':round(rmax,4),
            'same_tier_overlap':overlap,**ss})
    best=next((v for i,v in enumerate(frames) if v['center_clear_radius_m']>=R-.01 and
          all(not f['same_tier_overlap'] and f['two_tier_press_clear_possible'] for f in frames[:i+1])),None)
    # Never relabel a snapshot-only clear state as path-cleared.
    rmax=best['max_leaf_radial_m'] if best else None
    return {'design':name,'shape':shape,'requested_clear_radius_m':R,'blade_count':N,
        'pivot_radius_m':round(R+PIVOT_RADIAL_EXTRA_M,3),
        'pivot_relative_angle_deg':PIVOT_ANGLE_DEG,
        'closed_angular_sector_width_deg':round(360/N+2*OVER_DEG,3),
        'closed_coverage_of_disk':'100% analytic angular wedge coverage for all 0<r<=R; exact centre / finite edge seal NOT qualified',
        'same_tier_leaf_count':N//2,
        'nominal_blade_area_all_m2':round(math.pi*R*R*(1+(2*OVER_DEG*N/360)),3),
        'nominal_blade_armor_mass_t':round(math.pi*R*R*(1+(2*OVER_DEG*N/360))*F.AREAL/1000,3),
        'two_tier_nominal_axial_depth_m':round(TWO_TIER,4),
        'first_usable_angle':best,
        'stow_annulus':None if not best else {'r_inner_m':R,'r_outer_m':rmax,
            'radial_width_m':round(rmax-R,3),'area_m2':round(math.pi*(rmax*rmax-R*R),3)},
        'frames':frames}

def visibility(name,shape,R,r_outer):
    # Reserve full radial iris storage ring r=R..r_outer as opaque.
    # Pilot/NAV see through central open iris only; add outer four 40-degree
    # viewing windows from r_outer to original crown radius.
    crown=3.2 if shape[0]==.8 else 3.5
    pcenters=[45,135,225,315]
    def alpha(phi):
        return np.minimum.reduce([np.abs(D.angdiff(phi,u)) for u in pcenters])
    def aperture(r,phi,c,pat):
        return (r<=R)|((r>=r_outer)&(r<=crown)&(alpha(phi)<=20))
    def frame(r,phi,c,pat):
        central=abs(r-R)<.04
        rim=(abs(r-r_outer)<.04)|(abs(r-crown)<.04)
        seams=abs(alpha(phi)-20)*np.pi/180*r<.04
        return central|((r>=r_outer)&(rim|seams))
    orig_a,orig_f=D.aperture,D.frame_hit
    D.aperture,D.frame_hit=aperture,frame
    try:st=REF.detail(shape,crown,'radial')
    finally:D.aperture,D.frame_hit=orig_a,orig_f
    return {'worst_pilot_cone60':min(st[k]['cone60_integrated'] for k in ('PILOT','NAV')),
        'worst_pilot_forward':min(st[k]['forward_integrated'] for k in ('PILOT','NAV')),
        'worst_support_forward':min(st[k]['forward_integrated'] for k in ('S1','S2','S3','S4')),
        'stations':st}

def main():
    models=[simulate('compact +0.8m /35deg',(.8,1.2,35),R) for R in (1.2,1.45)]
    models +=[simulate('panorama +1.2m /50deg',(1.2,2.,50),R) for R in (1.6,1.8)]
    for m in models:
        good=m['first_usable_angle']
        if good:
            m['associated_window_layout_visibility']=visibility(m['design'],m['shape'],m['requested_clear_radius_m'],good['max_leaf_radial_m']+.04)
        print(m['design'],'R',m['requested_clear_radius_m'],'best',None if not good else {k:v for k,v in good.items() if k!='angle_deg'}|{'angle_deg':good['angle_deg']},
              'vis',m.get('associated_window_layout_visibility',{}).get('worst_pilot_forward'),flush=True)
    data={'status':'RESEARCH NON-GOVERNING MECHANISM SEARCH NOT CERTIFIED','source':'PR432 source head 3485830a56df',
      'model':'16 rigid wedge petals with full-closure overlap and alternating axial levels, rotating about off-axis pivots (not the image’s exact curved leaves)',
      'protection_areal_kg_m2':F.AREAL,'effective_density_t_m3':round(F.DENSITY/1000,4),
      'single_blade_thickness_m':round(T,4),'two_level_stack_depth_m':round(TWO_TIER,4),
      'blade_edge_angular_overlap_deg':OVER_DEG,'axial_tier_gap_m':GAP,
      'results':models,
      'unqualified':['Closed exact center, central plug/seal, edge loads and impact resistance',
       'Axial tiers create offset face steps unless additional panel articulation or deeply recessed seat; not shown flush',
       'The sampled 2D convex-polygon SAT verifies same-tier overlap only; each leaf is thick and cross-tier joins/rails are unmodeled',
       'A theoretical signed longitudinal slot for all leaves simultaneously is NOT a validated physical path/actuator',
       'The iris parking region makes an opaque radial band, reducing the panoramic side glazing',
       'No seals, pressure-pane structural qualification, dust erosion, motor torque or sensor obscuration proof']}
    (ROOT/'command/l1_armoured_iris_results.json').write_text(json.dumps(data,indent=2))
if __name__=='__main__': main()
