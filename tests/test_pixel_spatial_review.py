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

    def test_active_config_can_carry_optional_third_line(self):
        cfg = (self.repo / "engineering/pixel/active_qualification.txt").read_text(encoding="utf-8").splitlines()
        self.assertGreaterEqual(len(cfg), 3)
        self.assertIn("spatial_review.py", cfg[2])
        self.assertIn("--review neptune-mag-exact-sample", cfg[2])


if __name__ == "__main__":
    unittest.main()
