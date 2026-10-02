"""Executable full-Solar CIVPROP V0.3 propagation machinery test.

Uses the real HYBRID_V1 / method-reference-v9 engine with the Solar V0.3 bundle.
GAP-016 transport is an explicit non-physical scalar placeholder. GAP-014/015 stay OPEN.
"""
from __future__ import annotations
import argparse,hashlib,json,tempfile,time
from pathlib import Path
from engineering.civprop.solar_bundle_v0_3 import build_bundle_dir
from engineering.civprop.method_lab.contracts import load_bundle
from engineering.civprop.run_civprop_v1 import build_output
HERE=Path(__file__).resolve().parent
CATALOG=HERE/'contracts/infrastructure_archetypes_v1.json'

def run(seed=42):
 with tempfile.TemporaryDirectory(prefix='civprop_solar_v03_') as td:
  p=build_bundle_dir(Path(td))
  b=load_bundle(p)
  if (b.scenario.start_year,b.scenario.end_year)!=(2026,2226): raise ValueError('Solar V0.3 horizon mismatch')
  out=build_output(input_dir=p,infrastructure_catalog_path=CATALOG,seed=seed)
  out['solar_v0_3_execution']={
   'classification':'NON_CANON_MACHINERY_TEST',
   'transport_opportunity_surface':'EXPLICIT_AUTHORED_NONLINEAR_GAP016_FRICTION_PLACEHOLDER',
   'transport_gap':'GAP-016_OPEN',
   'gap_014':'OPEN_UNTOUCHED','gap_015':'OPEN_UNTOUCHED',
   'spice_consumed':False,
  }
  return out
def canonical_sha(out):
 return hashlib.sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--seed',type=int,default=42); ap.add_argument('--output'); ap.add_argument('--verify',action='store_true'); a=ap.parse_args()
 t=time.time(); x=run(a.seed); sha=canonical_sha(x)
 print('CIVPROP SOLAR V0.3 — EXPLICIT GAP-016 PLACEHOLDER')
 print('engine',x.get('engine_id'),x.get('method_reference'))
 print('period',x.get('start_year'),x.get('end_year'))
 print('sha256',sha,'seconds',round(time.time()-t,3))
 if a.output: Path(a.output).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
 if a.verify:
  y=run(a.seed); sha2=canonical_sha(y); print('deterministic', 'PASS' if sha==sha2 else 'FAIL',sha2)
  if sha!=sha2: raise SystemExit(1)
if __name__=='__main__': main()
