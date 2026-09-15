import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
Z3 = ROOT / 'engineering' / 'verification' / 'z3'
LIB = Z3 / 'wayfarer_shipyard_constraints_v0.1.smt2'
SYN = Z3 / 'wayfarer_shipyard_synthesis_v0.1.smt2'
HOSTILE = Z3 / 'wayfarer_shipyard_hostile_v0.1.smt2'
MASS_HOSTILE = Z3 / 'wayfarer_shipyard_mass_hostile_v0.1.smt2'
RUNNER = Z3 / 'run_wayfarer_shipyard_z3.sh'


class ShipyardConstraintTests(unittest.TestCase):
    def test_library_has_current_and_candidate_boundaries(self):
        text = LIB.read_text()
        self.assertIn('Current vehicle identities.', text)
        self.assertIn('Candidate dry-mass ledger', text)
        self.assertIn('candidate-ledger-valid', text)
        self.assertIn('aft-torch-packaging-valid', text)
        self.assertIn('configuration-valid', text)
        self.assertNotIn('(check-sat)', text)

    def test_current_mass_and_grammar_identities_are_explicit(self):
        text = LIB.read_text()
        for token in ('858.5', '300.0', '250.0', '50.0', '(= tanks 4)', '(= longerons 4)', '(= radiators 4)', '(= torch-count 1)'):
            self.assertIn(token, text)

    def test_synthesis_keeps_candidate_inputs_visibly_named(self):
        text = SYN.read_text()
        self.assertIn('CANDIDATE_LEDGER', text)
        self.assertIn('CANDIDATE_AFT_PACKAGING', text)
        self.assertIn('(get-value (launch radiators torch high-metric))', text)

    def test_hostile_proofs_enable_unsat_cores(self):
        for path in (HOSTILE, MASS_HOSTILE):
            text = path.read_text()
            self.assertIn('(set-option :produce-unsat-cores true)', text)
            self.assertIn('(get-unsat-core)', text)

    def test_runner_preserves_native_solver_diagnostics(self):
        text = RUNNER.read_text()
        self.assertIn('2>&1', text)
        self.assertIn('Z3 EXECUTION FAILED', text)
        self.assertIn('LOOM_Z3_WAYFARER_COMPUTATIONAL_SHIPYARD_SLICE1_STATUS=PASS', text)


if __name__ == '__main__':
    unittest.main()
