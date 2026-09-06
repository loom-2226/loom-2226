from __future__ import annotations
import sqlite3
import tempfile
import unittest
from pathlib import Path
from loom.campaign.execution import CampaignFlightCommitV1
from loom.campaign.shadow_ledger import CampaignShadowLedger, CampaignShadowLedgerError, SHADOW_DB_NAME

class CampaignShadowLedgerTest(unittest.TestCase):
    def commit(self, **changes):
        values=dict(flight_id="F000001",state_before_id="S1",state_after_id="S2",revision_before=1,revision_after=2,origin="CERES",destination="MARS",departure_epoch_utc="2226-01-01T00:00:00Z",arrival_epoch_utc="2226-01-02T00:00:00Z",remass_before_t=250.0,remass_after_t=245.5,state_path="/campaign/LOOM_STATE_V1.json",history_path="/campaign/LOOM_CAMPAIGN_HISTORY.jsonl.gz",history_record_number=7,history_record_sha256="abc123",final_state={"state_id":"S2","revision":2,"location_token":"MARS"})
        values.update(changes); return CampaignFlightCommitV1(**values)

    def test_mirror_creates_named_shadow_db_and_reconciles(self):
        with tempfile.TemporaryDirectory() as td:
            ledger=CampaignShadowLedger(td); commit=self.commit(); ledger.mirror_commit(commit)
            self.assertEqual(ledger.path,Path(td).resolve()/SHADOW_DB_NAME); self.assertTrue(ledger.path.is_file()); self.assertEqual(ledger.reconcile_commit(commit)["status"],"MATCH")
            with sqlite3.connect(ledger.path) as conn:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM campaign_flight_commits").fetchone()[0],1)

    def test_identical_mirror_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            ledger=CampaignShadowLedger(td); commit=self.commit(); ledger.mirror_commit(commit); ledger.mirror_commit(commit)
            with sqlite3.connect(ledger.path) as conn:self.assertEqual(conn.execute("SELECT COUNT(*) FROM campaign_flight_commits").fetchone()[0],1)

    def test_conflicting_same_flight_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            ledger=CampaignShadowLedger(td); ledger.mirror_commit(self.commit())
            with self.assertRaises(CampaignShadowLedgerError):ledger.mirror_commit(self.commit(destination="VENUS"))

    def test_reconcile_reports_missing_without_creating_db(self):
        with tempfile.TemporaryDirectory() as td:
            ledger=CampaignShadowLedger(td); result=ledger.reconcile_commit(self.commit()); self.assertEqual(result["status"],"MISSING_DB"); self.assertFalse(ledger.path.exists())

if __name__ == "__main__": unittest.main()
