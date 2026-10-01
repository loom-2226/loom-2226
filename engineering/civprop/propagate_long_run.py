#!/usr/bin/env python3
"""Standalone CIVPROP 2026-2226 actor-machinery propagation experiment V0.1.

This is deliberately NON_CANON. It exercises the promoted Earth economic
trajectory, actor baseline, interactions, CIVPROP project economics and a
minimal endogenous project/facility stock. It does not replace HYBRID_V1.
"""
from __future__ import annotations
import argparse, hashlib, json, random, time
from collections import Counter, defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
ACTORS=HERE/'contracts/actor_machinery_test_baseline_v0_1.json'
SUPPORT=HERE/'compiled_inputs/actor_earth_support_v0_1.json'
PARAMS=HERE/'contracts/actor_bridge_parameters_v0_1.json'
PROJECTS=HERE/'contracts/project_economics_v1.json'
LIFECYCLE=HERE/'contracts/asset_lifecycle_machinery_test_v0_1.json'

def load():
    actor=json.loads(ACTORS.read_text()); support=json.loads(SUPPORT.read_text())
    params=json.loads(PARAMS.read_text()); projects=json.loads(PROJECTS.read_text()); lifecycle=json.loads(LIFECYCLE.read_text())
    if actor['status']!='NON_CANON_MACHINERY_TEST_FIXTURE': raise ValueError('actor fixture status mismatch')
    if support['status']!='COMPILED_FROM_PROMOTED_EARTH_V4_ECONOMIC_TRAJECTORY_FOR_MACHINERY_TEST': raise ValueError('Earth support status mismatch')
    if params['status']!='NON_CANON_MACHINERY_TEST_ASSUMPTIONS': raise ValueError('bridge parameter status mismatch')
    return actor,support,params,projects,lifecycle

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical_sha(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def run(seed=42,start_year=2026,end_year=2226):
    if start_year<2026 or end_year>2226 or end_year<start_year: raise ValueError('supported horizon is 2026..2226')
    actor_pkg,support,params,project_pkg,lifecycle_pkg=load(); rng=random.Random(seed)
    lifecycle_policy={x['project_archetype_id']:x for x in lifecycle_pkg['policies']}
    support_by={(x['year'],x['iso3']):x for x in support['rows']}
    projects={x['project_archetype_id']:x for x in project_pkg['projects']}
    actors={a['actor_id']:a for a in actor_pkg['actors']}
    edges=actor_pkg['seed_edges']
    balances={a:0.0 for a in actors}; experience={a:0 for a in actors}; learned_caps={a:set() for a in actors}
    active=[]; facilities=[]; decisions=[]; transactions=[]; annual=[]
    caps=defaultdict(float)
    provider_edges=defaultdict(list)
    for e in edges: provider_edges[e['from']].append(e)

    def annual_capacity(a,year):
        inv=sum(float(support_by[(year,i)]['investment']) for i in a['earth_economy_links'])/1e9
        cls=a['actor_class']
        frac=(params['commercial_host_investment_allocation_fraction'] if cls=='COMMERCIAL'
              else params['multinational_member_allocation_fraction'] if cls=='MULTINATIONAL_AGENCY'
              else params['public_investment_allocation_fraction'])
        return inv*frac

    def has_cap(aid,cap):
        if cap in learned_caps[aid]:
            return True,None
        state=actors[aid]['capability'].get(cap,'UNKNOWN')
        if state=='OPERATIONAL':
            return True,None
        # ACCESS is deliberately resolved through an admitted provider edge when possible,
        # so access is not silently converted into owned capability.
        if state=='ACCESS':
            for e in provider_edges[aid]:
                provider=e['to']
                if actors.get(provider,{}).get('capability',{}).get(cap)=='OPERATIONAL':
                    return True,provider
            return True,None
        for e in provider_edges[aid]:
            provider=e['to']
            if actors.get(provider,{}).get('capability',{}).get(cap)=='OPERATIONAL':
                return True,provider
        return False,None

    for year in range(start_year,end_year+1):
        # Commission funded projects, then apply explicit machinery-test lifecycle.
        still=[]
        for p in active:
            if p['commission_year']<=year:
                p['retired_year']=None; p['gross_productive_capital']=p['capital_cost']
                facilities.append(p)
                if p['project'] in {'SURFACE_PORT','POWER_PLANT','HABITAT','RESOURCE_PLANT','INDUSTRIAL_WORKSHOP'}:
                    learned_caps[p['owner']].add('SURFACE_INFRASTRUCTURE')
            else: still.append(p)
        active=still
        caps=defaultdict(float); maintenance_total=0.0; retirements=0
        for f in facilities:
            policy=lifecycle_policy.get(f['project'])
            age=year-f['commission_year']
            if f['retired_year'] is None and policy and age>=policy['service_life_years']:
                f['retired_year']=year; retirements+=1
            if f['retired_year'] is None:
                for k,v in f['outputs'].items(): caps[k]+=float(v)
                if policy:
                    if age>0 and age%policy['maintenance_interval_years']==0:
                        m=f['gross_productive_capital']*policy['maintenance_cost_fraction']
                        balances[f['owner']]-=min(m,max(0.0,balances[f['owner']])); maintenance_total+=m
                    f['gross_productive_capital']=max(0.0,f['gross_productive_capital']*(1-policy['annual_depreciation_rate']))
        year_commits=0; year_waits=0; year_growth=0.0; year_replacement=0.0
        for aid,a in actors.items():
            balances[aid]=balances[aid]*params['annual_budget_carry_fraction']+annual_capacity(a,year)
            # One candidate per actor-year, rotating with experience so growth can diversify.
            order=params['project_order']; candidate=order[experience[aid]%len(order)]
            # If the desired project is blocked by shared physical infrastructure, actors may
            # propose the explicit enabling CIVPROP archetype rather than waiting forever.
            desired=projects[candidate]
            desired_missing=[k for k,v in desired.get('prerequisites',{}).items() if caps[k] < float(v['nominal'])]
            enabler={'power':'POWER_PLANT','transport':'LOGISTICS_NODE','industrial':'INDUSTRIAL_WORKSHOP'}.get(desired_missing[0]) if desired_missing else None
            if enabler is not None:
                candidate=enabler
            proj=projects[candidate]; req=params['capability_requirements'][candidate]
            providers=[]; missing=[]
            for cap in req:
                ok,provider=has_cap(aid,cap)
                if not ok: missing.append(cap)
                elif provider: providers.append(provider)
            # Physical prerequisites are satisfied only by already commissioned shared stock.
            physical_missing=[]
            for k,v in proj.get('prerequisites',{}).items():
                if caps[k] < float(v['nominal']): physical_missing.append(k)
            cost=float(proj['capital_cost']['nominal'])
            behavior=a['behavior']
            score=(0.35*behavior['investment_propensity']+0.20*behavior['risk_tolerance']+
                   0.25*behavior['exploration_weight']+0.20*behavior['commercial_weight']+
                   min(experience[aid],20)*0.005+rng.uniform(-params['decision_noise'],params['decision_noise']))
            feasible=not missing and not physical_missing and balances[aid]>=cost
            commit=feasible and score>=params['commit_threshold']
            reason='COMMIT' if commit else ('CAPABILITY' if missing else 'INFRASTRUCTURE' if physical_missing else 'BUDGET' if balances[aid]<cost else 'SCORE')
            decisions.append({'year':year,'actor_id':aid,'project':candidate,'decision':'COMMIT' if commit else 'WAIT','reason':reason,'score':round(score,6),'budget_before':round(balances[aid],6),'missing_capabilities':missing,'missing_infrastructure':physical_missing})
            if not commit:
                year_waits+=1; continue
            balances[aid]-=cost; experience[aid]+=1; year_commits+=1
            replacement=any(f['owner']==aid and f['project']==candidate and f['retired_year'] is not None for f in facilities)
            investment_class='REPLACEMENT' if replacement else 'GROWTH'
            if replacement: year_replacement+=cost
            else: year_growth+=cost
            for provider in sorted(set(providers)):
                fee=cost*0.05
                balances[provider]+=fee; balances[aid]-=min(fee,balances[aid])
                transactions.append({'year':year,'type':'BUY/PARTNER','buyer':aid,'provider':provider,'project':candidate,'test_transfer':round(fee,6)})
            lag=max(1,int(round(float(proj['construction_lag']['nominal']))))
            outputs={k:float(v['nominal']) for k,v in proj.get('outputs',{}).items()}
            active.append({'facility_id':f'{aid}-{candidate}-{year}-{experience[aid]}','owner':aid,'project':candidate,'funded_year':year,'commission_year':year+lag,'capital_cost':cost,'outputs':outputs,'investment_class':investment_class})
        annual.append({'year':year,'commits':year_commits,'waits':year_waits,'commissioned_facilities':len(facilities),'projects_under_construction':len(active),'shared_capacity':dict(sorted(caps.items())),'actor_budget_total':round(sum(balances.values()),6),'maintenance_requirement':round(maintenance_total,6),'retirements':retirements,'growth_investment':round(year_growth,6),'replacement_investment':round(year_replacement,6)})
    result={'format':'CIVPROP_LONG_RUN_ACTOR_MACHINERY_V0_1','status':'NON_CANON_MACHINERY_TEST_OUTPUT','seed':seed,'start_year':start_year,'end_year':end_year,
      'inputs':{'actor_baseline_sha256':sha(ACTORS),'earth_support_sha256':sha(SUPPORT),'bridge_parameters_sha256':sha(PARAMS),'project_economics_sha256':sha(PROJECTS),'lifecycle_parameter_sha256':sha(LIFECYCLE),'earth_source_designation':support['source_designation']},
      'semantics':['Earth-to-actor allocation fractions and behavior weights are non-empirical machinery-test assumptions.','Project cost/lag/output uses CIVPROP Project Economics V1 nominal scenario assumptions.','Maintenance, accounting depreciation and deterministic retirement use an explicit non-canon Asset Lifecycle V1 machinery-test parameter set.','Commissioned capacities are shared machinery-test infrastructure in V0.1; ownership is retained.','No canon future event is forced.'],
      'annual':annual,'decisions':decisions,'transactions':transactions,'facilities':facilities,'under_construction':active,
      'actor_final':{a:{'budget':round(balances[a],6),'experience':experience[a],'learned_capabilities':sorted(learned_caps[a])} for a in sorted(actors)}}
    result['canonical_sha256']=canonical_sha(result)
    return result

def summary(out,elapsed):
    d=Counter(x['decision'] for x in out['decisions']); reasons=Counter(x['reason'] for x in out['decisions'])
    print('LOOM CIVPROP LONG-RUN ACTOR MACHINERY V0.1')
    print('==========================================')
    print(f"Status: {out['status']}")
    print(f"Seed: {out['seed']} | Period: {out['start_year']} -> {out['end_year']}")
    print(f"Decisions: {len(out['decisions'])} | COMMIT: {d['COMMIT']} | WAIT: {d['WAIT']}")
    print(f"Wait reasons: {dict(sorted(reasons.items()))}")
    print(f"Commissioned facilities: {len(out['facilities'])} | Under construction: {len(out['under_construction'])}")
    print(f"Transactions: {len(out['transactions'])}")
    print(f"Lifecycle retirements: {sum(x['retirements'] for x in out['annual'])} | Maintenance: {sum(x['maintenance_requirement'] for x in out['annual']):.3f} USD_2026_billion")
    print(f"Growth investment: {sum(x['growth_investment'] for x in out['annual']):.3f} | Replacement investment: {sum(x['replacement_investment'] for x in out['annual']):.3f} USD_2026_billion")
    print(f"Final shared capacity: {out['annual'][-1]['shared_capacity']}")
    print(f"Canonical SHA-256: {out['canonical_sha256']}")
    print(f"Runtime: {elapsed:.3f} s")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--seed',type=int,default=42); ap.add_argument('--start-year',type=int,default=2026); ap.add_argument('--end-year',type=int,default=2226)
    ap.add_argument('--output',type=Path); ap.add_argument('--verify',action='store_true')
    a=ap.parse_args(); t=time.perf_counter(); out=run(a.seed,a.start_year,a.end_year); elapsed=time.perf_counter()-t
    if a.verify:
        out2=run(a.seed,a.start_year,a.end_year)
        if out['canonical_sha256']!=out2['canonical_sha256']: raise SystemExit('DETERMINISM: FAIL')
        print('Determinism: PASS')
    summary(out,elapsed)
    if a.output: a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(f'Output: {a.output}')
if __name__=='__main__': main()
