import unittest
from pathlib import Path

from wayfarer_inertia_audit import build_audit

REPO_ROOT = Path(__file__).resolve().parents[2]


class Phase5BInertiaAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = build_audit(REPO_ROOT)

    def test_mass_com_compatibility(self):
        d = self.audit["docked"]
        a = self.audit["absent"]
        self.assertEqual(d["mass_kg"], 1158500.0)
        self.assertEqual(d["center_of_mass_B_m"], [26.676650841605525, 0.0, 0.14812257229175657])
        self.assertEqual(a["mass_kg"], 1125500.0)
        self.assertEqual(a["center_of_mass_B_m"], [26.819635717458908, 0.0, 0.0])

    def test_docked_parallel_axis_tensor_known_answer(self):
        I = self.audit["docked"]["parallel_axis_I_B_kg_m2"]
        expected = [
            [866902.1665947302, 0.0, 836833.2844195078],
            [0.0, 135862345.5718602, 0.0],
            [836833.2844195078, 0.0, 134995443.4052654],
        ]
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(I[i][j], expected[i][j], delta=1e-6)

    def test_absent_parallel_axis_tensor_known_answer(self):
        I = self.audit["absent"]["parallel_axis_I_B_kg_m2"]
        expected = [
            [0.0, 0.0, 0.0],
            [0.0, 134187636.0506442, 0.0],
            [0.0, 0.0, 134187636.0506442],
        ]
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(I[i][j], expected[i][j], delta=1e-6)

    def test_partial_tensor_is_not_flight_authority(self):
        for key in ("docked", "absent"):
            row = self.audit[key]
            self.assertTrue(row["parallel_axis_psd"])
            self.assertLessEqual(row["parallel_axis_symmetry_error"], 1e-12)
            self.assertEqual(row["unresolved_centroidal_inertia_mass_fraction"], 1.0)
            self.assertFalse(row["flight_dynamics_authority"])
            self.assertEqual(row["authority_code"], "WAYFARER_INERTIA_OPEN_NOT_QUALIFIED")


if __name__ == "__main__":
    unittest.main()
