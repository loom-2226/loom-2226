#!/usr/bin/env python3
"""Read-only structural discovery; not a semantic or publication audit.

Run from repository root: python tools/audit_ceres_inspector_sources.py
Read data/AGENTS.md and all four mandatory semantic documents before interpreting.
"""
import hashlib
import json
import sqlite3
from pathlib import Path

IDS = ('CER-P01', 'CER-P02', 'CER-P03', 'CER-P04', 'CER-P05')
KEYS = {'entity_id', 'spatial_entity_id', 'parent_entity_id', 'noun_id', 'knowledge_entity_id', 'subject_entity_id', 'object_entity_id', 'source_entity_id', 'target_entity_id'}


def quote(s):
    return '"' + s.replace('"', '""') + '"'


def audit(path):
    path = Path(path).resolve()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    db = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    result = {'sha256': digest, 'size_bytes': path.stat().st_size, 'tables': []}
    try:
        for record in db.execute("SELECT name,type FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY name"):
            name = record['name']
            cols = [dict(c) for c in db.execute('PRAGMA table_info(' + quote(name) + ')')]
            keys = [c['name'] for c in cols if c['name'].lower() in KEYS or c['name'].lower().endswith('_entity_id')]
            matches = []
            for key in keys:
                sql = 'SELECT ' + quote(key) + ' AS id, COUNT(*) AS n FROM ' + quote(name) + ' WHERE ' + quote(key) + ' IN (' + ','.join('?' for _ in IDS) + ') GROUP BY ' + quote(key)
                for row in db.execute(sql, IDS):
                    matches.append({'column': key, 'id': row['id'], 'row_count': row['n']})
            result['tables'].append({'table': name, 'type': record['type'], 'columns': cols, 'identifier_columns': keys, 'exact_matches': matches})
    finally:
        db.close()
    return result


def main():
    report = {'status': 'STRUCTURAL_ONLY_SEMANTICS_UNRESOLVED', 'scope': 'Ceres facilities: candidate IDs only; Ceres body ID not yet verified', 'warning': 'Exact matches do not establish semantic association; no match does not prove absence. Do not publish this inventory as Inspector data.', 'world': audit('data/LOOM_2226.sqlite3'), 'civstate': audit('data/LOOM_2226_CIVSTATE.sqlite3')}
    output = Path('ceres_inspector_structural_audit.json')
    output.write_text(json.dumps(report, indent=2, default=str) + '\n', encoding='utf-8')
    for db in ('world', 'civstate'):
        print(db, 'tables', len(report[db]['tables']), 'tables_with_candidate_ID_matches', sum(bool(t['exact_matches']) for t in report[db]['tables']), 'sha256', report[db]['sha256'])
    print('Output:', output)


if __name__ == '__main__':
    main()
