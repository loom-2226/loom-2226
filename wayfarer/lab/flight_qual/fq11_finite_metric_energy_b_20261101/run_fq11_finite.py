#!/usr/bin/env python3
"""FQ11 finite-state LAB replay. No Navigator or canon authority.
Actual flightlab torch and RCS phases; conditional Metric law B applied FORWARD
to measured departure state after canonical_metric_operation REQUEST/HOLD seam.
"""
import copy,hashlib,json,math,sys
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'wayfarer/lab/flight'))
from flightlab import run,canonical_metric_operation
from metric_arrival_v1 import (calculate_fq11,planetary_state,metric_elapsed,
                               phi,frame,unit,norm,hill_half,AU_KM,FROZEN_CAVEAT)

G0=9.80665
REF_TOL_M_S=1.
MU_SUN=132712440018.
SOURCE='32a4a45a4f55007bbc5162d19438cd2ffd8300fe'
GEOM='4d598212aeb46fab14b326a6023bb6d55e7d584599d91fe821ef8a2f2d837331'
CALC=ROOT/'wayfarer/lab/flight_qual/fq11_calc_metric_energy_b_20261101'
CASE=json.loads((CALC/'FQ11_INPUT.json').read_text())
BASE=json.loads((ROOT/'wayfarer/lab/flight_qual/fq_house_power_20261101/current_fq1_fq4_fixture.json').read_text())
assert CASE['main_commit']==SOURCE and CASE['geometry_sha256']==GEOM
assert hashlib.sha256((ROOT/'wayfarer/results/out/wayfarer_v05_geometry.json').read_bytes()).hexdigest()==GEOM
assert BASE['provenance']['geometry_sha256']==GEOM
MU=float(CASE['sun_gm_km3_s2']); SUN_MASS=float(CASE['sun_mass_kg'])
REF=np.array(CASE['solar_reflex_approx_km_s'],float)
E=CASE['bodies']['EA'];M=CASE['bodies']['MA']
J={'position_au':[1.100291605909785,4.957284726653116,-0.04578946808622459],
   'velocity_au_day':[-0.007466590047133519,0.001986358853434159,0.0001576742027777811],
   'gm_km3_s2':126686534.0,'source':'main ephemeris_states JU at 2226-08-29T05:00:00Z'}
def quat_rotation(q):return Rotation.from_quat([q[1],q[2],q[3],q[0]])
def scalar_quat(r):
    q=r.as_quat();return np.array([q[3],*q[:3]])
def ephe_velocity(body,t):
    return (planetary_state(body,MU,t)[1]+REF)*1000.
def stage(ship,initial,phases,dt=1.):
    ex={'name':'FQ11 finite ordinary phase', 'gravity_mu_m3_s2':MU*1e9,
        'initial':{k:np.asarray(initial[k]).tolist() for k in ('position_m','velocity_m_s','q_body_to_inertial','omega_rad_s')},
        'phases':phases}
    return run(copy.deepcopy(ship),ex,dt=dt,sample_s=1e6)
def compact_phase(p):
    return {k:p.get(k) for k in ('kind','duration_s','known_propellant_used_kg','max_ideal_tvc_trim_deg',
      'peak_force_N','peak_angular_rate_deg_s','attitude_error_deg','rate_deg_s',
      'allocation_limit_steps','gimbal_limit_steps','thrust_limit_steps','throttle_clamp_steps')}
def calculate():
    cfg=copy.deepcopy(BASE)
    card=json.loads((CALC/'METRIC_LAB_CARD.json').read_text())
    cid=card.pop('id');sourcecard=card.pop('inherit_modes_from')
    card['modes']={k:copy.deepcopy(cfg['metric'][sourcecard]['modes'][k]) for k in card.pop('allowed_modes')}
    cfg['metric'][cid]=card
    ex={'enable_metric_arrival_law_v1':True,'phases':[
      {'kind':'torch','mode':'CRUISE','duration_s':1.},
      {'kind':'metric','mode':'NORMAL','model':'lab_energy_v1','arrival_rule':'ENERGY_ORBIT_RELATIVE_B','duration_s':1.},
      {'kind':'arrival_match','duration_s':1.}],
      'metric_arrival_v1':{'source_snapshot':CASE,'main_commit':SOURCE,'source_id':'EA','destination_id':'MA',
          'rcs_reserve_kg':5000.,'arrival_match_tolerance_m_s':1.}}
    return calculate_fq11(cfg,ex)
def simulate(factor,calc):
    sh=copy.deepcopy(BASE)
    p0,v0h=planetary_state(E,MU,0.)
    v0=(v0h+REF)*1000.
    plan_v=np.array(calc['phases'][1]['pre_velocity_km_s'])*1000.
    R,_=Rotation.align_vectors([unit(plan_v-v0)],[[-1.,0.,0.]])
    init={'position_m':p0*1000.,'velocity_m_s':v0,'q_body_to_inertial':scalar_quat(R),
          'omega_rad_s':np.zeros(3)}
    requested_T=calc['phases'][0]['nominal_burn_duration_s']*factor
    pre=stage(sh,init,[{'kind':'torch','mode':'CRUISE','duration_s':requested_T,'throttle':1.,
                       'hold_attitude':False},{'kind':'coast','duration_s':5.}],dt=1.)
    pre_state=pre['final_state']
    pre_m=float(pre_state['mass_kg'])
    pre_remass=float(pre_state['tanks_kg']['remass'])
    torch_end=float(pre['phases'][-1]['actuators_end']['torch_act']['torch_centerline'])
    if abs(torch_end)>1e-10:raise ValueError('torch did not shutdown before metric')
    # Source seam remains HOLD; this is an explicit lab-only override, not canonical execution.
    canonical=canonical_metric_operation({'kind':'metric','mode':'NORMAL',
                    'duration_s':4900.,'support_scenario':'MVP_2226'},
                    {'time_s':pre_state['time_s'],'position_m':pre_state['position_m'],
                     'velocity_m_s':pre_state['velocity_m_s'],'mass_kg':pre_m,
                     'tanks_kg':pre_state['tanks_kg'],
                     'q_body_to_inertial':pre_state['q_body_to_inertial']},
                    {'torch_centerline':torch_end})
    assert canonical['execution_status']=='HOLD' and canonical['terminal_state']['velocity_m_s'] is None
    vp=np.array(pre_state['velocity_m_s'])/1000.
    pp=np.array(pre_state['position_m'])/1000.
    te=float(pre_state['time_s'])
    tmet=metric_elapsed(pp,M,MU,sh['metric']['canonical']['modes']['NORMAL'])
    pm,vm=planetary_state(M,MU,te+tmet)
    Vt=vm+REF
    Fsrc=frame(pp,planetary_state(E,MU,te)[1])
    Fdst=frame(pm,vm)
    energy_v2=norm(vp)**2+2*(phi(pp,E['gm_km3_s2'],MU)-phi(pm,M['gm_km3_s2'],MU))
    if energy_v2<=0:raise ValueError('FQ11 actual preburn still ENERGY forbidden')
    # ***FORWARD law B from measured burn-end velocity, not inverse construction***
    va=math.sqrt(energy_v2)*(Fdst@(Fsrc.T@unit(vp)))
    mismatch_m_s=norm((va-Vt)*1000.)
    # Metric E/p/L is declared balancing bookkeeping, not an independent test.
    dp=pre_m*(va-vp)*1000.
    sun_dp=-dp
    p0m=pp*1000.;p1m=pm*1000.
    spin=-np.cross(p0m,dp)
    orbit=-np.cross(p1m-p0m,pre_m*va*1000)
    Lship=np.cross(p1m,pre_m*va*1000)-np.cross(p0m,pre_m*vp*1000)
    Lsun=spin+orbit
    dEship=pre_m*(.5*(norm(va*1000)**2-norm(vp*1000)**2)+
             (phi(pm,M['gm_km3_s2'],MU)-phi(pp,E['gm_km3_s2'],MU))*1e6)
    recoil_j=norm(dp)**2/(2*SUN_MASS)
    Efield=-dEship-recoil_j
    identities={'energy_J':dEship+recoil_j+Efield,
                'momentum_N_s':norm(dp+sun_dp),
                'angular_N_m_s':norm(Lship+Lsun)}
    # 0.5 Hill diagnostic offset at arrival. No positional capture claim.
    h=hill_half(pm,M['gm_km3_s2'],MU)
    trim_init={'position_m':(pm+h*unit(pm))*1000.,'velocity_m_s':va*1000.,
               'q_body_to_inertial':np.array(pre_state['q_body_to_inertial']),
               'omega_rad_s':np.array(pre_state['omega_rad_s'])}
    sh['tanks'][0]['initial_kg']=pre_remass
    target=ephe_velocity(M,te+tmet)
    torch_dir=quat_rotation(trim_init['q_body_to_inertial']).apply([-1,0,0])
    delta,_=Rotation.align_vectors([unit(target-trim_init['velocity_m_s'])],[torch_dir])
    goal=delta*quat_rotation(trim_init['q_body_to_inertial'])
    rel=(quat_rotation(trim_init['q_body_to_inertial']).inv()*goal).as_rotvec()
    a=math.degrees(norm(rel))
    rcs=stage(sh,trim_init,[{'kind':'rcs_turn','duration_s':220.,'post_hold_s':5.,
                            'axis_vector_body':(rel/norm(rel)).tolist(),'angle_deg':a}],dt=1.)
    rcs_state=rcs['final_state']
    epoch=te+tmet+float(rcs_state['time_s'])
    pointing=quat_rotation(rcs_state['q_body_to_inertial']).apply([-1,0,0])
    current_target=ephe_velocity(M,epoch)
    requested_dv_m_s=max(0.,float((current_target-np.array(rcs_state['velocity_m_s']))@pointing))
    mass_before=rcs_state['mass_kg']
    mdot=BASE['torch'][0]['modes']['CRUISE']['working_card_mdot_kg_s']
    available_trim_water=float(rcs_state['tanks_kg']['remass'])-5000.
    available_trim_dv_m_s=2e6*math.log(mass_before/(mass_before-max(0.,available_trim_water)))
    ttrim=mass_before*(1-math.exp(-requested_dv_m_s/2e6))/mdot
    sh['tanks'][0]['initial_kg']=rcs_state['tanks_kg']['remass']
    trim=stage(sh,rcs_state,[{'kind':'torch','mode':'CRUISE','duration_s':ttrim,
           'throttle':1.,'hold_attitude':False},{'kind':'coast','duration_s':5.}],dt=.05)
    final=trim['final_state']
    last_epoch=epoch+float(final['time_s'])
    first_trim_error=norm(np.array(final['velocity_m_s'])-ephe_velocity(M,last_epoch))
    rcs_correction=None
    if first_trim_error>REF_TOL_M_S:
        # Actual final correction attempt, not a constructed velocity assignment.
        desired=ephe_velocity(M,last_epoch)-np.array(final['velocity_m_s'])
        vbody=quat_rotation(np.array(final['q_body_to_inertial'])).inv().apply(desired)
        sh['tanks'][0]['initial_kg']=final['tanks_kg']['remass']
        rcs_correction=stage(sh,final,[{'kind':'rcs_translate','duration_s':120.,
                                         'delta_v_body_m_s':vbody.tolist()}],dt=1.)
        final=rcs_correction['final_state']
        last_epoch+=float(final['time_s'])
    final_error=norm(np.array(final['velocity_m_s'])-ephe_velocity(M,last_epoch))
    final_remass=float(final['tanks_kg']['remass'])
    full_fuel=float(BASE['tanks'][0]['initial_kg'])-final_remass
    fuel_phases=[float(pre['metrics']['known_propellant_used_kg']),
                 float(rcs['metrics']['known_propellant_used_kg']),
                 float(trim['metrics']['known_propellant_used_kg'])]
    if rcs_correction:
        fuel_phases.append(float(rcs_correction['metrics']['known_propellant_used_kg']))
    fuel_err=full_fuel-sum(fuel_phases)
    # Source CRUISE thermal/crew envelope is bounded, not physical hardware proof.
    cruise=BASE['torch'][0]['modes']['CRUISE']
    peak_g=max(float(pre['phases'][0]['peak_force_N'])/float(pre['phases'][0]['mass_end_kg'])/G0,
               float(trim['phases'][0]['peak_force_N'])/float(trim['phases'][0]['mass_end_kg'])/G0)
    max_jet_power=cruise['max_N']*cruise['ve_m_s']/2.
    ship_power_ceiling=BASE['torch'][0]['jet_power_ceiling_W']
    checks={
      'finite_preburn_measured':pre['phases'][0]['known_propellant_used_kg']>0,
      'mismatch_emerges_from_forward_law':mismatch_m_s>1.,
      'trim_within_source_remass_dv_budget':requested_dv_m_s<=available_trim_dv_m_s,
      'remass_floor_5t':final_remass>=5000,
      'remass_ledger':abs(fuel_err)<.001,
      'crew_4g':peak_g<=4.,
      'thermal_jet_card_ceiling_precision':max_jet_power<=ship_power_ceiling*(1+1e-6),
      'metric_EpL_identities':abs(identities['energy_J'])<=.001 and identities['momentum_N_s']<=.001 and identities['angular_N_m_s']<1e7,
      'arrival_matches_within_1m_s':final_error<=REF_TOL_M_S,
    }
    return {
      'case':'NOMINAL' if factor==1 else 'UNDERBURN_1_PERCENT',
      'status':'PASS' if all(checks.values()) else 'HOLD',
      'checks':checks,'preburn_scale':factor,'preburn_actual_duration_s':requested_T,
      'preburn_measured_remass_kg':fuel_phases[0],
      'preburn_peak_g':float(pre['phases'][0]['peak_force_N'])/float(pre['phases'][0]['mass_end_kg'])/G0,
      'metric_canonical_seam_execution_status':canonical['execution_status'],
      'metric_seam_hand_off_velocity_km_s':vp.tolist(),
      'metric_timing_s':tmet,
      'forward_B_arrival_velocity_km_s':va.tolist(),
      'mars_target_velocity_km_s':Vt.tolist(),
      'forward_arrival_mismatch_m_s':mismatch_m_s,
      'solar_angular_transfer_N_m_s':norm(Lsun),
      'solar_spin_impulse_term_N_m_s':norm(spin),
      'solar_orbit_transport_term_N_m_s':norm(orbit),
      'solar_recoil_m_s':norm(sun_dp)/SUN_MASS,
      'metric_ledger_IDENTITIES_BY_CONSTRUCTION':identities,
      'RCS_point_turn_deg':a,'RCS_turn_attitude_error_deg':rcs['phases'][0]['attitude_error_deg'],
      'RCS_turn_peak_rate_deg_s':rcs['phases'][0]['peak_angular_rate_deg_s'],
      'trim_requested_dv_m_s':requested_dv_m_s,
      'source_derived_available_trim_dv_m_s':available_trim_dv_m_s,
      'trim_actual_torch_duration_s':ttrim,
      'trim_measured_remass_kg':fuel_phases[2],
      'RCS_turn_measured_remass_kg':fuel_phases[1],
      'trim_torch_only_velocity_error_m_s':first_trim_error,
      'trim_post_velocity_error_m_s':final_error,
      'rcs_final_correction_used':rcs_correction is not None,
      'rcs_final_correction_remass_kg':0 if rcs_correction is None else fuel_phases[-1],
      'total_remass_kg':full_fuel,'remass_remaining_kg':final_remass,
      'remass_ledger_residual_kg':fuel_err,'peak_g':peak_g,
      'cruise_peak_jet_power_W':max_jet_power,'jet_power_ceiling_W':ship_power_ceiling,
      'jet_card_rounding_overage_W':max_jet_power-ship_power_ceiling,
      'phase_evidence':{'preburn':[compact_phase(p) for p in pre['phases']],
                        'rcs_reorientation':[compact_phase(p) for p in rcs['phases']],
                        'trim':[compact_phase(p) for p in trim['phases']],
                        'rcs_final_correction':[] if rcs_correction is None else [compact_phase(p) for p in rcs_correction['phases']]},
      'limitations':[FROZEN_CAVEAT,'Canonical_metric_operation remains HOLD; separate LAB override runs forward B from actual end state.',
         'Stages use flightlab.run with exact carried position/velocity/quaternion/angular rate/tank but actuator internal states reset at staging boundaries.',
         'Crew 4g and jet card power bound only; actual fin transient thermal closure OPEN.',
         'Diagnostic half-Hill positional placement; orbital capture and moving N-body gravity OPEN.']
    }
def forbidden_ej():
    pE,vE=planetary_state(E,MU,0.)
    pJ,vJ=planetary_state(J,MU,0.)
    speed2=norm(vE+REF)**2+2*(phi(pE,E['gm_km3_s2'],MU)-phi(pJ,J['gm_km3_s2'],MU))
    return {'case':'EARTH_TO_JUPITER_NO_PREBURN','v_arrival_squared_km2_s2':speed2,
            'expected':'ENERGY_FORBIDDEN','actual':'ENERGY_FORBIDDEN' if speed2<0 else 'UNEXPECTED_ALLOWED',
            'pass':speed2<0,'frozen_potential_caveat':FROZEN_CAVEAT}
if __name__=='__main__':
    calc=calculate()
    outputs=[simulate(1.,calc),simulate(.99,calc)]
    neg=forbidden_ej()
    assert neg['pass']
    assert outputs[1]['forward_arrival_mismatch_m_s']>outputs[0]['forward_arrival_mismatch_m_s']>1.
    assert all(x['checks']['remass_floor_5t'] and x['checks']['remass_ledger'] for x in outputs)
    status='PASS' if all(x['status']=='PASS' for x in outputs) else 'HOLD'
    out={'fq':'FQ11','status':status,'classification':'DRAFT_LAB_NON_CANON_NOT_NAVIGATOR',
         'replay_baseline_main_commit':'096796311afba04b71294558b360dd09bd11112b',
         'geometry_sha256':GEOM,'frozen_potential_caveat':FROZEN_CAVEAT,
         'measured_cases':outputs,'negative_test':neg,
         'note':'FQ11 is HOLD unless nominal and 1% underburn both recover within 1m/s; closed solar E/p/L balances are identities, not pass evidence.'}
    p=HERE/'FQ11_RESULT.json'
    p.write_text(json.dumps(out,indent=2,allow_nan=False,default=lambda v:v.item() if isinstance(v,np.generic) else v.tolist() if isinstance(v,np.ndarray) else (_ for _ in ()).throw(TypeError(type(v).__name__)))+'\n')
    for x in outputs:
        print(x['case'],x['status'],'raw mismatch m/s',round(x['forward_arrival_mismatch_m_s'],3),
        'posttrim m/s',round(x['trim_post_velocity_error_m_s'],3),'remass t',round(x['total_remass_kg']/1000,3))
    print('EJ FORBIDDEN',neg['pass'],'v²',neg['v_arrival_squared_km2_s2'])
    print('FQ11',status)
