from __future__ import annotations

import unittest

from loom.gis.navigation_overlay import build_navigation_overlay


class LiveVehicleStateContractTests(unittest.TestCase):
    def test_live_vehicle_state_is_independent_of_historical_route(self) -> None:
        overlay = build_navigation_overlay(
            None,
            current_vehicle_state={
                "location_token": "CERES",
                "epoch_utc": "2226-09-03T00:00:00Z",
                "revision": 3,
            },
        )
        self.assertEqual(overlay.current_vehicle_state["location_token"], "CERES")
        self.assertEqual(overlay.current_vehicle_state["revision"], 3)


if __name__ == "__main__":
    unittest.main()
