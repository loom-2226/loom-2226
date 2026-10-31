import sys,json,copy,time
from pathlib import Path
p=Path(__file__).resolve().parent;sys.path.insert(0,str(p))
from faultlab_safing import run
s=json.loads((p/'wayfarer_fq_water_rcs_1960.json').read_text())
s['reserve_policy']={'rcs_floor_kg':5000.}
s['tanks'][0]['initial_kg']=5000.
result={}
for dt in (.4,.2):
 for axis in ('pitch','roll','yaw'):
  exp={'name':f'RCS reserved 5t {axis}',
       'phases':[{'kind':'rcs_turn','duration_s':120,'post_hold_s':4,'angle_deg':180,'axis':axis}],
       'checks':{'attitude_error_deg':{'max':.25},'rate_deg_s':{'max':.05}}}
  z=run(copy.deepcopy(s),exp,dt=dt,sample_s=4)
  valid=z['qualification']['status']=='pass' and z['system_status']=='pass' and z['metrics']['known_propellant_used_kg']>0
  result[f'{axis}_{dt}']={'pass':valid,'water_used_kg':z['metrics']['total_propellant_used_kg'],
      'remain_kg':z['final_state']['tanks_kg']['remass']}
  print(axis,dt,valid,round(result[f'{axis}_{dt}']['water_used_kg'],3),flush=True)
 exp={'name':'Torch cannot consume RCS 5t floor','phases':[{'kind':'torch','duration_s':20,'mode':'CRUISE'}],'checks':{}}
 z=run(copy.deepcopy(s),exp,dt=dt,sample_s=4)
 result[f'torch_{dt}']={'pass':z['metrics']['total_propellant_used_kg']==0 and z['final_state']['tanks_kg']['remass']==5000,
                         'water_used_kg':z['metrics']['total_propellant_used_kg']}
 print('torch inhibited',dt,result[f'torch_{dt}']['pass'],flush=True)
(p/'FQ6_RESERVE_PARITY.json').write_text(json.dumps(result,indent=2,default=lambda x:x.item() if hasattr(x,"item") else str(x))+'\n')
