import pathlib
import unittest


class PixelAssistedQualificationContractTests(unittest.TestCase):
    def setUp(self):
        self.repo = pathlib.Path(__file__).resolve().parents[1]

    def test_raw_runner_remains_available_and_separate(self):
        raw = self.repo / "engineering/pixel/loom_pixel_run.sh"
        assisted = self.repo / "engineering/pixel/loom_pixel_run_assisted.sh"
        self.assertTrue(raw.is_file())
        self.assertTrue(assisted.is_file())
        text = assisted.read_text(encoding="utf-8")
        self.assertIn("loom_pixel_run.sh", text)
        self.assertIn("LOOM ASSISTED QUALIFICATION", text)

    def test_raw_runner_fetches_before_choosing_qualification_branch(self):
        text = (self.repo / "engineering/pixel/loom_pixel_run.sh").read_text(encoding="utf-8")
        self.assertIn("git fetch origin", text)
        self.assertIn("origin/main:engineering/pixel/active_qualification.txt", text)
        self.assertIn("git merge-base --is-ancestor", text)
        self.assertIn("CURRENT_UNMERGED_SELF_QUALIFICATION", text)
        self.assertIn("ORIGIN_MAIN_ACTIVE_QUALIFICATION", text)
        self.assertIn("git switch", text)
        self.assertIn("git pull --ff-only", text)

    def test_raw_runner_prefers_governed_remote_qualification_pointer(self):
        text = (self.repo / "engineering/pixel/loom_pixel_run.sh").read_text(encoding="utf-8")
        self.assertIn('QUALIFICATION_POINTER_REF="origin/qualification/active"', text)
        self.assertIn('git show "$QUALIFICATION_POINTER_REF:engineering/pixel/active_qualification.txt"', text)
        self.assertIn("REMOTE_QUALIFICATION_POINTER", text)
        self.assertIn('BOOTSTRAP_AUTHORITY="$QUALIFICATION_POINTER_REF"', text)

    def test_raw_runner_only_self_qualifies_when_current_branch_config_points_to_itself(self):
        text = (self.repo / "engineering/pixel/loom_pixel_run.sh").read_text(encoding="utf-8")
        self.assertIn('[[ "$LOCAL_CONFIG_BRANCH" == "$CURRENT_BRANCH" ]]', text)
        self.assertIn('git merge-base --is-ancestor "$CURRENT_HEAD" origin/main', text)
        self.assertIn("CURRENT_BRANCH_MERGED_INTO_ORIGIN_MAIN", text)

    def test_raw_runner_exports_repo_root_pythonpath_and_uses_login_shell(self):
        text = (self.repo / "engineering/pixel/loom_pixel_run.sh").read_text(encoding="utf-8")
        self.assertIn('export PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"', text)
        self.assertIn('bash -lc "$QUAL_COMMAND"', text)

    def test_assisted_runner_inherits_raw_runner_branch_bootstrap(self):
        text = (self.repo / "engineering/pixel/loom_pixel_run_assisted.sh").read_text(encoding="utf-8")
        self.assertIn('RAW_RUNNER="$SCRIPT_DIR/loom_pixel_run.sh"', text)
        self.assertIn('bash "$RAW_RUNNER"', text)

    def test_assisted_runner_surfaces_governed_qualification_disposition_markers(self):
        text = (self.repo / "engineering/pixel/loom_pixel_run_assisted.sh").read_text(encoding="utf-8")
        self.assertIn("grep -E", text)
        self.assertIn("QUALIFICATION_AXIS", text)
        self.assertIn("QUALIFICATION_DISPOSITION", text)
        self.assertIn("QUALIFICATION_MISSING_REQUIRED_EVIDENCE", text)
        self.assertIn("QUALIFICATION_SUMMARY", text)
        self.assertIn("append_qualification_summary", text)

    def test_assisted_runner_uses_detached_temp_worktree_and_no_git_authority(self):
        text = (self.repo / "engineering/pixel/loom_pixel_run_assisted.sh").read_text(encoding="utf-8")
        self.assertIn("git worktree add --detach", text)
        self.assertIn("LOOM_ASSISTED_MAX_ATTEMPTS", text)
        self.assertNotIn("git commit", text)
        self.assertNotIn("git push", text)
        self.assertIn("LOCAL_REPAIR_CANDIDATE_PASS", text)
        self.assertIn("GOVERNED_QUALIFICATION_PASS", text)

    def test_repair_agent_is_bounded_to_pixel_engineering_files(self):
        from engineering.pixel.mechanical_repair import is_editable_path

        self.assertTrue(is_editable_path("engineering/pixel/spatial_review.py"))
        self.assertTrue(is_editable_path("engineering/pixel/loom_pixel_run.sh"))
        self.assertFalse(is_editable_path("tests/test_pixel_spatial_review.py"))
        self.assertFalse(is_editable_path("src/loom_navigator_core.py"))
        self.assertFalse(is_editable_path("data/LOOM_2226.sqlite3"))
        self.assertFalse(is_editable_path("canon/anything.md"))
        self.assertFalse(is_editable_path("engineering/pixel/active_qualification.txt"))

    def test_repair_agent_uses_responses_api_and_structured_output(self):
        text = (self.repo / "engineering/pixel/mechanical_repair.py").read_text(encoding="utf-8")
        self.assertIn("https://api.openai.com/v1/responses", text)
        self.assertIn("gpt-5.6-terra", text)
        self.assertIn('"type": "json_schema"', text)
        self.assertIn("OPENAI_API_KEY", text)

    def test_repair_agent_exact_replacements_only(self):
        from engineering.pixel.mechanical_repair import apply_exact_replacements
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            p = root / "engineering/pixel/example.py"
            p.parent.mkdir(parents=True)
            p.write_text("alpha\nbeta\n", encoding="utf-8")
            applied = apply_exact_replacements(
                root,
                [{"path": "engineering/pixel/example.py", "old": "beta", "new": "gamma"}],
            )
            self.assertEqual(applied, ["engineering/pixel/example.py"])
            self.assertEqual(p.read_text(encoding="utf-8"), "alpha\ngamma\n")

    def test_candidate_patch_generator_does_not_require_worktree_git_metadata(self):
        from engineering.pixel.candidate_patch import build_candidate_patch
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td) / "base"
            repaired = pathlib.Path(td) / "repaired"
            rel = pathlib.Path("engineering/pixel/example.py")
            (base / rel).parent.mkdir(parents=True)
            (repaired / rel).parent.mkdir(parents=True)
            (base / rel).write_text("alpha\nbeta\n", encoding="utf-8")
            (repaired / rel).write_text("alpha\ngamma\n", encoding="utf-8")
            patch = build_candidate_patch(base, repaired, [rel.as_posix()])
            self.assertIn("--- a/engineering/pixel/example.py", patch)
            self.assertIn("+++ b/engineering/pixel/example.py", patch)
            self.assertIn("-beta", patch)
            self.assertIn("+gamma", patch)

    def test_assisted_runner_packages_candidate_without_git_diff_in_worktree(self):
        text = (self.repo / "engineering/pixel/loom_pixel_run_assisted.sh").read_text(encoding="utf-8")
        self.assertIn("candidate_patch.py", text)
        self.assertNotIn('git -C "$WORKTREE" diff', text)

    def test_installer_creates_two_distinct_termux_shortcuts(self):
        text = (self.repo / "engineering/pixel/install_qualify_shortcuts.sh").read_text(encoding="utf-8")
        self.assertIn("LOOM_Qualify.sh", text)
        self.assertIn("LOOM_Qualify_AI.sh", text)
        self.assertIn("loom_pixel_run.sh", text)
        self.assertIn("loom_pixel_run_assisted.sh", text)


if __name__ == "__main__":
    unittest.main()
