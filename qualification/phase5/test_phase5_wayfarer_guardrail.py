import unittest
from pathlib import Path

from portable_dynamics import DynamicsError, VehicleState
from wayfarer_phase5_adapter import (
    WAYFARER_INERTIA_OPEN_CODE,
    build_wayfarer_connection,
    resolve_wayfarer_mass_com,
    resolve_wayfarer_mass_properties_for_6dof,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


class Phase5WayfarerGuardrailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = build_wayfarer_connection(REPO_ROOT)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_wayfarer_docked_mass_com_seam(self):
        mp = resolve_wayfarer_mass_com(self.conn, "DOCKED")
        self.assertEqual(mp["mass_kg"], 1158500.0)
        self.assertEqual(mp["center_of_mass_B_m"], [26.676650841605525, 0.0, 0.14812257229175657])

    def test_wayfarer_6dof_fails_closed_without_inertia_authority(self):
        s = VehicleState(
            0.0,
            (0.0,0.0,0.0),
            (0.0,0.0,0.0),
            (1.0,0.0,0.0,0.0),
            (0.0,0.0,0.0),
            configuration="DOCKED",
        )
        with self.assertRaisesRegex(DynamicsError, WAYFARER_INERTIA_OPEN_CODE):
            resolve_wayfarer_mass_properties_for_6dof(self.conn, s)


if __name__ == "__main__":
    unittest.main()
