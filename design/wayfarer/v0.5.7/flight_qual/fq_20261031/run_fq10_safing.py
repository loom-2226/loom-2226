from pathlib import Path
import json,copy,sys,time,math
p=Path('/tmp/wayfarer_fq_20261031')
sys.path.insert(0,str(p))
from faultlab_safing import run,qerror
base=json.loads((p/'wayfarer_fq_water_rcs_1960.json').read_text())
assert base['provenance']['geometry_sha256']=='ea1fcb59f1e0a127cd48dc4e0321e7d42247e3f2e445cf89893bdefadb793266'
base['reserve_policy']={'rcs_floor_kg':5000.,'torch_cannot_consume_floor':True,
       'protected_water_kg':50000.,'rcs_from':'unprotected remass tank only'}
base['rcs_power_declaration']={'source':'A: main plant on demand',
      'minimum_W_per_nozzle':57663265.306,'real_world_power_closure':'OPEN',
      'option_B':'charged hot-water store, not baseline',
      'boiling_J_kg':2600000.,'v_e_m_s':1960.}
out={}
for mode in ('CRUISE','HARD'):
 for response in (False,True):
    ship=copy.deepcopy(base)
    exp={'name':f'FQ10 stuck TVC {mode} response {response}',
         'phases':[{'kind':'torch','duration_s':120.,'mode':mode,'hold_attitude':True}],
         'faults':[{'kind':'stuck_tvc','when_s':60.}],
         'checks':{}}
    if response:exp['safing']={'detect_delay_s':0.20,'cut_angle_deg':0.75,'cut_rate_deg_s':0.50,
                          'max_saturation_s':0.4,'allocation_limit':0.98}
    start=time.monotonic()
    r=run(ship,exp,dt=.05,sample_s=.1)
    safety=r['safing_observations']
    key=f'{mode}_{"mitigated" if response else "no_response"}'
    v={'mode':mode,'response':response,'status':r['qualification']['status'],
       'peak_attitude_error_deg':safety['peak_attitude_error_deg'],
       'peak_rate_deg_s':safety['peak_rate_deg_s'],
       'final_attitude_error_deg':r['metrics']['torch_attitude_drift_deg'],
       'final_rate_deg_s':r['metrics']['torch_final_angular_rate_deg_s'],
       'events':safety['events'],'authority_fraction':safety.get('authority_fraction'),
       'torch_cap_fraction':safety.get('torch_cap_fraction'),
       'fuel_used_kg':r['metrics']['total_propellant_used_kg'],
       'min_allocated_fraction':r['phases'][0]['minimum_allocated_fraction'],
       'runtime_s':round(time.monotonic()-start,2)}
    out[key]=v
    (p/'FQ10_SAFING_RESULTS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(key,'peak error',round(v['peak_attitude_error_deg'],5),'peak rate',round(v['peak_rate_deg_s'],5),'final error',round(v['final_attitude_error_deg'],5),'events',v['events'],'fuel',round(v['fuel_used_kg'],3),flush=True)
