from __future__ import annotations

import pathlib
import unittest


class PixelQualificationLogPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = pathlib.Path(__file__).resolve().parents[1]
        self.runner = (self.repo / "engineering/pixel/loom_pixel_run.sh").read_text(encoding="utf-8")

    def test_runner_persists_timestamped_log_outside_repo(self) -> None:
        self.assertIn("LOOM_Qualification_Logs", self.runner)
        self.assertIn("QUALIFICATION_LOG=", self.runner)
        self.assertIn("cp \"$TMP\" \"$QUALIFICATION_LOG\"", self.runner)

    def test_runner_updates_stable_latest_log_pointer(self) -> None:
        self.assertIn("LATEST_QUALIFICATION_LOG=", self.runner)
        self.assertIn("cp \"$TMP\" \"$LATEST_QUALIFICATION_LOG\"", self.runner)

    def test_runner_reports_persisted_log_paths(self) -> None:
        self.assertIn("QUALIFICATION_LOG_SAVED=", self.runner)
        self.assertIn("QUALIFICATION_LOG_LATEST=", self.runner)


if __name__ == "__main__":
    unittest.main()
