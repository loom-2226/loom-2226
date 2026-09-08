from __future__ import annotations

import argparse
import http.server
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional

HOST = "127.0.0.1"
DEFAULT_PORT = 2227
DEFAULT_VIEWER = "wayfarer_governed_synthesis.html"


class GovernedViewerServerError(RuntimeError):
    pass


class ViewerHandler(http.server.BaseHTTPRequestHandler):
    viewer_path: Path

    def do_GET(self) -> None:
        if self.path not in ("/", "/index.html", "/wayfarer"):
            self.send_error(404, "Not found")
            return
        body = self.viewer_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        print("[LOOM SYNTH HTTP] " + (fmt % args))


def validate_viewer(path: Path) -> Path:
    p = path.expanduser().resolve()
    if not p.is_file():
        raise GovernedViewerServerError(f"viewer not found: {p}")
    text = p.read_text(encoding="utf-8", errors="strict")
    required = (
        "WAYFARER — GOVERNED SYNTHESIS v0.1",
        "NOT_STRUCTURALLY_QUALIFIED",
        "OPEN_NO_COUPLED_DISCIPLINE_GRAPH_ADMITTED_v0.1",
        "CAND-5719E3F3251DE6E25FDF",
    )
    missing = [token for token in required if token not in text]
    if missing:
        raise GovernedViewerServerError("viewer failed identity/governance check: " + ", ".join(missing))
    return p


def _handler_for(viewer_path: Path):
    class BoundHandler(ViewerHandler):
        pass
    BoundHandler.viewer_path = viewer_path
    return BoundHandler


def serve(viewer_path: Path, port: int = DEFAULT_PORT, *, open_browser: bool = True) -> None:
    if port < 1 or port > 65535:
        raise GovernedViewerServerError(f"invalid port: {port}")
    viewer = validate_viewer(viewer_path)
    try:
        server = http.server.ThreadingHTTPServer((HOST, port), _handler_for(viewer))
    except OSError as exc:
        raise GovernedViewerServerError(f"could not bind {HOST}:{port}: {exc}") from exc
    if server.server_address[0] != HOST:
        server.server_close()
        raise GovernedViewerServerError("refusing non-loopback bind")
    url = f"http://{HOST}:{port}/"
    print("LOOM Wayfarer Governed Synthesis")
    print(f"VIEWER: {viewer}")
    print(f"LOCAL URL: {url}")
    print("AUTHORITY: research / non-canon / not structurally qualified")
    print("NETWORK: loopback only; no internet required")
    print("Press Ctrl+C to stop.")
    if open_browser:
        threading.Thread(target=lambda: (time.sleep(0.35), webbrowser.open(url)), daemon=True).start()
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print("\nStopping LOOM governed synthesis viewer.")
    finally:
        server.server_close()


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Serve the governed Wayfarer synthesis viewer over loopback-only HTTP.")
    parser.add_argument("--viewer", type=Path, default=Path(__file__).with_name(DEFAULT_VIEWER))
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)
    try:
        serve(args.viewer, args.port, open_browser=not args.no_browser)
    except GovernedViewerServerError as exc:
        print(f"LOOM SYNTHESIS VIEWER ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
