import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

UPDATER = Path(__file__).resolve().parents[1] / "deploy" / "loom_update.py"
spec = importlib.util.spec_from_file_location("loom_update", UPDATER)
loom_update = importlib.util.module_from_spec(spec)
sys.modules["loom_update"] = loom_update
spec.loader.exec_module(loom_update)


class LoomUpdateTests(unittest.TestCase):
    def setUp(self):
        self.nav = b"nav-code"
        self.gis = b"gis-code"
        self.world = b"world-db"
        self.civ = b"civ-db"
        self.media = b"media-db"
        self.artifacts = [
            {"path": "src/nav.py", "sha256": loom_update.sha256_bytes(self.nav), "size_bytes": len(self.nav), "source": "repository", "install_group": "code", "required": True},
            {"path": "src/gis.py", "sha256": loom_update.sha256_bytes(self.gis), "size_bytes": len(self.gis), "source": "repository", "install_group": "code", "required": True},
            {"path": "data/world.sqlite3", "sha256": loom_update.sha256_bytes(self.world), "size_bytes": len(self.world), "source": "repository", "install_group": "canonical_data", "required": True},
            {"path": "data/civ.sqlite3", "sha256": loom_update.sha256_bytes(self.civ), "size_bytes": len(self.civ), "source": "repository", "install_group": "canonical_data", "required": True},
            {"path": "data/media.sqlite3", "sha256": loom_update.sha256_bytes(self.media), "size_bytes": len(self.media), "source": "release_asset", "asset_id": 12345, "install_group": "media", "required": True},
        ]
        self.manifest = {
            "release_id": "test",
            "release_state": "staging",
            "source_ref": "test-ref",
            "artifacts": self.artifacts,
        }
        self.files = {
            "src/nav.py": self.nav,
            "src/gis.py": self.gis,
            "data/world.sqlite3": self.world,
            "data/civ.sqlite3": self.civ,
            "data/media.sqlite3": self.media,
        }

    def load_manifest(self, ref):
        self.assertEqual(ref, "test-ref")
        loom_update.validate_manifest(self.manifest)
        return self.manifest

    def fetch(self, artifact, ref):
        self.assertEqual(ref, "test-ref")
        if artifact["source"] == "release_asset":
            self.assertEqual(artifact["asset_id"], 12345)
        return self.files[artifact["path"]]

    def test_complete_install_validate_and_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "LOOM"
            rc = loom_update.main(
                ["update", "--root", str(root), "--ref", "test-ref"],
                self.load_manifest,
                self.fetch,
            )
            self.assertEqual(rc, 0)
            self.assertEqual((root / "src/nav.py").read_bytes(), self.nav)
            self.assertEqual((root / "data/media.sqlite3").read_bytes(), self.media)
            self.assertTrue((root / loom_update.INSTALL_STATE).exists())

            results = loom_update.validate_local(root, self.manifest)
            self.assertTrue(all(r.state == "OK" for r in results))

            results = loom_update.install_release(
                root, self.manifest, "test-ref", artifact_fetcher=self.fetch
            )
            self.assertTrue(all(r.state == "UNCHANGED" for r in results))

    def test_backup_on_replacement(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "LOOM"
            (root / "src").mkdir(parents=True)
            (root / "src/nav.py").write_bytes(b"old")
            loom_update.install_release(
                root, self.manifest, "test-ref", artifact_fetcher=self.fetch
            )
            self.assertEqual((root / ".loom_backups/test/src/nav.py").read_bytes(), b"old")

    def test_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "LOOM"

            def bad_fetch(artifact, ref):
                if artifact["path"] == "src/nav.py":
                    return b"evil"
                return self.fetch(artifact, ref)

            with self.assertRaisesRegex(RuntimeError, "SIZE MISMATCH|HASH MISMATCH"):
                loom_update.install_release(
                    root, self.manifest, "test-ref", artifact_fetcher=bad_fetch
                )

    def test_release_asset_requires_id(self):
        bad = dict(self.artifacts[-1])
        bad.pop("asset_id")
        manifest = dict(self.manifest)
        manifest["artifacts"] = self.artifacts[:-1] + [bad]
        with self.assertRaisesRegex(RuntimeError, "asset_id"):
            loom_update.validate_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
