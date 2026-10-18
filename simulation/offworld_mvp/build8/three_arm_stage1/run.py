"""One bounded four-arm TEST_ONLY orbital-recon experiment. Never writes a database."""
from __future__ import annotations
import copy, hashlib, json, sys, time
from collections import Counter
from datetime import date
from decimal import Decimal as D
from pathlib import Path
from simulation.offworld_mvp.build8.country_capital_input import load_investment_capacity
from simulation.offworld_mvp.build8.master_cast import actor
from simulation.offworld_mvp.build8.solar_reach_executor_spike import load, full_catalog, eligible_public_catalog, decide_bid, choose_body
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
from simulation.offworld_mvp.build8.box2_lazy_proof.proof import asset_index, missing_assets

HERE=Path(__file__).parent
ROOT=HERE.parents[3]
def rawhash(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),default=str)
def sha(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def money(x):return str(D(str(x)))

def main():
    config=json.loads((HERE/'experiment.json').read_text()); castdata,cast_sha=load()
    cast=copy.deepcopy(castdata['casts'][config['cast']]); catalog=full_catalog(castdata)
    access=eligible_public_catalog(castdata,catalog)
    source_paths={
      'executor':ROOT/'simulation/offworld_mvp/build8/solar_reach_executor_spike.py',
      'executor_cast':ROOT/'simulation/offworld_mvp/build8/solar_reach_cast.json',
      'box2':ROOT/'simulation/offworld_mvp/build8/box2_lazy_proof/proof.py',
      'box2_authored':ROOT/'simulation/offworld_mvp/build8/box2_lazy_proof/experiment.json',
      'route1':ROOT/'simulation/offworld_mvp/build8/country_capital_input.py',
      'route1_campaign':ROOT/'simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py',
      'geometry':ROOT/'simulation/offworld_mvp/build8/travel_pilot/on_demand.py',
      'catalog':ROOT/castdata['catalog_source']}
    pins={k:rawhash(v) for k,v in source_paths.items()}
    from importlib.metadata import version
    packages={k:version(k) for k in ('spiceypy','numpy','lamberthub')}
    cap,prov=load_investment_capacity(Path(config['earth_baseline_root']),max(config['years'])) if max(config['years'])>=2035 else load_investment_capacity(Path(config['earth_baseline_root']),2035)
    funding=[]
    for year in config['years']:
      for sponsor in cast['sponsors']:
        country=actor(sponsor['name'])['home_country']; modeled=cap[(country,year)]
        amount=modeled*D(config['funding_share'])
        funding.append({'year':year,'sponsor':sponsor['name'],'country':country,'capacity':money(modeled),'share':config['funding_share'],'transfer':money(amount),'label':config['funding_label']})
    travel=OnDemandTravel(asset_root=Path(config['asset_root']))
    assets,sources,coverage=asset_index(Path(config['asset_root']))
    year=config['years'][0]; day=f"{year}-{config['sampling']['month_day']}"
    statuses={}; eligible=[]
    for row in catalog:
      b=row['body_id']; endpoint=travel.endpoint(b,day); reason=endpoint['status']
      if b==config['origin']:reason='ORIGIN_NOT_DESTINATION'
      elif row['body_class'] in ('STAR','BARYCENTER','SPACECRAFT'):reason='NON_DESTINATION_'+row['body_class']
      elif b not in access:reason='NOT_STUDY_ELIGIBLE'
      elif endpoint['status']=='DIRECT':
        absent=missing_assets(b,day,assets,sources,coverage)+missing_assets(config['origin'],day,assets,sources,coverage)
        if absent:reason='REQUIRED_KERNEL_ASSET_MISSING'
        else:reason='COMPUTABLE'
      statuses[b]={'class':row['body_class'],'reason':reason}
      if reason=='COMPUTABLE':eligible.append(b)
    # The inherited subjective scorer is used without body-specific authored values.
    evaluations={}
    for sponsor in cast['sponsors']:
      _, scored=choose_body(sponsor,year,catalog,access,{},D(sponsor['cash']))
      evaluations[sponsor['name']]={r['body']:r for r in scored if r['body'] in eligible}
    # Scoring has no geometric price; a cheap screen may use public catalog ordering only.
    values={b:max((D(str(evaluations[s['name']].get(b,{}).get('score','0'))) for s in cast['sponsors']),default=D(0)) for b in eligible}
    value_order=sorted(eligible,key=lambda b:(-values[b],b))
    cheap_order=sorted(eligible)
    arms={'A_EXHAUSTIVE':eligible,'B_VALUE_FIRST':value_order[:config['shortlist_count']],
          'C_CHEAP_COST':cheap_order[:config['cheap_cost_count']], 'D_PRECOMPUTED':eligible}
    quote_cache={}; quoted_rows={}; times={}; solves={}; hits={}
    def quote(b):
      if b in quote_cache:return quote_cache[b],True
      before=travel.solve_count
      try:
        geometry=travel.geometry(config['origin'],b,day,strategy=config['sampling']['strategy'],flight_range_days=config['sampling']['flight_range_days'])
        admissible=travel.admissible(geometry,departure_limit=float(config['departure_limit_km_s']),arrival_limit=float(config['arrival_limit_km_s']))
        rate=D(config['price_rate_usd_millions_per_km_s'])
        candidates=[(rate*(D(str(x['departure_vinf_km_s']))+D(str(x['arrival_vinf_km_s']))),x) for x in admissible]
        best=min(candidates,key=lambda z:z[0]) if candidates else None
        result={'status':'PRICED','usd_millions':money(best[0]),'route1_units':money(best[0]/D(config['route1_unit_usd_millions'])),'geometry_key':sha(geometry['key'])} if best else {'status':'NO_ADMISSIBLE_SAMPLED_ROUTE'}
      except (ValueError,KeyError,RuntimeError) as exc:result={'status':'NO_QUOTE','reason':type(exc).__name__+':'+str(exc)}
      quote_cache[b]=result
      return result,False
    # One real geometry build, then B/C reuse shared exact quotes; D reads a hashed table.
    for arm in ('A_EXHAUSTIVE','B_VALUE_FIRST','C_CHEAP_COST'):
      start=time.perf_counter(); prior=travel.solve_count; cached=0
      for b in arms[arm]:
        _,hit=quote(b);cached+=int(hit)
      times[arm]=time.perf_counter()-start;solves[arm]=travel.solve_count-prior;hits[arm]=cached
    table={'identity':{'config_sha256':rawhash(HERE/'experiment.json'),'source_pins':pins,'year':year,'day':day,'sampling':config['sampling'],'transfer_family':config['transfer_family']},'quotes':quote_cache}
    table_sha=sha(table)
    start=time.perf_counter(); table_copy=json.loads(canonical(table));assert sha(table_copy)==table_sha
    times['D_PRECOMPUTED']=time.perf_counter()-start;solves['D_PRECOMPUTED']=0;hits['D_PRECOMPUTED']=len(eligible)
    # Compare actual winners after executor-local bid/decline, not merely sponsor rank.
    results={}
    for arm,bodies in arms.items():
      source=table_copy['quotes'] if arm=='D_PRECOMPUTED' else quote_cache
      sponsors=copy.deepcopy(cast['sponsors']);executors=copy.deepcopy(cast['executors'])
      cash={x['name']:D(x['cash']) for x in sponsors+executors};source_balance=D(0)
      initial=sum(cash.values(),D(0));transactions=[]; overrides=[]
      for transfer in funding:
        amount=D(transfer['transfer']);source_balance-=amount;cash[transfer['sponsor']]+=amount
        transactions.append({'type':'EARTH_CAPACITY_TO_SPONSOR','source':'EARTH_CAPACITY:'+transfer['country'],'destination':transfer['sponsor'],'amount':money(amount),'label':config['funding_label']})
      winners=[]
      for sponsor in sponsors:
        name=sponsor['name'];candidate=[]
        for b in bodies:
          q=source[b]
          if q['status']!='PRICED':continue
          score=D(str(evaluations[name].get(b,{}).get('score','0')))*D(config['value_multiplier_route1_per_score'])
          cost=D(q['route1_units']); bids=[]
          for executor in executors:
            model=executor['services'].get(config['executor_service'])
            if model is None:continue
            original=model['cost'];model['cost']=money(cost)
            state={'id':actor(executor['name'])['id'],'services':executor['services'],'beliefs':executor['beliefs'],'cash':money(cash[executor['name']])}
            # Executor decides margin, risk, capacity, reliability, working capital and expectation.
            bid=decide_bid(state,{'category':config['executor_service'],'body':b,'sponsor':name},{},year)
            model['cost']=original
            overrides.append({'executor':executor['name'],'body':b,'inherited_cost':original,'box2_cost_route1':money(cost)})
            if bid['action']=='BID':bids.append((D(bid['price']),executor['name'],bid))
          if bids:
            price,executor,bid=min(bids)
            if price<=cash[name] and price<=D(sponsor['decision']['max_contract_price']) and score>=price:
              candidate.append((score-price,b,executor,price))
        if candidate:
          surplus,b,executor,price=max(candidate,key=lambda x:(x[0],x[1]))
          cash[name]-=price;cash[executor]+=price
          transactions.append({'type':'ORBITAL_RECON_AWARD','source':name,'destination':executor,'body':b,'amount':money(price)})
          winners.append({'sponsor':name,'body':b,'executor':executor,'contract_route1_units':money(price),'surplus':money(surplus),'outcome':'AWARDED_PENDING_DELIVERY'})
      closing=sum(cash.values(),D(0))+source_balance
      if closing!=initial:raise ValueError('CONSERVATION_FAILURE:'+arm)
      results[arm]={'visible':len(catalog),'eligible':len(eligible),'quoted':len(bodies),'unquoted':len(eligible)-len(bodies),'solves':solves[arm],'cache_hits':hits[arm],'seconds':times[arm],'winners':winners,'transactions':transactions,'inherited_cost_overrides':overrides,'opening_money':money(initial),'closing_money_including_source':money(closing),'conserved':True,'body_statuses':{b:{**statuses[b],'quoted':b in bodies,'quote':source.get(b) if b in bodies else None} for b in statuses}}
    reference=results['A_EXHAUSTIVE']['winners']
    for arm,r in results.items():r['winner_changed']=r['winners']!=reference
    identity={'authored':config,'authored_sha256':rawhash(HERE/'experiment.json'),'source_pins':pins,'source_commits':config['source_commits'],'cast_sha256':cast_sha,'earth_sources':prov,'packages':packages,'table_sha256':table_sha}
    runid=sha(identity)
    science={k:{a:v for a,v in r.items() if a not in ('seconds','solves','cache_hits')} for k,r in results.items()}
    return {'run_identity':runid,'identity':identity,'effective_authored_values':config,'inherited_cast':cast,'funding':funding,'catalog_statuses':statuses,'table_sha256':table_sha,'table':table,'arms':results,'scientific_sha256':sha(science),'cpu_cores':__import__('os').cpu_count()}

if __name__=='__main__':
    first=main();second=main()
    if first['scientific_sha256']!=second['scientific_sha256'] or first['run_identity']!=second['run_identity']:
      raise SystemExit('REPLAY_MISMATCH')
    first['replay_scientific_sha256']=second['scientific_sha256'];first['replay_match']=True
    output=HERE/'RESULT.json';output.write_text(json.dumps(first,indent=2,sort_keys=True,default=str)+'\n')
    print('RUN',first['run_identity'],'REPLAY',first['replay_match'],'SCIENCE',first['scientific_sha256'])
    for k,v in first['arms'].items():print(k,'VISIBLE',v['visible'],'ELIGIBLE',v['eligible'],'QUOTED',v['quoted'],'SOLVES',v['solves'],'CACHE',v['cache_hits'],'SECONDS',round(v['seconds'],3),'WINNERS',v['winners'],'CHANGED',v['winner_changed'])
