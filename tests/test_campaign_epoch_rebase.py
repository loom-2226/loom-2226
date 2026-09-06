from __future__ import annotations

import gzip
import json
import tempfile
import unittest
from pathlib import Path

from loom_campaign_rebase import (
    SOURCE_SEED,
    TARGET_SEED,
    _canon,
    _sha,
    _stamp_state,
    rebase_campaign,
)


def write_history(path: Path, records):
    with open(path, "wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", compresslevel=9, mtime=0) as gz:
            for record in records:
                gz.write((json.dumps(record, separators=(",", ":")) + "\n").encode())


def record_payload(record):
    return {k: v for k, v in record.items() if k != "record_sha256"}


class CampaignEpochRebaseTest(unittest.TestCase):
    def test_rebase_preserves_duration_and_rebuilds_hashes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            s1 = _stamp_state({
                "schema":"LOOM_STATE_V1","revision":1,"epoch_utc":SOURCE_SEED,
                "location_token":"CERES","ship":{"remass_t":250.0,"wet_mass_t":1158.5},
                "last_flight":None,
            })
            s2_raw = json.loads(json.dumps(s1))
            s2_raw["epoch_utc"] = "2027-06-15T03:30:00Z"
            s2_raw["location_token"] = "MARS"
            s2_raw["revision"] = 2
            s2_raw["last_flight"] = {
                "flight_id":"F1","departure_state_id":s1["state_id"],
                "departure_epoch_utc":SOURCE_SEED,"arrival_epoch_utc":"2027-06-15T03:30:00Z"
            }
            s2 = _stamp_state(s2_raw)
            r1 = {
                "schema":"LOOM_CAMPAIGN_HISTORY_V1","record_number":1,"record_type":"CAMPAIGN_CREATED",
                "event_epoch_utc":SOURCE_SEED,"previous_record_sha256":None,
                "state_before_sha256":None,"state_after_sha256":s1["state_sha256"],
                "flight_id":None,"details":{},"state_after_snapshot":s1,
            }
            r1["record_sha256"] = _sha(record_payload(r1))
            r2 = {
                "schema":"LOOM_CAMPAIGN_HISTORY_V1","record_number":2,"record_type":"FLIGHT_ARRIVED",
                "event_epoch_utc":"2027-06-15T03:30:00Z","previous_record_sha256":r1["record_sha256"],
                "state_before_sha256":s1["state_sha256"],"state_after_sha256":s2["state_sha256"],
                "flight_id":"F1","details":{},"state_after_snapshot":s2,
            }
            r2["record_sha256"] = _sha(record_payload(r2))
            write_history(root / "LOOM_CAMPAIGN_HISTORY.jsonl.gz", [r1, r2])
            (root / "LOOM_STATE_V1.json").write_text(json.dumps(s2))

            dry = rebase_campaign(root)
            self.assertEqual(dry["status"], "DRY_RUN")
            self.assertEqual(dry["new_epoch_utc"], "2226-06-15T03:30:00Z")
            self.assertEqual(json.loads((root / "LOOM_STATE_V1.json").read_text())["epoch_utc"], "2027-06-15T03:30:00Z")

            out = rebase_campaign(root, apply=True)
            self.assertEqual(out["status"], "APPLIED")
            state = json.loads((root / "LOOM_STATE_V1.json").read_text())
            self.assertEqual(state["epoch_utc"], "2226-06-15T03:30:00Z")
            self.assertEqual(state["last_flight"]["departure_epoch_utc"], TARGET_SEED)
            self.assertNotEqual(state["state_id"], s2["state_id"])
            self.assertTrue(Path(out["backup_dir"]).is_dir())

            with gzip.open(root / "LOOM_CAMPAIGN_HISTORY.jsonl.gz", "rt") as fh:
                rows = [json.loads(line) for line in fh]
            self.assertEqual(rows[0]["event_epoch_utc"], TARGET_SEED)
            self.assertEqual(rows[1]["event_epoch_utc"], "2226-06-15T03:30:00Z")
            self.assertEqual(rows[1]["previous_record_sha256"], rows[0]["record_sha256"])
            self.assertEqual(rows[1]["state_after_snapshot"]["state_id"], state["state_id"])
            self.assertEqual(rows[1]["state_after_snapshot"]["last_flight"]["departure_state_id"], rows[0]["state_after_snapshot"]["state_id"])


if __name__ == "__main__":
    unittest.main()
