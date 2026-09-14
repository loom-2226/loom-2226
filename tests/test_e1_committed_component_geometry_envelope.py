import unittest

from engineering.experience_one.qualification.e1_committed_component_geometry_envelope import (
    build_e1_committed_component_geometry_envelope,
)


class E1CommittedComponentGeometryEnvelopeTests(unittest.TestCase):
    def setUp(self):
        self.result = build_e1_committed_component_geometry_envelope()

    def test_uses_deterministic_wayfarer_geometry_authority(self):
        self.assertEqual(self.result["schema"], "LOOM_E1_COMMITTED_COMPONENT_GEOMETRY_ENVELOPE_V1")
        self.assertEqual(self.result["source_geometry_schema"], "LOOM.Wayfarer.Geometry")
        self.assertEqual(self.result["source_geometry_schema_version"], "0.1")
        self.assertEqual(self.result["runtime_configuration"]["launch_attachment_state"], "DOCKED")
        self.assertEqual(self.result["runtime_configuration"]["external_attachment_state"], "FREE")
        self.assertEqual(self.result["runtime_configuration"]["deployable_structure_state"], "STOWED")

    def test_docked_launch_is_included_and_no_external_object_is_invented(self):
        ids = {c["id"] for c in self.result["committed_components"]}
        self.assertIn("planetary_launch", ids)
        self.assertIn("launch_bay", ids)
        self.assertNotIn("external_attachment", ids)
        self.assertTrue(self.result["configuration_policy"]["free_external_state_adds_no_external_component"])

    def test_union_envelope_is_numeric_and_contains_all_component_aabbs(self):
        env = self.result["component_geometry_envelope_m"]
        for axis in ("x", "y", "z"):
            self.assertLess(env[axis][0], env[axis][1])
        for component in self.result["committed_components"]:
            for axis in ("x", "y", "z"):
                self.assertLessEqual(env[axis][0], component["aabb_m"][axis][0])
                self.assertGreaterEqual(env[axis][1], component["aabb_m"][axis][1])

    def test_open_detail_is_bounded_not_promoted(self):
        self.assertEqual(self.result["disposition"], "COMMITTED_COMPONENT_GEOMETRY_ENVELOPE_PRESENT_WITH_OPEN_DETAIL_BOUNDED")
        self.assertTrue(self.result["sufficient_as_domain_containment_input"])
        self.assertTrue(self.result["open_detail_present"])
        self.assertFalse(self.result["open_detail_promoted_to_canon"])
        self.assertFalse(self.result["authority"]["certifies_translation_domain_boundary"])
        self.assertFalse(self.result["authority"]["certifies_domain_membership"])
        self.assertFalse(self.result["authority"]["certifies_domain_size"])

    def test_glb_is_not_promoted_to_authority(self):
        self.assertEqual(self.result["derivative_artifact_policy"]["glb_role"], "DERIVATIVE_CONFIRMATION_ONLY")
        self.assertFalse(self.result["derivative_artifact_policy"]["glb_is_geometry_authority"])


if __name__ == "__main__":
    unittest.main()
