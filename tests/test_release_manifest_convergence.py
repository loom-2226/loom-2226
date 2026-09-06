from pathlib import Path
import json
import unittest

ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / "manifests" / "release_manifest.json"

class ReleaseManifestConvergenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_is_staging_convergence_authority(self):
        m=self.manifest
        self.assertEqual(m["format"],"LOOM_RELEASE_MANIFEST_V2")
        self.assertEqual(m["release_state"],"staging")
        self.assertEqual(m["source_ref"],"integration/runtime-devops-convergence-2026-09-06")
        self.assertEqual(m["authority"]["campaign_policy"],"preserve_local_never_install")

    def test_required_runtime_surfaces_exist(self):
        required={"src/loom_gis.py","src/loom_navigator.py","src/loom_doctor.py","src/loom/runtime.py","src/loom/runtime_diagnostics.py","src/loom/runtime_trace.py","src/loom/campaign/execution.py","src/loom/campaign/shadow_ledger.py","src/loom/gis/flight_planning.py","src/loom/gis/flight_planning_http.py","deploy/loom_update.py","deploy/android/launch_gis.py","deploy/android/launch_navigator.py","deploy/windows/launch_gis.py","deploy/windows/launch_navigator.py"}
        declared=set(self.manifest["runtime_files"])
        self.assertTrue(required.issubset(declared))
        for path in declared:self.assertTrue((ROOT/path).is_file(),path)

    def test_campaign_authority_is_never_installable(self):
        forbidden={"LOOM_STATE_V1.json","LOOM_CAMPAIGN_HISTORY.jsonl.gz","LOOM_CAMPAIGN_DEV.sqlite3"}
        runtime={Path(p).name for p in self.manifest["runtime_files"]}
        data={Path(x["path"]).name for x in self.manifest["canonical_data"]}
        self.assertTrue(forbidden.isdisjoint(runtime|data))
        preserved={Path(p.rstrip("/")).name for p in self.manifest["preserve_local"]}
        self.assertTrue(forbidden.issubset(preserved))

    def test_canonical_data_matches_frozen_pixel_baseline(self):
        expected={
            "data/LOOM_2226.sqlite3":("e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde",4882432),
            "data/LOOM_2226_CIVSTATE.sqlite3":("9ef530bdc1b8d867fe217a8c6d3a05e3926b0b09b0d66a91ce090b3e52fae560",8093696),
            "data/LOOM_2226_media.sqlite3":("286873428afbf30b91bdb2e71b55146ed5979873cfd6af69579c121b724eb038",473837568),
        }
        actual={x["path"]:(x["sha256"],x["size_bytes"]) for x in self.manifest["canonical_data"]}
        self.assertEqual(actual,expected)

if __name__=="__main__":unittest.main()
