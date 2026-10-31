from pathlib import Path
import sys,json,copy,math,time
p=Path('/tmp/wayfarer_fq_20261031');sys.path.insert(0,str(p))
from faultlab_safing import run
ship=json.loads((p/'wayfarer_fq_water_rcs_1960.json').read_text())
ship['reserve_policy']={'rcs_floor_kg':5000.,'torch_cannot_consume_floor':True,'protected_water_kg':50000.}
ship['tanks'][0]['initial_kg']=5000.
r={}
def launch(name,exp,dt=.1):
 start=time.monotonic(); x=run(copy.deepcopy(ship),exp,dt=dt,sample_s=5)
 row={'status':x['qualification']['status'],'physical':x['physical_qualification']['status'],
      'fuel_used_kg':x['metrics']['total_propellant_used_kg'],
      'tank_left_kg':x['final_state']['tanks_kg']['remass'],
      'depletion_steps':sum(z['propellant_depletion_steps'] for z in x['phases']),
      'phases':[{'kind':z['kind'],'fuel_kg':z['known_propellant_used_kg'],
                 'attitude_error_deg':z.get('attitude_error_deg'),'rate_deg_s':z.get('rate_deg_s')}
                for z in x['phases']],
      'warnings':x['warnings'],'runtime_s':round(time.monotonic()-start,2)}
 r[name]=row;(p/'FQ5_RESERVE_RESULTS.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
 print(name, row,flush=True)
 return row
exp={'name':'FQ5 torch cannot burn 5t RCS floor',
     'phases':[{'kind':'torch','duration_s':30,'mode':'CRUISE','throttle':1.0}],
     'checks':{}}
launch('torch_at_5t_floor',exp,dt=.2)
for axis in ('pitch','roll','yaw'):
 exp={'name':f'FQ5 5t RCS floor 180 {axis}',
      'phases':[{'kind':'rcs_turn','duration_s':120,'axis':axis,'angle_deg':180.,'post_hold_s':4.}],
      'checks':{'attitude_error_deg':{'max':.25},'rate_deg_s':{'max':.05}}}
 launch('floor_flip_'+axis,exp,dt=.1)
exp={'name':'FQ5 consecutive pitch-roll-yaw flips in one RCS reserve state',
     'phases':[{'kind':'rcs_turn','duration_s':120,'axis':axis,'angle_deg':180.,'post_hold_s':4.}
               for axis in ('pitch','roll','yaw')],'checks':{}}
launch('floor_three_flips_one_state',exp,dt=.1)
