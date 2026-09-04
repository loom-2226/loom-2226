"""HTTP bridge for GIS flight planning and Phase-6 campaign execution."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Iterable
from urllib.parse import urlparse, parse_qs, urlencode
import json
import threading
import traceback
import uuid

from .flight_planning import GISFlightPlanningError, GISFlightPlanningSession


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, separators=(",", ":"), default=str) + "\n").encode("utf-8")


def planning_client_js() -> str:
    base = Path(__file__).with_name("flight_planning.js").read_text(encoding="utf-8")
    selection = Path(__file__).with_name("flight_planning_selection.js").read_text(encoding="utf-8")
    return base + "\n" + selection


def _canonical_navigation_endpoint(nav: Any, candidates: Iterable[str]) -> tuple[str | None, str | None]:
    """Resolve a GIS selection only against Navigator's declared endpoint registry.

    Mission normalization validates shape/aliases but does not prove that an arbitrary
    celestial body is a supported route endpoint.  The Navigator core's
    CIVSTATE_TOKEN_ENTITY mapping is the authoritative MVP endpoint registry.
    """
    registry = getattr(nav, "CIVSTATE_TOKEN_ENTITY", None)
    if not isinstance(registry, Mapping) or not registry:
        raise GISFlightPlanningError("Navigator endpoint registry is unavailable")

    token_lookup: dict[str, str] = {}
    entity_lookup: dict[str, str] = {}
    for raw_token, raw_entity in registry.items():
        token = str(raw_token or "").strip().upper()
        entity_id = str(raw_entity or "").strip().upper()
        if not token:
            continue
        token_lookup[token] = token
        if entity_id:
            entity_lookup[entity_id] = token

    for candidate in candidates:
        raw = str(candidate or "").strip()
        if not raw:
            continue
        key = raw.upper().replace(" ", "_")
        if key in token_lookup:
            return token_lookup[key], raw
        if key in entity_lookup:
            return entity_lookup[key], raw
    return None, None


def install_flight_planning(gis_module: Any, session: GISFlightPlanningSession) -> None:
    handler = gis_module.SolarHandler
    handler.flight_planning_session = session
    handler.flight_planning_base_overlay_json = bytes(getattr(handler, "navigation_overlay_json", b"{}"))
    handler.flight_planning_job_lock = threading.Lock()
    handler.flight_planning_job = {"status": "IDLE", "job_id": None, "state": None, "error": None}
    runtime_root = Path(getattr(session.context, "runtime_root", None) or Path.cwd())
    run_stamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    handler.flight_planning_log_path = runtime_root / f"LOOM_PHASE6_HTTP_{run_stamp}.log"
    latest_pointer = runtime_root / "LOOM_PHASE6_LATEST.txt"
    try:
        latest_pointer.write_text(
            f"HTTP_LOG={handler.flight_planning_log_path.name}\n",
            encoding="utf-8",
        )
    except Exception:
        pass
    old_get = handler.do_GET
    old_post = getattr(handler, "do_POST", None)

    def _log(event: str, **fields: Any) -> None:
        row = {"utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "event": event, **fields}
        try:
            handler.flight_planning_log_path.parent.mkdir(parents=True, exist_ok=True)
            with handler.flight_planning_log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, separators=(",", ":"), default=str) + "\n")
        except Exception:
            pass

    _log("flight_planning_installed", log_path=str(handler.flight_planning_log_path), runtime_root=str(runtime_root))

    def _send_json(self, value, status=200):
        return self._send(status, "application/json; charset=utf-8", _json_bytes(value))

    def _send_state(self, state, status=200):
        return _send_json(self, state.to_dict(), status=status)

    def _redirect(self, location: str, status: int = 303):
        body = ("redirecting to " + location + "\n").encode("utf-8")
        self.send_response(status)
        self.send_header("Location", location)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _job_snapshot():
        with handler.flight_planning_job_lock:
            return dict(handler.flight_planning_job)

    def _set_job(**updates):
        with handler.flight_planning_job_lock:
            handler.flight_planning_job.update(updates)
            return dict(handler.flight_planning_job)

    def _resolve_destination(entity: Any) -> dict[str, Any]:
        if not isinstance(entity, dict):
            raise GISFlightPlanningError("entity descriptor is required")
        display_name = str(entity.get("display_name") or entity.get("name") or entity.get("entity_id") or "SELECTION").strip()
        raw_candidates = [
            entity.get("navigation_token"),
            entity.get("route_token"),
            entity.get("navigator_token"),
            entity.get("canonical_token"),
            entity.get("body_token"),
            entity.get("name"),
            entity.get("display_name"),
            entity.get("parent_entity_id") if str(entity.get("entity_class") or "").upper() == "INFRASTRUCTURE" else None,
            entity.get("entity_id"),
        ]
        candidates: list[str] = []
        seen: set[str] = set()
        for value in raw_candidates:
            text = str(value or "").strip()
            if not text:
                continue
            variants = [text, text.upper().replace(" ", "_")]
            for variant in variants:
                if variant and variant not in seen:
                    seen.add(variant)
                    candidates.append(variant)

        nav_service = handler.flight_planning_session.service
        context = handler.flight_planning_session.context
        nav = nav_service._sequence_h(context)
        token, resolved_from = _canonical_navigation_endpoint(nav, candidates)

        if token is None:
            _log("destination_unavailable", entity_id=entity.get("entity_id"), display_name=display_name, candidates=candidates)
            return {
                "selectable": False,
                "route_token": None,
                "display_name": display_name,
                "entity_id": entity.get("entity_id"),
                "reason": "not a Navigator route endpoint",
                "authority": "NAVIGATOR_CIVSTATE_TOKEN_ENTITY",
            }

        if token == handler.flight_planning_session.origin:
            return {
                "selectable": False,
                "route_token": token,
                "display_name": display_name,
                "reason": "already at this location",
                "entity_id": entity.get("entity_id"),
                "authority": "NAVIGATOR_CIVSTATE_TOKEN_ENTITY",
            }

        return {
            "selectable": True,
            "route_token": token,
            "display_name": display_name,
            "entity_id": entity.get("entity_id"),
            "resolved_from": resolved_from,
            "authority": "NAVIGATOR_CIVSTATE_TOKEN_ENTITY",
        }

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
        t = threading.Thread(target=_run_discovery_job, args=(job_id, destination, priority), name=f"loom-flight-plan-{job_id}", daemon=True)
        t.start()
        return _job_snapshot(), 202

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        _log("http_get", path=path, query=parsed.query)
        if path == "/flight-planning.json":
            return _send_state(self, self.flight_planning_session.state())
        if path == "/flight-planning/status.json":
            return _send_json(self, _job_snapshot())
        if path == "/flight-planning/health.json":
            return _send_json(self, {"ok": True, "planning": self.flight_planning_session.state().to_dict(), "job": _job_snapshot(), "log_path": str(handler.flight_planning_log_path)})
        if path in ("/flight-planning/discover.json", "/flight-planning/discover-start"):
            q = parse_qs(parsed.query)
            destination = (q.get("destination") or [""])[0]
            priority = (q.get("priority") or ["BALANCED"])[0]
            if not destination:
                if path == "/flight-planning/discover-start":
                    return _redirect(self, "/?fp_error=destination_required")
                return _send_json(self, {"error": "destination is required"}, status=400)
            state, status = _start_discovery(destination, priority)
            if path == "/flight-planning/discover-start":
                if status == 202:
                    job_id = str(state.get("job_id") or "")
                    _log("discover_nav_redirect", job_id=job_id, destination=destination)
                    return _redirect(self, "/?" + urlencode({"fp_job": job_id, "fp_destination": destination}))
                job_id = str(state.get("job_id") or "")
                return _redirect(self, "/?" + urlencode({"fp_job": job_id, "fp_busy": "1"}))
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
            if path == "/flight-planning/resolve":
                capability = _resolve_destination(body.get("entity"))
                _log("destination_resolved", entity_id=capability.get("entity_id"), selectable=capability.get("selectable"), route_token=capability.get("route_token"))
                return _send_json(self, capability)
            if path == "/flight-planning/discover":
                state = session.discover(body.get("destination"), body.get("priority") or "BALANCED")
            elif path == "/flight-planning/preview":
                state = session.preview(body.get("route_id"))
                if state.preview_overlay is not None: handler.navigation_overlay_json = _json_bytes(state.preview_overlay)
            elif path == "/flight-planning/commit":
                state = session.commit(body.get("route_id"))
                if state.preview_overlay is not None: handler.navigation_overlay_json = _json_bytes(state.preview_overlay)
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
            return _send_json(self, {"error": f"Navigator acquisition exited: {detail}", "kind": "LEGACY_SYSTEM_EXIT", "path": path}, status=502)
        except BaseException as exc:
            _log("http_post_failure", path=path, error=f"{type(exc).__name__}: {exc}", traceback=traceback.format_exc())
            return _send_json(self, {"error": f"{type(exc).__name__}: {exc}", "kind": "SERVER_FAILURE", "path": path}, status=500)

    handler.do_GET = do_GET
    handler.do_POST = do_POST
    marker = "/* LOOM_PHASE5_FLIGHT_PLANNING */\n/* LOOM_PHASE6_CAMPAIGN_EXECUTION */"
    if "LOOM_PHASE5_FLIGHT_PLANNING" not in gis_module.CLIENT_JS:
        gis_module.CLIENT_JS += "\n" + marker + "\n" + planning_client_js() + "\n"
