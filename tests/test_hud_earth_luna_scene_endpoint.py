import json
import shutil
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen

from loom.application.contracts import SpatialState
from loom.hud import server
from loom.hud.earth_luna_scene_provider import (
    DEFAULT_EPOCH,
    GEOMETRY_FILENAME,
    build_earth_luna_hud_scene,
)


class HudEarthLunaSceneTests(unittest.TestCase):
    def test_provider_builds_governed_40_target_scene_without_owning_state(self):
        repo = server.repo_root()
        source_world = repo / "data" / "LOOM_2226.sqlite3"
        self.assertTrue(source_world.is_file())

        with tempfile.TemporaryDirectory() as tmp:
            data_root = Path(tmp)
            shutil.copy2(source_world, data_root / "LOOM_2226.sqlite3")

            def body_state(entity_id: str, epoch_utc: str) -> SpatialState:
                positions = {
                    "EA": (0.0, 0.0, 0.0),
                    "LU": (384400.0, 0.0, 0.0),
                }
                return SpatialState(
                    entity_id=entity_id,
                    epoch_utc=epoch_utc,
                    reference_frame="J2000/ECLIPTIC",
                    position_km=positions[entity_id],
                    velocity_km_s=(0.0, 0.0, 0.0),
                    provenance={"test": "injected shared-state seam"},
                    navigation_grade=False,
                )

            scene = build_earth_luna_hud_scene(
                epoch_utc=DEFAULT_EPOCH,
                app_root=repo,
                data_root=data_root,
                body_state_resolver=body_state,
            )

            self.assertEqual(scene["contract"], "LOOM_EARTH_LUNA_SCENE_V1")
            self.assertEqual(scene["target_count"], 40)
            self.assertEqual(len(scene["facilities"]), 31)
            self.assertEqual(len(scene["standard_orbits"]), 9)
            self.assertEqual(scene["state_authority"], "SHARED_SPATIAL_NAVIGATION_SERVICES")
            self.assertEqual(scene["geometry_authority"], "VISUALIZATION_ONLY_FOR_PROXIES")
            self.assertTrue((data_root / GEOMETRY_FILENAME).is_file())

    def test_live_hud_endpoint_passes_epoch_to_scene_provider(self):
        calls = []

        def fake_provider(*, epoch_utc: str):
            calls.append(epoch_utc)
            return {
                "contract": "LOOM_EARTH_LUNA_SCENE_V1",
                "epoch_utc": epoch_utc,
                "target_count": 40,
                "facilities": [],
                "standard_orbits": [],
            }

        with tempfile.TemporaryDirectory() as tmp:
            handler = server.make_handler(Path(tmp), earth_luna_scene_provider=fake_provider)
            httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            try:
                epoch = "2226-08-29T05:00:00Z"
                url = f"http://127.0.0.1:{httpd.server_port}{server.EARTH_LUNA_SCENE_ENDPOINT}?epoch={epoch}"
                with urlopen(url, timeout=5) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                self.assertEqual(response.status, 200)
                self.assertEqual(payload["contract"], "LOOM_EARTH_LUNA_SCENE_V1")
                self.assertEqual(payload["target_count"], 40)
                self.assertEqual(calls, [epoch])
            finally:
                httpd.shutdown()
                httpd.server_close()
                thread.join(timeout=5)

    def test_scene_endpoint_is_distinct_from_2026_qualification_endpoint(self):
        self.assertEqual(server.EARTH_LUNA_SCENE_ENDPOINT, "/earth-luna-scene.json")
        self.assertNotEqual(server.EARTH_LUNA_SCENE_ENDPOINT, server.EARTH_MOON_ENDPOINT)
        self.assertEqual(DEFAULT_EPOCH, "2226-08-29T05:00:00Z")


if __name__ == "__main__":
    unittest.main()
