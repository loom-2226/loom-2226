import pathlib
import unittest


class PixelQualificationRunnerContractTests(unittest.TestCase):
    def setUp(self):
        self.repo = pathlib.Path(__file__).resolve().parents[1]

    def test_active_qualification_declares_branch_and_command(self):
        cfg = (self.repo / "engineering/pixel/active_qualification.txt").read_text(encoding="utf-8").splitlines()
        self.assertGreaterEqual(len(cfg), 2)
        self.assertEqual(cfg[0].strip(), "engineering/e1-forced-collapse-radius-experiment-2026-09-14")
        self.assertIn("e1_forced_collapse_radius_experiment_entry.py", cfg[1])

    def test_runner_is_fail_closed_and_copies_output(self):
        text = (self.repo / "engineering/pixel/loom_pixel_run.sh").read_text(encoding="utf-8")
        self.assertIn("git status --porcelain", text)
        self.assertIn("git pull --ff-only", text)
        self.assertIn("termux-clipboard-set", text)
        self.assertIn("LOOM PIXEL QUALIFICATION", text)


if __name__ == "__main__":
    unittest.main()
