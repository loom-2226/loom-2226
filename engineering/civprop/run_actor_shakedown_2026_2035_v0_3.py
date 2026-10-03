#!/usr/bin/env python3
"""Step C bounded 80-economy / autonomous-actor shakedown.

Actor intent/recruitment observability only unless a real proposition independently
resolves hard authorities. No qualification-control authority is injected.
"""
import argparse,collections,hashlib,json,sys,time
from dataclasses import asdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from engineering.civprop.build_earth_country_opportunity_v0_3 import load
from engineering.civprop.contracts.earth_country_opportunity_v0_3 import derive
from engineering.civprop.contracts.earth_opportunity_trigger_v0_3 import triggers
from engineering.civprop.method_lab.actor_activation_v0_3 import ActorRegistryV03
from engineering.civprop.method_lab.earth_actor_matching_v0_3 import activate_opportunity
from engineering.civprop.method_lab.bounded_proposition_v0_3 import run_proposition_cycle,PropositionDisposition
from engineering.civprop.method_lab.counterparty_recruitment_v0_3 import decompose_and_recruit,respond_to_requests,RecruitmentDisposition

CI=ROOT/'engineering/civprop/candidate_inputs'
def J(n):return json.loads((CI/n).read_text())
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def run(database,start,end):
 base=J('ACTOR_BASELINE_2026_V0_3.json');audit=J('ACTOR_ROSTER_EXECUTION_ONTOLOGY_V0_3.json');jur=J('ACTOR_JURISDICTION_2026_V0_3.json')
 years=[];seen=set(); duplicate=0
 total=collections.Counter()
 for year in range(start,end+1):
  reg=ActorRegistryV03.from_actor_baseline(base,audit)
  rows=[asdict(x) for x in derive(load(database,year))];ts=triggers(rows)
  for t in ts:activate_opportunity(trigger=t,registry=reg,jurisdiction_links=jur['links'])
  tb={t.context_id:t for t in ts};rb={f"EARTH:{r['year']}:{r['iso3']}:{r['sector']}":r for r in rows}
  ds=run_proposition_cycle(registry=reg,triggers_by_id=tb,rows_by_context=rb)
  explores=[x for x in ds if x.disposition==PropositionDisposition.EXPLORE]
  reqs=[];resps=[]
  for dec in explores:
   if dec.proposition_id in seen:duplicate+=1;continue
   seen.add(dec.proposition_id)
   ident=reg.state(dec.actor_id).identity
   iso=dec.context_id.split(':')[2];sector=dec.context_id.split(':')[3]
   q=decompose_and_recruit(decision=dec,registry=reg,jurisdiction_links=jur['links'],
      proposition_category=ident.category,iso3=iso,sector=sector,provenance_refs=(f"STEP_C_SHAKEDOWN:{year}",))
   reqs.extend(q);resps.extend(respond_to_requests(registry=reg,requests=q))
  yc=collections.Counter(x.disposition.value for x in ds);rc=collections.Counter(x.disposition.value for x in resps)
  rec={"year":year,"earth_contexts":len(rows),"relevant_actors":sum(s.level.value=="RELEVANT" for s in reg.states()),
       "proposition_decisions":len(ds),"proposition_dispositions":dict(sorted(yc.items())),
       "requests":len(reqs),"unique_request_ids":len(set(x.request_id for x in reqs)),
       "responses":len(resps),"response_dispositions":dict(sorted(rc.items())),
       "unique_explored_propositions":len(explores)}
  years.append(rec)
  total.update({"contexts":len(rows),"decisions":len(ds),"explores":len(explores),"requests":len(reqs),"responses":len(resps)})
 return {"format":"LOOM_STEP_C_ACTOR_SHAKEDOWN_V0_3","classification":"NON_CANON_UNPROMOTED",
   "period":[start,end],"autonomous_actor_target":190,"years":years,"totals":dict(total),
   "duplicate_proposition_ids":duplicate,"unique_proposition_ids":len(seen),
   "hard_authority_policy":"NO_QUALIFICATION_CONTROL_INJECTION; UNKNOWN_REMAINS_BLOCKED",
   "digest":digest(years)}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--database',default='loom_dev');ap.add_argument('--start-year',type=int,default=2026);ap.add_argument('--end-year',type=int,default=2035);ap.add_argument('--output',required=True);ap.add_argument('--verify',action='store_true');a=ap.parse_args()
 t=time.time();x=run(a.database,a.start_year,a.end_year);p=Path(a.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
 print(json.dumps(x['totals'],sort_keys=True));print('digest',x['digest'],'duplicates',x['duplicate_proposition_ids'],'seconds',round(time.time()-t,3))
 if a.verify:
  y=run(a.database,a.start_year,a.end_year);ok=x==y;print('deterministic', 'PASS' if ok else 'FAIL');raise SystemExit(0 if ok else 1)
if __name__=='__main__':main()
