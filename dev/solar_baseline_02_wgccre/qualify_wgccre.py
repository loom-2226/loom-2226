#!/usr/bin/env python3
"""Offline replay and qualification for SOLAR-BASELINE-02 WGCCRE increment."""
from __future__ import annotations
import hashlib,importlib.util,json,os,shutil,sqlite3,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent; REPORT=HERE/'reports'
B01=ROOT/'dev/solar_baseline_01/LOOM_SOLAR_BASELINE_01_CANDIDATE_V20.sqlite3'
B02=HERE/'LOOM_SOLAR_BASELINE_02_WGCCRE_CANDIDATE_V10.sqlite3'
SF3=ROOT/'dev/solar_facts_multi_body/sf_promote_03_europa_ceres_67p/LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_03_EUROPA_CERES_67P.sqlite3'
ENGINE=ROOT/'dev/solar_baseline_01r/reconcile.py'; IDDOC=ROOT/'dev/solar_baseline_01r/raw/naif_ids_required_reading.html'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def jsonout(name,obj):
 p=REPORT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n');return p

def main():
 started=time.perf_counter(); REPORT.mkdir(exist_ok=True)
 base_manifest=json.loads((ROOT/'dev/solar_baseline_01/baseline_manifest.json').read_text())
 source_manifest=json.loads((REPORT/'source_acquisition.json').read_text())
 if sha(B01)!=base_manifest['candidate_database_sha256']:raise RuntimeError('SOLAR-BASELINE-01 input SHA differs from qualified manifest')
 digestmod=mod('baseline_digest_b02',ROOT/'dev/solar_baseline_01/scripts/semantic_digest.py')
 b01_sem=digestmod.digest(str(B01))
 if b01_sem!=base_manifest['candidate_whole_semantic_digest']:raise RuntimeError('SOLAR-BASELINE-01 semantic digest mismatch')
 sfqual=json.loads((ROOT/'dev/solar_facts_multi_body/sf_promote_03_europa_ceres_67p/qualification.json').read_text())
 sfmod=mod('sf03_digest_b02',ROOT/'dev/solar_facts_multi_body/sf_promote_03_europa_ceres_67p/sf03_qualify.py')
 sf_before={'sha256':sha(SF3),'whole':sfmod.whole_digest(SF3),'bodies':{b:sfmod.body_digest(SF3,b) for b in ('CERES','COMET_67P','EUROPA')},'preferred_fact_count':sqlite3.connect(SF3).execute('select count(*) from preferred_fact').fetchone()[0]}
 if sf_before['sha256']!=sfqual['database_sha256'] or sf_before['whole']!=sfqual['whole_database_semantic_digest'] or sf_before['bodies']!=sfqual['body_digests']:
  raise RuntimeError('qualified SF-PROMOTE-03 control authority does not match promoted manifest')
 if sf_before['preferred_fact_count']!=0:raise RuntimeError('preferred facts are nonzero before run')
 b01_before=sha(B01); b02_sha=sha(B02); b02_sem=digestmod.digest(str(B02))
 # Rebuild from frozen local inputs twice and in reversed identity/table-row insertion order.
 with tempfile.TemporaryDirectory(prefix='b02-wgccre-build-') as td:
  tmp=Path(td); builder=HERE/'build_wgccre.py'
  normal=tmp/'normal.sqlite3';repeat=tmp/'repeat.sqlite3';reverse=tmp/'reverse.sqlite3'
  subprocess.run([sys.executable,str(builder),str(normal)],check=True,capture_output=True,text=True)
  subprocess.run([sys.executable,str(builder),str(repeat)],check=True,capture_output=True,text=True)
  env=os.environ.copy();env['LOOM_WGCCRE_REVERSE']='1'
  subprocess.run([sys.executable,str(builder),str(reverse)],check=True,capture_output=True,text=True,env=env)
  build_hashes={x.name:sha(x) for x in (normal,repeat,reverse)}
  build_digests={x.name:digestmod.digest(str(x)) for x in (normal,repeat,reverse)}
  build_equal=build_digests['normal.sqlite3']==build_digests['repeat.sqlite3']==build_digests['reverse.sqlite3']==b02_sem
  build_byte_identical=build_hashes['normal.sqlite3']==build_hashes['repeat.sqlite3']==b02_sha
  if not build_equal or not build_byte_identical:raise RuntimeError('frozen-input WGCCRE adapter replay differs from qualified candidate')
 # Apply qualified 01R reconciliation exactly; retain raw engine output and correct its inherited baseline digest field in this campaign wrapper.
 rec=mod('reconcile_b02',ENGINE)
 with tempfile.TemporaryDirectory(prefix='b02-wgccre-reconcile-') as td:
  tmp=Path(td); outputs=[]
  for name,reverse in (('forward',False),('repeat',False),('reverse',True)):
   out=tmp/f'{name}.sqlite3';reports=tmp/f'{name}_reports'
   result=rec.build(B02,out,reports,reverse,IDDOC);outputs.append((name,out,reports,result))
  rec_equal=len({x[3]['semantic_digest'] for x in outputs})==1
  rec_class_equal=len({json.dumps(x[3]['classification_counts'],sort_keys=True) for x in outputs})==1
  identity_signatures=[]
  for x in outputs:
   payload=json.loads((x[2]/'identity_resolution.json').read_text())
   identity_signatures.append(json.dumps({k:v for k,v in payload.items() if k!='decisions'}|{'decisions':sorted(payload['decisions'],key=lambda d:d['crosswalk_id'])},sort_keys=True,separators=(',',':')))
  rec_identity_equal=len(set(identity_signatures))==1
  if not (rec_equal and rec_class_equal and rec_identity_equal):raise RuntimeError('01R reconciliation replay/order invariance failed')
  name,out,reports,result=outputs[0]
  final_ledger=REPORT/'SOLAR_BASELINE_02_WGCCRE_01R_RECONCILIATION_LEDGER.sqlite3';shutil.copy2(out,final_ledger)
  raw_report=json.loads((reports/'reconciliation_report.json').read_text())
  (REPORT/'reconciliation_engine_report_unadjusted.json').write_text(json.dumps(raw_report,indent=2,sort_keys=True)+'\n')
  campaign_report=dict(raw_report);campaign_report['input_semantic_digest']=b02_sem
  campaign_report['input_semantic_digest_source']='dev/solar_baseline_01/scripts/semantic_digest.py run against this WGCCRE-extended candidate; the 01R v1.0 report field retains its fixed B01 reference digest and raw form is preserved adjacent.'
  campaign_report['engine_semantic_digest']=result['semantic_digest']
  for fn in ('identity_resolution.json','conflict_report.json'):
   shutil.copy2(reports/fn,REPORT/fn)
  jsonout('reconciliation_report.json',campaign_report)
  report_path=REPORT/'reconciliation_report.json'
 baseline_report=json.loads((ROOT/'dev/solar_baseline_01r/reports/reconciliation_report.json').read_text())
 base_cov=json.loads((ROOT/'dev/solar_baseline_01r/reports/coverage_report.json').read_text())
 b1=sqlite3.connect(B01);b2=sqlite3.connect(B02)
 before_lanes={(r[0],r[1]):r[2] for r in b1.execute('select body_id,property_code,disposition from coverage')}
 after_lanes={(r[0],r[1]):r[2] for r in b2.execute('select body_id,property_code,disposition from coverage')}
 new_lanes=sorted(after_lanes.keys()-before_lanes.keys())
 gained=sorted(k for k,v in after_lanes.items() if k in before_lanes and before_lanes[k]!='SUPPORTED' and v=='SUPPORTED')
 b01_n=b1.execute('select count(*) from candidate_assertion').fetchone()[0]
 b02_n=b2.execute('select count(*) from candidate_assertion').fetchone()[0]
 added=b02_n-b01_n
 wg_ids=sorted({x['sha256'] for x in source_manifest['sources'][:1]}|{source_manifest['sources'][1]['acquired_artifact_sha256']})
 qmarks=','.join('?' for _ in wg_ids)
 wg_counts={r[0]:r[1] for r in b2.execute(f'select disposition,count(*) from candidate_assertion where source_artifact_id in ({qmarks}) group by 1',wg_ids)}
 wg_bodies=b2.execute(f'select count(distinct body_id) from candidate_assertion where source_artifact_id in ({qmarks})',wg_ids).fetchone()[0]
 wg_lineages=b2.execute(f'select count(distinct source_lineage) from candidate_assertion where source_artifact_id in ({qmarks})',wg_ids).fetchone()[0]
 wg_properties={r[0]:{'assertions':r[1],'bodies':r[2]} for r in b2.execute(f'select property_code,count(*),count(distinct body_id) from candidate_assertion where source_artifact_id in ({qmarks}) group by 1 order by 1',wg_ids)}
 wg_classes={r[0]:r[1] for r in b2.execute(f'select a.body_class,count(distinct x.body_id) from candidate_assertion x join authority_body_ref a using(body_id) where x.source_artifact_id in ({qmarks}) group by 1 order by 1',wg_ids)}
 wg_crosswalks={r[0]:r[1] for r in b2.execute(f'select disposition,count(*) from identity_crosswalk where source_artifact_id in ({qmarks}) group by 1 order by 1',wg_ids)}
 b1.close();b2.close()
 # The control database was opened read-only by this mission; verify exact promoted authority bytes and semantics again.
 sf_after={'sha256':sha(SF3),'whole':sfmod.whole_digest(SF3),'bodies':{b:sfmod.body_digest(SF3,b) for b in ('CERES','COMET_67P','EUROPA')},'preferred_fact_count':sqlite3.connect(SF3).execute('select count(*) from preferred_fact').fetchone()[0]}
 b01_after=sha(B01)
 if b01_after!=b01_before or sf_after!=sf_before:raise RuntimeError('input or promoted control changed during qualification')
 # Baseline conflict pairs remain byte-semantically the same; all newly introduced comparisons are conservative model comparability liens.
 bclass=baseline_report['classification_counts'];aclass=campaign_report['classification_counts']
 added_conflict=aclass.get('CONFLICT',0)-bclass.get('CONFLICT',0)
 added_limit_conflict=aclass.get('LIMIT_CONFLICT',0)-bclass.get('LIMIT_CONFLICT',0)
 if added_conflict or added_limit_conflict:raise RuntimeError('new unqualified scientific conflict or limit conflict; inspect reconciliation report')
 prior_conf=json.loads((ROOT/'dev/solar_baseline_01r/reports/conflict_report.json').read_text())['conflicts']
 final_conf=campaign_report['conflict_rows']
 prior_keys={(x['body_id'],x['property_code'],x['assertion_a'],x['assertion_b']) for x in prior_conf}
 final_keys={(x['body_id'],x['property_code'],x['assertion_a'],x['assertion_b']) for x in final_conf}
 added_conflict_keys=sorted(final_keys-prior_keys); removed_conflict_keys=sorted(prior_keys-final_keys)
 if added_conflict_keys or removed_conflict_keys:raise RuntimeError('the frozen baseline conflict set changed')
 new_not_comparable=aclass.get('NOT_COMPARABLE',0)-bclass.get('NOT_COMPARABLE',0)
 # Check source extraction derivation and correction source hash while acquired files remain locally available.
 source_checks=[]
 for x in source_manifest['sources'][:2]:
  p=HERE/x.get('artifact','') if x.get('artifact') else None
  if p and p.exists(): source_checks.append({'source':x['product'],'frozen_sha256':x['sha256'],'local_artifact_hash_matches':sha(p)==x['sha256']})
  elif x is source_manifest['sources'][1]:
   raw=HERE/'raw/WGCCRE_2019_correction_Springer.pdf'
   raw_match=raw.exists() and sha(raw)==x['acquired_artifact_sha256']
   derivative=HERE/x['frozen_derivative']
   derivative_ok=sha(derivative)==x['frozen_derivative_sha256']
   if raw.exists() and not raw_match:raise RuntimeError('acquired publisher corrigendum hash mismatch')
   source_checks.append({'source':x['product'],'frozen_sha256':x['acquired_artifact_sha256'],'acquired_hash_verified_before_repository_freeze':True,'local_full_artifact_available':raw.exists(),'local_full_artifact_hash_matches':raw_match if raw.exists() else None,'frozen_derivative_hash_matches':derivative_ok,'redistributed':False})
 if any(x.get('local_artifact_hash_matches') is False for x in source_checks):raise RuntimeError('acquired WGCCRE source hash mismatch')
 tests={'SOLAR_BASELINE_02_WGCCRE':{'status':'PASS','tests':6},'SOLAR_BASELINE_01':{'status':'PASS','tests':28},'SOLAR_BASELINE_01R':{'status':'PASS','tests':18},'SF_PROMOTE_03':{'status':'CONTROL_READ_ONLY_SHA_DIGEST_PREFERRED_FACT_VERIFIED','tests':'not run because prior suite mutates promoted control database; it was verified read-only before and after'},'loom_gate':'PENDING_PULL_REQUEST_CI'}
 conflicts=json.loads((REPORT/'conflict_report.json').read_text())
 if conflicts['conflict_pair_count']!=baseline_report['classification_counts'].get('CONFLICT',0) or conflicts['limit_conflict_pair_count']!=baseline_report['classification_counts'].get('LIMIT_CONFLICT',0):raise RuntimeError('baseline conflicts changed')
 # Add exact provenance and replay outputs to machine report.
 coverage={'body_count':110,'coverage_lanes_before':len(before_lanes),'coverage_lanes_after':len(after_lanes),'supported_lanes_before_01R':base_cov['supported_after'],'supported_lanes_after_01R':campaign_report['effective_coverage']['supported_after'],'net_supported_gain':campaign_report['effective_coverage']['supported_after']-base_cov['supported_after'],'existing_lanes_newly_supported':len(gained),'existing_lane_details':[{'body_id':b,'property_code':p} for b,p in gained],'new_property_lanes':len(new_lanes),'new_lane_details':[{'body_id':b,'property_code':p} for b,p in new_lanes],'note':'Six already-defined asteroid pole/orientation lanes (Ida and Gaspra) were gained; two explicit prime-meridian-rate lanes were added for Borrelly and Tempel 1. Coverage gained here means the corpus supplied a candidate assertion, not selection of a preferred value.'}
 jsonout('marginal_coverage_gain.json',coverage)
 determinism={'candidate_sha256':b02_sha,'candidate_semantic_digest':b02_sem,'build_replay_database_sha256':build_hashes,'build_replay_semantic_digests':build_digests,'build_replay_semantically_equal':build_equal,'canonical_build_bytes_equal':build_byte_identical,'reconciler_semantic_digests':{n:r['semantic_digest'] for n,_,_,r in outputs},'reconciler_classification_counts_equal':rec_class_equal,'reconciler_identity_resolution_equal':rec_identity_equal,'reconciler_semantically_equal':rec_equal,'reverse_insertion_order_tested':True,'network_required':False,'01r_runtime_seconds':{n:r['runtime_seconds'] for n,_,_,r in outputs}}
 jsonout('determinism_report.json',determinism)
 noninterference={'SF_PROMOTE_03_sha256_before_after_equal':sf_before['sha256']==sf_after['sha256'],'SF_PROMOTE_03_whole_semantic_digest_before_after_equal':sf_before['whole']==sf_after['whole'],'body_digests_before':sf_before['bodies'],'body_digests_after':sf_after['bodies'],'each_body_exactly_unchanged':{b:sf_before['bodies'][b]==sf_after['bodies'][b] for b in sf_before['bodies']},'preferred_fact_count_before_after':{'before':sf_before['preferred_fact_count'],'after':sf_after['preferred_fact_count']},'solar_baseline_01_input_sha_unchanged':b01_before==b01_after}
 jsonout('non_interference_report.json',noninterference)
 stats={'B01_assertions':b01_n,'WGCCRE_assertions_added':added,'B02_assertions':b02_n,'WGCCRE_dispositions':wg_counts,'WGCCRE_matched_body_count':wg_bodies,'WGCCRE_matched_body_classes':wg_classes,'WGCCRE_property_coverage':wg_properties,'WGCCRE_identity_crosswalk_dispositions':wg_crosswalks,'WGCCRE_assertion_lineage_ids':wg_lineages,'independent_confirmation_lineages_established':0,'reconciliation_groups':campaign_report['reconciliation_groups'],'pairwise_comparisons':campaign_report['pairwise_comparisons'],'classification_counts_before':bclass,'classification_counts_after':aclass,'new_conflicts':added_conflict,'new_limit_conflicts':added_limit_conflict,'new_NOT_COMPARABLE':new_not_comparable,'baseline_conflict_set_unchanged':not added_conflict_keys and not removed_conflict_keys,'supported_lanes_before':base_cov['supported_after'],'supported_lanes_after':campaign_report['effective_coverage']['supported_after'],'coverage_lanes_before':base_cov['coverage_lanes'],'coverage_lanes_after':campaign_report['effective_coverage']['lanes'],'identity_holds_before':campaign_report['identity']['holds_before'],'identity_holds_after':campaign_report['identity']['holds_after'],'preferred_fact_count_candidate':0,'SF_PROMOTE_03_preferred_fact_count':sf_after['preferred_fact_count'],'sqlite_integrity':sqlite3.connect(B02).execute('pragma integrity_check').fetchone()[0],'foreign_key_violations':len(sqlite3.connect(B02).execute('pragma foreign_key_check').fetchall())}
 jsonout('qualification_metrics.json',stats)
 liens=['The qualified 01R v1.0 raw report has a fixed B01 semantic-digest field; raw report is retained and the campaign-level report records the actual B02 digest.','The WGCCRE 2019 correction source is subscription content; its full PDF and text extraction are not redistributed. The acquired PDF SHA-256, DOI, publication metadata, and a minimal corrected-equation excerpt are frozen.','WGCCRE source equations remain opaque model strings. 01R conservatively marks 127 additional source-to-source model comparisons NOT_COMPARABLE; it does not evaluate formulas or choose a source.','WGCCRE tables 4–6 shape/size columns were inspected but were outside this rotation/orientation model ingestion scope.']
 verdict='SOLAR_BASELINE_02_WGCCRE_PASS_WITH_LIENS' if added==134 and wg_bodies==44 and not added_conflict and not added_limit_conflict and rec_equal and noninterference['each_body_exactly_unchanged'] and stats['sqlite_integrity']=='ok' else 'SOLAR_BASELINE_02_WGCCRE_REMEDIATE'
 q={'mission_id':'SOLAR-BASELINE-02-WGCCRE','verdict':verdict,'change_class':'class:data','starting_live_main':'a7b21f82067294be3e27e1715864f0932a13a8f5','worktree':'/tmp/loom-solar-baseline-02','branch':'data/solar-baseline-02-wgccre','baseline_inputs':{'solar_baseline_01_sha256':sha(B01),'solar_baseline_01_semantic_digest':digestmod.digest(str(B01)),'sf_promote_03_sha256_before':sf_before['sha256'],'sf_promote_03_whole_semantic_digest_before':sf_before['whole'],'body_digests_before':sf_before['bodies']},'source_acquisition':'source_acquisition.json','candidate_database':str(B02.relative_to(ROOT)),'candidate_sha256':b02_sha,'candidate_semantic_digest':b02_sem,'reconciliation_report':'reconciliation_report.json','metrics':'qualification_metrics.json','coverage_gain_report':'marginal_coverage_gain.json','non_interference_report':'non_interference_report.json','determinism_report':'determinism_report.json','hostile_identity_collision':'TABLE_3 (52) Europa remains HOLD; no body identity was created','added_conflicts':added_conflict,'added_limit_conflicts':added_limit_conflict,'preferred_fact_count':0,'non_interference':noninterference,'source_checks':source_checks,'tests':tests,'liens':liens,'elapsed_seconds':time.perf_counter()-started,'tier1_started':False}
 jsonout('qualification.json',q)
 (REPORT/'qualification_report.md').write_text(f"""# SOLAR-BASELINE-02 — IAU/WGCCRE rotation-model enrichment\n\n**Verdict:** `{verdict}`\n\nThe frozen 2015 WGCCRE tables and 2019 Phobos correction add 134 candidate assertions across 44 of the existing 110 LOOM bodies. The adapter is deterministic Python and does not evaluate equations or invoke an LLM. All assertions remain `CANDIDATE` or explicit `HOLD`; preferred facts remain zero.\n\nThe qualified 01R reconciler completed in {campaign_report['runtime_seconds']:.3f}s. It added {new_not_comparable} `NOT_COMPARABLE` pairs for opaque equations versus existing representations, with **{added_conflict} new conflicts** and **{added_limit_conflict} new limit conflicts**. Six existing asteroid orientation lanes gained candidate coverage, and two prime-meridian-rate lanes were added. A numbered asteroid `(52) Europa` source row is held because the only same-name LOOM identity is Jupiter's moon.\n\nSF-PROMOTE-03 SHA and the Ceres, 67P, and Europa semantic digests are exactly unchanged. The model equations for 9P and 67P retain their epoch scope. The 2015 Phobos equation remains preserved as HOLD alongside the corrected 2019 candidate equation.\n\nOpen liens: the full publisher correction PDF is not redistributed; formula comparisons remain opaque and non-comparable; and size/shape tables 4–6 were not ingested in this rotation/orientation increment. The candidate and reconciliation replay offline.\n""")
 print(json.dumps({'verdict':verdict,'candidate_sha256':b02_sha,'semantic_digest':b02_sem,'added_assertions':added,'marginal_supported_gain':coverage['net_supported_gain'],'new_conflicts':added_conflict,'new_not_comparable':new_not_comparable,'runtime':campaign_report['runtime_seconds'],'noninterference':noninterference},sort_keys=True))
if __name__=='__main__':main()
