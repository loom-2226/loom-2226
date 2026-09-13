from __future__ import annotations

"""Loopback-only Experience One HUD server.

Reads authoritative campaign state on each request and serves presentation-only
HTML/JSON. It contains no campaign writes, flight calculation, authorization or
execution path.
"""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from urllib.parse import urlparse

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engineering.experience_one.e1_hud_presenter import build_hud_payload, render_hud_html

DEFAULT_ROOT = Path("/storage/emulated/0/Download/LOOM_TEST")
STATE_FILE = "LOOM_STATE_V1.json"
DEFAULT_BIND = "127.0.0.1"
DEFAULT_PORT = 8877


def load_live_hud_payload(root: Path) -> dict:
    state_path = root / STATE_FILE
    if not state_path.exists():
        raise FileNotFoundError(f"authoritative campaign state not found: {state_path}")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(state, dict):
        raise ValueError("campaign state must be a JSON object")
    return build_hud_payload(state)


def make_handler(root: Path):
    class E1HUDHandler(BaseHTTPRequestHandler):
        server_version = "LOOM-E1-HUD/0.1"

        def _send(self, status: int, content_type: str, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-LOOM-Authority", "PRESENTATION_ONLY")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802 - stdlib handler contract
            try:
                route = urlparse(self.path).path
                payload = load_live_hud_payload(root)
                if route in ("/", "/index.html"):
                    body = render_hud_html(payload).encode("utf-8")
                    self._send(200, "text/html; charset=utf-8", body)
                    return
                if route == "/state.json":
                    body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
                    self._send(200, "application/json; charset=utf-8", body)
                    return
                self._send(404, "text/plain; charset=utf-8", b"not found\n")
            except Exception as exc:
                body = json.dumps({
                    "status": "ERROR",
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "authority": "PRESENTATION_ONLY",
                }, indent=2).encode("utf-8")
                self._send(500, "application/json; charset=utf-8", body)

        def do_POST(self) -> None:  # noqa: N802 - stdlib handler contract
            self._send(
                405,
                "application/json; charset=utf-8",
                json.dumps({
                    "status": "METHOD_NOT_ALLOWED",
                    "reason": "E1 HUD v0.1 is read-only",
                    "execution_authority": "ZERO",
                }).encode("utf-8"),
            )

        def log_message(self, fmt: str, *args) -> None:
            print("E1 HUD", self.address_string(), fmt % args)

    return E1HUDHandler


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--bind", default=DEFAULT_BIND)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    if args.bind not in {"127.0.0.1", "localhost"}:
        raise RuntimeError("E1 HUD qualification server is loopback-only")
    # Fail closed before binding if campaign state is absent/invalid.
    payload = load_live_hud_payload(args.root)
    campaign = payload["campaign"]
    print("LOOM E1 HUD             READ ONLY")
    print("CAMPAIGN STATE          ", campaign["state_id"])
    print("LOCATION                ", campaign["location_token"])
    print("EPOCH                   ", campaign["epoch_utc"])
    print("BROWSER AUTHORITY       PRESENTATION_ONLY")
    print("CALC/STATE/EXEC AUTH    ZERO / ZERO / ZERO")
    print(f"URL                     http://127.0.0.1:{args.port}/")

    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(args.root))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
