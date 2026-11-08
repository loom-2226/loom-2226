"""Replay realized mount commands through 42, independently integrating attitude.
42 qbn is vector-first and denotes N-to-B frame transform; numeric quaternion
components correspond to our body-to-inertial active rotation.
"""
from pathlib import Path
import json,sys,shutil,subprocess
import numpy as np
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parent; NASA=ROOT/'nasa42'; OUT=ROOT/'results'
label=sys.argv[1] if len(sys.argv)>1 else 'fixed300_pitch'
substeps=int(sys.argv[2]) if len(sys.argv)>2 else 1
case=NASA/('WF_'+label+'_'+str(substeps))
shutil.copytree(NASA/'InOut',case,dirs_exist_ok=True)
card=json.loads((ROOT/'source/design/wayfarer/v0.5.7/out/wayfarer_v05_card.json').read_text())
st=card['states']['S1'];I=np.array(st['inertia_tensor_kg_m2']);cg=st['cg_m']
th=json.loads((OUT/(label+'_mounts.json')).read_text())
cmd=np.loadtxt(OUT/(label+'_thrust.csv'),delimiter=',',skiprows=1)
ours=np.loadtxt(OUT/(label+'_state.csv'),delimiter=',',skiprows=1)
dt=cmd[1,0]-cmd[0,0];end=ours[-1,0]

def edit_lines(path,changes):
    lines=path.read_text().splitlines()
    for marker,value in changes.items():
        ix=[j for j,l in enumerate(lines) if (l.strip().endswith('! Mass') if marker=='body_mass' else marker in l)]
        assert len(ix)==1,(marker,ix)
        i=ix[0];lines[i]=str(value)+' ! '+lines[i].split('!',1)[-1]
    path.write_text('\n'.join(lines)+'\n')

edit_lines(case/'Inp_Sim.txt',{'Sim Duration':f'{end+dt/substeps} {dt/substeps}', 'File Output Interval':dt/substeps,
    'Graphics Front End':'FALSE','Input file for SC 0':'TRUE 0 SC_Wayfarer.txt'})
sc=case/'SC_Wayfarer.txt';shutil.copy(case/'SC_Simple.txt',sc)
edit_lines(sc,{'Flight Software Identifier':'PASSIVE_FSW','FSW Sample Time':dt/substeps,
    'Orbit Prop':'COWELL','Ang Vel wrt':'NQN','Ang Vel (deg/sec)':'0 0 0',
    'body_mass':st['mass_t']*1000,'Moments of Inertia':' '.join(str(I[k,k]) for k in range(3)),
    'Products of Inertia':f'{-I[0,1]} {-I[0,2]} {-I[1,2]}',
    'Location of mass center':' '.join(map(str,cg)),'Node File Name':'Nodes_Wayfarer.txt'})
lines=sc.read_text().splitlines();i=next(i for i,l in enumerate(lines) if 'Thruster Parameters' in l)
j=next(j for j,l in enumerate(lines) if '*** Gyro' in l)
thr=[lines[i],str(len(th))+' ! Number of Thrusters']
for k,t in enumerate(th):
    d=np.array(t['f'])/25000
    thr += [f'===== Thr {k} =====','PROPORTIONAL',str(t['max_force_N']),' '.join(map(str,d)), '0',str(k)]
sc.write_text('\n'.join(lines[:i]+thr+lines[j:])+'\n')
(case/'Nodes_Wayfarer.txt').write_text('Wayfarer nodes\nrev7 actual mounts\n'+str(len(th))+'\nLocations\n'+'\n'.join(' '.join(map(str,t['pos']))+f' "{t["cluster"]}:{t["kind"]}"' for t in th)+'\n')
commands=['Wayfarer mount-force replay: realized fractional thrust, not control software']
for row in cmd:
    for k,u in enumerate(row[1:]):commands.append(f'{row[0]:.8f} SC[0].AC.Thr[{k}].ThrustLevelCmd = {np.clip(u,0,1):.16g}')
commands+=['EOF']
(case/'Inp_Cmd.txt').write_text('\n'.join(commands)+'\n')
with (OUT/(label+f'_42_{substeps}.log')).open('w') as log:
    r=subprocess.run(['./42',case.name],cwd=NASA,stdout=log,stderr=subprocess.STDOUT)
assert r.returncode==0,r.returncode
q=np.loadtxt(case/'qbn.42');w=np.loadtxt(case/'wbn.42')
t=np.loadtxt(case/'time.42')
# 42 commands update actuators after the dynamics step; documented one-step latency.
indices=1+np.arange(len(ours))*substeps
indices=indices[indices<len(t)]
q=q[indices];w=w[indices];t=t[indices]-dt/substeps
n=min(len(t),len(ours));oq=ours[:n,[2,3,4,1]]
delta=(Rotation.from_quat(oq).inv()*Rotation.from_quat(q[:n])).magnitude()*180/np.pi
target=Rotation.from_rotvec([0,np.pi,0]);err=(Rotation.from_quat(q[:n]).inv()*target).magnitude()*180/np.pi
result={'label':label,'n_samples_42':len(t),'n_samples_python':len(ours),'dt42_s':dt/substeps,
 'documented_command_pipeline_delay_s':dt/substeps,
 'max_time_alignment_error_s':float(np.max(abs(t[:n]-ours[:n,0]))),
 'max_attitude_difference_deg':float(delta.max()),'final_attitude_difference_deg':float(delta[-1]),
 'max_angular_velocity_difference_rad_s':float(np.linalg.norm(w[:n]-ours[:n,5:8],axis=1).max()),
 'final_attitude_error_deg':float(err[-1]),'final_rate_deg_s':float(np.linalg.norm(w[n-1])*180/np.pi),
 'scope':'42 actual thruster force/torque and full Euler dynamics; same realized thrust replay, not independent controller/hardware',
 'inertia_product_sign':'42 input products negated to preserve actual LOOM off-diagonal tensor entries'}
print(json.dumps(result,indent=2));(OUT/(label+f'_42_{substeps}.json')).write_text(json.dumps(result,indent=2)+'\n')
np.savetxt(OUT/(label+f'_42_{substeps}_attitude.csv'),np.column_stack((t[:n],q[:n],w[:n],delta,err)),delimiter=',',header='t,qx,qy,qz,qw,wx,wy,wz,difference_deg,error_deg',comments='')
