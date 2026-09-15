import unittest

from src.wayfarer_rcs_installation_feasibility import build_installation_feasibility


class TestWayfarerRCSInstallationFeasibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = build_installation_feasibility()

    def test_binds_downselected_vehicle_architecture(self):
        r = self.result
        self.assertEqual(r["status"], "PASS_WITH_DEFERRED_COMPONENT_DETAIL")
        self.assertEqual(r["source_architecture_claim"], "RCS_ARCHITECTURE_FAMILY_DOWNSELECT_ONLY")
        self.assertEqual(r["installation_basis"]["mount_count"], 16)

    def test_installation_axes_are_explicit(self):
        axes = self.result["installation_axes"]
        self.assertEqual(axes["finite_plume"], "REQUIRED_BEFORE_COMPONENT_INSTALLATION_RELEASE")
        self.assertEqual(axes["radiator_external_hardware"], "CONFIGURATION_SWEEP_REQUIRED_WITH_PHYSICAL_PLUME_MODEL")
        self.assertEqual(axes["thermal"], "COMPONENT_HEAT_LOAD_AND_REJECTION_REQUIRED_AFTER_CYCLE_SELECTION")
        self.assertEqual(axes["structure"], "MOUNT_LOAD_PATH_AND_LOCAL_REINFORCEMENT_REQUIRED")

    def test_no_unearned_physical_clearance_or_load_claim(self):
        a = self.result["authority"]
        self.assertFalse(a["finite_plume_clearance_certified"])
        self.assertFalse(a["thermal_installation_certified"])
        self.assertFalse(a["structural_mount_loads_certified"])
        self.assertFalse(a["component_detailed_design_certified"])
        self.assertEqual(a["campaign_state_mutation"], "ZERO")
        self.assertEqual(a["llm_calculation_authority"], "ZERO")

    def test_vehicle_architecture_can_freeze_without_fake_component_detail(self):
        freeze = self.result["freeze_decision"]
        self.assertEqual(freeze["scope"], "E1_RCS_VEHICLE_ARCHITECTURE")
        self.assertEqual(freeze["decision"], "FREEZE_WITH_COMPONENT_INSTALLATION_HOLDS")
        self.assertTrue(freeze["torch_work_may_begin"])
        self.assertFalse(freeze["component_installation_release"])

    def test_open_holds_follow_into_integrated_vehicle_engineering(self):
        holds = set(self.result["component_installation_holds"])
        self.assertIn("PHYSICAL_PLUME_MODEL_AND_CLEARANCE_SWEEP", holds)
        self.assertIn("WORKING_FLUID_CYCLE_EXHAUST_VELOCITY_AND_THERMAL_LOAD", holds)
        self.assertIn("MIB_VALVE_RESPONSE_DUTY_TOTAL_IMPULSE_AND_CYCLE_LIFE", holds)
        self.assertIn("MOUNT_LOAD_PATH_LOCAL_STRUCTURE_AND_REINFORCEMENT", holds)
        self.assertEqual(self.result["qualified_next_step"], "BEGIN_TORCH_ENGINEERING_WITH_RCS_INSTALLATION_HOLDS_CARRIED_AS_INTEGRATION_CONSTRAINTS")


if __name__ == "__main__":
    unittest.main()
