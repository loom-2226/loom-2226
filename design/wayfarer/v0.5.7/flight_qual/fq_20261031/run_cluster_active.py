from pathlib import Path
import json,copy,sys,time
p=Path('/tmp/wayfarer_fq_20261031');sys.path.insert(0,str(p))
from faultlab_safing import run
ship=json.loads((p/'wayfarer_fq_water_rcs_1960.json').read_text())
ship['reserve_policy']={'rcs_floor_kg':5000.}
base={'name':'FQ10 cluster lost while active: 180 pitch 120s',
      'phases':[{'kind':'rcs_turn','duration_s':120,'axis':'pitch','angle_deg':180.,'post_hold_s':4.}],
      'checks':{'attitude_error_deg':{'max':.25},'rate_deg_s':{'max':.05}}}
start=time.monotonic()
o=run(copy.deepcopy(ship),copy.deepcopy(base),dt=.1,sample_s=2)
loads={}
for step in o['rcs_trace']:
 if 20<=step['t_s']<=30:
    for e in step['engine_samples']:
      if e['kind']!='rcs':continue
      cluster=e['id'].rsplit('_',1)[0]
      loads[cluster]=loads.get(cluster,0.)+e['actual_N']*step['step_s']
print('PREFault LOAD N*s',loads,flush=True)
cluster=max(loads,key=loads.get)
assert loads[cluster]>0
fault=copy.deepcopy(base)
fault['name']='FQ10 active '+cluster+' loss at t=25 in pitch flip'
fault['faults']=[{'kind':'cluster_out','when_s':25.}]
fault['faults'][0]['cluster']=cluster
start2=time.monotonic()
f=run(copy.deepcopy(ship),fault,dt=.1,sample_s=2)
result={'geometry_sha256':ship['provenance']['geometry_sha256'],
        'cluster':cluster,'commanded_pre_fault_impulse_Ns_20_to_30s':loads[cluster],
        'baseline_status':o['qualification']['status'],
        'baseline_final_att_error_deg':o['phases'][0]['at_end']['attitude_error_deg'],
        'baseline_final_rate_deg_s':o['phases'][0]['at_end']['rate_deg_s'],
        'failed_cluster_status':f['qualification']['status'],
        'fault_att_error_deg':f['phases'][0]['at_end']['attitude_error_deg'],
        'fault_rate_deg_s':f['phases'][0]['at_end']['rate_deg_s'],
        'fault_consumption_kg':f['metrics']['total_propellant_used_kg'],
        'fault_events':f['safing_observations']['events'],
        'baseline_runtime_s':round(start2-start,1),
        'fault_runtime_s':round(time.monotonic()-start2,1)}
(p/'FQ10_CLUSTER_ACTIVE_RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print('ACTIVE CLUSTER LOSS',json.dumps(result),flush=True)
