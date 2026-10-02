#!/usr/bin/env python3
"""Bounded read-only SQLite Ceres and one-hop institution/media evidence extraction."""
import hashlib,json,re,sqlite3,sys,zipfile
from pathlib import Path
from datetime import datetime,timezone
root=Path(sys.argv[1]).expanduser().resolve() if len(sys.argv)>1 else Path.home()/'loom-workspaces/ceres-atlas'
out=Path.home()/'ceres-evidence';out.mkdir(exist_ok=True)
manifest=json.loads((root/'docs/ceres/manifest.json').read_text())
seeds={'CERES'}
for f in manifest:
 for key in ('node_id','noun_id','asset_id','media_key'):
  if f.get(key):seeds.add(str(f[key]).upper())
 for z in f.get('civstate_zones',[]):
  if z.get('zone'):seeds.add(str(z['zone']).upper())
files=list((root/'data').glob('*.sqlite3'))
def pick(kind):
 matches=[p for p in files if ('civstate' in p.name.lower() if kind=='civstate' else 'media' in p.name.lower() if kind=='media' else not any(w in p.name.lower() for w in ('media','civstate')))]
 exact={'world':'LOOM_2226.sqlite3','civstate':'LOOM_2226_CIVSTATE.sqlite3','media':'LOOM_2226_media.sqlite3'}[kind]
 preferred=[p for p in matches if p.name==exact]
 return (preferred[0] if preferred else matches[0] if len(matches)==1 else None),[p.name for p in matches]
def quote(s):return '"'+s.replace('"','""')+'"'
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def safe(v):return {'blob':True,'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()} if isinstance(v,bytes) else v
id_name=re.compile(r'(^id$|_id$|_key$|^uuid$)',re.I)
id_value=re.compile(r'^(?:[A-Z0-9]+[:\-][A-Z0-9:_-]+|[0-9a-f]{8}-[0-9a-f-]{27,})$',re.I)
report={'created_utc':datetime.now(timezone.utc).isoformat(),'scope':'bounded lexical seed + one-hop identifier discovery, NOT complete relational closure','seeds':sorted(seeds),'manifest':manifest,'databases':{},'limitations':[]}
conns={}
for kind in ('world','civstate','media'):
 p,choices=pick(kind)
 if not p:report['databases'][kind]={'error':'missing or ambiguous database','candidates':choices};continue
 con=sqlite3.connect(p.resolve().as_uri()+'?mode=ro',uri=True);con.execute('PRAGMA query_only=ON');conns[kind]=con
 tables={}
 for name,typ,sql in con.execute("SELECT name,type,sql FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY name"):
  cols=[{'name':c[1],'type':c[2],'pk':c[5]} for c in con.execute(f'PRAGMA table_info({quote(name)})')]
  tables[name]={'type':typ,'sql':sql,'columns':cols,'matches':[],'passes':[]}
 report['databases'][kind]={'filename':p.name,'sha256':digest(p),'bytes':p.stat().st_size,'tables':tables}

def scan(terms,label,expand=False):
 found=set()
 for kind,con in conns.items():
  for name,t in report['databases'][kind]['tables'].items():
   cols=[c['name'] for c in t['columns'] if 'BLOB' not in c['type'].upper() and (not c['type'] or any(x in c['type'].upper() for x in ('TEXT','CHAR','CLOB')))]
   if not cols:continue
   # SQL filtering prevents reading every image BLOB into Python.
   where=' OR '.join(f'UPPER(CAST({quote(c)} AS TEXT)) LIKE ?' for c in cols for x in terms)
   params=[f'%{x}%' for c in cols for x in terms]
   try:
    cur=con.execute(f'SELECT * FROM {quote(name)} WHERE {where} LIMIT 3001',params)
    names=[d[0] for d in cur.description];existing={json.dumps(x,sort_keys=True,default=str) for x in t['matches']};n=0
    for row in cur:
     n+=1
     if n>3000:report['limitations'].append(f'{kind}.{name} {label}: more than 3000 matches');break
     obj={k:safe(v) for k,v in zip(names,row)};identity=json.dumps(obj,sort_keys=True,default=str)
     if identity not in existing:t['matches'].append(obj);existing.add(identity)
     if expand:
      for k,v in zip(names,row):
       if id_name.search(k) and isinstance(v,str) and id_value.fullmatch(v) and v.upper() not in seeds:found.add(v.upper())
    t['passes'].append({'phase':label,'hits':n,'limited_to':3000})
   except Exception as e:t['passes'].append({'phase':label,'error':str(e)});report['limitations'].append(f'{kind}.{name}: {e}')
 return found
print('Discovering Ceres and facility rows ...',flush=True)
found=sorted(scan(sorted(seeds),'direct',True)-seeds)
if len(found)>500:report['limitations'].append(f'One-hop identifiers capped: {len(found)} -> 500');found=found[:500]
report['one_hop_identifiers']=found
print(f'Discovering records associated with {len(found)} connected identifiers ...',flush=True)
if found:scan(found,'one_hop')
for c in conns.values():c.close()
summary=[]
for kind,info in report['databases'].items():
 summary.append(f'{kind}: {info.get("filename",info.get("error"))}')
 for name,t in info.get('tables',{}).items():
  if t['matches']:summary.append(f'  {name}: {len(t["matches"])} matching rows')
summary.append('LIMITATIONS / ERRORS: '+str(len(report['limitations'])));summary+=report['limitations']
j=out/'CERES_EVIDENCE_V2.json';j.write_text(json.dumps(report,indent=2,ensure_ascii=False,default=str))
s=out/'SUMMARY_V2.txt';s.write_text('\n'.join(summary)+'\n')
z=out/'CERES_EVIDENCE_V2.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:f.write(j,j.name);f.write(s,s.name)
print('\n'.join(summary));print('UPLOAD:',z,'bytes:',z.stat().st_size)
