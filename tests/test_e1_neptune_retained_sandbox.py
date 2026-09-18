import json
import tempfile
import unittest
from pathlib import Path

from engineering.experience_one.qualification.e1_neptune_retained_sandbox import (
    validate_retained_sandbox,
)


class E1NeptuneRetainedSandboxTests(unittest.TestCase):
    def test_validates_only_passed_neptune_sandbox(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "LOOM_STATE_V1.json").write_text(json.dumps({
                "state_id": "S000002-test",
                "epoch_utc": "2226-08-22T09:45:17Z",
                "location_token": "NEPTUNE_SYSTEM",
                "ship": {"remass_t": 236.6, "wet_mass_t": 1145.1},
            }), encoding="utf-8")
            result = {
                "qualification_pass": True,
                "real_campaign_unchanged_pass": True,
                "restart_destination_pass": True,
                "restart_state_id": "S000002-test",
                "restart_location": "NEPTUNE_SYSTEM",
            }
            summary = validate_retained_sandbox(root, result)
            self.assertEqual(summary["location_token"], "NEPTUNE_SYSTEM")
            self.assertEqual(summary["state_id"], "S000002-test")
            self.assertEqual(summary["authority"], "QUALIFIED_DISPOSABLE_CAMPAIGN_COPY")

    def test_rejects_unpassed_qualification(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "LOOM_STATE_V1.json").write_text(json.dumps({
                "state_id": "S1",
                "epoch_utc": "2226-08-22T01:32:00Z",
                "location_token": "CERES",
                "ship": {},
            }), encoding="utf-8")
            with self.assertRaises(RuntimeError):
                validate_retained_sandbox(root, {"qualification_pass": False})

    def test_rejects_state_result_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "LOOM_STATE_V1.json").write_text(json.dumps({
                "state_id": "S-WRONG",
                "epoch_utc": "2226-08-22T09:45:17Z",
                "location_token": "NEPTUNE_SYSTEM",
                "ship": {},
            }), encoding="utf-8")
            result = {
                "qualification_pass": True,
                "real_campaign_unchanged_pass": True,
                "restart_destination_pass": True,
                "restart_state_id": "S-EXPECTED",
                "restart_location": "NEPTUNE_SYSTEM",
            }
            with self.assertRaises(RuntimeError):
                validate_retained_sandbox(root, result)


if __name__ == "__main__":
    unittest.main()
