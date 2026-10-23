"""TEST_ONLY, non-canon read/execute integration boundary probe. Never patches a join."""
import hashlib,json,time,traceback,resource,sys,copy,inspect
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ROOT=HERE.parents[4]
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),default=str).encode()
def sha(x):return hashlib.sha256(x).hexdigest()
scenario=json.loads((HERE/'scenario.json').read_text())
start=time.monotonic()
report={'classification':'TEST_ONLY_NONCANON_NONRUNTIME','scenario':scenario,'scenario_sha256':digest(HERE/'scenario.json'),'run_identity':sha(canonical({'scenario_sha256':digest(HERE/'scenario.json'),'source_quote_sha256':scenario['source_quote_sha256'],'source_experiment_sha256':scenario['source_experiment_sha256']})),'joins':{},'started_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()}
def save():
 report['elapsed_seconds']=round(time.monotonic()-start,3)
 report['peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
 (HERE/'results.json').write_text(json.dumps(report,sort_keys=True,indent=2,default=str)+'\n')
def record(join,status,file,function,evidence):
 report['joins'][join]={'status':status,'file':file,'function':function,'evidence':evidence};save();print(join,status,evidence,flush=True)
print('SCENARIO',json.dumps(scenario,sort_keys=True),flush=True)
print('SCENARIO_SHA256',report['scenario_sha256'],'RUN_IDENTITY',report['run_identity'],flush=True)
try:
 from simulation.offworld_mvp.build8.three_arm_stage1 import sponsor_selection
 from simulation.offworld_mvp.build8.route1_cast_payments import CastPaymentTrial,PROJECTS,SERVICES
 from simulation.offworld_mvp.build8.route1_all_body_campaign_pr3b import AllBodyCampaign,run_all_body_campaign
 from simulation.offworld_mvp.build8.return_routing import DESTINATIONS,SOURCE,resolve_destination
 from simulation.offworld_mvp.build8.ceres_downstream import CeresDownstream
 from simulation.offworld_mvp.build8.persistent_trial import run_persistent_trial
 from simulation.offworld_mvp.build8.opening import EARTH_V4_ROOT
except Exception as e:
 for j in ('J1','J2','J3','J4','J5'):record(j,'BLOCKED',__file__,'imports',repr(e))
 sys.exit(0)
# Verify pinned source bytes and 2 sponsor / 1 executor inputs before any experiment.
checks=[('source_selection_file','source_selection_sha256'),('source_quote_file','source_quote_sha256'),('source_executor_cast_file','source_executor_cast_sha256'),('source_experiment_file','source_experiment_sha256')]
for f,h in checks:
 actual=digest(HERE/scenario[f]); assert actual==scenario[h],(f,actual,scenario[h])
assert len(scenario['main_campaign_sponsors'])==2 and len(set(scenario['main_campaign_sponsors']))==2
assert len(scenario['sponsor_selection_sponsors'])==2
assert scenario['body_count'] > 0 and scenario['start_year'] <= scenario['end_year']
try:
 selection=sponsor_selection.run(BASE/'SPONSOR_SELECTION_SCENARIO.json')
 assert len(selection['sponsors'])==len(scenario['sponsor_selection_sponsors'])
 trial=CastPaymentTrial()
 mapped=[s for s in scenario['sponsor_selection_sponsors'] if s in PROJECTS]
 main_quotes={s:trial.choose_quote(s,PROJECTS[s][1]) for s in scenario['main_campaign_sponsors']}
 quote_types=sorted({r['mission_type_id'] for s in selection['sponsors'] for r in s['candidates']})
 service_types=sorted(SERVICES)
 if set(mapped)!=set(scenario['sponsor_selection_sponsors']):
  record('J1','BLOCKED','three_arm_stage1/sponsor_selection.py / build8/route1_cast_payments.py','run / CastPaymentTrial.choose_quote',{'selection_sponsors':scenario['sponsor_selection_sponsors'],'main_sponsors':scenario['main_campaign_sponsors'],'mapped_selection_sponsors':mapped,'pr_quote_mission_types':quote_types,'main_service_categories':service_types,'main_executor_quotes':{k:{'executor':v['executor'],'price':str(v['price'])} for k,v in main_quotes.items()},'reason':'PR sponsor identities and USD mission quote units have no authored bridge to main campaign sponsor/category budget units; no conversion or motive mapping authored'})
 else:record('J1','BLOCKED','build8/route1_cast_payments.py','CastPaymentTrial.choose_quote',{'reason':'PR mission quote in USD versus main category work package in abstract model units; no authored conversion in sponsor choice'})
except Exception as e:record('J1','FAIL','three_arm_stage1/sponsor_selection.py','run',repr(e))
try:
 source=inspect.getsource(CeresDownstream._distribute)
 appropriations=inspect.getsource(CeresDownstream._appropriate)
 record('J2','BLOCKED','build8/ceres_downstream.py / build8/return_routing.py','CeresDownstream._distribute / _appropriate / resolve_destination',{'return_source':SOURCE,'destination_rules':{str(k):v for k,v in DESTINATIONS.items()},'main_campaign_hook':'AllBodyCampaign.on_year','reason':'Ceres return distributions require completed resource export sale, owner and return account; mission outcome is not an authored sale or owner-return claim. No mission-return amount exists to credit next-year budget. Public treasury rule delays appropriation three years, not next year.'})
except Exception as e:record('J2','FAIL','build8/ceres_downstream.py','CeresDownstream._distribute',repr(e))
try:
 from simulation.offworld_mvp.build8.box3_2040_observation_proof import STUDY_PAYMENT_AND_OBSERVATION_YEAR
 record('J3','BLOCKED','build8/route1_all_body_campaign_pr3b.py / build8/box3_2040_observation_proof.py','AllBodyCampaign.review_completed / Box3 2040 observation flow',{'main_2040_observation_year':STUDY_PAYMENT_AND_OBSERVATION_YEAR,'reason':'No authored interface maps Route1 A1/A2 generated hidden-truth observation to a later PR-priced mission candidate utility/belief decision. PR selector consumes authored values and executor beliefs, not campaign observations.'})
except Exception as e:record('J3','FAIL','build8/box3_2040_observation_proof.py','import',repr(e))
# Run actual 2026..2226 90-body main campaign, even if earlier joins blocked.
try:
 campaign=AllBodyCampaign(body_count=scenario['body_count'],participating_sponsors=tuple(scenario['main_campaign_sponsors']))
 campaign.record_states(scenario['start_year'])
 result=run_all_body_campaign(body_count=scenario['body_count'],participating_sponsors=tuple(scenario['main_campaign_sponsors']))
 report['campaign']={'body_count':len(campaign.bodies),'result_campaign_keys':sorted(result['campaign']),'yearly_rows':len(result['rows']),'annual_rows_sha256':sha(canonical(result['rows'])),'first_year':scenario['start_year'],'last_year':scenario['end_year']};save()
 record('J4','BLOCKED','build8/route1_all_body_campaign_pr3b.py / build8/persistent_trial.py','run_all_body_campaign / run_persistent_trial',{'single_run_completed':True,'reason':'No exposed year-step/resume entry point for the same AllBodyCampaign state; persistent_trial uses separate country-opening path. Hash-for-hash segmented comparison cannot be performed without changing existing runner.'})
except Exception as e:record('J4','FAIL','build8/route1_all_body_campaign_pr3b.py','run_all_body_campaign',{'exception':repr(e),'traceback':traceback.format_exc(limit=5)})
# Replay on PR selection only; do not claim full-world replay.
try:
 original=sponsor_selection.run(BASE/'SPONSOR_SELECTION_SCENARIO.json')
 again=sponsor_selection.run(BASE/'SPONSOR_SELECTION_SCENARIO.json')
 variant=json.loads((BASE/'SPONSOR_SELECTION_SCENARIO.json').read_text())
 # Change an existing authored input by exchanging two existing sponsor valuation pairs, without inventing values.
 sponsor=variant['sponsors'][0]; keys=list(sponsor['values']); sponsor['values'][keys[0]],sponsor['values'][keys[1]]=sponsor['values'][keys[1]],sponsor['values'][keys[0]]
 changed=sponsor_selection.run(BASE/'SPONSOR_SELECTION_SCENARIO.json',scenario_override=variant)
 a=sha(canonical(original)); b=sha(canonical(again)); c=sha(canonical(changed))
 if a==b and original['run_identity']!=changed['run_identity'] and a!=c:
  record('J5','BLOCKED','three_arm_stage1/sponsor_selection.py / build8/route1_all_body_campaign_pr3b.py','run / run_all_body_campaign',{'selection_replay_pass':True,'selection_hash':a,'variant_hash':c,'variant_identity_changed':True,'reason':'Selection-only replay works; no joined full-clock state from J1-J4 to replay and compare'})
 else:record('J5','FAIL','three_arm_stage1/sponsor_selection.py','run',{'repeat_equal':a==b,'variant_identity_changed':original['run_identity']!=changed['run_identity'],'variant_result_changed':a!=c})
except Exception as e:record('J5','FAIL','three_arm_stage1/sponsor_selection.py','run',repr(e))
save()
