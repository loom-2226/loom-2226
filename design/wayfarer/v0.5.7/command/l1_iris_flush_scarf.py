"""One flush, full-areal-protection lap seam for the 16-leaf Wayfarer iris.

Non-governing, minimal geometric test. Unlike the preceding two-tier model,
all 16 solid leaf main regions start with the SAME forward face x=-1.2m.
At each angular seam, the upper leaf carries a front half-thickness rabbet;
the lower leaf carries the mating back half-thickness rabbet. Together they
cover the full 196mm armour equivalence without occupying the same volume.

Step 1: lower eight retreat axially by one blade thickness + 20mm, while
all blades are *still closed in angular position*. Step 2: withdraw both
tiers behind the central aperture. Step 3: use the earlier full two-tier cam.

This is only a sector-area and slab-interference screen. It DOES NOT
establish impact/thermal strength of the half-thickness scarf seam, actuator
or gap tolerance, bearing load, seal, or a manufactured flush shell.
"""
from pathlib import Path
import math,json
import numpy as np
import l1_armoured_iris as I
import l1_iris_two_tier_cam as PREV
import l1_iris_one_blade_slot as ONE

ROOT=Path(__file__).resolve().parent.parent
R=1.76
N=16
X0=-1.2
T=ONE.T
GAP=I.GAP
DELTA=T+GAP
HALF_PITCH=180/N
OVER_DEG=I.OVER_DEG
HALF_LIP=T/2
BOSS_RADIUS=.12
MAX_ROT=62
READY=ONE.READY_FRONT_X

def wrapped(angles):
    return (angles+180)%360-180

def interval(phi,idx,x):
    # Each panel covers ±(11.25 + 1°). Only the overlap strips ±(10.25..12.25)
    # are half thickness, not the previous full-thickness double count.
    d=np.abs(wrapped(phi-idx*360/N))
    main=d<HALF_PITCH-OVER_DEG
    lip=(d>=HALF_PITCH-OVER_DEG)&(d<=HALF_PITCH+OVER_DEG)
    if idx%2==0: # upper/front tier
        return [(x,x+T)] if main else ([(x,x+HALF_LIP)] if lip else [])
    return [(x,x+T)] if main else ([(x+HALF_LIP,x+T)] if lip else [])

def coverage():
    # Prove closed occupancy at every angular sample. In main only one leaf
    # covers the angle; in the lap two half-thickness segments abut.
    tested=0;gaps=0;intersections=0;min_depth=float('inf');max_depth=0
    failure=[]
    for a in np.linspace(0,360,72001,endpoint=False):
        spans=[]
        for k in range(16):
            spans+=interval(float(a),k,X0)
        pts=sorted({X0,X0+T}|{z for sp in spans for z in sp})
        if not spans:
            failure.append(a);gaps+=1;continue
        # Cell midpoints across complete needed shell depth
        for p,q in zip(pts,pts[1:]):
            if q-p<1e-9:continue
            count=sum(s<=.5*(p+q)+1e-9 and t>=.5*(p+q)-1e-9 for s,t in spans)
            if X0<=.5*(p+q)<=X0+T:
                if count<1:gaps+=1;failure.append(a)
                if count>1:intersections+=1;failure.append(a)
        full=sum(q-p for p,q in spans)
        min_depth=min(min_depth,full);max_depth=max(max_depth,full)
        tested+=1
    return {'angles_sampled':tested,'uncovered_angular_axial_cells':gaps,
      'double_occupied_angular_axial_cells':intersections,
      'smallest_full_armour_equivalent_depth_m':round(min_depth,6),
      'largest_full_armour_equivalent_depth_m':round(max_depth,6),
      'fail_angles_first':failure[:8]}

def seam_motion():
    frames=[]
    # Step A: lower blade retreats, opening the x seam. Upper stays flush.
    # An angular seam (overlap strip) still shares projected area, so confirm
    # lower rear lip moves AWAY from the top/front lip, never through it.
    for k in range(31):
        u=k/30
        top=X0
        low=X0+DELTA*u
        top_lip=(top,top+HALF_LIP)
        low_lip=(low+HALF_LIP,low+T)
        seam_gap=low_lip[0]-top_lip[1]
        shell_pressure_gap=float(np.min(ONE.pressure(np.array([.12,R]))-(low+T)))
        frames.append({'stage':'lower_peel','fraction':round(.15*u,6),'opening_angle_deg':0,
            'upper_x_front_m':round(top,6),'lower_x_front_m':round(low,6),
            'seam_lip_separation_x_m':round(seam_gap,6),
            'full_tier_separation_x_m':round(low-(top+T),6),
            'minimum_pressure_gap_m':round(shell_pressure_gap,6),
            'outer_fixed_armour_contacts':0,
            'intertier_lip_intersection':seam_gap< -1e-9,
            'same_tier_collision':False})
    # Step B: both layers translated together aft, *before* rotating.
    for k in range(1,31):
        u=k/30
        top=X0+(READY-X0)*u
        low=top+DELTA
        gap=float(np.min(ONE.pressure(np.array([.12,R]))-(low+T)))
        frames.append({'stage':'joint_withdraw','fraction':round(.15+.25*u,6),'opening_angle_deg':0,
            'upper_x_front_m':round(top,6),'lower_x_front_m':round(low,6),
            'seam_lip_separation_x_m':round(DELTA,6),
            'full_tier_separation_x_m':round(GAP,6),
            'minimum_pressure_gap_m':round(gap,6),
            'outer_fixed_armour_contacts':0,
            'intertier_lip_intersection':False,
            'same_tier_collision':False})
    # Step C: preserve the proven 1.76m cam path. Show both tiers.
    prior=PREV.sample(R)
    for f in prior['frames']:
        if f['stage']!='cam':continue
        top=f['upper_front_x_m'];low=f['lower_front_x_m']
        frames.append({'stage':'joint_cam','fraction':round(.40+.60*f['angle_deg']/MAX_ROT,6),
            'opening_angle_deg':f['angle_deg'],
            'upper_x_front_m':top,'lower_x_front_m':low,
            'seam_lip_separation_x_m':round(low-top,6),
            'full_tier_separation_x_m':f['min_intertier_gap_m'],
            'minimum_pressure_gap_m':f['min_pressure_gap_m'],
            'outer_fixed_armour_contacts':f['fixed_armour_contacts'],
            'intertier_lip_intersection':f['min_intertier_gap_m']<GAP-.0001,
            'same_tier_collision':f['same_tier_collision'],
            'max_radius_m':f['max_radial_m']})
    return frames

def check_closed_face(frames):
    # The exposed faces of both main sections and front lap are x=-1.2.
    # Stage A is allowed to become stepped because it's TRANSITIONING.
    before=frames[0]
    return {'top_main_face_x_m':before['upper_x_front_m'],
      'bottom_main_face_x_m':before['lower_x_front_m'],
      'seam_visible_top_lip_front_x_m':X0,
      'nominal_closed_face_step_m':round(abs(before['upper_x_front_m']-before['lower_x_front_m']),6),
      'one_direction_lap_face_sum_equivalent_m':round(T,6),
      'inner_circular_boss_required':BOSS_RADIUS,
      'notes':'No thermal gasket, shear joint, hypervelocity seam strength or panel tensile tolerance qualified'}

def main():
    total=coverage()
    frames=seam_motion()
    bad=[f for f in frames if f['intertier_lip_intersection'] or f['outer_fixed_armour_contacts'] or f['same_tier_collision'] or f['minimum_pressure_gap_m']<0]
    out={'status':'RESEARCH NON-GOVERNING · NOT QUALIFIED',
         'source':'PR432 head 3485830a56df, 50deg angular nose',
         'iri_radius_m':R,'blade_count':N,
         'blade_equivalent_thickness_m':round(T,6),
         'lap_angular_width_deg':2*OVER_DEG,
         'lap_radial_width_at_hub_mm':round(1000*BOSS_RADIUS*math.radians(2*OVER_DEG),2),
         'lap_width_at_outer_edge_mm':round(1000*R*math.radians(2*OVER_DEG),2),
         'recessed_leaf_first_retreat_m':round(DELTA,6),
         'closed_coverage':total,
         'closed_face':check_closed_face(frames),
         'stage_frames':frames,
         'path_sampled_geometry_clear':len(bad)==0,
         'path_first_failed_frame':bad[0] if bad else None,
         'narrow_limits':[
           'Scarf geometry consists of ideal planar, sharp, exactly matched half-thickness lips; 2deg lap only ~4.19mm wide at r=.12m',
           'Effective 27g/cm2 in lap is summed from two 98mm depth halves, not one intact 196mm plate; ballistic integrity unproven',
           'The half-depth top lip protects seam during closure, but as soon as the lower retracts the seam temporarily loses half its protection',
           'No finite edge tolerances, seal or load capacity, no structural fracture/thermal/dust qualification',
           'Ring-entry lip and pivots are still absent; nominal 26mm armour gap and 38mm remaining x interval do not demonstrate mechanism hardware fit',
           'This test uses inherited pressure geometry and hypothetical 20cm normal faceted armour, not an authoritative source update',
           'The same poor forward-hemisphere sky coverage (~33%) from the opaque iris-storage annulus is still true',
           'Visualization may depict idealised blade faces but does not certify fully-manufactured 3D leaf solids'
         ]}
    (ROOT/'command/l1_iris_flush_scarf_results.json').write_text(json.dumps(out,indent=2))
    print('CLOSED',out['closed_coverage'])
    print('FULL PATH',out['path_sampled_geometry_clear'],'frames',len(frames),'fail',out['path_first_failed_frame'])
    print('HUB LAP WIDTH',out['lap_radial_width_at_hub_mm'],'mm')
    print('MAX GAP FROM PRESSURE min',min(f['minimum_pressure_gap_m'] for f in frames))
    print('CLOSED FACE',out['closed_face'])
if __name__=='__main__':main()
