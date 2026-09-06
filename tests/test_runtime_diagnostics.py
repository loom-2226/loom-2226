from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3
import unittest
from loom.runtime import resolve_runtime_roots
from loom.runtime_diagnostics import collect_runtime_manifest, render_runtime_audit
from loom.campaign.execution import CampaignFlightCommitV1
from loom.campaign.shadow_ledger import CampaignShadowLedger
class RuntimeDiagnosticsTest(unittest.TestCase):
    def test_manifest_reports_resolved_roots_and_existing_files(self):
        with TemporaryDirectory() as tmp:
            app=Path(tmp)/"app"; data=Path(tmp)/"data"; campaign=Path(tmp)/"campaign"; (app/"src"/"loom").mkdir(parents=True); data.mkdir(); campaign.mkdir(); (app/"src"/"loom_gis.py").write_text("# gis\n"); (app/"src"/"loom"/"runtime.py").write_text("# runtime\n"); (data/"LOOM_2226.sqlite3").write_bytes(b"world"); (campaign/"LOOM_STATE_V1.json").write_text("{}")
            manifest=collect_runtime_manifest(roots=resolve_runtime_roots(app_root=app,data_root=data,campaign_root=campaign)); self.assertEqual(manifest["roots"]["app_root"],str(app.resolve())); world=next(x for x in manifest["databases"] if x["root"]=="data_root" and x["name"]=="LOOM_2226.sqlite3"); self.assertTrue(world["exists"]); self.assertIsNotNone(world["sha256"]); self.assertTrue(manifest["campaign"]["state"]["exists"])
    def test_campaign_state_uses_app_compatibility_fallback(self):
        with TemporaryDirectory() as tmp:
            app=Path(tmp)/"app"; campaign=Path(tmp)/"campaign"; app.mkdir(); campaign.mkdir(); (app/"LOOM_STATE_V1.json").write_text("{}"); state=collect_runtime_manifest(roots=resolve_runtime_roots(app_root=app,campaign_root=campaign))["campaign"]["state"]; self.assertTrue(state["exists"]); self.assertTrue(state["compatibility_fallback"])
    def test_shadow_sql_diagnostics_are_read_only_and_report_integrity(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp); ledger=CampaignShadowLedger(root); commit=CampaignFlightCommitV1(flight_id="F1",state_before_id="S1",state_after_id="S2",revision_before=1,revision_after=2,origin="CERES",destination="MARS",departure_epoch_utc="2226-01-01T00:00:00Z",arrival_epoch_utc="2226-01-02T00:00:00Z",remass_before_t=250,remass_after_t=245,state_path="state",history_path="history",history_record_number=1,history_record_sha256="abc",final_state={"revision":2}); ledger.mirror_commit(commit); before=ledger.path.stat().st_mtime_ns
            shadow=collect_runtime_manifest(roots=resolve_runtime_roots(app_root=root,data_root=root/"data",campaign_root=root))["campaign"]["shadow_sql"]; self.assertTrue(shadow["exists"]); self.assertEqual(shadow["contract"],"LOOM_CAMPAIGN_SQL_SHADOW_V1"); self.assertEqual(shadow["flight_commit_count"],1); self.assertEqual(shadow["min_revision"],2); self.assertEqual(shadow["max_revision"],2); self.assertEqual(shadow["integrity_check"],"ok"); self.assertIsNone(shadow["error"]); self.assertEqual(ledger.path.stat().st_mtime_ns,before)
    def test_missing_shadow_sql_diagnostics_do_not_create_database(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp); manifest=collect_runtime_manifest(roots=resolve_runtime_roots(app_root=root,data_root=root/"data",campaign_root=root)); shadow=manifest["campaign"]["shadow_sql"]; self.assertFalse(shadow["exists"]); self.assertFalse((root/"LOOM_CAMPAIGN_DEV.sqlite3").exists())
    def test_audit_is_human_readable(self):
        with TemporaryDirectory() as tmp:
            roots=resolve_runtime_roots(app_root=tmp,data_root=Path(tmp)/"data",campaign_root=tmp); audit=render_runtime_audit(collect_runtime_manifest(roots=roots)); self.assertIn("LOOM RUNTIME AUDIT",audit); self.assertIn("APP ROOT",audit); self.assertIn("DATABASES",audit); self.assertIn("SHADOW SQL",audit)
if __name__=="__main__":unittest.main()
