"""Deterministic SF-PROMOTE-03 replay and row-order challenge."""
import json, os, sqlite3, tempfile
from pathlib import Path
from promote import build, sha
from sf03_qualify import whole_digest, body_digest
from validate import require_valid
HERE=Path(__file__).resolve().parent
LAB=Path(os.environ['ARP_EUROPA_LAB_ROOT']) if os.environ.get('ARP_EUROPA_LAB_ROOT') else None
def main():
 with tempfile.TemporaryDirectory() as td:
  a=build(Path(td)/'replay_a.sqlite3',LAB);b=build(Path(td)/'replay_b.sqlite3',LAB)
  same_bytes=sha(a)[0]==sha(b)[0]
  src=sqlite3.connect(a);dump=list(src.iterdump());src.close();rev=Path(td)/'reverse_rows.sqlite3';c=sqlite3.connect(rev);c.execute('PRAGMA foreign_keys=OFF')
  ddl=[x for x in dump if not x.startswith('INSERT INTO') and x not in ('BEGIN TRANSACTION;','COMMIT;')]
  rows=[x for x in dump if x.startswith('INSERT INTO')]
  for x in ddl:c.execute(x)
  for x in reversed(rows):c.execute(x)
  c.commit();c.close();require_valid(rev)
  bodies=['COMET_67P','CERES','EUROPA']
  result={'replay_builds_byte_identical':same_bytes,'replay_sha256':sha(a)[0],'row_insertion_order_challenge':'PASS' if all(body_digest(a,x)==body_digest(rev,x) for x in bodies) and whole_digest(a)==whole_digest(rev) else 'FAIL','whole_digest':whole_digest(a),'body_digests':{x:body_digest(a,x) for x in bodies},'alternate_body_insertion_order':'NOT_RUN','alternate_order_limitation':'Baseline Ceres and 67P were not rebuilt or reordered; only generic SQL row insertion order was challenged to preserve their frozen scientific inputs.'}
  if not same_bytes or result['row_insertion_order_challenge']=='FAIL':raise SystemExit('replay failure')
  (HERE/'replay_insertion_order.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
