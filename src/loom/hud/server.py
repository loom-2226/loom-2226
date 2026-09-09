#!/usr/bin/env python3
"""Local static server for the LOOM HUD qualification surface.

This module is presentation-only. It serves the checked-in HUD assets over
localhost and does not read or mutate campaign, navigation, physics, or data
authority.
"""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8767
DEFAULT_PAGE = "hud_mock_v0_1.html"


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


def serve(*, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, root: Path | None = None) -> None:
    page = validate_assets(root)
    directory = page.parent
    handler = partial(SimpleHTTPRequestHandler, directory=str(directory))
    url = f"http://{host}:{port}/{page.name}"
    print(f"LOOM HUD QUALIFICATION: {url}")
    print("AUTHORITY: MOCK / QUALIFICATION_ONLY")
    print("CAMPAIGN/DATA: READ NONE / WRITE NONE")
    with ThreadingHTTPServer((host, port), handler) as server:
        server.serve_forever()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Serve the LOOM HUD qualification page on localhost")
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
