#!/usr/bin/env python3
"""Local server for LOOM HUD qualification/live synthetic vision."""
from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import argparse
import json
import mimetypes
import secrets
import sqlite3

from loom.hud.earth_luna_scene_provider import (
    DEFAULT_EPOCH as EARTH_LUNA_DEFAULT_EPOCH,
    build_earth_luna_hud_scene,
)
from loom.hud.earth_moon_qualification import build_earth_moon_qualification
from loom.hud.engineering_state_payload import (
    attach_typed_engineering_payload,
    build_wayfarer_engineering_payload,
)
from loom.hud.flight_command_executor import execute_velocity_aligned_burn
from loom.hud.hud_family_selector import (
    live_qualification_selection_payload,
    rendezvous_selection_payload,
)
from loom.hud.intercept_qualification import solve_moon_intercept
from loom.hud.live_provider import load_live_flight_view, unavailable_live_payload
from loom.hud.maneuver_plan_executor import execute_maneuver_plan
from loom.hud.maneuver_plan_handoff import build_explicit_execution_plan_from_review
from loom.hud.maneuver_plan_review import validate_maneuver_plan_review
from loom.hud.orbital_sandbox import attach_orbital_state, initialize_earth_circular_orbit
from loom.hud.predicted_path import build_predicted_path
from loom.hud.realtime_flight_qualification import RealtimeFlightQualification
from loom.hud.rendezvous_qualification import solve_moon_rendezvous_feasibility
from loom.runtime import resolve_runtime_roots

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8767
DEFAULT_PAGE = "earth_moon_qualification.html"
LIVE_ENDPOINT = "/flight-view.json"
EARTH_MOON_ENDPOINT = "/earth-moon-qualification.json"
EARTH_LUNA_SCENE_ENDPOINT = "/earth-luna-scene.json"
REALTIME_ENDPOINT = "/qualification-flight.json"
TRAJECTORY_PREVIEW_ENDPOINT = "/qualification-flight/trajectory-preview.json"
PREDICTED_PATH_ENDPOINT = "/qualification-flight/predicted-path.json"
INTERCEPT_PREVIEW_ENDPOINT = "/qualification-flight/intercept-preview.json"
RENDEZVOUS_PREVIEW_ENDPOINT = "/qualification-flight/rendezvous-preview.json"
WAYFARER_ENGINEERING_ENDPOINT = "/wayfarer-engineering-state.json"
CONTROL_ENDPOINT = "/qualification-flight/control"
WAYFARER_GEOMETRY_ENDPOINT = "/wayfarer-geometry.json"
ASSET_PREFIX = "/qualification-assets/"


def demo_root() -> Path:
    return Path(__file__).resolve().parent / "demo"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def page_path(root: Path | None = None) -> Path:
    base = demo_root() if root is None else Path(root).resolve()
    return base / DEFAULT_PAGE


def validate_assets(root: Path | None = None) -> Path:
    page = page_path(root)
    if not page.is_file():
        raise FileNotFoundError(f"HUD qualification page missing: {page}")
    return page


def _compile_wayfarer_geometry(root: Path) -> dict:
    from wayfarer_geometry import compile_geometry
    seed = root / "geometry" / "wayfarer_geometry_seed.sql"
    if not seed.is_file():
        raise FileNotFoundError(f"Wayfarer geometry seed missing: {seed}")
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(seed.read_text(encoding="utf-8"))
        return compile_geometry(conn)
    finally:
        conn.close()


def _stamp_live_family(payload: dict) -> dict:
    stamped = dict(payload)
    stamped["hud_family_selection"] = live_qualification_selection_payload(stamped)
    return stamped


def _stamp_rendezvous_family(payload: dict) -> dict:
    stamped = dict(payload)
    stamped["hud_family_selection"] = rendezvous_selection_payload(stamped)
    return stamped


def _live_payload(session: RealtimeFlightQualification, *, advance: bool = True) -> dict:
    payload = session.snapshot(advance=advance)
    payload = attach_orbital_state(payload, session)
    payload = attach_typed_engineering_payload(payload)
    return _stamp_live_family(payload)


def make_handler(directory: Path, earth_luna_scene_provider=build_earth_luna_hud_scene):
    qualification_session: list[RealtimeFlightQualification | None] = [None]
    validated_reviews: dict[str, dict] = {}
    control_revision = [0]
    root = repo_root()

    def get_session() -> RealtimeFlightQualification:
        if qualification_session[0] is None:
            qualification_session[0] = RealtimeFlightQualification()
        return qualification_session[0]

    def invalidate_validated_reviews() -> None:
        control_revision[0] += 1
        validated_reviews.clear()

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

        def _asset(self, name: str):
            if "/" in name or "\\" in name or not name:
                self.send_error(404)
                return
            roots = resolve_runtime_roots()
            path = roots.data_root / "qualification" / "hud_assets" / name
            if not path.is_file():
                self.send_error(404, f"qualification asset missing: {name}")
                return
            content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            if path.suffix.lower() == ".glb":
                content_type = "model/gltf-binary"
            size = path.stat().st_size
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(size))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            with path.open("rb") as fh:
                while True:
                    chunk = fh.read(1024 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)

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
                    self._json({"contract":"LOOM_HUD_EARTH_MOON_QUALIFICATION_V2","status":"UNAVAILABLE","authority":"UNAVAILABLE","reason":str(exc)},503)
                return
            if parsed.path == EARTH_LUNA_SCENE_ENDPOINT:
                query = parse_qs(parsed.query)
                epoch = (query.get("epoch") or [EARTH_LUNA_DEFAULT_EPOCH])[0]
                try:
                    self._json(earth_luna_scene_provider(epoch_utc=epoch))
                except Exception as exc:
                    self._json({"contract":"LOOM_EARTH_LUNA_SCENE_V1","status":"UNAVAILABLE","authority":"UNAVAILABLE","reason":str(exc)},503)
                return
            if parsed.path == REALTIME_ENDPOINT:
                try:
                    self._json(_live_payload(get_session()))
                except Exception as exc:
                    self._json({"contract":"LOOM_HUD_REALTIME_FLIGHT_QUALIFICATION_V1","status":"UNAVAILABLE","authority":"UNAVAILABLE","reason":str(exc)},503)
                return
            if parsed.path == WAYFARER_ENGINEERING_ENDPOINT:
                try:
                    self._json(build_wayfarer_engineering_payload(epoch="QUALIFICATION_STATIC"))
                except Exception as exc:
                    self._json({"contract":"LOOM_HUD_WAYFARER_ENGINEERING_TYPED_PAYLOAD_V1","status":"UNAVAILABLE","authority":"UNAVAILABLE","reason":str(exc)},503)
                return
            if parsed.path == PREDICTED_PATH_ENDPOINT:
                query = parse_qs(parsed.query)
                try:
                    horizon_s = float((query.get("horizon_s") or ["21600"])[0])
                    sample_s = float((query.get("sample_s") or ["60"])[0])
                    self._json(build_predicted_path(get_session(), horizon_s=horizon_s, sample_s=sample_s))
                except Exception as exc:
                    self._json({"contract":"LOOM_PREDICTED_PATH_V1","status":"UNAVAILABLE","authority":"UNAVAILABLE","reason":str(exc)},503)
                return
            if parsed.path == TRAJECTORY_PREVIEW_ENDPOINT:
                query = parse_qs(parsed.query)
                try:
                    burn_s = float((query.get("burn_s") or ["600"])[0])
                    coast_s = float((query.get("coast_s") or ["21600"])[0])
                    mode = (query.get("mode") or ["CRUISE"])[0]
                    sample_s = float((query.get("sample_s") or ["60"])[0])
                    result = get_session().trajectory_preview(burn_s=burn_s, coast_s=coast_s, mode=mode, sample_s=sample_s)
                    if result.get("points"):
                        p = result["points"][-1]
                        from loom.hud.earth_moon_qualification import _state_from_jpl
                        _mp, mv, _src = _state_from_jpl(get_session().anchors, get_session().sim_epoch.fromisoformat(p["epoch_utc"].replace("Z", "+00:00")))
                        result["final"]["relative_speed_km_s"] = sum((float(p["wayfarer_velocity_earth_centered_km_s"][i])-float(mv[i]))**2 for i in range(3))**0.5
                    self._json(result)
                except Exception as exc:
                    self._json({"contract":"LOOM_HUD_TRAJECTORY_PREVIEW_QUALIFICATION_V1","status":"UNAVAILABLE","authority":"UNAVAILABLE","reason":str(exc)},503)
                return
            if parsed.path == INTERCEPT_PREVIEW_ENDPOINT:
                query = parse_qs(parsed.query)
                try:
                    max_time_s = float((query.get("max_time_s") or ["22200"])[0])
                    mode = (query.get("mode") or ["CRUISE"])[0]
                    sample_s = float((query.get("sample_s") or ["60"])[0])
                    self._json(solve_moon_intercept(get_session(), max_time_s=max_time_s, mode=mode, sample_s=sample_s))
                except Exception as exc:
                    self._json({"contract":"LOOM_HUD_INTERCEPT_PREVIEW_QUALIFICATION_V1","status":"UNAVAILABLE","authority":"UNAVAILABLE","reason":str(exc)},503)
                return
            if parsed.path == RENDEZVOUS_PREVIEW_ENDPOINT:
                query = parse_qs(parsed.query)
                try:
                    max_time_s = float((query.get("max_time_s") or ["22200"])[0])
                    mode = (query.get("mode") or ["CRUISE"])[0]
                    standoff_altitude_km = float((query.get("standoff_altitude_km") or ["1000"])[0])
                    sample_s = float((query.get("sample_s") or ["60"])[0])
                    result = solve_moon_rendezvous_feasibility(get_session(), max_time_s=max_time_s, mode=mode, standoff_altitude_km=standoff_altitude_km, sample_s=sample_s)
                    self._json(_stamp_rendezvous_family(result))
                except Exception as exc:
                    self._json({"contract":"LOOM_HUD_RENDEZVOUS_FEASIBILITY_QUALIFICATION_V1","status":"UNAVAILABLE","authority":"UNAVAILABLE","reason":str(exc)},503)
                return
            if parsed.path == WAYFARER_GEOMETRY_ENDPOINT:
                try:
                    self._json(_compile_wayfarer_geometry(root))
                except Exception as exc:
                    self._json({"status":"UNAVAILABLE","reason":str(exc)},503)
                return
            if parsed.path.startswith(ASSET_PREFIX):
                self._asset(parsed.path[len(ASSET_PREFIX):])
                return
            return super().do_GET()

        def do_POST(self):
            parsed = urlparse(self.path)
            if parsed.path != CONTROL_ENDPOINT:
                self.send_error(404)
                return
            try:
                length = int(self.headers.get("Content-Length") or "0")
                if length <= 0 or length > 16384:
                    raise ValueError("control request body size invalid")
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                action = str(payload.get("action") or "").upper()
                session = get_session()
                if action == "RESET_REALTIME":
                    invalidate_validated_reviews()
                    session.reset()
                    self._json(_live_payload(session, advance=False))
                    return
                if action == "TIME_SCALE":
                    invalidate_validated_reviews()
                    session.set_time_scale(float(payload["value"]))
                    self._json(_live_payload(session, advance=False))
                    return
                if action == "TORCH":
                    invalidate_validated_reviews()
                    session.set_torch(active=bool(payload.get("active")), mode=payload.get("mode"))
                    self._json(_live_payload(session, advance=False))
                    return
                if action == "INITIALIZE_EARTH_ORBIT":
                    invalidate_validated_reviews()
                    initialize_earth_circular_orbit(
                        session,
                        altitude_km=float(payload.get("altitude_km", 400.0)),
                        inclination_deg=float(payload.get("inclination_deg", 0.0)),
                    )
                    self._json(_live_payload(session, advance=False))
                    return
                if action == "VALIDATE_MANEUVER_PLAN_REVIEW":
                    invalidate_validated_reviews()
                    raw_plan = payload.get("plan") or {}
                    receipt = validate_maneuver_plan_review(session, raw_plan)
                    ticket = secrets.token_urlsafe(18)
                    validated_reviews[ticket] = {
                        "control_revision": control_revision[0],
                        "plan": raw_plan,
                    }
                    self._json({
                        "contract": "LOOM_HUD_MANEUVER_PLAN_REVIEW_RESPONSE_V1",
                        "receipt": receipt,
                        "execution_ticket": ticket,
                        "execution_available": True,
                        "control_revision": control_revision[0],
                    })
                    return
                if action == "EXECUTE_VALIDATED_MANEUVER_PLAN":
                    ticket = str(payload.get("execution_ticket") or "")
                    stored = validated_reviews.pop(ticket, None)
                    if stored is None:
                        raise ValueError("validated maneuver plan ticket is missing, stale, or already consumed")
                    if int(stored["control_revision"]) != control_revision[0]:
                        raise ValueError("validated maneuver plan is stale after a control-state change")
                    plan = build_explicit_execution_plan_from_review(session, stored["plan"])
                    receipt = execute_maneuver_plan(session, plan)
                    invalidate_validated_reviews()
                    self._json({
                        "contract": "LOOM_HUD_MANEUVER_PLAN_EXECUTION_RESPONSE_V1",
                        "receipt": receipt,
                        "live": _live_payload(session, advance=False),
                    })
                    return
                if action == "EXECUTE_VELOCITY_BURN":
                    invalidate_validated_reviews()
                    receipt = execute_velocity_aligned_burn(
                        session,
                        direction=payload.get("direction"),
                        duration_s=float(payload.get("duration_s", 5.0)),
                        torch_mode=str(payload.get("mode") or session.torch_mode),
                        requested_by="HUD_MANUAL_CONTROL",
                    )
                    self._json({
                        "contract": "LOOM_HUD_EXECUTION_RESPONSE_V1",
                        "receipt": receipt,
                        "live": _live_payload(session, advance=False),
                    })
                    return
                raise ValueError(f"unsupported qualification control action: {action}")
            except Exception as exc:
                self._json({"status":"REJECTED","reason":str(exc)},400)

    return HudHandler


def serve(*, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, root: Path | None = None) -> None:
    page = validate_assets(root)
    directory = page.parent
    handler = make_handler(directory)
    url = f"http://{host}:{port}/{page.name}"
    print(f"LOOM HUD: {url}")
    print(f"LIVE STATE: {LIVE_ENDPOINT} (READ ONLY / FAIL CLOSED)")
    print(f"EARTH-LUNA SCENE: {EARTH_LUNA_SCENE_ENDPOINT} (40 TARGETS / SHARED SPATIAL STATE / READ ONLY)")
    print(f"REALTIME QUALIFICATION: {REALTIME_ENDPOINT} (WALL-UTC SEEDED / NON-CAMPAIGN)")
    print(f"WAYFARER ENGINEERING: {WAYFARER_ENGINEERING_ENDPOINT} (TYPED PR96 / NON-CANON)")
    print(f"PREDICTED PATH: {PREDICTED_PATH_ENDPOINT} (CURRENT STATE / BALLISTIC / READ ONLY)")
    print(f"TRAJECTORY PREVIEW: {TRAJECTORY_PREVIEW_ENDPOINT} (READ ONLY / NO NAVIGATOR CLAIM)")
    print(f"INTERCEPT PREVIEW: {INTERCEPT_PREVIEW_ENDPOINT} (QUALIFICATION SEARCH / NO COMMIT)")
    print(f"RENDEZVOUS FEASIBILITY: {RENDEZVOUS_PREVIEW_ENDPOINT} (FINITE ATTITUDE ENVELOPE / NO COMMIT)")
    print(f"WAYFARER GEOMETRY: {WAYFARER_GEOMETRY_ENDPOINT} (IN-MEMORY COMPILE)")
    print(f"3D ASSETS: {ASSET_PREFIX} (LOCAL QUALIFICATION CACHE)")
    print("ORBITAL SANDBOX: INITIALIZE_EARTH_ORBIT (IN-MEMORY / NO CAMPAIGN WRITE)")
    print("MANEUVER PLAN REVIEW: VALIDATE_MANEUVER_PLAN_REVIEW (SERVER VALIDATION / NO EXECUTION / NO CAMPAIGN WRITE)")
    print("MANEUVER PLAN EXECUTION: EXECUTE_VALIDATED_MANEUVER_PLAN (ONE-TIME SERVER TICKET / LIVE QUALIFICATION STATE / NO CAMPAIGN WRITE)")
    print("FLIGHT EXECUTION: EXECUTE_VELOCITY_BURN (LIVE QUALIFICATION STATE / NO CAMPAIGN WRITE)")
    print("CAMPAIGN: WRITE NONE")
    with ThreadingHTTPServer((host, port), handler) as server:
        server.daemon_threads = True
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