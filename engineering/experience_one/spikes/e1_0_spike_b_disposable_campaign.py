#!/usr/bin/env python3
from __future__ import annotations

"""E1.0 Spike B — disposable-state interplanetary campaign continuity.

Exercises the EXISTING Navigator campaign flight path against a disposable copy
of authoritative campaign state/history. The real campaign is hashed before and
after and must remain bit-identical. No duplicate campaign mutation logic is
implemented here.
"""

import argparse, builtins, hashlib, importlib.util, json, os, shutil, tempfile
from pathlib import Path
from typing import Any

CAMPAIGN_FILES=("LOOM_STATE_V1.json","LOOM_STATE_V1.bak","LOOM_CAMPAIGN_HISTORY.jsonl.gz")
READ_INPUTS=("LOOM_Navigator_Cache_v1","LOOM_2226_CIVSTATE.sqlite3")
SCRIPT_PATH=Path(__file__).resolve(); DEFAULT_REPO=SCRIPT_PATH.parents[3]
ANDROID_ROOT=Path('/storage/emulated/0/Download'); DEFAULT_ROOT=ANDROID_ROOT if ANDROID_ROOT.exists() else Path.cwd()


def sha256_file(p:Path)->str|None:
    if not p.exists() or not p.is_file(): return None
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()


def campaign_hashes(root:Path)->dict[str,str|None]: return {n:sha256_file(root/n) for n in CAMPAIGN_FILES}


def load_module(path:Path):
    spec=importlib.util.spec_from_file_location('loom_e1_spike_b_nav',path)
    if spec is None or spec.loader is None: raise RuntimeError(f'unable to import {path}')
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def copy_or_link(src:Path,dst:Path)->None:
    if not src.exists(): return
    try: os.symlink(src,dst,target_is_directory=src.is_dir()); return
    except Exception: pass
    if src.is_dir(): shutil.copytree(src,dst)
    else: shutil.copy2(src,dst)


def prepare_disposable(real:Path,tmp:Path)->None:
    if not (real/'LOOM_STATE_V1.json').exists() or not (real/'LOOM_CAMPAIGN_HISTORY.jsonl.gz').exists():
        raise RuntimeError('existing state and history required; refusing to create campaign')
    for n in CAMPAIGN_FILES:
        p=real/n
        if p.exists(): shutil.copy2(p,tmp/n)
    for n in READ_INPUTS: copy_or_link(real/n,tmp/n)
    for p in real.iterdir():
        if p.name in CAMPAIGN_FILES or p.name in READ_INPUTS: continue
        low=p.name.lower()
        if p.is_file() and ('b1' in low or ('navigator' in low and p.suffix.lower() in ('.zip','.json'))): copy_or_link(p,tmp/p.name)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,default=DEFAULT_ROOT)
    ap.add_argument('--repo',type=Path,default=DEFAULT_REPO)
    ap.add_argument('--destination',default='NEPTUNE_SYSTEM')
    ap.add_argument('--priority',default='BALANCED')
    ap.add_argument('--plan',type=int,default=1)
    ap.add_argument('--out',type=Path,default=DEFAULT_ROOT/'E1_0_SPIKE_B_CAMPAIGN_RESULT.json')
    args=ap.parse_args(); real=args.root.resolve(); repo=args.repo.resolve()
    before=campaign_hashes(real)
    if before['LOOM_STATE_V1.json'] is None or before['LOOM_CAMPAIGN_HISTORY.jsonl.gz'] is None: raise RuntimeError('real campaign artifacts missing')
    navmod=load_module(repo/'src'/'loom_navigator_core.py')
    real_state=json.loads((real/'LOOM_STATE_V1.json').read_text(encoding='utf-8'))
    origin=real_state['location_token']; dest=str(args.destination)
    if dest.upper()==str(origin).upper(): raise RuntimeError('destination equals current location')
    result:dict[str,Any]={'schema':'LOOM_E1_0_SPIKE_B_CAMPAIGN_RESULT_V1','origin':origin,'destination':dest,'priority':args.priority.upper(),'real_campaign_hashes_before':before,'authorized_plan_number':args.plan,'authority_path':'EXISTING_NAVIGATOR_CAMPAIGN_FLIGHT_PATH'}

    with tempfile.TemporaryDirectory(prefix='loom_e1_spike_b_') as td:
        tmp=Path(td); prepare_disposable(real,tmp)
        original_path_ctor=navmod.Path
        download_literal='/storage/emulated/0/Download'
        def redirected_path(*parts):
            if len(parts)==1 and str(parts[0])==download_literal: return tmp
            return Path(*parts)
        navmod.Path=redirected_path
        navmod._MVP_INJECTED_COMMAND={
          'BASE_STATE':real_state['state_id'],'ELAPSED_HOURS':'0','LOCATION':origin,
          'DESTINATION':dest,'PRIORITY':args.priority.upper(),
          'CONSIDER_GRAVITY_ASSISTS':'NO','CONSIDER_PRECISION_COLLAPSE':'NO',
          'CONSIDER_SOLAR_WEATHER':'NO','CONSIDER_EXCHANGE_ASSIST':'NO',
          'NOTES':'E1.0 Spike B disposable campaign continuity test.'}
        # Existing Navigator still asks the human to choose the operational strategy
        # before choosing a ranked direct plan and explicitly authorizing commit.
        # 1 = DIRECT_NAVIGATION, then --plan, then y for COMMIT FLIGHT.
        responses=iter(['1',str(args.plan),'y']); original_input=builtins.input
        def scripted_input(prompt=''):
            try: value=next(responses)
            except StopIteration: raise RuntimeError(f'unexpected interactive prompt: {prompt!r}')
            print(f'{prompt}{value}'); return value
        builtins.input=scripted_input
        # Navigator normally ends an authorized flight by serving its generated HTML
        # indefinitely for human/browser qualification. That presentation hold is not
        # part of Spike B's campaign-continuity question, so replace only the server
        # hold with a no-op while leaving planning, validation, commit, persistence,
        # history, HTML generation and deterministic flight execution untouched.
        original_serve_sequence_d=navmod._load_core(tmp/'LOOM_E1_SPIKE_B_SERVER_PATCH').serve_sequence_d
        core_for_run=navmod._load_core(tmp/'LOOM_E1_SPIKE_B_SERVER_PATCH')
        original_load_core=navmod._load_core
        def load_core_without_server_hold(internal):
            core=original_load_core(internal)
            core.serve_sequence_d=lambda *a,**k: print('SPIKE B SERVER HOLD     SKIPPED / PRESENTATION OUT OF SCOPE')
            return core
        navmod._load_core=load_core_without_server_hold
        try:
            navmod._navigator_one_action_main()
        finally:
            builtins.input=original_input; navmod.Path=original_path_ctor; navmod._load_core=original_load_core

        sp=tmp/navmod.STATE_FILE; bp=tmp/navmod.BACKUP_FILE
        restarted,mode=navmod._setup_campaign(sp,bp,tmp/navmod.HISTORY_FILE)
        ledger=navmod.HistoryLedger(tmp,restarted)
        restarted=navmod._history_recover_if_needed(ledger,restarted,sp,bp); ledger.state=restarted
        arrivals=[r for r in ledger.records if r.get('record_type')=='FLIGHT_ARRIVED']
        if not arrivals: raise RuntimeError('no FLIGHT_ARRIVED record after authorized flight')
        arrival=arrivals[-1]; fid=arrival.get('flight_id'); rows=ledger.flight_records(fid)
        committed=next((r for r in rows if r.get('record_type')=='FLIGHT_COMMITTED'),None)
        if committed is None: raise RuntimeError('no FLIGHT_COMMITTED record for arrived flight')
        core=navmod._load_core(tmp/'LOOM_E1_SPIKE_B_INTERNAL'); replay_ok=bool(navmod._replay_flight(core,ledger,fid,tmp))
        result.update({'flight_id':fid,'disposable_mode_after_restart':mode,'flight_record_types':[r.get('record_type') for r in rows],'restart_state_id':restarted.get('state_id'),'restart_state_sha256':restarted.get('state_sha256'),'restart_location':restarted.get('location_token'),'restart_epoch_utc':restarted.get('epoch_utc'),'restart_remass_t':restarted.get('ship',{}).get('remass_t'),'restart_wet_mass_t':restarted.get('ship',{}).get('wet_mass_t'),'last_flight':restarted.get('last_flight'),'kinematic_boundary':restarted.get('kinematic_boundary'),'committed_plan_sha256':committed.get('details',{}).get('plan_sha256'),'replay_pass':replay_ok,'restart_destination_pass':str(restarted.get('location_token')).upper()==dest.upper(),'committed_and_arrived_pass':True})

    after=campaign_hashes(real); result['real_campaign_hashes_after']=after; result['real_campaign_unchanged_pass']=before==after
    result['spike_observation_pass']=bool(result['real_campaign_unchanged_pass'] and result['replay_pass'] and result['restart_destination_pass'] and result['committed_and_arrived_pass'])
    args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(result,indent=2,sort_keys=True),encoding='utf-8'); print(json.dumps(result,indent=2,sort_keys=True))
    if not result['real_campaign_unchanged_pass']: raise RuntimeError('REAL CAMPAIGN MUTATED — HARD FAIL')
    return 0 if result['spike_observation_pass'] else 2


if __name__=='__main__': raise SystemExit(main())
