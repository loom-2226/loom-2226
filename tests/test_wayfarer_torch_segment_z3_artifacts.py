from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "engineering" / "verification" / "z3"


class TorchSegmentZ3ArtifactTests(unittest.TestCase):
    def test_segment_model_uses_exact_linear_remass_accounting(self):
        s = (ROOT / "wayfarer_torch_segment_constraints_v0.1.smt2").read_text()
        self.assertIn("S_SEGMENT_REMASS_IDENTITY", s)
        self.assertIn("(* mdot_kg_s segment_duration_s)", s)
        self.assertIn("S_END_REMASS_NONNEGATIVE", s)
        self.assertNotIn("log", s.lower())

    def test_synthesis_is_not_prebound_to_a_mode(self):
        s = (ROOT / "wayfarer_torch_segment_synthesis_v0.1.smt2").read_text()
        for mode in ("ECON", "CRUISE", "EXPEDITE", "FAST", "HARD", "LIMIT"):
            self.assertNotIn(f"(= mode {mode})", s)
        self.assertIn("Q_MIN_THRUST_30_MN", s)
        self.assertIn("Q_MAX_JET_POWER_12_TW", s)
        self.assertIn("Q_KEEP_200_T_REMASS", s)

    def test_positive_duration_empty_remass_is_hostile_unsat_fixture(self):
        s = (ROOT / "wayfarer_torch_segment_negative_empty_limit_v0.1.smt2").read_text()
        self.assertIn("H_REQUIRE_POSITIVE_DURATION", s)
        self.assertIn("H_REQUIRE_EMPTY_START", s)
        self.assertIn("get-unsat-core", s)

    def test_no_new_physical_efficiency_is_encoded_in_z3(self):
        s = (ROOT / "wayfarer_torch_segment_constraints_v0.1.smt2").read_text().lower()
        self.assertNotIn("efficiency", s)
        self.assertNotIn("coupling", s)
        self.assertNotIn("detachment", s)


if __name__ == "__main__":
    unittest.main()
