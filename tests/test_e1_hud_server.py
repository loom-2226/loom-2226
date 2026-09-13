import json
import tempfile
import unittest
from pathlib import Path

from engineering.experience_one.e1_hud_server import load_live_hud_payload


class E1HUDServerTests(unittest.TestCase):
    def test_loads_campaign_read_only_projection(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state_path = root / "LOOM_STATE_V1.json"
            state_path.write_text(json.dumps({
                "state_id": "S1",
                "epoch_utc": "2226-08-22T09:45:17Z",
                "location_token": "NEPTUNE_SYSTEM",
                "ship": {"name": "WAYFARER", "remass_t": 236.6, "wet_mass_t": 1145.1},
            }), encoding="utf-8")
            before = state_path.read_bytes()
            payload = load_live_hud_payload(root)
            after = state_path.read_bytes()
            self.assertEqual(before, after)
            self.assertEqual(payload["campaign"]["location_token"], "NEPTUNE_SYSTEM")
            self.assertEqual(payload["browser_authority"], "PRESENTATION_ONLY")
            self.assertEqual(payload["execution_authority"], "ZERO")

    def test_missing_campaign_state_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(FileNotFoundError):
                load_live_hud_payload(Path(td))


if __name__ == "__main__":
    unittest.main()
