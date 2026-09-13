#!/usr/bin/env python3
from pathlib import Path
import argparse, importlib.util, shutil

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

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',type=Path,required=True)
    ap.add_argument('--runtime-root',type=Path,required=True)
    ap.add_argument('--out-root',type=Path,required=True)
    a=ap.parse_args()
    out=a.out_root.resolve()
    out.mkdir(parents=True,exist_ok=True)
    nav=load_nav(a.repo.resolve())
    state=nav._new_state('E1_NEPTUNE_QUALIFICATION','WAYFARER')
    nav._validate_state(state)
    if str(state.get('location_token')).upper()!='CERES':
        raise RuntimeError('Navigator fresh campaign no longer starts at CERES')
    ledger=nav.HistoryLedger(out,state)
    ledger.append('CAMPAIGN_CREATED',None,state,{'qualification':'E1_NEPTUNE'},state_after_snapshot=state)
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
