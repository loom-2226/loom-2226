import math
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import loom_navigator_core as campaign
from qualification.synthesis.generative_candidate_compiler import compile_wayfarer_survivor_family
from qualification.synthesis.shipyard_campaign_binding import validate_campaign_binding
from qualification.synthesis.shipyard_m2a_attitude_coupling import maneuver_aware_leg_summary
from qualification.synthesis.vehicle_dynamics_contract import build_vehicle_dynamics_contract


class ShipyardM2ARealNavigatorLegTests(unittest.TestCase):
    @staticmethod
    def _fixture_rows(hours=49):
        origin = []
        dest = []
        dest_x0_au = 0.02
        dest_vx_au_day = 0.001
        for hour in range(hours + 1):
            day = hour / 24.0
            source_time = float(hour)
            origin.append((source_time, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
            dest.append((source_time, dest_x0_au + dest_vx_au_day * day, 0.0, 0.0, dest_vx_au_day, 0.0, 0.0))
        return origin, dest

    def test_real_nav_v1a_raw_leg_is_constant_but_maneuver_aware_result_differs(self):
        family = compile_wayfarer_survivor_family(2226)
        self.assertGreaterEqual(len(family), 2)

        departure = datetime(2226, 8, 1, 0, 0, 0, tzinfo=timezone.utc)
        axis = {
            "start_utc": departure.isoformat().replace("+00:00", "Z"),
            "step_seconds": 3600.0,
        }
        origin_rows, dest_rows = self._fixture_rows()
        raw_times = []
        raw_remass = []
        coupled = []

        with tempfile.TemporaryDirectory() as td:
            nav = campaign._load_core(Path(td))
            for artifact in family:
                contract = build_vehicle_dynamics_contract(artifact)
                state = campaign._new_state("SHIPYARD-M2A-REAL-LEG", artifact.candidate_id)
                binding = validate_campaign_binding(contract, state)
                self.assertTrue(binding["compatible_for_navigator_consumption"])

                leg = nav._solve_leg(
                    "SHIPYARD_FIXTURE_ORIGIN",
                    "SHIPYARD_FIXTURE_DEST",
                    departure,
                    origin_rows,
                    dest_rows,
                    axis,
                    "NORMAL",
                    "CRUISE",
                    state["ship"]["wet_mass_t"],
                )
                self.assertEqual(leg["solver_model"], "NAV-V1-A")
                self.assertEqual(leg["solver_version"], "1.1")
                raw_times.append(float(leg["arrival"]["total_nav_time_s"]))
                raw_remass.append(float(leg["terminal_burn"]["remass_used_t"]))
                coupled.append(maneuver_aware_leg_summary(artifact, leg))

        # Current S1 family intentionally holds mass, remass and torch cards fixed.
        # Therefore raw translational Navigator output must remain the same; if it
        # differs, M2-A has accidentally introduced another physical driver.
        self.assertEqual(len({round(v, 9) for v in raw_times}), 1)
        self.assertEqual(len({round(v, 9) for v in raw_remass}), 1)
        self.assertTrue(all(math.isfinite(v) and v > 0 for v in raw_times))

        # Layout changes are admitted through Q4-v0.4 inertia/attitude mechanics,
        # so the finite brake-flip penalty and maneuver-aware mission time must vary.
        self.assertGreater(len({round(row["brake_flip_time_s"], 9) for row in coupled}), 1)
        self.assertGreater(len({round(row["maneuver_aware_total_time_s"], 9) for row in coupled}), 1)
        self.assertTrue(all(not row["raw_navigator_output_modified"] for row in coupled))
        self.assertTrue(all(row["m2a_disposition"] == "COUPLED_MISSION_DIFFERENTIATION_DEMONSTRATED" for row in coupled))


if __name__ == "__main__":
    unittest.main()
