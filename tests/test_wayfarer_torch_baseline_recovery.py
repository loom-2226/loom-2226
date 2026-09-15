from __future__ import annotations

import unittest

from src.wayfarer_torch_baseline_recovery import build_torch_baseline_recovery


class WayfarerTorchBaselineRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = build_torch_baseline_recovery()

    def test_current_authority_is_recovered_without_new_physics(self) -> None:
        self.assertEqual(self.result["status"], "PASS")
        self.assertEqual(self.result["authority"]["claim"], "E1_TORCH_BASELINE_RECOVERY_ONLY")
        self.assertFalse(self.result["authority"]["new_torch_physics_invented"])
        self.assertFalse(self.result["authority"]["canon_changed"])
        self.assertEqual(self.result["authority"]["campaign_state_mutation"], "ZERO")
        self.assertEqual(self.result["authority"]["llm_calculation_authority"], "ZERO")

    def test_governed_vehicle_interfaces_are_preserved(self) -> None:
        vehicle = self.result["vehicle_interfaces"]
        self.assertEqual(vehicle["primary_torch_count"], 1)
        self.assertEqual(vehicle["architecture"], "AXIAL_FUSION_TORCH_WITH_MAGNETIC_NOZZLE")
        self.assertEqual(vehicle["working_fluid_water_inventory_t"], 300.0)
        self.assertEqual(vehicle["normal_remass_allowance_t"], 250.0)
        self.assertEqual(vehicle["protected_water_reserve_t"], 50.0)
        self.assertEqual(vehicle["reference_wet_mass_t"], 1158.5)

    def test_operating_cards_are_recovered_exactly(self) -> None:
        cards = self.result["exhaust_velocity_cards_km_s"]
        self.assertEqual(cards, {
            "ECON": 3000.0,
            "CRUISE": 2000.0,
            "EXPEDITE": 1000.0,
            "FAST": 700.0,
            "HARD": 450.0,
            "LIMIT": 300.0,
        })

    def test_packaging_envelopes_are_candidates_not_certified_detail(self) -> None:
        p = self.result["candidate_packaging"]
        self.assertEqual(p["shadow_shield_x_m"], [38.0, 43.0])
        self.assertEqual(p["reactor_torch_machinery_x_m"], [43.0, 50.0])
        self.assertEqual(p["magnetic_nozzle_x_m"], [50.0, 57.0])
        self.assertFalse(self.result["authority"]["reactor_internal_design_certified"])
        self.assertFalse(self.result["authority"]["magnetic_coil_geometry_certified"])
        self.assertFalse(self.result["authority"]["torch_plume_envelope_certified"])
        self.assertFalse(self.result["authority"]["thermal_plumbing_certified"])

    def test_rcs_holds_are_carried_into_torch_integration(self) -> None:
        holds = set(self.result["carried_rcs_integration_holds"])
        self.assertIn("PHYSICAL_PLUME_MODEL_AND_CLEARANCE_SWEEP", holds)
        self.assertIn("WORKING_FLUID_CYCLE_EXHAUST_VELOCITY_AND_THERMAL_LOAD", holds)
        self.assertIn("MOUNT_LOAD_PATH_LOCAL_STRUCTURE_AND_REINFORCEMENT", holds)
        self.assertEqual(
            self.result["qualified_next_step"],
            "DERIVE_TORCH_PERFORMANCE_AND_REMASS_REQUIREMENT_ENVELOPE_FROM_RECOVERED_OPERATING_CARDS_AND_CURRENT_MASS_STATE",
        )


if __name__ == "__main__":
    unittest.main()
