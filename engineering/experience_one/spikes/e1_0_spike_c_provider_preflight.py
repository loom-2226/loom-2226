#!/usr/bin/env python3
from __future__ import annotations

"""E1.0 Spike C provider/runtime preflight.

Collects non-secret evidence about whether the Pixel/Termux runtime can plausibly
use GitHub Copilot CLI/SDK without assuming an OpenAI API key. It does NOT log
credential values and does NOT call a model.

Spike evidence only; no production architecture selection.
"""

import argparse, json, os, platform, shutil, subprocess, sys, time
from pathlib import Path
from typing import Any

DEFAULT_OUT=Path('/storage/emulated/0/Download/E1_0_SPIKE_C_PROVIDER_PREFLIGHT.json')


def run(cmd:list[str],timeout:float=15.0)->dict[str,Any]:
    t0=time.perf_counter()
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
        return {
            'cmd':cmd,
            'returncode':p.returncode,
            'stdout':p.stdout.strip()[:4000],
            'stderr':p.stderr.strip()[:4000],
            'elapsed_s':round(time.perf_counter()-t0,3),
        }
    except Exception as e:
        return {'cmd':cmd,'error':type(e).__name__+': '+str(e),'elapsed_s':round(time.perf_counter()-t0,3)}


def env_presence(name:str)->dict[str,Any]:
    v=os.environ.get(name)
    if not v: return {'present':False}
    prefix=''
    for candidate in ('github_pat_','gho_','ghu_','ghp_','ghs_','ghr_','sk-'):
        if v.startswith(candidate): prefix=candidate; break
    return {'present':True,'recognized_prefix':prefix or 'OTHER','length':len(v)}


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,default=DEFAULT_OUT)
    args=ap.parse_args()

    exes={name:shutil.which(name) for name in ('python','node','npm','copilot','gh','uname')}
    result:dict[str,Any]={
        'schema':'LOOM_E1_0_SPIKE_C_PROVIDER_PREFLIGHT_V1',
        'platform':{
            'python':sys.version,
            'system':platform.system(),
            'release':platform.release(),
            'machine':platform.machine(),
            'platform':platform.platform(),
            'android_root':os.environ.get('ANDROID_ROOT'),
            'termux_version_present':bool(os.environ.get('TERMUX_VERSION')),
            'prefix':os.environ.get('PREFIX'),
        },
        'executables':exes,
        'credential_presence_only':{
            'COPILOT_GITHUB_TOKEN':env_presence('COPILOT_GITHUB_TOKEN'),
            'GH_TOKEN':env_presence('GH_TOKEN'),
            'GITHUB_TOKEN':env_presence('GITHUB_TOKEN'),
            'OPENAI_API_KEY':env_presence('OPENAI_API_KEY'),
        },
        'checks':{},
        'notes':[
            'No credential values are recorded.',
            'This preflight does not make a model request.',
            'GitHub Models inference API is retired; candidate path is Copilot CLI/SDK.',
            'Android/Termux support must be proven empirically even if architecture is arm64.',
        ],
    }

    if exes['uname']: result['checks']['uname']=run(['uname','-a'])
    if exes['python']: result['checks']['python_version']=run([exes['python'],'--version'])
    if exes['node']: result['checks']['node_version']=run([exes['node'],'--version'])
    if exes['npm']: result['checks']['npm_version']=run([exes['npm'],'--version'])
    if exes['gh']:
        result['checks']['gh_version']=run([exes['gh'],'--version'])
        # gh auth status may reveal account name but never token value; useful entitlement-path evidence.
        result['checks']['gh_auth_status']=run([exes['gh'],'auth','status'])
    if exes['copilot']:
        result['checks']['copilot_version']=run([exes['copilot'],'--version'])
        result['checks']['copilot_help']=run([exes['copilot'],'--help'])

    node_major=None
    nv=result['checks'].get('node_version',{}).get('stdout','')
    if nv.startswith('v'):
        try: node_major=int(nv[1:].split('.')[0])
        except Exception: pass

    result['assessment']={
        'node_22_plus': bool(node_major is not None and node_major>=22),
        'npm_present': bool(exes['npm']),
        'copilot_present': bool(exes['copilot']),
        'gh_present': bool(exes['gh']),
        'github_auth_signal_present': any(result['credential_presence_only'][k]['present'] for k in ('COPILOT_GITHUB_TOKEN','GH_TOKEN','GITHUB_TOKEN')) or bool(exes['gh']),
        'next_step': None,
    }
    if exes['copilot']:
        result['assessment']['next_step']='TEST_COPILOT_AUTH_AND_MINIMAL_READ_ONLY_SESSION'
    elif exes['node'] and result['assessment']['node_22_plus'] and exes['npm']:
        result['assessment']['next_step']='INSTALL_COPILOT_CLI_THEN_RERUN_PREFLIGHT'
    else:
        result['assessment']['next_step']='PIXEL_RUNTIME_PREREQUISITE_GAP'

    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=='__main__': raise SystemExit(main())
