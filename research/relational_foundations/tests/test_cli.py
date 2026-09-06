from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from research.relational_foundations.src import cli


class LoomRfCliTests(unittest.TestCase):
    def test_validate_passes_for_current_lane(self):
        self.assertEqual(cli.validate(), 0)

    def test_infrastructure_smoke_is_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.object(cli, "DEFAULT_OUTPUT", Path(td)):
                self.assertEqual(cli.infrastructure_smoke(), 0)
                payload = json.loads((Path(td) / "infrastructure_smoke.json").read_text())
                self.assertEqual(payload["kind"], "infrastructure_smoke_not_rqo1")
                self.assertEqual(payload["nodes"], 12)
                self.assertEqual(payload["edges"], 12)
                self.assertEqual(payload["degree_sum"], 24)


if __name__ == "__main__":
    unittest.main()
