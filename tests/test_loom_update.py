import importlib.util
import json
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
        self.artifacts = [
            {"path": "src/nav.py", "sha256": loom_update.sha256_bytes(self.nav), "install_group": "code", "required": True},
            {"path": "src/gis.py", "sha256": loom_update.sha256_bytes(self.gis), "install_group": "code", "required": True},
            {"path": "data/world.sqlite3", "sha256": loom_update.sha256_bytes(self.world), "install_group": "canonical_data", "required": True},
            {"path": "data/civ.sqlite3", "sha256": loom_update.sha256_bytes(self.civ), "install_group": "canonical_data", "required": True},
            {"path": "data/media.sqlite3", "sha256": None, "install_group": "media", "required": True},
        ]
        self.manifest = {
            "release_id": "test",
            "release_state": "staging",
            "source_ref": "test-ref",
            "artifacts": self.artifacts,
        }
        self.files = {
            loom_update.MANIFEST_PATH: json.dumps(self.manifest).encode(),
            "src/nav.py": self.nav,
            "src/gis.py": self.gis,
            "data/world.sqlite3": self.world,
            "data/civ.sqlite3": self.civ,
        }

    def fetch(self, path, ref):
        self.assertEqual(ref, "test-ref")
        return self.files[path]

    def test_install_validate_backup_and_pending_media(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "LOOM"
            rc = loom_update.main(["update", "--root", str(root), "--ref", "test-ref"], self.fetch)
            self.assertEqual(rc, 2)
            self.assertEqual((root / "src/nav.py").read_bytes(), self.nav)
            self.assertEqual((root / "data/world.sqlite3").read_bytes(), self.world)
            self.assertTrue((root / loom_update.INSTALL_STATE).exists())

            results = loom_update.validate_local(root, self.manifest)
            self.assertEqual(sum(r.state == "OK" for r in results), 4)
            self.assertTrue(any(r.state == "PENDING_REQUIRED" for r in results))

            (root / "src/nav.py").write_bytes(b"old")
            loom_update.install_release(root, self.manifest, "test-ref", self.fetch)
            self.assertEqual((root / ".loom_backups/test/src/nav.py").read_bytes(), b"old")

    def test_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "LOOM"
            bad = dict(self.files)
            bad["src/nav.py"] = b"evil"

            def bad_fetch(path, ref):
                return bad[path]

            with self.assertRaisesRegex(RuntimeError, "HASH MISMATCH"):
                loom_update.install_release(root, self.manifest, "test-ref", bad_fetch)


if __name__ == "__main__":
    unittest.main()
