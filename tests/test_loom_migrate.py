from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util,sys,unittest,json

TOOL=Path(__file__).parents[1]/"deploy"/"loom_migrate.py"; spec=importlib.util.spec_from_file_location("loom_migrate",TOOL); m=importlib.util.module_from_spec(spec); sys.modules["loom_migrate"]=m; spec.loader.exec_module(m)

class LoomMigrateTest(unittest.TestCase):
 def seed(self,root):
  (root/"src").mkdir(parents=True); (root/"src"/"app.py").write_text("app"); (root/"LOOM_STATE_V1.json").write_text('{"revision":1}'); (root/"LOOM_CAMPAIGN_HISTORY.jsonl.gz").write_bytes(b"history"); (root/"logs").mkdir(); (root/"logs"/"x.log").write_text("log"); (root/"LOOM_Navigator_Cache_v1").mkdir(); (root/"LOOM_Navigator_Cache_v1"/"cache.bin").write_bytes(b"cache"); (root/"data").mkdir(); (root/"data"/"legacy.sqlite3").write_bytes(b"data")
 def test_audit_is_read_only_and_classifies_authority(self):
  with TemporaryDirectory() as td:
   source=Path(td)/"old"; target=Path(td)/"new"; source.mkdir(); self.seed(source); before={str(p.relative_to(source)):m.sha256(p) for p in source.rglob("*") if p.is_file()}; plan=m.audit(source,target); after={str(p.relative_to(source)):m.sha256(p) for p in source.rglob("*") if p.is_file()}; self.assertEqual(before,after); self.assertFalse(target.exists()); self.assertEqual(plan["unknown_count"],0); classes={Path(x["source"]).name:x["classification"] for x in plan["items"]}; self.assertEqual(classes["LOOM_STATE_V1.json"],"campaign"); self.assertEqual(classes["legacy.sqlite3"],"preserve_existing")
 def test_stage_copies_without_deleting_source(self):
  with TemporaryDirectory() as td:
   source=Path(td)/"old"; target=Path(td)/"new"; source.mkdir(); self.seed(source); plan=m.audit(source,target); result=m.stage(plan); self.assertTrue(result["valid"]); self.assertTrue((target/"runtime/src/app.py").is_file()); self.assertTrue((target/"campaign/LOOM_STATE_V1.json").is_file()); self.assertTrue((target/"logs/x.log").is_file()); self.assertTrue((target/"cache/LOOM_Navigator_Cache_v1/cache.bin").is_file()); self.assertTrue((source/"LOOM_STATE_V1.json").is_file()); self.assertFalse((target/"data/legacy.sqlite3").exists())
 def test_unknown_file_blocks_stage(self):
  with TemporaryDirectory() as td:
   source=Path(td)/"old"; target=Path(td)/"new"; source.mkdir(); (source/"mystery.bin").write_bytes(b"?"); plan=m.audit(source,target); self.assertEqual(plan["unknown_count"],1)
   with self.assertRaisesRegex(RuntimeError,"UNKNOWN FILES"):m.stage(plan)
   self.assertFalse(target.exists())
 def test_collision_mismatch_fails_closed(self):
  with TemporaryDirectory() as td:
   source=Path(td)/"old"; target=Path(td)/"new"; source.mkdir(); (source/"src").mkdir(); (source/"src/app.py").write_text("new"); (target/"runtime/src").mkdir(parents=True); (target/"runtime/src/app.py").write_text("different"); plan=m.audit(source,target)
   with self.assertRaisesRegex(RuntimeError,"COLLISION MISMATCH"):m.stage(plan)
   self.assertEqual((target/"runtime/src/app.py").read_text(),"different")
 def test_activate_requires_valid_stage_and_writes_only_contract(self):
  with TemporaryDirectory() as td:
   source=Path(td)/"old"; target=Path(td)/"new"; source.mkdir(); self.seed(source); plan=m.audit(source,target)
   with self.assertRaisesRegex(RuntimeError,"not fully staged"):m.activate(plan)
   m.stage(plan); contract=m.activate(plan); payload=json.loads(contract.read_text()); self.assertEqual(payload["contract"],m.ROOT_CONTRACT); self.assertEqual(payload["LOOM_APP_ROOT"],str((target/"runtime").resolve())); self.assertEqual(payload["LOOM_DATA_ROOT"],str((target/"data").resolve())); self.assertEqual(payload["LOOM_CAMPAIGN_ROOT"],str((target/"campaign").resolve())); self.assertTrue(source.exists())
 def test_pixel_audited_artifacts_have_explicit_destinations(self):
  cases={
   "LOOM_CAMPAIGN_HISTORY.jsonl.gz.bak":("backup","backups/campaign/LOOM_CAMPAIGN_HISTORY.jsonl.gz.bak"),
   "LOOM_Navigator_Visual_Design_B1_LOCKED_Package_v1.0.zip":("application","runtime/LOOM_Navigator_Visual_Design_B1_LOCKED_Package_v1.0.zip"),
   "LOOM_PHASE6_HTTP_20260903_215857.log":("logs","logs/LOOM_PHASE6_HTTP_20260903_215857.log"),
   "LOOM_PHASE6_LATEST.txt":("logs","logs/LOOM_PHASE6_LATEST.txt"),
   "LOOM_Navigator_Current.html":("generated","cache/generated/LOOM_Navigator_Current.html"),
   "LOOM_PHONE_RUNTIME_AUDIT.txt":("audit","audit/legacy/LOOM_PHONE_RUNTIME_AUDIT.txt"),
   "LOOM_Navigator_Browser_Report.json":("audit","audit/legacy/LOOM_Navigator_Browser_Report.json"),
   "LOOM_KNOWLEDGE_RELATIONSHIPS_DIFF.txt":("audit","audit/legacy/LOOM_KNOWLEDGE_RELATIONSHIPS_DIFF.txt"),
   "LOOM_Android_Phase6_Convergence_Sync.py":("audit","audit/legacy/LOOM_Android_Phase6_Convergence_Sync.py"),
   "LOOM_SequenceH_Core.py":("application","runtime/LOOM_SequenceH_Core.py"),
  }
  for raw,expected in cases.items():self.assertEqual(m.classify(Path(raw)),expected,raw)
 def test_bytecode_is_not_migrated_and_legacy_backups_are_preserved(self):
  self.assertEqual(m.classify(Path("src/__pycache__/x.cpython-313.pyc")),("generated",None))
  self.assertEqual(m.classify(Path(".loom_backups/phase6/src/x.py")),("backup","backups/legacy_runtime/phase6/src/x.py"))
if __name__=="__main__":unittest.main()
