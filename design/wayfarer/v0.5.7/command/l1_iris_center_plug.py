"""Single narrow closure check: a retractable 100mm-radius armour center plug.

Use PR432 unchanged pressure geometry, 50deg angular face and previously
studied 16 leaves. Model plug body as a 0.196m armor cylinder and a 130mm
radius, 6mm face lip with 3cm radial lap over truncated blades.

Sequential operation: blades move from closed to 62deg; while fully open,
plug moves aft, then sideways in the cavity to r2.5. Reverse for closing.
The actual blade lip groove and 2-level flush-face issue remain unresolved.
"""
import json,math
from pathlib import Path
import numpy as np
import l1_armoured_iris as I
import l1_fair_shutter_comparison as F

ROOT=Path(__file__).resolve().parent.parent
R=1.8
SHAPE=(1.2,2.,50.)
PLUG_BODY_R=.10
PLUG_LIP_R=.13
PLUG_DEPTH=F.T
PLUG_LIP_DEPTH=.006
REAR_CLEARANCE=.025
LEAF_BACK_GAP=.020
RADIAL_STOW=2.50
T=I.T
OPEN_DEG=62
SOURCE_BEST=next(z for z in json.loads((ROOT/'command/l1_armoured_iris_results.json').read_text())['results'] if z['shape']==list(SHAPE) and z['requested_clear_radius_m']==R)['first_usable_angle']
# With all blades still inside original flat face r<=R, open x-stack estimate:
# front-tier x = flat exterior x + common_x_shift
# second tier x = front_x + (T+.02). Both blades are 0.1963 m thick.
SHIFT=SOURCE_BEST['low_x_shift_m']+.025
FRONT_FACE=-SHAPE[0]+SHIFT
REAR_FACE=FRONT_FACE+(2*T+I.GAP)
STOW_PLUG_X=REAR_FACE+LEAF_BACK_GAP

def pressure(x,r):return I.pressure(r)

def path():
    out=[]
    # Step 1: plug extracts axially into free front cavity after blades opened.
    parked_center_x=float(I.pressure(0))-PLUG_DEPTH-REAR_CLEARANCE
    for t in np.linspace(0,1,51):
        out.append(('axial',t,0.,-SHAPE[0]+(parked_center_x+SHAPE[0])*t))
    # Step 2: plug slides to stow radially. Chosen x coordinate maximizes
    # space behind the leaf backing while keeping 25mm pressure clearance.
    for r in np.linspace(0,RADIAL_STOW,126):
        max_ax=float(I.pressure(max(0,r-PLUG_LIP_R)))-PLUG_DEPTH-REAR_CLEARANCE
        x=min(STOW_PLUG_X+.012,max_ax)
        out.append(('lateral',r/RADIAL_STOW,float(r),float(x)))
    return out

def verify_path():
    result=[]
    for phase,t,r,x in path():
        # Sample outside lip and full plug body; actual pressure head shape;
        # 130mm lip is 6mm thick and the main body has armour-equivalent depth.
        worst_pressure=float('inf')
        worst_exterior=float('inf')
        leaf_offset=float('inf')
        for rr in np.linspace(max(0,r-PLUG_LIP_R),r+PLUG_LIP_R,13):
            pr=float(I.pressure(float(rr)))
            back=x+(PLUG_DEPTH if abs(rr-r)<=PLUG_BODY_R+.001 else PLUG_LIP_DEPTH)
            worst_pressure=min(worst_pressure,pr-back)
            # exterior gap: positive x inside hull, negative outside it.
            ext=float(I.exterior(float(rr),SHAPE))
            worst_exterior=min(worst_exterior,x-ext)
        # Tip exceeds projected blade hole radius at 62deg only if r+lipR>1.7953.
        if r+PLUG_LIP_R>=SOURCE_BEST['center_clear_radius_m'] and phase=='lateral':
            leaf_offset=x-REAR_FACE
        result.append({'stage':phase,'progress':round(float(t),3),'plug_axis_radius_m':round(r,4),
            'front_x_m':round(x,4),'minimum_pressure_gap_m':round(worst_pressure,4),
            'lip_front_to_shell_gap_m':round(worst_exterior,4),
            'blade_back_axial_clearance_if_overlap_m':None if not math.isfinite(leaf_offset) else round(leaf_offset,4)})
    return result

def center_screen():
    # Same 224 + 256 sightline samples, original L1 eye/furniture, source sensor ring.
    D=I.D;REF=I.REF
    center_only=(.1,.12,.13)
    candidate=I.visibility('central with window ring',SHAPE,R,SOURCE_BEST['max_leaf_radial_m']+.04)
    saved_a,saved_f=D.aperture,D.frame_hit
    views=[]
    for hub in center_only:
        r_outer=SOURCE_BEST['max_leaf_radial_m']+.04
        def ap(r,phi,c,pat):
            alpha=np.minimum.reduce([np.abs(D.angdiff(phi,u)) for u in (45,135,225,315)])
            return ((r>=hub)&(r<=R))|((r>=r_outer)&(r<=3.5)&(alpha<=20))
        def fr(r,phi,c,pat):
            alpha=np.minimum.reduce([np.abs(D.angdiff(phi,u)) for u in (45,135,225,315)])
            return (abs(r-R)<.04)|((r>=r_outer)&((abs(r-r_outer)<.04)|(abs(r-3.5)<.04)|(abs(alpha-20)*np.pi/180*r<.04)))
        D.aperture,D.frame_hit=ap,fr
        try:st=REF.detail(SHAPE,3.5,'radial')
        finally:D.aperture,D.frame_hit=saved_a,saved_f
        views.append({'hub_radius_m':hub,'pilot_cone60':min(st[k]['cone60_integrated'] for k in ('PILOT','NAV')),
          'pilot_forward':min(st[k]['forward_integrated'] for k in ('PILOT','NAV')),
          'support_forward':min(st[k]['forward_integrated'] for k in ('S1','S2','S3','S4'))})
    return {'without_fixed_hub':{k:v for k,v in candidate.items() if k!='stations'},'with_fixed_hub':views}

def main():
    sweep=verify_path()
    pmin=min(z['minimum_pressure_gap_m'] for z in sweep)
    emax=max(z['lip_front_to_shell_gap_m'] for z in sweep)
    k=[z['blade_back_axial_clearance_if_overlap_m'] for z in sweep if z['blade_back_axial_clearance_if_overlap_m'] is not None]
    clearance=min(k) if k else None
    iris_closed_sector_coverage_degrees=360/I.N+2*I.OVER_DEG
    out={'status':'RESEARCH NON-CANON NOT QUALIFIED','design':'+1.2m, 50deg, R1.8m iris',
       'plug':{'body_radius_m':PLUG_BODY_R,'face_lip_radius_m':PLUG_LIP_R,
               'armor_equivalent_body_depth_m':round(PLUG_DEPTH,5),
               'lip_depth_m':PLUG_LIP_DEPTH,
               'nominal_mass_body_only_kg':round(math.pi*PLUG_BODY_R**2*F.AREAL,2),
               'closed_body_front_x_m':-SHAPE[0],
               'closed_body_rear_x_m':round(-SHAPE[0]+PLUG_DEPTH,3),
               'parked_ring_center_radial_m':RADIAL_STOW,
               'rear_leaf_face_x_m':round(REAR_FACE,4),
               'minimum_pressure_head_gap_path_m':round(pmin,4),
               'minimum_axial_gap_behind_open_blades_m':None if clearance is None else round(clearance,4)},
       'blade':{'closed_sector_coverage_width_deg':iris_closed_sector_coverage_degrees,
                'center_hole_radius_m':PLUG_BODY_R,
                'outer_face_step_even_odd_m':round(T+I.GAP,4),
                'same_tier_2d_collision_test':'prior 0-62deg pass',
                'kinematics':'2-level rigid wedge rotation, common x-translation, no real rail'},
       'center_coverage':'Closed disk idealized fully covered: annular 16 rotating leaves r>=.10 plus full-density central body r<=.10, overlap lip to .13; finite gasket/closure seam NOT modeled',
       'path_samples':len(sweep),
       'plug_sweep':sweep,
       'visibility':center_screen(),
       'limitations':['No actual gasket tolerance or recess cut; cap contact/lip engagement and finite seam not verified',
         'Sequential operation requires all iris leaves opened before withdrawing/parking center plug and cap centered before final close; if cap remains installed throughout rotation, leaf-tip cutout must be rechecked',
         'Hub plug is body mass only; drive and mechanical support not counted',
         'Common model has alternating exterior face step 0.216m; closed face is NOT flush',
         'Parked cap in an ideal empty layer behind blade stack assumes no rail, node or support at that location',
         'The axial swept plug test uses circle/radial bounds, not full collision mesh or actual plug-bearer',
         'Optical fixed boss alternative reduces view; retracted cap leaves iris open with no permanent boss']}
    (ROOT/'command/l1_iris_center_plug_results.json').write_text(json.dumps(out,indent=2))
    print('plug body',out['plug'])
    print('path bounds pressure min',pmin,'blade x-gap min',clearance,'samples',len(sweep))
    print('fixed hub views',out['visibility'])
if __name__=='__main__':main()
