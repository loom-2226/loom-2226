"""Independent NASA 42 rigid-body replay of a scratch lab fixed-RCS experiment.
Scope: constant mass, fixed thruster directions, and original lab realized commands.
Example: .venv/bin/python lab42.py wayfarer reversal40
"""
import json,sys,shutil,subprocess
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from flightlab import mass_properties
ROOT=Path(__file__).resolve().parent; NASA=ROOT/'nasa42'
shipname=sys.argv[1] if len(sys.argv)>1 else 'wayfarer'
expname=sys.argv[2] if len(sys.argv)>2 else 'reversal40'
ship=json.loads((ROOT/'configs'/(shipname+'.json')).read_text())
exp=json.loads((ROOT/'experiments'/(expname+'.json')).read_text())
if len(exp['phases'])!=1 or exp['phases'][0]['kind']!='rcs_turn':
    raise ValueError('42 replay currently limited to single RCS turn with constant inertia')
tag=shipname+'__'+expname
trace=json.loads((ROOT/'lab_results'/(tag+'.rcs_trace.json')).read_text())
result=json.loads((ROOT/'lab_results'/(tag+'.json')).read_text())
if result['metrics']['known_propellant_used_kg']>1e-8:
    raise ValueError('42 constant-mass replay cannot verify a fuel-depleting RCS run')
thr=[e for e in ship['rcs'] if e.get('enabled',True)]
ids=[e['id'] for e in thr]
assert trace and all(x['engine_ids']==ids for x in trace)
for e in thr:
    if 'gimbal' in e:raise ValueError('42 adapter supports fixed nozzles only; moving-gimbal replay unsupported')
    if 'gimbal_target_direction' in e and e['gimbal_target_direction']!=e['direction']:
        raise ValueError('42 replay of moving gimbals requires dynamic direction commands')
mass,cg,I=mass_properties(ship,{e['id']:e.get('initial_kg',e['capacity_kg']) for e in ship['tanks']})
dt=trace[1]['t_s']-trace[0]['t_s']
end=trace[-1]['t_s']+dt
case=NASA/('WF_LAB_'+tag)
shutil.copytree(NASA/'InOut',case,dirs_exist_ok=True)
def edit(path,repl):
    lines=path.read_text().splitlines()
    for marker,value in repl.items():
        found=[i for i,l in enumerate(lines) if (l.strip().endswith('! Mass') if marker=='body_mass' else marker in l)]
        if len(found)!=1:raise ValueError((marker,found))
        i=found[0];lines[i]=str(value)+' ! '+lines[i].split('!',1)[-1]
    path.write_text('\n'.join(lines)+'\n')
edit(case/'Inp_Sim.txt',{'Sim Duration':f'{end+dt} {dt}',
     'File Output Interval':dt,'Graphics Front End':'FALSE',
     'Input file for SC 0':'TRUE 0 SC_Lab.txt'})
sc=case/'SC_Lab.txt';shutil.copy(case/'SC_Simple.txt',sc)
edit(sc,{'Flight Software Identifier':'PASSIVE_FSW',
         'FSW Sample Time':dt,'Orbit Prop':'COWELL',
         'Ang Vel wrt':'NQN','Ang Vel (deg/sec)':'0 0 0',
         'body_mass':mass,
         'Moments of Inertia':' '.join(str(I[k,k]) for k in range(3)),
         'Products of Inertia':f'{-I[0,1]} {-I[0,2]} {-I[1,2]}',
         'Location of mass center':' '.join(map(str,cg)),
         'Node File Name':'Nodes_Lab.txt'})
lines=sc.read_text().splitlines()
i=next(i for i,l in enumerate(lines) if 'Thruster Parameters' in l)
j=next(j for j,l in enumerate(lines) if '*** Gyro' in l)
blocks=[lines[i],f'{len(thr)} ! Number of Thrusters']
for k,e in enumerate(thr):
    blocks += [f'===== Thr {k} =====','PROPORTIONAL',str(e['max_N']),
               ' '.join(map(str,e['direction'])),'0',str(k)]
sc.write_text('\n'.join(lines[:i]+blocks+lines[j:])+'\n')
(case/'Nodes_Lab.txt').write_text('Lab nodes\nrealized configuration\n'+str(len(thr))+
    '\nLocations\n'+'\n'.join(' '.join(map(str,e['pos_m']))+f' "{e["id"]}"' for e in thr)+'\n')
commands=['Lab NASA42 replay: realized thruster fractions, not controller software']
for row in trace:
    for k,u in enumerate(row['thrust_levels']):
        commands.append(f'{row["t_s"]:.8f} SC[0].AC.Thr[{k}].ThrustLevelCmd = {np.clip(u,0,1):.16g}')
commands.append('EOF')
(case/'Inp_Cmd.txt').write_text('\n'.join(commands)+'\n')
out=ROOT/'lab_results'
log=out/(tag+'_42.log')
with log.open('w') as file:
    proc=subprocess.run(['./42',case.name],cwd=NASA,stdout=file,stderr=subprocess.STDOUT)
if proc.returncode:raise RuntimeError('NASA42 failed: '+log.read_text()[-1200:])
q=np.loadtxt(case/'qbn.42');w=np.loadtxt(case/'wbn.42');times=np.loadtxt(case/'time.42')
# 42 applies commands after first dynamics step. Compare at same effective start times.
indices=1+np.arange(len(trace))
indices=indices[indices<len(times)]
q=q[indices];w=w[indices];times=times[indices]-dt
n=min(len(trace),len(q))
ours=np.array([x['q'] for x in trace[:n]])
oq=ours[:,[1,2,3,0]]
ow=np.array([x['omega_rad_s'] for x in trace[:n]])
dif=(Rotation.from_quat(oq).inv()*Rotation.from_quat(q[:n])).magnitude()*180/np.pi
velocity_err=np.linalg.norm(ow-w[:n],axis=1)
report={'ship':shipname,'experiment':expname,'samples':n,'step_s':dt,
    'max_time_error_s':float(np.max(abs(times[:n]-np.array([x['t_s'] for x in trace[:n]])))),
    'max_attitude_difference_deg':float(np.max(dif)),
    'last_attitude_difference_deg':float(dif[n-1]),
    'max_angular_velocity_difference_rad_s':float(np.max(velocity_err)),
    'independent_solver':'NASA 42 compiled in scratch workspace',
    'scope':'constant mass and fixed nozzles: replay of realized commands, not independent GNC verification'}
(out/(tag+'_42.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
