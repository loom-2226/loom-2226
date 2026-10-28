"""Minimum mechanical-fit screen for matched iris interlocking seams.

Evaluates geometry under finite clearance and staged axial withdrawal.
No impact mechanics, materials law, or protection qualification.
"""
from pathlib import Path
import json,math
import numpy as np
import l1_iris_seam_tolerance as OLD
import l1_armoured_iris as IRIS
import l1_iris_two_tier_cam as CAM

ROOT=Path(__file__).resolve().parent.parent
T=OLD.T
R=1.76
HUB=.12
SHAPES={
    'straight_scarf':([0.,1.],[.5,-.5]),
    'releasable_dogleg':([0.,1/3,2/3,1.],[.5,.35,-.35,-.5]),
    'reverse_lap_labyrinth':([0.,1/3,2/3,1.],[-.5,.5,-.5,.5])
}

def check_shape(name,lap_deg,error_mm):
    depths,relative=SHAPES[name]
    width=HUB*math.radians(lap_deg)
    x=np.array(depths)*T
    y=np.array(relative)*width
    gap=2*error_mm/1000
    xx=np.linspace(0,T,2001)
    f=np.interp(xx,x,y)
    # Matched parts separated by a total geometric clearance gap.
    ss=np.linspace(-width/2-gap,width/2+gap,1001)
    void=np.abs(ss[:,None]-f[None,:])<gap/2
    largest_void_depth_m=float(void.mean(axis=1).max()*T)
    # A pure axial peel moves the lower blade backward; any expanding
    # undercut along x forces the two moving solids to interpenetrate.
    worst_interference=0
    for travel in np.linspace(0,T,101):
        points=xx>=travel
        v=np.interp(xx[points]-travel,x,y)
        overlap=np.max(f[points]-v-gap)
        worst_interference=max(worst_interference,float(overlap))
    return {'type':name,'lap_deg':lap_deg,'edge_recession_mm':error_mm,
       'hub_nominal_lap_width_mm':round(width*1000,4),
       'max_lateral_interpenetration_during_axial_peel_mm':round(worst_interference*1000,4),
       'axially_releasable':worst_interference<=1e-8,
       'max_normal_void_depth_mm':round(largest_void_depth_m*1000,4),
       'nominal_material_depth_remaining_at_weakest_cross_section_mm':round((T-largest_void_depth_m)*1000,4),
       'note':'Only two-dimensional geometric occupancy, not mechanical/ballistic performance'}

def cam_check(deg):
    original=IRIS.OVER_DEG
    try:
        IRIS.OVER_DEG=deg/2
        q=CAM.sample(R)
    finally:IRIS.OVER_DEG=original
    return {'lap_deg':deg,'full_cam_sampled_clear':q['necessary_sampled_path_clear'],
       'open_clear_radius_m':q['open_center_clear_radius_m'],
       'signed_room_for_actuators_m':q['end_available_x_interval_m']}

def main():
    rows=[]
    for overlap in (2.,3.,4.):
        for name in SHAPES:
            for e in (.25,.5,1.,2.):
                rows.append(check_shape(name,overlap,e))
    cams=[cam_check(deg) for deg in (2.,3.,4.)]
    for c in cams:print('CAM',c,flush=True)
    for r in rows:
        if r['edge_recession_mm']==.5:
            print('JOINT',r,flush=True)
    data={'status':'RESEARCH NON-CANON NOT QUALIFIED',
       'source':'PR432 Rev7 3485830a + experimental 1.76m angular iris',
       'assumptions':'Blade edge modeled as a two-dimensional matched dividing curve across the full nominal panel depth. Clearance gap equals twice adverse edge recession.',
       'normal_equivalent_material_reference_m':T,
       'hub_radius_m':HUB,'radius_m':R,
       'cam_motion':cams,'seam_cross_section_checks':rows,
       'limits':['This is mechanical edge clearance and material occupancy, not a hypervelocity impact model.',
          'A 2D releasable joint does not demonstrate a manufactured 16-blade mechanism.',
          'The underlying 20cm normal exterior armour on angular facets is a declared test assumption.',
          'No bearing, seal, finite impact strength, cyclic fatigue or joint stiffness qualified.',
          'The earlier iris broad forward-hemisphere visibility deficit still applies.']}
    (ROOT/'command/l1_iris_joint_kinematics_results.json').write_text(json.dumps(data,indent=2))
if __name__=='__main__':main()
