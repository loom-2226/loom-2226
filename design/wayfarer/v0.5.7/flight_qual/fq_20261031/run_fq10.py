import json,time,sys,math
from pathlib import Path
P=Path('/tmp/wayfarer_fq_20261031')
sys.path[:0]=[str(P)]
from faultlab import run
s=json.loads((P/'wayfarer_fq_water_rcs_1960.json').read_text())
cases={'baseline':[],
       'cluster_out':[{'kind':'cluster_out','when_s':60,'cluster':'F+Y'}],
       'stuck_thruster':[{'kind':'stuck_thruster','when_s':60,'nozzle':'F+Y_tan+','stuck_fraction':1.}],
       'stuck_tvc':[{'kind':'stuck_tvc','when_s':60}]}
o={'geometry_sha256':s['provenance']['geometry_sha256'],'status':'FQ10 non-governing timed fault injection, not physical hardware failure qualification',
    'reference_lab_sha256':'137d13fe182578d227b444ad27ca5d55ac85475028e5e7909f53e2916a761bb2',
    'power':'OPEN, no RCS heater/power closure','cases':{}}
for k,v in cases.items():
 ex={'name':k,'phases':[{'kind':'torch','mode':'CRUISE','duration_s':120,'hold_attitude':True}],
     'faults':v,'checks':{}}
 st=time.monotonic()
 try:
    r=run(s,ex,dt=.1,sample_s=10)
    ph=r['phases'][0]; m=r['metrics']
    d={'status':r['qualification']['status'],'attitude_drift_deg':m.get('torch_attitude_drift_deg'),
       'final_angular_rate_deg_s':m.get('torch_final_angular_rate_deg_s'),
       'peak_torque_residual_Nm':ph.get('peak_torque_residual_Nm'),
       'peak_force_residual_N':ph.get('peak_force_residual_N'),
       'rcs_prop_used_kg':r['metrics'].get('known_propellant_used_kg')-681.66 if r['metrics'].get('known_propellant_used_kg') else None,
       'total_prop_used_kg':r['metrics'].get('known_propellant_used_kg'),
       'depletion_steps':ph.get('propellant_depletion_steps'),
       'faults':v,'runtime_s':round(time.monotonic()-st,2),'warnings':r['warnings']}
    d['bounded_attitude_gate']=(d['attitude_drift_deg'] is not None and d['attitude_drift_deg']<=1.0
                           and d['final_angular_rate_deg_s']<=.05 and d['depletion_steps']==0)
 except Exception as e:
    d={'status':'ERROR','error':repr(e),'faults':v}
 o['cases'][k]=d
 (P/'FQ10.json').write_text(json.dumps(o,indent=2,allow_nan=False)+'\n')
 print('FQ10',k,json.dumps(d),flush=True)
