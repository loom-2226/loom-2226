from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import loom_navigator_core as outer_core
from loom.navigation.service import (
    _looks_like_direct_coverage_unavailable,
    _run_acquisition_with_coverage_normalization,
)


class _Request:
    def key(self):
        return "coverage-normalization-test"

    def canonical(self):
        return {"command": "501", "center": "@5", "start": "2226-06-15", "stop": "2226-06-16"}


class CoverageNormalizationUnitTest(unittest.TestCase):
    def test_only_explicit_no_ephemeris_messages_are_classified(self):
        self.assertTrue(_looks_like_direct_coverage_unavailable(RuntimeError('No ephemeris for target "Io" after A.D. 2200-JAN-09 00:00:00.0000 TDB')))
        self.assertTrue(_looks_like_direct_coverage_unavailable(RuntimeError('No ephemeris for target "X" before A.D. 1900-JAN-01')))
        self.assertFalse(_looks_like_direct_coverage_unavailable(RuntimeError('HTTP 503 from Horizons')))
        self.assertFalse(_looks_like_direct_coverage_unavailable(RuntimeError('cache checksum mismatch')))


class CoverageNormalizationEmbeddedSequenceHFunctionalTest(unittest.TestCase):
    def _nav(self, td: str):
        return outer_core._load_core(Path(td) / "seqh")

    def _install_plan(self, nav, scope: str):
        original_window = nav.acquisition_window
        original_plan = nav.build_acquisition_plan
        nav.acquisition_window = lambda normalized: (
            nav._dt('2226-06-15T00:00:00Z'),
            nav._dt('2226-06-16T00:00:00Z'),
            {"start_utc":"2226-06-15T00:00:00Z","stop_utc":"2226-06-16T00:00:00Z","step_minutes":60},
        )
        nav.build_acquisition_plan = lambda normalized: [{
            "scope": scope,
            "system_id": "JU" if scope == "LOCAL" else None,
            "id": "IO" if scope == "LOCAL" else "MA",
            "name": "Io" if scope == "LOCAL" else "Mars",
            "request": _Request(),
        }]
        return original_window, original_plan

    def test_local_coverage_gap_uses_frozen_direct_unavailable_policy(self):
        with TemporaryDirectory() as td:
            nav = self._nav(td)
            original_fetch = nav.fetch_or_cache
            original_window, original_plan = self._install_plan(nav, "LOCAL")
            try:
                nav.fetch_or_cache = lambda *a, **k: (_ for _ in ()).throw(
                    nav.WorkflowError('No ephemeris for target "Io" after A.D. 2200-JAN-09 00:00:00.0000 TDB')
                )
                result = _run_acquisition_with_coverage_normalization(
                    nav,
                    {"test_id":"T","epoch_utc":"2226-06-15T00:00:00Z"},
                    Path(td) / "cache",
                    offline=True,
                    refresh=False,
                )
                self.assertEqual(result["direct_unavailable"], 1)
                self.assertEqual(result["entries"][0]["status"], "DIRECT_UNAVAILABLE")
                self.assertFalse(result["entries"][0].get("navigation_grade", False))
            finally:
                nav.fetch_or_cache = original_fetch
                nav.acquisition_window = original_window
                nav.build_acquisition_plan = original_plan

    def test_base_coverage_gap_still_fails_closed(self):
        with TemporaryDirectory() as td:
            nav = self._nav(td)
            original_fetch = nav.fetch_or_cache
            original_window, original_plan = self._install_plan(nav, "BASE")
            try:
                nav.fetch_or_cache = lambda *a, **k: (_ for _ in ()).throw(
                    nav.WorkflowError('No ephemeris for target "Mars" after A.D. 2200-JAN-09 00:00:00.0000 TDB')
                )
                with self.assertRaises(nav.DirectCoverageUnavailable):
                    _run_acquisition_with_coverage_normalization(
                        nav,
                        {"test_id":"T","epoch_utc":"2226-06-15T00:00:00Z"},
                        Path(td) / "cache",
                        offline=True,
                        refresh=False,
                    )
            finally:
                nav.fetch_or_cache = original_fetch
                nav.acquisition_window = original_window
                nav.build_acquisition_plan = original_plan

    def test_noncoverage_failure_is_never_downgraded(self):
        with TemporaryDirectory() as td:
            nav = self._nav(td)
            original_fetch = nav.fetch_or_cache
            original_window, original_plan = self._install_plan(nav, "LOCAL")
            try:
                nav.fetch_or_cache = lambda *a, **k: (_ for _ in ()).throw(nav.WorkflowError('HTTP 503 from Horizons'))
                with self.assertRaises(nav.WorkflowError):
                    _run_acquisition_with_coverage_normalization(
                        nav,
                        {"test_id":"T","epoch_utc":"2226-06-15T00:00:00Z"},
                        Path(td) / "cache",
                        offline=True,
                        refresh=False,
                    )
            finally:
                nav.fetch_or_cache = original_fetch
                nav.acquisition_window = original_window
                nav.build_acquisition_plan = original_plan


if __name__ == "__main__":
    unittest.main()
