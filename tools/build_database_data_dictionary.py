#!/usr/bin/env python3
"""Build the LOOM production database data dictionary.

The builder is exhaustive and evidence-tiered. It inventories every table/column,
merges maintained definitions, routes CIVSTATE self-documentation to the object it
describes, and gives every field a concrete storage contract without pretending
that an unrecovered formula is understood.

Recovery statuses:
- RECOVERED_EXACT: explicit preserved semantic/formula contract.
- RECOVERED_STRUCTURAL: key/lookup/metadata meaning proven by schema/value joins.
- RECOVERED_PARTIAL: useful meaning recovered but exact formula/unit is incomplete.
- RECOVERED_STORAGE_ONLY: field is inventoried and its storage role is known, but
  semantic/generating meaning is still open. This is NOT 'understood'.
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
    if 'civ_variable_semantics' in present:
        for r in rows_as_dict(c,'civ_variable_semantics'):
            evidence.append(dict(source_table='civ_variable_semantics',source_key=r.get('variable_key'),target_table=r.get('table_name'),target_column=r.get('column_name'),kind='VARIABLE_SEMANTICS',text=text_of(r),payload=r))
    for st,kind,key_candidates in [
        ('civ_readiness_audit','READINESS_AUDIT',('audit_key','audit_id','id')),
        ('civ_derivation','DERIVATION',('derivation_id','id')),
        ('civ_methodology_note','METHODOLOGY',('method_id','methodology_id','note_id','id')),
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
        txt=e['text']; hits=[t for t in ts if mentioned(txt,t)]
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
    ds=rows_as_dict(c,'civ_derivation')
    return [dict(source_table='civ_derivation',source_key=d.get('derivation_id'),kind='ROW_DERIVATION',text=text_of(d),payload=d) for d in ds if d.get('derivation_id') in ids]

def values(c,t,col):
    return [r[0] for r in c.execute(f'SELECT {qi(col)} FROM {qi(t)} WHERE {qi(col)} IS NOT NULL')]

def structural_definition(c,t,col):
    """Return only storage/key facts we can prove from schema/value domains."""
    n=col['name']; vals=values(c,t,n); present=set(tables(c))
    if n=='year': return dict(definition_status='RECOVERED_STRUCTURAL',definition='Model/reference year for this row.',unit='year',data_role='temporal key',generation='SQLite row structure')
    if n=='derivation_id' and 'civ_derivation' in present:
        known={r.get('derivation_id') for r in rows_as_dict(c,'civ_derivation')}; ok=all(v in known for v in vals)
        if ok:return dict(definition_status='RECOVERED_STRUCTURAL',definition='Derivation/provenance identifier; populated values resolve to civ_derivation.derivation_id.',unit=None,data_role='provenance key',generation='Verified value-domain join')
    if n=='run_id' and 'civ_model_run' in present:
        known={r.get('run_id') for r in rows_as_dict(c,'civ_model_run')}; ok=all(v in known for v in vals)
        if ok:return dict(definition_status='RECOVERED_STRUCTURAL',definition='Model-run identifier; populated values resolve to civ_model_run.run_id.',unit=None,data_role='run/provenance key',generation='Verified value-domain join')
    if n=='sector_id' and 'civ_sector' in present:
        known={r.get('sector_id') for r in rows_as_dict(c,'civ_sector')}; ok=all(v in known for v in vals)
        if ok:return dict(definition_status='RECOVERED_STRUCTURAL',definition='Sector lookup key; populated values resolve to civ_sector.sector_id.',unit=None,data_role='lookup key',generation='Verified value-domain join')
    if n=='asset_class' and 'civ_asset_class' in present:
        known={r.get('asset_class') for r in rows_as_dict(c,'civ_asset_class')}; ok=all(v in known for v in vals)
        if ok:return dict(definition_status='RECOVERED_STRUCTURAL',definition='Asset-class lookup key; populated values resolve to civ_asset_class.asset_class.',unit=None,data_role='lookup key',generation='Verified value-domain join')
    subject_names={'subject_id','node_subject_id','zone_subject_id','actor_subject_id','country_subject_id','institution_subject_id','recognizing_subject_id','issuing_actor_subject_id','predecessor_subject_id','origin_subject_id','destination_subject_id','geography_subject_id','parent_subject_id','spatial_subject_id'}
    if n in subject_names and 'civ_subject' in present:
        known={r.get('subject_id') for r in rows_as_dict(c,'civ_subject')}; ok=all(v in known for v in vals)
        if ok:return dict(definition_status='RECOVERED_STRUCTURAL',definition='CIVSTATE subject identifier; populated values resolve to civ_subject.subject_id.',unit=None,data_role='subject identifier',generation='Verified value-domain join')
    if n in {'display_name','canonical_name'}: return dict(definition_status='RECOVERED_STRUCTURAL',definition='Human-readable name/label stored for the row.',unit=None,data_role='label',generation='SQLite row structure')
    if n in {'sort_order','phase_order'}: return dict(definition_status='RECOVERED_STRUCTURAL',definition='Integer ordering key for the relevant lookup/sequence.',unit=None,data_role='ordering integer',generation='SQLite row structure')
    if n.endswith('_json'): return dict(definition_status='RECOVERED_STRUCTURAL',definition='JSON-encoded structured value for the named row property.',unit=None,data_role='JSON text',generation='SQLite row structure')
    if n.endswith('_at') or n in {'created_at','refreshed_at','updated_at'}: return dict(definition_status='RECOVERED_STRUCTURAL',definition='Timestamp stored for the named row event/update.',unit='timestamp',data_role='timestamp',generation='SQLite row structure')
    if n.startswith('is_') or n.startswith('active_') or n in {'primary_relation','fitted_to_country_targets'}: return dict(definition_status='RECOVERED_STRUCTURAL',definition='Boolean/integer flag for the named row property.',unit='0/1 flag',data_role='flag',generation='SQLite row structure')
    return None

def attach(c,db,t,col,exact,wild,col_ev):
    r=exact.get((db,t,col['name'])) or wild.get((db,t)); ev=col_ev.get((t,col['name']),[])
    if r:
        d=dict(definition_status=r.get('definition_status','RECOVERED_EXACT'),definition=r.get('definition'),unit=r.get('unit'),data_role=r.get('data_role'),scope=r.get('scope'),epistemic_status=r.get('epistemic_status'),generation=r.get('generation'),join_notes=r.get('join_notes'),misuse_warning=r.get('misuse_warning'))
    else:
        d=structural_definition(c,t,col)
        if d is None:
            d=dict(definition_status='RECOVERED_STORAGE_ONLY',definition=f"Stored `{col['name']}` value for the `{t}` row. Exact semantic definition or generating rule is not yet recovered from preserved evidence.",unit=None,data_role='stored field; semantics incomplete',scope=None,epistemic_status=None,generation='SQLite schema/row storage only',join_notes=None,misuse_warning='Do not infer scale, causal meaning, or generating formula from the identifier alone.')
        else:
            d.update(scope=None,epistemic_status=None,join_notes=None,misuse_warning=None)
    out=dict(col);out.update(d);out['self_documentation_evidence']=[dict(source_table=x['source_table'],source_key=x.get('source_key'),kind=x['kind'],text=x['text']) for x in ev];return out

def status_for(info):
    states=[x['definition_status'] for x in info['columns']]
    has_purpose=bool(info['self_documentation_evidence'] or info['row_derivation_evidence'])
    if states and all(s in {'RECOVERED_EXACT','RECOVERED_STRUCTURAL'} for s in states) and has_purpose:return 'UNDERSTOOD'
    if any(s!='RECOVERED_STORAGE_ONLY' for s in states) or has_purpose:return 'PARTIALLY_UNDERSTOOD'
    return 'NOT_UNDERSTOOD'

def build(paths,defs):
    exact,wild=load_defs(defs); out=dict(version='0.2',definition_rule='Every field is inventoried and receives an evidence-tiered storage contract. Storage-only does not count as semantic understanding.',databases=[])
    for p in paths:
        if not p.exists(): raise FileNotFoundError(p)
        c=sqlite3.connect(f'file:{p}?mode=ro',uri=True); ev=collect_self_docs(c); tev,cev=route_evidence(c,ev); db=dict(database=p.name,tables=[])
        for t in tables(c):
            inf=schema(c,t); inf['self_documentation_evidence']=[dict(source_table=x['source_table'],source_key=x.get('source_key'),kind=x['kind'],text=x['text']) for x in tev[t]]; inf['row_derivation_evidence']=[dict(source_table=x['source_table'],source_key=x.get('source_key'),kind=x['kind'],text=x['text']) for x in derivation_evidence(c,t)]; inf['columns']=[attach(c,p.name,t,x,exact,wild,cev) for x in inf['columns']]; inf['understanding_status']=status_for(inf); db['tables'].append(inf)
        c.close();out['databases'].append(db)
    return out

def render(doc):
    L=['# LOOM Production Database Data Dictionary v0.2','', 'Generated from production schemas plus routed self-documentation. Every field is present; recovery status distinguishes exact/structural knowledge from open semantics.','']; stats={'UNDERSTOOD':0,'PARTIALLY_UNDERSTOOD':0,'NOT_UNDERSTOOD':0}; rc={}; nc=0
    for db in doc['databases']:
        L += [f"## `{db['database']}`",'']
        for t in db['tables']:
            stats[t['understanding_status']]+=1; nc+=len(t['columns'])
            L += [f"### `{t['table']}`",'',f"- Rows: `{t['row_count']}`",f"- Primary key: `{', '.join(t['primary_key']) if t['primary_key'] else 'NONE'}`",f"- Status: **{t['understanding_status']}**",'']
            ev=t['self_documentation_evidence']+t['row_derivation_evidence']
            if ev:
                L += ['**Recovered documentation attached to this table:**','']; seen=set()
                for e in ev:
                    k=(e['source_table'],e.get('source_key'),e['text'])
                    if k in seen:continue
                    seen.add(k); L.append(f"- `{e['source_table']}` `{e.get('source_key')}`: {e['text']}")
                L.append('')
            L += ['| Column | Type | Recovery | Definition | Unit | Role | Evidence |','|---|---|---|---|---|---|---|']
            for x in t['columns']:
                rc[x['definition_status']]=rc.get(x['definition_status'],0)+1
                def esc(v):return str(v).replace('|','\\|').replace('\n',' ')
                fe='; '.join(f"{e['source_table']}:{e.get('source_key')}" for e in x['self_documentation_evidence']) or x.get('generation') or '—'
                L.append(f"| `{esc(x['name'])}` | `{esc(x['declared_type'] or 'UNTYPED')}` | `{esc(x['definition_status'])}` | {esc(x['definition'])} | {esc(x['unit'] or '—')} | {esc(x['data_role'] or '—')} | {esc(fe)} |")
            L.append('')
    L += ['## Coverage','',f"- Columns: `{nc}`"]+[f"- `{k}`: `{v}`" for k,v in sorted(rc.items())]+[f"- `UNDERSTOOD`: `{stats['UNDERSTOOD']}` tables",f"- `PARTIALLY_UNDERSTOOD`: `{stats['PARTIALLY_UNDERSTOOD']}` tables",f"- `NOT_UNDERSTOOD`: `{stats['NOT_UNDERSTOOD']}` tables",'', 'A field with RECOVERED_STORAGE_ONLY is documented but still semantically open; it never upgrades a table to UNDERSTOOD.']
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
