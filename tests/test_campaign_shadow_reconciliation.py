from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
from loom.campaign.execution import CampaignFlightCommitV1
from loom.campaign.reconciliation import reconcile_campaign_shadow
from loom.campaign.shadow_ledger import CampaignShadowLedger
class FakeLedger:
    records=[]
    def __init__(self,root,state):self.records=list(type(self).records)
    def verify(self):return {"status":"PASS","records":len(self.records),"active_records":len(self.records),"last_sha256":self.records[-1]["record_sha256"] if self.records else None}
class FakeCore:
    STATE_FILE="LOOM_STATE_V1.json"; HistoryLedger=FakeLedger
    @staticmethod
    def _validate_state(state):
        if "revision" not in state:raise RuntimeError("bad state")
def commit(fid="F1",revision_after=2,record_number=1,record_sha="sha1"):
    return CampaignFlightCommitV1(flight_id=fid,state_before_id="S1",state_after_id="S2",revision_before=revision_after-1,revision_after=revision_after,origin="CERES",destination="MARS",departure_epoch_utc="2226-01-01T00:00:00Z",arrival_epoch_utc="2226-01-02T00:00:00Z",remass_before_t=250,remass_after_t=245,state_path="state",history_path="history",history_record_number=record_number,history_record_sha256=record_sha,final_state={"state_id":"S2","revision":revision_after,"last_flight":{"departure_state_id":"S1"}})
def history(fid="F1",revision=2,record_number=1,record_sha="sha1"):
    return {"record_type":"FLIGHT_ARRIVED","flight_id":fid,"record_number":record_number,"record_sha256":record_sha,"state_after_snapshot":{"state_id":"S2","revision":revision,"last_flight":{"departure_state_id":"S1"}}}
class CampaignShadowReconciliationTest(unittest.TestCase):
    def setUp(self):FakeLedger.records=[]
    def root(self,td,revision=2):
        root=Path(td); (root/"LOOM_STATE_V1.json").write_text(json.dumps({"revision":revision}),encoding="utf-8"); return root
    def test_verified_canonical_history_matches_shadow(self):
        with tempfile.TemporaryDirectory() as td:
            root=self.root(td); FakeLedger.records=[history()]; CampaignShadowLedger(root).mirror_commit(commit()); before=(root/"LOOM_CAMPAIGN_DEV.sqlite3").stat().st_mtime_ns; result=reconcile_campaign_shadow(root,FakeCore); self.assertEqual(result["status"],"MATCH"); self.assertTrue(result["match"]); self.assertEqual(result["canonical_arrival_records"],1); self.assertTrue(result["state_revision_aligned"]); self.assertEqual((root/"LOOM_CAMPAIGN_DEV.sqlite3").stat().st_mtime_ns,before)
    def test_missing_shadow_commit_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            root=self.root(td); FakeLedger.records=[history()]; result=reconcile_campaign_shadow(root,FakeCore); self.assertEqual(result["status"],"MISSING_DB"); self.assertEqual(result["missing_in_sql"],["F1"]); self.assertFalse((root/"LOOM_CAMPAIGN_DEV.sqlite3").exists())
    def test_extra_shadow_commit_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            root=self.root(td); FakeLedger.records=[]; CampaignShadowLedger(root).mirror_commit(commit()); result=reconcile_campaign_shadow(root,FakeCore); self.assertEqual(result["status"],"MISMATCH"); self.assertEqual(result["extra_in_sql"],["F1"])
    def test_history_hash_mismatch_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            root=self.root(td); FakeLedger.records=[history(record_sha="canonical")]; CampaignShadowLedger(root).mirror_commit(commit(record_sha="shadow")); result=reconcile_campaign_shadow(root,FakeCore); self.assertEqual(result["status"],"MISMATCH"); self.assertEqual(result["mismatches"][0]["flight_id"],"F1")
if __name__=="__main__":unittest.main()
