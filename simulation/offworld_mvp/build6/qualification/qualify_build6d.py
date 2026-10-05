#!/usr/bin/env python3
"""Exact finite Build 6D procedure. Failures are retained, never retuned."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json,platform,subprocess,sys,unittest
from decimal import getcontext
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
KERNEL=ROOT/'simulation/offworld_mvp/phase3b/kernel'
sys.path.insert(0,str(KERNEL))
from build6d_fixture import BASE,SCENARIO_PATH,EARTH_PATH,PROTOCOL_PATH,run_case
from offworld_kernel.provenance import source_tree_hash,verify_commit_code_linkage
from offworld_kernel.causal_trace import content_hash,reconstruct,validate_trace

MODULES=('tests.test_context_admission','tests.test_causal_trace','tests.test_comparison_random',
         'tests.test_earth_reference_slice','tests.test_build6d_integrated_qualification','tests.test_build6d_compatibility')
REQUIRED={prefix+f'{i:02}' for prefix,count in [('C',14),('U',9),('F',16),('R',10),('E',7),('L',9),('B',5)] for i in range(1,count+1)}


def witness(k,h):
    return dict(status=k.state.projects['P'].status,blocked=h.get('blocked'),remote=h.get('REMOTE').signal if 'REMOTE' in h else None,
        surface=h.get('SURFACE').signal if 'SURFACE' in h else None,
        draws={c:str(h[c+'_draw']) for c in ('REMOTE','SURFACE') if c+'_draw' in h},
        first_output=str(h['first_output'].actual_extracted) if h.get('first_output') else None,
        second_output=str(h['second_output'].actual_extracted) if h.get('second_output') else None,
        sale_count=len(k.market_clearing_records),sale_value=str(k.market_clearing_records[0].transaction_value) if k.market_clearing_records else None,
        remaining=str(k.resources['RES'].remaining),people=k.population.offworld['OFF:T1'],cohort_total=k.population.total(),
        account_balances={aid:str(a.balance) for aid,a in sorted(k.state.accounts.items())},
        earth_shadow={str(y):{key:str(value) for key,value in k.earth_shadow_at(y).items()} for y in range(1,15)},
        all_A1_A9=bool(h['audits']) and all(all(row.values()) for row in h['audits']),
        epoch_results=[r.result_fingerprint for r in h['results']],trace_root=validate_trace(k.causal_envelopes,k.causal_artifacts),
        envelope_count=len(k.causal_envelopes),artifact_count=len(k.causal_artifacts),
        policy_outcomes={label:result.decision.outcome.value for label,result in h['policies'].items()},
        decision_fingerprints={label:content_hash(result) for label,result in h['policies'].items()},
        snapshot_fingerprints={label:s.fingerprint() for label,s in h['snapshots'].items()})


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--tests-only',action='store_true');parser.add_argument('--baseline-only',action='store_true')
    args=parser.parse_args();commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    code_hash=source_tree_hash();verify_commit_code_linkage(commit,code_hash)
    protocol=json.loads(PROTOCOL_PATH.read_text());ctx=getcontext()
    if platform.python_version()!=protocol['environment']['python'] or ctx.prec!=28 or str(ctx.rounding)!='ROUND_HALF_EVEN':raise RuntimeError('qualification environment mismatch')
    files=[SCENARIO_PATH,EARTH_PATH,PROTOCOL_PATH,BASE/'BUILD6D_CORE_QUALIFICATION_PROTOCOL_V1.md',Path(__file__),Path(__file__).with_name('build6d_fixture.py'),*[KERNEL/Path(m.replace('.','/')+'.py') for m in MODULES]]
    hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in files}
    report=dict(status='IN_PROGRESS',started_utc=datetime.now(timezone.utc).isoformat(),git_commit=commit,code_tree_sha256=code_hash,input_harness_hashes=hashes,
        environment=dict(python=platform.python_version(),platform=platform.platform(),encoding=sys.getdefaultencoding(),decimal=dict(precision=ctx.prec,rounding=str(ctx.rounding),Emin=ctx.Emin,Emax=ctx.Emax,traps={x.__name__:v for x,v in ctx.traps.items()})),tests={},hostile_ids={},cases={},failures=[])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    def save():args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    save()
    class EvidenceResult(unittest.TextTestResult):
        def addSuccess(self,test):
            super().addSuccess(test);report['tests'][test.id()]='PASS';save()
        def addFailure(self,test,err):
            super().addFailure(test,err);report['tests'][test.id()]='FAIL';report['failures'].append({'test':test.id(),'traceback':self._exc_info_to_string(err,test)});save()
        def addError(self,test,err):
            super().addError(test,err);report['tests'][test.id()]='ERROR';report['failures'].append({'test':test.id(),'traceback':self._exc_info_to_string(err,test)});save()
    suite=unittest.TestLoader().loadTestsFromNames(MODULES)
    result=unittest.TextTestRunner(verbosity=1,resultclass=EvidenceResult).run(suite)
    import re
    for test,status in report['tests'].items():
        match=re.search(r'\.test_([CUFRELB][0-9]{2})_',test)
        if match:report['hostile_ids'].setdefault(match.group(1),[]).append({'test':test,'status':status})
    missing=sorted(REQUIRED-set(report['hostile_ids']))
    if missing:report['failures'].append({'missing_hostile_ids':missing})
    if not args.tests_only:
        for case in protocol['cases']:
            if args.baseline_only and case['id']!='BASELINE':continue
            for world in protocol['worlds']:
                key=case['id']+':'+world
                try:
                    k,h=run_case(world,case['overrides']);observed=witness(k,h)
                    report['cases'][key]=observed
                    if not observed['all_A1_A9']:raise RuntimeError('accounting identity failure')
                    if case['id'] in ('BASELINE','JOINT_LOW','JOINT_HIGH','EQUAL_RATIO'):
                        expected={'NULL':('ABANDONED',0),'SPARSE':('CLOSED',10),'RICH':('OPERATING',10)}[world]
                        if (observed['status'],observed['people'])!=expected:raise RuntimeError('structural success criterion mismatch')
                        if observed['sale_count']!=(0 if world=='NULL' else 1):raise RuntimeError('one-sale witness mismatch')
                    if case['id']=='BASELINE':
                        replay,rh=run_case(world);report['cases'][key]['replay_exact']=witness(replay,rh)==observed
                        if not report['cases'][key]['replay_exact']:raise RuntimeError('deterministic replay mismatch')
                        packet=reconstruct(k.causal_envelopes,k.causal_artifacts,k.causal_envelopes[-1].envelope_id,perspective='GOVERNANCE',actor_id='AUDIT')
                        # Original typed payload archive and envelopes are supplied
                        # as review evidence, not a replacement executable state.
                        trace_path=args.output.with_name(args.output.stem+'-'+world+'-trace.json')
                        from offworld_kernel.causal_trace import typed
                        trace_path.write_text(json.dumps(typed(packet),sort_keys=True,separators=(',',':'))+'\n')
                        report['cases'][key]['trace_artifact']={'path':str(trace_path),'sha256':sha256(trace_path.read_bytes()).hexdigest()}
                    print(key,observed['status'],observed['blocked'] or '',flush=True)
                except Exception as exc:
                    import traceback
                    report['failures'].append({'case':key,'error':str(exc),'traceback':traceback.format_exc()})
                    print(key,'ERROR',str(exc),flush=True)
                save()
    after={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in files}
    if hashes!=after:report['failures'].append({'input_or_harness_mutation':True})
    report['hostile_required_count']=len(REQUIRED);report['hostile_observed_count']=len(set(report['hostile_ids'])&REQUIRED)
    report['completed_utc']=datetime.now(timezone.utc).isoformat();report['status']='PASS' if result.wasSuccessful() and not report['failures'] and not (args.tests_only or args.baseline_only) else 'PARTIAL_PASS' if result.wasSuccessful() and not report['failures'] else 'FAIL'
    save();return 0 if report['status'] in ('PASS','PARTIAL_PASS') else 1

if __name__=='__main__':sys.exit(main())
