import pathlib
import unittest


class PixelQualificationRunnerContractTests(unittest.TestCase):
    def setUp(self):
        self.repo = pathlib.Path(__file__).resolve().parents[1]

    def test_active_qualification_declares_branch_and_command(self):
        cfg = (self.repo / "engineering/pixel/active_qualification.txt").read_text(encoding="utf-8").splitlines()
        self.assertGreaterEqual(len(cfg), 2)
        self.assertTrue(cfg[0].strip())
        self.assertTrue(cfg[1].strip())
        self.assertTrue(cfg[0].strip().startswith("engineering/"))
        self.assertIn("python", cfg[1])

    def test_runner_is_fail_closed_and_copies_output(self):
        text = (self.repo / "engineering/pixel/loom_pixel_run.sh").read_text(encoding="utf-8")
        self.assertIn("git status --porcelain", text)
        self.assertIn("git pull --ff-only", text)
        self.assertIn("termux-clipboard-set", text)
        self.assertIn("LOOM PIXEL QUALIFICATION", text)

    def test_raw_runner_retains_transcript_for_interactive_review(self):
        text = (self.repo / "engineering/pixel/loom_pixel_run.sh").read_text(encoding="utf-8")
        self.assertIn('LATEST_QUALIFICATION_LOG="$QUALIFICATION_LOG_DIR/latest.log"', text)
        self.assertIn('less -R "$LATEST_QUALIFICATION_LOG"', text)
        self.assertIn("Press q when finished reviewing", text)
        self.assertIn('cat "$LATEST_QUALIFICATION_LOG"', text)

    def test_clipboard_is_compact_receipt_while_full_transcript_stays_local(self):
        text = (self.repo / "engineering/pixel/loom_pixel_run.sh").read_text(encoding="utf-8")
        self.assertIn('TRANSCRIPT_SHA256=', text)
        self.assertIn('TESTS=', text)
        self.assertIn('CLIPBOARD_RECEIPT=', text)
        self.assertIn('termux-clipboard-set < "$CLIPBOARD_RECEIPT"', text)
        self.assertNotIn('termux-clipboard-set < "$TMP"', text)
        self.assertIn('cp "$TMP" "$QUALIFICATION_LOG"', text)

    def test_runner_refuses_duplicate_live_qualification_session(self):
        text = (self.repo / "engineering/pixel/loom_pixel_run.sh").read_text(encoding="utf-8")
        self.assertIn('QUALIFICATION_LOCK_DIR="${TMPDIR:-$HOME/.cache/loom}/qualification.lock"', text)
        self.assertIn('mkdir "$QUALIFICATION_LOCK_DIR"', text)
        self.assertIn("QUALIFICATION_ALREADY_RUNNING", text)
        self.assertIn('kill -0 "$LOCK_PID"', text)
        self.assertIn('rm -rf "$QUALIFICATION_LOCK_DIR"', text)

    def test_lock_cleanup_is_owned_only_by_top_level_runner(self):
        text = (self.repo / "engineering/pixel/loom_pixel_run.sh").read_text(encoding="utf-8")
        self.assertIn('QUALIFICATION_LOCK_OWNER_BASHPID="$BASHPID"', text)
        self.assertIn('[[ "$BASHPID" == "$QUALIFICATION_LOCK_OWNER_BASHPID" ]]', text)
        self.assertIn('printf \'%s\\n\' "$QUALIFICATION_LOCK_OWNER_BASHPID" > "$QUALIFICATION_LOCK_DIR/pid"', text)


if __name__ == "__main__":
    unittest.main()
