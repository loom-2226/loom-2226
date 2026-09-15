from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
Z3 = ROOT / "engineering" / "verification" / "z3"


class WayfarerTorchModeZ3ArtifactTests(unittest.TestCase):
    def test_model_contains_exact_physical_identities_and_cards(self):
        text = (Z3 / "wayfarer_torch_mode_envelope_v0.1.smt2").read_text()
        self.assertIn("A_THRUST_IDENTITY", text)
        self.assertIn("A_JET_POWER_IDENTITY", text)
        for mode in ("ECON", "CRUISE", "EXPEDITE", "FAST", "HARD", "LIMIT"):
            self.assertIn(f"(= mode {mode})", text)

    def test_protected_water_and_metric_firewalls_are_preserved(self):
        text = (Z3 / "wayfarer_torch_mode_envelope_v0.1.smt2").read_text()
        self.assertIn("A_PROTECTED_WATER_FIREWALL", text)
        self.assertIn("A_TORCH_METRIC_EXCLUSION", text)

    def test_zero_remass_boundary_does_not_invent_duration_physics(self):
        text = (Z3 / "wayfarer_torch_mode_negative_zero_remass_active_v0.1.smt2").read_text()
        self.assertIn("intentionally SAT", text)
        self.assertNotIn("minimum burn", text.lower())

    def test_runner_requires_hostile_and_synthesis_cases(self):
        text = (Z3 / "run_wayfarer_torch_mode_z3.sh").read_text()
        self.assertIn("wayfarer_torch_mode_synthesis_v0.1.smt2 sat", text)
        self.assertIn("wayfarer_torch_mode_negative_power_v0.1.smt2 unsat", text)
        self.assertIn("LOOM_Z3_WAYFARER_TORCH_MODE_STATUS=PASS", text)


if __name__ == "__main__":
    unittest.main()
