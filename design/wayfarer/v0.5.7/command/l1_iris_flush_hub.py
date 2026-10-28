"""Narrow end-seal/flush-packing evaluation for angular Wayfarer iris.

Proof obligations: 0.12m fixed centre hub, 16 clipped leaves, two staggered
levels, raised-face flush alternative and whether a stow path must cross the
solid outer armour ring.

This does not declare the iris mechanically qualified.
"""
import json, math
from pathlib import Path
import numpy as np
import l1_armoured_iris as I
import l1_fair_shutter_comparison as F

ROOT=Path(__file__).resolve().parent.parent
R=1.8
HUB=.12
SHAPE=(1.2,2.,50.)
CLOSED_X=-1.2
T=F.T
LEVEL_GAP=.020
LEVEL=T+LEVEL_GAP
TWO_LEVEL=2*T+LEVEL_GAP
OPEN_ANG=62
BLADE_OPEN_FRONT_X=-.309 # source slot 0.866m low bound +0.025m margin
LOW_OPEN_FRONT_X=BLADE_OPEN_FRONT_X+T+.030
LOW_RAISED_DEPTH=2*T+LEVEL_GAP
NODE_RADII=[math.hypot(*f['pos'][1:]) for f in F.G['features'] if f.get('kind')=='node_face' and f.get('ring')==0]

def base_poly(half_deg,inner=.12):
    # Sample thick annular-sector material rather than a zero-dimensional
    # mathematical tip. The extreme radial and angular samples are enough
    # for the conservative radial envelope check under planar rotation.
    ph=np.linspace(-math.radians(half_deg),math.radians(half_deg),35)
    return np.array([[r*math.cos(a),r*math.sin(a)]
          for r in np.linspace(inner,R,28) for a in ph])

def radial_open_extent():
    p=base_poly(360/16/2+1)
    minr=[];maxr=[]
    for a in range(OPEN_ANG+1):
        v=I.move(p,R,None,a)
        rr=np.linalg.norm(v,axis=1)
        minr.append(float(rr.min()))
        maxr.append(float(rr.max()))
    return minr,maxr

def intertier_fairing():
    # Conservatively compare full outer-tier sector against LOWER TIER's
    # raised/exposed zone with all 1deg overlap strips excluded.
    upper=I.sector(R)
    report={}
    for half in [10.25,10.0,8.0,6.0]:
        ph=np.linspace(-math.radians(half),math.radians(half),25)
        raised=np.array([[0,0]]+[[R*math.cos(a),R*math.sin(a)] for a in ph])
        overlaps=[]
        for ang in range(OPEN_ANG+1):
            a=I.move(upper,R,None,ang)
            b=I.rotate(I.move(raised,R,None,ang),22.5)
            if I.collide(a,b):overlaps.append(ang)
        report[str(half)]={'first_interference_angle':min(overlaps) if overlaps else None,
                          'interfering_samples':len(overlaps),
                          'closed_interference':0 in overlaps}
    return report

def stage_envelope():
    # Rigid sheet x coordinates in a separate axial plane; the low face is
    # raised by LEVEL so all visible centre faces could align when CLOSED.
    # The same extra material remains present during stow, so cannot be
    # "compressed away".
    rmin,rmax=radial_open_extent()
    open_rmin=min(rmin[-1],R)
    pressure_at_open_min=float(I.pressure(open_rmin))
    min_external_gap=float(np.min(I.pressure(np.linspace(R,rmax[-1],300))-
                               I.exterior(np.linspace(R,rmax[-1],300),SHAPE)))
    upper_lift=CLOSED_X-.25
    return {
       'nominal_hull_x_closed_m':CLOSED_X,
       'upper_tier_initial_x_m':CLOSED_X,
       'lower_raised_front_initial_x_m':CLOSED_X,
       'lower_raised_back_initial_x_m':round(CLOSED_X+LOW_RAISED_DEPTH,4),
       'two_level_closed_face_step_without_fairing_m':round(LEVEL,4),
       'upper_forward_lift_during_staged_open_m':-.25,
       'upper_tier_forward_lift_x_m':upper_lift,
       'upper_to_lower_x_gap_during_rotation_m':round(CLOSED_X-(upper_lift+T),4),
       'max_radial_extent_during_blade_rotations_m':round(max(rmax),4),
       'minimal_inner_radius_along_opening_m':round(min(rmin),4),
       'upper_tier_open_x_range_m':[round(BLADE_OPEN_FRONT_X,3),round(BLADE_OPEN_FRONT_X+T,3)],
       'lower_faired_tier_open_x_range_m':[round(LOW_OPEN_FRONT_X,3),round(LOW_OPEN_FRONT_X+LOW_RAISED_DEPTH,3)],
       'open_intertier_x_gap_m':round(LOW_OPEN_FRONT_X-(BLADE_OPEN_FRONT_X+T),4),
       'pressure_at_innermost_open_radial_m':round(pressure_at_open_min,4),
       'lower_blade_back_margin_to_pressure_m':round(pressure_at_open_min-(LOW_OPEN_FRONT_X+LOW_RAISED_DEPTH),4),
       'minimum_hull_to_pressure_axial_gap_over_stow_annulus_m':round(min_external_gap,4),
       'material_depth_all_two_tiers_plus_one_fixed_rear_armour_m':round(T+LEVEL_GAP+LOW_RAISED_DEPTH+T,4),
       'raw_gross_gap_suffices_for_ideal_radially_conforming_parts':min_external_gap>T+LEVEL_GAP+LOW_RAISED_DEPTH+T,
       'actual_flat_leaf_plus_fixed_backing_clearance_at_innermost_r_m':round(pressure_at_open_min-(LOW_OPEN_FRONT_X+LOW_RAISED_DEPTH+T+.02),4)
    }

def armour_crossing():
    # At full radial open pose leaves live at r~1.8-2.71. A whole leaf
    # translating from OUTSIDE the surface to INSIDE the original fixed
    # armour must cross its intact exterior shell at r>1.8. Sample 80
    # radial-angle points for a single leaf, 41 translations.
    pts=base_poly(360/16/2+1)
    vv=I.move(pts,R,None,OPEN_ANG)
    rr=np.linalg.norm(vv,axis=1)
    ext=I.exterior(rr,SHAPE)
    start_x=-1.45
    end_x=BLADE_OPEN_FRONT_X
    path=[]
    for step in range(41):
        x=start_x+(end_x-start_x)*step/40
        within=(rr>R+.005)&(x>=ext)&(x<=ext+.2)
        path.append({'t':step/40,'fixed_armour_hit_count':int(within.sum())})
    return {'sampled_blade_surface_points':len(rr),
      'some_stage_intersects_original_fixed_armour':any(p['fixed_armour_hit_count'] for p in path),
      'first_stage_intersection':next((p['t'] for p in path if p['fixed_armour_hit_count']>0),None),
      'largest_sampled_intersecting_point_count':max(q['fixed_armour_hit_count'] for q in path),
      'path':path}

def main():
    center_r,maxr=radial_open_extent()
    report={'status':'RESEARCH NON-CANON NOT QUALIFIED',
            'configuration':'50deg flat face; 16 rotating leaves, R1.8m',
            'fixed_boss_radius_m':HUB,'fixed_boss_armor_equivalent_mass_kg':round(math.pi*HUB**2*F.AREAL,2),
            'fixed_boss_nominal_closed_coverage':'r<=0.12m by solid full-density hub, r>=0.12m by sixteen clipped leaves; physical circular impact lap/seal not engineered',
            'tip_clearance_radial_m_first_and_62deg':[round(center_r[0],4),round(center_r[-1],4)],
            'raised_lower_face_interference_by_angular_width':intertier_fairing(),
            'staged_rotation_and_stow':stage_envelope(),
            'outer_armour_path_crossing':armour_crossing(),
            'limits':['Fixed boss covers exact central tip but is always visible through an otherwise open aperture',
              'The 0.216m alternating two-tier closed step is not flush',
              'A lower-leaf raised face can match the closed plane only if it is nonoverlapping with upper leaves, but once they rotate the raised zones interfere in 2D; physical separation / staged movement needed',
              'Sequential outward lift of upper leaves by .25m is a proposed kinematic work-around, not a rendered, torque-tested or mounted mechanism',
              'Open-state two-tier or three-thickness annular capacity does not prove a path: fixed exterior shoulder armour must provide an access throat or be locally relocated/rebuilt',
              'A dedicated rear annular armour backing must also fit, protecting the stowage ring when the iris is absent; no real CAD or load path',
              'Visible side-window losses found in l1_armoured_iris_results remain unchanged']}
    (ROOT/'command/l1_iris_flush_hub_results.json').write_text(json.dumps(report,indent=2))
    for k in ('fixed_boss_armor_equivalent_mass_kg','tip_clearance_radial_m_first_and_62deg',
              'raised_lower_face_interference_by_angular_width','staged_rotation_and_stow'):
        print(k,report[k])
    print('Fixed armour path intersects:',report['outer_armour_path_crossing']['some_stage_intersects_original_fixed_armour'],
          'first t:',report['outer_armour_path_crossing']['first_stage_intersection'])
if __name__=='__main__':main()
