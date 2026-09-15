import unittest

from src.wayfarer_torch_integrated_architecture_readiness import build_readiness_review


class TorchIntegratedArchitectureReadinessTests(unittest.TestCase):
    def test_review_does_not_overclaim_component_freeze(self):
        r = build_readiness_review()
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(r["authority"]["claim"], "E1_TORCH_INTEGRATED_VEHICLE_ARCHITECTURE_FREEZE_READINESS_ONLY")
        self.assertFalse(r["authority"]["component_architecture_frozen"])
        self.assertFalse(r["authority"]["reactor_fuel_nozzle_certified"])
        self.assertFalse(r["authority"]["physical_plume_certified"])

    def test_earned_interfaces_are_integrated(self):
        r = build_readiness_review()
        earned = r["earned_interfaces"]
        self.assertIn("PERFORMANCE_AND_REMASS_ENVELOPE", earned)
        self.assertIn("THERMAL_SHIELD_THRUST_FRAME_REQUIREMENT_ENVELOPE", earned)
        self.assertIn("REACTOR_NOZZLE_TECHNOLOGY_FAMILY_TRADE", earned)
        self.assertIn("DEPOSITION_PARTITION_ACCOUNTING_CONTRACT", earned)
        self.assertIn("REMASS_COUPLING_MAGNETIC_NOZZLE_ENVELOPE", earned)
        self.assertIn("PHYSICAL_PLUME_EXTERNAL_CLEARANCE_REQUIREMENT_ENVELOPE", earned)

    def test_open_physics_blocks_component_freeze(self):
        r = build_readiness_review()
        self.assertEqual(r["freeze_readiness"]["decision"], "NOT_READY_FOR_COMPONENT_ARCHITECTURE_FREEZE")
        blockers = r["freeze_readiness"]["blocking_holds"]
        self.assertIn("PHYSICAL_DEPOSITION_PARTITION_BOUNDS", blockers)
        self.assertIn("REMASS_COUPLING_AND_NOZZLE_EFFICIENCY_BOUNDS", blockers)
        self.assertIn("PHYSICAL_PLUME_BY_MODE", blockers)
        self.assertIn("SHIELD_MAGNET_THERMAL_AND_STRUCTURE_LIFETIME_CLOSURE", blockers)

    def test_vehicle_topology_remains_stable(self):
        r = build_readiness_review()
        topo = r["stable_vehicle_topology"]
        self.assertEqual(topo["primary_torch_count"], 1)
        self.assertEqual(topo["architecture"], "AXIAL_FUSION_TORCH_WITH_MAGNETIC_NOZZLE")
        self.assertEqual(topo["normal_remass_t"], 250.0)
        self.assertEqual(topo["protected_water_reserve_t"], 50.0)

    def test_next_step_targets_physical_bounds_not_fake_freeze(self):
        self.assertEqual(
            build_readiness_review()["qualified_next_step"],
            "TORCH_PHYSICAL_BOUNDS_CLOSURE_CAMPAIGN",
        )


if __name__ == "__main__":
    unittest.main()
