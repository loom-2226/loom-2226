"""Additional Rev7 S1 six-mode and three-axis flight screening; NON-CANON."""
from pathlib import Path
import json, sys, math
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from flightlab import run,G0
OUT=Path(__file__).resolve().parent
base=json.loads((ROOT/'configs/wayfarer.json').read_text())
uprated=json.loads((ROOT/'configs/wayfarer_original_mount_300k.json').read_text())
rows=[]
def check(name,ship,experiment,dt):
    r=run(ship,experiment,dt=dt,sample_s=10.)
    p=r['phases'][0];m=r['metrics']
    a={'case':name,'numerical':r['qualification']['status'],'system':r['system_status'],
       'mass_start_kg':p['mass_start_kg'],'mass_end_kg':p['mass_end_kg'],
       'propellant_used_kg':p['propellant_used_kg'],
       'known_propellant_used_kg':p['known_propellant_used_kg'],
       'peak_force_N':p['peak_force_N'],'thrust_limit_steps':p['thrust_limit_steps'],
       'peak_angular_rate_deg_s':p['peak_angular_rate_deg_s'],
       'attitude_error_deg':m.get('attitude_error_deg'),
       'angular_rate_deg_s':m.get('rate_deg_s'),
       'translation_error_m_s':p.get('translation_velocity_error_m_s'),
       'attitude_hold_error_deg':p.get('attitude_hold_error_deg'),
       'torch_attitude_drift_deg':m.get('torch_attitude_drift_deg'),
       'torch_force_over_endmass_g_upper_bound':(p['peak_force_N']/p['mass_end_kg']/G0 if experiment['phases'][0]['kind']=='torch' else None)}
    if p['propellant_used_kg'] is not None:
        a['mass_ledger_error_kg']=p['mass_start_kg']-p['mass_end_kg']-p['propellant_used_kg']
    rows.append(a)
    (OUT/'flight_matrix.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(name,'numeric',a['numerical'],'system',a['system'],
          'err',a['attitude_error_deg'],'dv_error',a['translation_error_m_s'],
          'fuel_kg',a['propellant_used_kg'],'max_a_bound',round(a['torch_force_over_endmass_g_upper_bound'] or 0,5),flush=True)
for mode in ('ECON','CRUISE','EXPEDITE','FAST','HARD','LIMIT'):
    check('torch_'+mode,base,{'name':'torch '+mode,'phases':[{'kind':'torch','mode':mode,'duration_s':120.}],
          'checks':{'torch_attitude_drift_deg':{'max':1.0},
                    'torch_final_angular_rate_deg_s':{'max':0.05}}},.2)
for axis in ('roll','pitch','yaw'):
    for ship,tag,T in ((base,'original25',40.),(uprated,'original_mount_300',10.)):
        e={'name':axis+tag,'phases':[{'kind':'rcs_turn','duration_s':T,
              'axis':axis,'angle_deg':180.,'post_hold_s':4.}],
           'checks':{'attitude_error_deg':{'max':.25},'rate_deg_s':{'max':.05}}}
        check('rcs_'+axis+'_'+tag,ship,e,.05)
for axis,sgn in (('x',1),('x',-1),('y',1),('y',-1),('z',1),('z',-1)):
    dv=[0.,0.,0.];dv['xyz'.index(axis)]=.5*sgn
    e={'name':f'translation_{axis}{sgn:+d}','phases':[{'kind':'rcs_translate',
       'duration_s':20.,'delta_v_body_m_s':dv}],
       'checks':{'translation_velocity_error_m_s':{'max':.02},
                 'attitude_hold_error_deg':{'max':.5}}}
    check('rcs_translation_'+axis+str(sgn),base,e,.1)
print('MATRIX_FINISHED',len(rows),'modes=6 rotations=6 translations=6',flush=True)
