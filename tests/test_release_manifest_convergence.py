from pathlib import Path
import json
import unittest
import importlib.util
import sys
ROOT=Path(__file__).parents[1]; MANIFEST=ROOT/"manifests"/"release_manifest.json"
UPDATER=ROOT/"deploy"/"loom_update.py"; spec=importlib.util.spec_from_file_location("loom_update_manifest_test",UPDATER); updater=importlib.util.module_from_spec(spec); sys.modules["loom_update_manifest_test"]=updater; spec.loader.exec_module(updater)
class ReleaseManifestConvergenceTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
 def test_manifest_is_staging_convergence_authority(self):
  m=self.manifest; self.assertEqual(m["format"],"LOOM_RELEASE_MANIFEST_V2"); self.assertEqual(m["release_state"],"staging"); self.assertEqual(m["source_ref"],"integration/runtime-devops-convergence-2026-09-06"); self.assertEqual(m["authority"]["campaign_policy"],"preserve_local_never_install"); self.assertEqual(m["artifact_freeze_base"],"f3ff95a4b2aa0e567488e33fd2578f351bafc675")
 def test_manifest_is_updater_compatible(self):
  updater.validate_manifest(self.manifest)
 def test_runtime_files_exist_are_updater_artifacts_and_are_pinned(self):
  m=self.manifest; artifacts={a["path"]:a for a in m["artifacts"]}
  for path in m["runtime_files"]:
   self.assertTrue((ROOT/path).is_file(),path); self.assertIn(path,artifacts); self.assertEqual(artifacts[path]["install_group"],"code"); self.assertTrue(artifacts[path]["required"]); self.assertIn("git_blob_sha1",artifacts[path]); self.assertEqual(len(artifacts[path]["git_blob_sha1"]),40); self.assertGreater(artifacts[path]["size_bytes"],0)
 def test_campaign_authority_is_preserved_and_never_installable(self):
  m=self.manifest; forbidden={"LOOM_STATE_V1.json","LOOM_STATE_V1.bak","LOOM_CAMPAIGN_HISTORY.jsonl.gz","LOOM_CAMPAIGN_DEV.sqlite3"}; artifact_paths={a["path"] for a in m["artifacts"]}; self.assertTrue(forbidden.isdisjoint(artifact_paths)); self.assertTrue(forbidden.issubset(set(m["preserve_local"]))); self.assertNotIn("campaign",{a["install_group"] for a in m["artifacts"]})
 def test_canonical_data_matches_frozen_pixel_baseline(self):
  expected={"data/LOOM_2226.sqlite3":("e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde",4882432),"data/LOOM_2226_CIVSTATE.sqlite3":("9ef530bdc1b8d867fe217a8c6d3a05e3926b0b09b0d66a91ce090b3e52fae560",8093696),"data/LOOM_2226_media.sqlite3":("286873428afbf30b91bdb2e71b55146ed5979873cfd6af69579c121b724eb038",473837568)}; self.assertEqual({x["path"]:(x["sha256"],x["size_bytes"]) for x in self.manifest["canonical_data"]},expected)
 def test_repository_data_artifacts_use_repository_paths(self):
  artifacts={a["path"]:a for a in self.manifest["artifacts"]}; self.assertIn("data/LOOM_2226.sqlite3",artifacts); self.assertIn("data/LOOM_2226_CIVSTATE.sqlite3",artifacts); self.assertEqual(artifacts["data/LOOM_2226.sqlite3"]["install_group"],"canonical_data"); self.assertEqual(artifacts["data/LOOM_2226_CIVSTATE.sqlite3"]["install_group"],"canonical_data")
if __name__=="__main__":unittest.main()
