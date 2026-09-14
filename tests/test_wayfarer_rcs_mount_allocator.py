import unittest

from src.wayfarer_rcs_mount_allocator import build_mount_allocation_qualification


class WayfarerRCSMountAllocatorTests(unittest.TestCase):
    def test_nominal_axis_envelope_passes(self):
        payload = build_mount_allocation_qualification()
        self.assertTrue(payload["nominal"]["all_cases_pass"])

    def test_every_single_cluster_out_envelope_passes(self):
        payload = build_mount_allocation_qualification()
        self.assertTrue(all(case["all_cases_pass"] for case in payload["one_cluster_out"].values()))

    def test_mount_cap_is_respected(self):
        payload = build_mount_allocation_qualification()
        self.assertLessEqual(payload["summary"]["max_mount_utilization_fraction"], 1.0 + 1e-9)

    def test_current_configuration_com_is_consumed(self):
        payload = build_mount_allocation_qualification()
        self.assertEqual(payload["reference_state"]["mass_t"], 1158.5)
        self.assertAlmostEqual(payload["reference_state"]["center_of_mass_m"][0], 26.676650841605525)
        self.assertAlmostEqual(payload["reference_state"]["center_of_mass_m"][2], 0.14812257229175657)

    def test_allocation_is_mount_level_but_not_final_hardware(self):
        payload = build_mount_allocation_qualification()
        self.assertTrue(payload["authority"]["mount_level_bounded_allocation_requalified"])
        self.assertFalse(payload["authority"]["minimum_impulse_bit_certified"])
        self.assertFalse(payload["authority"]["finite_plume_clearance_certified"])
        self.assertFalse(payload["authority"]["structural_mount_loads_certified"])

    def test_no_canon_or_campaign_mutation(self):
        payload = build_mount_allocation_qualification()
        self.assertFalse(payload["authority"]["canon_changed"])
        self.assertEqual(payload["authority"]["campaign_state_mutation"], "ZERO")


if __name__ == "__main__":
    unittest.main()
