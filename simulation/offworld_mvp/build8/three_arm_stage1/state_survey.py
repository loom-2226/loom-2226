"""Measured per-body direct SPICE survey. Each body has an isolated bounded subprocess."""
import argparse,hashlib,json,subprocess,sys,time
from datetime import datetime,timedelta,timezone
from pathlib import Path
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
from simulation.offworld_mvp.build8.solar_reach_executor_spike import load,full_catalog,eligible_public_catalog
from simulation.offworld_mvp.build8.box2_lazy_proof.proof import asset_index,missing_assets
P=Path(__file__).resolve().parent;C=json.loads((P/'state_probe_config.json').read_text());E=json.loads((P/'experiment.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def child(body):
 t=OnDemandTravel(asset_root=Path(E['asset_root']));start=datetime(min(E['years']),*map(int,E['sampling']['start_month_day'].split('-')),tzinfo=timezone.utc)+timedelta(days=E['sampling']['flight_range_days'][0]);out={}
 for n in C['probe_sizes_states_per_call']:
  epochs=[start+timedelta(days=i*C['probe_grid_step_days']) for i in range(n)];st=time.perf_counter();t._batch_states(body,epochs);out[str(n)]=time.perf_counter()-st;print(json.dumps({'times':out}),flush=True)
def main():
 data,_=load();cat=full_catalog(data);access=eligible_public_catalog(data,cat);assets,sources,cov=asset_index(Path(E['asset_root']));t=OnDemandTravel(asset_root=Path(E['asset_root']));day=f"{min(E['years'])}-{E['sampling']['start_month_day']}";bodies=sorted(r['body_id'] for r in cat if r['body_id']!=E['origin'] and r['body_class'] not in ('STAR','BARYCENTER','SPACECRAFT') and r['body_id'] in access and t.endpoint(r['body_id'],day)['status']=='DIRECT' and not missing_assets(r['body_id'],day,assets,sources,cov) and not missing_assets(E['origin'],day,assets,sources,cov));out={'classification':'MEASURED_DIRECT_SPICE_SURVEY','config_sha256':sha(P/'state_probe_config.json'),'eligible_bodies':bodies,'status_by_body':{},'measurements':{}}
 for b in bodies:
  st=time.perf_counter()
  try:
   r=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--body',b],capture_output=True,text=True,timeout=C['hard_limit_seconds_per_body_process']);elapsed=time.perf_counter()-st
   if r.returncode!=0:status='ERROR';row={'returncode':r.returncode,'stderr':r.stderr[-1000:]}
   else:status='OK';row=json.loads(r.stdout.strip().splitlines()[-1]);
  except subprocess.TimeoutExpired:status='SLOW';row={'reason':'PER_PROCESS_HARD_TIMEOUT'};elapsed=time.perf_counter()-st
  out['status_by_body'][b]=status;out['measurements'][b]={'status':status,'elapsed_seconds':elapsed,**row};print('SURVEY',b,status,round(elapsed,3),flush=True)
 path=P/'state_survey_measured.json';path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print('SURVEY_OUTPUT_SHA256',sha(path),'PATH',path,'SLOW',[b for b in bodies if out['status_by_body'][b]=='SLOW'],flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--body');a=parser.parse_args();child(a.body) if a.body else main()
