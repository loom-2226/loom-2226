from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import hashlib
import io
import json
import runpy
import sys
import unittest


DOCTOR = Path(__file__).parents[1] / "src" / "loom_doctor.py"


def snapshot(root):
    result = {}
    for path in sorted(Path(root).rglob("*")):
        if path.is_file():
            result[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def run_doctor(argv):
    namespace = runpy.run_path(str(DOCTOR), run_name="loom_doctor_test_module")
    return namespace["main"](argv)


class LoomDoctorTest(unittest.TestCase):
    def test_json_mode_is_read_only(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp); app=root/"app"; data=root/"data"; campaign=root/"campaign"
            (app/"src"/"loom").mkdir(parents=True); data.mkdir(); campaign.mkdir()
            (app/"src"/"loom_gis.py").write_text("# gis\n")
            (app/"src"/"loom"/"runtime.py").write_text("# runtime\n")
            (data/"LOOM_2226.sqlite3").write_bytes(b"world")
            (campaign/"LOOM_STATE_V1.json").write_text('{"revision":1}')
            before=snapshot(root); output=io.StringIO()
            argv=["--app-root",str(app),"--data-root",str(data),"--campaign-root",str(campaign),"--json"]
            with redirect_stdout(output): rc=run_doctor(argv)
            self.assertEqual(rc,0); manifest=json.loads(output.getvalue())
            self.assertEqual(manifest["roots"]["app_root"],str(app.resolve()))
            self.assertEqual(snapshot(root),before)

    def test_human_mode_reports_explicit_roots(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp); app=root/"app"; data=root/"data"; campaign=root/"campaign"; app.mkdir(); data.mkdir(); campaign.mkdir(); output=io.StringIO()
            argv=["--app-root",str(app),"--data-root",str(data),"--campaign-root",str(campaign)]
            with redirect_stdout(output): rc=run_doctor(argv)
            self.assertEqual(rc,0); text=output.getvalue(); self.assertIn("LOOM RUNTIME AUDIT",text); self.assertIn(str(app.resolve()),text); self.assertIn(str(data.resolve()),text); self.assertIn(str(campaign.resolve()),text)


if __name__ == "__main__": unittest.main()
