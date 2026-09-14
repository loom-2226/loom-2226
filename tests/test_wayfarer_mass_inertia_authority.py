import math
import unittest

from src.wayfarer_mass_inertia_authority import build_mass_inertia_state


class WayfarerMassInertiaAuthorityTests(unittest.TestCase):
    def test_reference_wet_docked_mass_and_configuration(self):
        state = build_mass_inertia_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
        self.assertTrue(math.isclose(state["mass_t"], 1158.5, rel_tol=0.0, abs_tol=1e-9))
        self.assertEqual(state["launch_state"], "DOCKED")
        self.assertEqual(state["depletion_doctrine"], "BALANCED_FOUR_TANK_DRAW")

    def test_launch_absent_changes_mass_and_center_of_mass(self):
        docked = build_mass_inertia_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
        absent = build_mass_inertia_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=False)
        self.assertTrue(math.isclose(docked["mass_t"] - absent["mass_t"], 33.0, rel_tol=0.0, abs_tol=1e-9))
        self.assertNotEqual(docked["center_of_mass_m"], absent["center_of_mass_m"])

    def test_tensor_is_symmetric_positive_definite_and_configuration_aware(self):
        state = build_mass_inertia_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
        tensor = state["inertia_tensor_kg_m2"]
        for i in range(3):
            for j in range(3):
                self.assertTrue(math.isclose(tensor[i][j], tensor[j][i], rel_tol=0.0, abs_tol=1e-6))
        self.assertTrue(state["tensor_checks"]["symmetric"])
        self.assertTrue(state["tensor_checks"]["positive_definite_sylvester"])
        depleted = build_mass_inertia_state(normal_remass_t=0.0, protected_water_t=50.0, launch_docked=True)
        self.assertNotEqual(state["inertia_tensor_kg_m2"], depleted["inertia_tensor_kg_m2"])

    def test_intrinsic_inertia_is_explicit_and_exceeds_centroid_only_roll(self):
        state = build_mass_inertia_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
        self.assertTrue(state["intrinsic_component_inertia_included"])
        self.assertGreater(
            state["inertia_tensor_kg_m2"][0][0],
            state["centroid_only_comparator"]["inertia_tensor_kg_m2"][0][0],
        )
        self.assertGreater(state["model_delta_from_centroid_only"]["roll_Ixx_added_kg_m2"], 0.0)

    def test_assumptions_and_authority_are_not_hidden(self):
        state = build_mass_inertia_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
        self.assertEqual(state["authority"]["status"], "ENGINEERING_MODEL_FOR_RCS_REQUALIFICATION")
        self.assertFalse(state["authority"]["canon_changed"])
        self.assertFalse(state["authority"]["structural_fea_authority"])
        self.assertFalse(state["authority"]["fluid_slosh_authority"])
        self.assertGreater(len(state["equivalent_shape_assumptions"]), 0)
        self.assertIn("radiator_deployed_mass_distribution", state["open_physics"])

    def test_invalid_store_states_fail_closed(self):
        for remass in (-0.1, 250.1):
            with self.assertRaises(ValueError):
                build_mass_inertia_state(normal_remass_t=remass, protected_water_t=50.0, launch_docked=True)
        for water in (-0.1, 50.1):
            with self.assertRaises(ValueError):
                build_mass_inertia_state(normal_remass_t=250.0, protected_water_t=water, launch_docked=True)


if __name__ == "__main__":
    unittest.main()
