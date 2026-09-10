#!/usr/bin/env python3
"""Local server for the LOOM HUD surface.

Static HUD assets are served from the checked-in demo directory. The optional
`/flight-view.json` endpoint reads canonical campaign/spatial state through the
existing read-only adapters. `/earth-moon-qualification.json` is an explicitly
qualification-only 2026 Earth-Moon propagation surface built from the stored
LOOM celestial catalog; it never writes authority.
"""
from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import argparse
import json

from loom.hud.earth_moon_qualification import build_earth_moon_qualification
from loom.hud.live_provider import load_live_flight_view, unavailable_live_payload

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8767
DEFAULT_PAGE = "earth_moon_qualification.html"
LIVE_ENDPOINT = "/flight-view.json"
EARTH_MOON_ENDPOINT = "/earth-moon-qualification.json"


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

        def _json(self, payload, status=200):
            body = (json.dumps(payload, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == LIVE_ENDPOINT:
                try:
                    self._json(load_live_flight_view())
                except Exception as exc:
                    self._json(unavailable_live_payload(exc), 503)
                return
            if parsed.path == EARTH_MOON_ENDPOINT:
                query = parse_qs(parsed.query)
                epoch = (query.get("epoch") or ["2026-09-10T00:00:00Z"])[0]
                try:
                    days = int((query.get("days") or ["30"])[0])
                    self._json(build_earth_moon_qualification(epoch_utc=epoch, days=days))
                except Exception as exc:
                    self._json({
                        "contract": "LOOM_HUD_EARTH_MOON_QUALIFICATION_V1",
                        "status": "UNAVAILABLE",
                        "authority": "UNAVAILABLE",
                        "reason": str(exc),
                    }, 503)
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
    print(f"EARTH-MOON QUALIFICATION: {EARTH_MOON_ENDPOINT} (DERIVED / NON-NAVIGATION-GRADE)")
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
