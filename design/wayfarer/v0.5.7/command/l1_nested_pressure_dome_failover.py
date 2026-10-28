"""LOOM Wayfarer L1: two visually seamless independent pressure domes.

RESEARCH, non-canon. Hold 37-panel outer MMOD skin; source inner pressure
ellipsoid unchanged; translate identical outer backup dome forward by dx.

Check plausible gross spacing, weight, static pressure failover and cavity air.
No transient failure simulation, optical throughput, shell FEA or material law.
"""
from pathlib import Path
import json,math
import numpy as np
import l1_seamless_pressure_dome_screen as S
import l1_replaceable_outer_tiles as O

ROOT=Path(__file__).resolve().parent.parent
R=3.5
PCAB=101300.0 # kPa source L4/L5 isolation reference, not validated L1 design condition
ROOM_K=293.15 # illustrative, not governing ship environment
RAIR=287.05
RHO_PRESS=2210.0 # fused silica density benchmark, not selected 2226 glass
RHO_PROTECT=3670.0 # illustrative ALON outer shield reference, no validated HVI protection
AREAL_PRESS=85.2
AREAL_PROTECT=270.
T_PRESS=AREAL_PRESS/RHO_PRESS
T_PROTECT=AREAL_PROTECT/RHO_PROTECT
D_X_M=[.06,.08,.10,.12,.15,.20,.25]

def shell(shift_m=0):
    rr=np.linspace(0,R,6001)
    x=S.D.pressure_x(rr)-shift_m
    fprime=S.B*rr/(S.A*S.A*np.sqrt(1-(rr/S.A)**2))
    # A physical normal thickness t occupies t * sqrt(1+dx/dr**2) in axial
    # direction at fixed radial coordinate for local first-order offset.
    return rr,x,fprime,T_PRESS*np.sqrt(1+fprime**2)

def fit(dx):
    r,xp,fp,ppax=shell()
    xo=np.asarray(S.D.facet_x(r,*O.SHAPE))
    outer_protect_ax=np.where(r<=2.,T_PROTECT,T_PROTECT/math.cos(math.radians(50)))
    # mid-surface outer backup x=xp-dx; inner nominal x=xp
    # first-order local sheets of thickness ppax about their mid-surface.
    gap_between_pressure_ax=dx-ppax
    remaining_to_outer_shield_ax=(xp-dx-ppax/2)-(xo+outer_protect_ax)
    min_between=int(np.argmin(gap_between_pressure_ax))
    min_shield=int(np.argmin(remaining_to_outer_shield_ax))
    # Normal distance approx axial gap / sqrt(1+slope²) at given r
    cavity_normal_min=np.min(gap_between_pressure_ax/np.sqrt(1+fp**2))
    void_volume=np.trapz(2*math.pi*r*gap_between_pressure_ax,r) if np.all(gap_between_pressure_ax>0) else None
    return {'axial_center_separation_m':dx,
        'min_free_gap_between_pressure_shells_axial_m':round(float(gap_between_pressure_ax[min_between]),6),
        'min_free_gap_between_pressure_shells_normal_approx_m':round(float(cavity_normal_min),6),
        'min_shield_to_outer_pressure_shell_gap_axial_m':round(float(remaining_to_outer_shield_ax[min_shield]),6),
        'critical_r_between_pressure_m':round(float(r[min_between]),4),
        'critical_r_outer_shield_m':round(float(r[min_shield]),4),
        'inter_pressure_void_volume_m3':round(float(void_volume),6) if void_volume is not None else None,
        'gas_to_fill_cavity_at_cabin_p_and_293K_kg':round(float(PCAB*void_volume/(RAIR*ROOM_K)),4) if void_volume is not None else None,
        'positive_gross_axial_gaps':bool(np.all(gap_between_pressure_ax>0)&np.all(remaining_to_outer_shield_ax>0))}

def pressure_states(geom):
    F=geom['axial_pressure_resultant_MN']
    # cavity p maintained at vacuum by prior evacuation; normal vent isolation
    # is necessary, continuous vent open to vacuum would leak cabin if inner fails.
    states=[
     dict(event='normal',cabin_kPa=101.3,cavity_kPa=0.0,space_kPa=0.0,
          inner_diff_kPa=101.3,outer_backup_diff_kPa=0.0,
          inner_axial_force_MN=F,outer_axial_force_MN=0.,
          narrative='Inner primary bears pressure; cavity evacuated and ISOLATED; backup stands unloaded.'),
     dict(event='inner_primary_fails_stable',cabin_kPa=101.3,cavity_kPa=101.3,space_kPa=0.0,
          inner_diff_kPa=0.,outer_backup_diff_kPa=101.3,
          inner_axial_force_MN=0.,outer_axial_force_MN=F,
          narrative='If backup and both perimeter seals remain sound, cavity fills from cabin and backup takes full pressure; NOT an impact-transient prediction.'),
     dict(event='outer_backup_fails_stable',cabin_kPa=101.3,cavity_kPa=0.,space_kPa=0.0,
          inner_diff_kPa=101.3,outer_backup_diff_kPa=0.,
          inner_axial_force_MN=F,outer_axial_force_MN=0.,
          narrative='Inner primary still bears full pressure; exposed cavity is vacuum through failed backup.'),
     dict(event='both_fail',cabin_kPa=None,cavity_kPa=None,space_kPa=0.,
          inner_diff_kPa=None,outer_backup_diff_kPa=None,
          inner_axial_force_MN=None,outer_axial_force_MN=None,
          narrative='Lost pressure containment; no maintained cabin pressure is claimed.')
    ]
    for x in states[:3]:
        assert abs((x['inner_axial_force_MN']+x['outer_axial_force_MN'])-F)<1e-12
    return states

def main():
    ge=S.geometry()
    res=[fit(dx) for dx in D_X_M]
    for x in res:
        print('SEPARATION',round(x['axial_center_separation_m']*100),'cm',
              'free gap',round(x['min_free_gap_between_pressure_shells_normal_approx_m']*100,2),'cm',
              'outer shield clearance',round(x['min_shield_to_outer_pressure_shell_gap_axial_m']*100,2),'cm',
              'cavity',x['inter_pressure_void_volume_m3'],'m³',flush=True)
    assert all(x['positive_gross_axial_gaps'] for x in res)
    assert all(res[i]['inter_pressure_void_volume_m3']<res[i+1]['inter_pressure_void_volume_m3'] for i in range(len(res)-1))
    F=ge['axial_pressure_resultant_MN']
    t2=ge['curved_surface_m2']*AREAL_PRESS*2/1000
    out={'classification':'RESEARCH NON-CANON NON-RUNTIME NOT SAFE/QUALIFIED',
      'source_pr432_head':'3485830a56dfead79b2ef8bba031a595b536fbb5',
      'outer_37_held':O.PRESETS['staggered_trapezoids_compact_12'],
      'geometry':'Source original ellipsoidal pressure head for inner primary. Identical outer backup translated in -x by tested separation; same 3.5m crown. Outer shield is original fixed 37 tiles.',
      'fixed_assumptions':{'inner_shell_normal_thickness_m':T_PRESS,
         'outer_backup_shell_normal_thickness_m':T_PRESS,
         'outer_shield_normal_thickness_m':T_PROTECT,
         'nominal_reference_pressure_Pa':PCAB,
         'pressure_material':'Fused silica material-density benchmark only, not 2226 specification',
         'outer_protective_material':'ALON density benchmark only, not ballistic qualification',
         'cabin_temp_for_cavity_gas_K':ROOM_K,
         'cavity_initial_kPa':0.0,
         'cavity_must_be_isolated_from_space_during_normal_operation':True},
      'two_pressure_panes_total_material_mass_t':t2,
      'incremental_to_single_pressure_pane_t':t2/2,
      'outer_protective_37_material_allocation_t':52.888*AREAL_PROTECT/1000,
      'per_individual_pressure_shell_axial_pressure_resultant_MN':F,
      'per_individual_pressure_shell_perimeter_ideal_meridional_force_kN_per_m':
         ge['station_membrane']['3.5']['meridional_membrane_N_per_m']/1000,
      'two_pressure_shells_each_have_own_perimeter_load_path_required':True,
      'separation_sensitivity':res,
      'reference_separation_m':.12,
      'nominal_static_failover_states':pressure_states(ge),
      'limits':[
        'This models two separately sealed structural boundaries, not a laminated single monolith.',
        'Vented-to-space cavity must be isolated in service (no permanently open vent), else inner failure can vent cabin gas through the vent before pressure backup stabilizes.',
        'Stable failover states do not show dynamic rupture pressure waves, shock, acoustic loading or debris impact of failed pane into backup.',
        'At 101.3kPa nominal pressure the two shell axial projected loads are distributed by the cavity pressure; total 3.9MN, not 7.8MN simultaneously in normal quasi-static operation. Each shell attachment still must be individually capable of 3.9MN on failover.',
        'The 101.3kPa assumption is source L4/L5 isolation reference, not authoritative L1 pressure setpoint.',
        'The backup pane sits forward of the source pressure ellipsoid and requires an additional, independent sealed perimeter attachment; this is not qualified by the gross positive clearance.',
        'Same curvature shell x-translation is not the same as a constant-normal inter-shell gap; the calculated free gap and cavity are first-order axial/normal approximations.',
        'No permanent optics model of six transparent surfaces including two pressure shells and outer protective canopy.',
        'The ~7t mass omits two independent pressure perimeter rings, gap seals, mass of vents, maintenance access and structural supports.',
        'The 37 outer shield modules remain replaceable independently of the pressure system, but joints/impact equivalence are unqualified.',
        'No claim of practical manufacture, strength, thermal cycling, flaw reliability or compliant edge geometry at 7m diameter.',
        'Outer protective skin assumed not pressurized and vacuum-exposed; fracture of it does NOT imply pressure loss but may expose backup to impact.'
       ]}
    (ROOT/'command/l1_nested_pressure_dome_failover_results.json').write_text(json.dumps(out,indent=2))
    print('MASS',round(t2,3),'t two pressure shells; static loads',round(F,3),'MN',flush=True)
if __name__=='__main__':main()
