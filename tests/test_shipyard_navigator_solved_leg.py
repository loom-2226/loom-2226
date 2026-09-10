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
    """Probe the real embedded Navigator solve boundary before fixing a fixture.

    This intentionally does not claim M1 closure.  It proves CI can load the
    exact embedded Sequence-H solver owned by Navigator and exposes the source
    shape needed to bind a governed deterministic ephemeris fixture without
    replacing ``_solve_leg``.
    """

    def test_real_embedded_solve_leg_is_loadable(self):
        with TemporaryDirectory() as td:
            nav = outer_core._load_core(Path(td) / "sequence_h")
            solve = nav._solve_leg
            self.assertTrue(callable(solve))
            source = inspect.getsource(solve)
            self.assertIn("def _solve_leg", source)
            self.assertIn("remass_used_t", source)
            print("\n=== REAL NAVIGATOR _solve_leg SOURCE ===\n")
            print(source)


if __name__ == "__main__":
    unittest.main()
