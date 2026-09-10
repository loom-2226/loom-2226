#!/usr/bin/env python3
"""Local server for LOOM HUD qualification/live synthetic vision."""
from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import argparse
import json
import mimetypes
import sqlite3

from loom.hud.earth_moon_qualification import build_earth_moon_qualification
from loom.hud.intercept_qualification import solve_moon_intercept
from loom.hud.live_provider import load_live_flight_view, unavailable_live_payload
from loom.hud.realtime_flight_qualification import RealtimeFlightQualification
from loom.runtime import resolve_runtime_roots

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8767
DEFAULT_PAGE = "earth_moon_qualification.html"
LIVE_ENDPOINT = "/flight-view.json"
EARTH_MOON_ENDPOINT = "/earth-moon-qualification.json"
REALTIME_ENDPOINT = "/qualification-flight.json"
TRAJECTORY_PREVIEW_ENDPOINT = "/qualification-flight/trajectory-preview.json"
INTERCEPT_PREVIEW_ENDPOINT = "/qualification-flight/intercept-preview.json"
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


def make_handler(directory: Path):
    qualification_session: list[RealtimeFlightQualification | None] = [None]
    root = repo_root()

    def get_session() -> RealtimeFlightQualification:
        if qualification_session[0] is None:
            qualification_session[0] = RealtimeFlightQualification()
        return qualification_session[0]

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
                self.send_error(404); return
            roots = resolve_runtime_roots()
            path = roots.data_root / "qualification" / "hud_assets" / name
            if not path.is_file():
                self.send_error(404, f"qualification asset missing: {name}"); return
            content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            if path.suffix.lower() == ".glb": content_type = "model/gltf-binary"
            size = path.stat().st_size
            self.send_response(200); self.send_header("Content-Type", content_type); self.send_header("Content-Length", str(size)); self.send_header("Cache-Control", "no-cache"); self.end_headers()
            with path.open("rb") as fh:
                while True:
                    chunk = fh.read(1024 * 1024)
                    if not chunk: break
                    self.wfile.write(chunk)

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == LIVE_ENDPOINT:
                try: self._json(load_live_flight_view())
                except Exception as exc: self._json(unavailable_live_payload(exc), 503)
                return
            if parsed.path == EARTH_MOON_ENDPOINT:
                query = parse_qs(parsed.query); epoch = (query.get("epoch") or ["2026-09-10T00:00:00Z"])[0]
                try:
                    days = int((query.get("days") or ["30"])[0]); self._json(build_earth_moon_qualification(epoch_utc=epoch, days=days))
                except Exception as exc: self._json({"contract":"LOOM_HUD_EARTH_MOON_QUALIFICATION_V2","status":"UNAVAILABLE","authority":"UNAVAILABLE","reason":str(exc)},503)
                return
            if parsed.path == REALTIME_ENDPOINT:
                try: self._json(get_session().snapshot())
                except Exception as exc: self._json({"contract":"LOOM_HUD_REALTIME_FLIGHT_QUALIFICATION_V1","status":"UNAVAILABLE","authority":"UNAVAILABLE","reason":str(exc)},503)
                return
            if parsed.path == TRAJECTORY_PREVIEW_ENDPOINT:
                query = parse_qs(parsed.query)
                try:
                    burn_s = float((query.get("burn_s") or ["600"])[0]); coast_s = float((query.get("coast_s") or ["21600"])[0]); mode = (query.get("mode") or ["CRUISE"])[0]; sample_s = float((query.get("sample_s") or ["60"])[0])
                    result = get_session().trajectory_preview(burn_s=burn_s, coast_s=coast_s, mode=mode, sample_s=sample_s)
                    if result.get("points"):
                        p = result["points"][-1]
                        moon_v = get_session().anchors
                        from loom.hud.earth_moon_qualification import _state_from_jpl
                        _mp, mv, _src = _state_from_jpl(get_session().anchors, get_session().sim_epoch.fromisoformat(p["epoch_utc"].replace("Z", "+00:00")))
                        result["final"]["relative_speed_km_s"] = sum((float(p["wayfarer_velocity_earth_centered_km_s"][i])-float(mv[i]))**2 for i in range(3))**0.5
                    self._json(result)
                except Exception as exc: self._json({"contract":"LOOM_HUD_TRAJECTORY_PREVIEW_QUALIFICATION_V1","status":"UNAVAILABLE","authority":"UNAVAILABLE","reason":str(exc)},503)
                return
            if parsed.path == INTERCEPT_PREVIEW_ENDPOINT:
                query = parse_qs(parsed.query)
                try:
                    max_time_s = float((query.get("max_time_s") or ["22200"])[0]); mode = (query.get("mode") or ["CRUISE"])[0]; sample_s = float((query.get("sample_s") or ["60"])[0])
                    self._json(solve_moon_intercept(get_session(), max_time_s=max_time_s, mode=mode, sample_s=sample_s))
                except Exception as exc: self._json({"contract":"LOOM_HUD_INTERCEPT_PREVIEW_QUALIFICATION_V1","status":"UNAVAILABLE","authority":"UNAVAILABLE","reason":str(exc)},503)
                return
            if parsed.path == WAYFARER_GEOMETRY_ENDPOINT:
                try: self._json(_compile_wayfarer_geometry(root))
                except Exception as exc: self._json({"status":"UNAVAILABLE","reason":str(exc)},503)
                return
            if parsed.path.startswith(ASSET_PREFIX): self._asset(parsed.path[len(ASSET_PREFIX):]); return
            return super().do_GET()

        def do_POST(self):
            parsed = urlparse(self.path)
            if parsed.path != CONTROL_ENDPOINT: self.send_error(404); return
            try:
                length = int(self.headers.get("Content-Length") or "0")
                if length <= 0 or length > 16384: raise ValueError("control request body size invalid")
                payload = json.loads(self.rfile.read(length).decode("utf-8")); action = str(payload.get("action") or "").upper(); session = get_session()
                if action == "RESET_REALTIME": result = session.reset()
                elif action == "TIME_SCALE": result = session.set_time_scale(float(payload["value"]))
                elif action == "TORCH": result = session.set_torch(active=bool(payload.get("active")), mode=payload.get("mode"))
                else: raise ValueError(f"unsupported qualification control action: {action}")
                self._json(result)
            except Exception as exc: self._json({"status":"REJECTED","reason":str(exc)},400)

    return HudHandler


def serve(*, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, root: Path | None = None) -> None:
    page = validate_assets(root); directory = page.parent; handler = make_handler(directory); url = f"http://{host}:{port}/{page.name}"
    print(f"LOOM HUD: {url}"); print(f"LIVE STATE: {LIVE_ENDPOINT} (READ ONLY / FAIL CLOSED)"); print(f"REALTIME QUALIFICATION: {REALTIME_ENDPOINT} (WALL-UTC SEEDED / NON-CAMPAIGN)"); print(f"TRAJECTORY PREVIEW: {TRAJECTORY_PREVIEW_ENDPOINT} (READ ONLY / NO NAVIGATOR CLAIM)"); print(f"INTERCEPT PREVIEW: {INTERCEPT_PREVIEW_ENDPOINT} (QUALIFICATION SEARCH / NO COMMIT)"); print(f"WAYFARER GEOMETRY: {WAYFARER_GEOMETRY_ENDPOINT} (IN-MEMORY COMPILE)"); print(f"3D ASSETS: {ASSET_PREFIX} (LOCAL QUALIFICATION CACHE)"); print("CAMPAIGN: WRITE NONE")
    with ThreadingHTTPServer((host, port), handler) as server:
        server.daemon_threads = True; server.serve_forever()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Serve the LOOM HUD on localhost"); parser.add_argument("--host", default=DEFAULT_HOST); parser.add_argument("--port", type=int, default=DEFAULT_PORT); return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if not (1 <= args.port <= 65535): raise SystemExit("HUD port must be in 1..65535")
    try: serve(host=args.host, port=args.port)
    except KeyboardInterrupt: print("\nLOOM HUD stopped.")
    return 0

if __name__ == "__main__": raise SystemExit(main())
