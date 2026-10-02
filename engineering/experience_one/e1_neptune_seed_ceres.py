#!/usr/bin/env python3
from pathlib import Path
import argparse, importlib.util, shutil
from datetime import datetime, timezone

READ_INPUTS=("LOOM_Navigator_Cache_v1","LOOM_2226_CIVSTATE.sqlite3")

def load_nav(repo):
    p=repo/'src'/'loom_navigator_core.py'
    spec=importlib.util.spec_from_file_location('loom_e1_neptune_seed_nav',p)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'unable to import {p}')
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def copy_input(src,dst):
    if not src.exists():
        return
    if src.is_dir():
        shutil.copytree(src,dst,dirs_exist_ok=True)
    else:
        shutil.copy2(src,dst)

def normalize_utc_epoch(value):
    text=str(value).strip()
    try:
        dt=datetime.fromisoformat(text[:-1]+'+00:00' if text.endswith('Z') else text)
    except ValueError as exc:
        raise RuntimeError(f'invalid --epoch: {value}') from exc
    if dt.tzinfo is None or dt.utcoffset()!=timezone.utc.utcoffset(dt):
        raise RuntimeError('--epoch must be an explicit UTC ISO-8601 timestamp')
    return dt.astimezone(timezone.utc).isoformat().replace('+00:00','Z')

def retime_fresh_state(nav,state,epoch):
    """Retimes only the disposable fresh E1 seed using Navigator state authority."""
    out=dict(state)
    out['epoch_utc']=normalize_utc_epoch(epoch)
    out=nav._stamp_state(out,int(state['revision']))
    nav._validate_state(out)
    if str(out.get('location_token')).upper()!='CERES':
        raise RuntimeError('retimed E1 seed no longer starts at CERES')
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',type=Path,required=True)
    ap.add_argument('--runtime-root',type=Path,required=True)
    ap.add_argument('--out-root',type=Path,required=True)
    ap.add_argument('--epoch',help='Optional UTC epoch for disposable qualification seed; no live campaign mutation')
    a=ap.parse_args()
    out=a.out_root.resolve()
    out.mkdir(parents=True,exist_ok=True)
    nav=load_nav(a.repo.resolve())
    state=nav._new_state('E1_NEPTUNE_QUALIFICATION','WAYFARER')
    nav._validate_state(state)
    if str(state.get('location_token')).upper()!='CERES':
        raise RuntimeError('Navigator fresh campaign no longer starts at CERES')
    if a.epoch:
        state=retime_fresh_state(nav,state,a.epoch)
    ledger=nav.HistoryLedger(out,state)
    ledger.append('CAMPAIGN_CREATED',None,state,{'qualification':'E1_NEPTUNE','seed_epoch_source':'EXPLICIT_QUALIFICATION_INPUT' if a.epoch else 'NAVIGATOR_FRESH_CAMPAIGN_DEFAULT'},state_after_snapshot=state)
    nav._atomic_save(out/nav.STATE_FILE,out/nav.BACKUP_FILE,state)
    for name in READ_INPUTS:
        copy_input(a.runtime_root.resolve()/name,out/name)
    for p in a.runtime_root.resolve().iterdir():
        low=p.name.lower()
        if p.is_file() and ('b1' in low or ('navigator' in low and p.suffix.lower() in ('.zip','.json'))):
            copy_input(p,out/p.name)
    print(f'CERES QUALIFICATION ROOT: {out}')
    print(f'STATE: {state["state_id"]} | {state["epoch_utc"]} | {state["location_token"]}')

if __name__=='__main__':
    main()
