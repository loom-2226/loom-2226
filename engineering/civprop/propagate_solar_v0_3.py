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
from engineering.civprop.compile_inputs_v1 import capture_live_authority
from engineering.civprop.contracts.gap014_scenario_bridge_v1 import inject_demographic_authority
HERE=Path(__file__).resolve().parent
CATALOG=HERE/'contracts/infrastructure_archetypes_v1.json'

def _activate_gap014(bundle_dir: Path, *, database: str):
 capture=capture_live_authority(Path(bundle_dir)/'gap014_authority_capture.json',database=database)
 sp=Path(bundle_dir)/'scenario_v1.json'
 scenario=json.loads(sp.read_text())
 scenario=inject_demographic_authority(scenario=scenario,capture=capture)
 sp.write_text(json.dumps(scenario,indent=2,sort_keys=True)+'\n')
 # Re-seal the experimental bundle after the governed runtime overlay. The
 # original authority label remains non-canon; hashes must describe bytes loaded.
 mp=Path(bundle_dir)/'manifest_v1.json'
 manifest=json.loads(mp.read_text())
 scenario_bytes=sp.read_bytes()
 truth_bytes=(Path(bundle_dir)/manifest['truth_file']).read_bytes()
 manifest['sha256'][manifest['scenario_file']]=hashlib.sha256(scenario_bytes).hexdigest()
 manifest['bundle_sha256']=hashlib.sha256(scenario_bytes+b'\n'+truth_bytes).hexdigest()
 mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 return capture

def run(seed=42, *, trace_decisions=False, database='loom_dev'):
 with tempfile.TemporaryDirectory(prefix='civprop_solar_v03_') as td:
  p=build_bundle_dir(Path(td))
  capture=_activate_gap014(p,database=database)
  b=load_bundle(p)
  if (b.scenario.start_year,b.scenario.end_year)!=(2026,2226): raise ValueError('Solar V0.3 horizon mismatch')
  out=build_output(input_dir=p,infrastructure_catalog_path=CATALOG,seed=seed,trace_decisions=trace_decisions)
  out['solar_v0_3_execution']={
   'classification':'NON_CANON_MACHINERY_TEST',
   'transport_opportunity_surface':'EXPLICIT_AUTHORED_NONLINEAR_GAP016_FRICTION_PLACEHOLDER',
   'transport_gap':'GAP-016_OPEN',
   'gap_014':'OPEN_QUALIFIED_RUNTIME_BOUNDARY',
   'gap_014_runtime':{
     'earth_authority_snapshot_id':capture['earth']['snapshot']['snapshot_id'],
     'earth_authority_years':len(capture['earth']['global_demographic_2026_2226']),
     'migration_demand_status':'NO_AUTHORIZED_MIGRATION_DEMAND',
   },
   'gap_015':'OPEN_UNTOUCHED',
   'spice_consumed':False,
  }
  return out
def canonical_sha(out):
 # Keep json.dumps defaults (including ASCII escaping and float spelling).
 # iterencode avoids a second, whole-output string/bytes allocation.
 digest=hashlib.sha256()
 for chunk in json.JSONEncoder(sort_keys=True,separators=(',',':')).iterencode(out):
  digest.update(chunk.encode('utf-8'))
 return digest.hexdigest()
def write_output(path,out):
 with Path(path).open('w',encoding='utf-8') as stream:
  for chunk in json.JSONEncoder(indent=2,sort_keys=True).iterencode(out):
   stream.write(chunk)
  stream.write('\n')
def ledger_sizes(out):
 """Presentation-only row counts; never insert diagnostics into the payload."""
 return {key:len(value) for key,value in sorted(out.items()) if isinstance(value,list)}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--seed',type=int,default=42); ap.add_argument('--output'); ap.add_argument('--verify',action='store_true'); ap.add_argument('--trace-decisions',action='store_true'); ap.add_argument('--database',default='loom_dev'); a=ap.parse_args()
 t=time.time(); x=run(a.seed,trace_decisions=a.trace_decisions,database=a.database); sha=canonical_sha(x)
 print('CIVPROP SOLAR V0.3 — EXPLICIT GAP-016 PLACEHOLDER')
 print('engine',x.get('engine_id'),x.get('method_reference'))
 print('period',x.get('start_year'),x.get('end_year'))
 print('sha256',sha,'seconds',round(time.time()-t,3))
 if a.output: write_output(a.output,x)
 print('ledger_rows',json.dumps(ledger_sizes(x),sort_keys=True))
 if a.output: print('output_bytes',Path(a.output).stat().st_size)
 if a.verify:
  y=run(a.seed,trace_decisions=a.trace_decisions,database=a.database); sha2=canonical_sha(y); print('deterministic', 'PASS' if sha==sha2 else 'FAIL',sha2)
  if sha!=sha2: raise SystemExit(1)
if __name__=='__main__': main()
