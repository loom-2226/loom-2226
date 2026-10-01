#!/usr/bin/env python3
"""Standalone integrated CIVPROP 2026-2226 machinery propagation V0.2."""
from __future__ import annotations
import argparse, hashlib, json, time, sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from engineering.civprop.long_run_integration_v0_2 import run_integrated

def canonical_sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def run(seed=42):
    out=run_integrated(seed)
    out['long_run_integration']={
      'format':'CIVPROP_LONG_RUN_INTEGRATION_V0_2',
      'status':'NON_CANON_MACHINERY_TEST_OUTPUT',
      'rule':'CLOSED_GAP_CONTRACTS_ARE_CONSUMED_NOT_REIMPLEMENTED',
    }
    out['canonical_sha256']=canonical_sha(out)
    return out

def summary(out,elapsed):
    eng=out['metadata']['engine']; decisions=Counter(x['action'] for x in out['decisions']); missions=Counter(x['action'] for x in out['mission_decisions'])
    fac=Counter(x['project_archetype_id'] for x in out['facilities'])
    gaps={x['gap_id']:x['status'] for x in out['known_gaps']}
    print('LOOM CIVPROP INTEGRATED LONG-RUN V0.2')
    print('=======================================')
    print('Status: NON-CANON MACHINERY TEST')
    print(f"Engine: {eng['id']} / {eng['version']}")
    print(f"Seed: {eng['seed']} | Period: {eng['start_year']} -> {eng['end_year']}")
    print(f"Actors: {len({x['actor_id'] for x in out['actor_states']})}")
    print(f"Project decisions: {len(out['decisions'])} | COMMIT_PROJECT: {decisions['COMMIT_PROJECT']} | WAIT: {decisions['WAIT']}")
    print(f"Mission decisions: {len(out['mission_decisions'])} | COMMIT_MISSION: {missions['COMMIT_MISSION']} | WAIT: {missions['WAIT']}")
    print(f"Missions executed/observations: {len(out['missions'])}/{len(out['observations'])}")
    print(f"Facilities: {len(out['facilities'])} | {dict(sorted(fac.items()))}")
    print(f"Pressure states/qualifications: {len(out['pressure_states'])}/{len(out['pressure_qualifications'])}")
    print(f"Resource states/flows: {len(out['resource_states'])}/{len(out['resource_flows'])}")
    print(f"Production facility states: {len(out['facility_production_states'])}")
    print(f"Power states: {len(out['power_states'])} | Traffic demand states: {len(out['traffic_demand_states'])}")
    print(f"Materialized facilities: {len(out['materialized_facilities'])} | Lifecycle states: {len(out['asset_lifecycle_states'])}")
    print('Gap status: '+', '.join(f"{k}={gaps[k]}" for k in sorted(gaps)))
    print(f"Canonical SHA-256: {out['canonical_sha256']}")
    print(f"Runtime: {elapsed:.3f} s")

def main():
    ap=argparse.ArgumentParser(description='Run integrated CIVPROP 2026-2226 actor machinery through the promoted GAP-001..013 contracts.')
    ap.add_argument('--seed',type=int,default=42)
    ap.add_argument('--output',type=Path)
    ap.add_argument('--verify',action='store_true',help='Run twice and require byte-equivalent canonical output.')
    a=ap.parse_args(); t=time.perf_counter(); out=run(a.seed); elapsed=time.perf_counter()-t
    if a.verify:
        again=run(a.seed)
        if out['canonical_sha256']!=again['canonical_sha256']: raise SystemExit('Determinism: FAIL')
        print('Determinism: PASS')
    summary(out,elapsed)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(f'Output: {a.output}')
if __name__=='__main__': main()
