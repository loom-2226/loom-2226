"""Deterministic replay and insertion-order semantic comparison."""
import hashlib, json, sqlite3, tempfile
from pathlib import Path
from promote import OUT, build
from qualify import body_digest

def reverse_insert(source, target):
    src = sqlite3.connect(source); dst = sqlite3.connect(target); dst.execute('pragma foreign_keys=off')
    lines = list(src.iterdump()); src.close()
    ddl = [x for x in lines if not x.startswith('INSERT INTO') and x not in ('BEGIN TRANSACTION;','COMMIT;')]
    inserts = [x for x in lines if x.startswith('INSERT INTO')]
    for line in ddl: dst.execute(line)
    for line in reversed(inserts): dst.execute(line)
    dst.commit(); dst.close()

def main():
    with tempfile.TemporaryDirectory() as td:
        a = build(Path(td)/'a.sqlite3'); b = build(Path(td)/'b.sqlite3'); reverse_insert(a, Path(td)/'reverse.sqlite3')
        assert hashlib.sha256(a.read_bytes()).hexdigest() == hashlib.sha256(b.read_bytes()).hexdigest()
        for body in ('COMET_67P','CERES'):
            assert body_digest(a,body) == body_digest(b,body) == body_digest(Path(td)/'reverse.sqlite3',body)
        result={'deterministic_replay':True,'insertion_order_semantic_equivalence':True,'byte_identity_for_same_replay':True,'reverse_database_is_semantically_equivalent':True}
        (OUT.parent/'replay_insertion_order.json').write_text(json.dumps(result,indent=2)+'\n'); print(result)

if __name__ == '__main__': main()
