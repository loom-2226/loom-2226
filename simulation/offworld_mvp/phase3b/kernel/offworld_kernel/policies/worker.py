from __future__ import annotations
import builtins
import importlib.util
import json
from pathlib import Path
import sys

def _load_policy(filename,name):
    path=Path(__file__).resolve().parent/filename
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

POLICIES={
    'FINANCIER_SCREENING_V1':_load_policy('financier_v1.py','_loom_financier_v1'),
    'PUBLIC_EXPLORER_V1':_load_policy('public_explorer_v1.py','_loom_public_explorer_v1'),
    'PUBLIC_SURFACE_PROSPECTOR_V1':_load_policy('public_surface_prospector_v1.py','_loom_public_surface_prospector_v1'),
    'PUBLIC_PUBLISHER_V1':_load_policy('public_publisher_v1.py','_loom_public_publisher_v1'),
    'SPONSOR_OPERATOR_V1':_load_policy('sponsor_operator_v1.py','_loom_sponsor_operator_v1'),
}

def _deny(*args,**kwargs):
    raise PermissionError('policy sandbox denied operation')

def _lockdown():
    builtins.open=_deny
    builtins.__import__=_deny
    builtins.input=_deny
    builtins.exec=_deny
    builtins.eval=_deny
    builtins.compile=_deny

def _hostile_probe(payload):
    results={}
    for mod in ('os','time','random','secrets','socket','subprocess','pathlib','urllib.request'):
        try:
            builtins.__import__(mod)
            results['import:'+mod]='LEAK'
        except Exception:
            results['import:'+mod]='BLOCKED'
    try:
        builtins.open('/etc/passwd','r')
        results['filesystem']='LEAK'
    except Exception:
        results['filesystem']='BLOCKED'
    snapshot=payload.get('snapshot',{})
    for key in ('world_seed','seed','hidden_state','kernel','scheduler','resources','run_identity','universe_id'):
        results['input:'+key]='LEAK' if key in snapshot else 'BLOCKED'
    results['network']='BLOCKED' if results.get('import:socket')=='BLOCKED' else 'LEAK'
    results['wall_clock']='BLOCKED' if results.get('import:time')=='BLOCKED' else 'LEAK'
    results['system_random']='BLOCKED' if results.get('import:random')=='BLOCKED' and results.get('import:secrets')=='BLOCKED' else 'LEAK'
    results['environment']='BLOCKED' if results.get('import:os')=='BLOCKED' else 'LEAK'
    return results

def main():
    payload=json.loads(sys.stdin.read())
    mode=payload.get('mode','EVALUATE')
    _lockdown()
    if mode=='HOSTILE_ACCESS_PROBE':
        result=_hostile_probe(payload)
    elif mode=='EVALUATE':
        policy_id=payload['policy_id']
        if policy_id not in POLICIES:
            raise ValueError('unsupported policy id')
        result=POLICIES[policy_id].evaluate(
            payload['snapshot'],payload['request'],payload['manifest'],payload['decision_key'])
    else:
        raise ValueError('unsupported worker mode')
    sys.stdout.write(json.dumps(result,sort_keys=True,separators=(',',':')))

if __name__=='__main__':
    main()
