#!/usr/bin/env python3
"""LOOM 2226 media library browser + derived snapshot exporter.

Read-only against WORLD and MEDIA SQLite. Provides:
  1. local searchable browser grouped by celestial object / entity class;
  2. direct thumbnail/full-image viewing from MEDIA BLOBs;
  3. GitHub-friendly derived snapshot export (thumbnails + catalog.json + index.html).

The MEDIA SQLite remains authoritative. Exported catalog material is derived and
may be regenerated at any time.
"""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse
import argparse
import hashlib
import html
import json
import mimetypes
import os
import re
import sqlite3
import webbrowser

APP_VERSION = "1.0"
ANDROID_ROOT = Path("/storage/emulated/0/Download/LOOM_TEST")
WINDOWS_ROOT = Path.home() / "Documents" / "LOOM"


def loom_root(explicit=None):
    if explicit:
        return Path(explicit).expanduser().resolve()
    env = os.environ.get("LOOM_HOME", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    if ANDROID_ROOT.exists():
        return ANDROID_ROOT
    return WINDOWS_ROOT


def connect_ro(path):
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    c = sqlite3.connect(uri, uri=True, timeout=5.0)
    c.row_factory = sqlite3.Row
    return c


def require_schema(world, media):
    wt = {r[0] for r in world.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    mt = {r[0] for r in media.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    needed_w = {"entities", "knowledge_entities", "image_assets"}
    if not needed_w <= wt:
        raise RuntimeError("WORLD database missing tables: " + ", ".join(sorted(needed_w - wt)))
    if "media_assets" not in mt:
        raise RuntimeError("MEDIA database missing media_assets")


def load_catalog(world_path, media_path):
    w = connect_ro(world_path); m = connect_ro(media_path)
    try:
        require_schema(w, m)
        entities = {r["entity_id"]: dict(r) for r in w.execute(
            "SELECT entity_id,name,entity_class,parent_entity_id FROM entities"
        )}
        rows = w.execute("""
            SELECT a.asset_id,a.entity_id,a.asset_role,a.prompt_version,a.provider,a.model_id,
                   a.generation_status,a.review_status,a.media_key,a.mime_type,a.width_px,a.height_px,
                   a.content_hash,a.byte_length,a.thumbnail_hash,a.thumbnail_byte_length,a.created_at,
                   a.updated_at,a.is_current,k.canonical_name,k.noun_class,k.spatial_entity_id,
                   k.quick_description
            FROM image_assets a
            JOIN knowledge_entities k ON k.noun_id=a.entity_id
            WHERE a.media_key IS NOT NULL
            ORDER BY k.canonical_name,a.is_current DESC,a.asset_role,a.created_at DESC
        """).fetchall()
        media_meta = {r["media_key"]: dict(r) for r in m.execute(
            "SELECT media_key,mime_type,original_byte_length,thumbnail_mime_type,thumbnail_byte_length FROM media_assets"
        )}
        out=[]
        for r in rows:
            d=dict(r); sid=d.get("spatial_entity_id"); e=entities.get(sid) or {}
            d["display_name"] = e.get("name") or d.get("canonical_name") or d.get("entity_id")
            d["entity_class"] = e.get("entity_class") or d.get("noun_class") or "OTHER"
            d["parent_entity_id"] = e.get("parent_entity_id")
            p=entities.get(d["parent_entity_id"]) or {}
            d["parent_name"] = p.get("name")
            mm=media_meta.get(d["media_key"],{})
            d["media_present"] = bool(mm)
            d["original_present"] = bool(mm.get("original_byte_length"))
            d["thumbnail_present"] = bool(mm.get("thumbnail_byte_length"))
            d["thumbnail_mime_type"] = mm.get("thumbnail_mime_type")
            d["media_mime_type"] = mm.get("mime_type") or d.get("mime_type")
            d["group"] = group_label(d,e,p)
            out.append(d)
        return out
    finally:
        w.close(); m.close()


def group_label(d,e,p):
    cls=(d.get("entity_class") or "OTHER").upper()
    if cls in {"PLANET","DWARF_PLANET","STAR","MOON","ASTEROID","COMET"}:
        return cls.replace("_"," ")
    if p.get("name"):
        return f"{p['name']} · {cls.replace('_',' ')}"
    return cls.replace("_"," ")


def safe_name(s):
    s=re.sub(r"[^A-Za-z0-9._-]+","_",str(s)).strip("_")
    return s[:120] or "media"


def ext_for(mime):
    return {"image/jpeg":".jpg","image/png":".png","image/webp":".webp","image/gif":".gif"}.get(mime or "", mimetypes.guess_extension(mime or "") or ".bin")


def fetch_blob(media_path, media_key, thumb=True):
    m=connect_ro(media_path)
    try:
        r=m.execute("SELECT mime_type,original_blob,thumbnail_mime_type,thumbnail_blob FROM media_assets WHERE media_key=?",(media_key,)).fetchone()
        if not r: return None,None
        if thumb and r["thumbnail_blob"] is not None:
            return r["thumbnail_mime_type"] or r["mime_type"] or "image/jpeg", bytes(r["thumbnail_blob"])
        if r["original_blob"] is not None:
            return r["mime_type"] or "application/octet-stream", bytes(r["original_blob"])
        return None,None
    finally: m.close()


def browser_html(catalog, static=False):
    data=json.dumps(catalog,separators=(",",":"),ensure_ascii=False).replace("</","<\\/")
    img_expr = "x.snapshot_thumb" if static else "('/thumb/'+encodeURIComponent(x.media_key))"
    full_expr = "x.snapshot_full||x.snapshot_thumb" if static else "('/full/'+encodeURIComponent(x.media_key))"
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LOOM 2226 Media Library</title><style>
:root{{--bg:#071015;--panel:#0d1920;--line:#24414e;--text:#dce8ed;--muted:#78909b;--accent:#82c7d9}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:14px system-ui,sans-serif}}header{{position:sticky;top:0;z-index:3;background:#071015ee;border-bottom:1px solid var(--line);padding:14px}}h1{{font-size:18px;margin:0 0 10px;letter-spacing:.08em}}.bar{{display:flex;gap:8px;flex-wrap:wrap}}input,select{{background:#0b171d;color:var(--text);border:1px solid var(--line);border-radius:5px;padding:9px}}input{{flex:1;min-width:180px}}main{{padding:14px}}.stats{{color:var(--muted);margin:4px 0 14px}}h2{{font-size:14px;color:var(--accent);border-bottom:1px solid var(--line);padding:12px 0 7px;margin:18px 0 10px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px}}.card{{background:var(--panel);border:1px solid var(--line);border-radius:7px;overflow:hidden}}.card img{{width:100%;height:150px;object-fit:cover;background:#020608;display:block}}.meta{{padding:9px}}.name{{font-weight:700}}.sub{{color:var(--muted);font-size:12px;margin-top:3px;word-break:break-word}}.bad{{color:#d6a37c}}a{{color:inherit;text-decoration:none}}</style></head><body>
<header><h1>LOOM 2226 · MEDIA LIBRARY</h1><div class="bar"><input id="q" placeholder="Search object, class, role, status…"><select id="cls"><option value="">All classes</option></select><select id="role"><option value="">All roles</option></select></div></header><main><div class="stats" id="stats"></div><div id="out"></div></main>
<script>const DATA={data};const q=document.querySelector('#q'),cs=document.querySelector('#cls'),rs=document.querySelector('#role'),out=document.querySelector('#out'),stats=document.querySelector('#stats');
const esc=s=>String(s??'').replace(/[&<>\"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));
[...new Set(DATA.map(x=>x.entity_class))].sort().forEach(v=>cs.insertAdjacentHTML('beforeend','<option>'+esc(v)+'</option>'));[...new Set(DATA.map(x=>x.asset_role))].sort().forEach(v=>rs.insertAdjacentHTML('beforeend','<option>'+esc(v)+'</option>'));
function draw(){{let s=q.value.toLowerCase(),a=DATA.filter(x=>(!s||JSON.stringify(x).toLowerCase().includes(s))&&(!cs.value||x.entity_class===cs.value)&&(!rs.value||x.asset_role===rs.value));stats.textContent=a.length+' assets · '+a.filter(x=>x.thumbnail_present).length+' thumbnails · '+a.filter(x=>x.is_current).length+' current';let groups={{}};a.forEach(x=>(groups[x.group]??=[]).push(x));out.innerHTML=Object.keys(groups).sort().map(g=>'<h2>'+esc(g)+' · '+groups[g].length+'</h2><div class="grid">'+groups[g].map(x=>{{let im={img_expr},fu={full_expr};return '<div class="card"><a href="'+fu+'" target="_blank"><img loading="lazy" src="'+im+'"></a><div class="meta"><div class="name">'+esc(x.display_name)+'</div><div class="sub">'+esc(x.entity_class)+' · '+esc(x.asset_role)+(x.is_current?' · CURRENT':' · HISTORICAL')+'</div><div class="sub">'+esc(x.review_status)+' · '+esc(x.width_px||'?')+'×'+esc(x.height_px||'?')+'</div><div class="sub '+(x.thumbnail_present?'':'bad')+'">'+esc(x.media_key)+'</div></div></div>'}}).join('')+'</div>').join('')}}q.oninput=cs.onchange=rs.onchange=draw;draw();</script></body></html>'''


def export_snapshot(world_path, media_path, out_dir, include_full=False, current_only=False):
    catalog=load_catalog(world_path,media_path)
    if current_only: catalog=[x for x in catalog if x["is_current"]]
    out_dir=Path(out_dir); thumbs=out_dir/"thumbs"; full=out_dir/"full"
    thumbs.mkdir(parents=True,exist_ok=True)
    if include_full: full.mkdir(parents=True,exist_ok=True)
    exported=[]
    for i,x in enumerate(catalog,1):
        key=x["media_key"]; mime,blob=fetch_blob(media_path,key,True)
        if blob:
            fn=f"{safe_name(x['display_name'])}__{safe_name(x['asset_role'])}__{hashlib.sha1(key.encode()).hexdigest()[:10]}{ext_for(mime)}"
            (thumbs/fn).write_bytes(blob); x["snapshot_thumb"]="thumbs/"+fn
        else: x["snapshot_thumb"]=""
        if include_full:
            fm,fb=fetch_blob(media_path,key,False)
            if fb:
                fn=f"{safe_name(x['display_name'])}__{safe_name(x['asset_role'])}__{hashlib.sha1(key.encode()).hexdigest()[:10]}{ext_for(fm)}"
                (full/fn).write_bytes(fb); x["snapshot_full"]="full/"+fn
        exported.append(x)
        if i%50==0: print(f"EXPORTED        {i}/{len(catalog)}")
    (out_dir/"catalog.json").write_text(json.dumps(exported,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out_dir/"index.html").write_text(browser_html(exported,True),encoding="utf-8")
    readme=("# LOOM 2226 Derived Media Catalog\n\nGenerated from authoritative WORLD metadata and MEDIA BLOB storage.\n"
            "This directory is a derived inspection surface, not canon or media authority. Regenerate rather than hand-edit.\n")
    (out_dir/"README.md").write_text(readme,encoding="utf-8")
    print(f"SNAPSHOT        {out_dir}")
    print(f"ASSETS          {len(exported)}")
    return exported


class Handler(BaseHTTPRequestHandler):
    world_path=None; media_path=None; catalog=None
    def send_bytes(self,status,mime,body):
        self.send_response(status); self.send_header("Content-Type",mime); self.send_header("Content-Length",str(len(body))); self.send_header("Cache-Control","private, max-age=3600"); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        p=urlparse(self.path)
        if p.path in {"/","/index.html"}: return self.send_bytes(200,"text/html; charset=utf-8",browser_html(self.catalog).encode())
        if p.path=="/catalog.json": return self.send_bytes(200,"application/json",json.dumps(self.catalog).encode())
        if p.path.startswith("/thumb/") or p.path.startswith("/full/"):
            thumb=p.path.startswith("/thumb/"); key=unquote(p.path.split("/",2)[2]); mime,blob=fetch_blob(self.media_path,key,thumb)
            if blob is None: return self.send_bytes(404,"text/plain",b"media not found")
            return self.send_bytes(200,mime,blob)
        return self.send_bytes(404,"text/plain",b"not found")
    def log_message(self,fmt,*args): pass


def parse_args():
    p=argparse.ArgumentParser(description="Browse/export LOOM media library")
    p.add_argument("--root"); p.add_argument("--db"); p.add_argument("--media-db")
    p.add_argument("--host",default="127.0.0.1"); p.add_argument("--port",type=int,default=8766)
    p.add_argument("--export",help="Write derived snapshot directory instead of serving")
    p.add_argument("--include-full",action="store_true",help="Export original images too (large; thumbnails are default)")
    p.add_argument("--current-only",action="store_true")
    p.add_argument("--no-browser",action="store_true")
    return p.parse_args()


def main():
    a=parse_args(); root=loom_root(a.root); db=Path(a.db) if a.db else root/"data"/"LOOM_2226.sqlite3"; media=Path(a.media_db) if a.media_db else root/"data"/"LOOM_2226_media.sqlite3"
    for p in (db,media):
        if not p.exists(): raise SystemExit(f"LOOM file missing: {p}")
    print(f"LOOM MEDIA LIBRARY v{APP_VERSION}"); print(f"WORLD           {db}"); print(f"MEDIA           {media}")
    catalog=load_catalog(db,media); print(f"ASSETS          {len(catalog)}"); print(f"CURRENT         {sum(bool(x['is_current']) for x in catalog)}"); print(f"THUMBNAILS      {sum(bool(x['thumbnail_present']) for x in catalog)}")
    if a.export:
        export_snapshot(db,media,Path(a.export),a.include_full,a.current_only); return 0
    Handler.world_path=db; Handler.media_path=media; Handler.catalog=catalog
    server=ThreadingHTTPServer((a.host,a.port),Handler); url=f"http://{a.host}:{a.port}/"; print(f"BROWSER         {url}")
    if not a.no_browser:
        try: webbrowser.open(url)
        except Exception: pass
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
    return 0

if __name__=="__main__": raise SystemExit(main())
