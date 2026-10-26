"""Compare new lab propagation to GMAT with torque-free mass-matched reference."""
import json,math,numpy as np
from pathlib import Path
from flightlab import run
ROOT=Path(__file__).resolve().parent
ship=json.loads((ROOT/'configs/wayfarer.json').read_text())
gmat=json.loads((ROOT/'results/gmat_comparison.json').read_text())
center=[24.3996,.0248,-.3564]
ship['name']='Wayfarer mass, torque-free numerical check'
ship['base']['cg_m']=center
ship['tanks'][0]['cg_m']=center
ship['torch'][0]['pos_m']=center
ship['torch'][0]['direction']=[-1,0,0]
ship['torch'][0]['auto_trim']=False
au=149597870700.
mu=1.32712440018e20
q=[math.cos(-math.pi/4),0,0,math.sin(-math.pi/4)]
experiment={'name':'GMAT 600s reference',
            'initial':{'q_body_to_inertial':q,'position_m':[au,0,0],
                       'velocity_m_s':[0,math.sqrt(mu/au),0]},
            'gravity_mu_m3_s2':mu,
            'phases':[{'kind':'torch','mode':'CRUISE','duration_s':600}]}
result=run(ship,experiment,dt=1.,sample_s=60.)
fin=result['final_state']
computed=fin['position_m']+fin['velocity_m_s']+[fin['mass_kg']]
known=gmat['gmat_end_state_SI']
delta=np.array(computed)-np.array(known)
report={'basis':'mass-matched torque-free reference with inertial +Y thrust',
        'engine_source':'Wayfarer CRUISE card, conventional numerical surrogate',
        'GMAT_version':gmat['GMAT_release'],'dt_s':1.,
        'position_difference_m':float(np.linalg.norm(delta[:3])),
        'velocity_difference_m_s':float(np.linalg.norm(delta[3:6])),
        'mass_difference_kg':float(delta[6]),
        'lab_end_state_SI':computed,'gmat_end_state_SI':known,
        'scope':'Independent ordinary trajectory comparison only; NOT installed torch hardware'}
out=ROOT/'lab_results/gmat_vs_flightlab.json'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
