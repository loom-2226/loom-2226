from __future__ import annotations

import argparse
import os
import subprocess
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_VERSION = "LOOM_SHIPYARD_GLB_NATIVE_PIXEL_v0.1"
DEFAULT_PORT = 2227
HERE = Path(__file__).resolve()
APP_ROOT = HERE.parents[2]
SRC = APP_ROOT / "src"
SYN = SRC / "qualification" / "synthesis"
for p in (SRC, SYN):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from shipyard_glb_viewer import inspect_glb_file, viewer_html


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


def generate_governed_glb() -> Path:
    from governed_ship_synthesis import build_wayfarer_governed_synthesis
    from semantic_geometry import build_semantic_geometry
    from semantic_glb import build_semantic_glb, canonical_manifest_json

    source = build_wayfarer_governed_synthesis()
    semantic = build_semantic_geometry(source)
    glb, manifest = build_semantic_glb(source, semantic)
    out = runtime_root() / "semantic_glb"
    out.mkdir(parents=True, exist_ok=True)
    glb_path = out / "wayfarer_semantic_v0.1.glb"
    manifest_path = out / "wayfarer_semantic_v0.1.manifest.json"
    glb_path.write_bytes(glb)
    manifest_path.write_text(canonical_manifest_json(manifest) + "\n", encoding="utf-8")
    return glb_path


def resolve_model(arg: str | None) -> Path:
    if arg:
        path = Path(arg).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        return path
    return generate_governed_glb()


def _open_url(url: str) -> None:
    try:
        subprocess.run(["termux-open-url", url], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    except FileNotFoundError:
        webbrowser.open(url)


def serve(model_path: Path, port: int) -> None:
    html = viewer_html().encode("utf-8")
    model = model_path.read_bytes()
    info = inspect_glb_file(model_path)

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
    print(f"MODEL: {model_path}")
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
    parser.add_argument("--model", help="Optional external .glb visual compatibility fixture")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args(argv)
    try:
        model = resolve_model(args.model)
        info = inspect_glb_file(model)
    except Exception as exc:
        print(f"SHIPYARD GLB ERROR: {exc}")
        return 2
    if args.status:
        print(f"version={APP_VERSION}")
        print(f"model={model}")
        print(f"generator={info['generator']}")
        print(f"mesh_count={info['mesh_count']}")
        print(f"semantic_node_count={info['semantic_node_count']}")
        return 0
    serve(model, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
