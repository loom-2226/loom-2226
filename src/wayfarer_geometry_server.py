from __future__ import annotations

import argparse
import http.server
import socketserver
import threading
import urllib.request
import webbrowser
from pathlib import Path

from wayfarer_geometry import init_db, write_geometry

THREE_URL = "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.min.js"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure_three(root: Path, allow_download: bool = True) -> tuple[bool, str]:
    target = root / "web" / "three" / "three.module.min.js"
    if target.exists() and target.stat().st_size > 100_000:
        return True, f"THREE.JS          {target}"
    if not allow_download:
        return False, f"THREE.JS MISSING  {target}"
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(THREE_URL, timeout=20) as response:
            data = response.read()
        if len(data) < 100_000:
            raise RuntimeError(f"Downloaded Three.js payload unexpectedly small ({len(data)} bytes)")
        target.write_bytes(data)
        return True, f"THREE.JS CACHED   {target}"
    except Exception as exc:
        return False, f"THREE.JS MISSING  {exc}"


def build(root: Path, reset_db: bool = False) -> dict:
    db = root / "data" / "wayfarer_geometry.sqlite3"
    seed = root / "geometry" / "wayfarer_geometry_seed.sql"
    out = root / "geometry" / "wayfarer_geometry.json"
    conn = init_db(db, seed, reset=reset_db)
    try:
        return write_geometry(conn, out)
    finally:
        conn.close()


def make_handler(root: Path):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root), **kwargs)

        def do_GET(self):
            if self.path in ("/", ""):
                self.path = "/web/index.html"
            return super().do_GET()

        def log_message(self, fmt, *args):
            print("HTTP", fmt % args)
    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile and serve deterministic Wayfarer geometry")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--build-only", action="store_true")
    parser.add_argument("--reset-db", action="store_true", help="reseed geometry DB from SQL")
    parser.add_argument("--no-three-download", action="store_true")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    root = repo_root()
    payload = build(root, reset_db=args.reset_db)
    v = payload["validation"]
    print("LOOM WAYFARER GEOMETRY v0.1")
    print("ROOT             ", root)
    print("GEOMETRY JSON    ", root / "geometry" / "wayfarer_geometry.json")
    print(f"BOUNDARY PROXY    {v['normal_boundary_proxy_m2']:.1f} m^2 / {v['normal_boundary_target_m2']:.1f} m^2")
    print(f"DOCKED DRY MASS   {payload['mass_states']['DOCKED']['dry_mass_t']:.1f} t")
    print(f"DOCKED WET MASS   {payload['mass_states']['DOCKED']['wet_mass_t']:.1f} t")
    print("VALIDATION        ", "PASS" if v["overall_pass"] else "FAIL")
    if not v["overall_pass"]:
        raise SystemExit(2)

    _, msg = ensure_three(root, allow_download=not args.no_three_download)
    print(msg)
    if args.build_only:
        return

    url = f"http://{args.host}:{args.port}/"
    handler = make_handler(root)
    with socketserver.ThreadingTCPServer((args.host, args.port), handler) as httpd:
        httpd.daemon_threads = True
        print("VIEWER            ", url)
        print("STOP              Ctrl-C")
        if not args.no_browser:
            threading.Timer(0.8, lambda: webbrowser.open(url)).start()
        httpd.serve_forever()


if __name__ == "__main__":
    main()
