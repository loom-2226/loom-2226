import unittest

from src.wayfarer_e1_torch_integrated_qualification import build_review


class WayfarerE1TorchIntegratedQualificationTests(unittest.TestCase):
    def setUp(self):
        self.review = build_review()

    def test_t5_freezes_interface_with_technology_holds(self):
        self.assertEqual(self.review["schema"], "LOOM.Wayfarer.E1TorchIntegratedQualificationReview")
        self.assertEqual(self.review["status"], "E1_INTERFACE_CLOSED_WITH_TECHNOLOGY_HOLD")
        self.assertTrue(self.review["e1_interface_frozen"])
        self.assertFalse(self.review["component_hardware_certified"])

    def test_no_e1_blockers_remain(self):
        self.assertEqual(self.review["open_blocking_e1"], [])
        self.assertEqual(self.review["counts"]["OPEN_BLOCKING_E1"], 0)

    def test_t1_through_t4_are_integrated(self):
        self.assertEqual(set(self.review["earned_interfaces"]), {"T1", "T2", "T3", "T4"})
        self.assertEqual(self.review["classifications"]["primary_torch_vehicle_contract"], "E1_INTERFACE_CLOSED")
        self.assertEqual(self.review["classifications"]["source_energy_thermal_dependency_chain"], "E1_INTERFACE_CLOSED_WITH_TECHNOLOGY_HOLD")
        self.assertEqual(self.review["classifications"]["remass_feed_nozzle_requirement_interface"], "E1_INTERFACE_CLOSED_WITH_TECHNOLOGY_HOLD")
        self.assertEqual(self.review["classifications"]["structural_plume_operational_requirement_interface"], "E1_INTERFACE_CLOSED_WITH_TECHNOLOGY_HOLD")

    def test_component_certification_holds_are_not_erased(self):
        expected = {
            "SOURCE_REACTOR_REALIZABILITY",
            "DIRECTED_ENERGY_REMASS_COUPLING_PARTITION",
            "RADIATION_AND_PARTICLE_DEPOSITION",
            "WORKING_FLUID_STORAGE_FEED_IMPLEMENTATION",
            "MAGNETIC_NOZZLE_PHYSICS_AND_LIFETIME",
            "SHIELD_MAGNET_THERMAL_LIFETIME",
            "THRUST_FRAME_DYNAMICS_LOCAL_LOAD_AND_FATIGUE",
            "PHYSICAL_PLUME_EXTERNAL_HARDWARE_CLEARANCE",
            "RCS_INTEGRATION",
        }
        self.assertEqual(set(self.review["component_certification_holds"]), expected)
        self.assertEqual(self.review["counts"]["OPEN_BLOCKING_COMPONENT_CERTIFICATION_ONLY"], len(expected))

    def test_authority_boundary_is_explicit(self):
        self.assertFalse(self.review["authority"]["reactor_source_certified"])
        self.assertFalse(self.review["authority"]["working_fluid_selected"])
        self.assertFalse(self.review["authority"]["feed_hardware_certified"])
        self.assertFalse(self.review["authority"]["magnetic_nozzle_certified"])
        self.assertFalse(self.review["authority"]["physical_plume_certified"])
        self.assertFalse(self.review["authority"]["thrust_frame_certified"])
        self.assertFalse(self.review["authority"]["radiator_hardware_certified"])
        self.assertFalse(self.review["authority"]["rcs_installation_certified"])


if __name__ == "__main__":
    unittest.main()
