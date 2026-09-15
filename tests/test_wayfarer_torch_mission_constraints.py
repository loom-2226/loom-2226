import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
Z3 = ROOT / "engineering" / "verification" / "z3"
LIB = Z3 / "wayfarer_torch_mission_constraints_v0.1.smt2"
SYN = Z3 / "wayfarer_torch_mission_synthesis_v0.1.smt2"
NEG = Z3 / "wayfarer_torch_mission_negative_v0.1.smt2"
STATE_NEG = Z3 / "wayfarer_propulsion_state_negative_v0.1.smt2"
RUNNER = Z3 / "run_wayfarer_torch_mission_z3.sh"


class MissionConstraintTests(unittest.TestCase):
    def test_library_is_composable_and_has_no_solver_commands(self):
        text = LIB.read_text()
        self.assertIn('(include "wayfarer_torch_generated_cards_v0.1.smt2")', text)
        self.assertIn('(define-fun remass-after-t', text)
        self.assertIn('(define-fun segment-meets', text)
        self.assertIn('(define-fun propulsion-state-valid', text)
        self.assertNotIn('(check-sat)', text)
        self.assertNotIn('(get-model)', text)

    def test_mission_consumer_uses_generated_library_transitively(self):
        text = SYN.read_text()
        self.assertIn('(include "wayfarer_torch_mission_constraints_v0.1.smt2")', text)
        self.assertNotIn('4869001725', text)
        self.assertNotIn('284025100625', text)
        self.assertIn('(get-value (m1 m2 m3 m4 m5 r5))', text)

    def test_hostile_cases_enable_and_request_unsat_cores(self):
        for path, marker in ((NEG, 'H_FINAL_RESERVE'), (STATE_NEG, 'H_PROPULSION_STATE_VALID')):
            text = path.read_text()
            self.assertIn('(set-option :produce-unsat-cores true)', text)
            self.assertIn('(get-unsat-core)', text)
            self.assertIn(marker, text)
            self.assertLess(text.index('(set-option :produce-unsat-cores true)'), text.index('(check-sat)'))

    def test_runner_preserves_solver_diagnostics(self):
        text = RUNNER.read_text()
        self.assertIn('2>&1', text)
        self.assertIn('Z3 EXECUTION FAILED', text)
        self.assertIn('LOOM_Z3_WAYFARER_TORCH_MISSION_CONSTRAINT_STATUS=PASS', text)


if __name__ == '__main__':
    unittest.main()
