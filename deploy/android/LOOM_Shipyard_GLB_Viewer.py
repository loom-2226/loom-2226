from __future__ import annotations

import argparse
import os
import subprocess
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_VERSION = "LOOM_SHIPYARD_GLB_SQLITE_PIXEL_v0.1"
DEFAULT_PORT = 2227
HERE = Path(__file__).resolve()
APP_ROOT = HERE.parents[2]
SRC = APP_ROOT / "src"
SYN = SRC / "qualification" / "synthesis"
for p in (SRC, SYN):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from shipyard_glb_viewer import inspect_glb, inspect_glb_file, viewer_html
from shipyard_visual_artifact_store import store_semantic_glb


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


def generate_store_load_governed_glb(db_path: Path) -> tuple[bytes, dict]:
    from governed_ship_synthesis import build_wayfarer_governed_synthesis
    from semantic_geometry import build_semantic_geometry
    from semantic_glb import build_semantic_glb

    source = build_wayfarer_governed_synthesis()
    semantic = build_semantic_geometry(source)
    glb, manifest = build_semantic_glb(source, semantic)
    stored = store_semantic_glb(db_path, glb, manifest)
    return stored.payload, {
        "source": "SQLITE_BLOB",
        "db": str(db_path),
        "artifact_id": stored.artifact_id,
        "sha256": stored.artifact_sha256,
        "authority_status": stored.authority_status,
    }


def resolve_model(model_arg: str | None, db_path: Path) -> tuple[bytes, dict, dict]:
    if model_arg:
        path = Path(model_arg).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        payload = path.read_bytes()
        return payload, inspect_glb_file(path), {
            "source": "EXTERNAL_VISUAL_FIXTURE_FILE",
            "model": str(path),
            "authority_status": "VISUAL_FIXTURE_ONLY",
        }
    payload, storage = generate_store_load_governed_glb(db_path)
    return payload, inspect_glb(payload), storage


def _open_url(url: str) -> None:
    try:
        subprocess.run(["termux-open-url", url], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    except FileNotFoundError:
        webbrowser.open(url)


def serve(model: bytes, info: dict, storage: dict, port: int) -> None:
    html = viewer_html().encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ("/", "/index.html"):
                body, ctype = html, "text/html; charset=utf-8"
            elif self.path == "/model.glb":
                body, ctype = model, "model/gltf-binary"
            elif self.path == "/favicon.ico":
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
            print("[SHIPYARD GLB HTTP] " + (fmt % args))

    server = ThreadingHTTPServer(("127.0.0.1", int(port)), Handler)
    url = f"http://127.0.0.1:{int(port)}/"
    print("LOOM SHIPYARD GLB VIEWER")
    print("========================")
    print(APP_VERSION)
    print(f"SOURCE: {storage['source']}")
    if storage.get("db"):
        print(f"DB: {storage['db']}")
        print(f"ARTIFACT: {storage['artifact_id']}")
        print(f"SHA256: {storage['sha256']}")
    else:
        print(f"MODEL: {storage.get('model')}")
    print(f"GENERATOR: {info['generator']}")
    print(f"MESHES: {info['mesh_count']}  NODES: {info['node_count']}  SEMANTIC: {info['semantic_node_count']}")
    print(f"LOCAL URL: {url}")
    print("NETWORK: loopback only; no internet required")
    print("Ctrl-C to stop.")
    _open_url(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nViewer stopped.")
    finally:
        server.server_close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", help="Optional external .glb visual compatibility fixture; never stored as engineering authority")
    parser.add_argument("--db", help="Shipyard design-ledger SQLite path; defaults to LOOM_SHIPYARD/shipyard_design_ledger.sqlite3")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args(argv)
    db_path = Path(args.db).expanduser().resolve() if args.db else default_db()
    try:
        model, info, storage = resolve_model(args.model, db_path)
    except Exception as exc:
        print(f"SHIPYARD GLB ERROR: {exc}")
        return 2
    if args.status:
        print(f"version={APP_VERSION}")
        print(f"source={storage['source']}")
        if storage.get("db"):
            print(f"db={storage['db']}")
            print(f"artifact_id={storage['artifact_id']}")
            print(f"sha256={storage['sha256']}")
        print(f"generator={info['generator']}")
        print(f"mesh_count={info['mesh_count']}")
        print(f"semantic_node_count={info['semantic_node_count']}")
        return 0
    serve(model, info, storage, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
