"""HTTP bridge for GIS flight planning and Phase-6 campaign execution."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import json
import threading
import traceback
import uuid

from .flight_planning import GISFlightPlanningError, GISFlightPlanningSession


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, separators=(",", ":"), default=str) + "\n").encode("utf-8")


def planning_client_js() -> str:
    return Path(__file__).with_name("flight_planning.js").read_text(encoding="utf-8")


def install_flight_planning(gis_module: Any, session: GISFlightPlanningSession) -> None:
    handler = gis_module.SolarHandler
    handler.flight_planning_session = session
    handler.flight_planning_base_overlay_json = bytes(getattr(handler, "navigation_overlay_json", b"{}"))
    handler.flight_planning_job_lock = threading.Lock()
    handler.flight_planning_job = {"status": "IDLE", "job_id": None, "state": None, "error": None}
    old_get = handler.do_GET
    old_post = getattr(handler, "do_POST", None)

    def _send_json(self, value, status=200):
        return self._send(status, "application/json; charset=utf-8", _json_bytes(value))

    def _send_state(self, state, status=200):
        return _send_json(self, state.to_dict(), status=status)

    def _job_snapshot():
        with handler.flight_planning_job_lock:
            return dict(handler.flight_planning_job)

    def _set_job(**updates):
        with handler.flight_planning_job_lock:
            handler.flight_planning_job.update(updates)
            return dict(handler.flight_planning_job)

    def _run_discovery_job(job_id: str, destination: str, priority: str):
        try:
            state = handler.flight_planning_session.discover(destination, priority)
            _set_job(status="COMPLETE", job_id=job_id, state=state.to_dict(), error=None)
        except BaseException as exc:
            if isinstance(exc, SystemExit):
                code = getattr(exc, "code", None)
                detail = str(code) if code not in (None, "") else str(exc) or "legacy Navigator exited"
                message = f"Navigator acquisition exited: {detail}"
            else:
                message = f"{type(exc).__name__}: {exc}"
            print(f"FLIGHT PLAN ASYNC FAILURE · discover · {message}")
            traceback.print_exc()
            _set_job(status="ERROR", job_id=job_id, state=None, error=message)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/flight-planning.json":
            return _send_state(self, self.flight_planning_session.state())
        if path == "/flight-planning/status.json":
            return _send_json(self, _job_snapshot())
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
                destination = body.get("destination")
                priority = body.get("priority") or "BALANCED"
                prefer = str(self.headers.get("Prefer") or "").lower()
                if "respond-async" in prefer:
                    current = _job_snapshot()
                    if current.get("status") == "RUNNING":
                        return _send_json(self, current, status=409)
                    job_id = "fp-" + uuid.uuid4().hex[:12]
                    _set_job(status="RUNNING", job_id=job_id, state=None, error=None)
                    t = threading.Thread(
                        target=_run_discovery_job,
                        args=(job_id, destination, priority),
                        name=f"loom-flight-plan-{job_id}",
                        daemon=True,
                    )
                    t.start()
                    return _send_json(self, _job_snapshot(), status=202)
                state = session.discover(destination, priority)
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
            return _send_json(self, {"error": str(exc)}, status=400)
        except SystemExit as exc:
            code = getattr(exc, "code", None)
            detail = str(code) if code not in (None, "") else str(exc) or "legacy Navigator exited"
            print(f"FLIGHT PLAN SYSTEMEXIT · {path} · {detail}")
            return _send_json(self, {
                "error": f"Navigator acquisition exited: {detail}",
                "kind": "LEGACY_SYSTEM_EXIT",
                "path": path,
            }, status=502)
        except BaseException as exc:
            print(f"FLIGHT PLAN FAILURE · {path} · {type(exc).__name__}: {exc}")
            traceback.print_exc()
            return _send_json(self, {
                "error": f"{type(exc).__name__}: {exc}",
                "kind": "SERVER_FAILURE",
                "path": path,
            }, status=500)

    handler.do_GET = do_GET
    handler.do_POST = do_POST
    marker = "/* LOOM_PHASE5_FLIGHT_PLANNING */\n/* LOOM_PHASE6_CAMPAIGN_EXECUTION */"
    if "LOOM_PHASE5_FLIGHT_PLANNING" not in gis_module.CLIENT_JS:
        gis_module.CLIENT_JS += "\n" + marker + "\n" + planning_client_js() + "\n"
