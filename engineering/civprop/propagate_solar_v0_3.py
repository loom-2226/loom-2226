"""Run Solar V0.3 with explicit GAP-016 placeholder transport surface."""
import argparse,hashlib,json
from pathlib import Path
from engineering.civprop.long_run_integration_v0_3 import run_integrated
def canonical_sha(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--seed',type=int,default=42); ap.add_argument('--output'); a=ap.parse_args(); out=run_integrated(a.seed); sha=canonical_sha(out)
 if a.output: Path(a.output).write_text(json.dumps(out,sort_keys=True,separators=(',',':'))+'\n')
 print('CIVPROP SOLAR V0.3 - NON-CANON PROPAGATION TEST'); print('Transport: GAP-016 EXPLICIT PLACEHOLDER = 1.0 dimensionless_test_index'); print('Period:',out['start_year'],'->',out['end_year']); print('SHA256:',sha)
if __name__=='__main__': main()
