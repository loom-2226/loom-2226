from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import loom_clock


class LoomClockCliTest(unittest.TestCase):
    def test_cli_reports_authoritative_clock_read_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state = {
                "state_id": "S9",
                "revision": 9,
                "epoch_utc": "2226-08-22T14:24:14Z",
                "location_token": "CERES",
                "ship": {"remass_t": 238.0},
                "last_flight": {"flight_id": "flight-1"},
            }
            path = root / "LOOM_STATE_V1.json"
            original = json.dumps(state, sort_keys=True).encode("utf-8")
            path.write_bytes(original)
            out = StringIO()
            with redirect_stdout(out):
                rc = loom_clock.main(["--campaign-root", str(root), "--json"])
            self.assertEqual(rc, 0)
            payload = json.loads(out.getvalue())
            self.assertEqual(payload["revision"], 9)
            self.assertEqual(payload["epoch_utc"], "2226-08-22T14:24:14Z")
            self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
