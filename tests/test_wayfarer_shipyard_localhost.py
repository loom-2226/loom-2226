from __future__ import annotations

import http.client
import importlib.util
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "wayfarer_shipyard_localhost.py"
SPEC = importlib.util.spec_from_file_location("wayfarer_shipyard_localhost", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class WayfarerShipyardLocalhostTests(unittest.TestCase):
    def viewer(self, root: Path) -> Path:
        p = root / mod.DEFAULT_VIEWER
        p.write_text(
            "<html><body>WAYFARER SHIPYARD 3D REVIEW EVIDENCE ONLY "
            "CAND-5719E3F3251DE6E25FDF CAND-MUT-CB6ACB18C6768B2E0EF9</body></html>",
            encoding="utf-8",
        )
        return p

    def test_server_binds_loopback_only_and_serves_html(self):
        with tempfile.TemporaryDirectory() as td:
            viewer = self.viewer(Path(td))
            server = mod.make_server(viewer, 0)
            self.assertEqual(server.server_address[0], mod.HOST)
            port = server.server_address[1]
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                conn = http.client.HTTPConnection(mod.HOST, port, timeout=2)
                conn.request("GET", "/")
                resp = conn.getresponse()
                body = resp.read().decode("utf-8")
                self.assertEqual(resp.status, 200)
                self.assertTrue(resp.getheader("Content-Type").startswith("text/html"))
                self.assertEqual(resp.getheader("Cache-Control"), "no-store")
                self.assertIn("WAYFARER SHIPYARD 3D", body)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

    def test_unknown_path_is_404(self):
        with tempfile.TemporaryDirectory() as td:
            server = mod.make_server(self.viewer(Path(td)), 0)
            port = server.server_address[1]
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                conn = http.client.HTTPConnection(mod.HOST, port, timeout=2)
                conn.request("GET", "/nope")
                resp = conn.getresponse()
                resp.read()
                self.assertEqual(resp.status, 404)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

    def test_identity_check_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / mod.DEFAULT_VIEWER
            p.write_text("<html>wrong artifact</html>", encoding="utf-8")
            with self.assertRaises(mod.LocalOnlyServerError):
                mod.validate_viewer(p)


if __name__ == "__main__":
    unittest.main()
