import copy
import math
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import loom_navigator_core as campaign
from qualification.synthesis.shipyard_campaign_binding import validate_campaign_binding
from qualification.synthesis.vehicle_dynamics_contract import build_wayfarer_contract_family


class ShipyardRealNavigatorLegTests(unittest.TestCase):
    """Consumer-boundary test for the real embedded NAV-V1-A leg solver.

    The ephemeris rows below are deterministic interface fixtures only. They are
    intentionally not claimed as authoritative Solar-System states, route
    qualification evidence, or a replacement for Navigator acquisition/B1.
    """

    @classmethod
    def setUpClass(cls):
        cls.contract = build_wayfarer_contract_family(2226)[0]

    @staticmethod
    def _fixture_rows(hours=49):
        # Navigator row shape: [source_time, x_AU, y_AU, z_AU,
        #                       vx_AU_day, vy_AU_day, vz_AU_day].
        # Keep the destination kinematically consistent with its small x velocity
        # so interpolation exercises the real row path rather than a constant stub.
        origin = []
        dest = []
        dest_x0_au = 0.02
        dest_vx_au_day = 0.001
        for hour in range(hours + 1):
            day = hour / 24.0
            source_time = float(hour)
            origin.append((source_time, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
            dest.append(
                (
                    source_time,
                    dest_x0_au + dest_vx_au_day * day,
                    0.0,
                    0.0,
                    dest_vx_au_day,
                    0.0,
                    0.0,
                )
            )
        return origin, dest

    def test_bound_campaign_state_reaches_real_solve_leg_and_remass_gate(self):
        state = campaign._new_state("SHIPYARD-REAL-LEG-TEST", "WAYFARER-TEST")
        before = copy.deepcopy(state)

        binding = validate_campaign_binding(self.contract, state)
        self.assertTrue(binding["compatible_for_navigator_consumption"])
        self.assertEqual(binding["campaign_wet_mass_t"], state["ship"]["wet_mass_t"])

        departure = datetime(2226, 8, 1, 0, 0, 0, tzinfo=timezone.utc)
        axis = {
            "start_utc": departure.isoformat().replace("+00:00", "Z"),
            "step_seconds": 3600.0,
        }
        origin_rows, dest_rows = self._fixture_rows()

        with tempfile.TemporaryDirectory() as td:
            nav = campaign._load_core(Path(td))
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

        burn = leg["terminal_burn"]
        used = float(burn["remass_used_t"])

        self.assertEqual(leg["solver_model"], "NAV-V1-A")
        self.assertEqual(leg["solver_version"], "1.1")
        self.assertEqual(leg["metric_mode"], "NORMAL")
        self.assertEqual(leg["torch_mode"], "CRUISE")
        self.assertEqual(burn["wet_mass_start_t"], state["ship"]["wet_mass_t"])
        self.assertTrue(math.isfinite(used))
        self.assertGreater(used, 0.0)
        self.assertLessEqual(used, state["ship"]["remass_t"] + 1e-9)
        self.assertGreater(float(leg["metric_segment"]["distance_km"]), 0.0)
        self.assertGreater(float(leg["arrival"]["total_nav_time_s"]), 0.0)
        self.assertLess(abs(float(leg["root_solver"]["root_residual_s"])), 1e-6)
        self.assertEqual(len(leg["engineering_checkpoints"]), 5)

        # Solving consumes the bound campaign values as inputs; it does not commit
        # campaign state or elevate any Shipyard authority by itself.
        self.assertEqual(state, before)
        self.assertFalse(binding["navigator_authority_changed"])
        self.assertFalse(binding["flight_dynamics_authority"])
        self.assertFalse(binding["canon_changed"])
        self.assertFalse(binding["production_shipclasses_changed"])


if __name__ == "__main__":
    unittest.main()
