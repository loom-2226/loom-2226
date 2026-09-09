from __future__ import annotations

import os
import shutil
import subprocess
import sys
import webbrowser
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_VERSION = "LOOM_SHIPYARD_3D_TEST_PIXEL_v0.1"
DEFAULT_PORT = 2227
VIEWER_NAME = "wayfarer_semantic_3d_smoke.html"
ARTIFACT_ZIP_NAMES = ("wayfarer-semantic-3d-smoke.zip", "LOOM_Shipyard_3D_Test_Pixel.zip")


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


def discover_viewer() -> Path | None:
    here = Path(__file__).resolve().parent
    roots = (here, downloads_root(), runtime_root())
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
    return None


def _open_url(url: str) -> None:
    try:
        subprocess.run(
            ["termux-open-url", url],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
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
                self.send_response(204)
                self.end_headers()
            else:
                self.send_error(404, "Not found")

        def log_message(self, fmt, *args):
            print("[SHIPYARD 3D HTTP] " + (fmt % args))

    server = ThreadingHTTPServer(("127.0.0.1", int(port)), Handler)
    url = f"http://127.0.0.1:{int(port)}/"
    print("LOOM SHIPYARD 3D TEST")
    print("=====================")
    print(APP_VERSION)
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
        viewer = discover_viewer()
        print(f"version={APP_VERSION}")
        print(f"downloads={downloads_root()}")
        print(f"runtime={runtime_root()}")
        print(f"viewer={viewer}")
        return 0 if viewer else 2
    viewer = discover_viewer()
    if viewer is None:
        print(f"SHIPYARD ERROR: {VIEWER_NAME} not found.")
        print("Put the HTML or the semantic-3D ZIP in Downloads beside this launcher and run again.")
        return 2
    serve_viewer(viewer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
