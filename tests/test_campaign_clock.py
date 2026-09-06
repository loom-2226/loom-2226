from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from loom.campaign.clock import (
    CampaignClockError,
    LegacyCampaignClockService,
    clock_from_state,
    is_stamp_current,
    validate_clock_advance,
)


def _state(rev=9, epoch="2226-08-22T14:24:14Z", state_id="S000009"):
    return {
        "state_id": state_id,
        "revision": rev,
        "epoch_utc": epoch,
        "location_token": "CERES",
        "ship": {"remass_t": 238.0},
        "last_flight": {"flight_id": "flight-1"},
    }


class CampaignClockTest(unittest.TestCase):
    def test_clock_from_state_uses_legacy_campaign_identity_without_schema_write(self):
        clock = clock_from_state(_state())
        self.assertEqual(clock.campaign_id, "LOOM_CAMPAIGN_V1")
        self.assertEqual(clock.revision, 9)
        self.assertEqual(clock.last_transition_id, "flight-1")
        self.assertEqual(clock.payload["authority"], "CAMPAIGN_JSON_HISTORY")

    def test_service_reads_authoritative_json_without_mutating_it(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / "LOOM_STATE_V1.json"
            original = json.dumps(_state(), sort_keys=True).encode("utf-8")
            path.write_bytes(original)
            clock = LegacyCampaignClockService(root).now()
            self.assertEqual(clock.epoch_utc, "2226-08-22T14:24:14Z")
            self.assertEqual(path.read_bytes(), original)

    def test_transition_may_hold_or_advance_time_but_never_reverse(self):
        before = clock_from_state(_state(9, "2226-08-22T14:24:14Z", "S9"))
        same_time = clock_from_state(_state(10, "2226-08-22T14:24:14Z", "S10"))
        later = clock_from_state(_state(10, "2226-08-22T15:24:14Z", "S10"))
        validate_clock_advance(before, same_time)
        validate_clock_advance(before, later)
        backward = clock_from_state(_state(10, "2226-08-22T13:24:14Z", "S10"))
        with self.assertRaisesRegex(CampaignClockError, "cannot move backward"):
            validate_clock_advance(before, backward)

    def test_revision_must_advance_exactly_one(self):
        before = clock_from_state(_state(9))
        after = clock_from_state(_state(11, "2226-08-23T00:00:00Z", "S11"))
        with self.assertRaisesRegex(CampaignClockError, "exactly one"):
            validate_clock_advance(before, after)

    def test_solution_stamp_current_requires_revision_and_epoch(self):
        clock = clock_from_state(_state())
        self.assertTrue(is_stamp_current(clock, campaign_revision=9, solution_epoch=clock.epoch_utc))
        self.assertFalse(is_stamp_current(clock, campaign_revision=8, solution_epoch=clock.epoch_utc))
        self.assertFalse(is_stamp_current(clock, campaign_revision=9, solution_epoch="2226-08-22T14:24:15Z"))

    def test_assert_current_detects_stale_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / "LOOM_STATE_V1.json"
            path.write_text(json.dumps(_state()), encoding="utf-8")
            service = LegacyCampaignClockService(root)
            expected = service.now()
            path.write_text(json.dumps(_state(10, "2226-08-22T15:24:14Z", "S10")), encoding="utf-8")
            with self.assertRaisesRegex(CampaignClockError, "changed"):
                service.assert_current(expected)


if __name__ == "__main__":
    unittest.main()
