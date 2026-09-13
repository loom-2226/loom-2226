from __future__ import annotations

"""Loopback-only Experience One HUD server.

The browser may submit intent text, request Navigator comparison, select one
reviewed candidate for Navigator finalization, and explicitly authorize that
finalized plan. No execution endpoint exists in this slice.
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
from engineering.experience_one.e1_navigator_finalization_service import NavigatorFinalizationService

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


def load_live_hud_payload(root: Path, *, intent: dict | None = None, review_bundle: dict | None = None,
                          finalization: dict | None = None, authorization: dict | None = None) -> dict:
    review = None if review_bundle is None else review_bundle.get("review")
    details = None if review_bundle is None else review_bundle.get("candidate_display")
    return build_hud_payload(_read_campaign_state(root), intent=intent, review=review,
                             candidate_details=details, finalization=finalization,
                             authorization=authorization)


def build_mara_intent_session(*, api_key: str, audit_path: Path = DEFAULT_AUDIT,
                              model: str = "gpt-5.6-luna") -> MaraIntentSession:
    return MaraIntentSession(OpenAIMaraIntentAdapter(api_key=api_key, audit_path=audit_path, model=model).interpret)


def make_handler(root: Path, intent_session: MaraIntentSession | None = None,
                 navigator_service: NavigatorReviewService | None = None,
                 finalization_service: NavigatorFinalizationService | None = None):
    class E1HUDHandler(BaseHTTPRequestHandler):
        server_version = "LOOM-E1-HUD/0.4"

        def _send(self, status: int, content_type: str, body: bytes) -> None:
            self.send_response(status); self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body))); self.send_header("Cache-Control", "no-store")
            self.send_header("X-LOOM-Authority", "PRESENTATION_INTENT_REVIEW_AUTHORIZATION_REQUEST_ONLY")
            self.end_headers(); self.wfile.write(body)

        def _json(self, status: int, payload: dict) -> None:
            self._send(status, "application/json; charset=utf-8", json.dumps(payload, indent=2, sort_keys=True).encode())

        def _read_json_object(self) -> dict:
            raw_length = self.headers.get("Content-Length")
            if raw_length is None: raise ValueError("Content-Length is required")
            length = int(raw_length)
            if length < 0 or length > MAX_REQUEST_BYTES: raise ValueError("request size is invalid")
            request = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            if not isinstance(request, dict): raise ValueError("request must be a JSON object")
            return request

        def do_GET(self) -> None:  # noqa: N802
            try:
                route = urlparse(self.path).path
                current_intent = None if intent_session is None else intent_session.current()
                current_review = None if intent_session is None else intent_session.current_review()
                current_finalization = None if intent_session is None else intent_session.current_finalization()
                current_authorization = None if intent_session is None else intent_session.current_authorization()
                payload = load_live_hud_payload(root, intent=current_intent, review_bundle=current_review,
                                               finalization=current_finalization, authorization=current_authorization)
                if route in ("/", "/index.html"):
                    self._send(200, "text/html; charset=utf-8", render_hud_html(payload).encode()); return
                if route == "/state.json": self._json(200, payload); return
                self._send(404, "text/plain; charset=utf-8", b"not found\n")
            except Exception as exc:
                self._json(500, {"status":"ERROR","type":type(exc).__name__,"message":str(exc),"execution_authority":"ZERO"})

        def do_POST(self) -> None:  # noqa: N802
            route = urlparse(self.path).path
            try:
                if route == "/intent.json":
                    if intent_session is None: raise RuntimeError("OPENAI_API_KEY is not available to this HUD process")
                    request=self._read_json_object(); extras=sorted(set(request)-{"text"})
                    if extras: raise ValueError(f"unsupported intent request fields: {extras}")
                    typed=intent_session.capture(str(request.get("text") or ""))
                    self._json(200,{"status":"TYPED_INTENT_READY","intent":typed,"campaign_mutation":"NONE"}); return

                if route == "/navigator-review.json":
                    if intent_session is None or navigator_service is None: raise RuntimeError("Navigator review unavailable")
                    if self._read_json_object(): raise ValueError("Navigator review accepts no browser planning fields")
                    current=intent_session.current()
                    if current is None: raise ValueError("typed Mara intent is required before Navigator review")
                    bundle=navigator_service.generate(root, FlightIntent.from_mapping(current))
                    self._json(200,{"status":"NAVIGATOR_REVIEW_READY","review":intent_session.store_review(bundle),"campaign_mutation":"NONE"}); return

                if route == "/navigator-finalize.json":
                    if intent_session is None or finalization_service is None: raise RuntimeError("Navigator finalization unavailable")
                    request=self._read_json_object()
                    if sorted(request) != ["plan_number"]: raise ValueError("finalization requires only plan_number")
                    current=intent_session.current(); review=intent_session.current_review()
                    if current is None or review is None: raise ValueError("typed intent and Navigator review are required")
                    bundle=finalization_service.finalize(root, FlightIntent.from_mapping(current), review, int(request["plan_number"]))
                    self._json(200,{"status":"NAVIGATOR_FINAL_PLAN_READY","finalization":intent_session.store_finalization(bundle),"campaign_mutation":"NONE","execution_authority":"ZERO"}); return

                if route == "/authorize.json":
                    if intent_session is None: raise RuntimeError("interaction session unavailable")
                    request=self._read_json_object()
                    if sorted(request) != ["authorized"] or request.get("authorized") is not True:
                        raise ValueError("explicit authorized=true is required")
                    auth=intent_session.authorize("HUMAN_PIXEL")
                    self._json(200,{"status":"FLIGHT_AUTHORIZATION_RECORDED","authorization":auth,"campaign_mutation":"NONE","execution_status":"NOT_REQUESTED"}); return

                self._json(405,{"status":"METHOD_NOT_ALLOWED","execution_authority":"ZERO"})
            except Exception as exc:
                self._json(400,{"status":"REQUEST_REJECTED","type":type(exc).__name__,"message":str(exc),"campaign_mutation":"NONE","execution_authority":"ZERO"})

        def log_message(self, fmt: str, *args) -> None:
            print("E1 HUD", self.address_string(), fmt % args)

    return E1HUDHandler


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--root",type=Path,default=DEFAULT_ROOT)
    parser.add_argument("--bind",default=DEFAULT_BIND); parser.add_argument("--port",type=int,default=DEFAULT_PORT)
    parser.add_argument("--audit-path",type=Path,default=DEFAULT_AUDIT); parser.add_argument("--model",default="gpt-5.6-luna")
    args=parser.parse_args()
    if args.bind not in {"127.0.0.1","localhost"}: raise RuntimeError("E1 HUD qualification server is loopback-only")
    payload=load_live_hud_payload(args.root); campaign=payload["campaign"]
    key=os.environ.get("OPENAI_API_KEY","").strip()
    session=build_mara_intent_session(api_key=key,audit_path=args.audit_path,model=args.model) if key else None
    review_service=NavigatorReviewService(); finalize_service=NavigatorFinalizationService()
    print("LOOM E1 HUD             INTERACTIVE AUTHORIZATION v0.4")
    print("CAMPAIGN STATE          ",campaign["state_id"]); print("LOCATION                ",campaign["location_token"])
    print("EPOCH                   ",campaign["epoch_utc"])
    print("BROWSER AUTHORITY       PRESENTATION + REQUESTS ONLY")
    print("MARA INTENT             ","AUDITED / ENABLED" if session else "DISABLED / OPENAI_API_KEY NOT SET")
    print("NAVIGATOR REVIEW        READ ONLY / ENABLED")
    print("NAVIGATOR FINALIZATION  TEMP COPY / COMMIT DECLINED")
    print("EXECUTION ENDPOINT      NONE")
    print("CALC/STATE/EXEC AUTH    ZERO / ZERO / ZERO")
    print(f"URL                     http://127.0.0.1:{args.port}/")
    server=ThreadingHTTPServer(("127.0.0.1",args.port),make_handler(args.root,session,review_service,finalize_service))
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
    return 0

if __name__ == "__main__": raise SystemExit(main())
