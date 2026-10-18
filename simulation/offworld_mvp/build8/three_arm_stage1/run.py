"""Bounded noncanon four-arm orbital-recon comparison, with no persistent world edits."""
from __future__ import annotations
import copy,hashlib,json,math,time
from datetime import datetime,timezone
from decimal import Decimal as D
from pathlib import Path
from importlib.metadata import version
from simulation.offworld_mvp.build8.country_capital_input import load_investment_capacity
from simulation.offworld_mvp.build8.master_cast import actor
from simulation.offworld_mvp.build8.solar_reach_executor_spike import load,full_catalog,eligible_public_catalog,decide_bid
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
from simulation.offworld_mvp.build8.box2_lazy_proof.proof import asset_index,missing_assets
HERE=Path(__file__).parent; ROOT=HERE.parents[3]
def hfile(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'),default=str)
def digest(x):return hashlib.sha256(enc(x).encode()).hexdigest()
def m(x):return str(D(str(x)))
def usd(units,c):return m(D(str(units))*D(c['capacity_usd_per_route1_unit']))
def quote(travel,config,b,day):
 try:
  geo=travel.geometry(config['origin'],b,day,strategy=config['sampling']['strategy'],flight_range_days=config['sampling']['flight_range_days'])
  admissible=travel.admissible(geo,departure_limit=float(config['departure_limit_km_s']),arrival_limit=float(config['arrival_limit_km_s']))
  options=[(D(config['price_rate_usd_millions_per_km_s'])*(D(str(r['departure_vinf_km_s']))+D(str(r['arrival_vinf_km_s']))),r) for r in admissible]
  if not options:return {'status':'NO_ADMISSIBLE_SAMPLED_ROUTE'}
  price=min(options,key=lambda z:z[0])[0];unit=price/D(config['route1_unit_usd_millions'])
  return {'status':'PRICED','usd_millions':m(price),'usd':m(price*D('1000000')),'route1_units':m(unit),'geometry_key':digest(geo['key'])}
 except (ValueError,KeyError,RuntimeError) as e:return {'status':'NO_QUOTE','reason':type(e).__name__+':'+str(e)}
def decide(config,cast,years,funding,evaluations,arms,quotes,statuses,metrics):
 results={}
 for arm in arms:
  sponsors=copy.deepcopy(cast['sponsors']);executors=copy.deepcopy(cast['executors'])
  cash={a['name']:D(a['cash']) for a in sponsors+executors};source=D(0);opening=sum(cash.values(),D(0))
  transactions=[];winners=[];overrides=[];yearly=[]
  for year in years:
   for f in [x for x in funding if x['year']==year]:
    amt=D(f['route1_units']);source-=amt;cash[f['sponsor']]+=amt
    transactions.append({'year':year,'kind':'EARTH_CAPACITY_TRANSFER','source':'EARTH_CAPACITY:'+f['country'],'recipient':f['sponsor'],'route1_units':m(amt),'usd':usd(amt,config),'label':config['funding_label']})
   yr_winners=[]
   for sponsor in sponsors:
    name=sponsor['name']; candidates=[];shortfalls=[]
    for b in arms[arm][year]:
     q=quotes[arm][year][b]
     if q['status']!='PRICED':continue
     value=D(evaluations[name][b]['score'])*D(config['value_multiplier_route1_per_score']);cost=D(q['route1_units']);bids=[]
     for executor in executors:
      model=executor['services'].get(config['executor_service'])
      if model is None:continue
      original=model['cost'];model['cost']=m(cost)
      state={'id':actor(executor['name'])['id'],'services':executor['services'],'beliefs':executor['beliefs'],'cash':m(cash[executor['name']])}
      bid=decide_bid(state,{'category':config['executor_service'],'body':b,'sponsor':name},{},year)
      model['cost']=original
      overrides.append({'year':year,'body':b,'executor':executor['name'],'inherited_cost_route1':original,'inherited_cost_usd':usd(original,config),'replacement_route1':m(cost),'replacement_usd':usd(cost,config),'bid_action':bid['action'],'bid_reason':bid['reason']})
      if bid['action']=='BID':bids.append((D(bid['price']),executor['name']))
     if bids:
      price,exe=min(bids)
      if price>cash[name]:shortfalls.append({'body':b,'reason':'INSUFFICIENT_BUDGET_WAIT','required_usd':usd(price,config),'available_usd':usd(cash[name],config)})
      elif price<=D(sponsor['decision']['max_contract_price']) and value>=price:candidates.append((value-price,b,exe,price))
    if candidates:
     surplus,b,exe,price=max(candidates,key=lambda x:(x[0],x[1]));cash[name]-=price;cash[exe]+=price
     t={'year':year,'kind':'ORBITAL_RECON_CONTRACT','source':name,'recipient':exe,'body':b,'route1_units':m(price),'usd':usd(price,config)}
     transactions.append(t); win={'year':year,'sponsor':name,'body':b,'executor':exe,'price_route1':m(price),'price_usd':usd(price,config),'surplus_route1':m(surplus),'status':'AWARDED_PENDING_DELIVERY'}
     winners.append(win);yr_winners.append(win)
    yearly.append({'year':year,'sponsor':name,'closing_cash_route1':m(cash[name]),'closing_cash_usd':usd(cash[name],config),'budget_shortfalls':shortfalls,'awards':yr_winners})
   if sum(cash.values(),D(0))+source!=opening:raise ValueError('CONSERVATION_FAILURE:'+arm+':'+str(year))
  qcount=sum(len(arms[arm][y]) for y in years);eligible_count=sum(sum(s['reason']=='COMPUTABLE' for s in statuses[y].values()) for y in years)
  results[arm]={'visible':len(statuses[years[0]])*len(years),'eligible':eligible_count,'quoted':qcount,'unquoted':eligible_count-qcount,'solves':metrics[arm]['solves'],'cache_hits':metrics[arm]['cache_hits'],'seconds':metrics[arm]['seconds'],'winners':winners,'transactions':transactions,'yearly':yearly,'overridden_costs':overrides,'opening_route1':m(opening),'opening_usd':usd(opening,config),'closing_including_source_route1':m(sum(cash.values(),D(0))+source),'closing_including_source_usd':usd(sum(cash.values(),D(0))+source,config),'conserved':True}
 for arm,r in results.items():r['winner_changed']=r['winners']!=results['A_EXHAUSTIVE']['winners']
 return results

def main():
 c=json.loads((HERE/'experiment.json').read_text());data,cast_sha=load();cast=copy.deepcopy(data['casts'][c['cast']]);catalog=full_catalog(data);access=eligible_public_catalog(data,catalog);years=c['years']
 if len(years)!=len(set(years)) or years!=sorted(years):raise ValueError('INVALID_AUTHORED_YEARS')
 paths={'executor':ROOT/'simulation/offworld_mvp/build8/solar_reach_executor_spike.py','executor_cast':ROOT/'simulation/offworld_mvp/build8/solar_reach_cast.json','box2':ROOT/'simulation/offworld_mvp/build8/box2_lazy_proof/proof.py','box2_authored':ROOT/'simulation/offworld_mvp/build8/box2_lazy_proof/experiment.json','route1':ROOT/'simulation/offworld_mvp/build8/country_capital_input.py','route1_mobilization':ROOT/'simulation/offworld_mvp/build8/route1_gate2.py','geometry':ROOT/'simulation/offworld_mvp/build8/travel_pilot/on_demand.py','catalog':ROOT/data['catalog_source']}
 pins={k:hfile(v) for k,v in paths.items()};cap,prov=load_investment_capacity(Path(c['earth_baseline_root']),max(max(years),c['earth_reader_min_end_year']))
 if D(c['capacity_usd_per_route1_unit'])!=D(c['route1_unit_usd_millions'])*D('1000000'):raise ValueError('UNIT_MISMATCH')
 funding=[]
 for y in years:
  for s in cast['sponsors']:
   country=actor(s['name'])['home_country'];capacity=cap[country,y];unit=capacity/D(c['capacity_usd_per_route1_unit']);funded=unit*D(c['funding_share'])
   funding.append({'year':y,'sponsor':s['name'],'country':country,'capacity_usd':m(capacity),'capacity_route1_units':m(unit),'share':c['funding_share'],'route1_units':m(funded),'usd':usd(funded,c),'label':c['funding_label']})
   if D(funding[-1]['usd'])!=capacity*D(c['funding_share']):raise ValueError('FUNDING_USD_CHECK_FAILED')
 assets,sources,coverage=asset_index(Path(c['asset_root']));probe=OnDemandTravel(asset_root=Path(c['asset_root']))
 statuses={};elig={};evaluations={s['name']:{} for s in cast['sponsors']};ordering={}
 for y in years:
  day=f"{y}-{c['sampling']['month_day']}";rows={};eligible=[]
  for row in catalog:
   b=row['body_id'];ep=probe.endpoint(b,day);reason=ep['status']
   if b==c['origin']:reason='ORIGIN_NOT_DESTINATION'
   elif row['body_class'] in ('STAR','BARYCENTER','SPACECRAFT'):reason='NON_DESTINATION_'+row['body_class']
   elif b not in access:reason='NOT_STUDY_ELIGIBLE'
   elif ep['status']=='DIRECT':reason='REQUIRED_KERNEL_ASSET_MISSING' if missing_assets(b,day,assets,sources,coverage)+missing_assets(c['origin'],day,assets,sources,coverage) else 'COMPUTABLE'
   rows[b]={'class':row['body_class'],'reason':reason}
   if reason=='COMPUTABLE':eligible.append(b)
  statuses[y]=rows;elig[y]=eligible
  epoch=datetime.fromisoformat(day).replace(tzinfo=timezone.utc);origin,_=probe._state(c['origin'],epoch);rad=math.dist(origin.position_km,(0,0,0));cheap={}
  for b in eligible:
   state,_=probe._state(b,epoch);cheap[b]=abs(math.dist(state.position_km,(0,0,0))-rad)
   for s in cast['sponsors']:
    policy=s['decision'];raw=hashlib.sha256((policy['valuation_seed']+'|'+s['name']+'|'+b).encode()).digest();sample=D(int.from_bytes(raw[:8],'big'))/D(2**64)
    override=policy['body_overrides'].get(b,{});value=D(policy['base_value'])+D(policy['value_spread'])*sample+D(override.get('value_delta','0'))
    reach=D(policy['reach_cost_by_accessibility'][access[b]])+D(override.get('reach_delta','0'))
    score=D(policy['prior'])*value-D(policy['expected_service_cost'])-reach
    evaluations[s['name']][b]={'score':m(score),'value':m(value),'reach_cost':m(reach)}
  values={b:max(D(evaluations[s['name']][b]['score']) for s in cast['sponsors']) for b in eligible}
  ordering[y]={'A_EXHAUSTIVE':eligible,'B_VALUE_FIRST':sorted(eligible,key=lambda b:(-values[b],b))[:c['shortlist_count']],'C_CHEAP_COST':sorted(eligible,key=lambda b:(cheap[b],b))[:c['cheap_cost_count']],'D_PRECOMPUTED':eligible}
 arms={a:{y:ordering[y][a] for y in years} for a in ordering[years[0]]}
 quotes={};metrics={};tables={}
 for arm in arms:
  start=time.perf_counter();travel=OnDemandTravel(asset_root=Path(c['asset_root']));armquotes={};cache_hits=0
  for y in years:
   day=f"{y}-{c['sampling']['month_day']}";armquotes[y]={}
   for b in arms[arm][y]:
    if arm=='D_PRECOMPUTED':
     # Table built once from an initially empty cache; subsequent lookup does not solve.
     pass
    armquotes[y][b]=quote(travel,c,b,day)
  build_seconds=time.perf_counter()-start;table={'policy_sha256':hfile(HERE/'experiment.json'),'source_pins':pins,'years':years,'sampling':c['sampling'],'quotes':armquotes}
  tables[arm]={'sha256':digest(table),'build_seconds':build_seconds,'rows':sum(map(len,armquotes.values()))}
  if arm=='D_PRECOMPUTED':
   lookup_start=time.perf_counter();armquotes=json.loads(enc(table))['quotes'];armquotes={int(y):v for y,v in armquotes.items()}
   metrics[arm]={'solves':travel.solve_count,'cache_hits':0,'seconds':build_seconds,'lookup_seconds':time.perf_counter()-lookup_start}
  else:metrics[arm]={'solves':travel.solve_count,'cache_hits':cache_hits,'seconds':build_seconds}
  quotes[arm]=armquotes
 result=decide(c,cast,years,funding,evaluations,arms,quotes,statuses,metrics)
 replay=decide(c,cast,years,funding,evaluations,arms,quotes,statuses,metrics)
 science=digest(result);assert science==digest(replay),'REPLAY_MISMATCH'
 identity={'authored':c,'authored_sha256':hfile(HERE/'experiment.json'),'source_commits':c['source_commits'],'source_pins':pins,'cast_sha256':cast_sha,'earth_provenance':prov,'packages':{k:version(k) for k in ('spiceypy','numpy','lamberthub')},'table_hashes':{k:v['sha256'] for k,v in tables.items()}}
 report={'run_identity':digest(identity),'identity':identity,'authored_values':c,'inherited_cast':cast,'funding':funding,'eligibility':statuses,'candidate_lists':arms,'quotes':quotes,'tables':tables,'arms':result,'scientific_sha256':science,'replay_scientific_sha256':digest(replay),'replay_match':True}
 (HERE/'RESULT.json').write_text(json.dumps(report,indent=2,sort_keys=True,default=str)+'\n')
 print('RUN',report['run_identity'],'REPLAY',report['replay_match'],'SCIENCE',science,flush=True)
 for arm,r in result.items():print(arm,'VISIBLE',r['visible'],'ELIGIBLE',r['eligible'],'QUOTED',r['quoted'],'UNQUOTED',r['unquoted'],'SOLVES',r['solves'],'CACHE_HITS',r['cache_hits'],'SECONDS',round(r['seconds'],3),'WINNERS',r['winners'],'CHANGED',r['winner_changed'],flush=True)
if __name__=='__main__':main()
