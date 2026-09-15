import unittest

from src.wayfarer_torch_feed_dynamics_nozzle import build_envelope, evaluate_candidate


class TorchFeedDynamicsNozzleTests(unittest.TestCase):
    def test_authority_firewalls_and_open_inputs(self):
        r = build_envelope()
        self.assertFalse(r["authority"]["working_fluid_selected"])
        self.assertFalse(r["authority"]["hardware_certified"])
        self.assertEqual(r["authority"]["campaign_state_mutation"], "ZERO")
        self.assertIsNone(r["candidate_inputs"]["feed_response_time_s"])
        self.assertIsNone(r["candidate_inputs"]["coupling_efficiency"])
        self.assertIsNone(r["candidate_inputs"]["nozzle_efficiency"])

    def test_earned_feed_envelope_preserved(self):
        r = build_envelope()
        self.assertEqual(r["requirements"]["normal_remass_kg"], 250000.0)
        self.assertEqual(r["requirements"]["protected_water_kg"], 50000.0)
        self.assertAlmostEqual(r["requirements"]["peak_mass_flow_kg_s"], 284.025100625)
        self.assertAlmostEqual(r["requirements"]["turndown_ratio"], 284.025100625 / 1.1361004025)
        self.assertEqual(r["firewall"], "PROTECTED_50_T_WATER_RESERVE_IS_NOT_NORMAL_REMASS")

    def test_explicit_candidate_derives_coupled_power_without_certification(self):
        r = evaluate_candidate(
            mode="FAST",
            feed_response_time_s=0.25,
            coupling_efficiency=0.8,
            nozzle_efficiency=0.9,
        )
        self.assertEqual(r["mode"], "FAST")
        self.assertGreater(r["required_pre_coupling_power_W"], r["jet_power_W"])
        self.assertFalse(r["certified"])
        self.assertEqual(r["status"], "SENSITIVITY_ONLY_EXPLICIT_INPUTS")

    def test_candidate_inputs_must_be_physical(self):
        with self.assertRaises(ValueError):
            evaluate_candidate("FAST", 0.25, 0.0, 0.9)
        with self.assertRaises(ValueError):
            evaluate_candidate("FAST", -1.0, 0.8, 0.9)
        with self.assertRaises(ValueError):
            evaluate_candidate("NOPE", 0.25, 0.8, 0.9)


if __name__ == "__main__":
    unittest.main()
