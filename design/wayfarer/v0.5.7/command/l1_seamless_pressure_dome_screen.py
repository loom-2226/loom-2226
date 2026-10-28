"""Non-canon 7m seamless transparent pressure dome mechanics screen.

Known source geometry: x=2.35-2.15*sqrt(1-(r/4.3)^2); r <=3.5m.
Membrane *idealization* for shallow ellipsoid under uniform internal pressure.
External protective 37-pane arrangement HELD and unmodified.
Pressure-borne axial support resultant vs optics and ideal material flaw sensitivity.
No shell edge bending, fatigue, thermoelastic FEA, fracture qualification.
"""
import json,math
from pathlib import Path
import numpy as np
import l1_design_search as D
import l1_replaceable_outer_tiles as O

ROOT=Path(__file__).resolve().parent.parent
A=float(D.RP);B=float(D.HD)
R=3.5
PRESSURE_PA=101300.0 # a reference 1-atm equivalent from crew system 101.3kPa, not verified L1 structural setpoint
G=9.80665
G_CASE=4.0 # crew accel doctrine sustained cap reference; not a vessel structural load qualification
BASE_PANE_AREA_M2=25.
BASE_PANE_MASS_KG=2130.
AREAL=BASE_PANE_MASS_KG/BASE_PANE_AREA_M2
# rho reference and property data stated in model source notes; not a universal material batch property.
MATS={
 'fused_silica':{'density_kg_m3':2210,'elastic_modulus_GPa':72.1,'poisson':.17,
                 'cte_micro_per_K':.55,'KIC_MPa_sqrt_m':.75,
                 'source':'NIST ceramics data portal / NASA ISS fused silica window fracture paper; density common reference'},
 'transparent_spinel':{'density_kg_m3':3580,'elastic_modulus_GPa':271,'poisson':.26,
                 'cte_micro_per_K':5.9,'KIC_MPa_sqrt_m':1.9,
                 'source':'NRL Optica optical ceramics published table (2015)'},
 'ALON':{'density_kg_m3':3770,'elastic_modulus_GPa':323,'poisson':.24,
                 'cte_micro_per_K':5.7,'KIC_MPa_sqrt_m':1.4,
                 'source':'NRL Optica optical ceramics published table (2015): 3.77 g/cm3, grain/process variable'},
}
def geometry():
    r=np.linspace(1e-5,R,12001)
    z=1-(r/A)**2
    fp=B*r/(A*A*np.sqrt(z))
    fpp=B/(A*A)*z**(-1.5)
    meridian_curvature=fpp/(1+fp*fp)**1.5
    hoop_curvature=fp/(r*np.sqrt(1+fp*fp))
    # Balance axial pressure force on cap 0..r against meridional
    # tension around circular cut. Ring total axial component N_s * 2pi*r*sin(theta),
    # sin(theta) = fp / sqrt(1+fp^2).
    N_mer=PRESSURE_PA*r*np.sqrt(1+fp*fp)/(2*fp)
    # local normal equilibrium p = N_mer * k_mer + N_hoop*k_hoop.
    N_hoop=(PRESSURE_PA-N_mer*meridian_curvature)/hoop_curvature
    dr=r[1]-r[0]
    area=float(np.trapz(2*math.pi*r*np.sqrt(1+fp**2),r))
    axial_force=PRESSURE_PA*math.pi*R**2
    station={}
    for ra in [0.,1.,2.,3.,3.5]:
        i=int(np.argmin(abs(r-max(ra,1e-5))))
        station[str(ra)]={'r_m':float(r[i]),'meridional_membrane_N_per_m':float(N_mer[i]),
            'hoop_membrane_N_per_m':float(N_hoop[i]),'meridian_radius_curvature_m':float(1/meridian_curvature[i]),
            'hoop_radius_curvature_m':float(1/hoop_curvature[i]),
            'surface_slope_dx_dr':float(fp[i])}
    top_N=max(float(np.max(abs(N_mer))),float(np.max(abs(N_hoop))))
    return dict(pressure_shape_a_m=A,pressure_shape_b_m=B,transparent_radius_m=R,
      projected_aperture_m2=math.pi*R*R,curved_surface_m2=area,
      axial_pressure_resultant_MN=axial_force/1e6,
      perimeter_ring_circumference_m=2*math.pi*R,
      max_abs_membrane_N_per_m=top_N,station_membrane=station,
      all_meridional_tension=bool(np.all(N_mer>=0)),all_hoop_tension=bool(np.all(N_hoop>=-1e-8)),
      max_radial_bending_source='Membrane idealization deliberately EXCLUDES boundary-bending stress, thermal mismatch, flange fasteners and pressure load redistribution')

def flaw_radius(KIC, sigma_MPa,Y=1.12):
    # stress intensity K_I=Y*sigma*sqrt(pi*a); assumed mode-I surface flaw
    return (KIC/(Y*sigma_MPa*math.sqrt(math.pi)))**2

def material_cases(geo):
    rows={}
    N=geo['max_abs_membrane_N_per_m']
    for name,m in MATS.items():
        rho=m['density_kg_m3'];E=m['elastic_modulus_GPa']*1e9;alpha=m['cte_micro_per_K']*1e-6
        t=AREAL/rho
        s=N/t/1e6
        p4=AREAL*G_CASE*G
        # a body-acceleration normal-load scale (not force field superposition nor structural FEA)
        s_acc=s*(p4/PRESSURE_PA)
        thermal_proxy=[(dt,(E*alpha*dt/(1-m['poisson']))/1e6) for dt in (10.,20.,40.)]
        pressure_flaw=flaw_radius(m['KIC_MPa_sqrt_m'],s)
        worst_20=s+thermal_proxy[1][1]  # illustrative upper-bound algebra, not actual thermoelastic solution
        results={'normal_thickness_m_at_source_areal_mass':t,
          'full_single_dome_mass_t':geo['curved_surface_m2']*AREAL/1000,
          'source_like_areal_mass_kg_m2':AREAL,
          'ideal_pressure_max_membrane_stress_MPa':s,
          'acceleration_4g_normal_inertial_pressure_proxy_kPa':p4/1000,
          'incremental_ideal_4g_membrane_stress_if_aligned_MPa':s_acc,
          'fully_constrained_thermal_stress_proxy_MPa_by_delta_T_K':{str(int(x)):float(y) for x,y in thermal_proxy},
          'mode_I_surface_flaw_critical_length_mm_pressure_only':1000*pressure_flaw,
          'mode_I_surface_flaw_critical_length_mm_pressure_plus_20K_fully_clamped_upper_proxy':1000*flaw_radius(m['KIC_MPa_sqrt_m'],worst_20),
          'fully_independent_two_panes_each_same_thickness_mass_t':2*geo['curved_surface_m2']*AREAL/1000,
          'half_source_mass_per_pane_dual_case_pressure_stress_MPa':2*s,
          'ideal_t_for_5_MPa_MPa_tension_m':N/(5e6),
          'ideal_t_for_10_MPa_MPa_tension_m':N/(10e6),
          'ideal_t_for_20_MPa_MPa_tension_m':N/(20e6),
          'source_properties':m}
        rows[name]=results
    return rows

def main():
    geo=geometry()
    assert abs(geo['curved_surface_m2']-41.38)<.06
    assert abs(geo['axial_pressure_resultant_MN']-3.899)<.01
    assert geo['all_meridional_tension']
    # Compare transparent window mass to original already booked source pressure panes
    result={'classification':'RESEARCH NON-CANON NON-GOVERNING NO FEA NO WINDOW QUALIFICATION',
      'upstream_PR432_source':'3485830a56dfead79b2ef8bba031a595b536fbb5',
      'held_outer_37_panels':O.PRESETS['staggered_trapezoids_compact_12'],
      'pressure_assumption':'101.3 kPa from source L4/L5 crew isolation setpoint used as analog, not independently verified for L1',
      'acceleration_assumption':'4 g from crew accel_doctrine sustained cap, NOT a quantified dome support load case',
      'prior_inner_2p13t_pressure_panes_based_on_25m2':True,
      'geometry':geo,'material_sensitivity':material_cases(geo),
      'cautions':[
       'Linear thin-shell axisymmetric membrane equilibrium ignores bending stresses and stress concentrations at perimeter supports, joints and thermal gradients.',
       'Elastic material modulus and KIC are borrowed from published 2015 NRL ceramic measurements / NIST silica; flaw model assumes Y=1.12 and is only fracture-mechanics scaling, not probability or proof test.',
       'Full clamping thermal proxy is an upper-bound stress scale, not actual field: free thermal expansion gives much lower restraint; gradients may cause bending.',
       'Transparent 7m across is a hypothetical manufacturable 2226 pane, not proven size, structural reliability or long-term optical/thermal cycle performance.',
       'Perimeter mount is mandatory: visually frameless does NOT mean structurally support-free.',
       'Single shell creates a single full-pressure failure boundary; laminated layers do not automatically offer independent backup. A second separately sealed pressure shell and its cavity/venting would need real design if strict loss-of-one-layer redundancy is required.',
       'Reference total 85.2kg/m2 is an existing window-area/mass ratio and not a real approved 2226 material property; new surface area and perimeter support alter actual ledger.',
       'Outer 37-piece impact layer held fixed; cannot assume it fully protects inner pane from all damage, crack growth, thermal stress or cosmic radiation.',
       'Pressure shape is original oblate ellipsoidal 2.15m-deep bow pressure head; only r<=3.5m exchanged for transparent shell.',
       'Using pressure alone to declare safety would be false; flaw reliability, material manufacture at 7m and perimeter integration remain blocking.'
       ]}
    for name,props in result['material_sensitivity'].items():
        print(name,'t mm',round(props['normal_thickness_m_at_source_areal_mass']*1000,2),
              'mass t',round(props['full_single_dome_mass_t'],3),
              'ideal max stress MPa',round(props['ideal_pressure_max_membrane_stress_MPa'],2),
              'flaw pressure only mm',round(props['mode_I_surface_flaw_critical_length_mm_pressure_only'],3),
              'thermal upper @20K MPa',round(props['fully_constrained_thermal_stress_proxy_MPa_by_delta_T_K']['20'],1),
              'flaw combined 20K mm',round(props['mode_I_surface_flaw_critical_length_mm_pressure_plus_20K_fully_clamped_upper_proxy'],3),flush=True)
    print('geometry',geo,flush=True)
    (ROOT/'command/l1_seamless_pressure_dome_screen_results.json').write_text(json.dumps(result,indent=2))
if __name__=='__main__':main()
