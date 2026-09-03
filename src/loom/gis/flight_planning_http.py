"""HTTP bridge for GIS flight planning and Phase-6 campaign execution."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import json
import traceback

from .flight_planning import GISFlightPlanningError, GISFlightPlanningSession


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, separators=(",", ":"), default=str) + "\n").encode("utf-8")


def planning_client_js() -> str:
    return Path(__file__).with_name("flight_planning.js").read_text(encoding="utf-8")


def install_flight_planning(gis_module: Any, session: GISFlightPlanningSession) -> None:
    handler = gis_module.SolarHandler
    handler.flight_planning_session = session
    handler.flight_planning_base_overlay_json = bytes(getattr(handler, "navigation_overlay_json", b"{}"))
    old_get = handler.do_GET
    old_post = getattr(handler, "do_POST", None)

    def _send_state(self, state, status=200):
        self._send(status, "application/json; charset=utf-8", _json_bytes(state.to_dict()))

    def do_GET(self):
        if urlparse(self.path).path == "/flight-planning.json":
            return _send_state(self, self.flight_planning_session.state())
        return old_get(self)

    def do_POST(self):
        path = urlparse(self.path).path
        if not path.startswith("/flight-planning/"):
            if callable(old_post):
                return old_post(self)
            return self._send(404, "text/plain; charset=utf-8", b"not found")
        try:
            n = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(n) if n > 0 else b"{}"
            body = json.loads(raw.decode("utf-8") or "{}")
            if not isinstance(body, dict):
                raise GISFlightPlanningError("request body must be a JSON object")
            session = self.flight_planning_session
            if path == "/flight-planning/discover":
                state = session.discover(body.get("destination"), body.get("priority") or "BALANCED")
            elif path == "/flight-planning/preview":
                state = session.preview(body.get("route_id"))
                if state.preview_overlay is not None:
                    handler.navigation_overlay_json = _json_bytes(state.preview_overlay)
            elif path == "/flight-planning/commit":
                state = session.commit(body.get("route_id"))
                if state.preview_overlay is not None:
                    handler.navigation_overlay_json = _json_bytes(state.preview_overlay)
            elif path == "/flight-planning/execute":
                state = session.execute()
                executed = state.last_execution or {}
                overlay = executed.get("historical_overlay") if isinstance(executed, dict) else None
                handler.navigation_overlay_json = _json_bytes(overlay) if overlay else handler.flight_planning_base_overlay_json
            elif path == "/flight-planning/cancel":
                state = session.cancel()
                handler.navigation_overlay_json = handler.flight_planning_base_overlay_json
            else:
                return self._send(404, "text/plain; charset=utf-8", b"not found")
            return _send_state(self, state)
        except (GISFlightPlanningError, ValueError, KeyError) as exc:
            return self._send(400, "application/json; charset=utf-8", _json_bytes({"error": str(exc)}))
        except SystemExit as exc:
            # Frozen Sequence-H still contains CLI-era acquisition paths that may
            # raise SystemExit. In a ThreadingHTTPServer request thread that used
            # to terminate the request without a response, which Chrome surfaced
            # only as "Failed to fetch". Convert it to a diagnostic HTTP response
            # while keeping the GIS server alive.
            code = getattr(exc, "code", None)
            detail = str(code) if code not in (None, "") else str(exc) or "legacy Navigator exited"
            print(f"FLIGHT PLAN SYSTEMEXIT · {path} · {detail}")
            return self._send(502, "application/json; charset=utf-8", _json_bytes({
                "error": f"Navigator acquisition exited: {detail}",
                "kind": "LEGACY_SYSTEM_EXIT",
                "path": path,
            }))
        except BaseException as exc:
            # Do not allow any legacy request-thread failure to disappear as a
            # browser network error. KeyboardInterrupt remains meaningful only on
            # the main server thread; here it is safer to report and preserve the
            # running local GIS for diagnosis.
            print(f"FLIGHT PLAN FAILURE · {path} · {type(exc).__name__}: {exc}")
            traceback.print_exc()
            return self._send(500, "application/json; charset=utf-8", _json_bytes({
                "error": f"{type(exc).__name__}: {exc}",
                "kind": "SERVER_FAILURE",
                "path": path,
            }))

    handler.do_GET = do_GET
    handler.do_POST = do_POST
    # Keep the Phase-5 marker for backward qualification while adding the Gate-C marker.
    marker = "/* LOOM_PHASE5_FLIGHT_PLANNING */\n/* LOOM_PHASE6_CAMPAIGN_EXECUTION */"
    if "LOOM_PHASE5_FLIGHT_PLANNING" not in gis_module.CLIENT_JS:
        gis_module.CLIENT_JS += "\n" + marker + "\n" + planning_client_js() + "\n"
