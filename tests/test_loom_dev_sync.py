import json
from pathlib import Path
import tempfile
import unittest

from loom_dev_sync import discover_sources, sync


class LoomDevSyncTests(unittest.TestCase):
    def test_dev_sync_only_copies_application_allowlist(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            app = root / "runtime"
            (repo / "src/loom/application").mkdir(parents=True)
            (repo / "src/loom/application/contracts.py").write_text("x=1\n")
            (repo / "src/loom_gis.py").write_text("gis=1\n")
            (repo / "web").mkdir()
            (repo / "web/viewer.js").write_text("const x=1;\n")
            (repo / "data").mkdir()
            (repo / "data/LOOM_2226.sqlite3").write_bytes(b"DO NOT COPY")
            (repo / "campaign").mkdir()
            (repo / "campaign/LOOM_STATE_V1.json").write_text("{}")

            paths = [p.relative_to(repo).as_posix() for p in discover_sources(repo)]
            self.assertIn("src/loom/application/contracts.py", paths)
            self.assertIn("src/loom_gis.py", paths)
            self.assertIn("web/viewer.js", paths)
            self.assertFalse(any(path.startswith("data/") for path in paths))
            self.assertFalse(any(path.startswith("campaign/") for path in paths))

            result = sync(repo, app)
            self.assertTrue(result)
            self.assertTrue((app / "src/loom/application/contracts.py").exists())
            self.assertFalse((app / "data/LOOM_2226.sqlite3").exists())
            self.assertFalse((app / "campaign/LOOM_STATE_V1.json").exists())
            state = json.loads((app / ".loom_dev_state.json").read_text())
            self.assertEqual(state["authority_guards"]["campaign"], "never touched")

    def test_dev_sync_backs_up_replaced_application_file(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            app = root / "runtime"
            source = repo / "src/loom/test.py"
            target = app / "src/loom/test.py"
            source.parent.mkdir(parents=True)
            target.parent.mkdir(parents=True)
            source.write_text("new\n")
            target.write_text("old\n")

            sync(repo, app)
            backups = list((app / ".loom_dev_backups").glob("*/src/loom/test.py"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), "old\n")
            self.assertEqual(target.read_text(), "new\n")


if __name__ == "__main__":
    unittest.main()
