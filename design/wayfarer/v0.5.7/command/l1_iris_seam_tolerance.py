"""Small finite-tolerance/impact-geometry screen for LOOM iris scarf seam.

Do not derive ballistic limits from areal density. Published NASA/ESA impact
science requires threat velocity/density/angle, target constitutive behavior,
and tested multilayer arrangement; none are demonstrated for the 2226 shield.

Checks:
1) 2/3/4 degree overlap against full 16-blade cam and open clear circle.
2) Finite opposing edge errors of 0.25..3 mm near 120mm fixed boss.
3) Correct normal thickness with optional 0.5..2 mm axial interface gaps
   requires local projecting rear lips and reduces cam clearance.
4) Local angular ray-channel necessary conditions for shallow/canted impact.
"""
import json,math
from pathlib import Path
import numpy as np
import l1_armoured_iris as I
import l1_iris_two_tier_cam as CAM
import l1_iris_one_blade_slot as ONE

ROOT=Path(__file__).resolve().parent.parent
N=16
R=1.76
HUB=.12
T=ONE.T
PITCH=360/N
THREAT_ANGLES_DEG=[0,15,30,45,60,75]

def finite_at(r,overlap_deg,edge_mm):
    """Two complementary full slabs and their half-depth lips in a seam.

    epsilon is *per* projected circumferential boundary, each shrunk inward
    by epsilon. This is an illustrative misregistration/tolerance model,
    not a statistical distribution or proven manufacturing specification.
    """
    w=r*math.radians(overlap_deg)
    e=edge_mm/1000
    # When there is a trimmed boundary, front and back tongues still
    # span most of the seam, but uncovered full-density edge strips exist.
    full_max_overlap_m=max(0,w-2*e)
    part_width_m=2*min(e,max(0,w-e)) if e<w else 0
    zero_width_m=max(0,2*e-w)
    min_depth_m=T if e==0 else (0.0 if zero_width_m>0 else T/2)
    # total seam understrength area per all 16 radial seams, integrated
    # analytically as two e-wide strips if e<w/2 at every radius.
    return {
      'radius_m':r,'nominal_lap_width_mm':round(w*1000,4),
      'edge_error_per_lip_mm':edge_mm,
      'remaining_both_lips_overlap_mm':round(full_max_overlap_m*1000,4),
      'some_only_one_half_lip':e>0,
      'direct_projected_gap_mm':round(zero_width_m*1000,4),
      'minimum_local_normal_material_depth_m':round(min_depth_m,6),
      'minimum_nominal_local_protection_g_cm2':round(27*min_depth_m/T,4),
      'tangential_angle_needed_to_cross_between_lips_in_1mm_axial_gap_deg':
         round(math.degrees(math.atan2(full_max_overlap_m,.001)),2) if full_max_overlap_m>0 else 0
    }

def integrate_understrength(overlap_deg,error_mm):
    # Understrength strip area in closed circle, before physical edge
    # supports or finite ballistic response. Approximate widths for
    # sector seams against radius.
    dr=np.linspace(HUB,R,25001)
    e=error_mm/1000
    w=dr*math.radians(overlap_deg)
    # Region where only one half-density lip remains in x projection:
    # at e<=w/2 width 2e; with e>w/2 middle direct hole replaces part.
    half_width=np.maximum(0,2*np.minimum(e,np.maximum(0,w-e)))
    hole_width=np.maximum(0,2*e-w)
    weak_area=N*float(np.trapz(half_width,dr))
    hole_area=N*float(np.trapz(hole_width,dr))
    crown=math.pi*(R*R-HUB*HUB)
    return {'overlap_deg':overlap_deg,'edge_error_mm':error_mm,
       'under_half_density_area_m2':round(weak_area,6),
       'unarmoured_projected_hole_area_m2':round(hole_area,8),
       'fraction_of_central_annulus_below_full_density':round((weak_area+hole_area)/crown,8),
       'note':'Best-case ideal rectangular lips; not a ballistic or perforation probability'}

def cam_variant(overlap_deg):
    previous=I.OVER_DEG
    try:
        I.OVER_DEG=overlap_deg/2
        # PREV.sample calls I.sector and PREV.sample_blade with I.OVER_DEG.
        rec=CAM.sample(R)
    finally:
        I.OVER_DEG=previous
    return {'overlap_deg':overlap_deg,
       'nominal_open_angle_deg':62,
       'same_tier_clear':not rec['any_same_tier_collision'],
       'fixed_armor_clear':not rec['any_fixed_armour_contact'],
       'pressure_and_armor_path_clear':rec['necessary_sampled_path_clear'],
       'opening_radius_m':rec['open_center_clear_radius_m'],
       'radial_aperture_goal_R_minus_1cm_met':rec['open_center_clear_radius_m']>=R-.01,
       'outer_extent_m':rec['open_max_radius_m'],
       'remaining_x_positioning_interval_m':rec['end_available_x_interval_m']}

def main():
    variants=[cam_variant(a) for a in [2.,3.,4.]]
    tolerances=[]
    for lap in [2.,3.,4.]:
        for edge in [0,.25,.5,1.,2.,3.]:
            rr=[finite_at(r,lap,edge) for r in (HUB,0.3,1.,R)]
            tolerances.append({'overlap_deg':lap,'edge_error_mm':edge,
              'by_radius':rr,
              'integrated':integrate_understrength(lap,edge)})
    iface_gaps=[]
    for gap_mm in [.25,.5,1.,2.,5.]:
        # A rear lip can retain a full T column only if it extends an
        # extra "gap" behind the otherwise flush front material stack.
        # No manufacturing shape/mount is verified.
        iface_gaps.append({'gap_mm':gap_mm,
          'normal_27g_cm2_preserved_with_rearward_extra_lip_if_both_lips_present':True,
          'needed_extra_rearward_m':gap_mm/1000,
          'remaining_open_x_interval_m':round(variants[0]['remaining_x_positioning_interval_m']-gap_mm/1000,5),
          'if_total_installed_lap_depth_held_fixed_with_undercut_g_cm2':
           round(27*(1-gap_mm/1000/T),4),
          'note':'A gap within the same T external-to-internal depth costs material thickness; preserving full material length needs a locally rear-projecting tongue, not a manufactured or impact-verified seam'})
    out={'status':'RESEARCH NON-GOVERNING; FINITE TOLERANCE COMPATIBILITY NOT HVI QUALIFICATION',
      'source':'PR432 Rev7 source + research angular 50deg R1.76 iris',
      'geometry':'16 half-depth scarfed leaves, fixed radius .12m center boss',
      'nominal_protection_g_cm2':27,
      'nominal_full_leaf_depth_m':round(T,6),
      'nominal_two_half_lips_depth_m':round(T,6),
      'variants':variants,
      'finite_angular_clearances':tolerances,
      'axial_interface_gaps':iface_gaps,
      'important_caveats':[
        'Any nonzero adverse edge retreat creates half-density slivers at least. Original 72,001 angle closed proof was exactly zero tolerance.',
        'Areal-density of two separated 98mm lips does not establish HVI equivalence to one intact 196mm plate. For impact certification need specified particle density, size, speed, angle and material law/test.',
        'Unpressurized cabin remains behind original unchanged pressure hull. No iris leaf occupies that cabin in the hypothetical geometry.',
        'Numbers are deterministic geometry sensitivity, not probability estimates, tolerancing process capability or ballistic limits.',
        'Finite axial gapping makes a mating joint less than full depth unless compensated by an unverified custom rear lip; more room cost at open.',
        'No physical pressure-ring throat, cam bearing, actuator or joint stiffness solved. Full closed face is only idealized coplanar.',
        'Broad panoramic hemisphere still only ~33%, vs 69% Rev7 reference.']
    }
    (ROOT/'command/l1_iris_seam_tolerance_results.json').write_text(json.dumps(out,indent=2))
    print('VARIANTS')
    for v in variants:print(v)
    print('AT HUB: tolerances')
    for v in tolerances:
        if v['edge_error_mm'] in (.5,1.,2.,3.):
            q=v['by_radius'][0]
            print(v['overlap_deg'],v['edge_error_mm'],'hub lap',q['nominal_lap_width_mm'],
               'remaining',q['remaining_both_lips_overlap_mm'],
               'full-depth nominal local min',q['minimum_nominal_local_protection_g_cm2'],
               'hole width',q['direct_projected_gap_mm'],
               'area affected',v['integrated']['under_half_density_area_m2'],
               'hole m2',v['integrated']['unarmoured_projected_hole_area_m2'])
    print('AXIAL GAP',iface_gaps)
if __name__=='__main__':main()
