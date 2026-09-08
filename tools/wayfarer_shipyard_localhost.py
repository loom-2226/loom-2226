from __future__ import annotations

import argparse
import http.server
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional

HOST = "127.0.0.1"
DEFAULT_PORT = 2226
DEFAULT_VIEWER = "wayfarer_shipyard_3d_pixel_fix.html"


class LocalOnlyServerError(RuntimeError):
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
        print("[LOOM HTTP] " + (fmt % args))


def _handler_for(viewer_path: Path):
    class BoundViewerHandler(ViewerHandler):
        pass

    BoundViewerHandler.viewer_path = viewer_path
    return BoundViewerHandler


def validate_viewer(viewer_path: Path) -> Path:
    p = viewer_path.expanduser().resolve()
    if not p.is_file():
        raise LocalOnlyServerError(f"viewer not found: {p}")
    text = p.read_text(encoding="utf-8", errors="strict")
    required = (
        "WAYFARER SHIPYARD 3D",
        "REVIEW EVIDENCE ONLY",
        "CAND-5719E3F3251DE6E25FDF",
        "CAND-MUT-CB6ACB18C6768B2E0EF9",
    )
    missing = [token for token in required if token not in text]
    if missing:
        raise LocalOnlyServerError("viewer failed identity check: " + ", ".join(missing))
    return p


def make_server(viewer_path: Path, port: int = DEFAULT_PORT) -> http.server.ThreadingHTTPServer:
    # Port 0 is intentionally accepted for tests so the OS may choose a free
    # ephemeral loopback port. User-facing runs default to fixed port 2226.
    if port < 0 or port > 65535:
        raise LocalOnlyServerError(f"invalid port: {port}")
    viewer = validate_viewer(viewer_path)
    try:
        server = http.server.ThreadingHTTPServer((HOST, port), _handler_for(viewer))
    except OSError as exc:
        raise LocalOnlyServerError(f"could not bind {HOST}:{port}: {exc}") from exc
    if server.server_address[0] != HOST:
        server.server_close()
        raise LocalOnlyServerError("refusing non-loopback bind")
    return server


def wait_until_listening(port: int, timeout_s: float = 3.0) -> None:
    deadline = time.monotonic() + timeout_s
    last: Optional[BaseException] = None
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((HOST, port), timeout=0.2):
                return
        except OSError as exc:
            last = exc
            time.sleep(0.05)
    raise LocalOnlyServerError(f"localhost server did not become ready: {last}")


def serve(viewer_path: Path, port: int = DEFAULT_PORT, *, open_browser: bool = True) -> None:
    server = make_server(viewer_path, port)
    actual_port = int(server.server_address[1])
    url = f"http://{HOST}:{actual_port}/"
    print("LOOM Wayfarer Shipyard 3D")
    print(f"VIEWER: {validate_viewer(viewer_path)}")
    print(f"LOCAL URL: {url}")
    print("NETWORK: loopback only; no internet required")
    print("Press Ctrl+C to stop.")
    if open_browser:
        threading.Thread(target=lambda: (time.sleep(0.35), webbrowser.open(url)), daemon=True).start()
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print("\nStopping LOOM localhost viewer.")
    finally:
        server.server_close()


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Serve the frozen LOOM Wayfarer 3D viewer over Android-safe localhost HTTP.")
    parser.add_argument("--viewer", type=Path, default=Path(__file__).with_name(DEFAULT_VIEWER))
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open the local URL.")
    args = parser.parse_args(argv)
    try:
        serve(args.viewer, args.port, open_browser=not args.no_browser)
    except LocalOnlyServerError as exc:
        print(f"LOOM LOCALHOST ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
