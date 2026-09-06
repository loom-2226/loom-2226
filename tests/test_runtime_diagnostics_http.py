from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import hashlib
import json
import unittest

from loom.gis.flight_planning_http import install_flight_planning


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


class State:
    def to_dict(self):
        return {"status": "IDLE"}


class Session:
    def __init__(self, root):
        self.context = SimpleNamespace(runtime_root=str(root))
        self.service = SimpleNamespace(core=SimpleNamespace(CIVSTATE_TOKEN_ENTITY={}))
    def state(self):
        return State()
    def bind_trace(self, trace, trace_id):
        self.trace = trace
        self.trace_id = trace_id


class BaseHandler:
    navigation_overlay_json = b"{}"
    def do_GET(self):
        self.fell_through = True
    def _send(self, status, content_type, body):
        self.response = (status, content_type, body)
        return self.response


class DiagnosticsHTTPTest(unittest.TestCase):
    def _module(self):
        class Handler(BaseHandler):
            pass
        return SimpleNamespace(SolarHandler=Handler, CLIENT_JS="")

    def test_localhost_diagnostics_does_not_append_runtime_logs_or_trace(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            module = self._module()
            install_flight_planning(module, Session(root))
            handler = module.SolarHandler()
            handler.path = "/diagnostics"
            handler.client_address = ("127.0.0.1", 12345)
            http_log = module.SolarHandler.flight_planning_log_path
            trace_log = module.SolarHandler.runtime_trace.path
            latest = root / "LOOM_PHASE6_LATEST.txt"
            before = {p: (p.stat().st_size, digest(p)) for p in (http_log, trace_log, latest)}
            handler.do_GET()
            after = {p: (p.stat().st_size, digest(p)) for p in (http_log, trace_log, latest)}
            self.assertEqual(before, after)
            self.assertEqual(handler.response[0], 200)
            payload = json.loads(handler.response[2])
            self.assertEqual(payload["contract"], "LOOM_RUNTIME_DIAGNOSTICS_V1")

    def test_remote_diagnostics_is_rejected_without_writing(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            module = self._module()
            install_flight_planning(module, Session(root))
            handler = module.SolarHandler()
            handler.path = "/diagnostics"
            handler.client_address = ("192.0.2.25", 12345)
            http_log = module.SolarHandler.flight_planning_log_path
            trace_log = module.SolarHandler.runtime_trace.path
            before = {p: (p.stat().st_size, digest(p)) for p in (http_log, trace_log)}
            handler.do_GET()
            after = {p: (p.stat().st_size, digest(p)) for p in (http_log, trace_log)}
            self.assertEqual(before, after)
            self.assertEqual(handler.response[0], 403)
            self.assertIn("localhost-only", json.loads(handler.response[2])["error"])


if __name__ == "__main__":
    unittest.main()
