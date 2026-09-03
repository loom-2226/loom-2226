"""HTTP bridge for GIS flight planning and Phase-6 campaign execution."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, parse_qs
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
    runtime_root = Path(getattr(session.context, "runtime_root", None) or Path.cwd())
    handler.flight_planning_log_path = runtime_root / "LOOM_PHASE6_HTTP.log"
    old_get = handler.do_GET
    old_post = getattr(handler, "do_POST", None)

    def _log(event: str, **fields: Any) -> None:
        row = {
            "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "event": event,
            **fields,
        }
        try:
            handler.flight_planning_log_path.parent.mkdir(parents=True, exist_ok=True)
            with handler.flight_planning_log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, separators=(",", ":"), default=str) + "\n")
        except Exception:
            pass

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
        _log("discover_job_start", job_id=job_id, destination=destination, priority=priority)
        try:
            state = handler.flight_planning_session.discover(destination, priority)
            _set_job(status="COMPLETE", job_id=job_id, state=state.to_dict(), error=None)
            _log("discover_job_complete", job_id=job_id, candidates=len(state.candidates))
        except BaseException as exc:
            if isinstance(exc, SystemExit):
                code = getattr(exc, "code", None)
                detail = str(code) if code not in (None, "") else str(exc) or "legacy Navigator exited"
                message = f"Navigator acquisition exited: {detail}"
            else:
                message = f"{type(exc).__name__}: {exc}"
            _log("discover_job_error", job_id=job_id, error=message, traceback=traceback.format_exc())
            _set_job(status="ERROR", job_id=job_id, state=None, error=message)

    def _start_discovery(destination: str, priority: str):
        current = _job_snapshot()
        if current.get("status") == "RUNNING":
            return current, 409
        job_id = "fp-" + uuid.uuid4().hex[:12]
        _set_job(status="RUNNING", job_id=job_id, state=None, error=None)
        _log("discover_accepted", job_id=job_id, destination=destination, priority=priority)
        t = threading.Thread(
            target=_run_discovery_job,
            args=(job_id, destination, priority),
            name=f"loom-flight-plan-{job_id}",
            daemon=True,
        )
        t.start()
        return _job_snapshot(), 202

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        _log("http_get", path=path)
        if path == "/flight-planning.json":
            return _send_state(self, self.flight_planning_session.state())
        if path == "/flight-planning/status.json":
            return _send_json(self, _job_snapshot())
        if path == "/flight-planning/health.json":
            return _send_json(self, {
                "ok": True,
                "planning": self.flight_planning_session.state().to_dict(),
                "job": _job_snapshot(),
                "log_path": str(handler.flight_planning_log_path),
            })
        if path == "/flight-planning/discover.json":
            q = parse_qs(parsed.query)
            destination = (q.get("destination") or [""])[0]
            priority = (q.get("priority") or ["BALANCED"])[0]
            if not destination:
                return _send_json(self, {"error": "destination is required"}, status=400)
            state, status = _start_discovery(destination, priority)
            return _send_json(self, state, status=status)
        return old_get(self)

    def do_POST(self):
        path = urlparse(self.path).path
        _log("http_post", path=path, content_length=self.headers.get("Content-Length"), prefer=self.headers.get("Prefer"))
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
                    state, status = _start_discovery(destination, priority)
                    return _send_json(self, state, status=status)
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
            _log("http_post_complete", path=path)
            return _send_state(self, state)
        except (GISFlightPlanningError, ValueError, KeyError) as exc:
            _log("http_post_error", path=path, error=str(exc))
            return _send_json(self, {"error": str(exc)}, status=400)
        except SystemExit as exc:
            code = getattr(exc, "code", None)
            detail = str(code) if code not in (None, "") else str(exc) or "legacy Navigator exited"
            _log("http_post_systemexit", path=path, error=detail)
            return _send_json(self, {
                "error": f"Navigator acquisition exited: {detail}",
                "kind": "LEGACY_SYSTEM_EXIT",
                "path": path,
            }, status=502)
        except BaseException as exc:
            _log("http_post_failure", path=path, error=f"{type(exc).__name__}: {exc}", traceback=traceback.format_exc())
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
