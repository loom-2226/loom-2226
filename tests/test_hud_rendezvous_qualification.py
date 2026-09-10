import unittest

from loom.hud.rendezvous_qualification import CONTRACT, solve_moon_rendezvous_feasibility


class HudRendezvousQualificationTests(unittest.TestCase):
    def test_contract_is_explicitly_qualification_only_surface(self):
        self.assertEqual(CONTRACT, "LOOM_HUD_RENDEZVOUS_FEASIBILITY_QUALIFICATION_V1")

    def test_invalid_mode_rejected_before_session_access(self):
        with self.assertRaises(ValueError):
            solve_moon_rendezvous_feasibility(
                None, max_time_s=21600.0, mode="NOPE", standoff_altitude_km=1000.0
            )

    def test_invalid_horizon_rejected_before_session_access(self):
        with self.assertRaises(ValueError):
            solve_moon_rendezvous_feasibility(
                None, max_time_s=100.0, mode="CRUISE", standoff_altitude_km=1000.0
            )

    def test_standoff_inside_validation_floor_fails_closed(self):
        with self.assertRaises(ValueError):
            solve_moon_rendezvous_feasibility(
                None, max_time_s=21600.0, mode="CRUISE", standoff_altitude_km=50.0
            )

    def test_standoff_above_validation_ceiling_fails_closed(self):
        with self.assertRaises(ValueError):
            solve_moon_rendezvous_feasibility(
                None, max_time_s=21600.0, mode="CRUISE", standoff_altitude_km=100001.0
            )


if __name__ == "__main__":
    unittest.main()
