from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from loom.runtime import resolve_runtime_roots
from loom.runtime_diagnostics import collect_runtime_manifest, render_runtime_audit


class RuntimeDiagnosticsTest(unittest.TestCase):
    def test_manifest_reports_resolved_roots_and_existing_files(self):
        with TemporaryDirectory() as tmp:
            app = Path(tmp) / "app"
            data = Path(tmp) / "data"
            campaign = Path(tmp) / "campaign"
            (app / "src" / "loom").mkdir(parents=True)
            data.mkdir()
            campaign.mkdir()
            (app / "src" / "loom_gis.py").write_text("# gis\n", encoding="utf-8")
            (app / "src" / "loom" / "runtime.py").write_text("# runtime\n", encoding="utf-8")
            (data / "LOOM_2226.sqlite3").write_bytes(b"world")
            (campaign / "LOOM_STATE_V1.json").write_text("{}", encoding="utf-8")
            roots = resolve_runtime_roots(app_root=app, data_root=data, campaign_root=campaign)
            manifest = collect_runtime_manifest(roots=roots)
            self.assertEqual(manifest["roots"]["app_root"], str(app.resolve()))
            world = next(x for x in manifest["databases"] if x["root"] == "data_root" and x["name"] == "LOOM_2226.sqlite3")
            self.assertTrue(world["exists"])
            self.assertIsNotNone(world["sha256"])
            self.assertTrue(manifest["campaign"]["state"]["exists"])

    def test_campaign_state_uses_app_compatibility_fallback(self):
        with TemporaryDirectory() as tmp:
            app = Path(tmp) / "app"
            campaign = Path(tmp) / "campaign"
            app.mkdir()
            campaign.mkdir()
            (app / "LOOM_STATE_V1.json").write_text("{}", encoding="utf-8")
            roots = resolve_runtime_roots(app_root=app, campaign_root=campaign)
            manifest = collect_runtime_manifest(roots=roots)
            state = manifest["campaign"]["state"]
            self.assertTrue(state["exists"])
            self.assertTrue(state["compatibility_fallback"])

    def test_audit_is_human_readable(self):
        with TemporaryDirectory() as tmp:
            roots = resolve_runtime_roots(app_root=tmp, data_root=Path(tmp) / "data", campaign_root=tmp)
            audit = render_runtime_audit(collect_runtime_manifest(roots=roots))
            self.assertIn("LOOM RUNTIME AUDIT", audit)
            self.assertIn("APP ROOT", audit)
            self.assertIn("DATABASES", audit)


if __name__ == "__main__":
    unittest.main()
