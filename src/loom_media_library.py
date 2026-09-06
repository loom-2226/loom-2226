#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote
import argparse, json, os, sqlite3, webbrowser

def ro(p):
    c=sqlite3.connect(Path(p).resolve().as_uri()+"?mode=ro",uri=True); c.row_factory=sqlite3.Row; return c

def load(db,media):
    w,m=ro(db),ro(media)
    try:
        ents={r['entity_id']:dict(r) for r in w.execute('SELECT entity_id,name,entity_class,parent_entity_id FROM entities')}
        mm={r['media_key']:dict(r) for r in m.execute('SELECT media_key,original_byte_length,thumbnail_byte_length FROM media_assets')}
        q='''SELECT a.asset_id,a.asset_role,a.review_status,a.media_key,a.width_px,a.height_px,a.is_current,k.canonical_name,k.noun_class,k.spatial_entity_id FROM image_assets a JOIN knowledge_entities k ON k.noun_id=a.entity_id WHERE a.media_key IS NOT NULL ORDER BY k.canonical_name,a.is_current DESC'''
        out=[]
        for r in w.execute(q):
            d=dict(r); e=ents.get(d['spatial_entity_id']) or {}; p=ents.get(e.get('parent_entity_id')) or {}; z=mm.get(d['media_key']) or {}
            d['name']=e.get('name') or d['canonical_name']; d['class']=e.get('entity_class') or d['noun_class']; d['parent']=p.get('name') or ''; d['thumb']=bool(z.get('thumbnail_byte_length')); d['full']=bool(z.get('original_byte_length')); out.append(d)
        return out
    finally: w.close(); m.close()

def blob(media,key,thumb):
    m=ro(media)
    try:r=m.execute('SELECT mime_type,original_blob,thumbnail_mime_type,thumbnail_blob FROM media_assets WHERE media_key=?',(key,)).fetchone()
    finally:m.close()
    if not r:return None,None
    if thumb and r['thumbnail_blob'] is not None:return r['thumbnail_mime_type'] or r['mime_type'] or 'image/jpeg',bytes(r['thumbnail_blob'])
    if r['original_blob'] is not None:return r['mime_type'] or 'application/octet-stream',bytes(r['original_blob'])
    return None,None

def page(data):
    j=json.dumps(data,separators=(',',':')).replace('</','<\\/')
    return '''<!doctype html><meta name=viewport content="width=device-width,initial-scale=1"><title>LOOM Media</title><style>body{background:#071015;color:#dce8ed;font:14px system-ui;margin:0}header{position:sticky;top:0;background:#071015;padding:14px}input,select{padding:9px;margin:3px;background:#0d1920;color:#dce8ed}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;padding:14px}.card{border:1px solid #24414e;background:#0d1920}.card img{width:100%;height:150px;object-fit:cover}.m{padding:8px}small{color:#78909b}</style><header><b>LOOM 2226 · MEDIA LIBRARY</b><br><input id=q placeholder=Search><select id=c><option value="">All classes</option></select></header><div id=s></div><div class=grid id=o></div><script>const D='''+j+''',q=document.querySelector('#q'),c=document.querySelector('#c'),o=document.querySelector('#o'),s=document.querySelector('#s');[...new Set(D.map(x=>x.class))].sort().forEach(x=>c.innerHTML+='<option>'+x+'</option>');function d(){let t=q.value.toLowerCase(),a=D.filter(x=>(!t||JSON.stringify(x).toLowerCase().includes(t))&&(!c.value||x.class==c.value));s.textContent=a.length+' assets · '+a.filter(x=>x.thumb).length+' thumbnails · '+a.filter(x=>x.is_current).length+' current';o.innerHTML=a.map(x=>'<div class=card><a target=_blank href="/full/'+encodeURIComponent(x.media_key)+'"><img loading=lazy src="/thumb/'+encodeURIComponent(x.media_key)+'"></a><div class=m><b>'+x.name+'</b><br><small>'+x.class+(x.parent?' · '+x.parent:'')+' · '+x.asset_role+(x.is_current?' · CURRENT':' · HISTORICAL')+'<br>'+x.review_status+' · '+(x.width_px||'?')+'×'+(x.height_px||'?')+'</small></div></div>').join('')}q.oninput=c.onchange=d;d()</script>'''

class H(BaseHTTPRequestHandler):
    data=[]; media=None
    def sendb(self,n,m,b):self.send_response(n);self.send_header('Content-Type',m);self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        if self.path in ('/','/index.html'):return self.sendb(200,'text/html; charset=utf-8',page(self.data).encode())
        if self.path.startswith('/thumb/') or self.path.startswith('/full/'):
            thumb=self.path.startswith('/thumb/'); key=unquote(self.path.split('/',2)[2]); m,b=blob(self.media,key,thumb); return self.sendb(200,m,b) if b else self.sendb(404,'text/plain',b'not found')
        self.sendb(404,'text/plain',b'not found')
    def log_message(self,*a):pass

def main():
    p=argparse.ArgumentParser();p.add_argument('--root');p.add_argument('--port',type=int,default=8766);p.add_argument('--no-browser',action='store_true');a=p.parse_args()
    root=Path(a.root or os.environ.get('LOOM_HOME') or ('/storage/emulated/0/Download/LOOM_TEST' if Path('/storage/emulated/0').exists() else Path.home()/'Documents'/'LOOM'))
    db=root/'data'/'LOOM_2226.sqlite3'; media=root/'data'/'LOOM_2226_media.sqlite3'
    for x in (db,media):
        if not x.exists():raise SystemExit(f'LOOM file missing: {x}')
    H.data=load(db,media);H.media=media;print('LOOM MEDIA LIBRARY v1.1');print('ASSETS',len(H.data));url=f'http://127.0.0.1:{a.port}/';print('BROWSER',url)
    s=ThreadingHTTPServer(('127.0.0.1',a.port),H)
    if not a.no_browser:webbrowser.open(url)
    try:s.serve_forever()
    except KeyboardInterrupt:pass
    finally:s.server_close()
if __name__=='__main__':main()
