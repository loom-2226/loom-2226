from __future__ import annotations

import copy
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import loom_navigator_core as outer_core
from qualification.synthesis.shipyard_campaign_binding import validate_campaign_binding
from qualification.synthesis.vehicle_dynamics_contract import build_wayfarer_contract_family


AXIS = {
    "start_utc": "2226-06-15T00:00:00Z",
    "step_seconds": 3600.0,
}


def _qualification_ephemeris_rows():
    """Deterministic seam fixture; not a claim of celestial ephemeris authority.

    The seven-column shape matches Navigator's existing route-scoped
    qualification fixtures: sample coordinate, XYZ km, VXYZ km/s. Seventy-three
    hourly samples provide margin beyond Navigator's 48-hour root-search bound,
    including terminal-burn checkpoint interpolation. The destination translates
    consistently at +10 km/s in Y so the real terminal burn has non-zero delta-v.
    """
    origin = []
    destination = []
    for sample in range(73):
        elapsed_s = sample * AXIS["step_seconds"]
        origin.append((float(sample), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
        destination.append(
            (
                float(sample),
                100_000_000.0,
                10.0 * elapsed_s,
                0.0,
                0.0,
                10.0,
                0.0,
            )
        )
    return origin, destination


class ShipyardNavigatorSolvedLegTest(unittest.TestCase):
    """M1 seam qualification: governed Shipyard mass reaches real Navigator physics.

    This is deliberately narrower than full M1 closure because the celestial
    rows are a deterministic qualification replay, not a live/canonical B1
    ephemeris acquisition. `_solve_leg`, `_state_primary`, `_metric_time_s`,
    and `_torch_burn` remain the real embedded Navigator implementations.
    """

    def test_bound_shipyard_mass_executes_real_navigator_solve_leg(self):
        contract = build_wayfarer_contract_family(2226)[0]
        state = outer_core._new_state("SHIPYARD-SOLVED-LEG", "WAYFARER-TEST")
        original_state = copy.deepcopy(state)

        binding = validate_campaign_binding(contract, state)
        self.assertTrue(binding["compatible_for_navigator_consumption"])
        wet_mass_t = float(state["ship"]["wet_mass_t"])
        available_remass_t = float(state["ship"]["remass_t"])
        self.assertAlmostEqual(wet_mass_t, 1158.5, places=9)
        self.assertAlmostEqual(available_remass_t, 250.0, places=9)

        origin_rows, destination_rows = _qualification_ephemeris_rows()
        with TemporaryDirectory() as td:
            nav = outer_core._load_core(Path(td) / "sequence_h")
            # Select directly from Navigator's admitted mode registry rather than
            # introducing a Shipyard-side propulsion-mode name.
            torch_mode = sorted(nav.TORCH_MODES)[0]
            self.assertTrue(torch_mode)
            leg = nav._solve_leg(
                "CERES",
                "MARS",
                nav._dt(AXIS["start_utc"]),
                origin_rows,
                destination_rows,
                AXIS,
                "EXPEDITE",
                torch_mode,
                wet_mass_t,
            )

        burn = leg["terminal_burn"]
        used = float(burn["remass_used_t"])

        # The solved burn is genuine Navigator physics, driven by the bound
        # campaign wet mass rather than a Shipyard-side surrogate calculation.
        self.assertGreater(used, 0.0)
        self.assertLessEqual(used, available_remass_t)
        self.assertAlmostEqual(float(burn["wet_mass_start_t"]), wet_mass_t, places=9)
        self.assertAlmostEqual(float(burn["wet_mass_end_t"]), wet_mass_t - used, places=9)
        self.assertAlmostEqual(float(burn["delta_v_km_s"]), 10.0, places=9)
        self.assertEqual(leg["torch_mode"], torch_mode)

        # Real Navigator root/interpolation closure remains tight.
        self.assertLess(abs(float(leg["root_solver"]["root_residual_s"])), 1e-6)
        self.assertLess(float(leg["arrival"]["ship_position_residual_km"]), 1e-3)
        self.assertLess(float(leg["arrival"]["ship_velocity_residual_km_s"]), 1e-9)
        self.assertEqual(leg["solver_model"], nav.NAV_V1_A["model"])
        self.assertEqual(leg["solver_version"], nav.NAV_V1_A["version"])

        # Planning/solving is non-mutating. Campaign authority has not moved.
        self.assertEqual(state, original_state)
        self.assertFalse(binding["navigator_authority_changed"])
        self.assertFalse(binding["flight_dynamics_authority"])
        self.assertFalse(binding["canon_changed"])
        self.assertFalse(binding["production_shipclasses_changed"])


if __name__ == "__main__":
    unittest.main()
