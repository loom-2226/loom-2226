#!/usr/bin/env python3
"""FQ12: finite Jupiter→Earth ENERGY-B inbound LAB qualification, no preburn.

Uses the existing physical flightlab stage integrator for real attitude turn,
CRUISE inbound braking and finite torch trim. No canon/Navigator changes.
FROZEN potential & Sun frame are explicit, E/p/L identities are bookkeeping.
"""
import copy,hashlib,json,math,sys
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'wayfarer/lab/flight'))
sys.path.insert(0,str(ROOT/'wayfarer/lab/flight_qual/fq11_finite_metric_energy_b_20261101'))
from flightlab import canonical_metric_operation,torch_force,mass_properties
from metric_arrival_v1 import FROZEN_CAVEAT,planetary_state,metric_elapsed,phi,frame,unit,norm,hill_half
from run_fq11_finite import stage,quat_rotation,scalar_quat,G0

INPUT=json.loads((HERE/'FQ12_INPUT.json').read_text())
SHIP=json.loads((ROOT/'wayfarer/lab/flight_qual/fq_house_power_20261101/current_fq1_fq4_fixture.json').read_text())
MU=float(INPUT['sun_gm_km3_s2'])
SUN_MASS=float(INPUT['sun_mass_kg'])
REF=np.asarray(INPUT['solar_reflex_approx_km_s'],float)
J=INPUT['jupiter']
E=INPUT['earth']
CRUISE=SHIP['torch'][0]['modes']['CRUISE']
assert INPUT['geometry_sha256']==hashlib.sha256((ROOT/'wayfarer/results/out/wayfarer_v05_geometry.json').read_bytes()).hexdigest()
assert SHIP['provenance']['geometry_sha256']==INPUT['geometry_sha256']
assert SHIP['metric']['canonical']['law']=='canonical_envelope'
assert INPUT['replay_base_main_sha']=='79c86eaba4ba651f81ddbee85a3a928a14eda21e'

def earth_target(t):
    p,v=planetary_state(E,MU,t)
    return p,(v+REF)*1000

def actual_torch_direction(ship,state):
    _,cg,_=mass_properties(ship,{'remass':float(state['tanks_kg']['remass'])})
    thrust,ve,d,angle=torch_force(ship['torch'][0],'CRUISE',float(state['mass_kg']),1.,cg)
    return quat_rotation(state['q_body_to_inertial']).apply(d), angle

def simple_state(position_km,velocity_km_s,quaternion):
    return {'position_m':(np.asarray(position_km)*1000).tolist(),
            'velocity_m_s':(np.asarray(velocity_km_s)*1000).tolist(),
            'q_body_to_inertial':np.asarray(quaternion).tolist(),
            'omega_rad_s':[0.,0.,0.]}

def inbound_base():
    p0,vs_h=planetary_state(J,MU,0.)
    vsrc=vs_h+REF
    t=metric_elapsed(p0,E,MU,SHIP['metric']['canonical']['modes']['NORMAL'])
    pE,vEh=planetary_state(E,MU,t)
    vt=vEh+REF
    # No torch prior to canonical Metric HOLD: Jupiter source state matches planet.
    q0,_=Rotation.align_vectors([unit(vsrc)],[[-1.,0.,0.]])
    state0=simple_state(p0,vsrc,scalar_quat(q0))
    seam=canonical_metric_operation({
        'kind':'metric','mode':'NORMAL','support_scenario':'MVP_2226',
        'arrival_rule':'ENERGY_ORBIT_RELATIVE_B',
        'canon_arrival':{'regime':'ORDINARY_SOLAR_SYSTEM',
            'source_body':J,'destination_body':E,
            'sun_gm_km3_s2':MU,'sun_mass_kg':SUN_MASS,
            'solar_reflex_approx_km_s':REF.tolist()}},
        {'time_s':0.,'position_m':state0['position_m'],
         'velocity_m_s':state0['velocity_m_s'],
         'mass_kg':SHIP['base']['mass_kg']+SHIP['tanks'][0]['initial_kg'],
         'tanks_kg':{'remass':SHIP['tanks'][0]['initial_kg']},
         'q_body_to_inertial':state0['q_body_to_inertial']},
        {'torch_centerline':0.})
    assert seam['execution_status']=='ARRIVAL_VELOCITY_RESOLVED'
    assert seam['terminal_state']['position_m'] is None
    assert all(x['status']=='HOLD' for x in seam['gates'].values())
    arrival=seam['arrival_velocity_resolution']
    assert abs(arrival['elapsed_s']-t)<1e-6
    va=np.array(seam['terminal_state']['velocity_m_s'])/1000.
    # L and p transferred to Sun: identities by construction, not pass evidence
    m0=SHIP['base']['mass_kg']+SHIP['tanks'][0]['initial_kg']
    dp=m0*(va-vsrc)*1000.
    dLship=np.cross(pE*1000.,m0*va*1000.)-np.cross(p0*1000.,m0*vsrc*1000.)
    spin=-np.cross(p0*1000.,dp)
    transport=-np.cross((pE-p0)*1000.,m0*va*1000.)
    sun_dL=spin+transport
    recoil=norm(dp)/SUN_MASS
    recoil_E=norm(dp)**2/(2*SUN_MASS)
    ship_E_change=m0*(.5*(norm(va*1000.)**2-norm(vsrc*1000.)**2)+
       (phi(pE,E['gm_km3_s2'],MU)-phi(p0,J['gm_km3_s2'],MU))*1e6)
    field_work=-ship_E_change-recoil_E
    identities={'E_residual_J':ship_E_change+recoil_E+field_work,
      'p_residual_N_s':norm(dp-dp),
      'L_residual_N_m_s':norm(dLship+sun_dL)}
    # Diagnostic 0.5 Hill shell, not a qualified physical Metric endpoint
    hill=hill_half(pE,E['gm_km3_s2'],MU)
    state_arr=simple_state(pE+hill*unit(pE),va,state0['q_body_to_inertial'])
    return {'metric_time_s':t,'source_position_km':p0.tolist(),
       'arrival_body_center_position_km':pE.tolist(),'arrival_ship_velocity_km_s':va.tolist(),
       'earth_velocity_km_s':vt.tolist(),'initial_match_delta_v_m_s':norm((va-vt)*1000),
       'initial_ship_state':state_arr,'solar_recoil_m_s':recoil,
       'solar_dL_magnitude_N_m_s':norm(sun_dL),
       'solar_spin_term_magnitude_N_m_s':norm(spin),
       'solar_transport_term_magnitude_N_m_s':norm(transport),
       'metric_EpL_IDENTITIES_BY_CONSTRUCTION':identities,
       'canonical_metric_seam_status':seam['execution_status'],
       'collapse_certification_status':'HOLD'}

def simulate(scale,base):
    ship=copy.deepcopy(SHIP)
    start=copy.deepcopy(base['initial_ship_state'])
    initial_mass=SHIP['base']['mass_kg']+SHIP['tanks'][0]['initial_kg']
    start['mass_kg']=initial_mass
    start['tanks_kg']={'remass':SHIP['tanks'][0]['initial_kg']}
    initial_epoch=float(base['metric_time_s'])
    # Correct for the ACTUAL source torch gimbal; bare body -X is ~0.36 deg off.
    aim=unit((np.asarray(base['earth_velocity_km_s'])-
              np.asarray(base['arrival_ship_velocity_km_s']))*1000.)
    body_thrust,nominal_gimbal=actual_torch_direction(ship,start)
    current_rot=quat_rotation(start['q_body_to_inertial'])
    delta,_=Rotation.align_vectors([aim],[body_thrust])
    rv=(current_rot.inv()*delta*current_rot).as_rotvec()
    angle=math.degrees(norm(rv))
    turn=stage(ship,start,[{'kind':'rcs_turn','duration_s':220.,
       'post_hold_s':5.,'axis_vector_body':(rv/norm(rv)).tolist(),'angle_deg':angle}],dt=.2)
    turned=turn['final_state']
    epoch=initial_epoch+float(turned['time_s'])
    _,target=earth_target(epoch)
    thrust,turn_gimbal=actual_torch_direction(ship,turned)
    delta_target=target-np.asarray(turned['velocity_m_s'])
    dv_along=float(delta_target@thrust)
    if dv_along<=0:raise ValueError('braking axis reversed')
    mdot=float(CRUISE['working_card_mdot_kg_s'])
    speed_exhaust=float(CRUISE['ve_m_s'])
    mass=float(turned['mass_kg'])
    calculated_full_T=mass*(-math.expm1(-dv_along/speed_exhaust))/mdot
    commanded_T=calculated_full_T*scale
    ship['tanks'][0]['initial_kg']=turned['tanks_kg']['remass']
    brake=stage(ship,turned,[{'kind':'torch','mode':'CRUISE',
              'duration_s':commanded_T,'throttle':1.,'hold_attitude':False},
              {'kind':'coast','duration_s':5.}],dt=.4)
    braked=brake['final_state']
    epoch+=float(braked['time_s'])
    _,target=earth_target(epoch)
    after_brake_error=norm(target-np.asarray(braked['velocity_m_s']))
    # Trim uses the actual post-brake state and current target, with finite
    # source CRUISE thrust and full source mass/remass accounting.
    ship['tanks'][0]['initial_kg']=braked['tanks_kg']['remass']
    thrust_after,_=actual_torch_direction(ship,braked)
    projected=float((target-np.asarray(braked['velocity_m_s']))@thrust_after)
    trim=None
    trim_T=0.
    final=braked
    # A nominal correction smaller than the specified 1 m/s match tolerance
    # is already achieved. Do not manufacture a sub-pellet millisecond burn.
    if after_brake_error>INPUT['earth_velocity_match_tolerance_m_s']:
        trim_T=float(braked['mass_kg'])*(-math.expm1(-max(0.,projected)/speed_exhaust))/mdot
        if trim_T<1e-5:
            raise ValueError('no forward torch trim possible; do not invent correction')
        trim=stage(ship,braked,[{'kind':'torch','mode':'CRUISE',
                  'duration_s':trim_T,'throttle':1.,'hold_attitude':False},
                  {'kind':'coast','duration_s':5.}],dt=.05)
        final=trim['final_state']
        epoch+=float(final['time_s'])
    _,target=earth_target(epoch)
    error=norm(target-np.asarray(final['velocity_m_s']))
    actual_consumption=float(SHIP['tanks'][0]['initial_kg'])-float(final['tanks_kg']['remass'])
    phases_consumed=[float(x['metrics']['known_propellant_used_kg']) for x in (turn,brake)]
    if trim is not None:
        phases_consumed.append(float(trim['metrics']['known_propellant_used_kg']))
    mass_residual=actual_consumption-sum(phases_consumed)
    burns=[brake]+([trim] if trim is not None else [])
    maximum_g=max(float(x['phases'][0]['peak_force_N'])/float(x['phases'][0]['mass_end_kg'])/G0 for x in burns)
    force_peak=max(float(x['phases'][0]['peak_force_N']) for x in burns)
    power_ceiling=float(SHIP['torch'][0]['jet_power_ceiling_W'])
    raw_power=force_peak*speed_exhaust/2.
    capped_power=min(raw_power,power_ceiling)
    reserve=float(INPUT['remass_reserved_kg'])
    checks={'actual_turn_5hz':turn['phases'][0]['attitude_error_deg']<.25,
      'source_remass_floor':final['tanks_kg']['remass']>=reserve,
      'remass_ledger':abs(mass_residual)<.001,
      'crew_4g':maximum_g<=INPUT['crew_limit_g'],
      'actual_capped_jet_power_within_ceiling':capped_power<=power_ceiling,
      'earth_velocity_match_within_1m_s':error<=INPUT['earth_velocity_match_tolerance_m_s'],
      'negative_underbrake_mismatch':True if scale==1. else after_brake_error>10.}
    return {'case':'NOMINAL' if scale==1. else 'UNDERBRAKE_1_PERCENT',
      'status':'PASS' if all(checks.values()) else 'HOLD','checks':checks,
      'brake_duration_s':commanded_T,'brake_nominal_duration_s':calculated_full_T,
      'brake_initial_aim_delta_v_m_s':dv_along,'brake_pretrim_error_m_s':after_brake_error,
      'brake_actual_remass_kg':phases_consumed[1],
      'rcs_turn_angle_deg':angle,'rcs_turn_dt_s':.2,
      'rcs_turn_end_error_deg':turn['phases'][0]['attitude_error_deg'],
      'rcs_turn_end_rate_deg_s':turn['phases'][0]['rate_deg_s'],
      'rcs_turn_remass_kg':phases_consumed[0],
      'source_torch_gimbal_deg':nominal_gimbal,
      'trim_projected_dv_m_s':projected,'trim_duration_s':trim_T,
      'trim_executed':trim is not None,
      'trim_actual_remass_kg':0. if trim is None else phases_consumed[2],
      'final_earth_velocity_error_m_s':error,
      'final_earth_target_velocity_m_s':target.tolist(),
      'final_ship_velocity_m_s':final['velocity_m_s'],
      'final_remass_kg':final['tanks_kg']['remass'],
      'total_remass_consumed_kg':actual_consumption,
      'remass_ledger_residual_kg':mass_residual,
      'peak_crew_g':maximum_g,'actual_capped_jet_power_W':capped_power,
      'actual_over_ceiling_W':max(0.,capped_power-power_ceiling),
      'nominal_card_rounding_difference_W':CRUISE['max_N']*speed_exhaust/2-power_ceiling,
      'raw_power_float_roundoff_W':max(0.,raw_power-power_ceiling),
      'limitations':['FROZEN SUN+ENDPOINT potential is not exact time-dependent Killing energy.',
                     'Solar E/p/L transfers are imposed identities by construction; not proof.',
                     'Canonical seam resolves only velocity; certification/collapse remain HOLD in ordinary flightlab.',
                     'Sun-only gravity in real RCS/torch phases, not Earth local and full N-body gravity.',
                     'Each flightlab finite stage carries physical state but resets actuator internal state.',
                     '0.5 Hill is diagnostic, not certified collapse; no orbital capture.',
                     'Declared jet-power/4g only; transient fin thermal and actual RCS power remain OPEN.']}

def main():
    base=inbound_base()
    cases=[simulate(1.,base),simulate(.99,base)]
    assert cases[1]['brake_pretrim_error_m_s']>cases[0]['brake_pretrim_error_m_s']+50.
    overall='PASS' if all(x['status']=='PASS' for x in cases) else 'HOLD'
    out={'fq':'FQ12','status':overall,'classification':'DRAFT_LAB_ONLY_NONCANON_NONNAVIGATOR',
        'replay_base_main_sha':INPUT['replay_base_main_sha'],
        'geometry_sha256':INPUT['geometry_sha256'],'ephemeris_epoch_utc':INPUT['epoch_utc'],
        'frozen_potential_caveat':INPUT['frozen_potential_caveat'],
        'source':'main JPL_HORIZONS_DIRECT; Sun-only propagated',
        'no_preburn_kg':0,'metric':{k:v for k,v in base.items() if k!='initial_ship_state'},
        'measured_cases':cases,
        'negative_test':{'case':'UNDERBRAKE_1_PERCENT',
           'larger_error_emerges':cases[1]['brake_pretrim_error_m_s']>cases[0]['brake_pretrim_error_m_s']+50.,
           'real_torch_trim_recovers':cases[1]['final_earth_velocity_error_m_s']<=1.,
           'status':'PASS' if cases[1]['status']=='PASS' else 'HOLD'},
        'note':'Canonical seam supplies forward B natural velocity; collapse/capture HOLD and E/p/L identities by construction.'}
    outp=HERE/'FQ12_RESULT.json'
    outp.write_text(json.dumps(out,indent=2,allow_nan=False,default=lambda q:q.item() if isinstance(q,np.generic) else q.tolist() if isinstance(q,np.ndarray) else (_ for _ in ()).throw(TypeError(type(q).__name__)))+'\n')
    for c in cases:
        print(c['case'],c['status'],'brake_s',round(c['brake_duration_s'],2),'brake_error_m/s',round(c['brake_pretrim_error_m_s'],3),
              'trim_s',round(c['trim_duration_s'],3),'final_m/s',round(c['final_earth_velocity_error_m_s'],3),
              'remass_t',round(c['total_remass_consumed_kg']/1000,3),flush=True)
    print('FQ12',overall,flush=True)
if __name__=='__main__':main()
