#!/usr/bin/env python3
"""Local server for the LOOM HUD surface.

Static HUD assets are served from the checked-in demo directory. The optional
`/flight-view.json` endpoint reads canonical campaign/spatial state through the
existing read-only adapters. It never writes campaign/data authority and never
propagates, interpolates or invents missing vehicle state.
"""
from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import argparse
import json

from loom.hud.live_provider import load_live_flight_view, unavailable_live_payload

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8767
DEFAULT_PAGE = "hud_mock_v0_1.html"
LIVE_ENDPOINT = "/flight-view.json"


def demo_root() -> Path:
    return Path(__file__).resolve().parent / "demo"


def page_path(root: Path | None = None) -> Path:
    base = demo_root() if root is None else Path(root).resolve()
    return base / DEFAULT_PAGE


def validate_assets(root: Path | None = None) -> Path:
    page = page_path(root)
    if not page.is_file():
        raise FileNotFoundError(f"HUD qualification page missing: {page}")
    return page


def make_handler(directory: Path):
    class HudHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

        def do_GET(self):
            if urlparse(self.path).path == LIVE_ENDPOINT:
                try:
                    payload = load_live_flight_view()
                    status = 200
                except Exception as exc:
                    payload = unavailable_live_payload(exc)
                    status = 503
                body = (json.dumps(payload, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
                return
            return super().do_GET()

    return HudHandler


def serve(*, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, root: Path | None = None) -> None:
    page = validate_assets(root)
    directory = page.parent
    handler = make_handler(directory)
    url = f"http://{host}:{port}/{page.name}"
    print(f"LOOM HUD: {url}")
    print(f"LIVE STATE: {LIVE_ENDPOINT} (READ ONLY / FAIL CLOSED)")
    print("CAMPAIGN/DATA: READ ONLY / WRITE NONE")
    with ThreadingHTTPServer((host, port), handler) as server:
        server.serve_forever()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Serve the LOOM HUD on localhost")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if not (1 <= args.port <= 65535):
        raise SystemExit("HUD port must be in 1..65535")
    try:
        serve(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nLOOM HUD stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
