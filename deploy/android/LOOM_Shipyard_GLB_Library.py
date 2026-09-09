from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_VERSION = "LOOM_SHIPYARD_GLB_LIBRARY_PIXEL_v0.3"
DEFAULT_PORT = 2227
HERE = Path(__file__).resolve()
APP_ROOT = HERE.parents[2]
SRC = APP_ROOT / "src"
SYN = SRC / "qualification" / "synthesis"
for p in (SRC, SYN):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from shipyard_glb_viewer_compat import viewer_html
from shipyard_realization_handoff import build_library_realization_packet, canonical_packet_json
from shipyard_visual_library import add_glb_asset, import_glb_file, list_assets, load_asset


def downloads_root() -> Path:
    termux = Path.home() / "storage" / "downloads"
    if termux.exists():
        return termux.resolve()
    android = Path("/storage/emulated/0/Download")
    if android.exists():
        return android
    return Path.cwd().resolve()


def runtime_root() -> Path:
    override = os.environ.get("LOOM_SHIPYARD_HOME")
    return (Path(override).expanduser() if override else downloads_root() / "LOOM_SHIPYARD").resolve()


def default_db() -> Path:
    override = os.environ.get("LOOM_SHIPYARD_DB")
    return (Path(override).expanduser() if override else runtime_root() / "shipyard_design_ledger.sqlite3").resolve()


def ensure_governed_wayfarer(db_path: Path):
    from governed_ship_synthesis import build_wayfarer_governed_synthesis
    from semantic_geometry import build_semantic_geometry
    from semantic_glb import build_semantic_glb

    source = build_wayfarer_governed_synthesis()
    semantic = build_semantic_geometry(source)
    glb, manifest = build_semantic_glb(source, semantic)
    return add_glb_asset(
        db_path,
        glb,
        display_name="Wayfarer — Governed Semantic",
        ship_name="Wayfarer",
        artifact_class="GOVERNED_SEMANTIC",
        source_candidate_id=manifest.get("source_design_candidate_id"),
        source_candidate_hash=manifest.get("source_design_candidate_hash"),
        metadata={
            "source_governed_package_hash": manifest.get("source_governed_package_hash"),
            "source_semantic_package_hash": manifest.get("source_semantic_package_hash"),
            "open_semantic_items": manifest.get("open_semantic_items", []),
        },
    )


def _library_html() -> str:
    html = viewer_html()
    html = html.replace("fetch('/model.glb'", "fetch('/model.glb'+location.search")
    controls = r'''
<style>
#librarybar{display:grid;grid-template-columns:minmax(0,1fr) auto auto auto;gap:.35rem;align-items:center;padding:.35rem .45rem;background:#0f1319;border-bottom:1px solid #2a313c}
#librarySelect,#yardSelect{min-width:0;background:#171d25;color:#e7edf5;border:1px solid #465265;border-radius:.35rem;padding:.4rem}
#libraryMeta{font:10px ui-monospace,monospace;color:#aeb9c7;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:28vw}
#packetLink{display:inline-block;background:#1c232d;color:#e8edf3;border:1px solid #465265;border-radius:.35rem;padding:.38rem .52rem;text-decoration:none;font-size:12px}
@media(max-width:720px){
  header{gap:.22rem;padding:.32rem;overflow-x:auto;flex-wrap:nowrap}header strong{font-size:14px;white-space:nowrap}button{padding:.32rem .42rem;font-size:12px;white-space:nowrap}
  #librarybar{grid-template-columns:minmax(0,1fr) auto;grid-template-areas:'asset asset' 'yard packet' 'meta meta';padding:.3rem;gap:.28rem}
  #librarySelect{grid-area:asset;width:100%;font-size:12px}#yardSelect{grid-area:yard;font-size:12px}#packetLink{grid-area:packet;text-align:center;font-size:12px}
  #libraryMeta{grid-area:meta;max-width:none;width:100%;font-size:9px;white-space:normal;line-height:1.25}
  #hud{max-width:60vw;font-size:9px}#pick{max-width:34vw;font-size:9px}
}
</style>
<script>
(()=>{const app=document.getElementById('app'),header=app.querySelector('header');const bar=document.createElement('div');bar.id='librarybar';bar.innerHTML='<select id="librarySelect"></select><select id="yardSelect"><option>ASTERIA</option><option>KELDRIN</option><option>SHIKARI</option><option>TASCHEN</option></select><a id="packetLink" target="_blank">PACKET</a><span id="libraryMeta">SQL GLB LIBRARY</span>';header.insertAdjacentElement('afterend',bar);app.style.gridTemplateRows='auto auto 1fr';const sel=bar.querySelector('#librarySelect'),yard=bar.querySelector('#yardSelect'),meta=bar.querySelector('#libraryMeta'),packet=bar.querySelector('#packetLink');const params=new URLSearchParams(location.search),current=params.get('asset');function refreshPacket(){const asset=sel.value;if(!asset)return;packet.href='/api/realization?asset='+encodeURIComponent(asset)+'&yard='+encodeURIComponent(yard.value)}yard.onchange=refreshPacket;fetch('/api/library',{cache:'no-store'}).then(r=>r.json()).then(rows=>{for(const x of rows){const o=document.createElement('option');o.value=x.asset_id;o.textContent=x.display_name+' ['+x.artifact_class+']';if(x.asset_id===current)o.selected=true;sel.appendChild(o)}const chosen=rows.find(x=>x.asset_id===(current||sel.value))||rows[0];if(chosen)meta.textContent=chosen.mesh_count+' meshes • '+chosen.semantic_node_count+' semantic • '+chosen.authority_status;sel.onchange=()=>{location.search='?asset='+encodeURIComponent(sel.value)};refreshPacket()}).catch(e=>meta.textContent='LIBRARY ERROR: '+e);})();
</script>
'''
    return html.replace("</body>", controls + "</body>")


def _open_url(url: str) -> None:
    try:
        subprocess.run(["termux-open-url", url], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    except FileNotFoundError:
        webbrowser.open(url)


def serve(db_path: Path, port: int) -> None:
    html = _library_html().encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlsplit(self.path)
            if parsed.path in ("/", "/index.html"):
                body, ctype = html, "text/html; charset=utf-8"
            elif parsed.path == "/api/library":
                body = json.dumps(list_assets(db_path), sort_keys=True).encode("utf-8")
                ctype = "application/json; charset=utf-8"
            elif parsed.path == "/api/realization":
                query = urllib.parse.parse_qs(parsed.query)
                asset_id = query.get("asset", [None])[0]
                yard = query.get("yard", ["ASTERIA"])[0].upper()
                if asset_id is None:
                    self.send_error(400, "asset is required"); return
                try:
                    asset = load_asset(db_path, asset_id)
                    packet = build_library_realization_packet(asset, yard)
                    body = (canonical_packet_json(packet) + "\n").encode("utf-8")
                    ctype = "application/json; charset=utf-8"
                except Exception as exc:
                    self.send_error(400, str(exc)); return
            elif parsed.path == "/model.glb":
                query = urllib.parse.parse_qs(parsed.query)
                asset_id = query.get("asset", [None])[0]
                rows = list_assets(db_path)
                if not rows:
                    self.send_error(404, "No visual library assets"); return
                if asset_id is None:
                    asset_id = rows[0]["asset_id"]
                try:
                    asset = load_asset(db_path, asset_id)
                except Exception as exc:
                    self.send_error(404, str(exc)); return
                body, ctype = asset.payload, "model/gltf-binary"
            elif parsed.path == "/favicon.ico":
                self.send_response(204); self.end_headers(); return
            else:
                self.send_error(404, "Not found"); return
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            print("[SHIPYARD GLB LIBRARY HTTP] " + (fmt % args))

    server = ThreadingHTTPServer(("127.0.0.1", int(port)), Handler)
    url = f"http://127.0.0.1:{int(port)}/"
    rows = list_assets(db_path)
    print("LOOM SHIPYARD GLB LIBRARY")
    print("=========================")
    print(APP_VERSION)
    print(f"DB: {db_path}")
    print(f"ASSETS: {len(rows)}")
    for row in rows:
        print(f" - {row['display_name']} | {row['artifact_class']} | {row['mesh_count']} meshes | {row['asset_id']}")
    print(f"LOCAL URL: {url}")
    print("PACKET API: /api/realization?asset=<asset_id>&yard=ASTERIA|KELDRIN|SHIKARI|TASCHEN")
    print("NETWORK: loopback only; no internet required")
    print("Ctrl-C to stop.")
    _open_url(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nLibrary stopped.")
    finally:
        server.server_close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", help="Shipyard design-ledger SQLite path")
    parser.add_argument("--import-glb", dest="import_glb", help="Import a GLB into the visual library")
    parser.add_argument("--label", help="Display label for --import-glb")
    parser.add_argument("--ship", default="Wayfarer", help="Ship/library grouping name")
    parser.add_argument("--class", dest="artifact_class", default="VISUAL_REFERENCE", choices=["VISUAL_REFERENCE", "EXTERNAL_FIXTURE"])
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--packet-asset", help="Emit one realization packet for a library asset and exit")
    parser.add_argument("--yard", default="ASTERIA", choices=["ASTERIA", "KELDRIN", "SHIKARI", "TASCHEN"])
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args(argv)
    db_path = Path(args.db).expanduser().resolve() if args.db else default_db()
    try:
        ensure_governed_wayfarer(db_path)
        if args.import_glb:
            label = args.label or Path(args.import_glb).stem
            imported = import_glb_file(db_path, args.import_glb, display_name=label, ship_name=args.ship, artifact_class=args.artifact_class)
            print(f"IMPORTED: {imported.display_name} -> {imported.asset_id}")
        rows = list_assets(db_path)
        if args.packet_asset:
            packet = build_library_realization_packet(load_asset(db_path, args.packet_asset), args.yard)
            print(canonical_packet_json(packet))
            return 0
    except Exception as exc:
        print(f"SHIPYARD GLB LIBRARY ERROR: {exc}")
        return 2
    if args.list:
        print(f"version={APP_VERSION}")
        print(f"db={db_path}")
        for row in rows:
            print(json.dumps(row, sort_keys=True))
        return 0
    serve(db_path, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
