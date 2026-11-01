"""Non-governing conventional FQ1-FQ6 test matrix, exact source-derived mass tensors.
Does not include Navigator/Metric and never modifies reference simulator."""
import sys,json,hashlib,time,copy,math,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2] / 'flight'))
from flightlab import run
BASE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--state',choices=['full','half','empty'],required=True);parser.add_argument('--dt',type=float,required=True)
parser.add_argument('--subset',choices=['all','quick'],default='all')
parser.add_argument('--fixture',type=Path,default=BASE/'wayfarer_fq_water_rcs_1960.json')
parser.add_argument('--out-dir',type=Path,default=BASE)

a=parser.parse_args()
ship=json.loads(a.fixture.read_text())
if a.fixture.resolve()==(BASE/'wayfarer_fq_water_rcs_1960.json').resolve():
    assert ship['provenance']['geometry_sha256']=='ea1fcb59f1e0a127cd48dc4e0321e7d42247e3f2e445cf89893bdefadb793266'
else:
    src=Path(__file__).resolve().parents[3]/'results/out/wayfarer_v05_geometry.json'
    assert ship['provenance']['geometry_sha256']==hashlib.sha256(src.read_bytes()).hexdigest(), 'current fixture stale'
ship['tanks'][0]['initial_kg']={'full':250000,'half':125000,'empty':0}[a.state]
clusters=sorted(set(e['id'].split('_')[0] for e in ship['rcs']))
assert len(clusters)==8
modes=list(ship['torch'][0]['modes'])
results=[]
a.out_dir.mkdir(parents=True,exist_ok=True)
log=a.out_dir/f'fq_matrix_{a.state}_{str(a.dt).replace(".","p")}_{a.subset}.json'
def case(gate,tag,kind,spec,cluster=None):
    sim=copy.deepcopy(ship)
    if cluster:sim['rcs']=[e for e in sim['rcs'] if not e['id'].startswith(cluster+'_')]
    T=spec.pop('duration_s')
    exp={'name':tag,'phases':[{'kind':kind,'duration_s':T,**spec}],'checks':{}}
    start=time.monotonic();row={'fq':gate,'case':tag,'state':a.state,'dt':a.dt,'cluster_out':cluster}
    try:
      output=run(sim,exp,dt=a.dt,sample_s=5.0)
      phase=output['phases'][0];m=output['metrics']
      fuel=m.get('known_propellant_used_kg',0) or 0
      if kind=='rcs_turn':
        valid=phase.get('attitude_error_deg',999)<=.25 and phase.get('rate_deg_s',999)<=.05 and fuel>0 and phase.get('propellant_depletion_steps',999)==0
      elif kind=='rcs_translate':
        valid=phase.get('translation_velocity_error_m_s',999)<=.02 and phase.get('attitude_hold_error_deg',999)<=.1 and fuel>0 and phase.get('propellant_depletion_steps',999)==0
      elif kind=='torch':
        accel=max((math.sqrt(sum(v*v for v in tr['force_body_N']))/max(1.,tr['mass_kg'])/9.80665 for tr in output['rcs_trace']),default=0.)
        valid=(fuel>0 and phase['propellant_depletion_steps']==0 and accel<=4.0001
               and phase['max_ideal_tvc_trim_deg']<=1.0001)
        row.update(accel_g=accel,tvc_trim_deg=phase['max_ideal_tvc_trim_deg'],min_allocated_fraction=phase['minimum_allocated_fraction'])
      row.update(status='PASS' if valid else 'FAIL',numerical_model_status=output['qualification']['status'],
                 fuel_used_kg=fuel, mass_end_kg=phase.get('mass_end_kg'),
                 depletion_steps=phase.get('propellant_depletion_steps'),
                 attitude_error_deg=phase.get('attitude_error_deg'),rate_deg_s=phase.get('rate_deg_s'),
                 translation_error_m_s=phase.get('translation_velocity_error_m_s'),
                 warnings=output.get('warnings',[]))
    except Exception as ex:row.update(status='ERROR',error=repr(ex))
    row['elapsed_s']=round(time.monotonic()-start,2)
    results.append(row)
    log.write_text(json.dumps({'geometry_sha256':ship['provenance']['geometry_sha256'],
              'state':a.state,'dt':a.dt,'results':results},indent=2,allow_nan=False)+'\n')
    print(gate,a.state,a.dt,tag,cluster or '',row['status'],'fuel',round(row.get('fuel_used_kg',0),3),'elapsed',row['elapsed_s'],flush=True)
for axis in ['pitch','roll','yaw']:
    case('FQ1',f'{axis}_180', 'rcs_turn',{'duration_s':120 if axis=='yaw' else 60,'axis':axis,'angle_deg':180})
if a.subset=='all':
 for c in clusters:
    for axis in ['pitch','roll','yaw']:
       case('FQ2',f'{axis}_180_cluster_{c}','rcs_turn',{'duration_s':120,'axis':axis,'angle_deg':180},c)
for axis in range(3):
 for sign in [-1,1]:
    dv=[0.,0.,0.];dv[axis]=.5*sign
    case('FQ3',f'translate_{"xyz"[axis]}_{"plus" if sign>0 else "minus"}','rcs_translate',{'duration_s':20,'delta_v_body_m_s':dv})
for mode in modes:
   case('FQ4',f'torch_{mode}','torch',{'duration_s':10,'mode':mode,'throttle':1.0})
print('FINISHED',a.state,a.dt,a.subset, 'PASS',sum(x['status']=='PASS' for x in results),'TOTAL',len(results),flush=True)
