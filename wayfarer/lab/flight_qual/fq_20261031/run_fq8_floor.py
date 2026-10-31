import sys,json,time
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
from faultlab_safing import run
s=json.loads((P/'wayfarer_fq_water_rcs_1960.json').read_text())
s['reserve_policy']={'rcs_floor_kg':5000.}
rate=s['torch'][0]['modes']['CRUISE']['working_card_mdot_kg_s']
duration=245000/rate+120
e={'name':'FQ8 with 5t RCS floor','phases':[{'kind':'torch','duration_s':duration,'mode':'CRUISE'}],'checks':{}}
t=time.monotonic()
r=run(s,e,dt=10,sample_s=1800)
d={'duration_s':duration,'initial_remass_kg':250000,'rcs_floor_kg':5000,
   'torch_consumed_kg':r['phases'][0]['known_propellant_used_kg'],
   'final_remass_kg':r['final_state']['tanks_kg']['remass'],
   'protected_water_kg':50000,'warnings':r['warnings'],
   'seconds':time.monotonic()-t}
(P/'FQ8_5T_FLOOR_RESULTS.json').write_text(json.dumps(d,indent=2)+'\n')
print('FQ8 5T',d,flush=True)
