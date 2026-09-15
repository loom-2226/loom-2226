from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "engineering" / "verification" / "z3"


class MultiSegmentZ3Tests(unittest.TestCase):
    def test_planner_chains_remass_exactly(self):
        s = (ROOT / "wayfarer_torch_multisegment_synthesis_v0.1.smt2").read_text()
        self.assertIn("M_REMASS_AFTER_1", s)
        self.assertIn("M_REMASS_AFTER_2", s)
        self.assertIn("M_REMASS_AFTER_3", s)
        self.assertIn("Q_FINAL_RESERVE_180_T", s)

    def test_planner_does_not_prebind_modes(self):
        s = (ROOT / "wayfarer_torch_multisegment_synthesis_v0.1.smt2").read_text()
        self.assertNotIn("(= mode FAST)", s)
        self.assertNotIn("(= mode2", s)
        self.assertNotIn("(= mode3", s)

    def test_no_trajectory_or_unknown_physics_smuggled_into_smt(self):
        s = (ROOT / "wayfarer_torch_multisegment_synthesis_v0.1.smt2").read_text().lower()
        for forbidden in ("log", "delta_v", "coupling_efficiency", "nozzle_efficiency", "detachment", "fusion_gain"):
            self.assertNotIn(forbidden, s)

    def test_hostile_fixture_demands_unsat_core(self):
        s = (ROOT / "wayfarer_torch_multisegment_negative_v0.1.smt2").read_text()
        self.assertIn("H_LIMIT_MODE", s)
        self.assertIn("H_REQUIRE_200_T_RESERVE", s)
        self.assertIn("get-unsat-core", s)


if __name__ == "__main__":
    unittest.main()
