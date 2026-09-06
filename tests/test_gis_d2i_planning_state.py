from __future__ import annotations

import unittest

from loom.gis.flight_planning import GISPlanningStateV1


class D2IPlanningStateTests(unittest.TestCase):
    def test_state_exposes_engineering_shadow_without_changing_contract(self):
        state = GISPlanningStateV1(
            session_id="S",
            origin="CERES",
            destination="MARS",
            priority="BALANCED",
            gravity_engineering_feasibility_report={"status":"OPEN_VECTORING_AND_THERMAL_QUALIFICATION"},
        )
        out = state.to_dict()
        self.assertIn("gravity_engineering_feasibility_report", out)
        self.assertEqual(out["gravity_engineering_feasibility_report"]["status"], "OPEN_VECTORING_AND_THERMAL_QUALIFICATION")
        self.assertEqual(out["contract"], "LOOM_GIS_FLIGHT_PLANNING_V1")


if __name__ == "__main__":
    unittest.main()
