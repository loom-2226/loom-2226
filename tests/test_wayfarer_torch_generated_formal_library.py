from pathlib import Path
import unittest

from engineering.verification.z3.generate_wayfarer_torch_formal_library import generate
from src.wayfarer_torch_mode_cards import MODE_CARDS, mode_outputs

ROOT = Path(__file__).resolve().parents[1]
SMT = ROOT / "engineering/verification/z3/wayfarer_torch_generated_cards_v0.1.smt2"


class GeneratedFormalLibraryTests(unittest.TestCase):
    def test_checked_in_smt_is_exact_generator_output(self):
        self.assertEqual(SMT.read_text(), generate())

    def test_exact_mode_outputs_are_derived_not_rounded_literals(self):
        for mode in MODE_CARDS:
            mdot, ve, thrust, pjet = mode_outputs(mode)
            self.assertEqual(thrust, mdot * ve)
            self.assertEqual(pjet, mdot * ve * ve / 2)

    def test_generator_has_no_solver_commands(self):
        text = generate().lower()
        self.assertNotIn("check-sat", text)
        self.assertNotIn("get-model", text)
        self.assertNotIn("get-unsat-core", text)

    def test_off_is_zero_and_non_torch_by_construction(self):
        text = generate()
        self.assertIn("TorchMode OFF", text)
        self.assertIn("mode-torch-active", text)
        self.assertIn("(not (= m OFF))", text)


if __name__ == "__main__":
    unittest.main()
