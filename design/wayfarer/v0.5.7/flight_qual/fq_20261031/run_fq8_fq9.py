import json,sys,math,time
from pathlib import Path
sys.path.insert(0,'/home/ubuntu/wayfarer_flight_lab_scratch_20261026')
from flightlab import run
P=Path('/tmp/wayfarer_fq_20261031')
s=json.loads((P/'wayfarer_fq_water_rcs_1960.json').read_text())
assert s['provenance']['geometry_sha256']=='ea1fcb59f1e0a127cd48dc4e0321e7d42247e3f2e445cf89893bdefadb793266'
v=s['torch'][0]['modes']['CRUISE']['working_card_mdot_kg_s']
# Stop just before the 250t unprotected remass is spent. The 50t protected reserve is distinct.
T=(250000.0-.2)/v
ex={'name':'FQ8 CRUISE to 50t protected reserve, 0.2kg unprotected remass retained',
    'phases':[{'kind':'torch','duration_s':T,'mode':'CRUISE','throttle':1.0}],'checks':{}}
start=time.monotonic()
r=run(s,ex,dt=10,sample_s=1800)
q=r['phases'][0];d={'fq':'FQ8','geometry_sha256':s['provenance']['geometry_sha256'],
    'duration_s':T,'cruise_mdot_kg_s':v,'mass_start_kg':q['mass_start_kg'],
    'mass_end_kg':q['mass_end_kg'],'consumed_kg':q['propellant_used_kg'],
    'remass_left_kg':r['final_state']['tanks_kg']['remass'] if 'tanks_kg' in r['final_state'] else None,
    'protected_water_t':50,'protected_water_consumed_kg':0,'depletion_steps':q['propellant_depletion_steps'],
    'peak_accel_g':q['peak_force_N']/(q['mass_end_kg']*9.80665),
    'tvc_trim_deg':q['max_ideal_tvc_trim_deg'],'qualification':r['qualification']['status'],
    'runtime_s':time.monotonic()-start,'thermal':'HOLD unqualified long-duration torch 2226 heat closure'}
(P/'FQ8.json').write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
print('FQ8',json.dumps(d),flush=True)
ex={'name':'FQ9 single state burn-cut-flip-brake no metric',
    'phases':[{'kind':'torch','duration_s':60,'mode':'CRUISE','throttle':1.0},
              {'kind':'coast','duration_s':5},
              {'kind':'rcs_turn','duration_s':120,'axis':'pitch','angle_deg':180,'post_hold_s':4},
              {'kind':'torch','duration_s':60,'mode':'CRUISE','throttle':1.0}],
    'checks':{}}
start=time.monotonic()
r=run(s,ex,dt=.1,sample_s=20)
ph=[]
for i,z in enumerate(r['phases']):
    ph.append({'index':i,'kind':z['kind'],'mass_start':z['mass_start_kg'],'mass_end':z['mass_end_kg'],
          'propellant_kg':z['known_propellant_used_kg'],'t_start_s':z['t_start_s'],'t_end_s':z['t_end_s'],
          'attitude_error_deg':z.get('attitude_error_deg'),'rate_deg_s':z.get('rate_deg_s'),
          'min_allocated_fraction':z.get('minimum_allocated_fraction'),'depletion_steps':z.get('propellant_depletion_steps')})
massdelta=ph[0]['mass_start']-ph[-1]['mass_end'];massspent=sum(z['propellant_kg'] for z in ph)
d={'fq':'FQ9','geometry_sha256':s['provenance']['geometry_sha256'],'phases':ph,
   'mass_delta_kg':massdelta,'fuel_sum_kg':massspent,'ledger_error_kg':massdelta-massspent,
   'final_speed_m_s':r['metrics']['final_speed_m_s'],
   'final_state':{'mass_kg':r['final_state']['mass_kg'],'tanks_kg':r['final_state'].get('tanks_kg')},
   'qualification':r['qualification']['status'],'warnings':r['warnings'],
   'runtime_s':time.monotonic()-start}
(P/'FQ9.json').write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
print('FQ9',json.dumps({'qualification':d['qualification'],'mass_delta_kg':massdelta,'fuel_sum_kg':massspent,'ledger_error_kg':d['ledger_error_kg'],'phases':ph,'final_speed_m_s':d['final_speed_m_s']}),flush=True)
