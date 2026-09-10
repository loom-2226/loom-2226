from __future__ import annotations

import json
import threading
from http.server import ThreadingHTTPServer
from urllib.request import urlopen

from loom.hud import server
from loom.hud.wayfarer_engineering_state import ENGINEERING_SOURCE_COMMIT


def test_wayfarer_engineering_endpoint_serves_pinned_noncanon_state():
    handler = server.make_handler(server.demo_root())
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = httpd.server_address
        with urlopen(f"http://{host}:{port}{server.WAYFARER_ENGINEERING_ENDPOINT}", timeout=5.0) as response:
            assert response.status == 200
            payload = json.loads(response.read().decode("utf-8"))
        assert payload["contract"] == "LOOM_HUD_WAYFARER_ENGINEERING_HANDOFF_V1"
        assert payload["source"]["commit"] == ENGINEERING_SOURCE_COMMIT
        assert payload["authority"]["canon"] is False
        assert payload["dispatch"]["routine_optimizer_may_consume_protected_water"] is False
        assert payload["feedstock"]["certified_species"] == []
        assert payload["power_thermal"]["qualification_status"] == "OPEN_BOUNDED"
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5.0)
