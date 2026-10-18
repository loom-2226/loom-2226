"""Isolated Build 8 experimental lazy Box 2 travel price proof; no frozen edits."""
import argparse
import hashlib
import importlib.metadata
import json
import time
from datetime import date,timedelta
from decimal import Decimal
from pathlib import Path
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
from simulation.offworld_mvp.build8.travel_pilot.pilot import ANCHORS

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
MANIFESTS=[ROOT/'manifests/solar'/name for name in ('SOLAR_PHASE4B_AUTHORITY_V1.json','SOLAR_PHASE4C_MAJOR_MOONS_V1.json','SOLAR_PHASE4D_STRATEGIC_BODIES_V1.json','SOLAR_PHASE4E_CURATED_42_PLUS_5_V1.json','OFFICIAL_PLANET_CENTER_KERNELS_V1.json')]

def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))

def dates_for(y,policy):
    d=date(y,*map(int,policy['start_month_day'].split('-')));end=date(y,12,31);out=[]
    while d<=end:out.append(d.isoformat());d+=timedelta(days=policy['stride_days'])
    if policy['include_last_day'] and out[-1]!=end.isoformat():out.append(end.isoformat())
    return out

def asset_index(asset_root):
    assets={};sources={};cover={}
    for p in MANIFESTS:
        x=json.loads(p.read_text())
        for a in x.get('assets',[]):assets[a['asset_id']]=(asset_root/a['local_path'],a)
        for s in x.get('sources',[]):sources[s['ephemeris_source_id']]=s
        for c in x.get('coverage',[]):cover.setdefault(c['body_id'],[]).append(c)
    return assets,sources,cover

def missing_assets(body,epoch,assets,sources,cover):
    candidates=[c for c in cover.get(body,[]) if c['valid_from']<=epoch+'T00:00:00Z'<=c['valid_until'] and sources[c['ephemeris_source_id']]['navigation_grade']]
    if not candidates:return []
    viable=[];missing=[]
    for c in candidates:
        ids=sources[c['ephemeris_source_id']].get('kernel_asset_ids',[])
        absent=[{'asset_id':a,'path':str(assets[a][0])} for a in ids if a in assets and not assets[a][0].is_file()]
        if not absent:viable.append(c)
        else:missing.extend(absent)
    return [] if viable else missing

def replay(config,idx):
    p=OnDemandTravel(asset_root=Path(config['probe']['asset_root']))
    assets,sources,cover=asset_index(Path(config['probe']['asset_root']))
    rate=Decimal(config['pricing']['rate_usd_millions_per_km_s']);v=config['vehicle'];results=[];telemetry=[]
    for y in config['years']:
      for body in config['destinations']:
        tested=[];best=None;cache_hits=0;solves=0;wall=0.;failed=None
        for day in dates_for(y,config['sampling']):
          t=time.perf_counter();status=p.endpoint(body,day)
          if status['status']!='DIRECT':failed={'status':'UNKNOWN' if status['status'].startswith('UNKNOWN') else 'UNSUPPORTED','reason':status['status']+':'+str(status['reason'])};break
          absent=missing_assets(config['origin'],day,assets,sources,cover)+missing_assets(body,day,assets,sources,cover)
          if absent:failed={'status':'UNSUPPORTED','reason':'REQUIRED_KERNEL_ASSET_MISSING','assets':absent};break
          # The source check also covers the arrival epoch; the solver's qualified seam is authoritative.
          prior=p.solve_count
          try:g=p.geometry(config['origin'],body,day,strategy=config['sampling']['strategy'],flight_range_days=v['flight_range_days'])
          except Exception as e:
            failed={'status':'UNSUPPORTED','reason':type(e).__name__+':'+str(e)};break
          if p.solve_count==prior:cache_hits+=1
          else:solves+=1
          if config['probe']['cache_requery_each_computed_geometry']:
            before=p.solve_count
            repeated=p.geometry(config['origin'],body,day,strategy=config['sampling']['strategy'],flight_range_days=v['flight_range_days'])
            if repeated!=g or p.solve_count!=before:raise ValueError('GEOMETRY_CACHE_REPLAY_MISMATCH')
            cache_hits+=1
          choices=p.admissible(g,departure_limit=v['departure_limit_km_s'],arrival_limit=v['arrival_limit_km_s'])
          row={'departure':day,'admissible_count':len(choices),'sampled_count':g['sampled_solutions']}
          tested.append(row)
          for a in choices:
            burden=Decimal(str(a['departure_vinf_km_s']))+Decimal(str(a['arrival_vinf_km_s']))
            price=rate*burden
            candidate={'departure':day,'flight_days':a['flight_days'],'departure_vinf_km_s':a['departure_vinf_km_s'],'arrival_vinf_km_s':a['arrival_vinf_km_s'],'burden_km_s':str(burden),'price_usd_millions':str(price)}
            if best is None or (price,day,a['flight_days'])<(Decimal(best['price_usd_millions']),best['departure'],best['flight_days']):best=candidate
          wall+=time.perf_counter()-t
        # One authored, bounded daily refinement of an observed coarse status transition.
        refined=[]
        if not failed and config['sampling']['daily_refinement']:
          transitions=[(a['departure'],b['departure']) for a,b in zip(tested,tested[1:]) if bool(a['admissible_count'])!=bool(b['admissible_count'])]
          for left,right in transitions[:config['sampling']['max_transition_brackets_per_body_year']]:
            day=date.fromisoformat(left)+timedelta(days=config['sampling']['refinement_step_days'])
            while day<date.fromisoformat(right):
              d=day.isoformat();t=time.perf_counter()
              absent=missing_assets(config['origin'],d,assets,sources,cover)+missing_assets(body,d,assets,sources,cover)
              if absent:failed={'status':'UNSUPPORTED','reason':'REQUIRED_KERNEL_ASSET_MISSING','assets':absent};break
              try:g=p.geometry(config['origin'],body,d,strategy=config['sampling']['strategy'],flight_range_days=v['flight_range_days'])
              except Exception as e:failed={'status':'UNSUPPORTED','reason':type(e).__name__+':'+str(e)};break
              solves+=1
              if config['probe']['cache_requery_each_computed_geometry']:
                before=p.solve_count
                if p.geometry(config['origin'],body,d,strategy=config['sampling']['strategy'],flight_range_days=v['flight_range_days'])!=g or p.solve_count!=before:raise ValueError('GEOMETRY_CACHE_REPLAY_MISMATCH')
                cache_hits+=1
              choices=p.admissible(g,departure_limit=v['departure_limit_km_s'],arrival_limit=v['arrival_limit_km_s'])
              refined.append({'departure':d,'admissible_count':len(choices),'sampled_count':g['sampled_solutions']})
              for a in choices:
                burden=Decimal(str(a['departure_vinf_km_s']))+Decimal(str(a['arrival_vinf_km_s']));price=rate*burden
                candidate={'departure':d,'flight_days':a['flight_days'],'departure_vinf_km_s':a['departure_vinf_km_s'],'arrival_vinf_km_s':a['arrival_vinf_km_s'],'burden_km_s':str(burden),'price_usd_millions':str(price)}
                if best is None or (price,d,a['flight_days'])<(Decimal(best['price_usd_millions']),best['departure'],best['flight_days']):best=candidate
              wall+=time.perf_counter()-t;day+=timedelta(days=config['sampling']['refinement_step_days'])
            if failed:break
        value=Decimal(config['sponsor']['values_usd_millions'][body]);r={'year':y,'body':body,'status':failed['status'] if failed else ('PRICED' if best else 'EVALUATED_INFEASIBLE_SAMPLED'),'reason':failed['reason'] if failed else ('SAMPLED_FEASIBLE' if best else 'NO_ADMISSIBLE_SAMPLED_DEPARTURE_NOT_YEAR_CLOSED'),'requested_dates':dates_for(y,config['sampling']),'evaluated_dates':tested,'refined_dates':refined,'best':best,'sponsor_value_usd_millions':str(value),'sponsor_surplus_usd_millions':str(value-Decimal(best['price_usd_millions'])) if best else None,'eligible_for_award':best is not None and value-Decimal(best['price_usd_millions'])>Decimal(config['sponsor']['minimum_surplus_usd_millions'])}
        if failed and 'assets' in failed:r['missing_assets']=failed['assets']
        results.append(r);telemetry.append({'year':y,'body':body,'seconds':round(wall,6),'geometry_cache_hits':cache_hits,'new_geometry_solves':solves})
        print('replay',idx,y,body,r['status'],'solves',solves,'seconds',round(wall,2),flush=True)
    rankings={str(y):[{'body':r['body'],'surplus_usd_millions':r['sponsor_surplus_usd_millions']} for r in sorted((r for r in results if r['year']==y and r['eligible_for_award']),key=lambda r:(-Decimal(r['sponsor_surplus_usd_millions']),r['body']))] for y in config['years']}
    return {'results':results,'rankings':rankings},telemetry

def main():
    config_path=HERE/'experiment.json';raw=config_path.read_bytes();config=json.loads(raw);input_hash=sha(raw)
    installed={p:importlib.metadata.version(p) for p in config['probe']['required_packages']}
    if installed!=config['probe']['required_packages']:raise ValueError('DEPENDENCY_VERSION_MISMATCH')
    if sha(ANCHORS.read_bytes())!=config['pricing']['source_sha256']:raise ValueError('PRICE_ANCHOR_HASH_MISMATCH')
    if config['sampling']['flight_step_days']!=0.25 or config['sampling']['strategy']!='daily':raise ValueError('UNSUPPORTED_AUTHORED_SAMPLING')
    if config['sampling']['daily_refinement'] and config['sampling']['refinement_step_days']!=1:raise ValueError('UNSUPPORTED_REFINEMENT_STEP')
    if config['vehicle']['flight_range_days'][1]>5000:raise ValueError('FLIGHT_RANGE_EXCEEDS_SOLVER_BOUNDS')
    source_hashes={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in MANIFESTS}
    source_hashes[str(ANCHORS.relative_to(ROOT))]=sha(ANCHORS.read_bytes())
    source_hashes[str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__).read_bytes())
    run_identity=sha(canonical({'authored_input_sha256':input_hash,'source_hashes':source_hashes,'installed_versions':installed}).encode())
    outcomes=[];telemetry=[]
    for i in range(config['probe']['replays']):
        outcome,timing=replay(config,i+1);outcomes.append(outcome);telemetry.append(timing)
    replay_hashes=[sha(canonical(o).encode()) for o in outcomes]
    report={'classification':'EXPERIMENT_NONCANON_NONRUNTIME','authored_input':config,'authored_input_sha256':input_hash,'run_identity':run_identity,'source_hashes':source_hashes,'installed_versions':installed,'replay_hashes':replay_hashes,'replay_match':len(set(replay_hashes))==1,'scientific_results':outcomes[0],'timing_telemetry_per_replay':telemetry,'pricing_caveat':config['pricing']['caveat'],'sampling_caveat':config['probe']['date_coverage_policy']}
    (HERE/'RESULT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('RUN_ID',run_identity,'REPLAY_HASHES',replay_hashes,'MATCH',report['replay_match'],flush=True)
    if not report['replay_match']:raise ValueError('REPLAY_MISMATCH')
if __name__=='__main__':main()
