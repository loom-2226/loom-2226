from __future__ import annotations

import inspect
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src" / "qualification" / "synthesis"))

import loom_navigator_core as outer_core


class ShipyardNavigatorSolvedLegProbeTest(unittest.TestCase):
    """Probe only the real embedded Navigator contracts needed for an M1 seam test."""

    def test_real_embedded_solve_dependencies_are_loadable(self):
        with TemporaryDirectory() as td:
            nav = outer_core._load_core(Path(td) / "sequence_h")
            solve_source = inspect.getsource(nav._solve_leg)
            state_source = inspect.getsource(nav._state_primary)
            burn_source = inspect.getsource(nav._torch_burn)
            self.assertIn("def _solve_leg", solve_source)
            self.assertIn("terminal_burn", solve_source)
            self.assertIn("def _state_primary", state_source)
            self.assertIn("def _torch_burn", burn_source)
            print("\n=== REAL NAVIGATOR _state_primary SOURCE ===\n")
            print(state_source)
            print("\n=== REAL NAVIGATOR _torch_burn SOURCE ===\n")
            print(burn_source)


if __name__ == "__main__":
    unittest.main()
