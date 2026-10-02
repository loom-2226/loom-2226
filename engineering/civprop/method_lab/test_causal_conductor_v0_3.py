import inspect
import unittest

from engineering.civprop.method_lab.causal_conductor_v0_3 import (
    annual_authority_lane,
    project_lifecycle_lane,
    run_conductor,
    run_earth_project_conductor,
)


class CausalConductorV03Tests(unittest.TestCase):
    def test_conductor_has_no_global_year_range_or_hybrid_run(self):
        src = inspect.getsource(run_conductor)
        self.assertNotIn("range(", src)
        self.assertNotIn("HybridEngineV1", src)
        self.assertNotIn(".run(bundle", src)

    def test_annual_lane_self_schedules_on_master_queue(self):
        lane = annual_authority_lane(
            lane_id="EARTH_DEMOGRAPHY",
            values_by_year={2026: 8.0, 2027: 8.1, 2028: 8.2},
            state_key="earth_population",
            provenance_ref="earth:test",
        )
        out = run_conductor(
            start_year=2026, end_year=2030, initial_state={},
            seed_events=({
                "year": 2026, "phase": 10,
                "event_type": "ANNUAL_LANE_BOUNDARY",
                "lane_id": "EARTH_DEMOGRAPHY",
                "provenance_refs": ("earth:test",), "payload": {},
            },),
            lanes={"EARTH_DEMOGRAPHY": lane},
        )
        self.assertEqual(out.processed_years, (2026, 2027, 2028))
        self.assertEqual(out.annual_lane_invocations["EARTH_DEMOGRAPHY"], 3)
        self.assertEqual(out.global_annual_heartbeat_count, 0)
        self.assertEqual(out.final_state["earth_population"], 8.2)

    def test_nonannual_project_events_share_same_clock(self):
        earth = annual_authority_lane(
            lane_id="EARTH_DEMOGRAPHY",
            values_by_year={2026: 8.0, 2027: 8.1, 2028: 8.2, 2029: 8.3, 2030: 8.4},
            state_key="earth_population",
            provenance_ref="earth:test",
        )
        project = project_lifecycle_lane(project_id="P1")
        out = run_conductor(
            start_year=2026, end_year=2030,
            initial_state={"projects": {"P1": {"status": "COMMITTED"}}},
            seed_events=(
                {"year": 2026, "phase": 10, "event_type": "ANNUAL_LANE_BOUNDARY",
                 "lane_id": "EARTH_DEMOGRAPHY", "provenance_refs": ("earth:test",), "payload": {}},
                {"year": 2029, "phase": 30, "event_type": "PROJECT_LIFECYCLE_EVENT",
                 "lane_id": "PROJECT_LIFECYCLE", "provenance_refs": ("tx:test",),
                 "payload": {"action": "REVIEW", "provenance_refs": ("tx:test",)}},
            ),
            lanes={"EARTH_DEMOGRAPHY": earth, "PROJECT_LIFECYCLE": project},
        )
        self.assertEqual(out.final_state["projects"]["P1"]["status"], "ACTIVE")
        self.assertIn(2029, out.processed_years)
        self.assertIn(2030, out.processed_years)
        self.assertEqual(out.global_annual_heartbeat_count, 0)

    def test_unknown_lane_fails_closed_as_blocked_event(self):
        out = run_conductor(
            start_year=2026, end_year=2226, initial_state={},
            seed_events=({"year": 2050, "event_type": "X", "lane_id": "ABSENT"},),
            lanes={},
        )
        self.assertEqual(out.events[0].status, "BLOCKED_UNKNOWN_LANE")
        self.assertEqual(out.final_state, {})

    def test_real_horizon_adapter_requires_exact_201_year_authority(self):
        rows = [{"year": y, "biological_population": float(y)} for y in range(2026, 2227)]
        state = {"projects": {"P": {"status": "COMMITTED", "provenance_refs": ["tx:p"]}}}
        out = run_earth_project_conductor(
            earth_population_rows=rows, committed_state=state,
            project_id="P", review_year=2029,
        )
        self.assertEqual(out.annual_lane_invocations["EARTH_DEMOGRAPHY"], 201)
        self.assertEqual(out.final_state["earth_biological_population"], 2226.0)
        self.assertEqual(out.final_state["projects"]["P"]["status"], "ACTIVE")
        self.assertEqual(out.global_annual_heartbeat_count, 0)
        self.assertEqual(out.processed_years[0], 2026)
        self.assertEqual(out.processed_years[-1], 2226)

    def test_real_horizon_adapter_rejects_missing_authority_year(self):
        rows = [{"year": y, "biological_population": float(y)} for y in range(2026, 2227) if y != 2100]
        state = {"projects": {"P": {"status": "COMMITTED", "provenance_refs": ["tx:p"]}}}
        with self.assertRaisesRegex(ValueError, "EARTH_AUTHORITY_HORIZON_NOT_EXACT"):
            run_earth_project_conductor(
                earth_population_rows=rows, committed_state=state,
                project_id="P", review_year=2029,
            )

    def test_deterministic_replay(self):
        def once():
            lane = annual_authority_lane(
                lane_id="A", values_by_year={2026: 1, 2027: 2},
                state_key="x", provenance_ref="p")
            return run_conductor(
                start_year=2026, end_year=2226, initial_state={},
                seed_events=({"year": 2026, "event_type": "ANNUAL_LANE_BOUNDARY",
                              "lane_id": "A", "provenance_refs": ("p",)},),
                lanes={"A": lane})
        self.assertEqual(once().canonical_sha256, once().canonical_sha256)


if __name__ == "__main__":
    unittest.main()
