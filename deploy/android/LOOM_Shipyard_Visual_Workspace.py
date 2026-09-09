from __future__ import annotations

import argparse, json, os, subprocess, sys, urllib.parse, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_VERSION = "LOOM_SHIPYARD_VISUAL_WORKSPACE_PIXEL_v0.1"
DEFAULT_PORT = 2227
HERE = Path(__file__).resolve(); APP_ROOT = HERE.parents[2]; SRC = APP_ROOT / "src"; SYN = SRC / "qualification" / "synthesis"
for p in (SRC, SYN):
    if str(p) not in sys.path: sys.path.insert(0, str(p))

from shipyard_glb_viewer_compat import viewer_html
from shipyard_realization_handoff import build_library_realization_packet, canonical_packet_json
from shipyard_visual_library import list_assets, load_asset
from shipyard_visual_realizations import list_realizations, load_realization, store_realization
from LOOM_Shipyard_GLB_Library import default_db, ensure_governed_wayfarer


def _html() -> str:
    html = viewer_html().replace("fetch('/model.glb'", "fetch('/model.glb'+location.search")
    addon = r'''
<style>
#workbar{display:grid;grid-template-columns:minmax(0,1fr) auto auto auto auto;gap:.3rem;align-items:center;padding:.35rem;background:#0f1319;border-bottom:1px solid #2a313c}
#asset,#yard{background:#171d25;color:#e7edf5;border:1px solid #465265;border-radius:.35rem;padding:.38rem;min-width:0}#packet,#uploadBtn,#show3d{background:#1c232d;color:#e8edf3;border:1px solid #465265;border-radius:.35rem;padding:.38rem .5rem;text-decoration:none;font-size:12px;text-align:center}
#realizations{position:absolute;inset:.5rem;display:none;background:#0b0f15ee;border:1px solid #384353;border-radius:.5rem;padding:.5rem;overflow:auto;z-index:5}#realizations.show{display:block}.card{margin:.4rem 0;border:1px solid #384353;border-radius:.4rem;padding:.4rem}.card img{display:block;max-width:100%;max-height:62vh;margin:.35rem auto}.small{font:10px ui-monospace,monospace;color:#aeb9c7}
@media(max-width:720px){#workbar{grid-template-columns:1fr 1fr;grid-template-areas:'asset asset' 'yard packet' 'upload show';}.asset{grid-area:asset}#yard{grid-area:yard}#packet{grid-area:packet}#uploadBtn{grid-area:upload}#show3d{grid-area:show}header{overflow-x:auto;flex-wrap:nowrap}header strong{white-space:nowrap;font-size:14px}}
</style>
<input id="fileInput" type="file" accept="image/png,image/jpeg,image/webp" hidden>
<script>
(()=>{const app=document.getElementById('app'),header=app.querySelector('header'),stage=document.getElementById('stage');const bar=document.createElement('div');bar.id='workbar';bar.innerHTML='<select id="asset" class="asset"></select><select id="yard"><option>ASTERIA</option><option>KELDRIN</option><option>SHIKARI</option><option>TASCHEN</option></select><a id="packet" target="_blank">PACKET</a><button id="uploadBtn">IMPORT IMAGE</button><button id="show3d">REALIZATIONS</button>';header.insertAdjacentElement('afterend',bar);app.style.gridTemplateRows='auto auto 1fr';const panel=document.createElement('div');panel.id='realizations';panel.innerHTML='<button id="closePanel">CLOSE</button><div id="cards"></div>';stage.appendChild(panel);const asset=document.getElementById('asset'),yard=document.getElementById('yard'),packet=document.getElementById('packet'),input=document.getElementById('fileInput'),cards=document.getElementById('cards');const current=new URLSearchParams(location.search).get('asset');function packetUrl(){return '/api/realization?asset='+encodeURIComponent(asset.value)+'&yard='+encodeURIComponent(yard.value)}function refreshPacket(){packet.href=packetUrl()}async function loadCards(){const r=await fetch('/api/realizations?asset='+encodeURIComponent(asset.value),{cache:'no-store'});const rows=await r.json();cards.innerHTML=rows.length?'':'<div class="small">No stored realizations for this GLB yet.</div>';for(const x of rows){const d=document.createElement('div');d.className='card';d.innerHTML='<b>'+x.yard_id+' — '+x.display_name+'</b><div class="small">'+x.authority_status+'<br>'+x.image_sha256.slice(0,16)+'…</div><img src="/realization-image?id='+encodeURIComponent(x.realization_id)+'">';cards.appendChild(d)}}fetch('/api/library',{cache:'no-store'}).then(r=>r.json()).then(rows=>{for(const x of rows){const o=document.createElement('option');o.value=x.asset_id;o.textContent=x.display_name+' ['+x.artifact_class+']';if(x.asset_id===current)o.selected=true;asset.appendChild(o)}asset.onchange=()=>location.search='?asset='+encodeURIComponent(asset.value);yard.onchange=refreshPacket;refreshPacket()});document.getElementById('show3d').onclick=async()=>{await loadCards();panel.classList.add('show')};document.getElementById('closePanel').onclick=()=>panel.classList.remove('show');document.getElementById('uploadBtn').onclick=()=>input.click();input.onchange=async()=>{if(!input.files||!input.files[0])return;const f=input.files[0];const p=await fetch(packetUrl(),{cache:'no-store'}).then(r=>r.json());const url='/api/realization-image?asset='+encodeURIComponent(asset.value)+'&yard='+encodeURIComponent(yard.value)+'&packet_hash='+encodeURIComponent(p.packet_hash)+'&name='+encodeURIComponent(f.name)+'&mime='+encodeURIComponent(f.type||'image/png');const res=await fetch(url,{method:'POST',body:await f.arrayBuffer()});if(!res.ok){alert('IMPORT FAILED: '+await res.text());return}await loadCards();panel.classList.add('show');input.value=''};})();
</script>
'''
    return html.replace("</body>", addon + "</body>")


def _open(url: str):
    try: subprocess.run(["termux-open-url", url], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError: webbrowser.open(url)


def serve(db: Path, port: int):
    body_html = _html().encode()
    class H(BaseHTTPRequestHandler):
        def _send(self, body: bytes, ctype: str, status=200):
            self.send_response(status); self.send_header('Content-Type',ctype); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
        def do_GET(self):
            p=urllib.parse.urlsplit(self.path); q=urllib.parse.parse_qs(p.query)
            try:
                if p.path in ('/','/index.html'): return self._send(body_html,'text/html; charset=utf-8')
                if p.path=='/api/library': return self._send(json.dumps(list_assets(db),sort_keys=True).encode(),'application/json')
                if p.path=='/model.glb':
                    rows=list_assets(db); aid=q.get('asset',[rows[0]['asset_id'] if rows else None])[0]
                    if not aid: raise ValueError('No visual library assets')
                    return self._send(load_asset(db,aid).payload,'model/gltf-binary')
                if p.path=='/api/realization':
                    aid=q.get('asset',[None])[0]; yard=q.get('yard',['ASTERIA'])[0]
                    if not aid: raise ValueError('asset is required')
                    pkt=build_library_realization_packet(load_asset(db,aid),yard)
                    return self._send((canonical_packet_json(pkt)+'\n').encode(),'application/json')
                if p.path=='/api/realizations':
                    aid=q.get('asset',[None])[0]; return self._send(json.dumps(list_realizations(db,aid),sort_keys=True).encode(),'application/json')
                if p.path=='/realization-image':
                    rid=q.get('id',[None])[0]
                    if not rid: raise ValueError('id is required')
                    r=load_realization(db,rid); return self._send(r.payload,r.mime_type)
                if p.path=='/favicon.ico': self.send_response(204); self.end_headers(); return
                self.send_error(404)
            except Exception as e: self._send(str(e).encode(),'text/plain; charset=utf-8',400)
        def do_POST(self):
            p=urllib.parse.urlsplit(self.path); q=urllib.parse.parse_qs(p.query)
            if p.path!='/api/realization-image': self.send_error(404); return
            try:
                n=int(self.headers.get('Content-Length','0'))
                if n<=0 or n>40*1024*1024: raise ValueError('invalid image payload size')
                image=self.rfile.read(n); aid=q.get('asset',[None])[0]; yard=q.get('yard',[None])[0]; ph=q.get('packet_hash',[None])[0]; name=q.get('name',['realization'])[0]; mime=q.get('mime',['image/png'])[0]
                if not aid or not yard or not ph: raise ValueError('asset, yard and packet_hash are required')
                expected=build_library_realization_packet(load_asset(db,aid),yard)
                if expected['packet_hash']!=ph: raise ValueError('packet hash mismatch')
                r=store_realization(db,source_asset_id=aid,yard_id=yard,packet_hash=ph,display_name=name,mime_type=mime,payload=image)
                self._send(json.dumps({'realization_id':r.realization_id,'image_sha256':r.image_sha256,'authority_status':r.authority_status},sort_keys=True).encode(),'application/json')
            except Exception as e: self._send(str(e).encode(),'text/plain; charset=utf-8',400)
        def log_message(self,fmt,*args): print('[SHIPYARD VISUAL WORKSPACE] '+(fmt%args))
    server=ThreadingHTTPServer(('127.0.0.1',port),H); url=f'http://127.0.0.1:{port}/'; print('LOOM SHIPYARD VISUAL WORKSPACE'); print('================================'); print(APP_VERSION); print(f'DB: {db}'); print(f'LOCAL URL: {url}'); print('REALIZATIONS: stored in SQLite as non-authoritative image BLOBs'); print('Ctrl-C to stop.'); _open(url)
    try: server.serve_forever()
    except KeyboardInterrupt: print('\nWorkspace stopped.')
    finally: server.server_close()


def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument('--db'); ap.add_argument('--port',type=int,default=DEFAULT_PORT); args=ap.parse_args(argv); db=Path(args.db).expanduser().resolve() if args.db else default_db()
    try: ensure_governed_wayfarer(db)
    except Exception as e: print('SHIPYARD VISUAL WORKSPACE ERROR:',e); return 2
    serve(db,args.port); return 0

if __name__=='__main__': raise SystemExit(main())
