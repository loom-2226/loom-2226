from __future__ import annotations

import os
import shutil
import subprocess
import sys
import webbrowser
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_VERSION = "LOOM_SHIPYARD_3D_TEST_PIXEL_v0.3"
DEFAULT_PORT = 2227
VIEWER_NAME = "wayfarer_semantic_3d_smoke.html"
ARTIFACT_ZIP_NAMES = ("wayfarer-semantic-3d-smoke.zip", "LOOM_Shipyard_3D_Test_Pixel.zip")

HERE = Path(__file__).resolve()
APP_ROOT = HERE.parents[2]
BUILDER = APP_ROOT / "src" / "tools" / "wayfarer_semantic_3d_smoke_android.py"


def downloads_root() -> Path:
    override = os.environ.get("LOOM_SHIPYARD_DOWNLOADS")
    if override:
        return Path(override).expanduser().resolve()
    termux = Path.home() / "storage" / "downloads"
    if termux.exists():
        return termux.resolve()
    android = Path("/storage/emulated/0/Download")
    if android.exists():
        return android
    return Path.cwd().resolve()


def runtime_root() -> Path:
    override = os.environ.get("LOOM_SHIPYARD_HOME")
    root = Path(override).expanduser() if override else downloads_root() / "LOOM_SHIPYARD"
    return root.resolve()


def _generate_viewer() -> Path | None:
    if not BUILDER.is_file():
        return None
    out_dir = runtime_root() / "semantic_3d_smoke"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / VIEWER_NAME
    proc = subprocess.run([sys.executable, str(BUILDER), str(out)], cwd=str(APP_ROOT), text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        print("SHIPYARD BUILDER FAILED")
        if proc.stdout.strip(): print(proc.stdout.strip())
        if proc.stderr.strip(): print(proc.stderr.strip())
        return None
    return out if out.is_file() and out.stat().st_size > 0 else None


def discover_viewer(*, generate_if_missing: bool = True) -> Path | None:
    here = HERE.parent
    roots = (here, downloads_root(), runtime_root(), runtime_root() / "semantic_3d_smoke")
    for root in roots:
        candidate = root / VIEWER_NAME
        if candidate.is_file() and candidate.stat().st_size > 0:
            return candidate
    out_dir = runtime_root() / "semantic_3d_smoke"
    for root in roots:
        if not root.exists():
            continue
        zips = [root / name for name in ARTIFACT_ZIP_NAMES if (root / name).is_file()]
        zips += sorted(root.glob("*semantic*3d*.zip"))
        seen = set()
        for zpath in zips:
            if zpath in seen:
                continue
            seen.add(zpath)
            try:
                with zipfile.ZipFile(zpath) as zf:
                    members = [m for m in zf.namelist() if Path(m).name == VIEWER_NAME]
                    if not members:
                        continue
                    out_dir.mkdir(parents=True, exist_ok=True)
                    out = out_dir / VIEWER_NAME
                    with zf.open(sorted(members)[0]) as src, out.open("wb") as dst:
                        shutil.copyfileobj(src, dst)
                    if out.stat().st_size > 0:
                        return out
            except (zipfile.BadZipFile, OSError):
                continue
    if generate_if_missing:
        return _generate_viewer()
    return None


def _open_url(url: str) -> None:
    try:
        subprocess.run(["termux-open-url", url], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    except FileNotFoundError:
        pass
    webbrowser.open(url)


def serve_viewer(path: Path, port: int = DEFAULT_PORT) -> None:
    content = path.read_bytes()
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            elif self.path == "/favicon.ico":
                self.send_response(204); self.end_headers()
            else:
                self.send_error(404, "Not found")
        def log_message(self, fmt, *args):
            print("[SHIPYARD 3D HTTP] " + (fmt % args))
    server = ThreadingHTTPServer(("127.0.0.1", int(port)), Handler)
    url = f"http://127.0.0.1:{int(port)}/"
    print("LOOM SHIPYARD 3D TEST")
    print("=====================")
    print(APP_VERSION)
    print(f"BUILDER: {BUILDER}")
    print(f"VIEWER: {path}")
    print(f"LOCAL URL: {url}")
    print("NETWORK: loopback only; no internet required")
    print("Leave this Python process running while using Chrome.")
    _open_url(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nViewer stopped.")
    finally:
        server.server_close()


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ["--status"]:
        viewer = discover_viewer(generate_if_missing=False)
        print(f"version={APP_VERSION}")
        print(f"app_root={APP_ROOT}")
        print(f"builder={BUILDER if BUILDER.is_file() else None}")
        print(f"downloads={downloads_root()}")
        print(f"runtime={runtime_root()}")
        print(f"viewer={viewer}")
        return 0 if (viewer or BUILDER.is_file()) else 2
    viewer = discover_viewer(generate_if_missing=True)
    if viewer is None:
        print(f"SHIPYARD ERROR: could not locate or generate {VIEWER_NAME}.")
        print(f"Expected installed builder: {BUILDER}")
        return 2
    serve_viewer(viewer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
