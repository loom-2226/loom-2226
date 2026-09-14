import pathlib
import subprocess
import sys
import unittest


class PixelSpatialReviewContractTests(unittest.TestCase):
    def setUp(self):
        self.repo = pathlib.Path(__file__).resolve().parents[1]

    def test_review_module_renders_vector_html_with_physical_scale(self):
        from engineering.pixel.spatial_review import build_neptune_mag_exact_sample_review

        html = build_neptune_mag_exact_sample_review()
        self.assertIn("<svg", html)
        self.assertIn("viewBox=", html)
        self.assertIn("24,765 km", html)
        self.assertIn("QUALIFICATION FIXTURE — NOT PDS OBSERVATION", html)
        self.assertIn("EXACT BODY / EPOCH / FRAME / POSITION", html)
        self.assertIn("Scale bar", html)
        self.assertNotIn("canvas", html.lower())

    def test_pds_pairing_review_explains_problem_solution_legend_and_definitions(self):
        from engineering.pixel.spatial_review import build_neptune_mag_pds_source_contract_review

        html = build_neptune_mag_pds_source_contract_review()
        self.assertIn("Problem statement", html)
        self.assertIn("How we are trying to solve it", html)
        self.assertIn("Legend", html)
        self.assertIn("Definitions", html)
        self.assertIn("Exact epoch", html)
        self.assertIn("Fail closed", html)
        self.assertIn("12-second cadence", html)
        self.assertIn("same timestamp", html)
        self.assertIn("NO INTERPOLATION", html)
        self.assertIn("<svg", html)
        self.assertNotIn("canvas", html.lower())

    def test_review_script_executes_directly_from_repo_root(self):
        proc = subprocess.run(
            [
                sys.executable,
                "engineering/pixel/spatial_review.py",
                "--review",
                "neptune-mag-exact-sample",
                "--check",
            ],
            cwd=self.repo,
            text=True,
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)
        self.assertIn("SPATIAL_REVIEW_CHECK=PASS", proc.stdout)

    def test_review_server_is_read_only_and_port_separated(self):
        text = (self.repo / "engineering/pixel/spatial_review.py").read_text(encoding="utf-8")
        self.assertIn("DEFAULT_PORT = 8878", text)
        self.assertNotIn("do_POST", text)
        self.assertNotIn("do_PUT", text)
        self.assertNotIn("do_DELETE", text)

    def test_pixel_runner_supports_optional_spatial_review_command_after_pass(self):
        text = (self.repo / "engineering/pixel/loom_pixel_run.sh").read_text(encoding="utf-8")
        self.assertIn("SPATIAL_REVIEW_COMMAND", text)
        self.assertIn("LOOM_SPATIAL_REVIEW_URL", text)
        self.assertIn("termux-open-url", text)
        self.assertIn("if [[ $PIPE_RC -eq 0", text)

    def test_runner_uses_termux_writable_review_log_location(self):
        text = (self.repo / "engineering/pixel/loom_pixel_run.sh").read_text(encoding="utf-8")
        self.assertIn("TMPDIR", text)
        self.assertIn("REVIEW_LOG", text)
        self.assertNotIn(">/tmp/loom-spatial-review.log", text)
        self.assertNotIn("SPATIAL_REVIEW_LOG=/tmp/loom-spatial-review.log", text)

    def test_qualification_command_does_not_kill_its_own_shell_by_matching_command_text(self):
        cfg = (self.repo / "engineering/pixel/active_qualification.txt").read_text(encoding="utf-8").splitlines()
        qualification_command = cfg[1]
        self.assertNotIn("pkill -f 'engineering/pixel/spatial_review.py'", qualification_command)


if __name__ == "__main__":
    unittest.main()
