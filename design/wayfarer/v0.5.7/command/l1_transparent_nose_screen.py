"""LOOM Wayfarer L1 transparent nose: minimum no-shutter geometry/mass screen.

RESEARCH ONLY, non-runtime, non-governing. Uses current PR432 immutable source
L1 eyes, sensors, pressure-surface geometry; angular nose research alternative.
The 27 g/cm2 number is the existing nominal opaque armour-equivalent areal
allocation, NOT a qualified impact requirement for transparent materials.

This computes transparent area, gross mass allocation, possible equivalent
physical layer thickness and clear geometry. It CANNOT predict ballistic
survival, radiation performance, optical transmittance or structural strength.
"""
import json,math
from pathlib import Path
import numpy as np
import l1_refine as REF

ROOT=Path(__file__).resolve().parent.parent
D=REF.D
SHAPE=(1.2,2.0,50)
CROWNS=(2.8,3.2,3.5)
AREAL_KG_M2=270.0
# SOURCES: National Academies AlON 3.67, NIST spinel 3.581;
# common fused silica 2.21 (transparent armour materials technical table).
MATERIALS={
 'fused_silica':{'rho_kg_m3':2210,
    'provenance':'generic measured density; not HVI window performance'},
 'spinel_MgAl2O4':{'rho_kg_m3':3581,
    'provenance':'NIST reported single crystal density 3.581 g/cm3; polycrystal may differ'},
 'ALON':{'rho_kg_m3':3670,
    'provenance':'National Academies of Sciences 3.67 g/cm3; processing-dependent'},
}
BASELINE_SNAPSHOT={'Rev7_corrected_pilot_forward_hemisphere':.6914,
 'Rev7_corrected_worst_support_forward_hemisphere':.0547,
 'source_crown_pressure_panes_t':2.13,'source_crown_frame_t':1.8,
 'source_crown_brow_t':.5,'source_crown_tracks_drives_t':.5,
 'source_crown_deck_total_t':4.93,
 'source_original_crown_glazing_approx_m2':25.0,
 'source_exterior_opaque_armour_already_in_fixed_armour_ledger':True}
BASELINE_PRESS_KG_M2=2130./25.

def line_of_sight(crown):
    eyes=REF.detail(SHAPE,crown,'radial')
    return {'worst_pilot_forward_hemisphere':min(eyes[k]['forward_integrated'] for k in ('PILOT','NAV')),
        'worst_pilot_cone60':min(eyes[k]['cone60_integrated'] for k in ('PILOT','NAV')),
        'worst_support_forward_hemisphere':min(eyes[k]['forward_integrated'] for k in ('S1','S2','S3','S4')),
        'eyes':eyes}

def fit(crown,rho):
    r=np.linspace(0,crown,3001)
    pressure=np.asarray(D.pressure_x(r))
    outer=np.asarray(D.facet_x(r,*SHAPE))
    # Conservative axial thickness of a constant-normal-depth protective
    # shell on a 50deg conical facet (t_normal/cos(theta)), flat at r<=2.
    normal=AREAL_KG_M2/rho
    ax=np.where(r<=SHAPE[1],normal,normal/math.cos(math.radians(SHAPE[2])))
    gap=pressure-outer
    available=gap-ax
    idx=int(np.argmin(available))
    return {'physical_normal_thickness_m':round(normal,6),
        'max_needed_axial_thickness_m':round(float(ax.max()),6),
        'min_exterior_to_pressure_clearance_m':round(float(gap.min()),6),
        'min_clearance_remaining_after_illustrative_exterior_protection_m':round(float(available.min()),6),
        'critical_radius_m':round(float(r[idx]),4),
        'surface_profile_geometrically_fits':bool(np.all(available>0)),
        'critical_caveat':'Does not reserve space for primary/redundant pressure panes, ribs, mounting/spacing or optical damage layers'}

def main():
    rows=[]
    for crown in CROWNS:
        pressure_area=float(D.area_m2(crown,'radial'))
        exterior_area=float(D.exterior_aperture_area_m2(SHAPE,crown,'radial'))
        baseline_areal_mass=exterior_area*AREAL_KG_M2
        vis=line_of_sight(crown)
        mats={}
        for name,mat in MATERIALS.items():
            mats[name]={**mat,**fit(crown,mat['rho_kg_m3']),
                'mass_at_same_areal_allocation_t':round(baseline_areal_mass/1000,4),
                'total_material_volume_m3':round(baseline_areal_mass/mat['rho_kg_m3'],4)}
        row={'crown_radius_m':crown,
            'external_profile':{'extension_m':1.2,'flat_radius_m':2.0,'facet_angle_deg':50},
            'external_protective_glazing_surface_area_m2':round(exterior_area,2),
            'pressure_surface_new_glazing_area_m2':round(pressure_area,2),
            'replacing_opaque_protective_areal_mass_t':round(baseline_areal_mass/1000,4),
            'scaled_source_2_13t_pressure_panes_t':round(pressure_area*BASELINE_PRESS_KG_M2/1000,4),
            'additional_press_pane_est_t_over_2_13t':round(pressure_area*BASELINE_PRESS_KG_M2/1000-2.13,4),
            'line_of_sight':vis,
            'materials_at_constant_areal_allocation':mats,
            'pressure_coverage_replaces_prior_solid_pressure_hull_portions':crown>2.8}
        rows.append(row)
        print('CROWN',crown,'external m2',row['external_protective_glazing_surface_area_m2'],
              'protected mass t',row['replacing_opaque_protective_areal_mass_t'],
              'pressure glazing m2',row['pressure_surface_new_glazing_area_m2'],
              'pilot forward',vis['worst_pilot_forward_hemisphere'],
              'support',vis['worst_support_forward_hemisphere'],
              'ALON thick cm',round(mats['ALON']['physical_normal_thickness_m']*100,2),
              'margin m',mats['ALON']['min_clearance_remaining_after_illustrative_exterior_protection_m'],flush=True)
    outcome={'classification':'RESEARCH NON-CANON NON-RUNTIME NON-GOVERNING NOT IMPACT QUALIFIED',
        'authoritative_PR432_head':'3485830a56dfead79b2ef8bba031a595b536fbb5',
        'branch':'research/wayfarer-nose-l1-search-20261028',
        'baseline':BASELINE_SNAPSHOT,
        'target':'Test no-shutter transparent outer protection + transparent pressure panes retaining source L1 eyes/rings and internal pressure profile',
        'physics_context':[
         '27 g/cm2 is the incumbent opaque armour equivalence and mass budget only. No published ALON, spinel or nanoscale composite HVI evidence supplied establishing equal functional protection.',
         'Transparency assumed optically perfect for sampled geometric LOS; real transmittance/scatter/refraction at the displayed thickness remains unqualified.',
         'No existing source pressure window extending beyond original aperture is qualified. Extending to 3.5m means replacing opaque parts of the pressure hull with structural glazing, while retaining its physical envelope and pressure barrier.',
         'Density determines volume for a given areal mass; DOES NOT determine equivalent impact resistance.',
         'Original armor on the exterior has been counted in an existing fixed armour ledger. Treat replacing its area as reallocation, not 14 tonnes of automatically added mass.',
         'The scale-up of baseline pressure panes is only an area-ratio illustration; it does not account for larger pane span, support structure, differential pressure, thermal stress or redundancy.',
         'Exterior nose is a conical/flat research geometry, not a certified triangulated aircraft/ship pressure fitting.',
         'Sensor ray masking and 4 L1 support stations unchanged; no pressure-window qualification or mechanical frame sizing.'
        ],
        'result_rows':rows}
    (ROOT/'command/l1_transparent_nose_results.json').write_text(json.dumps(outcome,indent=2))
if __name__=='__main__':main()
