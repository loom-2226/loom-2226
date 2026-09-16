from pathlib import Path
import unittest


class PixelQualificationRunnerGovernanceTests(unittest.TestCase):
    def test_governed_remote_pointer_is_not_replaced_after_target_pull(self):
        text = Path("engineering/pixel/loom_pixel_run.sh").read_text()
        self.assertIn('load_qualification_pointer_config "POST_PULL_GOVERNED_POINTER"', text)
        self.assertNotIn('git pull --ff-only; load_config "POST_PULL"', text)

    def test_post_qualification_uses_governed_pointer(self):
        text = Path("engineering/pixel/loom_pixel_run.sh").read_text()
        self.assertIn('load_qualification_pointer_config "POST_QUALIFICATION"', text)


if __name__ == "__main__":
    unittest.main()
