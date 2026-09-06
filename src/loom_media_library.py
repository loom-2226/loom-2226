#!/usr/bin/env python3
"""LOOM 2226 Media + Canon Browser v1.2. Read-only SQL inspection surface."""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlparse
import argparse, html, json, mimetypes, os, re, sqlite3, webbrowser

APP_VERSION='1.2'
BODY_CLASSES={'STAR','PLANET','DWARF_PLANET','MOON','ASTEROID','COMET','PLANETOID','NATURAL_SATELLITE'}

def ro(p):
    c=sqlite3.connect(Path(p).resolve().as_uri()+'?mode=ro',uri=True,timeout=5); c.row_factory=sqlite3.Row; return c

def resolve_root(explicit=None):
    if explicit:return Path(explicit).expanduser().resolve()
    if os.environ.get('LOOM_HOME'):return Path(os.environ['LOOM_HOME']).expanduser().resolve()
    return Path(__file__).resolve().parent.parent

def entities(world):
    return {r['entity_id']:dict(r) for r in world.execute('SELECT entity_id,name,entity_class,parent_entity_id FROM entities')}

def ancestry(eid,ents):
    out=[]; seen=set(); cur=eid
    while cur and cur not in seen and cur in ents:
        seen.add(cur); e=ents[cur]; out.append(e); cur=e.get('parent_entity_id')
    return out

def celestial_for(eid,ents):
    chain=ancestry(eid,ents)
    for e in chain:
        if (e.get('entity_class') or '').upper() in BODY_CLASSES:return e
    return chain[-1] if chain else {}

def load_catalog(world_path,media_path):
    w,m=ro(world_path),ro(media_path)
    try:
        es=entities(w); mm={r['media_key']:dict(r) for r in m.execute('SELECT media_key,original_byte_length,thumbnail_byte_length FROM media_assets')}
        q='''SELECT a.asset_id,a.entity_id AS knowledge_entity_id,a.asset_role,a.review_status,a.media_key,a.width_px,a.height_px,a.is_current,k.canonical_name,k.noun_class,k.spatial_entity_id FROM image_assets a JOIN knowledge_entities k ON k.noun_id=a.entity_id WHERE a.media_key IS NOT NULL ORDER BY k.canonical_name,a.is_current DESC'''
        out=[]
        for r in w.execute(q):
            d=dict(r); e=es.get(d['spatial_entity_id']) or {}; p=es.get(e.get('parent_entity_id')) or {}; z=mm.get(d['media_key']) or {}; cel=celestial_for(d['spatial_entity_id'],es)
            d.update(name=e.get('name') or d['canonical_name'],object_type=e.get('entity_class') or d['noun_class'],parent=p.get('name') or '',celestial_object=cel.get('name') or '',celestial_id=cel.get('entity_id') or '',thumb=bool(z.get('thumbnail_byte_length')),full=bool(z.get('original_byte_length')))
            out.append(d)
        return out
    finally:w.close();m.close()

def blob(media,key,thumb=True):
    m=ro(media)
    try:r=m.execute('SELECT mime_type,original_blob,thumbnail_mime_type,thumbnail_blob FROM media_assets WHERE media_key=?',(key,)).fetchone()
    finally:m.close()
    if not r:return None,None
    if thumb and r['thumbnail_blob'] is not None:return r['thumbnail_mime_type'] or r['mime_type'] or 'image/jpeg',bytes(r['thumbnail_blob'])
    if r['original_blob'] is not None:return r['mime_type'] or 'application/octet-stream',bytes(r['original_blob'])
    return None,None

def esc(x):return html.escape('' if x is None else str(x))
def qident(x):return '"'+str(x).replace('"','""')+'"'
def printable(v):
    if isinstance(v,(bytes,bytearray,memoryview)):return f'<BLOB {len(v):,} bytes>'
    s='' if v is None else str(v); return s if len(s)<=4000 else s[:4000]+f' … <{len(s)-4000:,} chars omitted>'

def related_rows(db_path, ids):
    """Schema-driven direct reference scan. Exact values only; no fuzzy text matching."""
    c=ro(db_path); found=[]; ids={str(x) for x in ids if x}
    try:
        tables=[r['name'] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        for t in tables:
            cols=[r['name'] for r in c.execute('PRAGMA table_info('+qident(t)+')')]
            candidates=[x for x in cols if x.lower() in {'entity_id','spatial_entity_id','parent_entity_id','noun_id','knowledge_entity_id','subject_entity_id','object_entity_id','source_entity_id','target_entity_id'} or x.lower().endswith('_entity_id')]
            if not candidates:continue
            where=[]; params=[]
            for col in candidates:
                where.append(qident(col)+' IN ('+','.join('?'*len(ids))+')'); params.extend(sorted(ids))
            if not where:continue
            rows=c.execute('SELECT * FROM '+qident(t)+' WHERE '+' OR '.join(where)+' LIMIT 500',params).fetchall()
            if rows:found.append((t,[dict(r) for r in rows]))
        return found
    finally:c.close()

def inspector(world_path, dbs, entity_id):
    w=ro(world_path)
    try:
        es=entities(w); e=es.get(entity_id)
        if not e:return '<h1>Unknown entity</h1>'
        chain=ancestry(entity_id,es); ids={entity_id}
        kes=w.execute('SELECT * FROM knowledge_entities WHERE spatial_entity_id=?',(entity_id,)).fetchall()
        ids.update(str(r['noun_id']) for r in kes)
    finally:w.close()
    crumb=' → '.join(f'<a href="/inspect/{quote(x["entity_id"])}">{esc(x["name"])}</a>' for x in reversed(chain))
    sections=[]
    for label,path in dbs:
        if not path.exists():continue
        groups=related_rows(path,ids)
        if not groups:continue
        body=[]
        for table,rows in groups:
            cards=[]
            for row in rows:
                cards.append('<table>'+''.join(f'<tr><th>{esc(k)}</th><td>{esc(printable(v))}</td></tr>' for k,v in row.items())+'</table>')
            body.append(f'<details open><summary>{esc(table)} · {len(rows)} row(s)</summary>'+''.join(cards)+'</details>')
        sections.append(f'<section><h2>{esc(label)}</h2>'+''.join(body)+'</section>')
    return f'''<!doctype html><meta name=viewport content="width=device-width,initial-scale=1"><style>{CSS}table{{width:100%;border-collapse:collapse;margin:8px 0 18px}}th,td{{border-bottom:1px solid #24414e;padding:6px;text-align:left;vertical-align:top;word-break:break-word}}th{{width:30%;color:#82c7d9}}details{{margin:10px 0}}summary{{font-weight:700}}</style><header><a href="/">← Media</a><h1>{esc(e['name'])}</h1><div>{crumb}</div><small>{esc(e['entity_class'])} · {esc(entity_id)}</small></header><main>{''.join(sections) or '<p>No direct entity-keyed rows found.</p>'}</main>'''

CSS='''*{box-sizing:border-box}body{background:#071015;color:#dce8ed;font:14px system-ui;margin:0}header{position:sticky;top:0;z-index:3;background:#071015ee;padding:14px;border-bottom:1px solid #24414e}h1{font-size:20px}h2{color:#82c7d9}a{color:#9dd7e5;text-decoration:none}input,select,button{padding:9px;margin:3px;background:#0d1920;color:#dce8ed;border:1px solid #355463}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px;padding:14px}.card{border:1px solid #24414e;background:#0d1920}.card img{width:100%;height:150px;object-fit:cover}.m{padding:8px}small{color:#78909b}.inspect{display:inline-block;margin-top:8px;padding:6px 8px;border:1px solid #355463;border-radius:4px}main{padding:14px}'''

def page(data):
    j=json.dumps(data,separators=(',',':'),ensure_ascii=False).replace('</','<\\/')
    return f'''<!doctype html><meta name=viewport content="width=device-width,initial-scale=1"><title>LOOM Media</title><style>{CSS}</style><header><b>LOOM 2226 · MEDIA + CANON BROWSER</b><br><input id=q placeholder=Search><select id=cel><option value="">All celestial objects</option></select><select id=typ><option value="">All object types</option></select><select id=role><option value="">All media roles</option></select></header><div id=s style="padding:14px 14px 0"></div><div class=grid id=o></div><script>const D={j},q=document.querySelector('#q'),cel=document.querySelector('#cel'),typ=document.querySelector('#typ'),role=document.querySelector('#role'),o=document.querySelector('#o'),s=document.querySelector('#s');const E=x=>String(x??'').replace(/[&<>\"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));function fill(el,k){{[...new Set(D.map(x=>x[k]).filter(Boolean))].sort().forEach(x=>el.innerHTML+='<option>'+E(x)+'</option>')}}fill(cel,'celestial_object');fill(typ,'object_type');fill(role,'asset_role');function d(){{let t=q.value.toLowerCase(),a=D.filter(x=>(!t||JSON.stringify(x).toLowerCase().includes(t))&&(!cel.value||x.celestial_object==cel.value)&&(!typ.value||x.object_type==typ.value)&&(!role.value||x.asset_role==role.value));s.textContent=a.length+' assets · '+a.filter(x=>x.thumb).length+' thumbnails · '+a.filter(x=>x.is_current).length+' current';o.innerHTML=a.map(x=>'<div class=card><a target=_blank href="/full/'+encodeURIComponent(x.media_key)+'"><img loading=lazy src="/thumb/'+encodeURIComponent(x.media_key)+'"></a><div class=m><b>'+E(x.name)+'</b><br><small>'+E(x.object_type)+(x.celestial_object?' · '+E(x.celestial_object):'')+' · '+E(x.asset_role)+(x.is_current?' · CURRENT':' · HISTORICAL')+'<br>'+E(x.review_status)+' · '+E(x.width_px||'?')+'×'+E(x.height_px||'?')+'</small><br><a class=inspect href="/inspect/'+encodeURIComponent(x.spatial_entity_id)+'">Inspect authoritative SQL</a></div></div>').join('')}}q.oninput=cel.onchange=typ.onchange=role.onchange=d;d()</script>'''

def safe_name(s):return (re.sub(r'[^A-Za-z0-9._-]+','_',str(s)).strip('_')[:120] or 'media')
def ext_for(m):return {'image/jpeg':'.jpg','image/png':'.png','image/webp':'.webp'}.get(m,mimetypes.guess_extension(m or '') or '.bin')
def export_snapshot(catalog,media_path,out_dir):
    out=Path(out_dir); td=out/'thumbs'; td.mkdir(parents=True,exist_ok=True); exported=[]
    for x in catalog:
        y=dict(x); mime,b=blob(media_path,x['media_key'],True)
        if b:
            fn=safe_name(x['asset_id'])+ext_for(mime); (td/fn).write_bytes(b); y['snapshot_thumb']='thumbs/'+fn
        exported.append(y)
    (out/'catalog.json').write_text(json.dumps(exported,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (out/'README.md').write_text('# LOOM derived media snapshot\n\nDerived inspection surface. SQLite remains authoritative.\n',encoding='utf-8')
    print('SNAPSHOT',out,'ASSETS',len(exported))

class H(BaseHTTPRequestHandler):
    data=[]; media=None; world=None; dbs=[]
    def sendb(self,n,m,b):self.send_response(n);self.send_header('Content-Type',m);self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        p=urlparse(self.path).path
        if p in ('/','/index.html'):return self.sendb(200,'text/html; charset=utf-8',page(self.data).encode())
        if p.startswith('/inspect/'):
            eid=unquote(p.split('/',2)[2]); return self.sendb(200,'text/html; charset=utf-8',inspector(self.world,self.dbs,eid).encode())
        if p.startswith('/thumb/') or p.startswith('/full/'):
            thumb=p.startswith('/thumb/'); key=unquote(p.split('/',2)[2]); m,b=blob(self.media,key,thumb); return self.sendb(200,m,b) if b else self.sendb(404,'text/plain',b'not found')
        self.sendb(404,'text/plain',b'not found')
    def log_message(self,*a):pass

def main():
    p=argparse.ArgumentParser();p.add_argument('--root');p.add_argument('--port',type=int,default=8767);p.add_argument('--no-browser',action='store_true');p.add_argument('--export');a=p.parse_args()
    root=resolve_root(a.root); data=root/'data'; world=data/'LOOM_2226.sqlite3'; media=data/'LOOM_2226_media.sqlite3'; civ=data/'LOOM_2226_CIVSTATE.sqlite3'
    for x in (world,media):
        if not x.exists():raise SystemExit(f'LOOM file missing: {x}')
    catalog=load_catalog(world,media)
    if a.export:return export_snapshot(catalog,media,a.export)
    H.data=catalog;H.media=media;H.world=world;H.dbs=[('WORLD · LOOM_2226.sqlite3',world),('CIVSTATE · LOOM_2226_CIVSTATE.sqlite3',civ)]
    print('LOOM MEDIA + CANON BROWSER v'+APP_VERSION);print('ROOT',root);print('ASSETS',len(catalog));url=f'http://127.0.0.1:{a.port}/';print('BROWSER',url)
    s=ThreadingHTTPServer(('127.0.0.1',a.port),H)
    if not a.no_browser:webbrowser.open(url)
    try:s.serve_forever()
    except KeyboardInterrupt:pass
    finally:s.server_close()
if __name__=='__main__':main()
