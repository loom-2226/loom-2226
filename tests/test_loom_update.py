import importlib.util,sys,tempfile,unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch
UPDATER=Path(__file__).resolve().parents[1]/"deploy"/"loom_update.py"; spec=importlib.util.spec_from_file_location("loom_update",UPDATER); loom_update=importlib.util.module_from_spec(spec); sys.modules["loom_update"]=loom_update; spec.loader.exec_module(loom_update)
class LoomUpdateTests(unittest.TestCase):
 def setUp(self):
  self.nav=b"nav-code"; self.gis=b"gis-code"; self.world=b"world-db"; self.civ=b"civ-db"; self.media=b"media-db"; self.artifacts=[{"path":"src/nav.py","sha256":loom_update.sha256_bytes(self.nav),"size_bytes":len(self.nav),"source":"repository","install_group":"code","required":True},{"path":"src/gis.py","sha256":loom_update.sha256_bytes(self.gis),"size_bytes":len(self.gis),"source":"repository","install_group":"code","required":True},{"path":"data/world.sqlite3","sha256":loom_update.sha256_bytes(self.world),"size_bytes":len(self.world),"source":"repository","install_group":"canonical_data","required":True},{"path":"data/civ.sqlite3","sha256":loom_update.sha256_bytes(self.civ),"size_bytes":len(self.civ),"source":"repository","install_group":"canonical_data","required":True},{"path":"data/media.sqlite3","sha256":loom_update.sha256_bytes(self.media),"size_bytes":len(self.media),"source":"release_asset","asset_id":12345,"install_group":"media","required":True}]; self.manifest={"release_id":"test","release_state":"staging","source_ref":"test-ref","artifacts":self.artifacts}; self.files={"src/nav.py":self.nav,"src/gis.py":self.gis,"data/world.sqlite3":self.world,"data/civ.sqlite3":self.civ,"data/media.sqlite3":self.media}
 def load_manifest(self,ref):self.assertEqual(ref,"test-ref"); loom_update.validate_manifest(self.manifest); return self.manifest
 def fetch(self,a,ref):self.assertEqual(ref,"test-ref"); return self.files[a["path"]]
 def test_complete_install_validate_and_unchanged(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/"LOOM"; rc=loom_update.main(["update","--root",str(root),"--ref","test-ref"],self.load_manifest,self.fetch); self.assertEqual(rc,0); self.assertEqual((root/"src/nav.py").read_bytes(),self.nav); self.assertEqual((root/"data/media.sqlite3").read_bytes(),self.media); self.assertTrue((root/loom_update.INSTALL_STATE).exists()); self.assertTrue(all(r.state=="OK" for r in loom_update.validate_local(root,self.manifest))); self.assertTrue(all(r.state=="UNCHANGED" for r in loom_update.install_release(root,self.manifest,"test-ref",artifact_fetcher=self.fetch)))
 def test_separate_app_and_data_roots(self):
  with tempfile.TemporaryDirectory() as td:
   app=Path(td)/"app"; data=Path(td)/"canonical"; roots=loom_update.InstallRoots(app,data); loom_update.install_release(roots,self.manifest,"test-ref",artifact_fetcher=self.fetch); self.assertEqual((app/"src/nav.py").read_bytes(),self.nav); self.assertEqual((data/"world.sqlite3").read_bytes(),self.world); self.assertFalse((app/"data/world.sqlite3").exists())
 def test_campaign_root_is_never_an_install_target(self):
  with tempfile.TemporaryDirectory() as td:
   app=Path(td)/"app"; data=Path(td)/"data"; campaign=Path(td)/"campaign"; campaign.mkdir(); sentinel=campaign/"LOOM_STATE_V1.json"; sentinel.write_text("KEEP"); roots=loom_update.platform_roots(str(app),str(data),{"LOOM_CAMPAIGN_ROOT":str(campaign)}); loom_update.install_release(roots,self.manifest,"test-ref",artifact_fetcher=self.fetch); self.assertEqual(sentinel.read_text(),"KEEP"); self.assertEqual(list(campaign.iterdir()),[sentinel])
 def test_root_environment_precedence_and_legacy_compatibility(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td); roots=loom_update.platform_roots(environ={"LOOM_APP_ROOT":str(base/"app"),"LOOM_DATA_ROOT":str(base/"data"),"LOOM_HOME":str(base/"legacy")}); self.assertEqual(roots.app_root,(base/"app").resolve()); self.assertEqual(roots.data_root,(base/"data").resolve()); legacy=loom_update.platform_roots(environ={"LOOM_HOME":str(base/"legacy")}); self.assertEqual(legacy.app_root,(base/"legacy").resolve()); self.assertEqual(legacy.data_root,(base/"legacy"/"data").resolve())
 def test_backup_on_replacement(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/"LOOM"; (root/"src").mkdir(parents=True); (root/"src/nav.py").write_bytes(b"old"); loom_update.install_release(root,self.manifest,"test-ref",artifact_fetcher=self.fetch); self.assertEqual((root/".loom_backups/test/nav.py").read_bytes(),b"old")
 def test_hash_mismatch_fails_closed(self):
  with tempfile.TemporaryDirectory() as td:
   def bad(a,ref):return b"evil" if a["path"]=="src/nav.py" else self.fetch(a,ref)
   with self.assertRaisesRegex(RuntimeError,"SIZE MISMATCH|HASH MISMATCH"):loom_update.install_release(Path(td)/"LOOM",self.manifest,"test-ref",artifact_fetcher=bad)
 def test_release_asset_requires_id(self):
  bad=dict(self.artifacts[-1]); bad.pop("asset_id"); m=dict(self.manifest); m["artifacts"]=self.artifacts[:-1]+[bad]
  with self.assertRaisesRegex(RuntimeError,"asset_id"):loom_update.validate_manifest(m)
 def test_manifest_rejects_campaign_install_group(self):
  m={"artifacts":[{"path":"LOOM_STATE_V1.json","install_group":"campaign","required":True}]}
  with self.assertRaisesRegex(RuntimeError,"Unknown install_group"):loom_update.validate_manifest(m)
 def test_progress_line_with_known_total(self):self.assertIn("50.0%",loom_update._progress_line("data/media.sqlite3",50,100))
 def test_progress_line_without_total(self):self.assertNotIn("%",loom_update._progress_line("data/media.sqlite3",1024*1024,None))
 def test_streaming_download_progress_and_payload_integrity(self):
  payload=b"abcdefghij"
  class FakeResponse:
   headers={"Content-Length":str(len(payload))}
   def __enter__(self):return self
   def __exit__(self,*args):return False
   def read(self,n):
    if not hasattr(self,"_pos"):self._pos=0
    if self._pos>=len(payload):return b""
    c=payload[self._pos:self._pos+3]; self._pos+=len(c); return c
  out=StringIO()
  with patch.object(loom_update,"urlopen",return_value=FakeResponse()),patch.object(loom_update,"token",return_value="test-token"),patch.object(loom_update,"PROGRESS_THRESHOLD_BYTES",1),redirect_stdout(out):actual=loom_update.github_bytes("https://example.invalid/test","application/octet-stream",label="data/media.sqlite3",expected_size=len(payload))
  self.assertEqual(actual,payload); self.assertIn("100.0%",out.getvalue())
if __name__=="__main__":unittest.main()
