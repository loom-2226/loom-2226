"""Compare saved NON-CANON gimbal runs and independently replay their moving wrenches.
Uses SciPy DOP853 with independently written equations, not the lab RK4 routine.
Run after lab.py demo --manifest completion_manifest.json --dt .02 --out sol_results.
"""
import csv,hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.spatial.transform import Rotation
from flightlab import mass_properties,source_hash
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'sol_results'
def read(path):return json.loads(path.read_text())
def write(name,obj):(OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')

def refresh_comparison(manifest,dest):
    rows=[]
    for ship,experiment in read(ROOT/manifest):
        result=read(dest/(ship+'__'+experiment+'.json'))
        assert result['ship_sha256']==source_hash(read(ROOT/'configs'/(ship+'.json')))
        assert result['experiment_sha256']==source_hash(read(ROOT/'experiments'/(experiment+'.json')))
        rows.append(dict(ship_config=ship,experiment=experiment,status=result['qualification']['status'],
                         system_status=result['system_status'],metrics=result['metrics'],warnings=result['warnings'],
                         ship_sha256=result['ship_sha256'],experiment_sha256=result['experiment_sha256']))
    (dest/'comparison.json').write_text(json.dumps(rows,indent=2,allow_nan=False)+'\n')
    keys=['attitude_error_deg','rate_deg_s','gate_entry_s','sustained_gate_duration_s','residual_velocity_m_s',
          'peak_gimbal_rate_deg_s','peak_force_residual_N','known_propellant_used_kg','total_propellant_used_kg']
    with (dest/'comparison.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['ship','experiment','status','system_status']+keys)
        for r in rows:w.writerow([r['ship_config'],r['experiment'],r['status'],r['system_status']]+[r['metrics'].get(k) for k in keys])

def main():
    refresh_comparison('completion_manifest.json',OUT)
    refresh_comparison('demo_manifest.json',ROOT/'sol_baseline_results')
    historical=read(ROOT/'results/gimbal_dynamic.json');rows=[]
    for T,old in zip((10,12,14),historical):
        result=read(OUT/f'wayfarer_gimbal_reference__gimbal{T}.json');p=result['phases'][0]
        row={'duration_s':T,'simulated_terminal_status':result['qualification']['status'],
             'system_status':result['system_status'],'error_deg':p['attitude_error_deg'],
             'rate_deg_s':p['rate_deg_s'],'gate_entry_s':p['gate_entry_s'],
             'delta_error_deg':p['attitude_error_deg']-old['at_target_time']['attitude_error_deg'],
             'delta_rate_deg_s':p['rate_deg_s']-old['at_target_time']['rate_deg_s'],
             'delta_peak_net_force_N':p['peak_force_N']-old['peak_net_force_N'],
             'delta_peak_offaxis_torque_Nm':p['peak_offaxis_torque_Nm']-old['peak_offaxis_torque_Nm'],
             'peak_gimbal_rate_deg_s':p['peak_gimbal_rate_deg_s'],
             'residual_velocity_m_s':p['residual_velocity_m_s']}
        row['agreement']=(abs(row['delta_error_deg'])<1e-5 and abs(row['delta_rate_deg_s'])<1e-5
                          and abs(row['delta_peak_net_force_N'])<.1 and abs(row['delta_peak_offaxis_torque_Nm'])<.1
                          and ((result['qualification']['status']=='pass')==old['pass_at_target'])
                          and p['gate_entry_s']==old['gate_entry_s'])
        rows.append(row)
    write('gimbal_reference_comparison.json',rows)
    with (OUT/'gimbal_reference_comparison.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    fine=read(ROOT/'sol_timestep_results/wayfarer_gimbal_reference__gimbal12.json')['phases'][0]
    coarse=read(OUT/'wayfarer_gimbal_reference__gimbal12.json')['phases'][0]
    keys=['attitude_error_deg','rate_deg_s','peak_force_N','peak_offaxis_torque_Nm','residual_velocity_m_s']
    write('gimbal_timestep_comparison.json',{'scope':'step-end moving-vector and actuator discretization sensitivity; not an error bound',
          'dt_0.02_s':{k:coarse[k] for k in keys},'dt_0.01_s':{k:fine[k] for k in keys},
          'fine_minus_coarse':{k:fine[k]-coarse[k] for k in keys}})
    # Fixed mass, dynamically rotating nozzles: replay the realized body wrench.
    config=read(ROOT/'configs/wayfarer_gimbal_reference.json')
    result=read(OUT/'wayfarer_gimbal_reference__gimbal12.json')
    trace=read(OUT/'wayfarer_gimbal_reference__gimbal12.rcs_trace.json')
    m,cg,I=mass_properties(config,{t['id']:t.get('initial_kg',t['capacity_kg']) for t in config['tanks']})
    y=np.array(result['phases'][0]['state_start']);maxq=0.;maxw=0.;maxr=0.;maxv=0.
    for k,row in enumerate(trace):
        dq=(Rotation.from_quat(y[[1,2,3,0]]).inv()*Rotation.from_quat(np.array(row['q'])[[1,2,3,0]])).magnitude()
        maxq=max(maxq,math.degrees(dq));maxw=max(maxw,float(np.linalg.norm(y[4:7]-row['omega_rad_s'])))
        f=np.array(row['force_body_N']);torque=np.array(row['torque_body_Nm'])
        def rhs(t,z):
            q=z[:4]/np.linalg.norm(z[:4]);a,b,c,d=q;w=z[4:7]
            qdot=.5*np.array([-b*w[0]-c*w[1]-d*w[2],a*w[0]+c*w[2]-d*w[1],
                              a*w[1]+d*w[0]-b*w[2],a*w[2]+b*w[1]-c*w[0]])
            R=np.array([[1-2*(c*c+d*d),2*(b*c-a*d),2*(b*d+a*c)],
                        [2*(b*c+a*d),1-2*(b*b+d*d),2*(c*d-a*b)],
                        [2*(b*d-a*c),2*(c*d+a*b),1-2*(b*b+c*c)]])
            return np.r_[qdot,np.linalg.solve(I,torque-np.cross(w,I@w)),z[10:13],R@f/m]
        end=trace[k+1]['t_s'] if k+1<len(trace) else result['final_state']['time_s']
        h=end-row['t_s']
        sol=solve_ivp(rhs,[0,h],y,method='DOP853',rtol=1e-11,atol=1e-12)
        if not sol.success:raise RuntimeError(sol.message)
        y=sol.y[:,-1];y[:4]/=np.linalg.norm(y[:4])
    target=np.array(result['phases'][0]['state_end'])
    dq=(Rotation.from_quat(y[[1,2,3,0]]).inv()*Rotation.from_quat(target[[1,2,3,0]])).magnitude()
    replay={'solver':'independently coded equations with SciPy DOP853',
            'scope':'realized moving-gimbal wrench replay, frozen mass; controller and hardware not independently qualified',
            'steps':len(trace),'max_attitude_difference_deg':max(maxq,math.degrees(dq)),
            'max_rate_difference_rad_s':max(maxw,float(np.linalg.norm(y[4:7]-target[4:7]))),
            'final_position_difference_m':float(np.linalg.norm(y[7:10]-target[7:10])),
            'final_velocity_difference_m_s':float(np.linalg.norm(y[10:13]-target[10:13]))}
    write('gimbal_dop853_replay.json',replay)
    # Verify all persistent states including actuator state, not only phase end masses.
    combined=read(OUT/'scout_offset_metric__continuous.json')
    pairs=list(zip(combined['phases'],combined['phases'][1:]))
    continuity={'boundaries_checked':len(pairs),
        'all_state_boundaries_exact':all(a['state_end']==b['state_start'] for a,b in pairs),
        'all_actuator_boundaries_exact':all(a['actuators_end']==b['actuators_start'] for a,b in pairs),
        'max_mass_jump_kg':max(abs(a['mass_end_kg']-b['mass_start_kg']) for a,b in pairs),
        'total_known_propellant_kg':combined['metrics']['known_propellant_used_kg'],
        'mass_loss_kg':combined['phases'][0]['mass_start_kg']-combined['final_state']['mass_kg']}
    write('continuous_state_audit.json',continuity)
    source=read(ROOT/'source_manifest.json')
    matches={name:hashlib.sha256((ROOT/'source'/name).read_bytes()).hexdigest()==value
             for name,value in source['source_files'].items()}
    write('reference_integrity.json',{'source_files_matching_pinned_manifest':matches,
                                    'all_match':all(matches.values())})
    write('implementation_hashes.json',{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
          for name in ('flightlab.py','lab.py','lab42.py','make_completion_examples.py','completion_evidence.py',
                       'test_flightlab.py','test_completion.py')})
    assert all(r['agreement'] for r in rows),'historical moving-gimbal mismatch'
    assert replay['max_attitude_difference_deg']<1e-5,'moving-wrench replay mismatch'
    assert continuity['all_state_boundaries_exact'] and continuity['all_actuator_boundaries_exact']
    assert abs(continuity['mass_loss_kg']-continuity['total_known_propellant_kg'])<1e-6
    assert all(matches.values()),'read-only source integrity mismatch'
    print(json.dumps({'historical_gimbal_agreements':sum(r['agreement'] for r in rows),
                      'replay':replay,'continuity':continuity,'source_integrity':all(matches.values())},indent=2))
if __name__=='__main__':main()
