from __future__ import annotations

"""Loopback-only Experience One HUD server.

Reads authoritative campaign state on each request. Bounded POST endpoints may
translate natural language into the typed flight-intent contract and request a
read-only deterministic Navigator comparison. No campaign writes, authorization,
or execution live here.
"""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlparse

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engineering.experience_one.e1_flight_interaction_contract import FlightIntent
from engineering.experience_one.e1_hud_interaction import MaraIntentSession
from engineering.experience_one.e1_hud_presenter import build_hud_payload, render_hud_html
from engineering.experience_one.e1_mara_intent_adapter import OpenAIMaraIntentAdapter
from engineering.experience_one.e1_navigator_review_service import NavigatorReviewService

DEFAULT_ROOT = Path("/storage/emulated/0/Download/LOOM_TEST")
DEFAULT_AUDIT = Path("/storage/emulated/0/Download/LOOM_OPENAI_DEV_AUDIT.jsonl")
STATE_FILE = "LOOM_STATE_V1.json"
DEFAULT_BIND = "127.0.0.1"
DEFAULT_PORT = 8877
MAX_REQUEST_BYTES = 8192


def _read_campaign_state(root: Path) -> dict:
    state_path = root / STATE_FILE
    if not state_path.exists():
        raise FileNotFoundError(f"authoritative campaign state not found: {state_path}")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(state, dict):
        raise ValueError("campaign state must be a JSON object")
    return state


def load_live_hud_payload(
    root: Path,
    *,
    intent: dict | None = None,
    review_bundle: dict | None = None,
) -> dict:
    review = None if review_bundle is None else review_bundle.get("review")
    details = None if review_bundle is None else review_bundle.get("candidate_display")
    return build_hud_payload(
        _read_campaign_state(root),
        intent=intent,
        review=review,
        candidate_details=details,
    )


def build_mara_intent_session(
    *,
    api_key: str,
    audit_path: Path = DEFAULT_AUDIT,
    model: str = "gpt-5.6-luna",
) -> MaraIntentSession:
    adapter = OpenAIMaraIntentAdapter(api_key=api_key, audit_path=audit_path, model=model)
    return MaraIntentSession(adapter.interpret)


def make_handler(
    root: Path,
    intent_session: MaraIntentSession | None = None,
    navigator_service: NavigatorReviewService | None = None,
):
    class E1HUDHandler(BaseHTTPRequestHandler):
        server_version = "LOOM-E1-HUD/0.3"

        def _send(self, status: int, content_type: str, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-LOOM-Authority", "PRESENTATION_INTENT_REVIEW_ONLY")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, status: int, payload: dict) -> None:
            self._send(status, "application/json; charset=utf-8", json.dumps(payload, indent=2, sort_keys=True).encode("utf-8"))

        def _read_json_object(self) -> dict:
            raw_length = self.headers.get("Content-Length")
            if raw_length is None:
                raise ValueError("Content-Length is required")
            length = int(raw_length)
            if length < 0 or length > MAX_REQUEST_BYTES:
                raise ValueError("request size is invalid")
            raw = self.rfile.read(length)
            request = json.loads(raw.decode("utf-8") or "{}")
            if not isinstance(request, dict):
                raise ValueError("request must be a JSON object")
            return request

        def do_GET(self) -> None:  # noqa: N802
            try:
                route = urlparse(self.path).path
                current_intent = None if intent_session is None else intent_session.current()
                current_review = None if intent_session is None else intent_session.current_review()
                payload = load_live_hud_payload(root, intent=current_intent, review_bundle=current_review)
                if route in ("/", "/index.html"):
                    self._send(200, "text/html; charset=utf-8", render_hud_html(payload).encode("utf-8"))
                    return
                if route == "/state.json":
                    self._json(200, payload)
                    return
                self._send(404, "text/plain; charset=utf-8", b"not found\n")
            except Exception as exc:
                self._json(500, {"status": "ERROR", "type": type(exc).__name__, "message": str(exc), "execution_authority": "ZERO"})

        def do_POST(self) -> None:  # noqa: N802
            route = urlparse(self.path).path
            if route == "/intent.json":
                if intent_session is None:
                    self._json(503, {"status": "INTENT_PROVIDER_UNAVAILABLE", "message": "OPENAI_API_KEY is not available to this HUD process", "execution_authority": "ZERO"})
                    return
                try:
                    request = self._read_json_object()
                    extras = sorted(set(request) - {"text"})
                    if extras:
                        raise ValueError(f"unsupported intent request fields: {extras}")
                    typed = intent_session.capture(str(request.get("text") or ""))
                    self._json(200, {"status": "TYPED_INTENT_READY", "intent": typed, "navigator_planning_status": "NOT_REQUESTED_YET", "campaign_mutation": "NONE"})
                except Exception as exc:
                    self._json(400, {"status": "INTENT_REJECTED", "type": type(exc).__name__, "message": str(exc), "campaign_mutation": "NONE", "execution_authority": "ZERO"})
                return

            if route == "/navigator-review.json":
                if intent_session is None or navigator_service is None:
                    self._json(503, {"status": "NAVIGATOR_REVIEW_UNAVAILABLE", "execution_authority": "ZERO"})
                    return
                try:
                    request = self._read_json_object()
                    if request:
                        raise ValueError("Navigator review request accepts no browser-supplied planning fields")
                    current = intent_session.current()
                    if current is None:
                        raise ValueError("typed Mara intent is required before Navigator review")
                    intent = FlightIntent.from_mapping(current)
                    bundle = navigator_service.generate(root, intent)
                    stored = intent_session.store_review(bundle)
                    self._json(200, {
                        "status": "NAVIGATOR_REVIEW_READY",
                        "review": stored,
                        "campaign_mutation": "NONE",
                        "execution_authority": "NONE_REVIEW_ONLY",
                    })
                except Exception as exc:
                    self._json(400, {"status": "NAVIGATOR_REVIEW_REJECTED", "type": type(exc).__name__, "message": str(exc), "campaign_mutation": "NONE", "execution_authority": "ZERO"})
                return

            self._json(405, {"status": "METHOD_NOT_ALLOWED", "execution_authority": "ZERO"})

        def log_message(self, fmt: str, *args) -> None:
            print("E1 HUD", self.address_string(), fmt % args)

    return E1HUDHandler


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--bind", default=DEFAULT_BIND)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--audit-path", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--model", default="gpt-5.6-luna")
    args = parser.parse_args()

    if args.bind not in {"127.0.0.1", "localhost"}:
        raise RuntimeError("E1 HUD qualification server is loopback-only")

    payload = load_live_hud_payload(args.root)
    campaign = payload["campaign"]
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    intent_session = build_mara_intent_session(api_key=key, audit_path=args.audit_path, model=args.model) if key else None
    navigator_service = NavigatorReviewService()

    print("LOOM E1 HUD             INTERACTIVE REVIEW v0.3")
    print("CAMPAIGN STATE          ", campaign["state_id"])
    print("LOCATION                ", campaign["location_token"])
    print("EPOCH                   ", campaign["epoch_utc"])
    print("BROWSER AUTHORITY       PRESENTATION + INTENT + REVIEW REQUEST ONLY")
    print("MARA INTENT             ", "AUDITED / ENABLED" if intent_session else "DISABLED / OPENAI_API_KEY NOT SET")
    print("NAVIGATOR REVIEW        READ ONLY / ENABLED")
    print("CALC/STATE/EXEC AUTH    ZERO / ZERO / ZERO")
    print(f"URL                     http://127.0.0.1:{args.port}/")

    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(args.root, intent_session, navigator_service))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
