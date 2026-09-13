#!/usr/bin/env python3
"""Build the LOOM production database data dictionary.

Reads both production SQLite databases directly and emits exhaustive Markdown +
JSON. Maintained field definitions are merged with CIVSTATE self-documentation.

v0.2 recovery rule: documentation is routed to the table/field it DESCRIBES,
not merely the table in which the prose is stored. The recovery engine ingests:
  * civ_variable_semantics
  * civ_readiness_audit
  * civ_derivation (method/source_detail/notes)
  * civ_methodology_note
  * civ_assumption

No definition is inferred from an identifier. Unrecovered fields remain
DEFINITION_NOT_RECOVERED.
"""
from __future__ import annotations
import argparse, json, re, sqlite3
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_DBS=[ROOT/'data'/'LOOM_2226.sqlite3',ROOT/'data'/'LOOM_2226_CIVSTATE.sqlite3']
DEFAULT_DEFS=ROOT/'docs'/'database_semantics'/'DATA_DICTIONARY_FIELD_DEFINITIONS_v0.1.json'
DEFAULT_MD=ROOT/'docs'/'database_semantics'/'LOOM_DATABASE_DATA_DICTIONARY_v0.2.md'
DEFAULT_JSON=ROOT/'docs'/'database_semantics'/'LOOM_DATABASE_DATA_DICTIONARY_v0.2.json'
DOC_TABLES=('civ_variable_semantics','civ_readiness_audit','civ_derivation','civ_methodology_note','civ_assumption')

def qi(s): return '"'+s.replace('"','""')+'"'
def tables(c): return [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
def cols(c,t): return [dict(cid=r[0],name=r[1],declared_type=r[2] or None,not_null=bool(r[3]),default=r[4],pk_position=int(r[5])) for r in c.execute(f'PRAGMA table_info({qi(t)})')]
def rows_as_dict(c,t):
    names=[r[1] for r in c.execute(f'PRAGMA table_info({qi(t)})')]
    return [dict(zip(names,r)) for r in c.execute(f'SELECT * FROM {qi(t)}')]

def load_defs(p):
    x=json.loads(p.read_text()); exact={}; wild={}
    for r in x.get('fields',[]):
        (wild if r['column']=='*' else exact)[(r['database'],r['table']) if r['column']=='*' else (r['database'],r['table'],r['column'])]=r
    return exact,wild

def schema(c,t):
    cs=cols(c,t); fk={}
    for r in c.execute(f'PRAGMA foreign_key_list({qi(t)})'):
        fk.setdefault(r[3],[]).append(dict(target_table=r[2],from_column=r[3],target_column=r[4],on_update=r[5],on_delete=r[6]))
    ix=[]
    for r in c.execute(f'PRAGMA index_list({qi(t)})'):
        ix.append(dict(name=r[1],unique=bool(r[2]),origin=r[3],columns=[x[2] for x in c.execute(f'PRAGMA index_info({qi(r[1])})')]))
    for x in cs:x['foreign_keys']=fk.get(x['name'],[])
    pk=[x['name'] for x in sorted((x for x in cs if x['pk_position']),key=lambda z:z['pk_position'])]
    return dict(table=t,row_count=c.execute(f'SELECT COUNT(*) FROM {qi(t)}').fetchone()[0],primary_key=pk,indexes=ix,columns=cs)

def text_of(r): return ' '.join(str(v) for v in r.values() if v is not None)
def mentioned(text,name): return re.search(r'(?<![A-Za-z0-9_])'+re.escape(name)+r'(?![A-Za-z0-9_])',text,re.I) is not None

def collect_self_docs(c):
    present=set(tables(c)); evidence=[]
    # exact variable semantics: use actual schema flexibly
    if 'civ_variable_semantics' in present:
        for r in rows_as_dict(c,'civ_variable_semantics'):
            evidence.append(dict(source_table='civ_variable_semantics',source_key=r.get('variable_key'),target_table=r.get('table_name'),target_column=r.get('column_name'),kind='VARIABLE_SEMANTICS',text=text_of(r),payload=r))
    for st,kind,key_candidates in [
        ('civ_readiness_audit','READINESS_AUDIT',('audit_key','audit_id','id')),
        ('civ_derivation','DERIVATION',('derivation_id','id')),
        ('civ_methodology_note','METHODOLOGY',('methodology_id','note_id','id')),
        ('civ_assumption','ASSUMPTION',('assumption_id','id'))]:
        if st not in present: continue
        for r in rows_as_dict(c,st):
            key=next((r.get(k) for k in key_candidates if r.get(k) is not None),None)
            evidence.append(dict(source_table=st,source_key=key,target_table=None,target_column=None,kind=kind,text=text_of(r),payload=r))
    return evidence

def route_evidence(c,evidence):
    ts=tables(c); cmap={t:[x['name'] for x in cols(c,t)] for t in ts}; routed={t:[] for t in ts}; routed_col={(t,x):[] for t in ts for x in cmap[t]}
    for e in evidence:
        if e.get('target_table') in routed:
            routed[e['target_table']].append(e)
            if (e['target_table'],e.get('target_column')) in routed_col:routed_col[(e['target_table'],e['target_column'])].append(e)
            continue
        txt=e['text']
        hits=[t for t in ts if mentioned(txt,t)]
        # If prose names a field uniquely across tables, route it to that field/table too.
        for t in hits:routed[t].append(e)
        for t in hits:
            for col in cmap[t]:
                if mentioned(txt,col): routed_col[(t,col)].append(e)
    return routed,routed_col

def derivation_evidence(c,t):
    names={x['name'] for x in cols(c,t)}
    if 'derivation_id' not in names or 'civ_derivation' not in tables(c):return []
    ids=[r[0] for r in c.execute(f'SELECT DISTINCT derivation_id FROM {qi(t)} WHERE derivation_id IS NOT NULL')]
    if not ids:return []
    ds=rows_as_dict(c,'civ_derivation'); return [dict(source_table='civ_derivation',source_key=d.get('derivation_id'),kind='ROW_DERIVATION',text=text_of(d),payload=d) for d in ds if d.get('derivation_id') in ids]

def attach(db,t,col,exact,wild,col_ev):
    r=exact.get((db,t,col['name'])) or wild.get((db,t)); ev=col_ev.get((t,col['name']),[])
    if r:
        d=dict(definition_status='DEFINED',definition=r.get('definition'),unit=r.get('unit'),data_role=r.get('data_role'),scope=r.get('scope'),epistemic_status=r.get('epistemic_status'),generation=r.get('generation'),join_notes=r.get('join_notes'),misuse_warning=r.get('misuse_warning'))
    else:
        d=dict(definition_status='DEFINITION_NOT_RECOVERED',definition=None,unit=None,data_role=None,scope=None,epistemic_status=None,generation=None,join_notes=None,misuse_warning=None)
    out=dict(col);out.update(d);out['self_documentation_evidence']=[dict(source_table=x['source_table'],source_key=x.get('source_key'),kind=x['kind'],text=x['text']) for x in ev];return out

def status_for(info):
    n=len(info['columns']); defined=sum(x['definition_status']=='DEFINED' for x in info['columns']); has_purpose=bool(info['self_documentation_evidence'] or info['row_derivation_evidence'])
    if n and defined==n and has_purpose:return 'UNDERSTOOD'
    if defined or has_purpose:return 'PARTIALLY_UNDERSTOOD'
    return 'NOT_UNDERSTOOD'

def build(paths,defs):
    exact,wild=load_defs(defs); out=dict(version='0.2',definition_rule='Ingest all five CIVSTATE self-documentation layers and route findings to described tables/fields; never infer definitions from identifiers.',databases=[])
    for p in paths:
        c=sqlite3.connect(f'file:{p}?mode=ro',uri=True); ev=collect_self_docs(c); tev,cev=route_evidence(c,ev); db=dict(database=p.name,tables=[])
        for t in tables(c):
            inf=schema(c,t); inf['self_documentation_evidence']=[dict(source_table=x['source_table'],source_key=x.get('source_key'),kind=x['kind'],text=x['text']) for x in tev[t]]; inf['row_derivation_evidence']=[dict(source_table=x['source_table'],source_key=x.get('source_key'),kind=x['kind'],text=x['text']) for x in derivation_evidence(c,t)]; inf['columns']=[attach(p.name,t,x,exact,wild,cev) for x in inf['columns']]; inf['understanding_status']=status_for(inf); db['tables'].append(inf)
        c.close();out['databases'].append(db)
    return out

def render(doc):
    L=['# LOOM Production Database Data Dictionary v0.2','', 'Generated from production schemas plus routed CIVSTATE self-documentation. Evidence belongs to the table/field it describes, not merely the table where the prose is stored.','']; stats={'UNDERSTOOD':0,'PARTIALLY_UNDERSTOOD':0,'NOT_UNDERSTOOD':0}; nc=nd=0
    for db in doc['databases']:
        L += [f"## `{db['database']}`",'']
        for t in db['tables']:
            stats[t['understanding_status']]+=1; nc+=len(t['columns']); nd+=sum(x['definition_status']=='DEFINED' for x in t['columns'])
            L += [f"### `{t['table']}`",'',f"- Rows: `{t['row_count']}`",f"- Primary key: `{', '.join(t['primary_key']) if t['primary_key'] else 'NONE'}`",f"- Status: **{t['understanding_status']}**",'']
            ev=t['self_documentation_evidence']+t['row_derivation_evidence']
            if ev:
                L += ['**Recovered documentation attached to this table:**','']
                seen=set()
                for e in ev:
                    k=(e['source_table'],e.get('source_key'),e['text'])
                    if k in seen:continue
                    seen.add(k); L.append(f"- `{e['source_table']}` `{e.get('source_key')}`: {e['text']}")
                L.append('')
            L += ['| Column | Type | Definition | Unit | Role | Field evidence |','|---|---|---|---|---|---|']
            for x in t['columns']:
                def esc(v):return str(v).replace('|','\\|').replace('\n',' ')
                fe='; '.join(f"{e['source_table']}:{e.get('source_key')}" for e in x['self_documentation_evidence']) or '—'
                L.append(f"| `{esc(x['name'])}` | `{esc(x['declared_type'] or 'UNTYPED')}` | {esc(x['definition'] or '**DEFINITION_NOT_RECOVERED**')} | {esc(x['unit'] or '—')} | {esc(x['data_role'] or '—')} | {esc(fe)} |")
            L.append('')
    L += ['## Coverage','',f"- Columns: `{nc}`",f"- Explicit field definitions: `{nd}`",f"- `UNDERSTOOD`: `{stats['UNDERSTOOD']}` tables",f"- `PARTIALLY_UNDERSTOOD`: `{stats['PARTIALLY_UNDERSTOOD']}` tables",f"- `NOT_UNDERSTOOD`: `{stats['NOT_UNDERSTOOD']}` tables",'', 'Table status is mechanically derived: UNDERSTOOD requires every field defined plus table-purpose evidence; PARTIAL requires some field definition or routed purpose/derivation evidence.']
    return '\n'.join(L)+'\n'

def main():
    a=argparse.ArgumentParser();a.add_argument('--world',type=Path,default=DEFAULT_DBS[0]);a.add_argument('--civstate',type=Path,default=DEFAULT_DBS[1]);a.add_argument('--definitions',type=Path,default=DEFAULT_DEFS);a.add_argument('--markdown',type=Path,default=DEFAULT_MD);a.add_argument('--json',type=Path,default=DEFAULT_JSON);a.add_argument('--check',action='store_true');x=a.parse_args();doc=build([x.world,x.civstate],x.definitions);md=render(doc);js=json.dumps(doc,indent=2,ensure_ascii=False)+'\n'
    if x.check:
        ok=True
        for p,s in ((x.markdown,md),(x.json,js)):
            if not p.exists() or p.read_text()!=s:print('STALE:',p);ok=False
        return 0 if ok else 1
    x.markdown.write_text(md);x.json.write_text(js);print('wrote',x.markdown);print('wrote',x.json);return 0
if __name__=='__main__':raise SystemExit(main())
