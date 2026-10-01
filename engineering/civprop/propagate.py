#!/usr/bin/env python3
"""Human-facing standalone launcher for the qualified LOOM CIVPROP baseline."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engineering.civprop.run_civprop_v1 import build_output, default_paths, RUNNER_VERSION

HERE=Path(__file__).resolve().parent
MANIFEST=HERE/'baselines'/'CIVPROP_ENGINE_V1_GAP13_BASELINE_MANIFEST.json'
GOLDEN=HERE/'baselines'/'CIVPROP_ENGINE_V1_GAP13_ASSET_LIFECYCLE_SEED42.json'

def canonical_sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def run(seed:int):
    input_dir,catalog=default_paths()
    return build_output(input_dir=input_dir,infrastructure_catalog_path=catalog,seed=seed)

def verify():
    m=json.loads(MANIFEST.read_text()); expected=json.loads(GOLDEN.read_text()); observed=run(42)
    raw_ok=hashlib.sha256(GOLDEN.read_bytes()).hexdigest()==m['golden_output']['sha256']
    payload_ok=canonical_sha(observed)==m['golden_output']['canonical_payload_sha256'] and observed==expected
    print('LOOM CIVPROP QUALIFICATION')
    print('==========================')
    print(f"Baseline: {m['baseline_id']}")
    print(f"Engine: {m['engine']['id']} / {m['engine']['version']}")
    print(f"Runner: {RUNNER_VERSION}")
    print('Seed: 42')
    print(f"Golden file integrity: {'PASS' if raw_ok else 'FAIL'}")
    print(f"Deterministic reproduction: {'PASS' if payload_ok else 'FAIL'}")
    print(f"Reference canonical SHA-256: {m['golden_output']['canonical_payload_sha256']}")
    print(f"Generated canonical SHA-256: {canonical_sha(observed)}")
    print(f"RESULT: {'PASS' if raw_ok and payload_ok else 'FAIL'}")
    return 0 if raw_ok and payload_ok else 1

def main():
    ap=argparse.ArgumentParser(description='Run or independently verify the qualified LOOM CIVPROP baseline.')
    ap.add_argument('--verify',action='store_true',help='Reproduce and verify the frozen GAP-013 seed-42 baseline.')
    ap.add_argument('--seed',type=int,default=42,help='Deterministic propagation seed (default: 42).')
    ap.add_argument('--output',type=Path,help='Output JSON path for a propagation run.')
    args=ap.parse_args()
    if args.verify: return verify()
    if args.output is None: ap.error('--output is required unless --verify is used')
    out=run(args.seed); args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('LOOM CIVPROP PROPAGATION')
    print('========================')
    print(f"Runner: {RUNNER_VERSION}")
    print(f"Seed: {args.seed}")
    years=[int(x['year']) for x in out['annual_states']]
    print(f"Period: {min(years)} -> {max(years)}")
    print(f"Facilities: {len(out['facilities'])}")
    print(f"Lifecycle states: {len(out['asset_lifecycle_states'])}")
    print(f"Lifecycle-adjusted production states: {len(out['lifecycle_production_states'])}")
    print(f"Output: {args.output}")
    print(f"Canonical SHA-256: {canonical_sha(out)}")
    return 0

if __name__=='__main__': raise SystemExit(main())
