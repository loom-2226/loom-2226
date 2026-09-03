"""HTTP bridge for the Phase 5 GIS flight-planning session."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import json

from .flight_planning import GISFlightPlanningError, GISFlightPlanningSession


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, separators=(",", ":"), default=str) + "\n").encode("utf-8")


def planning_client_js() -> str:
    return Path(__file__).with_name("flight_planning.js").read_text(encoding="utf-8")


def install_flight_planning(gis_module: Any, session: GISFlightPlanningSession) -> None:
    """Install read-only planning endpoints and the Phase-5 browser controller."""
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
            elif path == "/flight-planning/cancel":
                state = session.cancel()
                handler.navigation_overlay_json = handler.flight_planning_base_overlay_json
            else:
                return self._send(404, "text/plain; charset=utf-8", b"not found")
            return _send_state(self, state)
        except (GISFlightPlanningError, ValueError, KeyError) as exc:
            return self._send(400, "application/json; charset=utf-8", _json_bytes({"error": str(exc)}))
        except Exception as exc:
            return self._send(500, "application/json; charset=utf-8", _json_bytes({"error": f"{type(exc).__name__}: {exc}"}))

    handler.do_GET = do_GET
    handler.do_POST = do_POST
    marker = "/* LOOM_PHASE5_FLIGHT_PLANNING */"
    if marker not in gis_module.CLIENT_JS:
        gis_module.CLIENT_JS += "\n" + marker + "\n" + planning_client_js() + "\n"
