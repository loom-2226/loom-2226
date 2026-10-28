"""Single rigid Wayfarer iris leaf: entry at central aperture lip, then
axially cam under the *intact* fixed shoulder armor as it rotates.

Compares with rotate-first/retract-after, which hit that armour in prior work.
NON-CANON/non-qualified. No physical bearing or throat seal is claimed.

Model assumptions:
* 50deg conical outer nose, flat r<=2.0m; full disk shutter R=1.8m.
* Fixed shoulder armor from r>=1.8, >=0.20m normal thickness.
  Source Rev7 original amour is an ellipsoid shell t=.20m, but the angular
  armor plate normals here are a new necessary-assumption experiment.
* One flat 0.1963m armoured rigid blade. The bottom of leaf can translate
  aft along x inside central open aperture BEFORE rotating and then cam.
* Unchanged original pressure head, unchanged sensor and Metric ring.
"""
from pathlib import Path
import numpy as np
import json,math
import l1_armoured_iris as I
import l1_fair_shutter_comparison as F

ROOT=Path(__file__).resolve().parent.parent
R=1.8
SHAPE=(1.2,2.0,50)
T=F.T
NORMAL_ARMOR_M=.20
COS_FACE=math.cos(math.radians(SHAPE[2]))
END_ANGLE=62
MIN_GAP=.025
FRONT_ARMOR_X_THICKNESS= NORMAL_ARMOR_M / COS_FACE
CLOSED_FRONT_X=-SHAPE[0]
READY_FRONT_X=CLOSED_FRONT_X+FRONT_ARMOR_X_THICKNESS+MIN_GAP

def panel_points():
    # Truncated real 16-leaf geometry, including angular overlap.
    # Three through-thickness samples for stationary-armour occupancy.
    a=np.linspace(-math.pi/I.N-math.radians(I.OVER_DEG),
                  math.pi/I.N+math.radians(I.OVER_DEG),29)
    r=np.linspace(.12,R,48)
    return np.array([[rv*math.cos(aa),rv*math.sin(aa)]
                    for rv in r for aa in a],float)

def outer(r):
    return np.asarray(I.exterior(r,SHAPE))
def pressure(r):
    return np.asarray(I.pressure(r))

def bounds(xy):
    radius=np.linalg.norm(xy,axis=1)
    band=radius>=R+1e-5
    min_front=float(np.max(outer(radius[band])+FRONT_ARMOR_X_THICKNESS+MIN_GAP)) if np.any(band) else -float('inf')
    max_front=float(np.min(pressure(radius)-T-MIN_GAP))
    return min_front,max_front

def stage_result(t,deg,x,xy):
    rr=np.linalg.norm(xy,axis=1)
    p=pressure(rr)
    ext=outer(rr)
    # Original fixed armor shell: r>1.8, x ranging over outward profile + normal shell thickness.
    # Classify collision only if leaf prism and shell overlap in axial x, not merely surfaces.
    fixed=(rr>=R+1e-5)&(x<ext+FRONT_ARMOR_X_THICKNESS-1e-6)&(x+T>ext+1e-6)
    min_p=float(np.min(p-(x+T)))
    min_fixed_shell_sep=float(np.min(x-(ext[rr>=R+1e-5]+FRONT_ARMOR_X_THICKNESS))) if np.any(rr>=R+1e-5) else None
    return {'stage_t':round(t,4),'angle_deg':round(float(deg),4),'x_front_m':round(float(x),4),
      'x_back_m':round(float(x+T),4),'max_r_m':round(float(rr.max()),4),
      'min_r_m':round(float(rr.min()),4),
      'fixed_armour_intersections':int(np.sum(fixed)),
      'min_pressure_gap_m':round(min_p,4),
      'min_fixed_shell_sep_m':None if min_fixed_shell_sep is None else round(min_fixed_shell_sep,4)}

def cam_path():
    base=panel_points()
    p=[]
    # Pull back axially through the central aperture, while still CLOSED.
    for n in range(31):
        u=n/30
        x=CLOSED_FRONT_X+(READY_FRONT_X-CLOSED_FRONT_X)*u
        p.append(stage_result(u*.25,0.,x,base))
    x=READY_FRONT_X
    # Next follow the intact armour underside as blade area moves radially outward.
    for deg in range(1,END_ANGLE+1):
        moving=I.move(base,R,None,deg)
        low,high=bounds(moving)
        x=max(x,low+.001)
        result=stage_result(.25+.75*deg/END_ANGLE,deg,x,moving)
        result['permitted_high_x_front_m']=round(high,4)
        result['permitted_low_x_front_m']=round(low,4) if math.isfinite(low) else None
        result['axial_available_m']=round(high-low,4) if math.isfinite(low) else None
        p.append(result)
    return p

def rotate_then_retract():
    b=panel_points()
    path=[]
    # Retain the idealised naive sequence for direct comparisons
    for deg in range(END_ANGLE+1):
        path.append(stage_result(.7*deg/END_ANGLE,deg,CLOSED_FRONT_X,I.move(b,R,None,deg)))
    rotated=I.move(b,R,None,END_ANGLE)
    low,_=bounds(rotated)
    for n in range(1,31):
        x=CLOSED_FRONT_X+(low+.001-CLOSED_FRONT_X)*n/30
        path.append(stage_result(.7+.3*n/30,END_ANGLE,x,rotated))
    return path

def fixed_rear_ring():
    # If original shoulder armour remains intact around open blade, the
    # protected ring is already covered: no new backing is needed.
    # Check only the radial 1.8..2.71 footprint against the original pressure.
    radius=np.linspace(R,2.72,200)
    skin_ax=outer(radius)+FRONT_ARMOR_X_THICKNESS
    pressure_gap=pressure(radius)-(skin_ax+T+MIN_GAP)
    return {'original_fixed_armor_preserved':True,
      'minimum_gap_between_normal_armor_inner_face_and_pressure_m':round(float(np.min(pressure(radius)-skin_ax)),4),
      'minimum_gap_with_single_leaf_and_25mm_margin_m':round(float(pressure_gap.min()),4),
      'note':'Local r-dependent gap not necessarily a manufacturable flat leaf slot; cam trajectory samples rigid flat leaf at each angle'}

def two_tier_necessary_interval():
    base=panel_points();rows=[]
    for theta in range(1,END_ANGLE+1):
        xy=I.move(base,R,None,theta)
        low,_=bounds(xy)
        rr=np.linalg.norm(xy,axis=1)
        high=float(np.min(pressure(rr)-2*T-I.GAP-MIN_GAP))
        rows.append({'angle_deg':theta,'available_interval_m':round(high-low,4)})
    return {'minimum_available_m':round(min(z['available_interval_m'] for z in rows),4),
            'last_open_angle_available_m':rows[-1]['available_interval_m'],
            'note':'For two stacked leaves, unlike the one-leaf cam path; physical seams and bearings not counted'}

def main():
    good,bad=cam_path(),rotate_then_retract()
    O={'status':'RESEARCH NON-GOVERNING; necessary point-cloud swept-prism collision checks',
       'shape':SHAPE,'iris_R_m':R,'blade_thickness_m':round(T,4),
       'armor_normal_depth_m':NORMAL_ARMOR_M,
       'armor_thickness_x_on_50deg_facet_m':round(FRONT_ARMOR_X_THICKNESS,4),
       'throat_r_m':R,'throat_requirement':'circumferential slot at central aperture edge must pass 0.196m blade thickness and retain strength/seals',
       'cam_path':good,'naive_path':bad,'fixed_shoulder_check':fixed_rear_ring(),
       'two_tier_same_path_necessary_interval':two_tier_necessary_interval(),
       'cam_results':{'max_fixed_shell_intersections':max(s['fixed_armour_intersections'] for s in good),
           'min_pressure_gap_m':min(s['min_pressure_gap_m'] for s in good),
           'min_shell_clearance_during_rotation_m':min(s['min_fixed_shell_sep_m'] for s in good if s['min_fixed_shell_sep_m'] is not None),
           'min_axial_available_m':min(s['axial_available_m'] for s in good if s.get('axial_available_m') is not None),
           'max_radius_m':max(s['max_r_m'] for s in good),
           'end_x_front_m':good[-1]['x_front_m']},
       'naive_results':{'max_fixed_shell_intersections':max(s['fixed_armour_intersections'] for s in bad),
           'first_intersection_stage_t':next((s['stage_t'] for s in bad if s['fixed_armour_intersections']>0),None)},
       'not_demonstrated':['Radial throat physical width for bearing rails and lip load path',
         'Closed return-to-flush seal after axial travel',
         'Real actuator motion and contact dynamics',
         'How 16 blade hinges fit, and all layers close flush',
         'Alternating tier leaves; only one blade physically screened',
         'Original bow sensor clearance of all actuator hardware',
         'Armour strength/redundancy at the 360-degree entry gap']}
    (ROOT/'command/l1_iris_one_blade_slot_results.json').write_text(json.dumps(O,indent=2))
    print('CAM',O['cam_results'])
    print('NAIVE',O['naive_results'])
    print('TWO_TIER',O['two_tier_same_path_necessary_interval'])
    print('RING',O['fixed_shoulder_check'])
    print('FIRST CAM',[(s['angle_deg'],s['x_front_m'],s['min_pressure_gap_m'],s.get('axial_available_m'))
             for s in good if s['angle_deg'] in [0,1,10,20,30,40,50,60,62]][::2])
if __name__=='__main__':main()
