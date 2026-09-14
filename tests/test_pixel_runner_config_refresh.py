from pathlib import Path
import unittest


RUNNER = Path("engineering/pixel/loom_pixel_run.sh")


class TestPixelRunnerConfigRefresh(unittest.TestCase):
    def test_runner_rereads_config_after_fast_forward_before_run(self):
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("load_config()", text)
        pull_index = text.index("git pull --ff-only")
        refresh_index = text.index("load_config \"POST_PULL\"", pull_index)
        run_index = text.index("bash -lc \"$QUAL_COMMAND\"", refresh_index)
        self.assertLess(pull_index, refresh_index)
        self.assertLess(refresh_index, run_index)

    def test_runner_can_follow_one_post_pull_branch_handoff_and_fails_closed_after_that(self):
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("CONFIG_HANDOFF", text)
        self.assertIn("git pull --ff-only", text)
        self.assertIn("CONFIG_BRANCH_CHAIN_REFUSED", text)
        self.assertIn("exit 94", text)

    def test_runner_reports_effective_config_not_only_bootstrap_config(self):
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("EFFECTIVE_CONFIG_BRANCH=", text)
        self.assertIn("EFFECTIVE_CONFIG_COMMAND=", text)


if __name__ == "__main__":
    unittest.main()
