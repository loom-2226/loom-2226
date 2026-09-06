from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import loom_gis
from loom.runtime import RuntimeRoots


class GISStageCCampaignEpochTest(unittest.TestCase):
    def _roots(self, root: Path) -> RuntimeRoots:
        app = root / "runtime"
        data = root / "data"
        campaign = root / "campaign"
        app.mkdir(); data.mkdir(); campaign.mkdir()
        return RuntimeRoots(
            app_root=app,
            data_root=data,
            campaign_root=campaign,
            app_source="test",
            data_source="test",
            campaign_source="test",
        )

    def test_live_scene_defaults_to_canonical_campaign_clock(self):
        with tempfile.TemporaryDirectory() as td:
            roots = self._roots(Path(td))
            (roots.campaign_root / "LOOM_STATE_V1.json").write_text(json.dumps({
                "revision": 9,
                "epoch_utc": "2226-06-15T09:59:34.811247Z",
                "state_id": "S9",
                "last_flight": {"flight_id": "F9"},
            }), encoding="utf-8")
            argv, epoch, source = loom_gis._bind_live_scene_epoch(["--port", "8766"], roots)
            self.assertEqual(epoch, "2226-06-15T09:59:34.811247Z")
            self.assertEqual(source, "CAMPAIGN_CLOCK")
            self.assertEqual(argv[:2], ["--epoch", "2226-06-15T09:59:34.811247Z"])

    def test_explicit_epoch_is_query_cursor_and_not_replaced(self):
        with tempfile.TemporaryDirectory() as td:
            roots = self._roots(Path(td))
            argv, epoch, source = loom_gis._bind_live_scene_epoch(
                ["--epoch", "2200-01-01T00:00:00Z", "--port", "9000"], roots
            )
            self.assertEqual(epoch, "2200-01-01T00:00:00Z")
            self.assertEqual(source, "EXPLICIT_QUERY")
            self.assertEqual(argv, ["--epoch", "2200-01-01T00:00:00Z", "--port", "9000"])


if __name__ == "__main__":
    unittest.main()
